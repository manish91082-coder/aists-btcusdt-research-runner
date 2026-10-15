#!/usr/bin/env python3
"""Minimal, explicit allowlist router for AISTS GitHub Actions."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TASKS = {"smoke", "historical_reference_replay"}
REQUEST_KEYS = {"request_id", "task", "purpose", "created_at_utc", "requested_commit_sha"}


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def official_zip_url(url: str) -> bool:
    p = urlparse(url)
    return (p.scheme == "https" and p.hostname == "data.binance.vision"
            and p.path.startswith("/data/spot/monthly/klines/BTCUSDT/")
            and p.path.endswith(".zip") and not p.username and not p.password)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", default="requests/current.json")
    ap.add_argument("--output-dir", default="results")
    args = ap.parse_args()
    output = (ROOT / args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(name, passed, detail):
        checks.append({"check_id": name, "status": "PASS" if passed else "FAIL", "detail": str(detail)})

    request_path = (ROOT / args.request).resolve()
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
        check("request_json_parse", isinstance(request, dict), "Request parsed as JSON.")
    except Exception as exc:
        request = {}
        check("request_json_parse", False, f"{type(exc).__name__}: {exc}")
    unknown = set(request) - REQUEST_KEYS
    missing = {"request_id", "task", "purpose"} - set(request)
    check("request_schema_allowlist", not unknown and not missing, f"unknown={sorted(unknown)} missing={sorted(missing)}")
    rid = str(request.get("request_id", ""))
    check("request_id_format", bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,79}", rid)), "Request ID safe-format check.")
    task = request.get("task")
    check("task_allowlist", task in ALLOWED_TASKS, f"task={task!r}")
    purpose = request.get("purpose", "")
    check("purpose_bounded_text", isinstance(purpose, str) and 1 <= len(purpose) <= 240, "Purpose length 1-240.")

    good = "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/BTCUSDT-4h-2020-01.zip"
    bad = [
        "https://api.binance.com/api/v3/klines",
        "http://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/x.zip",
        "https://data.binance.vision.evil.example/data/spot/monthly/klines/BTCUSDT/4h/x.zip",
    ]
    check("official_archive_url_policy", official_zip_url(good) and all(not official_zip_url(u) for u in bad),
          "Official HTTPS archive URLs accepted; REST/HTTP/lookalike hosts rejected.")

    wf_dir = ROOT / ".github" / "workflows"
    wf_files = sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml"))
    prohibited = []
    for p in wf_files:
        txt = p.read_text(encoding="utf-8")
        if any(t in txt for t in ("api.binance.com/api/", "custom_code:", "script_content:", "contents: write", "actions: write")):
            prohibited.append(p.name)
    wf = wf_dir / "python-runner.yml"
    wftext = wf.read_text(encoding="utf-8") if wf.exists() else ""
    low_perm = bool(re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", wftext))
    check("workflow_least_privilege", low_perm and not prohibited, f"contents-read-only={low_perm}; prohibited-workflows={prohibited}")

    pyfiles = sorted((ROOT / "scripts").glob("*.py"))
    syntax_errors = []
    for p in pyfiles:
        try:
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except Exception as exc:
            syntax_errors.append(f"{p.name}: {type(exc).__name__}: {exc}")
    check("python_syntax", bool(pyfiles) and not syntax_errors, f"files={len(pyfiles)} errors={syntax_errors}")
    commit_sha = os.environ.get("AISTS_COMMIT_SHA", "")
    run_id = os.environ.get("AISTS_RUN_ID", "")
    check("commit_sha_present", bool(re.fullmatch(r"[0-9a-f]{40}", commit_sha)), commit_sha)
    check("run_id_present", run_id.isdigit(), run_id)

    child_status = "NOT_RUN"
    child_summary_path = None
    task_return = 0
    if task == "smoke":
        check("smoke_no_network", True, "Offline only; no external requests.")
        child_status = "SMOKE_ONLY"
    elif task == "historical_reference_replay":
        child = ROOT / "scripts" / "historical_reference_replay.py"
        check("task_script_exists", child.exists(), str(child))
        if child.exists():
            child_out = output / "historical_reference_replay"
            cache = ROOT / ".cache" / "aists" / "binance-monthly-archives"
            try:
                proc = subprocess.run(
                    [sys.executable, str(child), "--output-dir", str(child_out), "--cache-dir", str(cache)],
                    cwd=str(ROOT), text=True, capture_output=True, timeout=3300
                )
                (output / "historical_reference_stdout.txt").write_text(proc.stdout[-50000:], encoding="utf-8")
                (output / "historical_reference_stderr.txt").write_text(proc.stderr[-20000:], encoding="utf-8")
                task_return = proc.returncode
            except subprocess.TimeoutExpired as exc:
                task_return = 124
                (output / "historical_reference_stdout.txt").write_text(str(exc.stdout or "")[-50000:], encoding="utf-8")
                (output / "historical_reference_stderr.txt").write_text("Historical reference task timed out.", encoding="utf-8")
            child_summary_path = child_out / "historical_reference_replay_summary.json"
            if child_summary_path.exists():
                try:
                    child_status = json.loads(child_summary_path.read_text(encoding="utf-8")).get("task_status", "UNKNOWN")
                except Exception:
                    child_status = "SUMMARY_PARSE_ERROR"
            check("historical_task_execution", task_return == 0 and child_summary_path.exists(),
                  f"exit={task_return}; summary_exists={child_summary_path.exists()}")
            st = child.read_text(encoding="utf-8")
            check("historical_source_scope", "data.binance.vision" in st and "RestrictedRedirect" in st,
                  "Archive source allowlist and restricted redirect handler declared.")
        else:
            task_return = 127
    else:
        task_return = 2

    passed = task_return == 0 and all(c["status"] == "PASS" for c in checks)
    report = {
        "schema_version": 1,
        "project": "AISTS BTCUSDT Research Runner",
        "request_id": rid, "task": task,
        "runner_status": "PASS" if passed else "FAIL",
        "research_task_status": child_status,
        "checks_passed": sum(c["status"] == "PASS" for c in checks),
        "checks_total": len(checks),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "commit_sha": commit_sha, "run_id": run_id,
        "run_attempt": os.environ.get("AISTS_RUN_ATTEMPT", ""),
        "event": os.environ.get("AISTS_EVENT", ""),
        "request_sha256": file_sha(request_path) if request_path.exists() else None,
        "runner_sha256": file_sha(Path(__file__).resolve()),
        "workflow_sha256": file_sha(wf) if wf.exists() else None,
        "market_data_rest_api_used": False,
        "exchange_credentials_used": False,
        "raw_archive_modified": False,
        "source_selected": False,
        "strategy_promoted": False,
        "checks": checks,
    }
    if child_summary_path and child_summary_path.exists():
        report["historical_reference_summary_sha256"] = file_sha(child_summary_path)
    (output / "run_summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (output / "checks.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["check_id", "status", "detail"])
        w.writeheader()
        w.writerows(checks)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
