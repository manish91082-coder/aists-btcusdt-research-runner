#!/usr/bin/env python3
"""CP-0117: frozen-rulebook disposition for the 11 open aggregation relationship blockers."""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
 "manifest_git_blob_sha1":"8d956499b8f5053335b738cc408ca8859d326a3d",
 "manifest_summary_git_blob_sha1":"964197632042dd3c761ab25cf32921601ed74e4f",
 "blockers_git_blob_sha1":"d3fca23bac424fa8c8b187434e8c63e8d188a0e1",
 "row_evidence_git_blob_sha1":"5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9",
 "cp0112_pointer_git_blob_sha1":"23038324c10ec0554c3968de35e01c34ef7324ec",
 "cp0112_report_git_blob_sha1":"7b9e05b9796eb61677537d38460e5f8cd77c4bc8",
 "cp0113_pointer_git_blob_sha1":"6d3476ed2770d1629596ea8e94e8508dabac776d",
 "cp0113_report_git_blob_sha1":"50973223cbb94eb1889f946d51369f7e7c5c63a5",
 "cp0114_pointer_git_blob_sha1":"ab6997b1d8dabcbaaccbba0f8f9915a8f11280cb",
 "cp0114_report_git_blob_sha1":"1546408f8b6c77b21a62fbd92fa9aceebdfcbe25",
 "cp0115_pointer_git_blob_sha1":"8377ffea70fae025620a67d6c330a7af8d740ff5",
 "cp0115_report_git_blob_sha1":"2e29d2aa1b64f9a11451464897e4a6f9d0d80f75",
 "cp0116_pointer_git_blob_sha1":"ccc4008d1099b900196e07b9cc88970a4ed3cc3d",
 "cp0116_report_git_blob_sha1":"3f2a11cb5abd31bb62e0324c40c0ceb027c6b1b4",
 "external_status_snapshot_git_blob_sha1":"75010522badfb8b762b4fc25b804234e6e02585e",
 "rulebook_sha256":"5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0",
 "sensitivity_pointer_git_blob_sha1":"cc3454422f19ed8e4da0859d1274e7bb91b26ea9",
 "sensitivity_performance_git_blob_sha1":"99568d23b66e94f573322651edd83314195567ae",
 "sensitivity_input_impact_git_blob_sha1":"294605dbec00fe314a641885c2454994be5909f0",
 "rulebook_decision_report_git_blob_sha1":"93ea40f97aa27054e8445b0059135458c934a2fa",
}
METRICS = ("open","high","low","close","volume","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume")

def blob_sha1(p):
 data=p.read_bytes()
 return hashlib.sha1(("blob "+str(len(data))+"\0").encode("utf-8")+data).hexdigest()

def sha256_file(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()

def read_csv(p):
 with p.open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def read_json(p):
 return json.loads(p.read_text(encoding="utf-8"))

def write_csv(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)

def parse_divergences(markdown):
 result={}
 for line in markdown.splitlines():
  if not re.match(r"^\|\s*(?:5m|15m|30m)\s*\|\s*20(?:17|18)-",line): continue
  cells=[c.strip() for c in line.split("|")[1:-1]]
  if len(cells)!=4: raise ValueError("Unexpected CP-0113 mismatch table row: "+line)
  interval,utc,count_token,field_token=cells
  utc=utc.replace(chr(96),"")
  fields=[v.strip() for v in field_token.replace(chr(96),"").split(";") if v.strip()]
  dt=datetime.fromisoformat(utc.replace("Z","+00:00"))
  ms=str(int(dt.timestamp()*1000)); count=int(count_token)
  if count!=len(fields): raise ValueError("Mismatch field count differs from field list for "+interval+"/"+utc)
  key=(interval,ms)
  if key in result: raise ValueError("Duplicate CP-0113 divergence key "+repr(key))
  result[key]={"interval":interval,"open_time_ms":ms,"open_time_utc":utc,"mismatch_field_count":count,"mismatch_fields":fields}
 return result

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--manifest",default="evidence/source_adjudication/CP0040_Run_38883792900/CP0040_ExactKey_Quarantine_Manifest.csv")
 ap.add_argument("--manifest-summary",default="evidence/source_adjudication/CP0040_Run_38883792900/CP0040_ExactKey_Quarantine_Manifest_Summary.json")
 ap.add_argument("--blockers",default="evidence/source_adjudication/CP0040_Run_38883792900/CP0040_NonRow_Blockers.csv")
 ap.add_argument("--row-evidence",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv")
 ap.add_argument("--rulebook",default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
 ap.add_argument("--cp0112-pointer",default="evidence/source_adjudication/CP0112_TradeDerived_Aggregation_Reconstruction_Current.json")
 ap.add_argument("--cp0112-report",default="evidence/source_adjudication/CP0112_TradeDerived_Aggregation_Reconstruction_HI.md")
 ap.add_argument("--cp0113-pointer",default="evidence/source_adjudication/CP0113_FieldLevel_Trade_Corroboration_Disposition_Current.json")
 ap.add_argument("--cp0113-report",default="evidence/source_adjudication/CP0113_FieldLevel_Trade_Corroboration_Disposition_HI.md")
 ap.add_argument("--cp0114-pointer",default="evidence/source_adjudication/CP0114_Quarantine_Overlap_G0_Impact_Current.json")
 ap.add_argument("--cp0114-report",default="evidence/source_adjudication/CP0114_Quarantine_Overlap_G0_Impact_Report_HI.md")
 ap.add_argument("--cp0115-pointer",default="evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Current.json")
 ap.add_argument("--cp0115-report",default="evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Report_HI.md")
 ap.add_argument("--cp0116-pointer",default="evidence/source_adjudication/CP0116_Candidate_Filter_Static_Audit_Current.json")
 ap.add_argument("--cp0116-report",default="evidence/source_adjudication/CP0116_Candidate_Filter_Static_Audit_Report_HI.md")
 ap.add_argument("--sensitivity-pointer",default="evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Current.json")
 ap.add_argument("--sensitivity-performance",default="evidence/source_adjudication/CP0040_Sensitivity_Run_38897836116/CP0040_Quarantine_Performance.csv")
 ap.add_argument("--sensitivity-input-impact",default="evidence/source_adjudication/CP0040_Sensitivity_Run_38897836116/CP0040_Input_Impact.csv")
 ap.add_argument("--rulebook-decision-report",default="evidence/source_adjudication/CP0040_Rulebook_Bound_Decision_Run_38904743112/CP0040_Rulebook_Bound_Eligibility_Decision_Report_HI.md")
 ap.add_argument("--external-snapshot",default="evidence/source_adjudication/CP0117_External_Provenance_Issue_Status_Snapshot_20261016.json")
 ap.add_argument("--output-dir",default="results/cp0117_rulebook_bound_blocker_disposition")
 a=ap.parse_args()
 names={
  "manifest":a.manifest,"manifest_summary":a.manifest_summary,"blockers":a.blockers,"row_evidence":a.row_evidence,
  "rulebook":a.rulebook,"cp0112_pointer":a.cp0112_pointer,"cp0112_report":a.cp0112_report,
  "cp0113_pointer":a.cp0113_pointer,"cp0113_report":a.cp0113_report,"cp0114_pointer":a.cp0114_pointer,"cp0114_report":a.cp0114_report,
  "cp0115_pointer":a.cp0115_pointer,"cp0115_report":a.cp0115_report,"cp0116_pointer":a.cp0116_pointer,"cp0116_report":a.cp0116_report,
  "sensitivity_pointer":a.sensitivity_pointer,"sensitivity_performance":a.sensitivity_performance,
  "sensitivity_input_impact":a.sensitivity_input_impact,"rulebook_decision_report":a.rulebook_decision_report,"external_status_snapshot":a.external_snapshot
 }
 paths={k:(ROOT/v).resolve() for k,v in names.items()};out=(ROOT/a.output_dir).resolve()
 if any(ROOT not in p.parents for p in list(paths.values())+[out]): raise ValueError("Path escapes repository root")
 for k,p in paths.items():
  if not p.is_file(): raise FileNotFoundError(k+": "+str(p))
 out.mkdir(parents=True,exist_ok=True)
 identities={k+"_git_blob_sha1":blob_sha1(p) for k,p in paths.items() if k!="rulebook"}
 identities["rulebook_sha256"]=sha256_file(paths["rulebook"])
 checks=[]
 def ck(name,ok,detail): checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":detail})
 for k,expected in EXPECTED.items():
  ck("frozen_identity_"+k,identities.get(k)==expected,{"actual":identities.get(k),"expected":expected})
 rule_text=paths["rulebook"].read_text(encoding="utf-8")
 manifest=read_csv(paths["manifest"]); blockers=read_csv(paths["blockers"]); evidence=read_csv(paths["row_evidence"])
 ms=read_json(paths["manifest_summary"]);p12=read_json(paths["cp0112_pointer"]);p13=read_json(paths["cp0113_pointer"])
 p14=read_json(paths["cp0114_pointer"]);p15=read_json(paths["cp0115_pointer"]);p16=read_json(paths["cp0116_pointer"])
 sens=read_json(paths["sensitivity_pointer"]);external=read_json(paths["external_status_snapshot"])
 m12=paths["cp0112_report"].read_text(encoding="utf-8");m13=paths["cp0113_report"].read_text(encoding="utf-8")
 m14=paths["cp0114_report"].read_text(encoding="utf-8");m15=paths["cp0115_report"].read_text(encoding="utf-8")
 m16=paths["cp0116_report"].read_text(encoding="utf-8");decision_report=paths["rulebook_decision_report"].read_text(encoding="utf-8")
 performance=read_csv(paths["sensitivity_performance"]);impact=read_csv(paths["sensitivity_input_impact"])
 manifest_sha=sha256_file(paths["manifest"]);manifest_by_key={};dups=[]
 manifest_by_case={}
 for r in manifest:
  key=(r.get("interval",""),r.get("open_time_ms",""))
  if key in manifest_by_key: dups.append(key)
  manifest_by_key[key]=r
  for cid in [v.strip() for v in r.get("aggregation_bucket_case_ids","").split(";") if v.strip()]:
   manifest_by_case.setdefault(cid,[]).append(r)
 blocker_ids=[r.get("case_id","") for r in blockers]
 evidence_by_case={};evidence_keys={}
 for r in evidence:
  if r.get("row_found")!="True": continue
  cid=r.get("bucket_case_id","")
  evidence_by_case.setdefault(cid,[]).append(r)
  evidence_keys.setdefault(cid,set()).add((r.get("interval",""),r.get("expected_open_time_ms","")))
 b12={r.get("case_id"):r for r in p12.get("bucket_results",[])}
 divergences=parse_divergences(m13);div_membership={}
 for key,d in divergences.items():
  mr=manifest_by_key.get(key,{})
  for cid in [v.strip() for v in mr.get("aggregation_bucket_case_ids","").split(";") if v.strip()]:
   div_membership.setdefault(cid,[]).append(d)
 g0=("G0 — Source/data eligibility" in rule_text and "प्रत्येक unresolved item स्पष्ट रूप से quarantined हो" in rule_text and "final metrics उस quarantine policy पर आधारित हों" in rule_text)
 g3=("G3 — Candidate stability / stress" in rule_text and "Material metric differences caused by a source policy mean the data gate remains open" in rule_text)
 ck("frozen_rulebook_G0_G3_clauses_present",g0 and g3,{"g0_quarantine_clause":g0,"g3_material_policy_clause":g3})
 ck("manifest_hash_row_count_unique_keys_and_blockers",len(manifest)==1427 and len(manifest_by_key)==1427 and not dups and manifest_sha==ms.get("row_level_manifest",{}).get("sha256") and len(blockers)==11 and ms.get("status")=="PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN" and ms.get("nonrow_blockers",{}).get("candidate_eligibility_blocked") is True,
  {"rows":len(manifest),"unique_keys":len(manifest_by_key),"duplicates":len(dups),"blockers":len(blockers),"summary_status":ms.get("status")})
 ck("CP0112_reconstruction_pointer_metrics",p12.get("status")=="PASS_TRADE_DERIVED_RECONSTRUCTION_COMPLETE_SOURCE_AUTHORITY_OPEN" and p12.get("results",{}).get("unique_target_candle_keys")==35 and p12.get("results",{}).get("daily_metric_fields_exact_match")=="315/315" and p12.get("results",{}).get("monthly_unique_bars_exact_match")=="21/35" and p12.get("results",{}).get("monthly_metric_fields_exact_match")=="218/315" and p12.get("results",{}).get("direct_trade_derived_parent_equals_child_rollup")=="11/11",p12.get("results",{}))
 ck("CP0113_pointer_matches_14_key_97_field_report",p13.get("status")=="PASS_FIELD_LEVEL_CROSSWALK_SOURCE_AUTHORITY_OPEN" and p13.get("counts",{}).get("target_keys_compared")==35 and p13.get("counts",{}).get("monthly_divergent_keys")==14 and p13.get("counts",{}).get("monthly_mismatching_metric_fields")==97 and len(divergences)==14 and sum(x["mismatch_field_count"] for x in divergences.values())==97,{"divergent_keys":len(divergences),"fields":sum(x["mismatch_field_count"] for x in divergences.values())})
 ck("CP0112_has_exactly_11_blocker_bucket_results",len(b12)==11 and set(b12)==set(blocker_ids) and all(r.get("parent_child_rollup")=="PASS" for r in b12.values()),{"bucket_results":len(b12),"blockers":len(blocker_ids),"rollups_pass":sum(r.get("parent_child_rollup")=="PASS" for r in b12.values())})
 case_rows=[];case_mismatches=[]
 for br in blockers:
  cid=br["case_id"];mrows=manifest_by_case.get(cid,[])
  mkeys={(r.get("interval",""),r.get("open_time_ms","")) for r in mrows};ekeys=evidence_keys.get(cid,set())
  b=b12.get(cid,{});drows=div_membership.get(cid,[])
  open_no_source=bool(mrows) and all(r.get("canonical_source","").upper()=="NONE" and r.get("case_closed","").lower()=="false" for r in mrows)
  same=mkeys==ekeys and bool(mkeys);all_in=all(k in manifest_by_key for k in ekeys)
  if not same or not all_in or not open_no_source:case_mismatches.append({"case_id":cid,"manifest_keys":len(mkeys),"evidence_keys":len(ekeys),"same_keyset":same,"all_in_manifest":all_in,"open_no_source":open_no_source})
  child=sorted({r.get("interval","") for r in evidence_by_case.get(cid,[]) if r.get("role")=="CHILD"})
  parent=sorted({r.get("interval","") for r in evidence_by_case.get(cid,[]) if r.get("role")=="PARENT"})
  bucket_times=sorted({r.get("bucket_utc","") for r in evidence_by_case.get(cid,[])})
  case_rows.append({
   "case_id":cid,"record_type":br.get("record_type",""),"blocker_disposition_at_start":br.get("disposition",""),
   "child_intervals":";".join(child),"parent_intervals":";".join(parent),"bucket_utc":";".join(bucket_times),
   "row_evidence_unique_keys":len(ekeys),"manifest_tagged_unique_keys":len(mkeys),
   "manifest_keyset_equals_row_evidence":same,"keys_open_no_canonical_source":open_no_source,
   "daily_trade_derived_bucket_match":b.get("daily_match","NOT_IN_CP0112"),
   "monthly_archive_bucket_match":b.get("monthly_match","NOT_IN_CP0112"),
   "trade_derived_parent_child_rollup":b.get("parent_child_rollup","NOT_IN_CP0112"),
   "monthly_divergent_keys_in_bucket":len(drows),
   "monthly_divergent_field_memberships_in_bucket":sum(x["mismatch_field_count"] for x in drows),
   "source_root_cause":"OPEN_NOT_ESTABLISHED","historical_archive_version_provenance":"OPEN_NOT_ESTABLISHED",
   "actual_candidate_quarantine_metrics":"NOT_PRODUCED_PRODUCTION_BUILD_BLOCKED",
   "rulebook_disposition":"KEEP_OPEN_EXACT_ROWS_QUARANTINED_RELATIONSHIP_UNRESOLVED",
   "case_closed":False,"canonical_source_selected":False
  })
 ck("all_11_cases_have_exact_manifest_and_row_evidence_keyset_match",len(case_rows)==11 and not case_mismatches,{"case_count":len(case_rows),"cases":{r["case_id"]:r["row_evidence_unique_keys"] for r in case_rows},"mismatches":case_mismatches})
 ck("all_35_bucket_keys_have_case_links",ms.get("aggregation_bucket_quarantine",{}).get("unique_exact_keys")==35 and ms.get("row_level_manifest",{}).get("all_bucket_parent_and_child_keys_in_manifest") is True and sum(bool(r.get("aggregation_bucket_case_ids")) for r in manifest)==35,{"summary_key_count":ms.get("aggregation_bucket_quarantine",{}).get("unique_exact_keys"),"tagged_manifest_rows":sum(bool(r.get("aggregation_bucket_case_ids")) for r in manifest)})
 ck("CP0114_keeps_global_G0_blocked_no_conflict_keys_applied",p14.get("status")=="PASS_MANIFEST_OVERLAP_AUDIT_G0_STILL_BLOCKED" and p14.get("decision",{}).get("g0")=="BLOCKED_GLOBAL" and p14.get("counts",{}).get("divergent_keys_in_sensitivity_applied_list")==0 and p14.get("decision",{}).get("source_cases_closed")==0,{"g0":p14.get("decision",{}).get("g0"),"conflict_keys_applied":p14.get("counts",{}).get("divergent_keys_in_sensitivity_applied_list")})
 ck("CP0115_reports_9_direct_low_timeframe_candidate_overlaps",p15.get("status")=="PASS_CANDIDATE_INTERVAL_OVERLAP_AUDIT_G0_STILL_BLOCKED" and p15.get("counts",{}).get("direct_interval_overlap_candidate_count")==9 and p15.get("counts",{}).get("g2_fail")==23,{"direct_interval_overlaps":p15.get("counts",{}).get("direct_interval_overlap_candidate_count"),"g2_fail":p15.get("counts",{}).get("g2_fail")})
 ck("CP0116_static_filter_pass_does_not_claim_real_candidate_output",p16.get("status")=="PASS_STATIC_AND_SYNTHETIC_KEY_FILTER_AUDIT_G0_STILL_BLOCKED" and p16.get("results",{}).get("synthetic_target_rows_excluded")==35 and p16.get("results",{}).get("synthetic_target_rows_kept")==0 and p16.get("decision",{}).get("production_candidate_build_performed") is False and p16.get("decision",{}).get("real_candidate_output_filter_application_proven") is False,{"status":p16.get("status"),"synthetic_excluded":p16.get("results",{}).get("synthetic_target_rows_excluded"),"production_build":p16.get("decision",{}).get("production_candidate_build_performed")})
 perf={r.get("period"):r for r in performance};train_delta=float(perf["TRAIN"]["delta_net_return_percentage_points"]) if "TRAIN" in perf else None
 impact_by={r.get("interval"):r for r in impact}
 g3_effect="BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT" in decision_report
 ck("G3_material_quarantine_sensitivity_and_input_impact_still_blocked",len(perf)==3 and train_delta is not None and abs(train_delta)>=1.0 and sens.get("g0")=="BLOCKED_GLOBAL" and sens.get("canonical_source")=="NONE" and g3_effect and set(impact_by)=={"4h","1d","1mo"} and all(int(r.get("replacements_added",-1))==0 for r in impact_by.values()),{"TRAIN_delta_pp":train_delta,"g0":sens.get("g0"),"G3_material_effect_reported":g3_effect,"input_impact":{k:{"removed":v.get("removed_exact_key_rows"),"replacements":v.get("replacements_added")} for k,v in impact_by.items()}})
 issues=external.get("issues",[]);issue504=next((i for i in issues if i.get("number")==504),{});issue475=next((i for i in issues if i.get("number")==475),{})
 ext_ok=external.get("observed_date_utc")=="2026-10-16" and issue504.get("state")=="open" and issue504.get("comments_count")==0 and issue504.get("maintainer_answer_observed") is False and issue475.get("state")=="open" and issue475.get("only_comment",{}).get("maintainer_identity_confirmed") is False
 ck("external_historical_provenance_snapshot_is_bounded",ext_ok,{"issue_504_state":issue504.get("state"),"issue_504_comments":issue504.get("comments_count"),"issue_475_state":issue475.get("state"),"different_target_dates_only":True})
 ck("rulebook_bound_prior_decision_explicitly_blocks_global_G0_and_G3", "GLOBAL_GATES_REMAIN_BLOCKED" in decision_report and "G0: BLOCKED_GLOBAL" in decision_report and "G3: BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT" in decision_report and "cases closed=0" in decision_report,{"global_g0_blocked":"G0: BLOCKED_GLOBAL" in decision_report,"g3_blocked":g3_effect})
 ck("no_source_authority_or_case_closure_in_inputs",p12.get("disposition",{}).get("canonical_source_selected") is False and p13.get("disposition",{}).get("canonical_source_selected") is False and p14.get("decision",{}).get("canonical_source")=="NONE" and all(r["case_closed"] is False and r["canonical_source_selected"] is False for r in case_rows),{"canonical_source":"NONE","closed_cases":0})
 status="PASS_RULEBOOK_BOUND_NONROW_DISPOSITION_G0_STILL_BLOCKED" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_RULEBOOK_BOUND_NONROW_DISPOSITION"
 matrix_path=out/"CP0117_NonRow_Blocker_Disposition_Matrix.csv"
 report_path=out/"CP0117_Rulebook_Bound_Blocker_Disposition_Report_HI.md"
 summary_path=out/"CP0117_Rulebook_Bound_Blocker_Disposition_Summary.json"
 write_csv(matrix_path,case_rows,list(case_rows[0].keys()))
 summary={
  "schema_version":1,"checkpoint":"CP-0117","task":"cp0117_rulebook_bound_nonrow_blocker_disposition_audit","status":status,
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),"input_blob_sha1":identities,
  "counts":{"nonrow_blockers":len(blockers),"case_dispositions":len(case_rows),"cases_kept_open":sum(r["case_closed"] is False for r in case_rows),
   "cases_with_exact_manifest_keyset_match":sum(bool(r["manifest_keyset_equals_row_evidence"]) for r in case_rows),
   "unique_bucket_keys":ms.get("aggregation_bucket_quarantine",{}).get("unique_exact_keys"),
   "CP0112_parent_child_rollups_pass":sum(r.get("parent_child_rollup")=="PASS" for r in b12.values()),
   "daily_trade_derived_bars_exact":p12.get("results",{}).get("daily_unique_bars_exact_match"),
   "daily_trade_derived_metric_fields_exact":p12.get("results",{}).get("daily_metric_fields_exact_match"),
   "monthly_unique_bars_exact":p12.get("results",{}).get("monthly_unique_bars_exact_match"),
   "monthly_metric_fields_exact":p12.get("results",{}).get("monthly_metric_fields_exact_match"),
   "monthly_divergent_keys":len(divergences),"monthly_divergent_fields":sum(r["mismatch_field_count"] for r in divergences.values()),
   "conflict_keys_in_sensitivity_applied_list":p14.get("counts",{}).get("divergent_keys_in_sensitivity_applied_list"),
   "direct_overlap_candidates":p15.get("counts",{}).get("direct_interval_overlap_candidate_count"),
   "synthetic_filter_excluded":p16.get("results",{}).get("synthetic_target_rows_excluded"),
   "external_provenance_issue_504_open_no_comments":ext_ok,"TRAIN_quarantine_delta_pp":train_delta,
   "checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks)},
  "per_blocker_disposition":case_rows,"checks":checks,
  "decision":{"row_level_quarantine_coverage":"PASS_35_UNIQUE_KEYS_PRESENT_OPEN_NO_CANONICAL_SOURCE",
   "trade_derived_rollup_consistency":"PASS_11_OF_11",
   "daily_values":"CORROBORATED_BY_CURRENT_CHECKSUM_VERIFIED_TRADES_FOR_THESE_35_KEYS",
   "monthly_values":"CONFLICT_ON_14_KEYS_97_FIELDS",
   "historical_archive_version_provenance":"OPEN_NOT_ESTABLISHED",
   "accepted_candidate_quarantine_metrics_for_all_affected_candidates":"NOT_ESTABLISHED_PRODUCTION_BUILD_BLOCKED",
   "nonrow_blocker_disposition":"KEEP_ALL_11_OPEN_QUARANTINED_DIAGNOSTIC_ONLY",
   "canonical_source_selected":False,"source_cases_closed":0,"unresolved_aggregation_blockers":11,
   "g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g3":"BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT","g7":"LIVE_BLOCKED"},
  "non_actions":{"network_used_in_audit":False,"archive_downloads":0,"raw_source_archives_modified":False,
   "candidate_build_performed":False,"backtest_performed":False,"strategy_promoted":False,
   "timestamps_shifted_or_rounded":False,"synthetic_candles_created":False,"source_cases_closed":0,
   "live_signing_enabled":False,"public_broadcast_enabled":False,"binance_orders_placed":False},"outputs":{}
 }
 report_lines=[
  "# CP-0117: Frozen-rulebook disposition of the 11 non-row aggregation blockers","",
  "Status: "+status,"",
  "## Evidence result","",
  "- The 11 non-row blockers join one-to-one with CP-0112 bucket results. All 35 unique row keys evidenced by CP-0107 are tagged to their associated blocker case or cases in the 1,427-row CP-0040 manifest. The case-specific manifest key sets equal the frozen row-evidence key sets.",
  "- Trade-derived parent candles reconcile to reconstructed child-candle rollups for 11/11 buckets. For the 35 exact target bars, current checksum-verified Spot trades reproduce 35/35 daily bars and 315/315 daily metric fields. The monthly source matches 21/35 bars and 218/315 fields; 14 keys / 97 fields remain divergent.",
  "- This improves diagnostic corroboration of the current daily values, but it does not establish a historical version timeline or prove which bytes were publicly available at a historical decision time.",
  "- The dated public issue snapshot records issue #504 as open with zero comments; no maintainer answer to the historical-version/timestamp question was observed. Issue #475 remains open but concerns different dates and is only contextual evidence.",
  "- CP-0116 verified the exact-key filter implementation and excluded 35/35 synthetic probe rows, but production CP-0026 main was not invoked. Production candidate inputs and policy-based final metrics were not generated.",
  "- Frozen CP-0040 sensitivity shows TRAIN net return changed by "+(train_delta===None?"not available":format(train_delta,".6f"))+" percentage points; the rulebook-bound G3 status therefore remains blocked.",
  "",
  "## Per-case disposition","",
  "| Case | Keys | Child -> parent | Daily exact | Monthly exact | Divergent keys / field memberships | Disposition |",
  "|---|---:|---|---:|---:|---:|---|"
 ]
 for r in case_rows:
  report_lines.append("| "+r["case_id"]+" | "+str(r["row_evidence_unique_keys"])+" | "+r["child_intervals"]+" -> "+r["parent_intervals"]+" | "+r["daily_trade_derived_bucket_match"]+" | "+r["monthly_archive_bucket_match"]+" | "+str(r["monthly_divergent_keys_in_bucket"])+" / "+str(r["monthly_divergent_field_memberships_in_bucket"])+" | KEEP OPEN |")
 report_lines.extend([
  "",
  "## Frozen-rulebook conclusion","",
  "All eleven relationship blockers remain open. Their implicated exact rows are represented in the frozen quarantine manifest, but row-level coverage alone does not resolve the cross-interval relationship or historical version provenance. CP-0040 requires material source-policy effects to be included in candidate metrics, and the real candidate build is fail-closed before data read while these blockers remain. A prior candidate-specific diagnostic PASS for MTF_BREAKOUT_4H_D1 is not global G0 approval.",
  "",
  "No daily-over-monthly precedence rule is introduced. The current evidence supports a bounded daily-data corroboration statement for the 35 exact keys, not global canonical-source authority. The 11 root causes remain OPEN_NOT_ESTABLISHED.",
  "",
  "## Gates and non-actions","",
  "- G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G7 LIVE_BLOCKED.",
  "- Canonical source NONE; source cases closed 0; 11 non-row blockers remain open.",
  "- No archive downloads/network inside this audit; no source edits, timestamp rounding, synthetic candles, production build, backtest, promotion, signing, broadcast or Binance orders.",
  "",
  "## Next bounded step","",
  "Do not repeat checksum acquisition or bypass the fail-closed builder. Continue only with an independently evidenced historical-version/source adjudication for the 11 relationships, or a formally frozen conservative quarantine policy with actual candidate-specific final metrics. Until then, preserve all blockers open."
 ])
 report_path.write_text("\n".join(report_lines)+"\n",encoding="utf-8")
 for p in (matrix_path,report_path): summary["outputs"][p.name]={"bytes":p.stat().st_size,"sha256":sha256_file(p),"git_blob_sha1":blob_sha1(p)}
 summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps({"checkpoint":"CP-0117","status":status,"counts":summary["counts"],"per_blocker_disposition":case_rows,
  "checks":checks,"decision":summary["decision"],"outputs":summary["outputs"]},ensure_ascii=False,sort_keys=True),flush=True)
 return 0

if __name__=="__main__": raise SystemExit(main())
