#!/usr/bin/env python3
"""CP-0107 Shared-52 candidate-input dependency map.

Read-only reconciliation of the already committed 52-case economic-conflict
crosswalk against the frozen CP-0040 exact-key quarantine manifest, the official
correction-package inventory, and the already-published MTF_BREAKOUT_4H_D1
quarantine-sensitivity result. No downloads, no candidate build/backtest, and
no source-authority or row-closure decisions.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW_CROSSWALK_BLOB="acbdf6fc6e161cbf18abde221a050701e88a9c01"
OFFICIAL_CROSSWALK_BLOB="718c2ac990d9fb5d9c731fdda4fc92657d375ad2"
MATRIX_BLOB="8e727ea57035240a912040972e73a3ed12c2a653"
MANIFEST_SHA256="e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a"
OFFICIAL_PACKAGE_SUMMARY_BLOB="f604dcbea77c1a642d37e14f36e36a38c4d25359"
SENSITIVITY_SUMMARY_SHA256="cf774e24112b3cb472853f8de725de0c4eb23f710b9d1b9266d628b9c606f809"
DIRECT_INTERVALS={"4h","1d"}
EXPECTED_DIRECT_KEYS={
 ("1d","1611187200000"),
 ("4h","1611216000000"),
 ("1d","1640304000000"),
 ("4h","1640304000000"),
}
def now(): return datetime.now(timezone.utc).isoformat()
def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str: return sha(Path(p).read_bytes())
def git_blob_sha1(b:bytes)->str: return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read_json(p:Path): return json.loads(Path(p).read_text(encoding="utf-8"))
def read_csv(p:Path):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write_json(p:Path,obj):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p:Path,rows:list[dict]):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n")
        w.writeheader()
        if rows: w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-crosswalk",default="evidence/source_adjudication/CP0107_Shared52_RowValue_VersionCrosswalk.csv")
    ap.add_argument("--official-crosswalk",default="evidence/source_adjudication/CP0107_Official_Update_Package_Shared52_DailyCrosswalk.csv")
    ap.add_argument("--matrix",default="evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Matrix.csv")
    ap.add_argument("--official-package-summary",default="evidence/source_adjudication/CP0107_Official_Update_Package_Summary.json")
    ap.add_argument("--manifest-pointer",default="evidence/source_adjudication/CP0040_Current_Manifest.json")
    ap.add_argument("--sensitivity-pointer",default="evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Current.json")
    ap.add_argument("--output-dir",default="results/cp0107_shared52_candidate_input_dependency_audit")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    checks=[]
    def ck(name,ok,detail): checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
    try:
        raw_path=ROOT/a.raw_crosswalk; official_path=ROOT/a.official_crosswalk; matrix_path=ROOT/a.matrix
        package_path=ROOT/a.official_package_summary; package=read_json(package_path)
        mptr=read_json(ROOT/a.manifest_pointer); sptr=read_json(ROOT/a.sensitivity_pointer)
        manifest_path=ROOT/mptr["manifest_path"]; blocker_path=ROOT/mptr["blockers_path"]
        sensitivity_summary_path=ROOT/sptr["summary_path"]
        sensitivity_summary=read_json(sensitivity_summary_path)
        impact_path=sensitivity_summary_path.parent/"CP0040_Input_Impact.csv"
        performance_path=sensitivity_summary_path.parent/"CP0040_Quarantine_Performance.csv"
        required=(raw_path,official_path,matrix_path,package_path,manifest_path,blocker_path,sensitivity_summary_path,impact_path,performance_path)
        missing=[str(p) for p in required if not p.is_file()]
        ck("all_frozen_inputs_present",not missing,missing or "all present")
        if missing: raise ValueError("Missing frozen input(s): "+", ".join(missing))
        raw_rows=read_csv(raw_path); official_rows=read_csv(official_path); matrix_rows=read_csv(matrix_path)
        manifest_rows=read_csv(manifest_path); blockers=read_csv(blocker_path)
        input_impact=read_csv(impact_path); performance=read_csv(performance_path)
        raw_blob=git_blob_sha1(raw_path.read_bytes()); official_blob=git_blob_sha1(official_path.read_bytes()); matrix_blob=git_blob_sha1(matrix_path.read_bytes())
        ck("shared52_raw_crosswalk_blob_and_rows",raw_blob==RAW_CROSSWALK_BLOB and len(raw_rows)==52,f"blob={raw_blob}; rows={len(raw_rows)}")
        ck("shared52_official_crosswalk_blob_and_rows",official_blob==OFFICIAL_CROSSWALK_BLOB and len(official_rows)==52,f"blob={official_blob}; rows={len(official_rows)}")
        ck("shared52_matrix_blob_and_rows",matrix_blob==MATRIX_BLOB and len(matrix_rows)==52,f"blob={matrix_blob}; rows={len(matrix_rows)}")
        ck("official_update_package_summary_anchor",git_blob_sha1(package_path.read_bytes())==OFFICIAL_PACKAGE_SUMMARY_BLOB and package.get("status")=="PASS_OFFICIAL_UPDATE_PACKAGE_INSPECTED_SOURCE_AUTHORITY_OPEN" and package.get("checks_passed")==13 and package.get("checks_total")==13,{"blob":git_blob_sha1(package_path.read_bytes()),"status":package.get("status")})
        ck("official_bundle_contains_no_target_archive_members",package.get("package_inventory",{}).get("exact_archive_member_name_hits")==0 and package.get("package_inventory",{}).get("text_filename_reference_hits")==0 and package.get("package_inventory",{}).get("frozen_hash_token_hits")==0 and package.get("package_inventory",{}).get("member_count")==2,package.get("package_inventory",{}))
        ck("official_shared52_path_coverage_anchor",package.get("shared52_daily_crosswalk",{}).get("exact_official_daily_path_case_rows")==33 and package.get("shared52_daily_crosswalk",{}).get("no_exact_official_daily_path_case_rows")==19,package.get("shared52_daily_crosswalk",{}))
        manifest_sha=sha_file(manifest_path); block_sha=sha_file(blocker_path)
        ck("manifest_pointer_hash_and_gate",mptr.get("manifest_sha256")==MANIFEST_SHA256 and manifest_sha==MANIFEST_SHA256 and mptr.get("candidate_eligibility_blocked") is True,f"sha={manifest_sha}; status={mptr.get('status')}")
        ck("eleven_nonrow_blockers_preserved",block_sha=="f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36" and len(blockers)==11,{"sha256":block_sha,"rows":len(blockers)})
        sens_sha=sha_file(sensitivity_summary_path)
        ck("sensitivity_summary_anchor_and_gate",sens_sha==SENSITIVITY_SUMMARY_SHA256 and sensitivity_summary.get("status")=="PASS_QUARANTINE_SENSITIVITY_DIAGNOSTIC_COMPLETE" and sensitivity_summary.get("baseline_metric_gate")=="PASS",{"sha256":sens_sha,"status":sensitivity_summary.get("status"),"baseline_gate":sensitivity_summary.get("baseline_metric_gate")})
        ck("quarantine_manifest_unique_exact_keys",len(manifest_rows)==1427 and len({(r.get("interval",""),r.get("open_time_ms","")) for r in manifest_rows})==1427,{"rows":len(manifest_rows),"unique_keys":len({(r.get("interval",""),r.get("open_time_ms","")) for r in manifest_rows})})
        raw_by={r["case_id"]:r for r in raw_rows}; official_by={r["case_id"]:r for r in official_rows}; matrix_by={r["case_id"]:r for r in matrix_rows}
        ids=[r["case_id"] for r in raw_rows]
        ck("crosswalk_case_ids_unique_and_exact_joined",len(ids)==52 and len(set(ids))==52 and set(ids)==set(official_by)==set(matrix_by),{"raw":len(ids),"unique":len(set(ids)),"official":len(official_by),"matrix":len(matrix_by)})
        manifest_by_key={(r.get("interval",""),r.get("open_time_ms","")):r for r in manifest_rows}
        output_rows=[]
        for r in raw_rows:
            cid=r["case_id"]; iv=r["interval"]; ts=r["open_time_ms"]; key=(iv,ts)
            man=manifest_by_key.get(key); off=official_by[cid]; mat=matrix_by[cid]
            direct=iv in DIRECT_INTERVALS
            expected_direct=key in EXPECTED_DIRECT_KEYS
            key_match=bool(man and man.get("case_id")==cid and man.get("case_class")=="SHARED_ECONOMIC_CONFLICT")
            official_no_path=str(off.get("exact_official_daily_path_found","")).strip().lower()=="false"
            state_ok=(r.get("current_disposition")=="UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION" and
                      r.get("canonical_source")=="NONE" and str(r.get("case_closed","")).lower()=="false" and
                      man is not None and man.get("disposition")=="UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION" and
                      man.get("canonical_source")=="NONE" and str(man.get("case_closed","")).lower()=="false")
            output_rows.append({
                "case_id":cid,"interval":iv,"utc_date":r["utc_date"],"open_time_ms":ts,"open_time_utc":r["open_time_utc"],
                "economic_difference_fields":r.get("economic_difference_fields",""),
                "direct_input_for_frozen_MTF_BREAKOUT_4H_D1":direct,
                "strategy_direct_input_role":"LOCAL_4H_BARS" if iv=="4h" else ("COMPLETED_1D_REGIME" if iv=="1d" else "NOT_DIRECT_INPUT_INTERVAL"),
                "exact_key_in_frozen_quarantine_manifest":bool(man),
                "same_case_id_and_shared_economic_class":key_match,
                "exact_official_daily_path_in_inspected_update_bundle":not official_no_path,
                "new_checksum_matches_frozen_daily_sha256":off.get("official_new_checksum_matches_frozen_daily_sha256",""),
                "original_checksum_matches_frozen_daily_sha256":off.get("official_original_checksum_matches_frozen_daily_sha256",""),
                "disposition_preserved":state_ok,
                "disposition":r.get("current_disposition",""),
                "canonical_source":r.get("canonical_source",""),
                "case_closed":r.get("case_closed",""),
                "direct_key_expected_from_frozen_case_set":expected_direct,
                "evidence_limit":"Official bundle exact path/checksum is provenance only; conflict remains open."
            })
        direct_rows=[r for r in output_rows if r["direct_input_for_frozen_MTF_BREAKOUT_4H_D1"]]
        direct_keys={(r["interval"],r["open_time_ms"]) for r in direct_rows}
        impact_by={r["interval"]:r for r in input_impact}
        expected_impact=set(impact_by)=={"4h","1d","1mo"} and all(str(impact_by[iv].get("replacements_added"))=="0" for iv in impact_by)
        perf_by={r["period"]:r for r in performance}
        train_delta=float(perf_by["TRAIN"]["delta_net_return_percentage_points"])
        dev_delta=float(perf_by["DEVELOPMENT_CHECK"]["delta_net_return_percentage_points"])
        oos_delta=float(perf_by["CONSUMED_OOS_DIAGNOSTIC"]["delta_net_return_percentage_points"])
        ck("all_52_shared_keys_exactly_match_quarantine_manifest",all(r["exact_key_in_frozen_quarantine_manifest"] and r["same_case_id_and_shared_economic_class"] for r in output_rows),f"matched={sum(r['exact_key_in_frozen_quarantine_manifest'] for r in output_rows)}/52")
        ck("four_direct_input_keys_match_frozen_expected_set",len(direct_rows)==4 and direct_keys==EXPECTED_DIRECT_KEYS and all(r["direct_key_expected_from_frozen_case_set"] for r in direct_rows),[r["case_id"] for r in direct_rows])
        ck("all_four_direct_input_keys_quarantined_and_open",len(direct_rows)==4 and all(r["exact_key_in_frozen_quarantine_manifest"] and r["disposition_preserved"] and r["exact_official_daily_path_in_inspected_update_bundle"] is False for r in direct_rows),[{"case_id":r["case_id"],"manifest":r["exact_key_in_frozen_quarantine_manifest"],"no_bundle_path":not r["exact_official_daily_path_in_inspected_update_bundle"]} for r in direct_rows])
        ck("remaining_48_not_direct_for_this_frozen_comparator",sum(not r["direct_input_for_frozen_MTF_BREAKOUT_4H_D1"] for r in output_rows)==48 and all(r["strategy_direct_input_role"]=="NOT_DIRECT_INPUT_INTERVAL" for r in output_rows if not r["direct_input_for_frozen_MTF_BREAKOUT_4H_D1"]),{"direct":len(direct_rows),"non_direct":len(output_rows)-len(direct_rows)})
        ck("input_impact_counts_and_no_replacement",expected_impact and int(impact_by["4h"]["removed_exact_key_rows"])==6 and int(impact_by["1d"]["removed_exact_key_rows"])==3 and int(impact_by["1mo"]["removed_exact_key_rows"])==0, {iv:{"removed":int(r["removed_exact_key_rows"]),"after":int(r["quarantine_rows_after_filter"]),"replacements":r["replacements_added"]} for iv,r in impact_by.items()})
        ck("three_frozen_sensitivity_period_metrics_present",set(perf_by)=={"TRAIN","DEVELOPMENT_CHECK","CONSUMED_OOS_DIAGNOSTIC"} and all(r.get("baseline_metric_anchors_match")=="True" for r in performance),{"TRAIN_delta_pp":train_delta,"DEVELOPMENT_CHECK_delta_pp":dev_delta,"CONSUMED_OOS_DIAGNOSTIC_delta_pp":oos_delta})
        ck("source_authority_and_promotion_gates_unchanged",all(r["disposition_preserved"] for r in output_rows) and mptr.get("status")=="PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN" and sptr.get("status")=="PASS_QUARANTINE_SENSITIVITY_DIAGNOSTIC_COMPLETE",{"all_52_open":all(r["disposition_preserved"] for r in output_rows),"g0":"BLOCKED_GLOBAL","canonical_source":"NONE"})
        status="PASS_SHARED52_CANDIDATE_INPUT_DEPENDENCY_MAP_COMPLETE_NOT_G0_APPROVAL" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_SHARED52_INPUT_MAP_GATE_FAILURE"
        s={
            "schema_version":1,"checkpoint":"CP-0107","task":"cp0107_shared52_candidate_input_dependency_audit",
            "status":status,"started_at_utc":started,"finished_at_utc":now(),
            "scope":"READ_ONLY_SHARED52_ECONOMIC_CONFLICTS_VS_FROZEN_MTF_BREAKOUT_4H_D1_INPUTS_AND_CP0040_QUARANTINE",
            "evidence":{"raw_crosswalk_git_blob_sha1":raw_blob,"official_crosswalk_git_blob_sha1":official_blob,"matrix_git_blob_sha1":matrix_blob,
                "official_package_summary_git_blob_sha1":git_blob_sha1(package_path.read_bytes()),"cp0040_manifest_sha256":manifest_sha,
                "cp0040_nonrow_blockers_sha256":block_sha,"sensitivity_summary_sha256":sens_sha},
            "candidate_dependency":{"comparator":"MTF_BREAKOUT_4H_D1","direct_input_intervals":["4h","1d"],
                "shared52_total":52,"direct_input_conflicts":len(direct_rows),"direct_4h_conflicts":sum(r["interval"]=="4h" for r in direct_rows),
                "direct_1d_conflicts":sum(r["interval"]=="1d" for r in direct_rows),"not_direct_interval_conflicts":len(output_rows)-len(direct_rows),
                "direct_cases":[{"case_id":r["case_id"],"interval":r["interval"],"open_time_utc":r["open_time_utc"],"fields":r["economic_difference_fields"]} for r in direct_rows],
                "all_52_exact_keys_in_cp0040_quarantine_manifest":all(r["exact_key_in_frozen_quarantine_manifest"] for r in output_rows),
                "all_four_direct_keys_in_quarantine_manifest":all(r["exact_key_in_frozen_quarantine_manifest"] for r in direct_rows),
                "all_four_direct_cases_missing_exact_path_in_inspected_official_update_bundle":all(not r["exact_official_daily_path_in_inspected_update_bundle"] for r in direct_rows)},
            "quarantine_effect":{"rows_removed_by_interval":{"4h":int(impact_by["4h"]["removed_exact_key_rows"]),"1d":int(impact_by["1d"]["removed_exact_key_rows"]),"1mo":int(impact_by["1mo"]["removed_exact_key_rows"])},
                "TRAIN_net_return_delta_percentage_points":train_delta,"DEVELOPMENT_CHECK_net_return_delta_percentage_points":dev_delta,
                "CONSUMED_OOS_DIAGNOSTIC_net_return_delta_percentage_points":oos_delta,
                "causal_attribution_to_four_direct_cases":"NOT_ESTABLISHED; sensitivity was a full-manifest scenario, not a four-row ablation"},
            "official_update_package":{"status":package["status"],"checks_passed":package["checks_passed"],"checks_total":package["checks_total"],
                "member_count":package["package_inventory"]["member_count"],"target_archive_member_name_hits":package["package_inventory"]["exact_archive_member_name_hits"],
                "target_text_filename_hits":package["package_inventory"]["text_filename_reference_hits"],
                "shared52_exact_paths":package["shared52_daily_crosswalk"]["exact_official_daily_path_case_rows"],
                "shared52_no_exact_path":package["shared52_daily_crosswalk"]["no_exact_official_daily_path_case_rows"]},
            "rows":output_rows,"checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
            "network_used":False,"archive_downloads":0,"source_bytes_modified":False,"production_candidate_build":False,"backtest_rerun":False,
            "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
            "unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","strategy_promoted":False,
            "live_signing_broadcast_orders":"BLOCKED",
            "decision":"Four of 52 economic conflicts (two 4h and two 1d) coincide with the frozen comparator's direct intervals. All four are in the exact-key quarantine manifest and remain unresolved; the inspected official correction bundle provides no exact daily archive path for them. This supports quarantine as an input-control action but does not adjudicate which source is canonical. The full-manifest TRAIN delta is material; no four-row causal attribution was run.",
            "next_action":"Do not repeat the already-complete correction-bundle inventory. Advance to the remaining G0 eligibility blocker: verify the frozen CP-0040 rulebook in its original source pack, then explicitly decide whether the candidate-specific exact-key quarantine policy satisfies every G0 clause while the 11 relationship blockers remain open. Keep the production builder fail-closed until the frozen rulebook conditions are met."
        }
        write_json(out/"CP0107_Shared52_Candidate_Input_Dependency_Summary.json",s)
        write_csv(out/"CP0107_Shared52_Candidate_Input_Dependency_Matrix.csv",output_rows)
        lines=["# CP-0107 Shared-52 candidate-input dependency audit","",
            "Status: "+status,
            "",
            "## Frozen comparator and direct-input overlap",
            "- Comparator: MTF_BREAKOUT_4H_D1; direct intervals are 4h local bars and completed 1d regime.",
            "- Shared-52 economic conflicts: 52. Direct-input overlaps: 4 (2 x 4h, 2 x 1d); remaining 48 are in other intervals and are not direct inputs for this comparator.",
            "- All 52 exact (interval, open_time_ms) keys join the frozen CP-0040 quarantine manifest by key/case ID and remain unresolved, canonical source NONE, case_closed false.",
            "",
            "| Case | Interval | UTC open | Official update bundle exact daily path | Exact-key quarantined | Disposition |",
            "|---|---|---|---|---|---|"]
        for r in direct_rows:
            lines.append("| "+r["case_id"]+" | "+r["interval"]+" | "+r["open_time_utc"]+" | "+str(r["exact_official_daily_path_in_inspected_update_bundle"])+" | "+str(r["exact_key_in_frozen_quarantine_manifest"])+" | OPEN |")
        lines += ["","## Already-published full-manifest sensitivity",
            "- Exact-key rows removed: 4h=6, 1d=3, 1mo=0; replacements added=0.",
            f"- Return delta: TRAIN {train_delta:.6f} percentage points; DEVELOPMENT_CHECK {dev_delta:.6f}; CONSUMED_OOS_DIAGNOSTIC {oos_delta:.6f}.",
            "- These are full-manifest results; impact attributable to only the four direct Shared-52 cases is NOT_ESTABLISHED because a four-row ablation was not run.",
            "",
            "## Official correction-package limit",
            "- The previously verified official 2022-08-08 correction bundle has 2 non-directory members, no target monthly archive members, 0 target filename text references and 0 current frozen monthly SHA token references.",
            "- For Shared-52, the bundle has exact daily paths for 33 cases and none for 19. All four direct 4h/1d cases fall in the no-exact-path group.",
            "- Bundle-path absence is not evidence that the archive never existed; New checksum matches for 33 other cases are provenance evidence only.",
            "",
            "## Decision",
            "- Keep all 52 cases open; no canonical source selected; root cause OPEN_NOT_ESTABLISHED; all 11 non-row aggregation blockers open; G0 BLOCKED_GLOBAL.",
            "- Next: verify the frozen CP-0040 rulebook bytes against the original source pack and make a rulebook-bound candidate eligibility decision. Do not weaken the CP-0026 builder gate.",
            "- No network, archive download, data edits, candidate build, backtest rerun, strategy promotion or live actions occurred."]
        (out/"CP0107_Shared52_Candidate_Input_Dependency_Report_HI.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
        print(json.dumps({"status":status,"checks_passed":s["checks_passed"],"checks_total":s["checks_total"],
            "shared52":len(output_rows),"direct_conflicts":len(direct_rows),"direct_4h":sum(r["interval"]=="4h" for r in direct_rows),
            "direct_1d":sum(r["interval"]=="1d" for r in direct_rows),"manifest_key_matches":sum(r["exact_key_in_frozen_quarantine_manifest"] for r in output_rows),
            "TRAIN_delta_pp":train_delta,"network_used":False,"g0":"BLOCKED_GLOBAL"},ensure_ascii=False,sort_keys=True))
        return 0 if status.startswith("PASS") else 1
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0107","task":"cp0107_shared52_candidate_input_dependency_audit",
            "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),
            "error_type":type(exc).__name__,"error":str(exc),"checks":checks,"network_used":False,"archive_downloads":0,
            "source_bytes_modified":False,"production_candidate_build":False,"backtest_rerun":False,
            "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
            "unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","strategy_promoted":False,
            "live_signing_broadcast_orders":"BLOCKED"}
        write_json(out/"CP0107_Shared52_Candidate_Input_Dependency_Summary.json",summary)
        (out/"CP0107_Shared52_Candidate_Input_Dependency_Report_HI.md").write_text(
            "# CP-0107 Shared-52 candidate-input dependency audit\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\n"+type(exc).__name__+": "+str(exc)+"\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1
if __name__=="__main__": raise SystemExit(main())
