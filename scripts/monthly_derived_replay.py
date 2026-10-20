#!/usr/bin/env python3
"""Rebuild CP-0026-style monthly bars from official checksum-verified 1d bars.

Available official 1mo monthly archives are cross-checks only. The derived
series is reference data, not an overwrite/canonical-source decision.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import historical_reference_replay as core

UTC=timezone.utc
FIRST=(2017,8)
LAST=(2026,9)
STRATEGIES=core.STRATEGIES
PERIODS=core.PERIODS
FEES=core.FEE_BPS
SLIPS=core.SLIP_BPS


def month_list():
    y,m=FIRST
    while (y,m)<=LAST:
        yield y,m
        if m==12: y,m=y+1,1
        else: m+=1


def dsum(rows, index):
    total=Decimal("0")
    for row in rows: total += Decimal(row["raw_fields"][index])
    return total


def aggregate_month(rows, year, month):
    rows=sorted(rows,key=lambda r:r["open_us"])
    if not rows:
        return None
    raw=[r["raw_fields"] for r in rows]
    start=datetime(year,month,1,tzinfo=UTC)
    end=core.next_open(start,"1mo")
    unit=1 if start>=datetime(2025,1,1,tzinfo=UTC) else 1000
    return {
        "interval":"1mo","year_month":f"{year:04d}-{month:02d}",
        "open_us":core.to_us(start),"close_us":core.to_us(end)-unit,
        "open":Decimal(raw[0][1]),"high":max(Decimal(x[2]) for x in raw),
        "low":min(Decimal(x[3]) for x in raw),"close":Decimal(raw[-1][4]),
        "volume":dsum(rows,5),"quote_volume":dsum(rows,7),
        "trades":sum(int(x[8]) for x in raw),
        "taker_base":dsum(rows,9),"taker_quote":dsum(rows,10),
        "daily_bars":len(rows),"derived_from":"official_1d_archive_bars",
        "source_first_open_utc":core.from_us(rows[0]["open_us"]).isoformat(),
        "source_last_open_utc":core.from_us(rows[-1]["open_us"]).isoformat(),
    }


def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8"); return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)


def self_tests():
    cases=[]
    a=datetime(2020,2,1,tzinfo=UTC)
    rows=[
        {"open_us":core.to_us(a),"raw_fields":["","100","110","90","95","5","","50","10","2","20","0"]},
        {"open_us":core.to_us(datetime(2020,2,2,tzinfo=UTC)),"raw_fields":["","101","112","95","101","7","","75","12","3","30","0"]},
    ]
    m=aggregate_month(rows,2020,2)
    cases.append({"test":"monthly_ohlc_aggregation","status":"PASS" if m and m["open"]==Decimal("100") and m["high"]==Decimal("112") and m["low"]==Decimal("90") and m["close"]==Decimal("101") else "FAIL"})
    cases.append({"test":"monthly_volume_aggregation","status":"PASS" if m and m["volume"]==Decimal("12") and m["quote_volume"]==Decimal("125") and m["trades"]==22 else "FAIL"})
    cases.append({"test":"monthly_close_time","status":"PASS" if m and m["close_us"]==core.to_us(datetime(2020,3,1,tzinfo=UTC))-1000 else "FAIL"})
    parsed,bound,_=core.parse_checksum(b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa BTCUSDT-1mo-2020-02.zip","BTCUSDT-1mo-2020-02.zip")
    cases.append({"test":"checksum_binding","status":"PASS" if parsed=="a"*64 and bound else "FAIL"})
    return {"total":len(cases),"passed":sum(x["status"]=="PASS" for x in cases),"tests":cases}


def main():
    from g0_execution_guard import require_authenticated_g0
    require_authenticated_g0("monthly_derived_replay")
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",default="results/monthly_derived_replay")
    ap.add_argument("--cache-dir",default=".cache/aists/binance-monthly-archives")
    args=ap.parse_args()
    root=Path.cwd(); out=(root/args.output_dir).resolve(); cache=(root/args.cache_dir).resolve()
    out.mkdir(parents=True,exist_ok=True)
    tests=self_tests()
    (out/"self_tests.json").write_text(json.dumps(tests,indent=2)+"\n",encoding="utf-8")
    if tests["passed"]!=tests["total"]:
        (out/"monthly_derived_replay_summary.json").write_text(json.dumps({"task_status":"BLOCKED_SELF_TEST_FAILURE","self_tests":tests},indent=2)+"\n",encoding="utf-8")
        return 2

    started=datetime.now(UTC)
    daily_manifest=[]; daily_issues=[]; daily_bars=[]; daily_gets=0
    with ThreadPoolExecutor(max_workers=10) as pool:
        futs=[pool.submit(core.archive_one,"1d",y,m,cache) for y,m in month_list()]
        for fut in as_completed(futs):
            row,bars,issues,gets=fut.result()
            daily_manifest.append(row); daily_issues.extend(issues); daily_gets+=gets
            if row.get("status") in ("PASS_HASH_CRC_CONTENT","HASH_CRC_PASS_CONTENT_REVIEW"):
                daily_bars.extend(bars)
    daily_manifest.sort(key=lambda r:r["month"])
    daily_bars.sort(key=lambda r:r["open_us"])
    duplicates=sum(daily_bars[i]["open_us"]==daily_bars[i-1]["open_us"] for i in range(1,len(daily_bars)))
    gaps=[]
    for left,right in zip(daily_bars,daily_bars[1:]):
        expected=core.to_us(core.next_open(core.from_us(left["open_us"]),"1d"))
        if right["open_us"]!=expected:
            gaps.append({"previous_open_utc":core.from_us(left["open_us"]).isoformat(),"next_observed_open_utc":core.from_us(right["open_us"]).isoformat(),"expected_next_open_utc":core.from_us(expected).isoformat()})
    daily_clean=(len(daily_manifest)==110 and all(x.get("status")=="PASS_HASH_CRC_CONTENT" for x in daily_manifest) and len(daily_bars)==3332 and duplicates==0 and not gaps)
    daily_digest=hashlib.sha256("".join(f'{r["open_us"]},{r["close"]:.12g},{r["volume"]:.12g}\n' for r in daily_bars).encode()).hexdigest()
    write_csv(out/"daily_source_manifest.csv",daily_manifest)
    write_csv(out/"daily_source_issues.csv",daily_issues)
    (out/"daily_source_qa.json").write_text(json.dumps({"expected_archives":110,"clean_archives":sum(x.get("status")=="PASS_HASH_CRC_CONTENT" for x in daily_manifest),"parseable_bars":len(daily_bars),"duplicates":duplicates,"gap_events":len(gaps),"bars_sha256":daily_digest,"source_gate":"PASS" if daily_clean else "REVIEW_REQUIRED"},indent=2)+"\n",encoding="utf-8")

    groups={}
    for bar in daily_bars:
        dt=core.from_us(bar["open_us"]); groups.setdefault((dt.year,dt.month),[]).append(bar)
    derived=[]
    for y,m in month_list():
        # CP-0026 explicitly excludes the initial partial 2017-08 month from backtests.
        if (y,m)==FIRST:
            continue
        item=aggregate_month(groups.get((y,m),[]),y,m)
        if item: derived.append(item)
    expected_month_count=109
    monthly_direct_manifest=[]; monthly_direct_bars=[]; monthly_gets=0; monthly_issues=[]
    with ThreadPoolExecutor(max_workers=10) as pool:
        futs=[pool.submit(core.archive_one,"1mo",y,m,cache) for y,m in month_list()]
        for fut in as_completed(futs):
            row,bars,issues,gets=fut.result()
            monthly_direct_manifest.append(row); monthly_issues.extend(issues); monthly_gets+=gets
            if row.get("status") in ("PASS_HASH_CRC_CONTENT","HASH_CRC_PASS_CONTENT_REVIEW"):
                monthly_direct_bars.extend(bars)
    monthly_direct_manifest.sort(key=lambda r:r["month"])
    direct_by_month={}
    for bar in monthly_direct_bars:
        dt=core.from_us(bar["open_us"]); direct_by_month[(dt.year,dt.month)]=bar
    crosschecks=[]
    for item in derived:
        key=tuple(map(int,item["year_month"].split("-")))
        direct=direct_by_month.get(key)
        base={"year_month":item["year_month"],"derived_daily_bars":item["daily_bars"],"direct_monthly_available":bool(direct),
              "derived_from_1d_sha256":daily_digest,"status":"","mismatched_columns":""}
        if direct is None:
            base["status"]="DIRECT_MONTHLY_UNAVAILABLE"
            base["mismatched_columns"]=""
        else:
            fields=direct["raw_fields"]
            mismatches=[]
            if direct["open_us"]!=item["open_us"]: mismatches.append("open_time")
            if direct["close_us"]!=item["close_us"]: mismatches.append("close_time")
            for col,idx in [("open",1),("high",2),("low",3),("close",4),("volume",5),("quote_volume",7),("trades",8),("taker_base",9),("taker_quote",10)]:
                if col=="trades":
                    if int(fields[idx])!=item[col]: mismatches.append(col)
                elif Decimal(fields[idx])!=item[col]:
                    mismatches.append(col)
            base["mismatched_columns"]=";".join(mismatches)
            base["status"]="MATCH_EXACT" if not mismatches else "MISMATCH"
        crosschecks.append(base)
    write_csv(out/"derived_monthly_bars.csv",[
        {"year_month":x["year_month"],"open_us":x["open_us"],"close_us":x["close_us"],
         "open":str(x["open"]),"high":str(x["high"]),"low":str(x["low"]),"close":str(x["close"]),
         "volume":str(x["volume"]),"quote_volume":str(x["quote_volume"]),"trades":x["trades"],
         "taker_base":str(x["taker_base"]),"taker_quote":str(x["taker_quote"]),
         "daily_bars":x["daily_bars"],"derived_from":x["derived_from"],"source_first_open_utc":x["source_first_open_utc"],
         "source_last_open_utc":x["source_last_open_utc"]} for x in derived])
    write_csv(out/"monthly_source_crosscheck.csv",crosschecks)
    write_csv(out/"monthly_direct_archive_manifest.csv",monthly_direct_manifest)
    write_csv(out/"monthly_direct_source_issues.csv",monthly_issues)
    all_match=bool(crosschecks) and all(x["status"] in ("MATCH_EXACT","DIRECT_MONTHLY_UNAVAILABLE") for x in crosschecks) and all(x["status"]=="MATCH_EXACT" for x in crosschecks if x["direct_monthly_available"])
    derived_clean=(daily_clean and len(derived)==expected_month_count and all_match)
    bars=[]
    for r in derived:
        bars.append({"open_us":r["open_us"],"close_us":r["close_us"],"open":float(r["open"]),"high":float(r["high"]),
                     "low":float(r["low"]),"close":float(r["close"]),"volume":float(r["volume"]),"source_archive":"DERIVED_FROM_1D"})
    digest=hashlib.sha256("".join(f'{b["open_us"]},{b["open"]:.12g},{b["high"]:.12g},{b["low"]:.12g},{b["close"]:.12g},{b["volume"]:.12g}\n' for b in bars).encode()).hexdigest()
    grid=[]; candidates=[]
    for strategy in STRATEGIES:
        sig=core.make_signals(bars,strategy); baselines={}
        for fee in FEES:
            for slip in SLIPS:
                for pname,start,end in PERIODS:
                    ids=[i for i,b in enumerate(bars) if core.to_us(start)<=b["open_us"]<core.to_us(end)]
                    if ids:
                        st,en=ids[0],ids[-1]+1; metric=core.replay(bars,sig,st,en,fee,slip); nrows=en-st
                    else:
                        metric={"status":"NO_BARS","return_pct":None,"max_close_drawdown_pct":None,"round_trips":0,"profit_factor":None,"win_rate_pct":None,"exposure_pct":None}; nrows=0
                    grid.append({"interval":"1mo_DERIVED_FROM_1D","strategy":strategy,"period":pname,"fee_bps_per_side":fee,"slippage_bps_per_side":slip,"rows":nrows,"bars_sha256":digest,**metric})
                    if fee==10 and slip==5: baselines[pname]=metric
        dds=[x["max_close_drawdown_pct"] for x in grid if x["strategy"]==strategy and isinstance(x.get("max_close_drawdown_pct"),(int,float))]
        candidates.append({"candidate_id":f"REF_1mo_DERIVED_{strategy}","strategy":strategy,
            "train_return_pct_fee10_slip5":baselines.get("TRAIN",{}).get("return_pct"),
            "validation_return_pct_fee10_slip5":baselines.get("VALIDATION",{}).get("return_pct"),
            "consumed_oos_diagnostic_return_pct_fee10_slip5":baselines.get("CONSUMED_OOS_DIAGNOSTIC",{}).get("return_pct"),
            "train_round_trips":baselines.get("TRAIN",{}).get("round_trips"),
            "validation_round_trips":baselines.get("VALIDATION",{}).get("round_trips"),
            "consumed_oos_round_trips":baselines.get("CONSUMED_OOS_DIAGNOSTIC",{}).get("round_trips"),
            "worst_close_drawdown_pct_across_cost_grid":min(dds) if dds else None,
            "derived_monthly_data_gate":"PASS_REFERENCE_DERIVATION" if derived_clean else "REVIEW_REQUIRED",
            "direct_archive_crosschecks_exact":sum(x["status"]=="MATCH_EXACT" for x in crosschecks),
            "direct_archive_crosschecks_mismatch":sum(x["status"]=="MISMATCH" for x in crosschecks),
            "direct_monthly_missing":sum(x["status"]=="DIRECT_MONTHLY_UNAVAILABLE" for x in crosschecks),
            "bars_sha256":digest,"reproduction_status":"CP0026_METHOD_ALIGNMENT_ATTEMPT_NOT_BIT_IDENTICAL_CP0027",
            "promotion":"NOT_ALLOWED_WITHOUT_FROZEN_RULEBOOK_REVIEW"})
    write_csv(out/"monthly_reference_backtest_grid.csv",grid)
    write_csv(out/"monthly_candidate_reference_summary.csv",candidates)
    finished=datetime.now(UTC)
    summary={"schema_version":1,"task_status":"COMPLETED_WITH_RESULTS" if derived else "NO_DERIVED_MONTHS",
        "started_at_utc":started.isoformat(),"finished_at_utc":finished.isoformat(),"elapsed_seconds":round((finished-started).total_seconds(),2),
        "source_daily_expected_archives":110,"source_daily_clean_archives":sum(x.get("status")=="PASS_HASH_CRC_CONTENT" for x in daily_manifest),
        "source_daily_bars":len(daily_bars),"source_daily_gate":"PASS" if daily_clean else "REVIEW_REQUIRED",
        "derived_month_count":len(derived),"expected_month_count":expected_month_count,
        "direct_monthly_archive_clean":sum(x.get("status")=="PASS_HASH_CRC_CONTENT" for x in monthly_direct_manifest),
        "direct_monthly_archive_missing_or_review":sum(x.get("status")!="PASS_HASH_CRC_CONTENT" for x in monthly_direct_manifest),
        "direct_monthly_crosschecks_exact":sum(x["status"]=="MATCH_EXACT" for x in crosschecks),
        "direct_monthly_crosschecks_mismatch":sum(x["status"]=="MISMATCH" for x in crosschecks),
        "direct_monthly_unavailable":sum(x["status"]=="DIRECT_MONTHLY_UNAVAILABLE" for x in crosschecks),
        "derived_monthly_data_gate":"PASS_REFERENCE_DERIVATION" if derived_clean else "REVIEW_REQUIRED",
        "daily_and_monthly_checksum_get_requests":daily_gets+monthly_gets,
        "network_scope":"Official data.binance.vision monthly daily and 1mo kline ZIP/CHECKSUM objects; same-object redirects restricted to allowlisted distribution hosts.",
        "binance_rest_api_used":False,"raw_archive_mutation":False,"repair":False,"canonical_source_selected":False,"source_cases_closed":0,"strategy_promoted":False,
        "reference_replay_note":"CP-0026-style monthly bars derived from 1d data; available 1mo archives are validation crosschecks. Not a bit-identical reproduction and not promotion.",
        "self_tests":tests,"artifacts":["monthly_derived_replay_summary.json","daily_source_manifest.csv","daily_source_issues.csv","daily_source_qa.json","derived_monthly_bars.csv","monthly_source_crosscheck.csv","monthly_direct_archive_manifest.csv","monthly_direct_source_issues.csv","monthly_reference_backtest_grid.csv","monthly_candidate_reference_summary.csv","self_tests.json"]}
    (out/"monthly_derived_replay_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
