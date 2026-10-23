#!/usr/bin/env python3
"""Compare official Spot 1m and Spot 5m archive gaps for known failed months.

Diagnostic only: this script never fills, drops, or reconstructs candles.
"""
from __future__ import annotations
import argparse, calendar, csv, hashlib, io, json, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://data.binance.vision"
SYMBOL = "BTCUSDT"
MONTHS = ["2020-02","2020-03","2020-04","2020-06","2020-11","2020-12",
          "2021-02","2021-03","2021-04","2021-08","2021-09","2023-03"]

def get(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent":"aists-btcusdt-research-runner/1.0"}), timeout=90) as r:
        if r.status != 200:
            raise ValueError(f"HTTP {r.status}: {url}")
        return r.read()

def expected_count(month: str, interval_ms: int) -> int:
    y, m = map(int, month.split("-"))
    return calendar.monthrange(y, m)[1] * 86400000 // interval_ms

def load_archive(month: str, interval: str, interval_ms: int) -> dict:
    url = f"{BASE}/data/spot/monthly/klines/{SYMBOL}/{interval}/{SYMBOL}-{interval}-{month}.zip"
    body = get(url)
    sidecar = get(url + ".CHECKSUM").decode("utf-8").strip().split()[0].lower()
    digest = hashlib.sha256(body).hexdigest()
    if digest != sidecar:
        raise ValueError(f"{interval} checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        members = [n for n in z.namelist() if not n.endswith("/")]
        if len(members) != 1:
            raise ValueError(f"{interval}: expected one CSV member, got {len(members)}")
        rows = list(csv.reader(io.StringIO(z.read(members[0]).decode("utf-8-sig"))))
    if rows and rows[0][0].strip().lower() in ("open_time", "open_time_ms"):
        rows = rows[1:]
    times = []
    candle_rows = []
    malformed = []
    for idx, row in enumerate(rows, 1):
        if len(row) != 12:
            malformed.append({"row":idx,"reason":f"columns={len(row)}"})
            continue
        raw = int(row[0]); ts = raw // 1000 if raw >= 100_000_000_000_000 else raw
        times.append(ts)
        candle_rows.append({"open_time_ms": ts, "open": row[1], "high": row[2], "low": row[3], "close": row[4], "volume": row[5], "close_time_raw": row[6]})
    anomalies = []
    for prev, cur in zip(times, times[1:]):
        if cur - prev != interval_ms:
            anomalies.append({"after_ms":prev,"before_ms":cur,"delta_ms":cur-prev,
                              "missing_intervals":max(0,(cur-prev)//interval_ms-1),
                              "ordered":cur>prev})
    return {"month":month,"interval":interval,"url":url,"archive_sha256":digest,
            "checksum_matches":True,"rows":len(rows),"valid_timestamp_rows":len(times),
            "expected_rows":expected_count(month,interval_ms),
            "row_count_delta":expected_count(month,interval_ms)-len(rows),
            "first_open_time_ms":times[0] if times else None,
            "last_open_time_ms":times[-1] if times else None,
            "gap_or_order_anomaly_count":len(anomalies),"first_anomalies":anomalies[:100],
            "malformed_rows":malformed[:10], "candle_rows":candle_rows}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",default="artifacts/btcusdt-spot-gap-reconciliation")
    args=p.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    results=[]
    for month in MONTHS:
        item={"month":month}
        try:
            one=load_archive(month,"1m",60000)
            five=load_archive(month,"5m",300000)
            one_gaps=[]
            for gap in one["first_anomalies"]:
                if gap["ordered"]:
                    start=gap["after_ms"]+60000
                    end=gap["before_ms"]
                    first_bucket=(start//300000)*300000
                    last_bucket=(end//300000)*300000
                    one_gaps.append({**gap,"missing_span_start_ms":start,"missing_span_end_exclusive_ms":end,
                                     "aligned_5m_bucket_start_ms":first_bucket,
                                     "aligned_5m_bucket_end_ms":last_bucket,
                                     "possible_5m_buckets_touched":max(1,(last_bucket-first_bucket)//300000+1)})
            def context(rows, gaps, radius=3):
                selected = {}
                for gap in gaps:
                    before = gap["after_ms"]; after = gap["before_ms"]
                    left = [r for r in rows if r["open_time_ms"] <= before][-radius:]
                    right = [r for r in rows if r["open_time_ms"] >= after][:radius]
                    selected[f"{before}->{after}"] = {"before_rows":left,"after_rows":right}
                return selected
            one_context = context(one["candle_rows"], one["first_anomalies"])
            five_context = context(five["candle_rows"], five["first_anomalies"])
            # Keep the report compact: retain boundary rows only, not full monthly candles.
            one.pop("candle_rows", None); five.pop("candle_rows", None)
            item.update({"spot_1m":one,"spot_5m":five, "boundary_context":{"spot_1m":one_context,"spot_5m":five_context},
                         "comparison":{"one_minute_gap_count":one["gap_or_order_anomaly_count"],
                                       "five_minute_gap_count":five["gap_or_order_anomaly_count"],
                                       "one_minute_row_delta":one["row_count_delta"],
                                       "five_minute_row_delta":five["row_count_delta"],
                                       "one_minute_gap_spans":one_gaps,
                                       "note":"Descriptive comparison only; no candle was synthesized or excluded."}})
            item["status"]="INSPECT" if one["gap_or_order_anomaly_count"] or five["gap_or_order_anomaly_count"] else "NO_GAPS_FOUND"
        except Exception as exc:
            item.update({"status":"ERROR","error":f"{type(exc).__name__}: {exc}"})
        results.append(item)
        print(json.dumps({"month":month,"status":item["status"],
                          "spot_1m":item.get("spot_1m",{}).get("rows"),
                          "spot_5m":item.get("spot_5m",{}).get("rows"),
                          "comparison":item.get("comparison"),"error":item.get("error")},ensure_ascii=False),flush=True)
    report={"gate":"SPOT-1M-5M-GAP-RECONCILIATION","created_utc":datetime.now(timezone.utc).isoformat(),
            "purpose":"Compare official Spot 1m and Spot 5m source timestamps for known failed months.",
            "months":MONTHS,"results":results,
            "summary":{"months_requested":len(MONTHS),"completed":sum("comparison" in r for r in results),
                       "errors":sum(r["status"]=="ERROR" for r in results)},
            "limitations":["No gap filling or candle reconstruction.","Checksum match verifies archive bytes, not correctness or continuity.",
                           "The comparison does not prove whether gaps are valid no-trade intervals or archive omissions."]}
    path=out/"btc-usdt-spot-1m-5m-gap-reconciliation.json"
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"report":str(path),**report["summary"]},indent=2),flush=True)
    return 0 if report["summary"]["completed"]==len(MONTHS) else 1
if __name__=="__main__":
    raise SystemExit(main())
