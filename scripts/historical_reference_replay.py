#!/usr/bin/env python3
"""Official Binance BTCUSDT monthly archives QA + independent reference replay.

No Binance REST market-data API, exchange keys, order signing, order placement,
raw data repair or source acceptance. Metrics are an independent reference,
not a bit-identical reproduction of historical CP-0027.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

UTC = timezone.utc
HOST = "data.binance.vision"
S3_HOSTS = {
    "s3.amazonaws.com", "s3-ap-northeast-1.amazonaws.com", "s3.ap-northeast-1.amazonaws.com",
    "s3.dualstack.ap-northeast-1.amazonaws.com", "data.binance.vision.s3.amazonaws.com",
    "data.binance.vision.s3-ap-northeast-1.amazonaws.com", "data.binance.vision.s3.ap-northeast-1.amazonaws.com",
}
INTERVALS = ("4h", "1d", "1mo")
FIRST_MONTH = (2017, 8)
LAST_MONTH = (2026, 9)
FEE_BPS = (10, 15, 20)
SLIP_BPS = (5, 10, 20)
PERIODS = (
    ("TRAIN", datetime(2017, 8, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC)),
    ("VALIDATION", datetime(2023, 1, 1, tzinfo=UTC), datetime(2025, 1, 1, tzinfo=UTC)),
    ("CONSUMED_OOS_DIAGNOSTIC", datetime(2025, 1, 1, tzinfo=UTC), datetime(2026, 10, 1, tzinfo=UTC)),
)
STRATEGIES = ("EMA_12_26", "RSI14_30_55", "DONCHIAN20_10")
COLS = 12


def months():
    y, m = FIRST_MONTH
    while (y, m) <= LAST_MONTH:
        yield y, m
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1


def to_us(dt):
    return int(round(dt.timestamp() * 1_000_000))


def from_us(value):
    return datetime.fromtimestamp(value / 1_000_000, tz=UTC)


def unit_of(raw):
    return 1 if raw >= 100_000_000_000_000 else 1000


def next_open(dt, interval):
    if interval == "4h":
        return dt + timedelta(hours=4)
    if interval == "1d":
        return dt + timedelta(days=1)
    if interval == "1mo":
        return datetime(dt.year + (1 if dt.month == 12 else 0), 1 if dt.month == 12 else dt.month + 1, 1, tzinfo=UTC)
    raise ValueError(interval)


def on_grid(dt, interval):
    if interval == "4h":
        return dt.hour % 4 == 0 and dt.minute == dt.second == dt.microsecond == 0
    if interval == "1d":
        return dt.hour == dt.minute == dt.second == dt.microsecond == 0
    return dt.day == 1 and dt.hour == dt.minute == dt.second == dt.microsecond == 0


def official_url(url, rel):
    p = urlparse(url)
    if p.scheme != "https" or p.username or p.password or p.query or p.fragment:
        return False
    if p.hostname == HOST:
        return p.path == "/data/spot" + rel
    if p.hostname in S3_HOSTS:
        return p.path.endswith("/data/spot" + rel) or p.path.endswith("/data.binance.vision/data/spot" + rel)
    return False


class RestrictedRedirect(HTTPRedirectHandler):
    def __init__(self, rel):
        super().__init__()
        self.rel = rel

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not official_url(newurl, self.rel):
            raise HTTPError(newurl, code, "Redirect rejected by source allowlist", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get_bytes(url, rel):
    if not official_url(url, rel):
        return {"ok": False, "status": "BLOCKED_URL_POLICY", "error": "Initial URL rejected"}
    error = ""
    for attempt in range(4):
        try:
            req = Request(url, headers={"User-Agent": "AISTS-Evidence-Runner/1.0", "Accept": "application/octet-stream"})
            with build_opener(RestrictedRedirect(rel)).open(req, timeout=45) as response:
                final = response.geturl()
                if not official_url(final, rel):
                    return {"ok": False, "status": "BLOCKED_REDIRECT_POLICY", "error": "Final URL rejected"}
                return {"ok": True, "status": int(response.status), "final_host": urlparse(final).hostname, "body": response.read()}
        except HTTPError as exc:
            error = f"HTTP {exc.code}: {exc.reason}"
            if exc.code == 404 or exc.code not in (408, 425, 429, 500, 502, 503, 504):
                break
        except (URLError, TimeoutError, OSError) as exc:
            error = f"{type(exc).__name__}: {exc}"
        if attempt < 3:
            time.sleep(min(2 ** attempt, 8))
    return {"ok": False, "status": "NETWORK_OR_HTTP_ERROR", "error": error}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_checksum(body, filename):
    text = body.decode("utf-8-sig", errors="replace").strip()
    hashes = re.findall(r"(?i)\b[0-9a-f]{64}\b", text)
    return (hashes[0].lower() if len(hashes) == 1 else None, filename in text, text[:300])


def parse_zip(body, interval, year, month, name):
    qa = {"zip_crc": "FAIL", "members": 0, "csv_members": 0, "rows": 0, "parseable_rows": 0,
          "bad_schema": 0, "bad_numeric": 0, "bad_close_time": 0, "off_grid": 0,
          "outside_month": 0, "bad_ohlc": 0, "non_increasing": 0, "timestamp_unit_mismatch": 0,
          "member": "", "error": ""}
    bars, issues = [], []
    try:
        with zipfile.ZipFile(io.BytesIO(body), "r") as z:
            broken = z.testzip()
            qa["zip_crc"] = "PASS" if broken is None else "FAIL"
            members = [m for m in z.infolist() if not m.is_dir()]
            csvs = [m for m in members if m.filename.lower().endswith(".csv")]
            qa["members"], qa["csv_members"] = len(members), len(csvs)
            if broken:
                qa["error"] = f"ZIP CRC failed: {broken}"
                return qa, bars, issues
            if len(members) != 1 or len(csvs) != 1:
                qa["error"] = f"Expected one CSV member; members={len(members)} csv={len(csvs)}"
                return qa, bars, issues
            qa["member"] = csvs[0].filename
            previous = None
            with z.open(csvs[0], "r") as binary, io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                for line, fields in enumerate(csv.reader(text), 1):
                    if not fields or not any(x.strip() for x in fields):
                        continue
                    if line == 1 and fields[0].strip().lower() in {"open_time", "open time", "opentime"}:
                        continue
                    qa["rows"] += 1
                    row_hash = hashlib.sha256(",".join(fields).encode()).hexdigest()
                    if len(fields) != COLS:
                        qa["bad_schema"] += 1
                        issues.append({"archive": name, "line_number": line, "issue": "BAD_SCHEMA", "row_sha256": row_hash})
                        continue
                    try:
                        raw_open, raw_close = int(fields[0]), int(fields[6])
                        dec = [Decimal(x) for x in fields[1:6]]
                        qav, trades = Decimal(fields[7]), int(fields[8])
                        taker_base, taker_quote = Decimal(fields[9]), Decimal(fields[10])
                        ignore = Decimal(fields[11])
                        if not all(x.is_finite() for x in dec + [qav, taker_base, taker_quote, ignore]):
                            raise InvalidOperation
                    except (ValueError, InvalidOperation):
                        qa["bad_numeric"] += 1
                        issues.append({"archive": name, "line_number": line, "issue": "BAD_NUMERIC", "row_sha256": row_hash})
                        continue
                    uo, uc = unit_of(raw_open), unit_of(raw_close)
                    openus, closeus = raw_open * uo, raw_close * uc
                    dt = from_us(openus)
                    if uo != uc:
                        qa["timestamp_unit_mismatch"] += 1
                        issues.append({"archive": name, "line_number": line, "issue": "TIMESTAMP_UNIT_MISMATCH", "row_sha256": row_hash})
                    if closeus != to_us(next_open(dt, interval)) - uo:
                        qa["bad_close_time"] += 1
                        issues.append({"archive": name, "line_number": line, "issue": "BAD_CLOSE_TIME", "row_sha256": row_hash})
                    if not on_grid(dt, interval):
                        qa["off_grid"] += 1
                        issues.append({"archive": name, "line_number": line, "issue": "OFF_GRID_OPEN_TIME", "row_sha256": row_hash})
                    if (dt.year, dt.month) != (year, month):
                        qa["outside_month"] += 1
                        issues.append({"archive": name, "line_number": line, "issue": "OUTSIDE_FILENAME_MONTH", "row_sha256": row_hash})
                    o, h, l, c, v = [float(x) for x in dec]
                    if min(o, h, l, c) <= 0 or v < 0 or qav < 0 or trades < 0 or taker_base < 0 or taker_quote < 0 or h < max(o, c, l) or l > min(o, c, h):
                        qa["bad_ohlc"] += 1
                        issues.append({"archive": name, "line_number": line, "issue": "BAD_OHLC_OR_NEGATIVE_VOLUME", "row_sha256": row_hash})
                    if previous is not None and openus <= previous:
                        qa["non_increasing"] += 1
                        issues.append({"archive": name, "line_number": line, "issue": "NON_INCREASING_OPEN_TIME", "row_sha256": row_hash})
                    previous = openus
                    bars.append({"open_us": openus, "close_us": closeus, "open": o, "high": h,
                                 "low": l, "close": c, "volume": v, "source_archive": name,
                                 "raw_fields": list(fields), "open_unit": uo})
                    qa["parseable_rows"] += 1
    except Exception as exc:
        qa["error"] = f"{type(exc).__name__}: {exc}"
    return qa, bars, issues


def archive_one(interval, year, month, cache):
    name = f"BTCUSDT-{interval}-{year:04d}-{month:02d}.zip"
    rel = f"/monthly/klines/BTCUSDT/{interval}/{name}"
    relsum = rel + ".CHECKSUM"
    url = "https://data.binance.vision/data/spot" + rel
    sumurl = url + ".CHECKSUM"
    row = {"interval": interval, "month": f"{year:04d}-{month:02d}", "filename": name,
           "zip_url": url, "checksum_url": sumurl, "checksum_http": "", "zip_http": "",
           "checksum_sha256": "", "expected_sha256": "", "computed_sha256": "",
           "checksum_name_bound": False, "cache_used": False, "zip_bytes": 0,
           "zip_crc": "NOT_RUN", "members": 0, "csv_members": 0, "rows": 0, "parseable_rows": 0,
           "bad_schema": 0, "bad_numeric": 0, "bad_close_time": 0, "off_grid": 0,
           "outside_month": 0, "bad_ohlc": 0, "non_increasing": 0, "timestamp_unit_mismatch": 0,
           "status": "REVIEW_REQUIRED", "error": ""}
    side = get_bytes(sumurl, relsum)
    row["checksum_http"] = side.get("status", "ERROR")
    gets = 1
    if not side["ok"]:
        row["error"] = "CHECKSUM fetch failed: " + str(side.get("error", side.get("status")))
        return row, [], [{"archive": name, "line_number": 0, "issue": "CHECKSUM_FETCH_FAILED", "row_sha256": ""}], gets
    row["checksum_sha256"] = sha(side["body"])
    expected, bound, _ = parse_checksum(side["body"], name)
    row["expected_sha256"], row["checksum_name_bound"] = expected or "", bound
    if not expected or not bound:
        row["error"] = "CHECKSUM sidecar must contain exactly one hash and the target ZIP filename."
        return row, [], [{"archive": name, "line_number": 0, "issue": "CHECKSUM_BINDING_FAILED", "row_sha256": ""}], gets
    cachefile = cache / interval / f"{year:04d}-{month:02d}" / name
    cachefile.parent.mkdir(parents=True, exist_ok=True)
    body = None
    if cachefile.exists():
        cached = cachefile.read_bytes()
        if sha(cached) == expected:
            body = cached
            row["cache_used"] = True
            row["zip_http"] = "CACHE_HASH_MATCH_FRESH_CHECKSUM"
    if body is None:
        got = get_bytes(url, rel)
        gets += 1
        row["zip_http"] = got.get("status", "ERROR")
        if not got["ok"]:
            row["error"] = "ZIP fetch failed: " + str(got.get("error", got.get("status")))
            return row, [], [{"archive": name, "line_number": 0, "issue": "ZIP_FETCH_FAILED", "row_sha256": ""}], gets
        body = got["body"]
        cachefile.write_bytes(body)
    row["zip_bytes"] = len(body)
    row["computed_sha256"] = sha(body)
    if row["computed_sha256"] != expected:
        row["error"] = "ZIP SHA-256 differs from official sidecar."
        return row, [], [{"archive": name, "line_number": 0, "issue": "ZIP_HASH_MISMATCH", "row_sha256": row["computed_sha256"]}], gets
    qa, bars, issues = parse_zip(body, interval, year, month, name)
    for k in ("zip_crc", "members", "csv_members", "rows", "parseable_rows", "bad_schema", "bad_numeric",
              "bad_close_time", "off_grid", "outside_month", "bad_ohlc", "non_increasing",
              "timestamp_unit_mismatch", "error"):
        row[k] = qa[k]
    if not row["error"] and row["zip_crc"] == "PASS" and row["members"] == 1 and row["csv_members"] == 1 and row["parseable_rows"] > 0:
        row["status"] = "PASS_HASH_CRC_CONTENT" if not issues else "HASH_CRC_PASS_CONTENT_REVIEW"
    else:
        row["status"] = "REVIEW_REQUIRED"
        if not row["error"]:
            row["error"] = "No valid single-CSV archive or no parseable rows."
    return row, bars, issues, gets


def ema(values, span):
    if not values:
        return []
    alpha = 2 / (span + 1)
    out = [values[0]]
    for value in values[1:]:
        out.append(alpha * value + (1-alpha) * out[-1])
    return out


def make_signals(bars, strategy):
    close = [b["close"] for b in bars]
    high = [b["high"] for b in bars]
    low = [b["low"] for b in bars]
    n = len(bars)
    signals = [False] * n
    if strategy == "EMA_12_26":
        fast, slow = ema(close, 12), ema(close, 26)
        return [i >= 25 and fast[i] > slow[i] for i in range(n)]
    if strategy == "RSI14_30_55":
        gains, losses, state = [0.0]*n, [0.0]*n, False
        for i in range(1, n):
            d = close[i] - close[i-1]
            gains[i], losses[i] = max(d, 0), max(-d, 0)
        for i in range(14, n):
            gain, loss = sum(gains[i-13:i+1])/14, sum(losses[i-13:i+1])/14
            value = 100 if loss == 0 and gain > 0 else (50 if gain == loss == 0 else (0 if loss == 0 else 100-100/(1+gain/loss)))
            if not state and value < 30:
                state = True
            elif state and value > 55:
                state = False
            signals[i] = state
        return signals
    if strategy == "DONCHIAN20_10":
        state = False
        for i in range(20, n):
            if not state and close[i] > max(high[i-20:i]):
                state = True
            elif state and close[i] < min(low[i-10:i]):
                state = False
            signals[i] = state
        return signals
    raise ValueError(strategy)


def replay(bars, signal, start, end, fee_bps, slip_bps):
    if end <= start:
        return {"status": "NO_BARS", "return_pct": None, "max_close_drawdown_pct": None,
                "round_trips": 0, "profit_factor": None, "win_rate_pct": None, "exposure_pct": None}
    fee, slip = fee_bps/10000, slip_bps/10000
    cash, qty, basis = 1.0, 0.0, 0.0
    trade_pnls, peak, maxdd, exposure = [], 1.0, 0.0, 0
    for i in range(start, end):
        want = signal[i-1] if i else False
        bar = bars[i]
        if qty > 0 and not want:
            proceeds = qty * bar["open"] * (1-slip) * (1-fee)
            trade_pnls.append(proceeds - basis)
            cash, qty, basis = proceeds, 0.0, 0.0
        if qty == 0 and want:
            basis = cash
            entry = bar["open"] * (1+slip)
            qty = cash / (entry * (1+fee))
            cash = 0.0
        equity = cash + qty * bar["close"]
        peak = max(peak, equity)
        if peak > 0:
            maxdd = min(maxdd, equity/peak - 1)
        exposure += int(qty > 0)
    if qty > 0:
        proceeds = qty * bars[end-1]["close"] * (1-slip) * (1-fee)
        trade_pnls.append(proceeds - basis)
        cash = proceeds
    wins = sum(x for x in trade_pnls if x > 0)
    losses = -sum(x for x in trade_pnls if x < 0)
    return {"status": "COMPUTED", "return_pct": (cash-1)*100,
            "max_close_drawdown_pct": maxdd*100, "round_trips": len(trade_pnls),
            "profit_factor": wins/losses if losses else (None if wins == 0 else "INF"),
            "win_rate_pct": 100*sum(x > 0 for x in trade_pnls)/len(trade_pnls) if trade_pnls else None,
            "exposure_pct": exposure/(end-start)*100}


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def self_test():
    tests = []
    def add(n, ok): tests.append({"test": n, "status": "PASS" if ok else "FAIL"})
    rel = "/monthly/klines/BTCUSDT/4h/BTCUSDT-4h-2020-01.zip"
    add("official_url_exact_host_path", official_url("https://data.binance.vision/data/spot" + rel, rel))
    add("rest_host_rejected", not official_url("https://api.binance.com/api/v3/klines", "/v3/klines"))
    add("lookalike_host_rejected", not official_url("https://data.binance.vision.evil.example/data/spot" + rel, rel))
    add("http_rejected", not official_url("http://data.binance.vision/data/spot" + rel, rel))
    add("ms_timestamp_unit", unit_of(1512367200000) == 1000)
    add("us_timestamp_unit", unit_of(1735689600000000) == 1)
    add("month_boundary", next_open(datetime(2020,12,1,tzinfo=UTC), "1mo") == datetime(2021,1,1,tzinfo=UTC))
    raw = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  BTCUSDT-4h-2020-01.zip"
    parsed, bound, _ = parse_checksum(raw, "BTCUSDT-4h-2020-01.zip")
    add("checksum_exact_binding", parsed == "a"*64 and bound)
    bars = []
    base = datetime(2020,1,1,tzinfo=UTC)
    for i in range(240):
        p = 100 + i*.2 + math.sin(i/4)
        bars.append({"open_us":to_us(base+timedelta(hours=i*4)), "open":p-.1, "high":p+.5, "low":p-.5, "close":p, "volume":1.0})
    sig = make_signals(bars,"EMA_12_26")
    add("signal_length", len(sig) == len(bars) and len(make_signals(bars,"RSI14_30_55")) == len(bars) and len(make_signals(bars,"DONCHIAN20_10")) == len(bars))
    low = replay(bars,sig,0,len(bars),10,5)
    high = replay(bars,sig,0,len(bars),20,20)
    add("higher_friction_not_more_profitable", high["return_pct"] <= low["return_pct"] + 1e-9)
    return {"total":len(tests), "passed":sum(t["status"]=="PASS" for t in tests), "tests":tests}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",default="results/historical_reference_replay")
    ap.add_argument("--cache-dir",default=".cache/aists/binance-monthly-archives")
    args=ap.parse_args()
    root=Path.cwd()
    out=(root/args.output_dir).resolve()
    cache=(root/args.cache_dir).resolve()
    out.mkdir(parents=True,exist_ok=True)
    cache.mkdir(parents=True,exist_ok=True)
    tests=self_test()
    (out/"self_tests.json").write_text(json.dumps(tests,indent=2)+"\n",encoding="utf-8")
    if tests["passed"] != tests["total"]:
        (out/"historical_reference_replay_summary.json").write_text(json.dumps({"task_status":"BLOCKED_SELF_TEST_FAILURE","self_tests":tests},indent=2)+"\n",encoding="utf-8")
        return 2

    start=datetime.now(UTC)
    tasklist=[(i,y,m) for i in INTERVALS for y,m in months()]
    manifest, issues, barsets, gets = [], [], {i:[] for i in INTERVALS}, 0
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures=[pool.submit(archive_one,i,y,m,cache) for i,y,m in tasklist]
        for fut in as_completed(futures):
            try:
                row,bars,iss,nget=fut.result()
            except Exception as exc:
                row={"interval":"UNKNOWN","month":"","filename":"","zip_url":"","checksum_url":"","status":"ERROR","error":f"{type(exc).__name__}: {exc}"}
                bars,iss,nget=[],[],0
            manifest.append(row); issues.extend(iss); gets+=nget
            if row.get("status") in ("PASS_HASH_CRC_CONTENT","HASH_CRC_PASS_CONTENT_REVIEW"):
                barsets[row["interval"]].extend(bars)
    manifest.sort(key=lambda r:(r.get("interval",""),r.get("month","")))
    write_csv(out/"archive_manifest.csv",manifest)
    write_csv(out/"row_issues.csv",issues)

    qa_rows, all_gaps, grid, candidates = [], [], [], []
    for interval in INTERVALS:
        bars=sorted(barsets[interval],key=lambda x:x["open_us"])
        duplicates=sum(bars[i]["open_us"]==bars[i-1]["open_us"] for i in range(1,len(bars)))
        noninc=sum(bars[i]["open_us"]<=bars[i-1]["open_us"] for i in range(1,len(bars)))
        gaps=[]
        for prev,nxt in zip(bars,bars[1:]):
            exp=to_us(next_open(from_us(prev["open_us"]),interval))
            if nxt["open_us"] != exp:
                gaps.append({"interval":interval,"previous_open_utc":from_us(prev["open_us"]).isoformat(),
                             "next_observed_open_utc":from_us(nxt["open_us"]).isoformat(),"expected_next_open_utc":from_us(exp).isoformat()})
        all_gaps.extend(gaps)
        arcs=[m for m in manifest if m.get("interval")==interval]
        notclean=[m for m in arcs if m.get("status")!="PASS_HASH_CRC_CONTENT"]
        digest=hashlib.sha256("".join(f'{b["open_us"]},{b["open"]:.12g},{b["high"]:.12g},{b["low"]:.12g},{b["close"]:.12g},{b["volume"]:.12g}\n' for b in bars).encode()).hexdigest()
        clean=bool(bars) and not notclean and not duplicates and not gaps
        qa_rows.append({"interval":interval,"archives_expected":len(arcs),
                        "archives_clean":sum(m.get("status")=="PASS_HASH_CRC_CONTENT" for m in arcs),
                        "archives_review_or_error":len(notclean),"parsed_bars_from_hash_crc_valid_archives":len(bars),
                        "duplicate_open_times":duplicates,"non_increasing_open_times":noninc,
                        "gap_events":len(gaps),"bars_sha256":digest,
                        "interval_data_gate":"PASS" if clean else "REVIEW_REQUIRED",
                        "policy":"No source row repaired and no gap filled. Parsed rows from hash/CRC-valid archives can inform diagnostics, never source acceptance."})
        if len(bars)<50:
            for strategy in STRATEGIES:
                candidates.append({"candidate_id":f"REF_{interval}_{strategy}","interval":interval,"strategy":strategy,
                                   "reference_status":"INSUFFICIENT_BARS","interval_data_gate":qa_rows[-1]["interval_data_gate"],
                                   "promotion":"NOT_ALLOWED","bars_sha256":digest})
            continue
        for strategy in STRATEGIES:
            sig=make_signals(bars,strategy)
            base={}
            for fee in FEE_BPS:
                for slip in SLIP_BPS:
                    for pname,pstart,pend in PERIODS:
                        idx=[i for i,b in enumerate(bars) if to_us(pstart)<=b["open_us"]<to_us(pend)]
                        if idx:
                            st,en=idx[0],idx[-1]+1
                            metrics=replay(bars,sig,st,en,fee,slip)
                            nrows=en-st
                        else:
                            metrics={"status":"NO_BARS","return_pct":None,"max_close_drawdown_pct":None,"round_trips":0,"profit_factor":None,"win_rate_pct":None,"exposure_pct":None}
                            nrows=0
                        grid.append({"interval":interval,"strategy":strategy,"period":pname,"fee_bps_per_side":fee,"slippage_bps_per_side":slip,
                                     "rows":nrows,"bars_sha256":digest,**metrics})
                        if fee==10 and slip==5: base[pname]=metrics
            dds=[r["max_close_drawdown_pct"] for r in grid if r["interval"]==interval and r["strategy"]==strategy and isinstance(r.get("max_close_drawdown_pct"),(int,float))]
            candidates.append({"candidate_id":f"REF_{interval}_{strategy}","interval":interval,"strategy":strategy,
                "train_return_pct_fee10_slip5":base.get("TRAIN",{}).get("return_pct"),
                "validation_return_pct_fee10_slip5":base.get("VALIDATION",{}).get("return_pct"),
                "consumed_oos_diagnostic_return_pct_fee10_slip5":base.get("CONSUMED_OOS_DIAGNOSTIC",{}).get("return_pct"),
                "train_round_trips":base.get("TRAIN",{}).get("round_trips"),
                "validation_round_trips":base.get("VALIDATION",{}).get("round_trips"),
                "consumed_oos_round_trips":base.get("CONSUMED_OOS_DIAGNOSTIC",{}).get("round_trips"),
                "worst_close_drawdown_pct_across_cost_grid":min(dds) if dds else None,
                "interval_data_gate":qa_rows[-1]["interval_data_gate"],
                "reproduction_status":"INDEPENDENT_REFERENCE_NOT_BIT_IDENTICAL_CP0027",
                "promotion":"NOT_ALLOWED_WITHOUT_FROZEN_RULEBOOK_REVIEW","bars_sha256":digest})
    write_csv(out/"bar_qa_summary.csv",qa_rows)
    write_csv(out/"gap_events.csv",all_gaps)
    write_csv(out/"reference_backtest_grid.csv",grid)
    write_csv(out/"candidate_reference_summary.csv",candidates)
    end=datetime.now(UTC)
    summary={"schema_version":1,"task_status":"COMPLETED_WITH_RESULTS" if any(m.get("status") in ("PASS_HASH_CRC_CONTENT","HASH_CRC_PASS_CONTENT_REVIEW") for m in manifest) else "COMPLETED_NO_VALID_ARCHIVES",
        "started_at_utc":start.isoformat(),"finished_at_utc":end.isoformat(),"elapsed_seconds":round((end-start).total_seconds(),2),
        "month_range_inclusive":f"{FIRST_MONTH[0]:04d}-{FIRST_MONTH[1]:02d}..{LAST_MONTH[0]:04d}-{LAST_MONTH[1]:02d}",
        "intervals":list(INTERVALS),"expected_monthly_archives":len(tasklist),
        "clean_archives":sum(m.get("status")=="PASS_HASH_CRC_CONTENT" for m in manifest),
        "hash_crc_valid_content_review":sum(m.get("status")=="HASH_CRC_PASS_CONTENT_REVIEW" for m in manifest),
        "archive_review_or_error":sum(m.get("status") not in ("PASS_HASH_CRC_CONTENT","HASH_CRC_PASS_CONTENT_REVIEW") for m in manifest),
        "official_get_requests_attempted":gets,"archive_bytes_fetched_or_reused":sum(int(m.get("zip_bytes",0) or 0) for m in manifest),
        "cache_hits":sum(bool(m.get("cache_used")) for m in manifest),
        "source_scope":"Official Binance Spot monthly ZIP and .CHECKSUM objects only; source URL and each redirect are object-path allowlisted.",
        "binance_market_data_rest_api_used":False,"exchange_credentials":False,"orders_or_signing":False,
        "raw_archive_mutation":False,"auto_repair":False,"canonical_source_selected":False,"source_cases_closed":0,"strategy_promoted":False,
        "periods":[{"name":n,"start_utc_inclusive":a.isoformat(),"end_utc_exclusive":b.isoformat(),"note":"2025-2026 is consumed diagnostic, not an untouched holdout."} for n,a,b in PERIODS],
        "strategies":list(STRATEGIES),"fee_bps_per_side":list(FEE_BPS),"slippage_bps_per_side":list(SLIP_BPS),
        "self_tests":tests,"interval_qa":qa_rows,"reference_note":"Diagnostic reference only; not a bit-identical CP-0027 rerun; no promotion.",
        "artifacts":["historical_reference_replay_summary.json","archive_manifest.csv","row_issues.csv","bar_qa_summary.csv","gap_events.csv","reference_backtest_grid.csv","candidate_reference_summary.csv","self_tests.json"]}
    (out/"historical_reference_replay_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
