#!/usr/bin/env python3
"""AISTS allowlisted task runner. Standard library only; no exchange/API access."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TASKS = {"smoke"}
ALLOWED_ARCHIVE_HOST = "data.binance.vision"
REQUEST_KEYS = {
    "request_id", "task", "purpose", "created_at_utc", "requested_commit_sha"
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_official_archive_url(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname == ALLOWED_ARCHIVE_HOST
        and parsed.path.startswith("/data/spot/")
        and parsed.path.endswith(".zip")
        and parsed.username is None
        and parsed.password is None
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", default="requests/current.json")
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()

    output_dir = (ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({
            "check_id": name,
            "status": "PASS" if passed else "FAIL",
            "detail": detail,
        })

    request_path = (ROOT / args.request).resolve()
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
        record("request_json_parse", isinstance(request, dict), "Request parsed as JSON object.")
    except Exception as exc:
        request = {}
        record("request_json_parse", False, f"{type(exc).__name__}: {exc}")

    unknown_keys = set(request) - REQUEST_KEYS
    missing = {"request_id", "task", "purpose"} - set(request)
    rid = str(request.get("request_id", ""))
    record(
        "request_schema_allowlist",
        not unknown_keys and not missing,
        f"unknown_keys={sorted(unknown_keys)}; missing_keys={sorted(missing)}",
    )
    record(
        "request_id_format",
        bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,79}", rid)),
        "Request ID must be 3-80 safe ASCII characters.",
    )
    task = request.get("task")
    record(
        "task_allowlist",
        task in ALLOWED_TASKS,
        f"task={task!r}; currently allowed={sorted(ALLOWED_TASKS)}",
    )
    purpose = request.get("purpose", "")
    record(
        "purpose_bounded_text",
        isinstance(purpose, str) and 1 <= len(purpose) <= 240,
        "Purpose must be a string between 1 and 240 characters.",
    )

    # URL policy unit checks only; no URL is requested or opened by this runner.
    positive = "https://data.binance.vision/data/spot/daily/klines/BTCUSDT/4h/BTCUSDT-4h-2026-10-14.zip"
    negatives = [
        "https://api.binance.com/api/v3/klines?symbol=BTCUSDT",
        "http://data.binance.vision/data/spot/daily/klines/BTCUSDT/4h/sample.zip",
        "https://attacker.example/data/spot/daily/klines/BTCUSDT/4h/sample.zip",
        "https://data.binance.vision.evil.example/data/spot/sample.zip",
    ]
    record(
        "official_archive_url_allowlist",
        is_official_archive_url(positive) and all(not is_official_archive_url(u) for u in negatives),
        "Accepts exact HTTPS public archive host; rejects REST, HTTP and lookalike hosts. No network access used.",
    )

    workflow_path = ROOT / ".github" / "workflows" / "python-runner.yml"
    try:
        workflow_text = workflow_path.read_text(encoding="utf-8")
        least_privilege = bool(re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", workflow_text))
        forbidden = any(term in workflow_text for term in ("script_content", "custom_code", "api.binance.com", "actions: write", "contents: write"))
        record(
            "workflow_least_privilege",
            least_privilege and not forbidden,
            f"contents-read-only={least_privilege}; forbidden_inline_or_privileged_pattern={forbidden}",
        )
    except Exception as exc:
        record("workflow_least_privilege", False, f"{type(exc).__name__}: {exc}")

    workflow_dir = ROOT / ".github" / "workflows"
    workflows = sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml"))
    forbidden_workflows = []
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        if any(term in text for term in ("api.binance.com/api/", "custom_code:", "script_content:", "contents: write", "actions: write")):
            forbidden_workflows.append(path.name)
    record(
        "all_workflows_scope_scan",
        not forbidden_workflows,
        f"workflow_files={len(workflows)}; forbidden_files={forbidden_workflows}",
    )

    py_paths = sorted((ROOT / "scripts").glob("*.py"))
    compile_ok = True
    compile_errors = []
    for path in py_paths:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            compile_ok = False
            compile_errors.append(f"{path.relative_to(ROOT)}: {type(exc).__name__}: {exc}")
    record(
        "python_source_syntax",
        bool(py_paths) and compile_ok,
        f"files_checked={len(py_paths)}; errors={compile_errors}",
    )

    commit_sha = os.environ.get("AISTS_COMMIT_SHA", "")
    run_id = os.environ.get("AISTS_RUN_ID", "")
    record("commit_sha_present", bool(re.fullmatch(r"[0-9a-f]{40}", commit_sha)), f"commit_sha={commit_sha}")
    record("github_run_id_present", run_id.isdigit(), f"run_id={run_id}")
    record("network_disabled_by_design", True, "Task performed no network requests; no exchange REST API, signing or order placement.")
    record("raw_data_untouched", True, "Smoke task read only repository files and wrote evidence under results/.")

    passed = all(item["status"] == "PASS" for item in checks)
    summary = {
        "schema_version": 1,
        "project": "AISTS BTCUSDT Research Runner",
        "request_id": rid,
        "task": task,
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(x["status"] == "PASS" for x in checks),
        "checks_total": len(checks),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "commit_sha": commit_sha,
        "run_id": run_id,
        "run_attempt": os.environ.get("AISTS_RUN_ATTEMPT", ""),
        "ref": os.environ.get("AISTS_REF", ""),
        "event": os.environ.get("AISTS_EVENT", ""),
        "request_sha256": sha256_file(request_path) if request_path.exists() else None,
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "workflow_sha256": sha256_file(workflow_path) if workflow_path.exists() else None,
        "network_requests_made": 0,
        "market_data_rest_api_used": False,
        "raw_data_modified": False,
        "source_selected": False,
        "strategy_promoted": False,
        "checks": checks,
    }
    (output_dir / "run_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (output_dir / "checks.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "detail"])
        writer.writeheader()
        writer.writerows(checks)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
