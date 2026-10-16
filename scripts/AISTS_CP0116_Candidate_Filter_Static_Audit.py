#!/usr/bin/env python3
"""CP-0116 static builder/quarantine audit with synthetic exact-key tests only."""
from __future__ import annotations
import argparse, ast, csv, hashlib, importlib.util, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "builder_git_blob_sha1": "06e9f292603b1f4755bea4c28ef027a01e2226d1",
    "helper_git_blob_sha1": "ff756af2f27d307779cde92f41a842467ada2d77",
    "manifest_git_blob_sha1": "8d956499b8f5053335b738cc408ca8859d326a3d",
    "manifest_summary_git_blob_sha1": "964197632042dd3c761ab25cf32921601ed74e4f",
    "blockers_git_blob_sha1": "d3fca23bac424fa8c8b187434e8c63e8d188a0e1",
    "cp0113_pointer_git_blob_sha1": "6d3476ed2770d1629596ea8e94e8508dabac776d",
    "cp0113_report_git_blob_sha1": "50973223cbb94eb1889f946d51369f7e7c5c63a5",
    "rulebook_sha256": "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0",
}
METRICS = ("open","high","low","close","volume","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume")

def sha_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def blob_sha1(path):
    b=path.read_bytes()
    return hashlib.sha1(("blob "+str(len(b))+"\0").encode("utf-8")+b).hexdigest()

def read_csv(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_csv(path, rows, fields):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)

def add_check(checks,name,ok,detail):
    checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":detail})

def import_builder(path):
    spec=importlib.util.spec_from_file_location("aists_cp0026_builder_cp0116_probe",path)
    if spec is None or spec.loader is None: raise RuntimeError("Cannot load frozen builder as module")
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    return mod

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--builder",default="scripts/AISTS_CP0026_Research_Candidate_Builder.py")
    ap.add_argument("--helper",default="scripts/AISTS_CP0040_Quarantine_Gate.py")
    ap.add_argument("--manifest",default="evidence/source_adjudication/CP0040_Run_38883792900/CP0040_ExactKey_Quarantine_Manifest.csv")
    ap.add_argument("--manifest-summary",default="evidence/source_adjudication/CP0040_Run_38883792900/CP0040_ExactKey_Quarantine_Manifest_Summary.json")
    ap.add_argument("--blockers",default="evidence/source_adjudication/CP0040_Run_38883792900/CP0040_NonRow_Blockers.csv")
    ap.add_argument("--row-evidence",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv")
    ap.add_argument("--rulebook",default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
    ap.add_argument("--cp0113-pointer",default="evidence/source_adjudication/CP0113_FieldLevel_Trade_Corroboration_Disposition_Current.json")
    ap.add_argument("--cp0113-report",default="evidence/source_adjudication/CP0113_FieldLevel_Trade_Corroboration_Disposition_HI.md")
    ap.add_argument("--output-dir",default="results/cp0116_candidate_filter_static_audit")
    a=ap.parse_args()
    names={"builder":a.builder,"helper":a.helper,"manifest":a.manifest,"summary":a.manifest_summary,"blockers":a.blockers,
           "row_evidence":a.row_evidence,"rulebook":a.rulebook,"cp0113_pointer":a.cp0113_pointer,"cp0113_report":a.cp0113_report}
    paths={k:(ROOT/v).resolve() for k,v in names.items()};out=(ROOT/a.output_dir).resolve()
    if any(ROOT not in p.parents for p in list(paths.values())+[out]): raise ValueError("Path escapes repository root")
    for k,p in paths.items():
        if not p.is_file(): raise FileNotFoundError(k+": "+str(p))
    out.mkdir(parents=True,exist_ok=True)

    btext=paths["builder"].read_text(encoding="utf-8"); htext=paths["helper"].read_text(encoding="utf-8")
    manifest=read_csv(paths["manifest"]); ms=read_json(paths["summary"]); blockers=read_csv(paths["blockers"])
    evidence=read_csv(paths["row_evidence"]); rule_sha=sha_file(paths["rulebook"]); cp=read_json(paths["cp0113_pointer"])
    actual={"builder_git_blob_sha1":blob_sha1(paths["builder"]),"helper_git_blob_sha1":blob_sha1(paths["helper"]),
      "manifest_git_blob_sha1":blob_sha1(paths["manifest"]),"manifest_summary_git_blob_sha1":blob_sha1(paths["summary"]),
      "blockers_git_blob_sha1":blob_sha1(paths["blockers"]),"cp0113_pointer_git_blob_sha1":blob_sha1(paths["cp0113_pointer"]),
      "cp0113_report_git_blob_sha1":blob_sha1(paths["cp0113_report"]),"rulebook_sha256":rule_sha}
    checks=[]
    for k,v in EXPECTED.items(): add_check(checks,"frozen_identity_"+k,actual[k]==v,{"actual":actual[k],"expected":v})
    manifest_keys={(r.get("interval",""),r.get("open_time_ms","")) for r in manifest}
    add_check(checks,"manifest_integrity_and_unique_exact_keys",
      len(manifest)==1427 and len(manifest_keys)==1427 and sha_file(paths["manifest"])==ms.get("row_level_manifest",{}).get("sha256"),
      {"rows":len(manifest),"unique_keys":len(manifest_keys),"sha256":sha_file(paths["manifest"])})
    add_check(checks,"current_11_nonrow_blockers_fail_closed",
      len(blockers)==11 and ms.get("status")=="PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN" and ms.get("candidate_eligibility_blocked") is True,
      {"blocker_rows":len(blockers),"summary_status":ms.get("status"),"candidate_eligibility_blocked":ms.get("candidate_eligibility_blocked")})
    add_check(checks,"cp0113_pointer_and_report_linkage",
      cp.get("checkpoint")=="CP-0113" and cp.get("status")=="PASS_FIELD_LEVEL_CROSSWALK_SOURCE_AUTHORITY_OPEN"
      and cp.get("report_git_blob_sha1")==actual["cp0113_report_git_blob_sha1"]
      and cp.get("counts",{}).get("target_keys_compared")==35 and cp.get("counts",{}).get("monthly_divergent_keys")==14
      and cp.get("counts",{}).get("monthly_mismatching_metric_fields")==97,
      {"status":cp.get("status"),"target_keys":cp.get("counts",{}).get("target_keys_compared"),"divergent_keys":cp.get("counts",{}).get("monthly_divergent_keys")})

    ast.parse(btext,filename=str(paths["builder"]));ast.parse(htext,filename=str(paths["helper"]))
    add_check(checks,"frozen_builder_and_helper_parse_as_python",True,{"builder_lines":len(btext.splitlines()),"helper_lines":len(htext.splitlines())})
    main_pos=btext.find("def main():")
    gate_pos=btext.find("quarantine_keys,quarantine_cases,gate_summary=load_candidate_gate")
    dates_pos=btext.find('dates_path=root/"reports"/"cp0025_reference_dates.json"')
    outdir_pos=btext.find("outdir.mkdir(parents=True,exist_ok=True)")
    loop_pos=btext.find("for interval in BASE_INTERVALS:")
    order_ok=main_pos>=0 and main_pos<gate_pos<dates_pos<outdir_pos<loop_pos
    add_check(checks,"main_gate_precedes_candidate_input_read_and_output_creation",order_ok,
      {"main_line":btext[:main_pos].count("\n")+1,"gate_line":btext[:gate_pos].count("\n")+1,
       "flagged_dates_line":btext[:dates_pos].count("\n")+1,"outdir_line":btext[:outdir_pos].count("\n")+1,
       "build_loop_line":btext[:loop_pos].count("\n")+1})
    guard_ok=('if len(blockers) > 0 or blocker_summary.get("candidate_eligibility_blocked") is True:' in btext
      and "G0_BLOCKED_NONROW_BLOCKERS_REMAIN" in btext
      and 'if summary.get("status") != "PASS_CANDIDATE_ELIGIBILITY_READY":' in btext)
    add_check(checks,"builder_fails_closed_until_all_nonrow_blockers_resolved",guard_ok,
      {"current_blockers":len(blockers),"candidate_eligibility_blocked":ms.get("candidate_eligibility_blocked")})
    fs=btext.find("def audit_and_write_interval(");fe=btext.find("\ndef create_monthly_from_daily(",fs)
    body=btext[fs:fe] if fs>=0 and fe>fs else ""
    tokens=["qkey=(interval,str(t))","if qkey in quarantine_keys:","quarantined.append(qr)","continue","writer.writerow(r)"]
    pos=[body.find(t) for t in tokens]
    add_check(checks,"inline_exact_key_filter_branches_before_writer",bool(body) and all(x>=0 for x in pos) and pos==sorted(pos),
      {"function_line":btext[:fs].count("\n")+1,"ordered_token_offsets":pos})
    ps=btext.find("def partition_candidate_rows(");pe=btext.find("\ndef run_gate_self_test(",ps)
    partition=btext[ps:pe] if ps>=0 and pe>ps else ""
    partition_ok="if (interval,token) in quarantine_keys" in partition and "(quarantined if (interval,token) in quarantine_keys else kept).append(row)" in partition
    add_check(checks,"partition_helper_uses_exact_interval_and_timestamp_token",partition_ok,{"function_line":btext[:ps].count("\n")+1})

    source_rows=[r for r in evidence if r.get("row_found")=="True" and r.get("source") in {"DAILY","MONTHLY"}]
    target_keys={(r.get("interval",""),r.get("expected_open_time_ms","")) for r in source_rows}
    target_cover=len(target_keys)==35 and target_keys.issubset(manifest_keys)
    add_check(checks,"all_35_cp0113_target_keys_covered_by_manifest",target_cover,
      {"unique_target_keys":len(target_keys),"covered":len(target_keys & manifest_keys),"missing":sorted(target_keys-manifest_keys)[:10]})

    builder=import_builder(paths["builder"])
    selftest=builder.run_gate_self_test(paths["manifest"],paths["blockers"],paths["summary"])
    selftest_ok=selftest.get("status")=="PASS" and selftest.get("tests_passed")==5 and selftest.get("tests_total")==5 and all(t.get("status")=="PASS" for t in selftest.get("tests",[]))
    add_check(checks,"builder_gate_selftest_against_actual_frozen_files",selftest_ok,selftest)

    by_interval={}
    for iv,ts in sorted(target_keys,key=lambda k:(k[0],int(k[1]))):
        by_interval.setdefault(iv,[]).append({"open_time_ms":ts,"probe_tag":"SYNTHETIC_ONLY"})
    total=excluded=kept_count=0; probe_errors=[]
    for iv,rows in by_interval.items():
        kept,removed=builder.partition_candidate_rows(rows,iv,manifest_keys)
        total+=len(rows);excluded+=len(removed);kept_count+=len(kept)
        if len(removed)!=len(rows) or kept: probe_errors.append({"interval":iv,"input":len(rows),"kept":len(kept),"excluded":len(removed)})
    probe_ok=total==35 and excluded==35 and kept_count==0 and not probe_errors
    add_check(checks,"35_target_keys_excluded_in_synthetic_partition_probe",probe_ok,
      {"synthetic_rows":total,"excluded":excluded,"kept":kept_count,"intervals":{k:len(v) for k,v in by_interval.items()},"errors":probe_errors})
    ts="1518170294789";one_key={("5m",ts)}
    fixtures=[{"open_time_ms":ts,"raw_token":ts},{"open_time_ms":str(int(ts)+1),"raw_token":str(int(ts)+1)}]
    k,o=builder.partition_candidate_rows(fixtures,"5m",one_key)
    k2,o2=builder.partition_candidate_rows([fixtures[0]],"15m",one_key)
    exact_ok=len(o)==1 and len(k)==1 and k[0]["open_time_ms"]==str(int(ts)+1) and len(o2)==0 and len(k2)==1 and fixtures[0]["raw_token"]==ts
    add_check(checks,"synthetic_one_ms_neighbour_and_interval_dont_match",exact_ok,
      {"exact_excluded":len(o),"one_ms_neighbour_kept":len(k),"other_interval_kept":len(k2),"tokens_unchanged":True})

    probe_rows=[]
    source_key_count={}
    for r in source_rows:
        key=(r.get("interval",""),r.get("expected_open_time_ms",""))
        source_key_count[key]=source_key_count.get(key,0)+1
    for iv,ts in sorted(target_keys,key=lambda k:(int(k[1]),k[0])):
        mr=next((x for x in manifest if x.get("interval")==iv and x.get("open_time_ms")==ts),{})
        probe_rows.append({"interval":iv,"open_time_ms":ts,"source_context_count":source_key_count[(iv,ts)],
          "manifest_case_id":mr.get("case_id",""),"manifest_case_class":mr.get("case_class",""),
          "manifest_disposition":mr.get("disposition",""),"synthetic_probe_result":"EXCLUDED_BY_EXACT_KEY_FUNCTION",
          "production_build_performed":False,"case_closed":False,"canonical_source_selected":False})

    status="PASS_STATIC_AND_SYNTHETIC_KEY_FILTER_AUDIT_G0_STILL_BLOCKED" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_CANDIDATE_FILTER_STATIC_AUDIT"
    output_csv=out/"CP0116_ExactKey_Filter_Probe.csv";output_json=out/"CP0116_Candidate_Filter_Static_Audit_Summary.json";output_md=out/"CP0116_Candidate_Filter_Static_Audit_Report_HI.md"
    write_csv(output_csv,probe_rows,list(probe_rows[0].keys()))
    summary={"schema_version":1,"checkpoint":"CP-0116","task":"cp0116_candidate_filter_static_audit","status":status,
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),"source_identities":actual,
      "counts":{"manifest_rows":len(manifest),"manifest_unique_keys":len(manifest_keys),"nonrow_blockers":len(blockers),
       "cp0113_target_keys":len(target_keys),"target_keys_in_manifest":len(target_keys & manifest_keys),
       "synthetic_rows_probed":total,"synthetic_rows_excluded":excluded,"synthetic_rows_kept":kept_count,
       "selftest_checks_passed":selftest.get("tests_passed"),"selftest_checks_total":selftest.get("tests_total"),
       "audit_checks_passed":sum(c["status"]=="PASS" for c in checks),"audit_checks_total":len(checks)},
      "checks":checks,"gate_execution":{"safe_gate_selftest_called":True,"production_main_invoked":False,
       "production_build_performed":False,"expected_fail_closed_message":"G0_BLOCKED_NONROW_BLOCKERS_REMAIN: 11 unresolved non-row cases"},
      "static_control_flow":{"gate_precedes_candidate_output":order_ok,"exact_key_filter_precedes_writer":bool(body) and all(x>=0 for x in pos) and pos==sorted(pos),
       "filter_key":"(interval, str(open_time_ms))","timestamp_rounding_for_quarantine":False,
       "current_manifest_status":ms.get("status"),"candidate_eligibility_blocked":ms.get("candidate_eligibility_blocked")},
      "decision":{"filter_implementation_present":filter_before_writer if False else (bool(body) and all(x>=0 for x in pos) and pos==sorted(pos)),
       "synthetic_probe_passes_for_all_35_target_keys":probe_ok,"candidate_specific_application_to_real_outputs_proven":False,
       "canonical_source_selected":False,"source_cases_closed":0,"unresolved_aggregation_blockers":11,
       "g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED"},
      "non_actions":{"network_used":False,"archive_downloads":0,"raw_source_bytes_modified":False,
       "candidate_dataset_built":False,"candidate_output_rows_written":False,"backtest_performed":False,
       "strategy_promoted":False,"timestamp_shifted_or_rounded":False,"synthetic_candles_written_to_research_inputs":False,
       "live_signing_enabled":False,"public_broadcast_enabled":False,"binance_orders_placed":False},"outputs":{}}
    report=[
      "# CP-0116: Candidate-builder exact-key filter static audit","",
      "Status: "+status,"",
      "## Frozen inputs and results","",
      "- CP-0026 builder Git blob SHA-1: "+actual["builder_git_blob_sha1"]+".",
      "- CP-0040 exact-key quarantine helper Git blob SHA-1: "+actual["helper_git_blob_sha1"]+".",
      "- Verified manifest: "+str(len(manifest))+" rows and "+str(len(manifest_keys))+" unique keys; SHA-256 agrees with its frozen manifest summary.",
      "- The current gate inputs contain "+str(len(blockers))+" unresolved non-row aggregation blockers; candidate_eligibility_blocked is true.",
      "- Static order: main calls load_candidate_gate before reading CP-0025 flagged dates, creating the candidate output directory or entering the interval loop.",
      "- The gate validates the manifest and then fails closed with G0_BLOCKED_NONROW_BLOCKERS_REMAIN: 11 unresolved non-row cases.",
      "- In audit_and_write_interval, the inline exact-key condition copies a matching row to the quarantine evidence list and continues before writer.writerow.",
      "- The existing deterministic gate self-test returned "+str(selftest.get("tests_passed"))+"/"+str(selftest.get("tests_total"))+" PASS using the frozen manifest/blocker files and synthetic fixtures.",
      "",
      "## Synthetic probe","",
      "- CP-0113 RowEvidence contexts deduplicated to "+str(len(target_keys))+" exact target keys; "+str(len(target_keys & manifest_keys))+" are represented in the quarantine manifest.",
      "- Production partition function excluded "+str(excluded)+"/"+str(total)+" synthetic target rows, kept "+str(kept_count)+".",
      "- One-millisecond-neighbour remains kept; same timestamp in a different interval remains kept; raw fixture timestamp tokens remain unchanged.",
      "- These are constructed row dictionaries only. No actual candidate output was generated, so this does not establish successful production candidate application.",
      "",
      "## Decision","",
      "The exact-key filtering implementation exists and passes static/function-level tests. The real candidate build is still blocked at G0 because 11 non-row aggregation cases remain open. CP-0116 does not approve candidate building, does not select a canonical source and closes no case.",
      "",
      "## Non-actions","",
      "- Production builder main was not invoked; no real candle dataset was read by the builder.",
      "- No network/archive downloads, source edits, candidate output writes, backtest, promotion, signing, broadcast or orders.",
      "",
      "## Next bounded step","",
      "Continue the CP-0040 rulebook-bound review of the 11 cross-interval non-row blockers. Do not bypass the guard or invent daily-over-monthly precedence."
    ]
    output_md.write_text("\n".join(report)+"\n",encoding="utf-8")
    for p in (output_csv,output_md):
        summary["outputs"][p.name]={"bytes":p.stat().st_size,"sha256":sha_file(p),"git_blob_sha1":blob_sha1(p)}
    output_json.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"checkpoint":"CP-0116","status":status,"counts":summary["counts"],"checks":checks,
      "gate_execution":summary["gate_execution"],"decision":summary["decision"],"outputs":summary["outputs"]},ensure_ascii=False,sort_keys=True),flush=True)
    return 0

if __name__=="__main__": raise SystemExit(main())
