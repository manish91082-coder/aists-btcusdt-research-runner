#!/usr/bin/env python3
"""AISTS GitHub Actions runner: explicit task allowlist, minimal permissions, compact evidence."""
from __future__ import annotations
import argparse, ast, csv, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_TASKS={"smoke","historical_reference_replay","monthly_derived_replay","legacy_pipeline","source_adjudication_diagnostic","cp0107_feb2018_raw_row_extract","cp0107_feb2018_disposition_overlay","cp0107_dec2020_child_window_audit","cp0107_field_review_hash_audit","cp0107_monthly_checksum_provenance_audit"}
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
        publisher=re.search(r"(?ms)^  publish_cp0107_evidence:\n(.*?)(?=^  [A-Za-z0-9_]+:|\Z)",text)
        publisher_block=publisher.group(1) if publisher else ""
        publisher_scoped=bool(re.search(r"(?m)^    permissions:\s*\n^      contents: write\s*$",publisher_block)
                              and re.search(r"(?m)^    if:.*needs\.run\.outputs\.task",publisher_block)
                              and "cp0107_feb2018_raw_row_extract" in publisher_block
                              and "cp0107_feb2018_disposition_overlay" in publisher_block)
        if writes and not (writes==1 and publisher_scoped):
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
    elif task in ("historical_reference_replay","monthly_derived_replay","legacy_pipeline","source_adjudication_diagnostic","cp0107_feb2018_raw_row_extract","cp0107_feb2018_disposition_overlay","cp0107_dec2020_child_window_audit","cp0107_field_review_hash_audit","cp0107_monthly_checksum_provenance_audit"):
        script_name={"historical_reference_replay":"historical_reference_replay.py",
                     "monthly_derived_replay":"monthly_derived_replay.py",
                     "legacy_pipeline":"aists_legacy_pipeline.py",
                     "source_adjudication_diagnostic":"AISTS_CP0103_Source_Adjudication_Diagnostic.py",
                     "cp0107_feb2018_raw_row_extract":"AISTS_CP0107_Feb2018_Raw_Row_Extract.py",
                     "cp0107_feb2018_disposition_overlay":"AISTS_CP0107_Feb2018_Disposition_Overlay.py","cp0107_dec2020_child_window_audit":"AISTS_CP0107_Dec2020_ChildWindow_Audit.py","cp0107_field_review_hash_audit":"AISTS_CP0107_FieldReview_HashAudit.py","cp0107_monthly_checksum_provenance_audit":"AISTS_CP0107_MonthlyChecksumProvenanceAudit.py"}[task]
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
            else:
                argv=[sys.executable,str(child),"--output-dir",f"results/{task}","--cache-dir",".cache/aists/binance-monthly-archives"]
                timeout=3300
                summary_name="historical_reference_replay_summary.json" if task=="historical_reference_replay" else "monthly_derived_replay_summary.json"
                child_summary_path=output/task/summary_name
            try:
                if task in ("legacy_pipeline","source_adjudication_diagnostic","cp0107_feb2018_raw_row_extract","cp0107_feb2018_disposition_overlay","cp0107_dec2020_child_window_audit","cp0107_field_review_hash_audit","cp0107_monthly_checksum_provenance_audit"):
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
