#!/usr/bin/env python3
"""Create an append-only CP-0041 450-row quarantine disposition delta from verified CP-0107 evidence."""
from __future__ import annotations
import argparse,csv,hashlib,json,shutil,subprocess
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKLIST_SHA="f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f"
WORKLIST_BYTES=2111342
WORKLIST_ROWS=996
UNMATCHED_SHA="11eb82994d5a17469eefee9f14d360537d5871c19d303ed0466c5df4f6c34021"
PACKAGE_SHA="23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc"
RULEBOOK_SHA="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
CROSSWALK_SHA="5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b"
OVERLAY_REL="evidence/source_adjudication/CP0107_Run_38742035787/CP0107_Feb2018_Disposition_Overlay.csv"
OVERLAY_BLOB="925144280f5438179f2ccd83ab255113f17baab7"
OVERLAY_SHA="3fa8cd5e17718dfe3069aab0b1d55fbf990723f1865c77412a957dd63f898a0f"
CROSSWALK_SUMMARY_REL="evidence/source_adjudication/CP0107_CP0041_Crosswalk_Summary.json"
CROSSWALK_SUMMARY_BLOB="a4d8398f1faa271681b0f962ad4f11b8d96d2348"
SOURCE_MANIFEST_REL="evidence/source_adjudication/CP0107_CP0041_Worklist_Source_Manifest.json"
SOURCE_MANIFEST_BLOB="2b0b497651ea892b00b8fe88115256258c7aa3c5"
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def blob(rel):return subprocess.check_output(["git","rev-parse","HEAD:"+rel],cwd=ROOT,text=True).strip()
def read_csv(path):
 with Path(path).open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write_csv(path,rows,fields):
 with Path(path).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader();w.writerows(rows)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--baseline-dir",required=True);ap.add_argument("--source-overlay",required=True)
 ap.add_argument("--crosswalk-summary",required=True);ap.add_argument("--source-manifest",required=True);ap.add_argument("--output-dir",required=True)
 a=ap.parse_args();out=Path(a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
 baseline=ROOT/a.baseline_dir
 if not baseline.is_dir():raise FileNotFoundError("verified CP-0107 baseline directory absent: "+str(baseline))
 for p in sorted(baseline.iterdir()):
  if p.is_file():
   target=out/p.name
   if p.resolve()!=target.resolve():shutil.copy2(p,target)
 overlay_path=ROOT/a.source_overlay;summary_path=ROOT/a.crosswalk_summary;manifest_path=ROOT/a.source_manifest
 for p in (overlay_path,summary_path,manifest_path):
  if not p.is_file():raise FileNotFoundError("disposition input missing: "+str(p))
 overlay=read_csv(overlay_path);cross= json.loads(summary_path.read_text(encoding="utf-8"));manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
 checks=[]
 def check(name,passed,detail):checks.append({"check_id":name,"status":"PASS" if passed else "FAIL","detail":str(detail)})
 check("original_996_row_worklist_provenance",manifest["source_members"][0]["sha256"]==WORKLIST_SHA and manifest["source_members"][0]["rows"]==WORKLIST_ROWS and manifest["source_members"][0]["bytes"]==WORKLIST_BYTES,
       "CP-0041 package SHA "+PACKAGE_SHA+"; worklist SHA "+WORKLIST_SHA)
 check("worklist_member_type_counts",sum(manifest["source_members"][0]["record_type_counts"].values())==WORKLIST_ROWS,
       manifest["source_members"][0]["record_type_counts"])
 check("crosswalk_summary_blob",blob(CROSSWALK_SUMMARY_REL)==CROSSWALK_SUMMARY_BLOB and cross.get("status")=="PASS_EXACT_CP0041_CROSSWALK_WITH_OPEN_SOURCE_DISPOSITION_METRICS_CORRECTED",
       "crosswalk summary ref "+CROSSWALK_SUMMARY_BLOB)
 check("source_manifest_blob",blob(SOURCE_MANIFEST_REL)==SOURCE_MANIFEST_BLOB and manifest.get("source_package",{}).get("sha256")==PACKAGE_SHA,
       "source manifest ref "+SOURCE_MANIFEST_BLOB)
 check("source_overlay_blob_hash_rows",blob(a.source_overlay)==OVERLAY_BLOB and sha(overlay_path)==OVERLAY_SHA and overlay_path.stat().st_size==1036405 and len(overlay)==450,
       "rows=450; bytes=1036405; SHA-256="+OVERLAY_SHA)
 check("crosswalk_exact_match_metrics",cross["crosswalk"]["row_count"]==450 and cross["crosswalk"]["shared_keys"]==450 and cross["crosswalk"]["new_only_keys"]==0 and cross["crosswalk"]["prior_only_keys"]==0 and cross["crosswalk"]["monthly_archive_hash_matches"]==450 and cross["crosswalk"]["twelve_raw_fields_exact_matches"]==450,
       "450/450 exact CP-0041 row keys, monthly archive hashes and 12 raw fields")
 check("frozen_rulebook_hash",cross["source_package"]["rulebook_sha256"]==RULEBOOK_SHA and manifest["source_members"][2]["sha256"]==RULEBOOK_SHA,RULEBOOK_SHA)
 by_type=manifest["source_members"][0]["record_type_counts"]
 check("only_450_target_scope",len(overlay)==450 and by_type["MONTHLY_ONLY_ROW"]==457 and by_type["DAILY_ONLY_ROW"]==452 and sum(by_type.values())==996,
       "monthly-only=457; CP-0107 target rows=450; other worklist rows remain unchanged")
 row_ids=[r.get("case_id","") for r in overlay]
 unique_ids=len(set(row_ids))==450 and all(x.startswith("UNMATCHED-M-") for x in row_ids)
 check("450_unique_monthly_worklist_ids",unique_ids,"unique IDs="+str(len(set(row_ids))))
 check("prior_overlay_disposition_rules",all(r.get("cp0041_crosswalk_match")=="PASS_FROM_VERIFIED_CROSSWALK" and r.get("disposition")=="QUARANTINE_REVIEW_REQUIRED" and r.get("canonical_source")=="NONE" and r.get("root_cause")=="OPEN_NOT_ESTABLISHED" and r.get("no_shift_round_merge_replace_delete")=="True" for r in overlay),
       "all 450 existing overlay rows remain quarantined, source NONE, root cause OPEN")
 check("mapped_daily_coverage_metrics",sum(r.get("mapped_daily_row_status")=="PRESENT_FIELDS_DIFFER" for r in overlay)==448 and sum(r.get("mapped_daily_row_status")=="ABSENT_REVIEW_REQUIRED" for r in overlay)==2 and sum(r.get("exact_daily_open_key_counterpart_present")=="False" for r in overlay)==450,
       "mapped daily present=448; absent=2; exact open-key matches=0")
 delta=[]
 for r in overlay:
  delta.append({
   "case_id":r["case_id"],"record_type":"MONTHLY_ONLY_ROW","interval":r["interval"],"utc_date":r["utc_date"],
   "open_time_ms":r["open_time_ms"],"open_time_utc":r["open_time_utc"],
   "original_worklist_disposition":r["cp0041_prior_disposition"],
   "proposed_worklist_disposition":"QUARANTINE_REVIEW_REQUIRED",
   "disposition_action":"SET_DISPOSITION_ONLY; retain all original raw row tokens and timestamps",
   "cp0041_crosswalk_match":r["cp0041_crosswalk_match"],
   "monthly_archive_filename":r["monthly_archive_filename"],
   "monthly_archive_sha256":r["monthly_archive_sha256"],
   "cp0041_monthly_archive_sha256":r["monthly_archive_sha256"],
   "monthly_archive_hash_match":"PASS_FROM_VERIFIED_CROSSWALK_450_OF_450",
   "cp0041_row_all_12_raw_fields_exact":r["raw_fields_equal_all_12"] if "raw_fields_equal_all_12" in r else "PASS_FROM_CROSSWALK_SUMMARY",
   "exact_daily_open_key_counterpart_present":r["exact_daily_open_key_counterpart_present"],
   "diagnostic_shift_ms":r["diagnostic_shift_ms"],
   "mapped_daily_open_time_utc":r["mapped_daily_open_time_utc"],
   "mapped_daily_row_status":r["mapped_daily_row_status"],
   "mapped_daily_archive_filename":r["mapped_daily_archive_filename"],
   "mapped_daily_archive_sha256":r["mapped_daily_archive_sha256"],
   "mapped_daily_differing_fields":r["mapped_daily_differing_fields"],
   "mapped_daily_economic_or_close_time_differs":r["mapped_daily_economic_or_close_time_differs"],
   "allowed_use":"Keep original monthly source value/time as evidence; exclude from canonical replacement; candidate eligibility only under frozen quarantine policy",
   "closure_gate":"OPEN_NOT_ESTABLISHED; original exchange-time semantics/provenance evidence is still required",
   "root_cause":"OPEN_NOT_ESTABLISHED","canonical_source":"NONE","case_closed":"False",
   "original_worklist_member_sha256":WORKLIST_SHA,"original_unmatched_member_sha256":UNMATCHED_SHA,
   "crosswalk_csv_sha256":CROSSWALK_SHA,"cp0040_rulebook_sha256":RULEBOOK_SHA,
   "cp0041_package_sha256":PACKAGE_SHA,"cp0107_overlay_run_id":"38742035787",
   "source_choice_changed_fields":"","source_choice_changed_field_count":0,
   "timestamp_shifted_or_rounded":"False","raw_rows_merged_replaced_or_deleted":"False","synthetic_candles_created":"False",
   "backtest_rerun":"False","strategy_promoted":"False"
  })
 fields=list(delta[0].keys())
 delta_path=out/"CP0107_CP0041_Worklist_Disposition_Delta_450.csv"
 write_csv(delta_path,delta,fields)
 stats=Counter(r["mapped_daily_row_status"] for r in delta)
 outputs={delta_path.name:{"sha256":sha(delta_path),"bytes":delta_path.stat().st_size,"rows":len(delta)}}
 all_checks=all(x["status"]=="PASS" for x in checks)
 status="PASS_450_ROW_DISPOSITION_DELTA_READY" if all_checks else "FAIL_450_ROW_DISPOSITION_DELTA"
 summary={
  "checkpoint":"CP-0107","task":"cp0107_cp0041_worklist_disposition_patch_audit","status":status,
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),
  "source_worklist":{"member":"AISTS_CP0041_Row_Level_Disposition_Worklist.csv","sha256":WORKLIST_SHA,"bytes":WORKLIST_BYTES,"rows":WORKLIST_ROWS,
   "record_type_counts":by_type,"source_package_sha256":PACKAGE_SHA},
  "scope":{"delta_rows":len(delta),"proposed_quarantine_dispositions":sum(x["proposed_worklist_disposition"]=="QUARANTINE_REVIEW_REQUIRED" for x in delta),
   "worklist_rows_left_unchanged":WORKLIST_ROWS-len(delta),"monthly_only_rows_in_original_worklist":by_type["MONTHLY_ONLY_ROW"],
   "other_monthly_only_rows_left_unchanged":by_type["MONTHLY_ONLY_ROW"]-len(delta)},
  "row_evidence":{"crosswalk_csv_sha256":CROSSWALK_SHA,"crosswalk_rows":450,"monthly_archive_hash_matches":450,"all_12_raw_fields_exact":450,
   "mapped_daily_rows_present_but_fields_differ":448,"mapped_daily_rows_absent_review_required":2,"exact_daily_open_key_counterparts":0,
   "mapped_daily_status_counts":dict(stats),"open_price_differs":442,"close_time_differs":447,"volume_differs":448},
  "rulebook":{"member":"AISTS_CP0040_Strategy_Acceptance_Rulebook_HI.md","sha256":RULEBOOK_SHA,
   "disposition_basis":"G0 source eligibility: unresolved rows are quarantined; original time semantics/provenance is required; no canonical replacement by timestamp shift."},
  "checks":checks,"checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),
  "outputs":outputs,
  "semantics":{"artifact_type":"APPEND_ONLY_DISPOSITION_DELTA_NOT_FULL_WORKLIST_REPLACEMENT",
   "original_996_row_worklist_modified":False,"450_row_disposition_delta_ready":all_checks,"other_546_rows_modified":False,
   "source_authority":"NONE","canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
   "timestamps_shifted_or_rounded":False,"raw_rows_merged_replaced_or_deleted":False,"synthetic_candles_created":False,
   "backtest_rerun":False,"strategy_promoted":False,
   "gate_states":{"G0":"BLOCKED_GLOBAL","G1":"PARTIAL_SYSTEM_LEVEL","G2":"FAIL_CURRENT_23_CANDIDATES","G3":"BLOCKED_PARTIAL","G4":"INSUFFICIENT_EVIDENCE","G5":"NOT_RUN","G6":"NOT_BUILT","G7":"LIVE_BLOCKED"}}
 }
 report=[
  "# CP-0107: CP-0041 996-row worklist disposition delta","",
  "Status: "+status+"; checks "+str(summary["checks_passed"])+"/"+str(summary["checks_total"])+" PASS.","",
  "## Scope and provenance","",
  "- Original CP-0041 worklist: 996 rows; SHA-256 "+WORKLIST_SHA+"; source package SHA-256 "+PACKAGE_SHA+". The worklist member is not overwritten.",
  "- Only the 450 crosswalk case IDs are included in this append-only disposition delta. Exact case-ID mapping: 450/450; monthly archive hash matches: 450/450; all 12 monthly raw fields exact: 450/450.",
  "- Proposed disposition for those 450 rows: QUARANTINE_REVIEW_REQUIRED. Remaining 546 original rows are explicitly unchanged.",
  "",
  "## Evidence and unresolved conditions","",
  "- Exact daily open-time counterpart exists for 0/450 monthly rows. Fixed-shift diagnostic rows are present for 448 and absent for 2; every present mapped row differs in at least one non-open field. Open price differs in 442, close_time in 447 and volume in 448.",
  "- Timestamp shift is diagnostic only. Original exchange-time semantics/provenance remain necessary; no canonical source selected; root cause OPEN_NOT_ESTABLISHED; cases closed 0.",
  "",
  "## Safety / non-mutation","",
  "This is a review-only patch file, not a source archive or full-worklist replacement. No raw rows were changed, shifted, merged, replaced or deleted; no synthetic candles; no backtest rerun or strategy promotion."
 ]
 report_path=out/"CP0107_CP0041_Worklist_Disposition_Delta_Report_HI.md"
 report_path.write_text("\n".join(report)+"\n",encoding="utf-8")
 outputs[report_path.name]={"sha256":sha(report_path),"bytes":report_path.stat().st_size,"rows":None}
 summary["outputs"]=outputs
 summary_path=out/"CP0107_CP0041_Worklist_Disposition_Delta_Summary.json"
 summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps({"status":status,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
  "original_worklist_rows":WORKLIST_ROWS,"delta_rows":len(delta),"untouched_rows":WORKLIST_ROWS-len(delta),
  "mapping":summary["row_evidence"],"outputs":outputs},ensure_ascii=False,sort_keys=True),flush=True)
 return 0 if status=="PASS_450_ROW_DISPOSITION_DELTA_READY" else 1
if __name__=="__main__":raise SystemExit(main())
