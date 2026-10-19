#!/usr/bin/env python3
"""CP-0271: read-only alternate-source corroboration probe; never closes G0."""
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "cp0271_alternate_source"
CACHE = ROOT / ".cache" / "aists" / "binance-monthly-archives"
MANIFEST = ROOT / "evidence/source_adjudication/CP0040_Run_38882377148/CP0040_ExactKey_Quarantine_Manifest.csv"
URL = "https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_1h.csv"
FOUR_HOURS_MS = 4 * 60 * 60 * 1000

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def to_ms(value):
    n = int(float(value))
    if n > 100_000_000_000_000:
        return n // 1000
    if n < 100_000_000_000:
        return n * 1000
    return n

def f(row, *names):
    lowered = {str(k).strip().lower().replace(" ", "").replace("_", ""): v for k, v in row.items()}
    for name in names:
        key = name.lower().replace(" ", "").replace("_", "")
        if key in lowered and lowered[key] not in (None, ""):
            return lowered[key]
    return None

def read_cdd(raw):
    text = raw.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    # CryptoDataDownload CSVs may begin with a plain URL banner (not a # comment).
    # Locate the real header instead of assuming it is the first physical line.
    header_index = next((i for i, line in enumerate(lines[:25])
                         if "," in line and "unix" in line.lower()
                         and "open" in line.lower() and "close" in line.lower()), None)
    if header_index is None:
        raise ValueError("CDD_CSV_HEADER_NOT_FOUND:" + repr(lines[:5]))
    reader = csv.DictReader(lines[header_index:])
    rows = {}
    bad = 0
    for row in reader:
        try:
            ts = to_ms(f(row, "unix", "timestamp", "open_time"))
            o = float(f(row, "open")); h = float(f(row, "high"))
            l = float(f(row, "low")); c = float(f(row, "close"))
            vb = float(f(row, "Volume BTC", "volume btc", "volume", "base_volume"))
            vq_raw = f(row, "Volume USDT", "volume usdt", "quote_volume")
            vq = float(vq_raw) if vq_raw is not None else None
            tc_raw = f(row, "tradecount", "trade_count", "trades")
            tc = int(float(tc_raw)) if tc_raw is not None else None
            if ts % 3_600_000 != 0 or not (l <= min(o,c) <= max(o,c) <= h):
                bad += 1; continue
            rows[ts] = {"o":o,"h":h,"l":l,"c":c,"vb":vb,"vq":vq,"tc":tc}
        except Exception:
            bad += 1
    return rows, bad

def aggregate_4h(hourly):
    buckets = defaultdict(list)
    for ts, row in hourly.items():
        buckets[(ts // FOUR_HOURS_MS) * FOUR_HOURS_MS].append((ts,row))
    out = {}
    incomplete = 0
    for key, items in buckets.items():
        items.sort()
        if len(items) != 4 or [t for t,_ in items] != [key+i*3_600_000 for i in range(4)]:
            incomplete += 1
            continue
        rs = [r for _,r in items]
        vq = None if any(r["vq"] is None for r in rs) else sum(r["vq"] for r in rs)
        tc = None if any(r["tc"] is None for r in rs) else sum(r["tc"] for r in rs)
        out[key] = {"o":rs[0]["o"],"h":max(r["h"] for r in rs),"l":min(r["l"] for r in rs),
                    "c":rs[-1]["c"],"vb":sum(r["vb"] for r in rs),"vq":vq,"tc":tc}
    return out, incomplete

def read_binance_4h():
    out = {}
    files = list(CACHE.rglob("BTCUSDT-4h-*.zip")) if CACHE.exists() else []
    parsed = 0
    errors = []
    for path in sorted(files):
        try:
            with zipfile.ZipFile(path) as z:
                members = [n for n in z.namelist() if n.lower().endswith(".csv")]
                for member in members:
                    for row in csv.reader(io.TextIOWrapper(z.open(member), encoding="utf-8-sig")):
                        if len(row) < 11: continue
                        try:
                            ts = to_ms(row[0])
                            # Spot kline CSV: open, high, low, close, base vol, close time, quote vol, trades...
                            out[ts] = {"o":float(row[1]),"h":float(row[2]),"l":float(row[3]),"c":float(row[4]),
                                       "vb":float(row[5]),"vq":float(row[7]),"tc":int(float(row[8]))}
                            parsed += 1
                        except Exception:
                            continue
        except Exception as exc:
            errors.append(f"{path.name}:{type(exc).__name__}")
    return out, len(files), parsed, errors

def compare(a, b):
    fields = ["o","h","l","c","vb","vq","tc"]
    result = {}
    for field in fields:
        x, y = a.get(field), b.get(field)
        if x is None or y is None:
            result[field] = "NOT_COMPARABLE"
        elif field == "tc":
            result[field] = "MATCH" if int(x) == int(y) else "DIFF"
        else:
            result[field] = "MATCH" if abs(float(x)-float(y)) <= max(1e-8, abs(float(y))*1e-8) else "DIFF"
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "checkpoint":"CP-0271",
        "purpose":"Alternative-source exact-key corroboration only; no source authority decision or G0 closure",
        "source_url":URL,
        "source_access_status":"PENDING",
        "source_sha256":None,
        "source_bytes":None,
        "source_hourly_rows":0,
        "source_parse_rejects":None,
        "complete_4h_aggregates":0,
        "incomplete_4h_buckets_excluded":None,
        "binance_cache_zip_count":0,
        "binance_cache_parsed_4h_rows":0,
        "manifest_4h_unresolved_keys":0,
        "exact_key_comparisons":0,
        "all_field_matches":0,
        "any_field_differences":0,
        "field_level_results":{},
        "limitations":[
            "Third-party OHLCV is corroboration, not official historical-version authority.",
            "No exact key is closed by this probe; frozen CP-0040 and authorized adjudication remain controlling.",
            "No synthetic bars are created; 4h aggregation requires all four complete, grid-aligned 1h rows.",
            "Downloaded source bytes are used transiently and are not republished in the artifact."
        ]
    }
    try:
        req = urllib.request.Request(URL, headers={"User-Agent":"AISTS-Research-Audit/CP-0271"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read()
            report["source_http_status"] = getattr(resp, "status", None)
            report["source_content_type"] = resp.headers.get("Content-Type")
        report["source_sha256"] = sha256_bytes(raw)
        report["source_bytes"] = len(raw)
        hourly, bad = read_cdd(raw)
        report["source_hourly_rows"] = len(hourly)
        report["source_parse_rejects"] = bad
        report["source_first_open_time_utc"] = datetime.fromtimestamp(min(hourly)/1000, timezone.utc).isoformat() if hourly else None
        report["source_last_open_time_utc"] = datetime.fromtimestamp(max(hourly)/1000, timezone.utc).isoformat() if hourly else None
        report["source_access_status"] = "DOWNLOADED_PARSED" if hourly else "DOWNLOADED_NO_PARSEABLE_ROWS"
        agg, incomplete = aggregate_4h(hourly)
        report["complete_4h_aggregates"] = len(agg)
        report["incomplete_4h_buckets_excluded"] = incomplete
        official, zip_count, parsed_count, errors = read_binance_4h()
        report["binance_cache_zip_count"] = zip_count
        report["binance_cache_parsed_4h_rows"] = parsed_count
        report["binance_cache_errors"] = errors
        with MANIFEST.open(newline="", encoding="utf-8-sig") as stream:
            manifest_rows = list(csv.DictReader(stream))
        keys = sorted({int(r["open_time_ms"]) for r in manifest_rows
                       if r.get("interval") == "4h" and str(r.get("open_time_ms","")).isdigit()})
        report["manifest_4h_unresolved_keys"] = len(keys)
        field_counts = defaultdict(lambda: defaultdict(int))
        per_key = []
        for key in keys:
            rec = {
                "open_time_ms": key,
                "open_time_utc": datetime.fromtimestamp(key/1000, timezone.utc).isoformat(),
                "third_party_4h_available": key in agg,
                "binance_monthly_4h_available": key in official,
            }
            if key not in agg or key not in official:
                rec["comparison"] = "NO_OVERLAP"
                per_key.append(rec)
                continue
            cmp = compare(agg[key], official[key])
            rec["field_comparison"] = cmp
            rec["comparison"] = "ALL_FIELDS_MATCH" if all(v == "MATCH" for v in cmp.values()) else ("FIELD_DIFFERENCE" if any(v == "DIFF" for v in cmp.values()) else "PARTIAL_NOT_COMPARABLE")
            report["exact_key_comparisons"] += 1
            if all(v == "MATCH" for v in cmp.values()):
                report["all_field_matches"] += 1
            elif any(v == "DIFF" for v in cmp.values()):
                report["any_field_differences"] += 1
            for field, status in cmp.items():
                field_counts[field][status] += 1
            per_key.append(rec)
        report["per_key_results"] = per_key
        report["field_level_results"] = {k:dict(v) for k,v in field_counts.items()}
        report["comparison_status"] = ("COMPARISON_COMPLETED" if report["exact_key_comparisons"] else "NO_OVERLAPPING_EXACT_KEYS")
    except Exception as exc:
        report["source_access_status"] = "ACQUISITION_OR_PARSE_FAILED"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["comparison_status"] = "PENDING_ACQUISITION"
    report["global_g0_status"] = "BLOCKED_GLOBAL"
    report["canonical_historical_source"] = "NONE"
    report["historical_version_provenance"] = "NOT_VERIFIED"
    report["acceptance_grade"] = False
    report["backtest_approved"] = False
    report["profitability_established"] = False
    report["live_signing_broadcast_orders"] = "BLOCKED"
    (OUT/"CP0271_Alternate_Source_Probe.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    lines = ["# CP-0271 Alternate-Source Probe", "", "This is a read-only corroboration probe, not G0 closure.", ""]
    for k,v in report.items():
        lines.append(f"- **{k}:** {json.dumps(v, sort_keys=True) if isinstance(v,(dict,list)) else v}")
    (OUT/"CP0271_Alternate_Source_Probe.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
if __name__ == "__main__":
    main()
