#!/usr/bin/env python3
"""Write a secret-safe, machine-readable execution receipt for GitHub Actions.

The receipt is intentionally limited to public run metadata and explicitly
allowlisted environment fields. It never serializes the full environment.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def build_receipt() -> dict:
    return {
        "schema_version": 1,
        "status": os.environ.get("RECEIPT_STATUS", "UNKNOWN"),
        "started_utc": os.environ.get("RECEIPT_STARTED_UTC", ""),
        "finished_utc": utc_now(),
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
        "workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF", ""),
        "event_name": os.environ.get("GITHUB_EVENT_NAME", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
        "job": os.environ.get("GITHUB_JOB", ""),
        "commit_sha": os.environ.get("GITHUB_SHA", ""),
        "ref": os.environ.get("GITHUB_REF", ""),
        "actor": os.environ.get("GITHUB_ACTOR", ""),
        "runner_os": platform.platform(),
        "python": sys.version.split()[0],
        "inputs": {
            "month": os.environ.get("INPUT_MONTH", ""),
            "start_month": os.environ.get("INPUT_START_MONTH", ""),
            "end_month": os.environ.get("INPUT_END_MONTH", ""),
            "include_funding": os.environ.get("INPUT_INCLUDE_FUNDING", ""),
        },
        "exit_codes": {
            "collector": os.environ.get("COLLECTOR_EXIT_CODE", ""),
            "uploader": os.environ.get("UPLOADER_EXIT_CODE", ""),
        },
        "notes": os.environ.get("RECEIPT_NOTES", ""),
        "secret_values_recorded": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/execution-receipt")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    receipt = build_receipt()
    json_path = out / "execution-receipt.json"
    md_path = out / "execution-receipt.md"
    json_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Execution receipt",
        "",
        f"- Status: **{receipt['status']}**",
        f"- Repository: {receipt['repository'] or 'UNAVAILABLE'}",
        f"- Workflow: {receipt['workflow'] or 'UNAVAILABLE'}",
        f"- Event: {receipt['event_name'] or 'UNAVAILABLE'}",
        f"- Run: {receipt['run_id'] or 'UNAVAILABLE'} (attempt {receipt['run_attempt'] or 'UNAVAILABLE'})",
        f"- Job: {receipt['job'] or 'UNAVAILABLE'}",
        f"- Commit: {receipt['commit_sha'] or 'UNAVAILABLE'}",
        f"- Started UTC: {receipt['started_utc'] or 'UNAVAILABLE'}",
        f"- Finished UTC: {receipt['finished_utc']}",
        f"- Inputs: {json.dumps(receipt['inputs'], sort_keys=True)}",
        f"- Exit codes: {json.dumps(receipt['exit_codes'], sort_keys=True)}",
        f"- Notes: {receipt['notes'] or 'None'}",
        "- Secret values recorded: **no**",
        "",
        "This receipt records run metadata only. Consult the workflow log and source manifest for detailed operation results.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"receipt_json={json_path}")
    print(f"receipt_markdown={md_path}")
    print(f"receipt_status={receipt['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
