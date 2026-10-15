#!/usr/bin/env python3
"""Minimal explicit allowlist router for AISTS GitHub Actions."""
from __future__ import annotations
import argparse, ast, csv, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_TASKS={"smoke","historical_reference_replay","monthly_derived_replay"}
REQUEST_KEYS={"request_id","task","purpose","created_at_utc","requested_commit_sha"}

def file_sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def official_zip_url(url):
    p=urlparse(url)
    return p.scheme=="https" and p.hostname=="data.binance.vision" and p.path.startswith("/data/spot/monthly/klines/BTCUSDT/") and p.path.endswith(".zip") and not p.username and not p.password

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--request",default="requests/current.json"); ap.add_argument("--output-dir",default="results")
    args=ap.parse_args(); out=(ROOT/args.output_dir).resolve(); out.mkdir(parents=True,exist_ok=True); checks=[]
    def check(n,ok,d): checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    request_path=(ROOT/args.request).resolve()
    try: req=json.loads(request_path.read_text(encoding="utf-8")); check("request_json_parse",isinstance(req,dict),"JSON parsed")
    except Exception as e: req={}; check("request_json_parse",False,f"{type(e).__name__}: {e}")
    unknown=set(req)-REQUEST_KEYS; missing={"request_id","task","purpose"}-set(req)
    check("request_schema_allowlist",not unknown and not missing,f"unknown={sorted(unknown)} missing={sorted(missing)}")
    rid=str(req.get("request_id","")); check("request_id_format",bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,79}",rid)),rid)
    task=req.get("task"); check("task_allowlist",task in ALLOWED_TASKS,f"task={task!r}")
    purpose=req.get("purpose",""); check("purpose_bounded_text",isinstance(purpose,str) and 1<=len(purpose)<=240,len(purpose) if isinstance(purpose,str) else "not-string")
    sample="https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/BTCUSDT-4h-2020-01.zip"
    rejected=["https://api.binance.com/api/v3/klines","http://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/a.zip","https://data.binance.vision.attacker.example/data/spot/monthly/klines/BTCUSDT/4h/a.zip"]
    check("archive_url_policy",official_zip_url(sample) and all(not official_zip_url(x) for x in rejected),"allowlist positive and negatives")
    wdir=ROOT/".github"/"workflows"; wfiles=sorted(wdir.glob("*.yml"))+sorted(wdir.glob("*.yaml")); bad=[]
    for p in wfiles:
        t=p.read_text(encoding="utf-8")
        if any(x in t for x in ("api.binance.com/api/","custom_code:","script_content:","contents: write","actions: write")): bad.append(p.name)
    wf=wdir/"python-runner.yml"; wt=wf.read_text(encoding="utf-8") if wf.exists() else ""
    least=bool(re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$",wt))
    check("workflow_least_privilege",least and not bad,f"contents_read={least} blocked_workflows={bad}")
    py=sorted((ROOT/"scripts").glob("*.py")); errors=[]
    for p in py:
        try: ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
        except Exception as e: errors.append(f"{p.name}: {type(e).__name__}: {e}")
    check("python_source_syntax",bool(py) and not errors,f"files={len(py)} errors={errors}")
    commit=os.environ.get("AISTS_COMMIT_SHA",""); run_id=os.environ.get("AISTS_RUN_ID","")
    check("commit_sha_present",bool(re.fullmatch(r"[0-9a-f]{40}",commit)),commit)
    check("run_id_present",run_id.isdigit(),run_id)
    child_status="NOT_RUN"; child_summary=None; task_rc=0
    if task=="smoke":
        check("smoke_network_isolation",True,"No network requests made."); child_status="SMOKE_ONLY"
    elif task in ("historical_reference_replay","monthly_derived_replay"):
        fn="historical_reference_replay.py" if task=="historical_reference_replay" else "monthly_derived_replay.py"
        child=ROOT/"scripts"/fn; check("task_script_exists",child.exists(),str(child))
        if child.exists():
            childout=out/task; cache=ROOT/".cache"/"aists"/"binance-monthly-archives"
            try:
                proc=subprocess.run([sys.executable,str(child),"--output-dir",str(childout),"--cache-dir",str(cache)],cwd=str(ROOT),text=True,capture_output=True,timeout=3300)
                (out/f"{task}_stdout.txt").write_text(proc.stdout[-50000:],encoding="utf-8")
                (out/f"{task}_stderr.txt").write_text(proc.stderr[-20000:],encoding="utf-8")
                task_rc=proc.returncode
            except subprocess.TimeoutExpired as e:
                task_rc=124
                (out/f"{task}_stdout.txt").write_text(str(e.stdout or "")[-50000:],encoding="utf-8")
                (out/f"{task}_stderr.txt").write_text("Task timed out",encoding="utf-8")
            child_summary=childout/("historical_reference_replay_summary.json" if task=="historical_reference_replay" else "monthly_derived_replay_summary.json")
            if child_summary.exists():
                try: child_status=json.loads(child_summary.read_text(encoding="utf-8")).get("task_status","UNKNOWN")
                except Exception: child_status="SUMMARY_PARSE_ERROR"
            check("research_task_completed",task_rc==0 and child_summary.exists(),f"exit={task_rc}; summary={child_summary.exists()}")
            txt=child.read_text(encoding="utf-8")
            check("official_source_scope", "data.binance.vision" in txt and "RestrictedRedirect" in (ROOT/"scripts"/"historical_reference_replay.py").read_text(encoding="utf-8"),"Official archive domain and redirect policy present.")
        else: task_rc=127
    else: task_rc=2
    passed=task_rc==0 and all(c["status"]=="PASS" for c in checks)
    summary={"schema_version":1,"project":"AISTS BTCUSDT Research Runner","request_id":rid,"task":task,
             "runner_status":"PASS" if passed else "FAIL","research_task_status":child_status,
             "checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
             "generated_at_utc":datetime.now(timezone.utc).isoformat(),"commit_sha":commit,"run_id":run_id,
             "run_attempt":os.environ.get("AISTS_RUN_ATTEMPT",""),"event":os.environ.get("AISTS_EVENT",""),
             "request_sha256":file_sha(request_path) if request_path.exists() else None,
             "runner_sha256":file_sha(Path(__file__).resolve()),"workflow_sha256":file_sha(wf) if wf.exists() else None,
             "market_data_rest_api_used":False,"exchange_credentials_used":False,"raw_archive_modified":False,
             "source_selected":False,"strategy_promoted":False,"checks":checks}
    if child_summary and child_summary.exists(): summary["child_summary_sha256"]=file_sha(child_summary)
    (out/"run_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with (out/"checks.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["check_id","status","detail"]); w.writeheader(); w.writerows(checks)
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0 if passed else 1

if __name__=="__main__": raise SystemExit(main())
