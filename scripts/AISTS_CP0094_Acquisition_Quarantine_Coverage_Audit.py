#!/usr/bin/env python3
"""CP-0094 exact-key reconciliation of CP-0093 acquisition discrepancies to CP-0040 quarantine.

Read-only and rulebook-bound. Proves whether the 14 economic conflicts and 10
missing daily-grid keys from the completed CP-0107 reference audit are explicitly
represented in the frozen CP-0040 manifest. Does not choose a source or close a case.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RULEBOOK_SHA="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
MANIFEST_SHA="e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a"
BLOCKERS_SHA="f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36"
def now(): return datetime.now(timezone.utc).isoformat()
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def read_json(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def read_csv(p):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write_json(p,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p,rows):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader()
        if rows:w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--triage-dir",default="evidence/source_adjudication/CP0093_DailyReference_Discrepancy_Triage_Run_38910674953")
    ap.add_argument("--acquisition-dir",default="evidence/source_adjudication/CP0107_Run_38909366995")
    ap.add_argument("--manifest-pointer",default="evidence/source_adjudication/CP0040_Current_Manifest.json")
    ap.add_argument("--rulebook",default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
    ap.add_argument("--output-dir",default="results/cp0094_acquisition_quarantine_coverage")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True);checks=[]
    def ck(n,ok,d):checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    try:
        triage_dir=(ROOT/a.triage_dir).resolve();acq_dir=(ROOT/a.acquisition_dir).resolve()
        triage_summary_path=triage_dir/"CP0093_DailyReference_Discrepancy_Triage_Summary.json"
        econ_path=triage_dir/"CP0093_Economic_Divergence_14_Row_Detail.csv"
        gaps_path=triage_dir/"CP0093_MonthlyOnly_10_Key_Review.csv"
        case_path=triage_dir/"CP0093_DailyReference_Case_Triage.csv"
        raw_path=acq_dir/"CP0107_CP0041_DailyReference_RawRow_Comparison.csv"
        archive_path=acq_dir/"CP0107_CP0041_DailyReference_Archive_Manifest.csv"
        period_path=acq_dir/"CP0107_CP0041_DailyReference_Period_Summary.csv"
        monthly_path=acq_dir/"CP0107_CP0041_MonthlyArchive_Manifest_Subset.csv"
        rule_path=(ROOT/a.rulebook).resolve();pointer=read_json(ROOT/a.manifest_pointer)
        manifest_path=ROOT/pointer["manifest_path"];manifest_summary_path=ROOT/pointer["summary_path"]
        blockers_path=ROOT/pointer["blockers_path"]
        required=[triage_summary_path,econ_path,gaps_path,case_path,raw_path,archive_path,period_path,monthly_path,rule_path,manifest_path,manifest_summary_path,blockers_path]
        missing=[str(p) for p in required if not p.is_file()]
        ck("all_frozen_input_files_present",not missing,missing or "all 12 input files found")
        if missing:raise ValueError("Missing required frozen input: "+", ".join(missing))
        triage=read_json(triage_summary_path);manifest_summary=read_json(manifest_summary_path)
        econ=read_csv(econ_path);gaps=read_csv(gaps_path);case_rows=read_csv(case_path)
        raw=read_csv(raw_path);archives=read_csv(archive_path);periods=read_csv(period_path);monthly=read_csv(monthly_path)
        manifest=read_csv(manifest_path);blockers=read_csv(blockers_path)
        # Verify CP-0093's derived evidence outputs and the CP-0107 upstream raw input before joining.
        for name,p in ((econ_path.name,econ_path),(gaps_path.name,gaps_path),(case_path.name,case_path)):
            rec=triage.get("outputs",{}).get(name,{})
            ck("triage_output_hash:"+name,bool(rec) and p.stat().st_size==rec.get("bytes") and sha(p.read_bytes())==rec.get("sha256"),
               {"bytes":p.stat().st_size,"sha256":sha(p.read_bytes()),"recorded":rec})
        expected_raw=triage.get("source_evidence_hashes",{}).get(raw_path.name,{})
        ck("raw_row_source_hash_size",bool(expected_raw) and raw_path.stat().st_size==expected_raw.get("bytes") and sha(raw_path.read_bytes())==expected_raw.get("sha256"),
           {"bytes":raw_path.stat().st_size,"sha256":sha(raw_path.read_bytes()),"recorded":expected_raw})
        rule_bytes=rule_path.read_bytes();rule_text=rule_bytes.decode("utf-8")
        g0_clause=("G0 — Source/data eligibility" in rule_text and "जबतक किसी item का source adjudication न हो" in rule_text and
                   "प्रत्येक unresolved item स्पष्ट रूप से quarantined हो" in rule_text and
                   "final metrics उस quarantine policy पर आधारित हों" in rule_text)
        ck("frozen_rulebook_hash_and_G0_quarantine_clause",len(rule_bytes)==10630 and sha(rule_bytes)==RULEBOOK_SHA and g0_clause,
           {"bytes":len(rule_bytes),"sha256":sha(rule_bytes),"G0_clause_present":g0_clause})
        manifest_sha=sha(manifest_path.read_bytes());blocker_sha=sha(blockers_path.read_bytes())
        mk={(r.get("interval","").strip(),r.get("open_time_ms","").strip()):r for r in manifest}
        ck("frozen_CP0040_manifest_hash_unique_keys",manifest_sha==MANIFEST_SHA and pointer.get("manifest_sha256")==MANIFEST_SHA and
           pointer.get("candidate_eligibility_blocked") is True and len(manifest)==1427 and len(mk)==1427,
           {"sha256":manifest_sha,"rows":len(manifest),"unique_keys":len(mk),"status":pointer.get("status")})
        ck("all_eleven_nonrow_blockers_still_open",blocker_sha==BLOCKERS_SHA and len(blockers)==11 and
           pointer.get("status")=="PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN",
           {"sha256":blocker_sha,"rows":len(blockers),"pointer_status":pointer.get("status")})
        ck("upstream_source_audits_pass",triage.get("status")=="PASS_DAILY_REFERENCE_DISCREPANCY_TRIAGE_COMPLETE_SOURCE_AUTHORITY_OPEN" and
           triage.get("checks_passed")==14 and triage.get("checks_total")==14 and
           triage.get("acquisition",{}).get("daily_zip_sha256_tokens_matched")==16 and
           triage.get("acquisition",{}).get("daily_zip_crc_pass")==16 and
           len(archives)==16 and all(r.get("fetch_status")=="PASS" and r.get("zip_crc")=="PASS" and r.get("sidecar_token_matches_zip")=="True" for r in archives) and
           len(monthly)==14 and all(r.get("status")=="MATCH" and r.get("zip_crc")=="PASS" for r in monthly),
           {"triage_status":triage.get("status"),"triage_checks":str(triage.get("checks_passed"))+"/"+str(triage.get("checks_total")),
            "daily_pairs":len(archives),"monthly_archives":len(monthly)})
        ck("triage_denominators_stable",len(econ)==14 and len(gaps)==10 and len(case_rows)==16 and len(raw)==1992 and
           triage.get("comparison",{}).get("economic_field_divergent_pairs")==14 and triage.get("comparison",{}).get("missing_expected_grid_keys")==10,
           {"economic_rows":len(econ),"missing_grid_keys":len(gaps),"case_rows":len(case_rows),"raw_rows":len(raw)})
        raw_by={(r.get("case_id",""),r.get("interval",""),r.get("open_time_ms","")):r for r in raw}
        archive_by={r.get("filename",""):r for r in archives}
        monthly_by={r.get("filename",""):r for r in monthly}
        matrix=[]
        def make_row(src,source_group,manifest_class,source_case,source_record,need_raw):
            iv=str(src.get("interval","")).strip();ts=str(src.get("open_time_ms") or src.get("expected_open_time_ms") or "").strip()
            key=(iv,ts);hit=mk.get(key)
            source_id=src.get("case_id","")
            record=raw_by.get((source_id,iv,ts)) if need_raw else None
            if record is None and need_raw:
                # Source case IDs in CP-0093 use FETCHREF-queue IDs and exactly match the raw comparison rows.
                record=next((r for r in raw if r.get("case_id")==source_id and r.get("interval")==iv and r.get("open_time_ms")==ts),None)
            ok=(bool(hit) and hit.get("case_class")==manifest_class and hit.get("acquisition_source_case_id")==source_id and
                hit.get("source_record_type")==source_record and hit.get("disposition")=="OPEN_REVIEW_REQUIRED" and hit.get("canonical_source")=="NONE" and hit.get("case_closed","").lower()=="false")
            archive=None;monthly_archive=None
            if need_raw and record:
                archive=archive_by.get(record.get("daily_archive_filename",""))
                monthly_archive=monthly_by.get(record.get("monthly_archive_filename",""))
            elif hit:
                archive=archive_by.get(hit.get("acquisition_daily_archive",""))
                monthly_archive=monthly_by.get(hit.get("acquisition_monthly_archive",""))
            upstream_fields_ok=True
            if need_raw:
                upstream_fields_ok=bool(record) and record.get("row_relation")=="SHARED_RAW_DIVERGENT" and int(record.get("economic_differing_field_count") or 0)>0 and record.get("source_authority")=="NONE" and record.get("disposition")=="OPEN_REVIEW_REQUIRED"
            else:
                upstream_fields_ok=any(p.get("case_id")==source_id and p.get("interval")==iv and p.get("open_time_ms")==ts and
                                       p.get("row_relation")=="MONTHLY_ONLY_KEY" for p in raw) is False
                # A missing daily expected-grid key is recorded in the separate missing-key ledger, not the shared-row table.
                upstream_fields_ok=bool(src.get("status")=="EXPECTED_GRID_KEY_ABSENT_REVIEW_ONLY" and src.get("synthetic_candle_created")=="False")
            monthly_ref_ok=bool(hit and monthly_archive is not None and monthly_archive.get("actual_sha256")==hit.get("acquisition_monthly_sha256"))
            daily_ref_ok=bool(hit and archive is not None and archive.get("zip_sha256")==hit.get("acquisition_daily_sha256"))
            field_match=True
            if need_raw and record and hit:
                field_match=(hit.get("acquisition_economic_differing_fields","")==record.get("economic_differing_fields",""))
            return {
              "source_case_id":source_id,"source_group":source_group,"interval":iv,"open_time_ms":ts,
              "open_time_utc":src.get("open_time_utc") or src.get("expected_open_time_utc",""),
              "source_relation":source_record,"expected_manifest_class":manifest_class,
              "manifest_exact_key_match":bool(hit),"manifest_case_id":hit.get("case_id","") if hit else "",
              "manifest_case_class":hit.get("case_class","") if hit else "",
              "manifest_source_case_match":bool(hit and hit.get("acquisition_source_case_id")==source_id),
              "manifest_record_type_match":bool(hit and hit.get("source_record_type")==source_record),
              "manifest_disposition":hit.get("disposition","") if hit else "",
              "canonical_source":hit.get("canonical_source","") if hit else "",
              "case_closed":hit.get("case_closed","") if hit else "",
              "monthly_archive":record.get("monthly_archive_filename","") if record else hit.get("acquisition_monthly_archive","") if hit else "",
              "monthly_archive_hash_match_to_manifest":monthly_ref_ok,
              "daily_archive":record.get("daily_archive_filename","") if record else hit.get("acquisition_daily_archive","") if hit else "",
              "daily_archive_hash_match_to_manifest":daily_ref_ok,
              "economic_field_list_matches_frozen_raw_row":field_match,
              "upstream_row_evidence_reconciles":upstream_fields_ok,
              "quarantine_coverage_gate":"PASS" if ok and upstream_fields_ok and field_match and monthly_ref_ok and daily_ref_ok else "FAIL",
              "source_authority":"NONE","closure_effect":"NO_CASE_CLOSURE"
            }
        for r in econ:matrix.append(make_row(r,"EXACT_KEY_ECONOMIC_CONFLICT","ACQUISITION_ECONOMIC_CONFLICT","FETCHREF", "SHARED_RAW_DIVERGENT",True))
        for r in gaps:matrix.append(make_row(r,"MISSING_EXPECTED_DAILY_GRID_KEY","ACQUISITION_MONTHLY_ONLY_ROW",r.get("case_id",""),"MONTHLY_ONLY_KEY",False))
        # Validate the 14 source IDs exactly; helper above treats economic IDs as FETCHREF queue IDs.
        for r in matrix:
            r["manifest_source_case_match"]=bool(r["manifest_exact_key_match"] and
               next((m.get("acquisition_source_case_id")==r["source_case_id"] for m in manifest if m.get("case_id")==r["manifest_case_id"]),False))
        econ_rows=matrix[:len(econ)];gap_rows=matrix[len(econ):]
        classes=Counter(r["manifest_case_class"] for r in matrix if r["manifest_exact_key_match"])
        checks_count_before=len(checks)
        ck("all_14_economic_conflicts_quarantined_by_exact_key",len(econ_rows)==14 and all(r["quarantine_coverage_gate"]=="PASS" and r["manifest_case_class"]=="ACQUISITION_ECONOMIC_CONFLICT" and r["manifest_source_case_match"] and r["economic_field_list_matches_frozen_raw_row"] for r in econ_rows),
           {"matched":sum(r["manifest_exact_key_match"] for r in econ_rows),"expected_class":classes.get("ACQUISITION_ECONOMIC_CONFLICT",0),
            "sources":sum(r["manifest_source_case_match"] for r in econ_rows)})
        ck("all_10_missing_grid_keys_quarantined_by_exact_key",len(gap_rows)==10 and all(r["quarantine_coverage_gate"]=="PASS" and r["manifest_case_class"]=="ACQUISITION_MONTHLY_ONLY_ROW" and r["manifest_source_case_match"] for r in gap_rows),
           {"matched":sum(r["manifest_exact_key_match"] for r in gap_rows),"expected_class":classes.get("ACQUISITION_MONTHLY_ONLY_ROW",0),
            "sources":sum(r["manifest_source_case_match"] for r in gap_rows)})
        keys=[(r["interval"],r["open_time_ms"]) for r in matrix]
        ck("24_selected_keys_unique_across_both_groups",len(keys)==24 and len(set(keys))==24,{"rows":len(keys),"unique_keys":len(set(keys))})
        ck("no_case_closure_or_source_promotion",all(r["canonical_source"]=="NONE" and r["case_closed"].lower()=="false" and r["source_authority"]=="NONE" for r in matrix),
           "24/24 keys remain unresolved, canonical source NONE, case_closed false")
        ck("global_gates_remain_blocked",len(blockers)==11 and pointer.get("candidate_eligibility_blocked") is True and triage.get("decisions",{}).get("canonical_source_selected") is False and triage.get("decisions",{}).get("source_cases_closed")==0,
           {"nonrow_blockers":len(blockers),"G0":"BLOCKED_GLOBAL","G2":"FAIL_CURRENT_23_CANDIDATES","G7":"LIVE_BLOCKED"})
        passed=sum(c["status"]=="PASS" for c in checks);total=len(checks)
        status="PASS_24_ACQUISITION_KEYS_CONFIRMED_QUARANTINED_SOURCE_AUTHORITY_OPEN" if passed==total else "REVIEW_REQUIRED_ACQUISITION_QUARANTINE_COVERAGE"
        outputs=[
          "CP0094_Acquisition_Quarantine_Coverage_Summary.json",
          "CP0094_Acquisition_Quarantine_Coverage_Matrix.csv",
          "CP0094_Acquisition_Quarantine_Coverage_Report_HI.md"]
        write_csv(out/outputs[1],matrix)
        report=[
          "# CP-0094: exact-key acquisition quarantine coverage audit","",
          "Status: "+status,"",
          "## Frozen rulebook and provenance",
          "- Rulebook bytes verified: 10,630; SHA-256 "+RULEBOOK_SHA+".",
          "- CP-0040 exact-key quarantine manifest SHA-256 "+manifest_sha+"; 1,427 rows with unique (interval, open_time_ms) keys.",
          "- Upstream CP-0107 daily reference audit: "+str(triage.get("status"))+" with 14/14 CP-0093 discrepancy triage checks; 16/16 daily ZIP/.CHECKSUM pairs and 14/14 monthly cache ZIPs already hash/CRC verified; no new download in this audit.","",
          "## Exact-key coverage",
          "- Economic conflicts: "+str(sum(r["quarantine_coverage_gate"]=="PASS" for r in econ_rows))+"/14 exact keys map to class ACQUISITION_ECONOMIC_CONFLICT, with matching CP-0107 source case ID, raw economic field list and both monthly/daily archive hash references.",
          "- Missing expected daily-grid keys: "+str(sum(r["quarantine_coverage_gate"]=="PASS" for r in gap_rows))+"/10 exact keys map to class ACQUISITION_MONTHLY_ONLY_ROW and matching CP-0107 source case ID.",
          "- Total: "+str(sum(r["quarantine_coverage_gate"]=="PASS" for r in matrix))+"/24 acquisition discrepancy keys explicitly covered by frozen CP-0040 quarantine.","",
          "## Decision boundary",
          "- This proves quarantine coverage only. It does not decide which verified archive is canonical, establish same-candle equivalence, or close any conflict.",
          "- Global G0 remains BLOCKED_GLOBAL because 11 non-row aggregation relationships and broader source-adjudication debt remain open. G2 remains FAIL for current 23 candidates; G7 remains LIVE_BLOCKED.",
          "- No row/worklist changes, no network/archive downloads, no candidate build or backtest, no strategy promotion, no exchange action.","",
          "## Next bounded action",
          "- Use this 24-key coverage evidence to prioritize source-authority adjudication: exact economic conflicts remain dual-source disputes; ten missing daily-grid keys remain missing-reference cases. Keep the conservative quarantine policy frozen and the builder fail-closed."
        ]
        (out/outputs[2]).write_text("\n".join(report)+"\n",encoding="utf-8")
        summary={
          "schema_version":1,"checkpoint":"CP-0094","task":"cp0094_acquisition_quarantine_coverage_audit",
          "status":status,"started_at_utc":started,"finished_at_utc":now(),
          "inputs":{"triage_summary_status":triage.get("status"),"triage_summary_sha256":sha(triage_summary_path.read_bytes()),
            "rulebook_sha256":sha(rule_bytes),"manifest_sha256":manifest_sha,"manifest_pointer_sha1":hashlib.sha1(manifest_path.read_bytes()).hexdigest(),
            "blockers_sha256":blocker_sha,"raw_row_comparison_sha256":sha(raw_path.read_bytes())},
          "coverage":{"economic_keys":len(econ_rows),"economic_exact_keys_quarantined":sum(r["quarantine_coverage_gate"]=="PASS" for r in econ_rows),
            "monthly_only_expected_grid_keys":len(gap_rows),"monthly_only_exact_keys_quarantined":sum(r["quarantine_coverage_gate"]=="PASS" for r in gap_rows),
            "all_24_quarantined":len(matrix)==24 and all(r["quarantine_coverage_gate"]=="PASS" for r in matrix),
            "classes":dict(classes),"manifest_rows":len(manifest),"manifest_unique_exact_keys":len(mk)},
          "checks":checks,"checks_passed":passed,"checks_total":total,
          "network_used":False,"archive_downloads":0,"source_bytes_modified":False,"worklist_mutated":False,
          "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
          "unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED",
          "production_candidate_build":False,"backtest_rerun":False,"strategy_promoted":False,
          "next_action":"Continue evidence-linked source-authority adjudication without source preference; preserve quarantine and blocked global gates."}
        for name in outputs[1:]:
            p=out/name;summary.setdefault("outputs",{})[name]={"bytes":p.stat().st_size,"sha256":sha(p.read_bytes()),"rows":len(read_csv(p)) if name.endswith(".csv") else None}
        write_json(out/outputs[0],summary)
        print(json.dumps({"status":status,"checks_passed":passed,"checks_total":total,
          "economic_quarantined":summary["coverage"]["economic_exact_keys_quarantined"],
          "missing_grid_quarantined":summary["coverage"]["monthly_only_exact_keys_quarantined"],
          "all24":summary["coverage"]["all_24_quarantined"],"g0":"BLOCKED_GLOBAL"},ensure_ascii=False,sort_keys=True))
        return 0 if status.startswith("PASS_") else 1
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0094","task":"cp0094_acquisition_quarantine_coverage_audit",
          "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),
          "error_type":type(exc).__name__,"error":str(exc),"checks":checks,"network_used":False,"archive_downloads":0,
          "canonical_source_selected":False,"source_cases_closed":0,"unresolved_nonrow_aggregation_blockers":11,
          "g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED"}
        write_json(out/"CP0094_Acquisition_Quarantine_Coverage_Summary.json",summary)
        (out/"CP0094_Acquisition_Quarantine_Coverage_Report_HI.md").write_text("# CP-0094 acquisition quarantine coverage audit\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\n"+type(exc).__name__+": "+str(exc)+"\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1
if __name__=="__main__":raise SystemExit(main())
