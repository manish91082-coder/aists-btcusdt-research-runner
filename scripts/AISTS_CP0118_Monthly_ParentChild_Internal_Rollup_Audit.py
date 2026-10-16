#!/usr/bin/env python3
"""CP-0118: exact Decimal parent-child rollups within frozen source rows."""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 "row_evidence_git_blob_sha1":"5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9",
 "bucket_snapshot_git_blob_sha1":"6e32188472ab45b43e1b90fe138399818c937277",
 "cp0117_pointer_git_blob_sha1":"1515a6f07dbb5a8b84e8de05ce3794558feb0bbf",
 "cp0117_report_git_blob_sha1":"cee4dd57a8a7a42b99cd0934177a3540f26834cb",
 "rulebook_sha256":"5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0",
}
METRICS=("open","high","low","close","volume","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume")
SUM_FIELDS=("volume","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume")

def blob_sha1(p):
 b=p.read_bytes()
 return hashlib.sha1(("blob "+str(len(b))+"\0").encode("utf-8")+b).hexdigest()
def sha256_file(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def read_csv(p):
 with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def read_json(p):return json.loads(p.read_text(encoding="utf-8"))
def write_csv(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--row-evidence",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv")
 ap.add_argument("--bucket-snapshot",default="evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv")
 ap.add_argument("--rulebook",default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
 ap.add_argument("--cp0117-pointer",default="evidence/source_adjudication/CP0117_Rulebook_Bound_Blocker_Disposition_Current.json")
 ap.add_argument("--cp0117-report",default="evidence/source_adjudication/CP0117_Rulebook_Bound_Blocker_Disposition_Report_HI.md")
 ap.add_argument("--output-dir",default="results/cp0118_monthly_parent_child_rollup")
 a=ap.parse_args()
 raw={"row_evidence":a.row_evidence,"bucket_snapshot":a.bucket_snapshot,"rulebook":a.rulebook,"cp0117_pointer":a.cp0117_pointer,"cp0117_report":a.cp0117_report}
 paths={k:(ROOT/v).resolve() for k,v in raw.items()};out=(ROOT/a.output_dir).resolve()
 if any(ROOT not in p.parents for p in list(paths.values())+[out]):raise ValueError("Path escapes repository root")
 for k,p in paths.items():
  if not p.is_file():raise FileNotFoundError(k+": "+str(p))
 out.mkdir(parents=True,exist_ok=True)
 identities={k+"_git_blob_sha1":blob_sha1(p) for k,p in paths.items() if k!="rulebook"}
 identities["rulebook_sha256"]=sha256_file(paths["rulebook"])
 checks=[]
 def ck(name,ok,detail):checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":detail})
 for k,v in EXPECTED.items():ck("frozen_identity_"+k,identities.get(k)==v,{"actual":identities.get(k),"expected":v})
 ptr=read_json(paths["cp0117_pointer"])
 ptr_ok=ptr.get("checkpoint")=="CP-0117" and ptr.get("status")=="PASS_RULEBOOK_BOUND_NONROW_DISPOSITION_G0_STILL_BLOCKED" and ptr.get("report",{}).get("git_blob_sha1")==identities["cp0117_report_git_blob_sha1"]
 ck("CP0117_pointer_and_report_linkage",ptr_ok,{"status":ptr.get("status"),"report_pointer_sha1":ptr.get("report",{}).get("git_blob_sha1"),"actual_report_sha1":identities["cp0117_report_git_blob_sha1"]})
 ck("CP0117_keeps_11_cases_open",ptr.get("decision",{}).get("unresolved_aggregation_blockers")==11 and ptr.get("decision",{}).get("source_cases_closed")==0,ptr.get("decision",{}))
 records=read_csv(paths["row_evidence"]);snapshot=read_csv(paths["bucket_snapshot"])
 if len(records)!=78 or len(snapshot)!=11:raise ValueError("Frozen evidence cardinality mismatch")
 cases=[];detail_rows=[];duplicate_count=0;duplicate_conflicts=[]
 for snap in snapshot:
  cid=snap["case_id"]
  case_rows=[r for r in records if r.get("bucket_case_id")==cid and r.get("row_found")=="True"]
  source_results={}
  for source in ("DAILY","MONTHLY"):
   by_key={}
   for r in case_rows:
    if r.get("source")!=source:continue
    key=(r.get("interval",""),r.get("expected_open_time_ms",""))
    if key in by_key:
     duplicate_count+=1
     old=by_key[key]
     compare_fields=["raw_"+m for m in METRICS]+["raw_open_time","raw_close_time","source_archive_filename","source_archive_sha256"]
     if any(old.get(f)!=r.get(f) for f in compare_fields):duplicate_conflicts.append({"case_id":cid,"source":source,"key":key})
    else:by_key[key]=r
   unique=list(by_key.values())
   children=sorted([r for r in unique if r.get("role")=="CHILD"],key=lambda r:int(r["expected_open_time_ms"]))
   parents=[r for r in unique if r.get("role")=="PARENT"]
   if len(parents)!=1 or len(children)<2:
    source_results[source]={"status":"FAIL_PARENT_CHILD_CARDINALITY","children":len(children),"parents":len(parents)}
    continue
   parent=parents[0]
   roll={
    "open":Decimal(children[0]["raw_open"]),
    "high":max(Decimal(r["raw_high"]) for r in children),
    "low":min(Decimal(r["raw_low"]) for r in children),
    "close":Decimal(children[-1]["raw_close"]),
    "volume":sum((Decimal(r["raw_volume"]) for r in children),Decimal(0)),
    "quote_asset_volume":sum((Decimal(r["raw_quote_asset_volume"]) for r in children),Decimal(0)),
    "number_of_trades":sum(int(r["raw_number_of_trades"]) for r in children),
    "taker_buy_base_asset_volume":sum((Decimal(r["raw_taker_buy_base_asset_volume"]) for r in children),Decimal(0)),
    "taker_buy_quote_asset_volume":sum((Decimal(r["raw_taker_buy_quote_asset_volume"]) for r in children),Decimal(0)),
   }
   mismatches=[]
   for m in METRICS:
    pv=int(parent["raw_number_of_trades"]) if m=="number_of_trades" else Decimal(parent["raw_"+m])
    if roll[m]!=pv:mismatches.append(m)
   source_results[source]={
    "status":"PASS_FULL_PARENT_CHILD_ROLLUP" if not mismatches else "FAIL_INTERNAL_PARENT_CHILD_ROLLUP",
    "child_count":len(children),"parent_count":len(parents),"matched_fields":len(METRICS)-len(mismatches),
    "total_fields":len(METRICS),"mismatch_fields":mismatches,
    "calculated_child_rollup":{k:str(v) for k,v in roll.items()},
    "parent_values":{m:parent["raw_"+m] for m in METRICS},
   }
   detail_rows.append({"case_id":cid,"source":source,"bucket_utc":snap["bucket_utc"],
    "child_interval":snap["child_interval"],"parent_interval":snap["parent_interval"],
    "rollup_status":source_results[source]["status"],"child_count":len(children),
    "matched_metric_fields":len(METRICS)-len(mismatches),"total_metric_fields":len(METRICS),
    "mismatch_fields":";".join(mismatches),
    **{"child_rollup_"+k:str(v) for k,v in roll.items()},
    **{"parent_raw_"+k:parent["raw_"+k] for k in METRICS},
    "case_closed":False,"canonical_source_selected":False})
  daily=source_results.get("DAILY",{});monthly=source_results.get("MONTHLY",{})
  cases.append({
   "case_id":cid,"child_interval":snap["child_interval"],"parent_interval":snap["parent_interval"],"bucket_utc":snap["bucket_utc"],
   "frozen_monthly_mismatch_fields":snap.get("monthly_mismatch_fields_frozen",""),
   "daily_rollup_status":daily.get("status","MISSING"),"daily_matched_fields":daily.get("matched_fields",0),
   "daily_mismatch_fields":";".join(daily.get("mismatch_fields",[])),
   "monthly_rollup_status":monthly.get("status","MISSING"),"monthly_matched_fields":monthly.get("matched_fields",0),
   "monthly_mismatch_fields":";".join(monthly.get("mismatch_fields",[])),
   "monthly_child_volume_sum":monthly.get("calculated_child_rollup",{}).get("volume",""),
   "monthly_parent_volume":monthly.get("parent_values",{}).get("volume",""),
   "monthly_child_trade_count_sum":monthly.get("calculated_child_rollup",{}).get("number_of_trades",""),
   "monthly_parent_trade_count":monthly.get("parent_values",{}).get("number_of_trades",""),
   "historical_archive_version_provenance":"OPEN_NOT_ESTABLISHED","source_root_cause":"OPEN_NOT_ESTABLISHED",
   "case_closed":False,"canonical_source_selected":False})
 daily_full=sum(r["daily_rollup_status"]=="PASS_FULL_PARENT_CHILD_ROLLUP" for r in cases)
 monthly_full=sum(r["monthly_rollup_status"]=="PASS_FULL_PARENT_CHILD_ROLLUP" for r in cases)
 monthly_mismatch_fields=sum(len(r["monthly_mismatch_fields"].split(";")) for r in cases if r["monthly_mismatch_fields"])
 field_freq={m:sum(m in r["monthly_mismatch_fields"].split(";") for r in cases) for m in METRICS}
 core_all=sum(all(m in r["monthly_mismatch_fields"].split(";") for m in ("volume","quote_asset_volume","number_of_trades")) for r in cases)
 ck("daily_parent_child_rollup_passes_11_of_11",daily_full==11,{"pass":daily_full,"total":11})
 ck("monthly_parent_child_internal_mismatch_exists_in_all_11",monthly_full==0 and all(r["monthly_rollup_status"]=="FAIL_INTERNAL_PARENT_CHILD_ROLLUP" for r in cases),{"full_pass":monthly_full,"mismatch_cases":11,"field_mismatch_memberships":monthly_mismatch_fields})
 ck("volume_quote_volume_trade_count_all_mismatch_in_each_monthly_bucket",core_all==11,{"cases":core_all})
 ck("duplicate_source_contexts_consistent",not duplicate_conflicts,{"duplicate_context_rows":duplicate_count,"conflicting_values":len(duplicate_conflicts)})
 status="PASS_MONTHLY_PARENT_CHILD_INTERNAL_ROLLUP_AUDIT_SOURCE_AUTHORITY_OPEN" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_MONTHLY_PARENT_CHILD_ROLLUP_AUDIT"
 out_case=out/"CP0118_ParentChild_Internal_Rollup_Matrix.csv";out_detail=out/"CP0118_ParentChild_Internal_Rollup_Details.csv";out_json=out/"CP0118_ParentChild_Internal_Rollup_Summary.json";out_md=out/"CP0118_Monthly_ParentChild_Internal_Rollup_Report_HI.md"
 write_csv(out_case,cases,list(cases[0].keys()));write_csv(out_detail,detail_rows,list(detail_rows[0].keys()))
 summary={
  "schema_version":1,"checkpoint":"CP-0118","task":"cp0118_monthly_parent_child_internal_rollup_audit","status":status,
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),"input_blob_sha1":identities,
  "counts":{"buckets":len(cases),"daily_parent_child_full_rollups":daily_full,"monthly_parent_child_full_rollups":monthly_full,
   "monthly_parent_child_mismatch_cases":sum(r["monthly_rollup_status"]=="FAIL_INTERNAL_PARENT_CHILD_ROLLUP" for r in cases),
   "monthly_field_mismatch_memberships_across_cases":monthly_mismatch_fields,"monthly_mismatch_field_frequency_by_case":field_freq,
   "monthly_volume_quote_volume_trade_count_mismatch_cases":core_all,"duplicate_context_rows":duplicate_count,"conflicting_duplicate_values":len(duplicate_conflicts),
   "source_cases_closed":0,"canonical_source_selected":False,"unresolved_aggregation_blockers":11},
  "case_results":cases,"checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
  "decision":{"daily_parent_child_relation":"PASS_11_OF_11","monthly_parent_child_relation":"INTERNAL_MISMATCH_11_OF_11",
   "volume_quote_volume_trade_count_mismatch":"PRESENT_IN_11_OF_11_MONTHLY_BUCKETS",
   "historical_archive_version_provenance":"OPEN_NOT_ESTABLISHED","relationship_root_cause":"OPEN_NOT_ESTABLISHED",
   "canonical_source_selected":False,"source_cases_closed":0,"unresolved_aggregation_blockers":11,
   "g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g3":"BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT","g7":"LIVE_BLOCKED"},
  "non_actions":{"network_used":False,"archive_downloads":0,"raw_source_archives_modified":False,"timestamps_shifted_or_rounded":False,
   "synthetic_candles_created":False,"production_candidate_build_performed":False,"backtest_performed":False,"strategy_promoted":False,
   "live_signing_enabled":False,"public_broadcast_enabled":False,"binance_orders_placed":False},"outputs":{}
 }
 report=["# CP-0118: Daily and monthly internal parent-child rollup audit","","Status: "+status,"",
  "- Frozen CP-0107 RowEvidence was grouped by exact blocker case and source. Decimal arithmetic was used for economic numeric fields and integer arithmetic for trade count; no source data was changed.",
  "- Daily rows reconcile internally: all 11/11 parent candles reproduce the child-rollup OHLC, volume, quote volume, trade count and taker-buy metrics across all nine fields.",
  "- Monthly rows do not reconcile internally: 0/11 parent rows match all nine metrics rolled up from the monthly child rows. There are "+str(monthly_mismatch_fields)+" per-case field-mismatch memberships over the 11 buckets; these memberships overlap and are not the CP-0113 deduplicated 97-field total.",
  "- Volume, quote_asset_volume and number_of_trades mismatch in all 11 monthly buckets. Taker-buy base/quote fields each mismatch in "+str(field_freq["taker_buy_base_asset_volume"])+"/11 and "+str(field_freq["taker_buy_quote_asset_volume"])+"/11. Individual OHLC field frequencies are in the summary.",
  "- CP-0112 showed 35/35 daily bars and 315/315 daily fields match verified trade reconstruction, while the monthly rows match 21/35 bars and 218/315 fields. CP-0118 independently establishes an exact arithmetic failure inside the stored monthly parent-child relationships for every frozen bucket.",
  "- This localizes the observed inconsistency to the current monthly archive's own parent-child row relationship in these exact windows. It does not prove whether the cause is historical revision, publication/version skew, processing differences or another root cause; provenance stays open.",
  "",
  "| Case | Child -> parent | Daily rollup | Monthly rollup | Monthly mismatches | Child volume sum | Parent volume | Child trades sum | Parent trades |",
  "|---|---|---|---|---|---:|---:|---:|---:|"]
 for r in cases:
  report.append("| "+r["case_id"]+" | "+r["child_interval"]+" -> "+r["parent_interval"]+" | "+str(r["daily_matched_fields"])+"/9 | "+str(r["monthly_matched_fields"])+"/9 | "+r["monthly_mismatch_fields"]+" | "+r["monthly_child_volume_sum"]+" | "+r["monthly_parent_volume"]+" | "+r["monthly_child_trade_count_sum"]+" | "+r["monthly_parent_trade_count"]+" |")
 report.extend(["","## Interpretation boundary","",
  "The audit proves arithmetic inconsistency between each current monthly parent row and the nine-field rollup of its own current monthly child rows for these 11 windows. It does not prove a historical version timeline or explain the cause. Current official checksum sidecars authenticate the current bytes, not the byte version available at historical decision time. Do not infer global daily-over-monthly precedence.",
  "",
  "## Disposition and gates","",
  "- Keep all 11 non-row blockers open; canonical source NONE; source cases closed 0.",
  "- G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G7 LIVE_BLOCKED.",
  "- No network/archive downloads, source mutation, timestamp shifts/rounding, synthetic source candles, production candidate build, backtest, strategy promotion, signing, broadcast or orders.",
  "",
  "## Next bounded step","",
  "Compare these exact monthly internal mismatches with any dated correction/version evidence tied to the exact daily and monthly archive hashes. Until rulebook-accepted source adjudication or a formally frozen conservative quarantine policy with actual candidate-specific final metrics exists, keep all 11 blockers open."])
 out_md.write_text("\n".join(report)+"\n",encoding="utf-8")
 for p in (out_case,out_detail,out_md):summary["outputs"][p.name]={"bytes":p.stat().st_size,"sha256":sha256_file(p),"git_blob_sha1":blob_sha1(p)}
 out_json.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps({"checkpoint":"CP-0118","status":status,"counts":summary["counts"],"case_results":cases,"checks":checks,"decision":summary["decision"],"outputs":summary["outputs"]},ensure_ascii=False,sort_keys=True),flush=True)
 return 0
if __name__=="__main__":raise SystemExit(main())
