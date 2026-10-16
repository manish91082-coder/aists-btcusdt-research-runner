#!/usr/bin/env python3
"""Read-only triage of the already-published CP-0107 exact-date daily-reference audit."""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def now(): return datetime.now(timezone.utc).isoformat()
def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def read_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def read_csv(p):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write_json(p,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p,rows):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader()
        if rows:w.writerows(rows)
def sha_file(p): return sha(Path(p).read_bytes())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",required=True)
    ap.add_argument("--output-dir",default="results/cp0093_daily_reference_discrepancy_triage")
    a=ap.parse_args();started=now();source_dir=(ROOT/a.source_dir).resolve();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    checks=[]
    def ck(n,ok,d): checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    try:
        names=[
          "CP0107_CP0041_DailyReference_Period_Summary.csv",
          "CP0107_CP0041_DailyReference_Archive_Manifest.csv",
          "CP0107_CP0041_DailyReference_RawRow_Comparison.csv",
          "CP0107_CP0041_DailyReference_MissingExpectedKeys.csv",
          "CP0107_CP0041_DailyReference_Queue_Snapshot.csv",
          "CP0107_CP0041_MonthlyArchive_Manifest_Subset.csv"]
        summary_path=source_dir/"CP0107_CP0041_DailyReference_Acquisition_Summary.json"
        inputs={n:source_dir/n for n in names}
        missing_files=[str(p) for p in [summary_path,*inputs.values()] if not p.is_file()]
        ck("all_published_input_files_present",not missing_files,missing_files or "source summary + 6 CSVs present")
        if missing_files: raise ValueError("Missing acquisition evidence: "+", ".join(missing_files))
        src=read_json(summary_path)
        ck("source_acquisition_98_checks_pass",src.get("status")=="PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED" and src.get("checks_passed")==98 and src.get("checks_total")==98,{"status":src.get("status"),"checks":str(src.get("checks_passed"))+"/"+str(src.get("checks_total"))})
        source_outputs=src.get("outputs",{})
        for name,p in inputs.items():
            b=p.read_bytes();rec=source_outputs.get(name,{})
            ok=bool(rec) and len(b)==rec.get("bytes") and sha(b)==rec.get("sha256")
            if rec.get("rows") is not None: ok=ok and len(read_csv(p))==rec.get("rows")
            ck("source_hash_size:"+name,ok,{"actual_bytes":len(b),"actual_sha256":sha(b),"source_record":rec})
        periods=read_csv(inputs[names[0]]);archives=read_csv(inputs[names[1]]);rows=read_csv(inputs[names[2]])
        missing=read_csv(inputs[names[3]]);queue=read_csv(inputs[names[4]]);monthly=read_csv(inputs[names[5]])
        ck("source_denominators",len(periods)==16 and len(archives)==16 and len(rows)==1992 and len(missing)==10 and len(queue)==16 and len(monthly)==14,
           {"periods":len(periods),"archives":len(archives),"comparison_rows":len(rows),"missing_expected":len(missing),"queue":len(queue),"monthly":len(monthly)})
        rel=Counter(r.get("row_relation","") for r in rows)
        divergent=[r for r in rows if r.get("row_relation")=="SHARED_RAW_DIVERGENT"]
        economic=[r for r in divergent if int(r.get("economic_differing_field_count") or 0)>0]
        raw_field_counts=Counter();economic_field_counts=Counter();signature_counts=Counter()
        grouped=defaultdict(list)
        for r in rows:
            grouped[r.get("case_id","")].append(r)
            if r.get("row_relation")!="SHARED_RAW_DIVERGENT": continue
            raw=sorted(x for x in r.get("differing_raw_fields","").split(";") if x)
            econ=sorted(x for x in r.get("economic_differing_fields","").split(";") if x)
            signature_counts[";".join(raw) if raw else "UNSPECIFIED"]+=1
            raw_field_counts.update(raw);economic_field_counts.update(econ)
        ignore_only=sum(1 for r in divergent if sorted(x for x in r.get("differing_raw_fields","").split(";") if x)==["ignore"])
        close_plus_ignore=sum(1 for r in divergent if sorted(x for x in r.get("differing_raw_fields","").split(";") if x)==["close_time","ignore"])
        unique_keys={(r.get("case_id",""),r.get("interval",""),r.get("open_time_ms","")) for r in rows}
        ck("comparison_row_keys_unique",len(unique_keys)==len(rows),{"rows":len(rows),"unique_case_interval_open_keys":len(unique_keys)})
        ck("independent_relation_counts_match_source_summary",
           rel.get("SHARED_RAW_EXACT",0)==1550 and rel.get("SHARED_RAW_DIVERGENT",0)==432 and rel.get("MONTHLY_ONLY_KEY",0)==10 and rel.get("DAILY_ONLY_KEY",0)==0 and len(economic)==14,
           {"relations":dict(rel),"economic_rows":len(economic)})
        ck("divergence_classes_reconcile",ignore_only==415 and close_plus_ignore==3 and len(economic)==14 and ignore_only+close_plus_ignore+len(economic)==len(divergent),
           {"ignore_only":ignore_only,"close_time_plus_ignore":close_plus_ignore,"economic":len(economic),"all_divergent":len(divergent)})
        ck("all_archive_sidecar_pairs_and_monthly_rows_pass",
           len(archives)==16 and all(r.get("fetch_status")=="PASS" and r.get("zip_crc")=="PASS" and r.get("sidecar_token_matches_zip")=="True" for r in archives) and
           len(monthly)==14 and all(r.get("status")=="MATCH" and r.get("zip_crc")=="PASS" for r in monthly),
           {"daily_zip_sidecar_pairs":len(archives),"monthly_archives":len(monthly)})
        ck("source_authority_and_raw_mutation_guards",
           all(r.get("disposition")=="OPEN_REVIEW_REQUIRED" and r.get("source_authority")=="NONE" and r.get("timestamp_shifted_or_rounded")=="False" and r.get("synthetic_candle_created")=="False" for r in rows) and
           src.get("canonical_source_selected") is False and src.get("source_cases_closed")==0,
           "all raw comparison rows remain open; no source authority, no case closure, no timestamp/candle changes")
        period_by={r["case_id"]:r for r in periods}
        archive_by={r["case_id"]:r for r in archives}
        missing_by=Counter(r["case_id"] for r in missing)
        case_rows=[]
        for item in queue:
            cid=item["case_id"];p=period_by[cid];ar=archive_by[cid];g=grouped[cid]
            c=Counter(r.get("row_relation","") for r in g)
            eco=[r for r in g if int(r.get("economic_differing_field_count") or 0)>0]
            ign=sum(1 for r in g if r.get("row_relation")=="SHARED_RAW_DIVERGENT" and sorted(x for x in r.get("differing_raw_fields","").split(";") if x)==["ignore"])
            cti=sum(1 for r in g if r.get("row_relation")=="SHARED_RAW_DIVERGENT" and sorted(x for x in r.get("differing_raw_fields","").split(";") if x)==["close_time","ignore"])
            gap=int(missing_by.get(cid,0));div=c.get("SHARED_RAW_DIVERGENT",0)
            if eco and gap: status="ECONOMIC_AND_COVERAGE_REVIEW_REQUIRED"
            elif eco: status="ECONOMIC_SOURCE_CONFLICT_REVIEW_REQUIRED"
            elif gap: status="MISSING_KEY_COVERAGE_REVIEW_REQUIRED"
            elif div: status="NON_ECONOMIC_RAW_FIELD_REVIEW_REQUIRED"
            else: status="RAW_MATCH_DIAGNOSTIC_ONLY_SOURCE_AUTHORITY_OPEN"
            case_rows.append({
              "case_id":cid,"interval":item["interval"],"utc_date":item["utc_date"],"daily_zip_filename":item["daily_zip_filename"],
              "daily_zip_sha256":ar.get("zip_sha256",""),"daily_sidecar_sha256":ar.get("sidecar_sha256",""),
              "sidecar_token_matches_zip":ar.get("sidecar_token_matches_zip",""),"zip_crc":ar.get("zip_crc",""),
              "monthly_archive_filename":p.get("monthly_archive_filename",""),"monthly_archive_sha256":p.get("monthly_archive_sha256",""),
              "shared_open_keys":int(p.get("shared_open_keys","0")),"exact_raw_pairs":int(p.get("exact_raw_row_pairs","0")),
              "divergent_raw_pairs":int(p.get("divergent_raw_row_pairs","0")),"economic_divergent_pairs":len(eco),
              "ignore_only_pairs":ign,"close_time_plus_ignore_pairs":cti,
              "daily_only_keys":int(p.get("daily_only_open_keys","0")),"monthly_only_keys":int(p.get("monthly_only_open_keys","0")),
              "absent_expected_grid_keys":gap,"economic_differing_fields":";".join(sorted(economic_field_counts.keys())) if eco else "",
              "triage_status":status,"source_authority":"NONE","case_closed":"False"})
        econ_columns=["case_id","interval","utc_date","open_time_ms","open_time_utc","differing_raw_fields","economic_differing_fields",
          "monthly_open","daily_open","monthly_high","daily_high","monthly_low","daily_low","monthly_close","daily_close",
          "monthly_volume","daily_volume","monthly_quote_asset_volume","daily_quote_asset_volume","monthly_number_of_trades","daily_number_of_trades",
          "monthly_taker_buy_base_asset_volume","daily_taker_buy_base_asset_volume","monthly_taker_buy_quote_asset_volume","daily_taker_buy_quote_asset_volume",
          "monthly_close_time","daily_close_time","monthly_ignore","daily_ignore","disposition","source_authority"]
        econ_rows=[{k:r.get(k,"") for k in econ_columns} for r in economic]
        missing_rows=[{k:r.get(k,"") for k in ["case_id","interval","utc_date","expected_open_time_ms","expected_open_time_utc","status","archive_filename","archive_sha256","synthetic_candle_created"]} for r in missing]
        field_rows=[{"field":k,"raw_differgent_row_count":v,"economic_differgent_row_count":economic_field_counts.get(k,0)} for k,v in sorted(raw_field_counts.items())]
        signature_rows=[{"raw_difference_signature":k,"row_count":v,"interpretation":"Diagnostic only; source authority remains NONE"} for k,v in sorted(signature_counts.items(),key=lambda x:(-x[1],x[0]))]
        status="PASS_DAILY_REFERENCE_DISCREPANCY_TRIAGE_COMPLETE_SOURCE_AUTHORITY_OPEN" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_DAILY_REFERENCE_TRIAGE"
        outputs={
          "CP0093_DailyReference_Case_Triage.csv":case_rows,
          "CP0093_Economic_Divergence_14_Row_Detail.csv":econ_rows,
          "CP0093_MonthlyOnly_10_Key_Review.csv":missing_rows,
          "CP0093_Field_Divergence_Counts.csv":field_rows,
          "CP0093_Raw_Difference_Signature_Counts.csv":signature_rows}
        for name,data in outputs.items():write_csv(out/name,data)
        report=[
          "# CP-0093: Daily-reference discrepancy triage","",
          "Status: "+status,"",
          "## Evidence integrity",
          "- Source audit: "+str(src.get("status"))+", checks "+str(src.get("checks_passed"))+"/"+str(src.get("checks_total"))+" PASS.",
          "- Daily references: 16 ZIP/.CHECKSUM pairs reused from previous Actions artifact 11993600932; archive hashes matched sidecar tokens and ZIP CRC passed 16/16. This triage downloaded zero new archives.",
          "- Monthly archives: 14 cached ZIPs matched the frozen CP-0041 manifest and CRC; downloads=0.","",
          "## Raw-row results (exact open-time key; raw tokens preserved)",
          "- Union rows: 1992; shared keys: 1982; exact raw pairs: 1550; divergent raw pairs: 432.",
          "- Divergence classes: 415 ignore-only rows; 3 close_time-plus-ignore rows; 14 economic-field divergent rows.",
          "- Daily-only keys: 0; monthly-only keys: 10; absent expected-grid keys: 10. Coverage review is required for the two 2017-12-04 periods at 5m and 15m.",
          "- Economic field counts: "+json.dumps(dict(sorted(economic_field_counts.items())),sort_keys=True)+".","",
          "## Decision boundary",
          "- All 16 target cases remain open for source-authority review. Canonical source NONE; cases closed=0.",
          "- The original worklist and market-data rows are not mutated. No timestamp shifting/rounding, row merge/replacement/deletion, synthetic candles, backtest or strategy promotion.",
          "- Global G0 remains BLOCKED_GLOBAL; G2 remains FAIL for the current 23 candidates; G7 remains LIVE_BLOCKED.","",
          "## Next bounded action",
          "- Review the 14 exact-key economic conflicts and 10 monthly-only keys against the frozen CP-0040 rulebook, one evidence-linked case at a time. Do not auto-prefer the daily or monthly archive."
        ]
        report_path=out/"CP0093_DailyReference_Discrepancy_Triage_Report_HI.md"
        report_path.write_text("\n".join(report)+"\n",encoding="utf-8")
        out_manifest={}
        for name in outputs:
            p=out/name;out_manifest[name]={"bytes":p.stat().st_size,"sha256":sha_file(p),"rows":len(read_csv(p))}
        out_manifest[report_path.name]={"bytes":report_path.stat().st_size,"sha256":sha_file(report_path),"rows":None}
        summary={
          "schema_version":1,"checkpoint":"CP-0093","task":"cp0093_daily_reference_discrepancy_triage","status":status,
          "started_at_utc":started,"finished_at_utc":now(),"input_source_run_id":38909366995,
          "source_status":src.get("status"),"source_checks":str(src.get("checks_passed"))+"/"+str(src.get("checks_total")),
          "source_evidence_hashes":{n:{"bytes":p.stat().st_size,"sha256":sha_file(p)} for n,p in inputs.items()},
          "comparison":{"union_open_key_rows":len(rows),"shared_open_keys":rel.get("SHARED_RAW_EXACT",0)+rel.get("SHARED_RAW_DIVERGENT",0),
            "exact_raw_row_pairs":rel.get("SHARED_RAW_EXACT",0),"divergent_raw_row_pairs":rel.get("SHARED_RAW_DIVERGENT",0),
            "ignore_only_pairs":ignore_only,"close_time_plus_ignore_pairs":close_plus_ignore,"economic_field_divergent_pairs":len(economic),
            "economic_field_count_by_field":dict(economic_field_counts),"daily_only_keys":rel.get("DAILY_ONLY_KEY",0),
            "monthly_only_keys":rel.get("MONTHLY_ONLY_KEY",0),"missing_expected_grid_keys":len(missing),
            "periods_complete_expected_grid":sum(1 for r in periods if int(r.get("monthly_only_open_keys","0"))==0 and int(r.get("daily_only_open_keys","0"))==0),
            "periods_open_coverage_review":sum(1 for r in periods if int(r.get("monthly_only_open_keys","0"))>0 or int(r.get("daily_only_open_keys","0"))>0),
            "case_triage_rows":len(case_rows),"cases_with_economic_divergence":sum(1 for r in case_rows if r["economic_divergent_pairs"]>0),
            "cases_with_missing_expected_grid_keys":sum(1 for r in case_rows if int(r["absent_expected_grid_keys"])>0)},
          "checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
          "outputs":out_manifest,"network_used":False,"archive_downloads":0,"source_bytes_modified":False,
          "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
          "unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED",
          "production_candidate_build":False,"backtest_rerun":False,"strategy_promoted":False}
        write_json(out/"CP0093_DailyReference_Discrepancy_Triage_Summary.json",summary)
        print(json.dumps({"status":status,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
          "union_rows":len(rows),"exact":rel.get("SHARED_RAW_EXACT",0),"divergent":rel.get("SHARED_RAW_DIVERGENT",0),
          "economic":len(economic),"monthly_only":rel.get("MONTHLY_ONLY_KEY",0),"missing_expected":len(missing),
          "source_authority":"NONE","cases_closed":0,"network_used":False,"g0":"BLOCKED_GLOBAL"},ensure_ascii=False,sort_keys=True))
        return 0 if status.startswith("PASS") else 1
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0093","task":"cp0093_daily_reference_discrepancy_triage",
          "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),
          "error_type":type(exc).__name__,"error":str(exc),"checks":checks,"network_used":False,
          "canonical_source_selected":False,"source_cases_closed":0,"g0":"BLOCKED_GLOBAL","g7":"LIVE_BLOCKED"}
        write_json(out/"CP0093_DailyReference_Discrepancy_Triage_Summary.json",summary)
        (out/"CP0093_DailyReference_Discrepancy_Triage_Report_HI.md").write_text(
          "# CP-0093 Daily-reference discrepancy triage\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\n"+type(exc).__name__+": "+str(exc)+"\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1
if __name__=="__main__":raise SystemExit(main())
