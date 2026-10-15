#!/usr/bin/env python3
"""
AISTS CP-0023: Evidence-first forensic checks for the BTCUSDT Spot archives already stored in Drive.

Tasks:
1) Check each local ZIP against Binance's official .CHECKSUM sidecar where available.
2) Identify exact candle rows behind OHLC/timestamp anomalies.
3) Report concrete time gaps instead of relying only on summary counts.
4) Rebuild calendar-month candles from existing 1d archives into a SEPARATE derived file.
5) Compare Binance-native 1mo monthly candles to daily-derived months without overwriting raw ZIPs.

No API key, no order placement, no raw ZIP deletion or rewrite.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Only official downloadable public archive/checksum objects are allowed; no REST API.
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, build_opener

_OFFICIAL_REDIRECT_HOSTS = {
    "data.binance.vision",
    "s3.amazonaws.com",
    "s3-ap-northeast-1.amazonaws.com",
    "s3.ap-northeast-1.amazonaws.com",
    "s3.dualstack.ap-northeast-1.amazonaws.com",
    "data.binance.vision.s3.amazonaws.com",
    "data.binance.vision.s3-ap-northeast-1.amazonaws.com",
    "data.binance.vision.s3.ap-northeast-1.amazonaws.com",
}

def _official_object_path_ok(url, original_path=None):
    p = urlparse(url)
    if p.scheme != "https" or p.username or p.password or p.query or p.fragment or p.port not in (None, 443):
        return False
    if not (p.path.endswith(".zip") or p.path.endswith(".zip.CHECKSUM")):
        return False
    if p.hostname == "data.binance.vision":
        return p.path.startswith("/data/spot/")
    if p.hostname in _OFFICIAL_REDIRECT_HOSTS and original_path:
        return p.path in {original_path, "/data.binance.vision" + original_path}
    return False

class _OfficialArchiveRedirect(HTTPRedirectHandler):
    def __init__(self, original_path):
        super().__init__()
        self.original_path = original_path

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _official_object_path_ok(newurl, self.original_path):
            raise HTTPError(newurl, code, "Redirect outside exact official archive/checksum allowlist", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def _official_archive_get(url, timeout):
    original = urlparse(url)
    if original.hostname != "data.binance.vision" or not _official_object_path_ok(url):
        raise ValueError("Blocked non-official Binance downloadable archive/checksum URL")
    opener = build_opener(_OfficialArchiveRedirect(original.path))
    with opener.open(Request(url, headers={"User-Agent": USER_AGENT}), timeout=timeout) as response:
        final_url = response.geturl()
        if not _official_object_path_ok(final_url, original.path):
            raise ValueError("Final URL failed official host/path validation")
        return response.status, response.read()


SYMBOL = "BTCUSDT"
BASE = "https://data.binance.vision/data/spot/monthly/klines"
INTERVALS = ["5m", "15m", "30m", "1h", "4h", "1d", "1mo"]
STEP_MS = {"5m":300_000, "15m":900_000, "30m":1_800_000, "1h":3_600_000, "4h":14_400_000, "1d":86_400_000}
ROOT = Path("/content/drive/MyDrive/AISTS/market_data/binance_spot/BTCUSDT")
USER_AGENT = "AISTS-CP0023-Forensic-Audit/1.0"
TIMEOUT_SECONDS = 25
MAX_WORKERS = 8
MAX_RETRIES = 2
PRICE_VOLUME_COLS = [1, 2, 3, 4, 5, 7, 9, 10]
NUMERIC_COMPARE = ["open", "high", "low", "close", "volume", "quote_asset_volume",
                   "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume", "ignore"]

def get_root():
    try:
        import google.colab  # noqa: F401
        from google.colab import drive
        if not Path("/content/drive/MyDrive").exists():
            drive.mount("/content/drive")
        if not Path("/content/drive/MyDrive").exists():
            raise RuntimeError("Drive not mounted at /content/drive/MyDrive")
        return ROOT
    except ImportError:
        local = Path(os.environ.get("AISTS_DATA_ROOT", "/content/AISTS/market_data/binance_spot/BTCUSDT"))
        print("Colab not detected; local fallback:", local)
        return local

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def get_bytes(url):
    return _official_archive_get(url, TIMEOUT_SECONDS)

def parse_epoch(raw):
    # Avoid float conversion. Binance Spot public archives use microseconds from 2025-01-01.
    x = int(str(raw).strip())
    if x >= 100_000_000_000_000:
        x //= 1000
    return x

def utc_iso(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()

def iter_archives(root, interval):
    folder = root / "klines" / interval
    if not folder.exists():
        return
    pattern = f"{SYMBOL}-{interval}-????-??.zip"
    for path in sorted(folder.glob(pattern)):
        yield path

def verify_one_checksum(path):
    filename = path.name
    interval = path.parent.name
    yearmonth = filename.removesuffix(".zip")
    url = f"{BASE}/{SYMBOL}/{interval}/{filename}.CHECKSUM"
    rec = {
        "interval": interval, "filename": filename, "local_path": str(path),
        "checksum_url": url, "local_sha256": None, "official_sha256": None,
        "status": None, "http_status": None, "detail": None
    }
    try:
        rec["local_sha256"] = sha256_file(path)
    except Exception as e:
        rec.update(status="LOCAL_READ_ERROR", detail=f"{type(e).__name__}: {e}")
        return rec
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            code, payload = get_bytes(url)
            rec["http_status"] = code
            text = payload.decode("utf-8", errors="replace").strip()
            match = re.search(r"(?i)\b([0-9a-f]{64})\b", text)
            if not match:
                rec.update(status="INVALID_CHECKSUM_SIDECAR", detail=text[:500])
                return rec
            official = match.group(1).lower()
            rec["official_sha256"] = official
            if official == rec["local_sha256"].lower():
                rec.update(status="MATCH", detail="Local SHA256 matches official sidecar")
            else:
                rec.update(status="MISMATCH", detail="Local SHA256 differs from official sidecar")
            return rec
        except HTTPError as e:
            rec["http_status"] = e.code
            if e.code == 404:
                rec.update(status="SIDECAR_NOT_FOUND", detail="Binance .CHECKSUM sidecar returned 404")
                return rec
            last_error = f"HTTPError {e.code}: {e.reason}"
        except (URLError, TimeoutError, OSError) as e:
            last_error = f"{type(e).__name__}: {e}"
        if attempt < MAX_RETRIES:
            time.sleep(0.5 * (attempt + 1))
    rec.update(status="CHECKSUM_FETCH_ERROR", detail=last_error)
    return rec

def run_checksum_verification(root):
    paths = [p for interval in INTERVALS for p in iter_archives(root, interval)]
    print(f"Official SHA256 sidecar verification: {len(paths)} local archives; up to {MAX_WORKERS} parallel requests.")
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(verify_one_checksum, p): p for p in paths}
        done = 0
        for future in as_completed(futures):
            try:
                rec = future.result()
            except Exception as e:
                p = futures[future]
                rec = {"interval": p.parent.name, "filename": p.name, "local_path": str(p),
                       "checksum_url": "", "local_sha256": None, "official_sha256": None,
                       "status": "INTERNAL_ERROR", "http_status": None, "detail": f"{type(e).__name__}: {e}"}
            results.append(rec)
            done += 1
            if done % 50 == 0 or done == len(paths):
                counts = {}
                for r in results:
                    counts[r["status"]] = counts.get(r["status"], 0) + 1
                print(f"[{done}/{len(paths)}] checksum status counts: {counts}")
    results.sort(key=lambda x: (x.get("interval",""), x.get("filename","")))
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    with (reports / "official_checksum_verification.csv").open("w", newline="", encoding="utf-8") as f:
        cols = ["interval","filename","local_path","checksum_url","local_sha256","official_sha256","status","http_status","detail"]
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(results)
    summary = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    summary_json = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "archives_checked": len(paths),
        "status_counts": summary,
        "pass_count": summary.get("MATCH", 0),
        "blocking_count": sum(v for k,v in summary.items() if k not in ("MATCH","SIDECAR_NOT_FOUND")),
        "note": "A checksum MATCH proves the downloaded bytes match the published sidecar, not that the exchange's historical dataset is economically complete/correct."
    }
    (reports / "official_checksum_summary.json").write_text(json.dumps(summary_json, indent=2), encoding="utf-8")
    print("Checksum summary:", json.dumps(summary_json, indent=2))
    return results, summary_json

def parse_kline(row):
    if len(row) < 12:
        raise ValueError(f"Expected 12 fields, got {len(row)}")
    open_ms = parse_epoch(row[0])
    close_ms = parse_epoch(row[6])
    vals = {}
    for idx, key in [(1,"open"),(2,"high"),(3,"low"),(4,"close"),(5,"volume"),(7,"quote_asset_volume"),(9,"taker_buy_base_asset_volume"),(10,"taker_buy_quote_asset_volume")]:
        vals[key] = Decimal(str(row[idx]).strip())
        if not vals[key].is_finite():
            raise ValueError(f"{key} is not finite")
    vals["number_of_trades"] = int(str(row[8]).strip())
    vals["open_time_ms"] = open_ms
    vals["close_time_ms"] = close_ms
    vals["ignore"] = row[11]
    return vals

def forensic_interval(root, interval, gap_cap=10000):
    paths = list(iter_archives(root, interval))
    anomalies = []
    gap_events = []
    row_count = duplicates = out_of_order = gap_total = 0
    prev_ms = None
    first = last = None
    invalid_zip_count = 0
    expected_step = STEP_MS.get(interval)

    for path in paths:
        try:
            with zipfile.ZipFile(path) as zf:
                bad_member = zf.testzip()
                if bad_member:
                    anomalies.append({"interval": interval, "filename": path.name, "type": "ZIP_CRC_ERROR", "detail": bad_member})
                    invalid_zip_count += 1
                    continue
                csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if not csv_names:
                    anomalies.append({"interval": interval, "filename": path.name, "type": "CSV_MISSING"})
                    invalid_zip_count += 1
                    continue
                for inner_name in csv_names:
                    with zf.open(inner_name, "r") as raw:
                        import io
                        reader = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline=""))
                        for line_no, row in enumerate(reader, 1):
                            if not row:
                                continue
                            try:
                                k = parse_kline(row)
                            except Exception as e:
                                anomalies.append({
                                    "interval": interval, "filename": path.name, "inner_csv": inner_name,
                                    "line_number": line_no, "type": "ROW_PARSE_ERROR", "raw_row": row[:15],
                                    "detail": f"{type(e).__name__}: {e}"
                                })
                                continue
                            o,h,l,c,v = [k[key] for key in ("open","high","low","close","volume")]
                            reasons = []
                            if l > min(o,c): reasons.append("LOW_ABOVE_OPEN_OR_CLOSE")
                            if h < max(o,c): reasons.append("HIGH_BELOW_OPEN_OR_CLOSE")
                            if l > h: reasons.append("LOW_ABOVE_HIGH")
                            if v < 0: reasons.append("NEGATIVE_VOLUME")
                            if k["close_time_ms"] < k["open_time_ms"]: reasons.append("CLOSE_BEFORE_OPEN")
                            if reasons:
                                anomalies.append({
                                    "interval": interval, "filename": path.name, "inner_csv": inner_name,
                                    "line_number": line_no, "type": "OHLC_OR_TIME_ANOMALY",
                                    "open_time_utc": utc_iso(k["open_time_ms"]),
                                    "open_time_ms": k["open_time_ms"], "reasons": reasons,
                                    "open": str(o), "high": str(h), "low": str(l), "close": str(c),
                                    "volume": str(v), "close_time_ms": k["close_time_ms"]
                                })
                            t = k["open_time_ms"]
                            if first is None:
                                first = {"open_time_utc": utc_iso(t), "file": path.name}
                            if prev_ms is not None:
                                delta = t - prev_ms
                                if delta == 0:
                                    duplicates += 1
                                elif delta < 0:
                                    out_of_order += 1
                                    if len(anomalies) < 20000:
                                        anomalies.append({"interval": interval, "filename": path.name, "type": "OUT_OF_ORDER",
                                                          "previous_open_time_utc": utc_iso(prev_ms), "open_time_utc": utc_iso(t)})
                                elif expected_step and delta > expected_step:
                                    if delta % expected_step == 0:
                                        missing = max(0, delta // expected_step - 1)
                                    else:
                                        missing = None
                                    gap_total += missing if missing is not None else 1
                                    if len(gap_events) < gap_cap:
                                        gap_events.append({
                                            "interval": interval, "file": path.name,
                                            "previous_open_time_utc": utc_iso(prev_ms),
                                            "next_open_time_utc": utc_iso(t),
                                            "elapsed_ms": delta, "expected_step_ms": expected_step,
                                            "estimated_missing_bars": missing,
                                            "spacing_type": "integral_gap" if missing is not None else "non_integral_spacing"
                                        })
                            prev_ms = t
                            last = {"open_time_utc": utc_iso(t), "file": path.name}
                            row_count += 1
        except Exception as e:
            invalid_zip_count += 1
            anomalies.append({"interval": interval, "filename": path.name, "type": "ARCHIVE_READ_ERROR", "detail": f"{type(e).__name__}: {e}"})

    return {
        "interval": interval, "archive_count": len(paths), "rows_scanned": row_count,
        "anomaly_count": len(anomalies), "anomalies": anomalies[:20000],
        "duplicate_open_times": duplicates, "out_of_order_open_times": out_of_order,
        "gap_event_count": len(gap_events), "estimated_missing_intervals": gap_total if expected_step else None,
        "gap_events": gap_events, "first_candle": first, "last_candle": last,
        "invalid_archive_count": invalid_zip_count,
        "gap_note": "Observed spacing gaps need source coverage/candle semantics review; do not infer a defective market feed from the count alone."
    }

def read_daily_rows(root):
    result = []
    for path in iter_archives(root, "1d"):
        try:
            with zipfile.ZipFile(path) as zf:
                names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                for name in names:
                    with zf.open(name, "r") as raw:
                        import io
                        reader = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline=""))
                        for line_no, row in enumerate(reader, 1):
                            if not row: continue
                            try:
                                result.append(parse_kline(row))
                            except Exception:
                                continue
        except Exception:
            continue
    result.sort(key=lambda r: r["open_time_ms"])
    # Keep first copy only; duplicate detection is reported separately in forensic report.
    deduped = []
    seen = set()
    for r in result:
        if r["open_time_ms"] not in seen:
            deduped.append(r); seen.add(r["open_time_ms"])
    return deduped

def month_start_ms(year, month):
    return int(datetime(year, month, 1, tzinfo=timezone.utc).timestamp() * 1000)

def next_month_start_ms(year, month):
    return month_start_ms(year + (month == 12), 1 if month == 12 else month + 1)

def build_derived_monthly(root):
    """Build calendar-month candles from daily candles, write separate CSV, compare against native 1mo files."""
    daily = read_daily_rows(root)
    grouped = {}
    for r in daily:
        dt = datetime.fromtimestamp(r["open_time_ms"]/1000, tz=timezone.utc)
        key = (dt.year, dt.month)
        grouped.setdefault(key, []).append(r)
    derived = []
    for (year, month), bars in sorted(grouped.items()):
        bars.sort(key=lambda x: x["open_time_ms"])
        first, last = bars[0], bars[-1]
        row = {
            "open_time": month_start_ms(year, month),
            "open": first["open"],
            "high": max(b["high"] for b in bars),
            "low": min(b["low"] for b in bars),
            "close": last["close"],
            "volume": sum((b["volume"] for b in bars), Decimal("0")),
            "close_time": next_month_start_ms(year, month) - 1,
            "quote_asset_volume": sum((b["quote_asset_volume"] for b in bars), Decimal("0")),
            "number_of_trades": sum(b["number_of_trades"] for b in bars),
            "taker_buy_base_asset_volume": sum((b["taker_buy_base_asset_volume"] for b in bars), Decimal("0")),
            "taker_buy_quote_asset_volume": sum((b["taker_buy_quote_asset_volume"] for b in bars), Decimal("0")),
            "ignore": "0",
            "daily_bars_used": len(bars),
            "first_daily_candle_utc": utc_iso(first["open_time_ms"]),
            "last_daily_candle_utc": utc_iso(last["open_time_ms"]),
        }
        derived.append(row)

    derived_dir = root / "derived" / "1mo_from_1d"
    derived_dir.mkdir(parents=True, exist_ok=True)
    out_csv = derived_dir / "BTCUSDT-1mo-derived-from-1d.csv"
    fields = ["open_time","open","high","low","close","volume","close_time","quote_asset_volume",
              "number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore",
              "daily_bars_used","first_daily_candle_utc","last_daily_candle_utc"]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in derived:
            w.writerow({k: (str(v) if isinstance(v, Decimal) else v) for k,v in r.items()})

    native = {}
    for path in iter_archives(root, "1mo"):
        try:
            with zipfile.ZipFile(path) as zf:
                for name in [n for n in zf.namelist() if n.lower().endswith(".csv")]:
                    with zf.open(name, "r") as raw:
                        import io
                        reader = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline=""))
                        for row in reader:
                            if not row: continue
                            try:
                                k = parse_kline(row)
                            except Exception:
                                continue
                            dt = datetime.fromtimestamp(k["open_time_ms"]/1000, tz=timezone.utc)
                            native[(dt.year,dt.month)] = k
        except Exception:
            continue

    comparisons = []
    for d in derived:
        keydt = datetime.fromtimestamp(d["open_time"]/1000, tz=timezone.utc)
        key = (keydt.year, keydt.month)
        n = native.get(key)
        if n is None:
            comparisons.append({"year":key[0],"month":key[1],"status":"NO_NATIVE_1MO_ARCHIVE_ROW","different_fields":[]})
            continue
        diffs = []
        for field in NUMERIC_COMPARE:
            derived_value = d[field]
            native_key = {
                "quote_asset_volume":"quote_asset_volume",
                "number_of_trades":"number_of_trades",
                "taker_buy_base_asset_volume":"taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume":"taker_buy_quote_asset_volume"
            }.get(field, field)
            native_value = n[native_key]
            if field == "number_of_trades":
                eq = int(derived_value) == int(native_value)
            else:
                eq = Decimal(derived_value) == Decimal(native_value)
            if not eq:
                diffs.append({"field":field,"daily_derived":str(derived_value),"native_1mo":str(native_value)})
        comparisons.append({"year":key[0],"month":key[1],
                            "status":"MATCH" if not diffs else "VALUE_MISMATCH",
                            "different_fields":diffs})
    comp_path = root / "reports" / "monthly_native_vs_daily_derived.csv"
    comp_path.parent.mkdir(parents=True, exist_ok=True)
    with comp_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year","month","status","different_fields"])
        w.writeheader()
        for r in comparisons:
            w.writerow({**r, "different_fields": json.dumps(r["different_fields"], ensure_ascii=False)})
    match_count = sum(x["status"]=="MATCH" for x in comparisons)
    mismatch_count = sum(x["status"]=="VALUE_MISMATCH" for x in comparisons)
    no_native_count = sum(x["status"]=="NO_NATIVE_1MO_ARCHIVE_ROW" for x in comparisons)
    summary = {
        "derived_month_rows": len(derived),
        "first_derived_month": [derived[0]["open_time"] if derived else None],
        "last_derived_month": [derived[-1]["open_time"] if derived else None],
        "native_month_rows": len(native),
        "native_daily_derived_matches": match_count,
        "native_daily_derived_mismatches": mismatch_count,
        "derived_months_without_native_row": no_native_count,
        "derived_csv": str(out_csv),
        "comparison_csv": str(comp_path),
        "note": "Derived candles were written separately from raw archives. Monthly reconciliation differences may reflect upstream archive discrepancies or incomplete daily data and must be investigated."
    }
    (root / "reports" / "monthly_reconciliation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Monthly reconciliation:", json.dumps(summary, indent=2))
    return summary

def main():
    root = get_root()
    if not root.exists():
        raise FileNotFoundError(f"Data root not found: {root}. Confirm Drive is mounted and archives exist.")
    print("AISTS CP-0023 forensic audit")
    print("Root:", root)
    print("Raw ZIPs will not be changed or deleted.")
    checksum_rows, checksum_summary = run_checksum_verification(root)
    results = []
    print("\nScanning exact row anomalies and gap events...")
    for interval in INTERVALS:
        r = forensic_interval(root, interval)
        results.append(r)
        print(json.dumps({
            "interval": r["interval"], "archive_count": r["archive_count"],
            "rows_scanned": r["rows_scanned"], "anomaly_count": r["anomaly_count"],
            "duplicate_open_times": r["duplicate_open_times"], "out_of_order_open_times": r["out_of_order_open_times"],
            "gap_event_count": r["gap_event_count"], "estimated_missing_intervals": r["estimated_missing_intervals"],
            "invalid_archive_count": r["invalid_archive_count"], "first_candle": r["first_candle"], "last_candle": r["last_candle"],
            "anomaly_examples": r["anomalies"][:5], "gap_examples": r["gap_events"][:5]
        }, ensure_ascii=False))
    forensic_report = {
        "project":"AISTS CP-0023", "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "symbol":SYMBOL, "market":"spot", "root":str(root),
        "binance_official_source":"https://data.binance.vision/",
        "timestamp_policy":"Spot archive timestamps before 2025-01-01 are milliseconds; from 2025-01-01 they are microseconds. All are normalized to UTC milliseconds for internal checks.",
        "checksum_summary":checksum_summary, "interval_results":results
    }
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "forensic_row_and_gap_report.json").write_text(json.dumps(forensic_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (reports / "forensic_row_anomalies.csv").write_text("interval,filename,inner_csv,line_number,type,detail\n", encoding="utf-8")
    anomalies = [a for r in results for a in r["anomalies"]]
    if anomalies:
        allkeys = sorted(set().union(*(a.keys() for a in anomalies)))
        with (reports / "forensic_row_anomalies.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=allkeys, extrasaction="ignore")
            w.writeheader()
            for a in anomalies:
                w.writerow({k:(json.dumps(v, ensure_ascii=False) if isinstance(v,(dict,list)) else v) for k,v in a.items()})
    all_gaps = [g for r in results for g in r["gap_events"]]
    gapkeys = sorted(set().union(*(g.keys() for g in all_gaps))) if all_gaps else ["interval","file","previous_open_time_utc","next_open_time_utc","elapsed_ms","expected_step_ms","estimated_missing_bars","spacing_type"]
    with (reports / "forensic_gap_events.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=gapkeys, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_gaps)

    monthly_summary = build_derived_monthly(root)
    bundle = reports / "AISTS_CP0023_Forensic_Audit_Bundle.zip"
    members = [
        reports / "official_checksum_verification.csv",
        reports / "official_checksum_summary.json",
        reports / "forensic_row_and_gap_report.json",
        reports / "forensic_row_anomalies.csv",
        reports / "forensic_gap_events.csv",
        reports / "monthly_native_vs_daily_derived.csv",
        reports / "monthly_reconciliation_summary.json",
    ]
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in members:
            if p.exists(): zf.write(p, arcname=p.name)
    print("\nCP-0023 COMPLETE")
    print("Compact evidence bundle:", bundle)
    print("Monthly candles derived from 1d:", root / "derived" / "1mo_from_1d" / "BTCUSDT-1mo-derived-from-1d.csv")
    print("Upload the compact bundle to this chat. It contains reports, not the raw market dataset.")
    print("No backtest should start until checksum results, exact row anomalies, data gaps, and monthly reconciliation have been reviewed.")

if __name__ == "__main__":
    main()