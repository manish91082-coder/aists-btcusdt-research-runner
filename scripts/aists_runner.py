#!/usr/bin/env python3
"""AISTS GitHub Actions runner: explicit task allowlist, minimal permissions, compact evidence."""
from __future__ import annotations
import argparse, ast, csv, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_TASKS={"smoke","cp0040_quarantine_gate_tests","cp0040_quarantine_manifest_build","cp0040_quarantine_manifest_extend_acquisition","cp0040_quarantine_manifest_extend_aggregation","cp0040_candidate_builder_gate_tests","cp0040_quarantine_sensitivity_preflight","cp0040_baseline_reconstruction_audit","cp0040_quarantine_sensitivity_run","cp0040_aggregation_monthly_sidecar_audit","cp0040_archive_integrity_conflict_matrix","cp0040_candidate_input_relevance_audit","cp0107_shared52_candidate_input_dependency_audit","cp0040_rulebook_bound_eligibility_decision","historical_reference_replay","monthly_derived_replay","legacy_pipeline","source_adjudication_diagnostic","cp0107_feb2018_raw_row_extract","cp0107_feb2018_disposition_overlay","cp0107_dec2020_child_window_audit","cp0107_field_review_hash_audit","cp0107_monthly_checksum_provenance_audit","cp0107_cp0041_daily_reference_acquisition_audit","cp0107_cp0041_aggregation_bucket_overlay_audit","cp0107_cp0041_worklist_disposition_patch_audit","cp0107_cp0041_dec2020_residual7_exact_key_audit","cp0107_official_update_package_audit"}
REQUEST_KEYS={"request_id","task","purpose","created_at_utc","requested_commit_sha"}

def file_sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--request",default="requests/current.json")
    ap.add_argument("--output-dir",default="results")
    args=ap.parse_args()
    output=(ROOT/args.output_dir).resolve(); output.mkdir(parents=True,exist_ok=True)
    checks=[]
    def check(name, passed, detail):
        checks.append({"check_id":name,"status":"PASS" if passed else "FAIL","detail":str(detail)})
    request_path=(ROOT/args.request).resolve()
    try:
        request=json.loads(request_path.read_text(encoding="utf-8"))
        check("request_json_parse",isinstance(request,dict),"JSON parsed")
    except Exception as exc:
        request={}; check("request_json_parse",False,f"{type(exc).__name__}: {exc}")
    unknown=set(request)-REQUEST_KEYS
    missing={"request_id","task","purpose"}-set(request)
    check("request_schema_allowlist",not unknown and not missing,f"unknown={sorted(unknown)} missing={sorted(missing)}")
    rid=str(request.get("request_id",""))
    check("request_id_format",bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,79}",rid)),rid)
    task=request.get("task")
    check("task_allowlist",task in ALLOWED_TASKS,f"task={task!r}")
    purpose=request.get("purpose","")
    check("purpose_bounded_text",isinstance(purpose,str) and 1<=len(purpose)<=240,len(purpose) if isinstance(purpose,str) else "not-string")

    wfdir=ROOT/".github"/"workflows"
    wf=wfdir/"python-runner.yml"
    wftext=wf.read_text(encoding="utf-8") if wf.exists() else ""
    forbidden=[]
    scoped_publisher_write=False
    for path in sorted(list(wfdir.glob("*.yml"))+list(wfdir.glob("*.yaml"))):
        text=path.read_text(encoding="utf-8")
        if any(token in text for token in ("custom_code:","script_content:","actions: write","api.binance.com/api/")):
            forbidden.append(path.name)
        writes=text.count("contents: write")
        publisher_blocks=[]
        for publisher_name in ("publish_cp0107_evidence","publish_cp0040_quarantine_manifest","publish_cp0040_baseline_reconstruction_audit","publish_cp0040_quarantine_sensitivity_audit","publish_cp0040_aggregation_monthly_sidecar_audit","publish_cp0040_archive_integrity_conflict_matrix","publish_cp0040_candidate_input_relevance_audit","publish_cp0107_shared52_candidate_input_dependency_audit","publish_cp0040_rulebook_bound_eligibility_decision"):
            publisher=re.search(r"(?ms)^  "+re.escape(publisher_name)+r":\n(.*?)(?=^  [A-Za-z0-9_]+:|\Z)",text)
            publisher_blocks.append((publisher_name,publisher.group(1) if publisher else ""))
        scoped_count=0
        for publisher_name,publisher_block in publisher_blocks:
            if not publisher_block:
                continue
            has_scoped_permissions=bool(re.search(r"(?m)^    permissions:\s*\n^      contents: write\s*$",publisher_block))
            has_task_scope=bool(re.search(r"(?m)^    if:.*needs\.run\.outputs\.task",publisher_block))
            if publisher_name=="publish_cp0107_evidence":
                task_allowlist=("cp0107_feb2018_raw_row_extract" in publisher_block and "cp0107_feb2018_disposition_overlay" in publisher_block)
            elif publisher_name=="publish_cp0040_quarantine_manifest":
                task_allowlist=("cp0040_quarantine_manifest_build" in publisher_block)
            elif publisher_name=="publish_cp0040_baseline_reconstruction_audit":
                task_allowlist=("cp0040_baseline_reconstruction_audit" in publisher_block)
            elif publisher_name=="publish_cp0040_quarantine_sensitivity_audit":
                task_allowlist=("cp0040_quarantine_sensitivity_run" in publisher_block)
            elif publisher_name=="publish_cp0040_aggregation_monthly_sidecar_audit":
                task_allowlist=("cp0040_aggregation_monthly_sidecar_audit" in publisher_block)
            elif publisher_name=="publish_cp0040_archive_integrity_conflict_matrix":
                task_allowlist=("cp0040_archive_integrity_conflict_matrix" in publisher_block)
            elif publisher_name=="publish_cp0040_candidate_input_relevance_audit":
                task_allowlist=("cp0040_candidate_input_relevance_audit" in publisher_block)
            elif publisher_name=="publish_cp0107_shared52_candidate_input_dependency_audit":
                task_allowlist=("cp0107_shared52_candidate_input_dependency_audit" in publisher_block)
            else:
                task_allowlist=("cp0040_rulebook_bound_eligibility_decision" in publisher_block)
            if has_scoped_permissions and has_task_scope and task_allowlist:
                scoped_count += 1
        publisher_scoped=(scoped_count==9)
        if writes and not (writes==scoped_count and scoped_count in (1,2,3,4,5,6,7,8,9)):
            forbidden.append(path.name+": unscoped contents: write")
        if publisher_scoped:
            scoped_publisher_write=True
    least_privilege=bool(re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$",wftext))
    check("workflow_least_privilege",least_privilege and not forbidden,
          f"top_level_contents_read={least_privilege}; scoped_cp0107_publisher_write={scoped_publisher_write}; forbidden={forbidden}")
    pyfiles=sorted((ROOT/"scripts").glob("*.py"))
    syntax_errors=[]
    for path in pyfiles:
        try: ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
        except Exception as exc: syntax_errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
    check("all_python_sources_parse",bool(pyfiles) and not syntax_errors,f"files={len(pyfiles)} errors={syntax_errors}")
    commit=os.environ.get("AISTS_COMMIT_SHA",""); run_id=os.environ.get("AISTS_RUN_ID","")
    check("commit_sha_present",bool(re.fullmatch(r"[0-9a-f]{40}",commit)),commit)
    check("actions_run_id_present",run_id.isdigit(),run_id)

    child_status="NOT_RUN"; child_summary_path=None; child_rc=0
    if task=="smoke":
        check("smoke_no_network",True,"No HTTP requests; standard library only.")
        child_status="SMOKE_ONLY"
    elif task=="cp0040_candidate_builder_gate_tests":
        child=ROOT/"scripts"/"AISTS_CP0026_Research_Candidate_Builder.py"
        check("task_script_exists",child.exists(),str(child))
        pointer=ROOT/"evidence/source_adjudication/CP0040_Current_Manifest.json"
        if pointer.is_file():
            current=json.loads(pointer.read_text(encoding="utf-8"))
            manifest=ROOT/current["manifest_path"]
            blockers=ROOT/current["blockers_path"]
            gate_summary=ROOT/current["summary_path"]
        else:
            manifest=ROOT/"evidence/source_adjudication/CP0040_Run_38882377148/CP0040_ExactKey_Quarantine_Manifest.csv"
            blockers=ROOT/"evidence/source_adjudication/CP0040_Run_38882377148/CP0040_NonRow_Blockers.csv"
            gate_summary=ROOT/"evidence/source_adjudication/CP0040_Run_38882377148/CP0040_ExactKey_Quarantine_Manifest_Summary.json"
        child_summary_path=output/"cp0040_candidate_builder_gate"/"CP0040_Candidate_Builder_Gate_Summary.json"
        argv=[sys.executable,str(child),"--gate-self-test","--manifest",str(manifest),
              "--blockers",str(blockers),"--gate-summary",str(gate_summary),
              "--gate-test-output",str(child_summary_path)]
        try:
            proc=subprocess.run(argv,cwd=str(ROOT),text=True,capture_output=True,timeout=120)
            (output/"cp0040_candidate_builder_gate_stdout.txt").write_text(proc.stdout[-60000:],encoding="utf-8")
            (output/"cp0040_candidate_builder_gate_stderr.txt").write_text(proc.stderr[-30000:],encoding="utf-8")
            child_rc=proc.returncode
        except subprocess.TimeoutExpired as exc:
            child_rc=124
            (output/"cp0040_candidate_builder_gate_stderr.txt").write_text(f"Candidate-builder gate test timeout: {exc}",encoding="utf-8")
        if child_summary_path.exists():
            try: child_status=json.loads(child_summary_path.read_text(encoding="utf-8")).get("status","UNKNOWN")
            except Exception: child_status="SUMMARY_PARSE_ERROR"
        check("task_exit_and_summary",child_rc==0 and child_summary_path.exists(),
              f"exit={child_rc}; summary_exists={child_summary_path.exists()}")
    elif task=="cp0040_quarantine_manifest_extend_aggregation":
        child=ROOT/"scripts"/"AISTS_CP0040_Quarantine_Manifest_Aggregation_Extension.py"
        check("task_script_exists",child.exists(),str(child))
        child_summary_path=output/"cp0040_quarantine_manifest"/"CP0040_ExactKey_Quarantine_Manifest_Summary.json"
        argv=[sys.executable,str(child),"--output-dir",str(output/"cp0040_quarantine_manifest")]
        try:
            proc=subprocess.run(argv,cwd=str(ROOT),text=True,capture_output=True,timeout=180)
            (output/"cp0040_quarantine_manifest_aggregation_stdout.txt").write_text(proc.stdout[-60000:],encoding="utf-8")
            (output/"cp0040_quarantine_manifest_aggregation_stderr.txt").write_text(proc.stderr[-30000:],encoding="utf-8")
            child_rc=proc.returncode
        except subprocess.TimeoutExpired as exc:
            child_rc=124
            (output/"cp0040_quarantine_manifest_aggregation_stderr.txt").write_text(f"Aggregation manifest extension timeout: {exc}",encoding="utf-8")
        if child_summary_path.exists():
            try: child_status=json.loads(child_summary_path.read_text(encoding="utf-8")).get("status","UNKNOWN")
            except Exception: child_status="SUMMARY_PARSE_ERROR"
        check("task_exit_and_summary",child_rc==0 and child_summary_path.exists(),
              f"exit={child_rc}; summary_exists={child_summary_path.exists()}")
    elif task=="cp0040_quarantine_manifest_extend_acquisition":
        child=ROOT/"scripts"/"AISTS_CP0040_Quarantine_Manifest_Acquisition_Extension.py"
        check("task_script_exists",child.exists(),str(child))
        child_summary_path=output/"cp0040_quarantine_manifest"/"CP0040_ExactKey_Quarantine_Manifest_Summary.json"
        argv=[sys.executable,str(child),"--output-dir",str(output/"cp0040_quarantine_manifest")]
        try:
            proc=subprocess.run(argv,cwd=str(ROOT),text=True,capture_output=True,timeout=180)
            (output/"cp0040_quarantine_manifest_extension_stdout.txt").write_text(proc.stdout[-60000:],encoding="utf-8")
            (output/"cp0040_quarantine_manifest_extension_stderr.txt").write_text(proc.stderr[-30000:],encoding="utf-8")
            child_rc=proc.returncode
        except subprocess.TimeoutExpired as exc:
            child_rc=124
            (output/"cp0040_quarantine_manifest_extension_stderr.txt").write_text(f"Manifest extension timeout: {exc}",encoding="utf-8")
        if child_summary_path.exists():
            try: child_status=json.loads(child_summary_path.read_text(encoding="utf-8")).get("status","UNKNOWN")
            except Exception: child_status="SUMMARY_PARSE_ERROR"
        check("task_exit_and_summary",child_rc==0 and child_summary_path.exists(),
              f"exit={child_rc}; summary_exists={child_summary_path.exists()}")
    elif task=="cp0040_quarantine_manifest_build":
        child=ROOT/"scripts"/"AISTS_CP0040_Quarantine_Manifest_Builder.py"
        check("task_script_exists",child.exists(),str(child))
        child_summary_path=output/"cp0040_quarantine_manifest"/"CP0040_ExactKey_Quarantine_Manifest_Summary.json"
        argv=[sys.executable,str(child),"--output-dir",str(output/"cp0040_quarantine_manifest")]
        try:
            proc=subprocess.run(argv,cwd=str(ROOT),text=True,capture_output=True,timeout=120)
            (output/"cp0040_quarantine_manifest_stdout.txt").write_text(proc.stdout[-60000:],encoding="utf-8")
            (output/"cp0040_quarantine_manifest_stderr.txt").write_text(proc.stderr[-30000:],encoding="utf-8")
            child_rc=proc.returncode
        except subprocess.TimeoutExpired as exc:
            child_rc=124
            (output/"cp0040_quarantine_manifest_stderr.txt").write_text(f"Manifest build timeout: {exc}",encoding="utf-8")
        if child_summary_path.exists():
            try: child_status=json.loads(child_summary_path.read_text(encoding="utf-8")).get("status","UNKNOWN")
            except Exception: child_status="SUMMARY_PARSE_ERROR"
        check("task_exit_and_summary",child_rc==0 and child_summary_path.exists(),
              f"exit={child_rc}; summary_exists={child_summary_path.exists()}")
    elif task=="cp0040_quarantine_gate_tests":
        child=ROOT/"scripts"/"AISTS_CP0040_Quarantine_Gate.py"
        check("task_script_exists",child.exists(),str(child))
        child_summary_path=output/"cp0040_quarantine_gate"/"CP0040_Quarantine_Gate_Summary.json"
        argv=[sys.executable,str(child),"--self-test","--output",str(child_summary_path)]
        try:
            proc=subprocess.run(argv,cwd=str(ROOT),text=True,capture_output=True,timeout=120)
            (output/"cp0040_quarantine_gate_stdout.txt").write_text(proc.stdout[-60000:],encoding="utf-8")
            (output/"cp0040_quarantine_gate_stderr.txt").write_text(proc.stderr[-30000:],encoding="utf-8")
            child_rc=proc.returncode
        except subprocess.TimeoutExpired as exc:
            child_rc=124
            (output/"cp0040_quarantine_gate_stderr.txt").write_text(f"Self-test timeout: {exc}",encoding="utf-8")
        if child_summary_path.exists():
            try: child_status=json.loads(child_summary_path.read_text(encoding="utf-8")).get("status","UNKNOWN")
            except Exception: child_status="SUMMARY_PARSE_ERROR"
        check("task_exit_and_summary",child_rc==0 and child_summary_path.exists(),
              f"exit={child_rc}; summary_exists={child_summary_path.exists()}")
    elif task in ("historical_reference_replay","monthly_derived_replay","legacy_pipeline","source_adjudication_diagnostic","cp0040_quarantine_sensitivity_preflight","cp0040_baseline_reconstruction_audit","cp0040_quarantine_sensitivity_run","cp0040_aggregation_monthly_sidecar_audit","cp0040_archive_integrity_conflict_matrix","cp0040_candidate_input_relevance_audit","cp0107_shared52_candidate_input_dependency_audit","cp0040_rulebook_bound_eligibility_decision","cp0107_feb2018_raw_row_extract","cp0107_feb2018_disposition_overlay","cp0107_dec2020_child_window_audit","cp0107_field_review_hash_audit","cp0107_monthly_checksum_provenance_audit","cp0107_cp0041_daily_reference_acquisition_audit","cp0107_cp0041_aggregation_bucket_overlay_audit","cp0107_cp0041_worklist_disposition_patch_audit","cp0107_cp0041_dec2020_residual7_exact_key_audit","cp0107_official_update_package_audit"):
        script_name={"historical_reference_replay":"historical_reference_replay.py",
                     "monthly_derived_replay":"monthly_derived_replay.py",
                     "legacy_pipeline":"aists_legacy_pipeline.py",
                     "source_adjudication_diagnostic":"AISTS_CP0103_Source_Adjudication_Diagnostic.py",
                     "cp0040_quarantine_sensitivity_preflight":"AISTS_CP0040_Quarantine_Sensitivity_Preflight.py",
                     "cp0040_baseline_reconstruction_audit":"AISTS_CP0040_Baseline_Reconstruction_Audit.py",
                     "cp0040_quarantine_sensitivity_run":"AISTS_CP0040_Quarantine_Sensitivity_Audit.py",
                     "cp0040_aggregation_monthly_sidecar_audit":"AISTS_CP0040_Aggregation_Monthly_Sidecar_Audit.py",
                     "cp0040_archive_integrity_conflict_matrix":"AISTS_CP0040_Archive_Integrity_Conflict_Matrix.py",
                     "cp0040_candidate_input_relevance_audit":"AISTS_CP0040_Candidate_Input_Relevance_Audit.py",
                     "cp0107_shared52_candidate_input_dependency_audit":"AISTS_CP0107_Shared52_Candidate_Input_Dependency_Audit.py",
                     "cp0040_rulebook_bound_eligibility_decision":"AISTS_CP0040_Rulebook_Bound_Eligibility_Decision.py",
                     "cp0107_feb2018_raw_row_extract":"AISTS_CP0107_Feb2018_Raw_Row_Extract.py",
                     "cp0107_feb2018_disposition_overlay":"AISTS_CP0107_Feb2018_Disposition_Overlay.py","cp0107_dec2020_child_window_audit":"AISTS_CP0107_Dec2020_ChildWindow_Audit.py","cp0107_field_review_hash_audit":"AISTS_CP0107_FieldReview_HashAudit.py","cp0107_monthly_checksum_provenance_audit":"AISTS_CP0107_MonthlyChecksumProvenanceAudit.py","cp0107_cp0041_daily_reference_acquisition_audit":"AISTS_CP0107_CP0041_DailyReference_Acquisition_Audit.py","cp0107_cp0041_aggregation_bucket_overlay_audit":"AISTS_CP0107_CP0041_AggregationBucket_Overlay_Audit.py","cp0107_cp0041_worklist_disposition_patch_audit":"AISTS_CP0107_CP0041_Worklist_Disposition_Patch_Audit.py","cp0107_cp0041_dec2020_residual7_exact_key_audit":"AISTS_CP0107_CP0041_Dec2020_Residual7_ExactKey_Audit.py","cp0107_official_update_package_audit":"AISTS_CP0107_Official_Update_Package_Audit.py"}[task]
        child=ROOT/"scripts"/script_name
        check("task_script_exists",child.exists(),str(child))
        if child.exists():
            if task=="legacy_pipeline":
                argv=[sys.executable,str(child),"--output-dir","results/legacy_pipeline",
                      "--cache-dir",".cache/aists/binance-monthly-archives",
                      "--data-root",".aists_workspace/market_data/binance_spot/BTCUSDT"]
                timeout=10500
                child_summary_path=output/"legacy_pipeline"/"legacy_pipeline_summary.json"
            elif task=="source_adjudication_diagnostic":
                argv=[sys.executable,str(child),"--monthly-cache",".cache/aists/binance-monthly-archives",
                      "--daily-cache",".cache/aists/binance-daily-references",
                      "--output-dir","results/source_adjudication_diagnostic"]
                timeout=1800
                child_summary_path=output/"source_adjudication_diagnostic"/"CP0103_Run_Summary.json"
            elif task=="cp0040_quarantine_sensitivity_preflight":
                argv=[sys.executable,str(child)]
                timeout=300
                child_summary_path=output/"cp0040_quarantine_sensitivity_preflight"/"CP0040_Quarantine_Sensitivity_Preflight_Summary.json"
            elif task=="cp0040_baseline_reconstruction_audit":
                argv=[sys.executable,str(child),
                      "--monthly-cache",".cache/aists/binance-monthly-archives",
                      "--daily-cache",".cache/aists/binance-daily-references",
                      "--anchors","evidence/source_adjudication/CP0040_Baseline_Reconstruction_Anchors.json",
                      "--flagged-dates","evidence/runs/38725478106_flagged_dates.csv",
                      "--output-dir","results/cp0040_baseline_reconstruction_audit"]
                timeout=1800
                child_summary_path=output/"cp0040_baseline_reconstruction_audit"/"CP0040_Baseline_Reconstruction_Audit_Summary.json"
            elif task=="cp0040_quarantine_sensitivity_run":
                argv=[sys.executable,str(child),
                      "--monthly-cache",".cache/aists/binance-monthly-archives",
                      "--daily-cache",".cache/aists/binance-daily-references",
                      "--anchors","evidence/source_adjudication/CP0040_Baseline_Reconstruction_Anchors.json",
                      "--metric-anchors","evidence/source_adjudication/CP0040_MTF_BREAKOUT_4H_D1_Metric_Anchors.json",
                      "--manifest-pointer","evidence/source_adjudication/CP0040_Current_Manifest.json",
                      "--scope-lock","evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Scope_Lock_HI.md",
                      "--engine-payload","scripts/vendor/CP0031_Engine_R1.py.gz.b64",
                      "--flagged-dates","evidence/runs/38725478106_flagged_dates.csv",
                      "--output-dir","results/cp0040_quarantine_sensitivity_audit"]
                timeout=2700
                child_summary_path=output/"cp0040_quarantine_sensitivity_audit"/"CP0040_Quarantine_Sensitivity_Audit_Summary.json"
            elif task=="cp0040_aggregation_monthly_sidecar_audit":
                argv=[sys.executable,str(child),
                      "--monthly-cache",".cache/aists/binance-monthly-archives",
                      "--manifest-pointer","evidence/source_adjudication/CP0040_Current_Manifest.json",
                      "--bucket-snapshot","evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv",
                      "--bucket-summary","evidence/source_adjudication/CP0107_CP0041_AggregationBucket_Summary.json",
                      "--bucket-comparison","evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Comparison.csv",
                      "--daily-archive-manifest","evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_DailyReference_Archive_Manifest.csv",
                      "--output-dir","results/cp0040_aggregation_monthly_sidecar_audit"]
                timeout=900
                child_summary_path=output/"cp0040_aggregation_monthly_sidecar_audit"/"CP0040_Aggregation_Monthly_Sidecar_Audit_Summary.json"
            elif task=="cp0040_archive_integrity_conflict_matrix":
                argv=[sys.executable,str(child),
                      "--manifest-pointer","evidence/source_adjudication/CP0040_Current_Manifest.json",
                      "--bucket-snapshot","evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv",
                      "--bucket-summary","evidence/source_adjudication/CP0107_CP0041_AggregationBucket_Summary.json",
                      "--bucket-comparison","evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Comparison.csv",
                      "--row-evidence","evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv",
                      "--daily-archive-manifest","evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_DailyReference_Archive_Manifest.csv",
                      "--monthly-sidecar-pointer","evidence/source_adjudication/CP0040_Aggregation_Monthly_Sidecar_Current.json",
                      "--output-dir","results/cp0040_archive_integrity_conflict_matrix"]
                timeout=600
                child_summary_path=output/"cp0040_archive_integrity_conflict_matrix"/"CP0040_Archive_Integrity_Conflict_Matrix_Summary.json"
            elif task=="cp0040_candidate_input_relevance_audit":
                argv=[sys.executable,str(child),
                      "--manifest-pointer","evidence/source_adjudication/CP0040_Current_Manifest.json",
                      "--matrix-pointer","evidence/source_adjudication/CP0040_Archive_Integrity_Matrix_Current.json",
                      "--sensitivity-pointer","evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Current.json",
                      "--builder","scripts/AISTS_CP0026_Research_Candidate_Builder.py",
                      "--engine-payload","scripts/vendor/CP0031_Engine_R1.py.gz.b64",
                      "--output-dir","results/cp0040_candidate_input_relevance_audit"]
                timeout=600
                child_summary_path=output/"cp0040_candidate_input_relevance_audit"/"CP0040_Candidate_Input_Relevance_Audit_Summary.json"
            elif task=="cp0107_shared52_candidate_input_dependency_audit":
                argv=[sys.executable,str(child),
                      "--raw-crosswalk","evidence/source_adjudication/CP0107_Shared52_RowValue_VersionCrosswalk.csv",
                      "--official-crosswalk","evidence/source_adjudication/CP0107_Official_Update_Package_Shared52_DailyCrosswalk.csv",
                      "--matrix","evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Matrix.csv",
                      "--official-package-summary","evidence/source_adjudication/CP0107_Official_Update_Package_Summary.json",
                      "--manifest-pointer","evidence/source_adjudication/CP0040_Current_Manifest.json",
                      "--sensitivity-pointer","evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Current.json",
                      "--output-dir","results/cp0107_shared52_candidate_input_dependency_audit"]
                timeout=600
                child_summary_path=output/"cp0107_shared52_candidate_input_dependency_audit"/"CP0107_Shared52_Candidate_Input_Dependency_Summary.json"
            elif task=="cp0040_rulebook_bound_eligibility_decision":
                argv=[sys.executable,str(child),
                      "--rulebook","evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md",
                      "--rulebook-receipt","evidence/source_adjudication/CP0040_Original_Rulebook_Verification_Receipt.json",
                      "--manifest-pointer","evidence/source_adjudication/CP0040_Current_Manifest.json",
                      "--sensitivity-pointer","evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Current.json",
                      "--dependency-pointer","evidence/source_adjudication/CP0107_Shared52_Candidate_Input_Dependency_Current.json",
                      "--relevance-pointer","evidence/source_adjudication/CP0040_Candidate_Input_Relevance_Current.json",
                      "--matrix-pointer","evidence/source_adjudication/CP0040_Archive_Integrity_Matrix_Current.json",
                      "--builder","scripts/AISTS_CP0026_Research_Candidate_Builder.py",
                      "--output-dir","results/cp0040_rulebook_bound_eligibility_decision"]
                timeout=600
                child_summary_path=output/"cp0040_rulebook_bound_eligibility_decision"/"CP0040_Rulebook_Bound_Eligibility_Decision_Summary.json"
            elif task=="cp0107_feb2018_raw_row_extract":
                argv=[sys.executable,str(child),"--monthly-cache",".cache/aists/binance-monthly-archives",
                      "--daily-cache",".cache/aists/binance-daily-references",
                      "--manifest","evidence/source_adjudication/CP0107_SourceArchive_Manifest_66.csv",
                      "--segment-inventory","evidence/source_adjudication/CP0106_Run_38730420808_Feb2018_OffGrid_Segments.csv",
                      "--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_Feb2018_Extraction_Summary.json"
            elif task=="cp0107_feb2018_disposition_overlay":
                argv=[sys.executable,str(child),
                      "--source-dir","evidence/source_adjudication/CP0107_Run_38735418645",
                      "--crosswalk-summary","evidence/source_adjudication/CP0107_CP0041_Crosswalk_Summary.json",
                      "--rulebook-sha256","5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0",
                      "--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_Feb2018_Disposition_Overlay_Summary.json"
            elif task=="cp0107_dec2020_child_window_audit":
                argv=[sys.executable,str(child),"--monthly-cache",".cache/aists/binance-monthly-archives","--daily-cache",".cache/aists/binance-daily-references","--manifest","evidence/source_adjudication/CP0107_SourceArchive_Manifest_66.csv","--rollup-csv","evidence/source_adjudication/CP0107_Dec2020_Rollup_Disposition.csv","--source-dir","evidence/source_adjudication/CP0107_Run_38735418645","--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_Dec2020_ChildWindow_Audit_Summary.json"
            elif task=="cp0107_field_review_hash_audit":
                argv=[sys.executable,str(child),"--source-dir","evidence/source_adjudication/CP0107_Run_38756665405",
                      "--evidence-dir","evidence/source_adjudication","--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_Dec2020_FieldReview_Summary.json"
            elif task=="cp0107_monthly_checksum_provenance_audit":
                argv=[sys.executable,str(child),"--source-dir","evidence/source_adjudication/CP0107_Run_38771142900",
                      "--manifest","evidence/source_adjudication/CP0107_SourceArchive_Manifest_66.csv",
                      "--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_Monthly_Checksum_Provenance_Summary.json"
            elif task=="cp0107_cp0041_daily_reference_acquisition_audit":
                argv=[sys.executable,str(child),
                      "--source-dir","evidence/source_adjudication/CP0107_Run_38771593935",
                      "--monthly-cache",".cache/aists/binance-monthly-archives",
                      "--reuse-dir","prior_daily_ref/cp0107_feb2018",
                      "--reuse-run-id","38775174019","--reuse-artifact-id","11993600932",
                      "--reuse-artifact-sha256","912267a36aed3f726be1aa08c207076303fca31d2ea5669e5d723825c0e6141b",
                      "--output-dir","results/cp0107_feb2018"]
                timeout=2400
                child_summary_path=output/"cp0107_feb2018"/"CP0107_CP0041_DailyReference_Acquisition_Summary.json"
            elif task=="cp0107_cp0041_aggregation_bucket_overlay_audit":
                argv=[sys.executable,str(child),
                      "--bucket-snapshot","evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv",
                      "--row-comparison","evidence/source_adjudication/CP0107_Run_38775666304/CP0107_CP0041_DailyReference_RawRow_Comparison.csv",
                      "--period-summary","evidence/source_adjudication/CP0107_Run_38775666304/CP0107_CP0041_DailyReference_Period_Summary.csv",
                      "--archive-manifest","evidence/source_adjudication/CP0107_Run_38775666304/CP0107_CP0041_DailyReference_Archive_Manifest.csv",
                      "--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_CP0041_AggregationBucket_Summary.json"
            elif task=="cp0107_cp0041_worklist_disposition_patch_audit":
                argv=[sys.executable,str(child),
                      "--baseline-dir","evidence/source_adjudication/CP0107_Run_38775666304",
                      "--source-overlay","evidence/source_adjudication/CP0107_Run_38742035787/CP0107_Feb2018_Disposition_Overlay.csv",
                      "--crosswalk-summary","evidence/source_adjudication/CP0107_CP0041_Crosswalk_Summary.json",
                      "--source-manifest","evidence/source_adjudication/CP0107_CP0041_Worklist_Source_Manifest.json",
                      "--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_CP0041_Worklist_Disposition_Delta_Summary.json"
            elif task=="cp0107_cp0041_dec2020_residual7_exact_key_audit":
                argv=[sys.executable,str(child),
                      "--snapshot","evidence/source_adjudication/CP0107_CP0041_Dec2020_Residual7_RowSnapshot.csv",
                      "--manifest","evidence/source_adjudication/CP0107_SourceArchive_Manifest_66.csv",
                      "--monthly-cache",".cache/aists/binance-monthly-archives",
                      "--daily-cache",".cache/aists/binance-daily-references",
                      "--baseline-dir","evidence/source_adjudication/CP0107_Run_38775666304",
                      "--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_CP0041_Dec2020_Residual7_Summary.json"
            elif task=="cp0107_official_update_package_audit":
                argv=[sys.executable,str(child),"--repo-root",str(ROOT),"--output-dir","results/cp0107_feb2018"]
                timeout=900
                child_summary_path=output/"cp0107_feb2018"/"CP0107_Official_Update_Package_Summary.json"
            else:
                argv=[sys.executable,str(child),"--output-dir",f"results/{task}","--cache-dir",".cache/aists/binance-monthly-archives"]
                timeout=3300
                summary_name="historical_reference_replay_summary.json" if task=="historical_reference_replay" else "monthly_derived_replay_summary.json"
                child_summary_path=output/task/summary_name
            try:
                if task in ("legacy_pipeline","source_adjudication_diagnostic","cp0107_feb2018_raw_row_extract","cp0107_feb2018_disposition_overlay","cp0107_dec2020_child_window_audit","cp0107_field_review_hash_audit","cp0107_monthly_checksum_provenance_audit","cp0107_cp0041_daily_reference_acquisition_audit","cp0107_cp0041_aggregation_bucket_overlay_audit","cp0107_cp0041_worklist_disposition_patch_audit","cp0107_cp0041_dec2020_residual7_exact_key_audit","cp0107_official_update_package_audit"):
                    log_path=output/f"{task}_stdout.txt"
                    with log_path.open("w",encoding="utf-8") as log:
                        proc=subprocess.Popen(argv,cwd=str(ROOT),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1)
                        assert proc.stdout is not None
                        for line in proc.stdout:
                            print(line,end="",flush=True)
                            log.write(line);log.flush()
                        child_rc=proc.wait()
                    (output/f"{task}_stderr.txt").write_text("",encoding="utf-8")
                else:
                    proc=subprocess.run(argv,cwd=str(ROOT),text=True,capture_output=True,timeout=timeout)
                    (output/f"{task}_stdout.txt").write_text(proc.stdout[-60000:],encoding="utf-8")
                    (output/f"{task}_stderr.txt").write_text(proc.stderr[-30000:],encoding="utf-8")
                    child_rc=proc.returncode
            except subprocess.TimeoutExpired as exc:
                child_rc=124
                (output/f"{task}_stdout.txt").write_text(str(exc.stdout or "")[-60000:],encoding="utf-8")
                (output/f"{task}_stderr.txt").write_text(f"Task timeout after {timeout}s",encoding="utf-8")
            if child_summary_path and child_summary_path.exists():
                try: child_status=json.loads(child_summary_path.read_text(encoding="utf-8")).get("status",
                    json.loads(child_summary_path.read_text(encoding="utf-8")).get("task_status","UNKNOWN"))
                except Exception: child_status="SUMMARY_PARSE_ERROR"
            check("task_exit_and_summary",child_rc==0 and child_summary_path is not None and child_summary_path.exists(),
                  f"exit={child_rc}; summary_exists={bool(child_summary_path and child_summary_path.exists())}")
        else: child_rc=127
    else:
        child_rc=2

    passed=child_rc==0 and all(c["status"]=="PASS" for c in checks)
    summary={
        "schema_version":1,"project":"AISTS BTCUSDT Research Runner","request_id":rid,"task":task,
        "runner_status":"PASS" if passed else "FAIL","research_task_status":child_status,
        "checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),"commit_sha":commit,"run_id":run_id,
        "run_attempt":os.environ.get("AISTS_RUN_ATTEMPT",""),"event":os.environ.get("AISTS_EVENT",""),
        "request_sha256":file_sha(request_path) if request_path.exists() else None,
        "runner_sha256":file_sha(Path(__file__).resolve()),
        "workflow_sha256":file_sha(wf) if wf.exists() else None,
        "market_data_rest_api_used":False,"exchange_credentials_used":False,
        "raw_source_archives_modified":False,"source_selected":False,"strategy_promoted":False,
        "checks":checks,
    }
    if child_summary_path and child_summary_path.exists(): summary["child_summary_sha256"]=file_sha(child_summary_path)
    (output/"run_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    with (output/"checks.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["check_id","status","detail"]);w.writeheader();w.writerows(checks)
    print(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True))
    return 0 if passed else 1

if __name__=="__main__": raise SystemExit(main())
