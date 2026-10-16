#!/usr/bin/env python3
"""Rulebook-bound candidate-specific G0 decision for MTF_BREAKOUT_4H_D1.

Read-only: verifies the frozen acceptance rulebook, exact-key quarantine scope,
published sensitivity metrics, relationship blocker relevance, and the unchanged
production builder guard. No download, source mutation, candidate build/backtest,
source selection, strategy promotion or live order.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RULEBOOK_SHA="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
RULEBOOK_BYTES=10630
CP0041_PACK_SHA="23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc"
CP0046_PACK_SHA="014b6eb93aef6d3fb111dae7c965b8b49c027ace3c11cb140f7ebb4a83813c4b"
MANIFEST_SHA="e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a"
BLOCKERS_SHA="f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36"
SENSITIVITY_SUMMARY_SHA="cf774e24112b3cb472853f8de725de0c4eb23f710b9d1b9266d628b9c606f809"
EXPECTED_REMOVALS={"4h":6,"1d":3,"1mo":0}

def now(): return datetime.now(timezone.utc).isoformat()
def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str: return sha(Path(p).read_bytes())
def read_json(p:Path): return json.loads(Path(p).read_text(encoding="utf-8"))
def read_csv(p:Path):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write_json(p:Path,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p:Path,rows):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader()
        if rows:w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--rulebook",default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
    ap.add_argument("--rulebook-receipt",default="evidence/source_adjudication/CP0040_Original_Rulebook_Verification_Receipt.json")
    ap.add_argument("--manifest-pointer",default="evidence/source_adjudication/CP0040_Current_Manifest.json")
    ap.add_argument("--sensitivity-pointer",default="evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Current.json")
    ap.add_argument("--dependency-pointer",default="evidence/source_adjudication/CP0107_Shared52_Candidate_Input_Dependency_Current.json")
    ap.add_argument("--relevance-pointer",default="evidence/source_adjudication/CP0040_Candidate_Input_Relevance_Current.json")
    ap.add_argument("--matrix-pointer",default="evidence/source_adjudication/CP0040_Archive_Integrity_Matrix_Current.json")
    ap.add_argument("--builder",default="scripts/AISTS_CP0026_Research_Candidate_Builder.py")
    ap.add_argument("--output-dir",default="results/cp0040_rulebook_bound_eligibility_decision")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    checks=[]
    def ck(n,ok,d):checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    try:
        rulebook_path=ROOT/a.rulebook;receipt_path=ROOT/a.rulebook_receipt
        mp=read_json(ROOT/a.manifest_pointer);sp=read_json(ROOT/a.sensitivity_pointer)
        dp=read_json(ROOT/a.dependency_pointer);rp=read_json(ROOT/a.relevance_pointer);xp=read_json(ROOT/a.matrix_pointer)
        manifest=ROOT/mp["manifest_path"];manifest_summary_path=ROOT/mp["summary_path"];blockers=ROOT/mp["blockers_path"]
        sens_path=ROOT/sp["summary_path"];sens=read_json(sens_path)
        impact_path=sens_path.parent/"CP0040_Input_Impact.csv"
        keyapp_path=sens_path.parent/"CP0040_Quarantine_Key_Application.csv"
        perf_path=sens_path.parent/"CP0040_Quarantine_Performance.csv"
        dep=read_json(ROOT/dp["summary_path"]);rel=read_json(ROOT/rp["summary_path"])
        matrix_summary=read_json(ROOT/xp["summary_path"])
        builder_path=ROOT/a.builder
        required=(rulebook_path,receipt_path,manifest,manifest_summary_path,blockers,sens_path,impact_path,keyapp_path,perf_path,
                  ROOT/dp["summary_path"],ROOT/rp["summary_path"],ROOT/xp["summary_path"],builder_path)
        missing=[str(p) for p in required if not p.is_file()]
        ck("all_frozen_evidence_files_present",not missing,missing or "all present")
        if missing: raise ValueError("Missing frozen evidence: "+", ".join(missing))

        rule_bytes=rulebook_path.read_bytes();rule_sha=sha(rule_bytes);rule_text=rule_bytes.decode("utf-8")
        receipt=read_json(receipt_path);rr=receipt.get("rulebook",{})
        ck("rulebook_exact_bytes_and_sha256",len(rule_bytes)==RULEBOOK_BYTES and rule_sha==RULEBOOK_SHA,{"bytes":len(rule_bytes),"sha256":rule_sha})
        packages=receipt.get("source_packages",[])
        cp41=next((x for x in packages if x.get("filename")=="AISTS_CP0041_Row_Level_Evidence_Disposition_Pack.zip"),{})
        cp46=next((x for x in packages if x.get("filename")=="AISTS_CP0046_Candidate_Source_Impact_Audit_Pack.zip"),{})
        ck("dual_original_pack_provenance",rr.get("sha256")==RULEBOOK_SHA and rr.get("bytes")==RULEBOOK_BYTES and rr.get("byte_identical_across_packages") is True and cp41.get("sha256")==CP0041_PACK_SHA and cp46.get("sha256")==CP0046_PACK_SHA and cp41.get("zip_crc")=="PASS" and cp46.get("zip_crc")=="PASS",{"CP0041_pack":cp41.get("sha256"),"CP0046_pack":cp46.get("sha256")})
        g0_clause=("G0 — Source/data eligibility" in rule_text and "each unresolved item explicitly quarantined" in rule_text and "final metrics based on that quarantine policy" in rule_text)
        g3_clause=("G3 — Candidate stability / stress" in rule_text and "Material metric differences caused by a source policy mean the data gate remains open" in rule_text)
        s3_clause=("MTF_BREAKOUT_4H_D1" in rule_text and "FAIL / NOT PROMOTED under current screen" in rule_text and "No candidate currently passes the frozen acceptance gates" in rule_text)
        ck("frozen_G0_G3_and_current_candidate_decision_clauses_present",g0_clause and g3_clause and s3_clause,{"G0_quarantine_branch":g0_clause,"G3_material_sensitivity_rule":g3_clause,"Section_3_frozen_fail":s3_clause})
        ck("rulebook_copy_path_and_member_name",rr.get("path")==a.rulebook and rr.get("original_member_name")=="AISTS_CP0040_Strategy_Acceptance_Rulebook_HI.md",rr)

        manifest_sha=sha_file(manifest);block_sha=sha_file(blockers)
        manifest_rows=read_csv(manifest);blocker_rows=read_csv(blockers)
        unique_keys={(r.get("interval",""),r.get("open_time_ms","")) for r in manifest_rows}
        ck("frozen_manifest_hash_and_unique_keys",manifest_sha==MANIFEST_SHA and mp.get("manifest_sha256")==MANIFEST_SHA and len(manifest_rows)==1427 and len(unique_keys)==1427 and mp.get("candidate_eligibility_blocked") is True,{"sha256":manifest_sha,"rows":len(manifest_rows),"unique_keys":len(unique_keys)})
        ck("eleven_nonrow_blockers_remain_open",block_sha==BLOCKERS_SHA and len(blocker_rows)==11 and sp.get("g0")=="BLOCKED_GLOBAL" and mp.get("status")=="PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN",{"sha256":block_sha,"rows":len(blocker_rows),"g0":sp.get("g0")})

        impact=read_csv(impact_path);keyapp=read_csv(keyapp_path);perf=read_csv(perf_path)
        interval_counts={iv:sum(r.get("interval")==iv for r in manifest_rows) for iv in ("4h","1d","1mo")}
        ck("manifest_keys_on_candidate_intervals_exact_counts",interval_counts=={"4h":6,"1d":3,"1mo":0},interval_counts)
        impact_by={r.get("interval"):r for r in impact}
        impact_ok=set(impact_by)==set(EXPECTED_REMOVALS) and all(int(impact_by[iv].get("removed_exact_key_rows","-1"))==n and str(impact_by[iv].get("replacements_added"))=="0" and str(impact_by[iv].get("output_content_roundtrip"))=="True" for iv,n in EXPECTED_REMOVALS.items())
        ck("candidate_input_quarantine_counts_and_no_replacements",impact_ok,{iv:{"removed":r.get("removed_exact_key_rows"),"after":r.get("quarantine_rows_after_filter"),"replacement":r.get("replacements_added")} for iv,r in impact_by.items()})
        app_by={(r.get("interval",""),r.get("open_time_ms","")):r for r in keyapp}
        direct_rows=[r for r in manifest_rows if r.get("interval") in ("4h","1d")]
        direct_keys={(r.get("interval",""),r.get("open_time_ms","")) for r in direct_rows}
        applied_keys=set(app_by)
        exact_removed=len(direct_rows)==9 and len(keyapp)==9 and direct_keys==applied_keys and all(
            app_by.get(k) is not None and app_by[k].get("baseline_row_removed")=="True" and
            app_by[k].get("replacement_row_added")=="False" and app_by[k].get("canonical_source")=="NONE" and
            str(app_by[k].get("case_closed","")).lower()=="false" for k in direct_keys)
        ck("all_nine_direct_4h_1d_exact_keys_removed_without_replacement",exact_removed,{"manifest_direct_keys":len(direct_rows),"key_application_rows":len(keyapp),"exact_key_sets_equal":direct_keys==applied_keys,"removed_rows":sum(app_by.get(k,{}).get("baseline_row_removed")=="True" for k in direct_keys)})
        sens_sha=sha_file(sens_path)
        ck("published_sensitivity_summary_anchored",sens_sha==SENSITIVITY_SUMMARY_SHA and sens.get("status")=="PASS_QUARANTINE_SENSITIVITY_DIAGNOSTIC_COMPLETE" and sens.get("baseline_metric_gate")=="PASS" and sens.get("canonical_source")=="NONE" and sens.get("unresolved_nonrow_aggregation_blockers")==11,{"sha256":sens_sha,"status":sens.get("status"),"baseline_gate":sens.get("baseline_metric_gate")})
        perf_by={r.get("period"):r for r in perf};periods={"TRAIN","DEVELOPMENT_CHECK","CONSUMED_OOS_DIAGNOSTIC"}
        perf_ok=set(perf_by)==periods and all(r.get("baseline_metric_anchors_match")=="True" for r in perf)
        train_delta=float(perf_by["TRAIN"]["delta_net_return_percentage_points"])
        dev_delta=float(perf_by["DEVELOPMENT_CHECK"]["delta_net_return_percentage_points"])
        oos_delta=float(perf_by["CONSUMED_OOS_DIAGNOSTIC"]["delta_net_return_percentage_points"])
        ck("three_frozen_period_metrics_anchored",perf_ok,{"TRAIN_delta_pp":train_delta,"DEVELOPMENT_CHECK_delta_pp":dev_delta,"CONSUMED_OOS_DIAGNOSTIC_delta_pp":oos_delta})
        ck("shared52_four_direct_conflicts_are_quarantined",dp.get("status")=="PASS_SHARED52_CANDIDATE_INPUT_DEPENDENCY_MAP_COMPLETE_NOT_G0_APPROVAL" and dep.get("candidate_dependency",{}).get("direct_input_conflicts")==4 and dep.get("candidate_dependency",{}).get("all_four_direct_keys_in_quarantine_manifest") is True,{"status":dp.get("status"),"direct_conflicts":dep.get("candidate_dependency",{}).get("direct_input_conflicts")})
        ck("eleven_aggregation_buckets_outside_comparator_direct_inputs",rp.get("status")=="PASS_CANDIDATE_INPUT_RELEVANCE_REVIEW_COMPLETE_NOT_G0_APPROVAL" and rel.get("strategy_dependency",{}).get("residual_blockers_with_direct_4h_d1_interval_overlap")==0 and xp.get("status")=="PASS_OFFICIAL_ARCHIVE_INTEGRITY_CONFLICT_MATRIX_COMPLETE",{"direct_overlap":rel.get("strategy_dependency",{}).get("residual_blockers_with_direct_4h_d1_interval_overlap"),"matrix_status":xp.get("status")})
        builder=builder_path.read_text(encoding="utf-8");builder_sha=sha_file(builder_path)
        builder_guard=("G0_BLOCKED_NONROW_BLOCKERS_REMAIN" in builder and "if len(blockers) > 0" in builder)
        ck("production_builder_unchanged_fail_closed_guard",builder_guard,{"sha256":builder_sha,"guard_present":builder_guard})

        candidate_g0=("PASS_QUARANTINE_BRANCH_FOR_THIS_FROZEN_DIAGNOSTIC_COMPARATOR_ONLY" if (
            g0_clause and exact_removed and perf_ok and sens.get("baseline_metric_gate")=="PASS" and
            rel.get("strategy_dependency",{}).get("residual_blockers_with_direct_4h_d1_interval_overlap")==0
        ) else "BLOCKED_CANDIDATE_SPECIFIC_EVIDENCE_INCOMPLETE")
        global_g0="BLOCKED_GLOBAL" if len(blocker_rows)==11 and builder_guard else "REVIEW_REQUIRED_GLOBAL_G0"
        g3="BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT" if abs(train_delta)>=1.0 else "REVIEW_REQUIRED_G3"
        overall="PASS_RULEBOOK_BOUND_DECISION_GLOBAL_GATES_REMAIN_BLOCKED" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_RULEBOOK_DECISION_INPUT_GATE"
        decision={
          "candidate":"MTF_BREAKOUT_4H_D1",
          "candidate_specific_g0_quarantine_branch":candidate_g0,
          "global_g0":global_g0,
          "production_candidate_build":"BLOCKED_CP0026_FAIL_CLOSED_NONROW_BLOCKERS",
          "g2":"FAIL_NOT_PROMOTED",
          "g3":g3,
          "canonical_source":"NONE","source_cases_closed":0,"unresolved_nonrow_aggregation_blockers":11,"live":"BLOCKED",
          "basis":"All 9 exact-key manifest entries on the comparator's 4h/1d input rows were removed under the frozen quarantine scenario with zero replacements. Quarantine-period metrics are published and baseline anchors passed. The 11 relationship blockers are in lower intervals and have no direct overlap with this comparator.",
          "limit":"This candidate-specific interpretation is not global G0 PASS or production authorization. TRAIN net return changes materially under the full manifest quarantine scenario. G3 remains partial; the original CP-0026 builder remains fail-closed; the frozen rulebook Section 3 already labels this comparator FAIL / NOT PROMOTED.",
          "no_promotion_reason":"G2 remains FAIL / NOT PROMOTED; consumed OOS diagnostic stays negative and cannot be relabelled as pristine OOS."
        }
        summary={
          "schema_version":1,"checkpoint":"CP-0040","task":"cp0040_rulebook_bound_eligibility_decision",
          "status":overall,"started_at_utc":started,"finished_at_utc":now(),
          "rulebook":{"path":a.rulebook,"bytes":len(rule_bytes),"sha256":rule_sha,"receipt_path":a.rulebook_receipt,
            "source_pack_sha256s":[cp41.get("sha256"),cp46.get("sha256")]},
          "input_evidence_hashes":{"manifest_sha256":manifest_sha,"blockers_sha256":block_sha,"sensitivity_summary_sha256":sens_sha,
            "shared52_status":dp.get("status"),"candidate_relevance_status":rp.get("status"),"builder_sha256":builder_sha},
          "input_impact":{"candidate_intervals":{
            "4h":{"baseline_rows":int(impact_by["4h"]["baseline_rows"]),"removed":int(impact_by["4h"]["removed_exact_key_rows"]),"remaining":int(impact_by["4h"]["quarantine_rows_after_filter"])},
            "1d":{"baseline_rows":int(impact_by["1d"]["baseline_rows"]),"removed":int(impact_by["1d"]["removed_exact_key_rows"]),"remaining":int(impact_by["1d"]["quarantine_rows_after_filter"])},
            "1mo":{"baseline_rows":int(impact_by["1mo"]["baseline_rows"]),"removed":int(impact_by["1mo"]["removed_exact_key_rows"]),"remaining":int(impact_by["1mo"]["quarantine_rows_after_filter"])}},
            "direct_key_rows":len(direct_rows),"direct_key_rows_removed":sum(app_by.get((r.get("interval",""),r.get("open_time_ms","")),{}).get("baseline_row_removed")=="True" for r in direct_rows),
            "replacement_rows":sum(app_by.get((r.get("interval",""),r.get("open_time_ms","")),{}).get("replacement_row_added")=="True" for r in direct_rows)},
          "sensitivity":{"TRAIN_delta_net_return_percentage_points":train_delta,"DEVELOPMENT_CHECK_delta_net_return_percentage_points":dev_delta,
            "CONSUMED_OOS_DIAGNOSTIC_delta_net_return_percentage_points":oos_delta,"baseline_anchors_match":perf_ok},
          "open_relationships":{"count":len(blocker_rows),"candidate_direct_overlap":0,"all_remain_open":True,"root_cause":"OPEN_NOT_ESTABLISHED"},
          "decision":decision,"checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
          "network_used":False,"archive_downloads":0,"source_bytes_modified":False,"production_candidate_build":False,
          "backtest_rerun":False,"canonical_source_selected":False,"strategy_promoted":False,
          "live_signing_broadcast_orders":"BLOCKED","g0_global":"BLOCKED_GLOBAL","g2":"FAIL_NOT_PROMOTED","g3":"BLOCKED_PARTIAL"}
        write_json(out/"CP0040_Rulebook_Bound_Eligibility_Decision_Summary.json",summary)
        write_csv(out/"CP0040_Rulebook_Eligibility_Check_Register.csv",checks)
        gate_rows=[
          {"gate":"G0 candidate-specific quarantine criterion","status":candidate_g0,"evidence":"9/9 direct 4h/1d manifest keys removed under exact-key quarantine; zero replacements; frozen baseline anchors and quarantine metrics verified."},
          {"gate":"G0 global / CP-0026 production builder","status":global_g0,"evidence":"11 non-row relationship blockers remain open; production builder explicitly fails closed."},
          {"gate":"G2 historical strategy screen","status":"FAIL_NOT_PROMOTED","evidence":"Frozen rulebook Section 3 says MTF_BREAKOUT_4H_D1 FAIL / NOT PROMOTED."},
          {"gate":"G3 source-policy stability","status":g3,"evidence":"Full-manifest quarantine changes TRAIN net return by "+str(round(train_delta,6))+" percentage points."},
          {"gate":"Source authority","status":"NONE","evidence":"All direct unresolved rows remain open; no canonical source selected."},
          {"gate":"Live / exchange actions","status":"BLOCKED","evidence":"No live signing, broadcast or exchange orders."}
        ]
        write_csv(out/"CP0040_Rulebook_Gate_Decision_Table.csv",gate_rows)
        report=[
          "# CP-0040 Rulebook-bound eligibility decision","",
          "Status: "+overall,"",
          "## Original frozen rulebook verification",
          "- Exact frozen rulebook member verified from two separately packaged source packs: 10,630 bytes; SHA-256 "+RULEBOOK_SHA+".",
          "- Runner recomputed the repository copy hash before this decision.","",
          "## G0: candidate-specific vs global",
          "- The frozen G0 clause permits candidate-specific PASS when unresolved candidate input rows are explicitly quarantined and final metrics are computed under that quarantine policy.",
          "- For MTF_BREAKOUT_4H_D1, the direct 4h/1d input rows have 9 exact-key manifest entries (4h=6, 1d=3). All 9 were removed with no replacements; baseline anchors passed and quarantine metrics are available.",
          "- The 11 relationship blockers are in lower intervals and have no direct interval overlap with this comparator.",
          "- Candidate-specific diagnostic assessment: "+candidate_g0+". This is not global G0 PASS or production-builder authorization.","",
          "## Gates that remain closed",
          "- Global G0: "+global_g0+". The 11 non-row relationship blockers remain open and CP-0026 builder remains fail-closed.",
          "- G3: "+g3+". The full-manifest quarantine scenario changes TRAIN net return by "+str(round(train_delta,6))+" percentage points; source-policy stability/adoption is not cleared.",
          "- G2 remains FAIL / NOT PROMOTED per frozen rulebook Section 3. The consumed OOS diagnostic remains negative and cannot be relabelled pristine OOS.",
          "- Canonical source NONE; cases closed=0; live signing, public broadcast and exchange orders BLOCKED.","",
          "## Next action",
          "- Do not weaken the builder gate or repeat completed archive-provenance checks. Continue to a rulebook-registered diagnostic review of the candidate's remaining G2/G3 research debt; keep all source cases open until independent source authority is established."
        ]
        (out/"CP0040_Rulebook_Bound_Eligibility_Decision_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
        print(json.dumps({"status":overall,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
            "candidate_specific_g0":candidate_g0,"global_g0":global_g0,"g2":"FAIL_NOT_PROMOTED","g3":g3,
            "direct_keys_removed":summary["input_impact"]["direct_key_rows_removed"],"direct_keys_total":len(direct_rows),
            "TRAIN_delta_pp":train_delta,"production_candidate_build":False,"backtest_rerun":False},
            ensure_ascii=False,sort_keys=True))
        return 0
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0040","task":"cp0040_rulebook_bound_eligibility_decision",
          "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),
          "error_type":type(exc).__name__,"error":str(exc),"checks":checks,"network_used":False,"archive_downloads":0,
          "source_bytes_modified":False,"production_candidate_build":False,"backtest_rerun":False,
          "canonical_source_selected":False,"strategy_promoted":False,"source_cases_closed":0,
          "unresolved_nonrow_aggregation_blockers":11,"g0_global":"BLOCKED_GLOBAL","live_signing_broadcast_orders":"BLOCKED"}
        write_json(out/"CP0040_Rulebook_Bound_Eligibility_Decision_Summary.json",summary)
        (out/"CP0040_Rulebook_Bound_Eligibility_Decision_Report_HI.md").write_text(
          "# CP-0040 Rulebook-bound eligibility decision\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\n"+type(exc).__name__+": "+str(exc)+"\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1
if __name__=="__main__": raise SystemExit(main())
