#!/usr/bin/env python3
"""CP-0040 candidate-input relevance audit.

Read-only. Verifies the frozen CP0031 engine's actual MTF_BREAKOUT_4H_D1
input wiring against the 11 open lower-timeframe aggregation blockers and
the already-published quarantine sensitivity result. This does not change
the production builder gate or grant G0 approval.
"""
from __future__ import annotations
import argparse,base64,csv,gzip,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE_SHA="6b92b0956522ad6e6a7bdcaa364ee677c97b8926e3705d6250866c17cc70ceec"
MANIFEST_SHA="e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a"
BLOCKERS_SHA="f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36"
MATRIX_CSV_SHA="81de607e5b56dc721e076332cfd1fb1ca4c86d720e4de0d3ce900fddb892b7d6"
SENSITIVITY_SUMMARY_SHA="cf774e24112b3cb472853f8de725de0c4eb23f710b9d1b9266d628b9c606f809"
BUILDER_REVIEW_BLOB="3ef0376ff4d8e6f6cfd6550512029e75d99ad75b"

def now(): return datetime.now(timezone.utc).isoformat()
def sha(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha(Path(p).read_bytes())
def git_blob_sha1(b): return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
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
    ap.add_argument("--manifest-pointer",default="evidence/source_adjudication/CP0040_Current_Manifest.json")
    ap.add_argument("--matrix-pointer",default="evidence/source_adjudication/CP0040_Archive_Integrity_Matrix_Current.json")
    ap.add_argument("--sensitivity-pointer",default="evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Current.json")
    ap.add_argument("--builder",default="scripts/AISTS_CP0026_Research_Candidate_Builder.py")
    ap.add_argument("--engine-payload",default="scripts/vendor/CP0031_Engine_R1.py.gz.b64")
    ap.add_argument("--output-dir",default="results/cp0040_candidate_input_relevance_audit")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    checks=[];findings=[]
    def ck(n,ok,d):checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    try:
        mp=read_json(ROOT/a.manifest_pointer);xp=read_json(ROOT/a.matrix_pointer);sp=read_json(ROOT/a.sensitivity_pointer)
        manifest=ROOT/mp["manifest_path"];blockers=ROOT/mp["blockers_path"]
        ms=ROOT/xp["summary_path"];matrix_path=ms.parent/"CP0040_Archive_Integrity_Conflict_Matrix.csv"
        ss=ROOT/sp["summary_path"];perf_path=ss.parent/"CP0040_Quarantine_Performance.csv"
        builder_path=ROOT/a.builder;payload_path=ROOT/a.engine_payload
        required=(manifest,blockers,ms,matrix_path,ss,perf_path,builder_path,payload_path)
        missing=[str(p) for p in required if not p.is_file()]
        ck("all_frozen_inputs_present",not missing,missing or "all present")
        if missing:raise ValueError("Required frozen input missing: "+", ".join(missing))
        man_sha=sha_file(manifest);block_sha=sha_file(blockers);matrix_sha=sha_file(matrix_path);sens_sha=sha_file(ss)
        ck("current_manifest_hash_and_status",man_sha==MANIFEST_SHA and mp.get("status")=="PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN" and mp.get("candidate_eligibility_blocked") is True,f"sha={man_sha}; status={mp.get('status')}")
        ck("current_nonrow_blocker_hash_and_count",block_sha==BLOCKERS_SHA and len(read_csv(blockers))==11,f"sha={block_sha}; rows={len(read_csv(blockers))}")
        ck("matrix_pointer_and_summary_status",xp.get("status")=="PASS_OFFICIAL_ARCHIVE_INTEGRITY_CONFLICT_MATRIX_COMPLETE" and read_json(ms).get("status")==xp.get("status"),xp.get("status"))
        ck("matrix_csv_hash_and_count",matrix_sha==MATRIX_CSV_SHA and len(read_csv(matrix_path))==11,f"sha={matrix_sha}; rows={len(read_csv(matrix_path))}")
        ck("sensitivity_pointer_and_summary_status",sp.get("status")=="PASS_QUARANTINE_SENSITIVITY_DIAGNOSTIC_COMPLETE" and read_json(ss).get("status")==sp.get("status"),sp.get("status"))
        ck("sensitivity_summary_hash_and_baseline_gate",sens_sha==SENSITIVITY_SUMMARY_SHA and read_json(ss).get("baseline_metric_gate")=="PASS",f"sha={sens_sha}; baseline_gate={read_json(ss).get('baseline_metric_gate')}")
        manifest_rows=read_csv(manifest)
        exact_keys=[(r.get("interval","").strip(),r.get("open_time_ms","").strip()) for r in manifest_rows]
        ck("manifest_exact_keys_unique",len(manifest_rows)==1427 and len(set(exact_keys))==1427,f"rows={len(manifest_rows)} unique={len(set(exact_keys))}")
        msumm=read_json(ms);matrix=read_csv(matrix_path);sensitivity=read_json(ss);performance=read_csv(perf_path)
        ck("published_11_bucket_integrity_invariants",msumm.get("source_evidence",{}).get("matrix_buckets_with_both_archive_sets_authenticated")==11 and msumm.get("source_evidence",{}).get("matrix_buckets_with_daily_rollup_match_and_monthly_conflict")==11,msumm.get("source_evidence",{}))
        ck("matrix_dispositions_all_open",len(matrix)==11 and all(r.get("disposition")=="UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT" and r.get("canonical_source_selected")=="False" and r.get("case_closed")=="False" for r in matrix),"all 11 open / canonical source NONE")
        blockers_by_interval=sorted({iv for r in matrix for iv in (r.get("child_interval",""),r.get("parent_interval",""))})
        active_payload=base64.b64decode("".join(payload_path.read_text(encoding="ascii").split()),validate=True)
        engine_bytes=gzip.decompress(active_payload)
        engine_sha=sha(engine_bytes);engine=engine_bytes.decode("utf-8")
        ck("frozen_engine_hash",engine_sha==ENGINE_SHA,f"bytes={len(engine_bytes)} sha256={engine_sha}")
        has_intervals=bool(re.search(r'(?m)^INTERVALS\s*=\s*\["4h",\s*"1d",\s*"1mo"\]\s*$',engine))
        has_higher=bool(re.search(r'(?m)^HIGHER_MAP\s*=\s*\{"4h":\s*"1d",\s*"1d":\s*"1mo"\}\s*$',engine))
        has_strategy=bool(re.search(r'\("4h",\s*"MTF_BREAKOUT_4H_D1"\)',engine))
        has_join=bool(re.search(r'featured\["4h"\]\s*=\s*attach_completed_regime\(add_features\(frames\["4h"\],\s*"4h"\),\s*higher_feat\["1d"\],\s*"1d"\)',engine))
        ck("engine_frozen_interval_map",has_intervals and has_higher,{"has_intervals":has_intervals,"has_higher_map":has_higher})
        ck("engine_4h_d1_strategy_wiring",has_strategy and has_join,{"strategy_tuple":has_strategy,"4h_to_1d_join":has_join})
        direct={"4h","1d"}
        expanded=[]
        for r in matrix:
            ivs={r["child_interval"],r["parent_interval"]}
            direct_overlap=sorted(ivs&direct)
            expanded.append({
                "case_id":r["case_id"],"child_interval":r["child_interval"],"parent_interval":r["parent_interval"],
                "bucket_utc":r["bucket_utc"],"blocker_intervals":",".join(sorted(ivs)),
                "direct_mtf_breakout_4h_d1_interval_overlap":",".join(direct_overlap),
                "direct_interval_overlap":bool(direct_overlap),
                "both_archive_families_authenticated":r.get("both_source_archive_integrity_complete",""),
                "daily_rollup_matches_daily_parent":r.get("daily_rollup_matches_daily_parent",""),
                "monthly_mismatch_signature_reproduced":r.get("monthly_mismatch_signature_reproduced",""),
                "disposition":"UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT",
                "decision":"No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate"
            })
        no_direct=all(not r["direct_interval_overlap"] for r in expanded)
        ck("all_11_blockers_outside_direct_4h_d1_intervals",no_direct,{"blocker_intervals":blockers_by_interval,"direct_strategy_intervals":sorted(direct),"overlapping_cases":sum(r["direct_interval_overlap"] for r in expanded)})
        impacts=sensitivity.get("input_impact",[])
        byiv={r.get("interval"):r for r in impacts}
        impacts_ok=set(byiv)=={"4h","1d","1mo"} and byiv["4h"].get("removed_exact_key_rows")==6 and byiv["1d"].get("removed_exact_key_rows")==3 and byiv["1mo"].get("removed_exact_key_rows")==0 and all(r.get("replacements_added")==0 for r in impacts)
        ck("quarantine_input_impact_counts",impacts_ok,{iv:{"removed":r.get("removed_exact_key_rows"),"rows_after":r.get("quarantine_rows_after_filter")} for iv,r in byiv.items()})
        perf_by={r.get("period"):r for r in performance}
        train_delta=float(perf_by.get("TRAIN",{}).get("delta_net_return_percentage_points","nan"))
        dev_delta=float(perf_by.get("DEVELOPMENT_CHECK",{}).get("delta_net_return_percentage_points","nan"))
        oos_delta=float(perf_by.get("CONSUMED_OOS_DIAGNOSTIC",{}).get("delta_net_return_percentage_points","nan"))
        ck("three_period_quarantine_metrics_present",set(perf_by)=={"TRAIN","DEVELOPMENT_CHECK","CONSUMED_OOS_DIAGNOSTIC"} and all(r.get("baseline_metric_anchors_match")=="True" for r in performance),{"TRAIN_delta_pp":train_delta,"DEVELOPMENT_CHECK_delta_pp":dev_delta,"CONSUMED_OOS_DIAGNOSTIC_delta_pp":oos_delta})
        builder=builder_path.read_text(encoding="utf-8")
        builder_sha=sha_file(builder_path)
        gate_fail_closed=("G0_BLOCKED_NONROW_BLOCKERS_REMAIN" in builder and "if len(blockers) > 0" in builder)
        ck("production_builder_still_fails_closed_on_nonrow_blockers",gate_fail_closed,{"builder_sha256":builder_sha,"gate_guard_present":gate_fail_closed})
        status="PASS_CANDIDATE_INPUT_RELEVANCE_REVIEW_COMPLETE_NOT_G0_APPROVAL" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_INPUT_RELEVANCE_GATE_FAILURE"
        summary={
            "schema_version":1,"checkpoint":"CP-0040","task":"cp0040_candidate_input_relevance_audit",
            "status":status,"started_at_utc":started,"finished_at_utc":now(),
            "scope":"READ_ONLY_FROZEN_ENGINE_INPUT_DEPENDENCY_AND_QUARANTINE_IMPACT_REVIEW",
            "evidence_hashes":{"manifest_sha256":man_sha,"nonrow_blockers_sha256":block_sha,"matrix_csv_sha256":matrix_sha,
                "sensitivity_summary_sha256":sens_sha,"frozen_engine_sha256":engine_sha,"current_builder_sha256":builder_sha},
            "strategy_dependency":{"comparator":"MTF_BREAKOUT_4H_D1","direct_local_interval":"4h","direct_higher_interval":"1d",
                "direct_interval_set":["4h","1d"],"engine_validated_candidate_intervals":["4h","1d","1mo"],
                "engine_source_sha256":engine_sha,"blocker_intervals":blockers_by_interval,
                "residual_blockers_with_direct_4h_d1_interval_overlap":sum(r["direct_interval_overlap"] for r in expanded)},
            "quarantine_impact":{"manifest_rows":len(manifest_rows),"manifest_unique_exact_keys":len(set(exact_keys)),
                "4h_rows_removed":byiv["4h"]["removed_exact_key_rows"],"4h_rows_after":byiv["4h"]["quarantine_rows_after_filter"],
                "1d_rows_removed":byiv["1d"]["removed_exact_key_rows"],"1d_rows_after":byiv["1d"]["quarantine_rows_after_filter"],
                "1mo_rows_removed":byiv["1mo"]["removed_exact_key_rows"],"1mo_rows_after":byiv["1mo"]["quarantine_rows_after_filter"],
                "train_return_delta_percentage_points":train_delta,"development_check_return_delta_percentage_points":dev_delta,
                "consumed_oos_diagnostic_return_delta_percentage_points":oos_delta},
            "relationship_evidence":{"buckets":len(matrix),"both_archive_integrity_authenticated":msumm["source_evidence"]["matrix_buckets_with_both_archive_sets_authenticated"],
                "daily_rollup_matches_monthly_conflict_persists":msumm["source_evidence"]["matrix_buckets_with_daily_rollup_match_and_monthly_conflict"],
                "root_cause":"OPEN_NOT_ESTABLISHED","canonical_source":"NONE"},
            "matrix":expanded,"checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
            "network_used":False,"archive_downloads":0,"source_bytes_modified":False,"production_candidate_build":False,
            "backtest_rerun":False,"canonical_source_selected":False,"canonical_source":"NONE","source_cases_closed":0,
            "unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","strategy_promoted":False,
            "live_signing_broadcast_orders":"BLOCKED",
            "decision":"The 11 relationship blockers are in 5m/15m/30m/1h intervals, not the comparator's direct 4h/1d signal inputs. This is input-relevance evidence only: it does not clear the global CP-0026 gate or select a canonical source. The broader row-level quarantine materially changes TRAIN return, so the overall quarantine-policy decision remains material and unresolved.",
            "next_action":"Stop repeating monthly/daily archive-provenance checks for these 11 buckets. Complete a frozen-rulebook decision on the full exact-key quarantine policy and candidate-specific eligibility; keep the production builder fail-closed until that decision satisfies the existing gate."
        }
        write_json(out/"CP0040_Candidate_Input_Relevance_Audit_Summary.json",summary)
        write_csv(out/"CP0040_Candidate_Input_Relevance_Matrix.csv",expanded)
        report=[
            "# CP-0040 Candidate-input relevance audit: MTF_BREAKOUT_4H_D1","",
            "Status: "+status,
            "",
            "## What is now proven",
            "- Frozen CP-0031 engine hash matches the recorded anchor; MTF_BREAKOUT_4H_D1 uses 4h local bars with completed 1d regime.",
            "- All 11 open aggregation relationships involve only these intervals: "+", ".join(blockers_by_interval)+". None overlaps the comparator's direct 4h/1d interval pair.",
            "- All 11 have both monthly/daily archive integrity authenticated; all 11 daily roll-ups match their daily parents, while the monthly mismatch signature persists.",
            "- The complete 1,427-key quarantine manifest was applied in the previous sensitivity run: 4h removed 6 rows; 1d removed 3; 1mo removed 0; replacements added 0.",
            f"- Net-return delta from frozen baseline under exact-key quarantine: TRAIN {train_delta:.6f} percentage points; DEVELOPMENT_CHECK {dev_delta:.6f}; CONSUMED_OOS_DIAGNOSTIC {oos_delta:.6f}.",
            "",
            "## Decision boundary",
            "- The 11 lower-timeframe relationships have no direct interval overlap with this comparator. That is not a claim that the conflicts are solved, nor that their source authority is known.",
            "- The exact-key sensitivity still materially changes TRAIN results. The current CP-0026 production builder continues to fail closed on any non-row blockers.",
            "- Therefore this review does not grant G0 PASS, does not build a production candidate, and does not promote the comparator.",
            "",
            "## Gates",
            "- All 11 relationship cases remain open; root cause OPEN_NOT_ESTABLISHED; canonical source NONE.",
            "- G0 BLOCKED_GLOBAL; G2 existing strategy screen still applies; live signing, broadcast and exchange orders remain BLOCKED.",
            "- No downloads, network activity, source mutation, candidate build or backtest rerun occurred in this audit.",
            "",
            "## Next bounded action",
            "- Stop repeating archive-provenance checks for the same 11 buckets unless genuinely new evidence arrives.",
            "- Resolve the frozen-rulebook decision for the full row-level quarantine policy and candidate-specific eligibility; preserve the fail-closed production gate until that decision is complete."
        ]
        (out/"CP0040_Candidate_Input_Relevance_Audit_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
        print(json.dumps({"status":status,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
            "blockers_outside_direct_4h_d1_inputs":sum(not r["direct_interval_overlap"] for r in expanded),
            "TRAIN_delta_pp":train_delta,"DEVELOPMENT_CHECK_delta_pp":dev_delta,
            "CONSUMED_OOS_DIAGNOSTIC_delta_pp":oos_delta,"production_candidate_build":False,"g0":"BLOCKED_GLOBAL"},
            ensure_ascii=False,sort_keys=True))
        return 0 if status.startswith("PASS") else 1
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0040","task":"cp0040_candidate_input_relevance_audit",
            "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),
            "error_type":type(exc).__name__,"error":str(exc),"checks":checks,
            "network_used":False,"archive_downloads":0,"source_bytes_modified":False,"production_candidate_build":False,
            "backtest_rerun":False,"canonical_source_selected":False,"source_cases_closed":0,
            "unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","strategy_promoted":False,
            "live_signing_broadcast_orders":"BLOCKED"}
        write_json(out/"CP0040_Candidate_Input_Relevance_Audit_Summary.json",summary)
        (out/"CP0040_Candidate_Input_Relevance_Audit_Report_HI.md").write_text("# CP-0040 Candidate Input Relevance Audit\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\n"+type(exc).__name__+": "+str(exc)+"\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1

if __name__=="__main__": raise SystemExit(main())
