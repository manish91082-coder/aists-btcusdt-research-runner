"""Independent structural verifier for serialized AISTS research audit reports.

This verifier checks internal consistency and byte/hash bindings only. It cannot
authenticate gate evidence, source archives, the repository, or profitability.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


class ResearchReportVerificationError(ValueError):
    """Raised when an audit report fails structural or integrity verification."""


_REQUIRED_GATES = ("G0", "G2", "G3", "G4", "G6", "G7")
_REQUIRED_CONTROLS = {
    "live_signing": "BLOCKED",
    "public_broadcast": "BLOCKED",
    "exchange_orders": "BLOCKED",
    "automatic_stop_loss": "NOT_IMPLEMENTED_BY_DESIGN",
    "automatic_take_profit": "NOT_IMPLEMENTED_BY_DESIGN",
}


def _canonical_hash(report: Mapping[str, Any]) -> str:
    unsigned = dict(report)
    unsigned.pop("report_sha256", None)
    try:
        encoded = json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ResearchReportVerificationError("report is not finite canonical JSON") from exc
    return hashlib.sha256(encoded).hexdigest()


def verify_research_audit_report(
    report: Mapping[str, Any],
    *,
    expected_repository_head_sha: str | None = None,
    expected_run_id: str | None = None,
) -> dict[str, Any]:
    """Verify report hash, required fields, gate/status consistency and safety controls."""
    if not isinstance(report, Mapping):
        raise ResearchReportVerificationError("report must be a mapping")
    if report.get("schema_version") != "aists.end_to_end_research_audit.v1":
        raise ResearchReportVerificationError("unsupported audit report schema")
    if not isinstance(report.get("report_sha256"), str) or _canonical_hash(report) != report["report_sha256"]:
        raise ResearchReportVerificationError("report SHA-256 mismatch")
    head = report.get("repository_head_sha")
    if not isinstance(head, str) or len(head) != 40 or any(c not in "0123456789abcdef" for c in head.lower()):
        raise ResearchReportVerificationError("invalid repository_head_sha")
    if expected_repository_head_sha is not None and head.lower() != expected_repository_head_sha.lower():
        raise ResearchReportVerificationError("repository head binding mismatch")
    run_id = report.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ResearchReportVerificationError("missing run_id")
    if expected_run_id is not None and run_id != expected_run_id:
        raise ResearchReportVerificationError("run_id binding mismatch")
    if report.get("mode") != "OFFLINE_RESEARCH_ONLY":
        raise ResearchReportVerificationError("report mode must be OFFLINE_RESEARCH_ONLY")

    gates = report.get("gate_snapshot")
    if not isinstance(gates, Mapping) or any(
        not isinstance(gates.get(key), str) or not gates[key].strip()
        for key in _REQUIRED_GATES
    ):
        raise ResearchReportVerificationError("missing or invalid gate snapshot")
    controls = report.get("controls")
    if not isinstance(controls, Mapping) or any(
        controls.get(key) != value for key, value in _REQUIRED_CONTROLS.items()
    ):
        raise ResearchReportVerificationError("safety control status mismatch")

    g0 = gates["G0"]
    status = report.get("status")
    run = report.get("run")
    input_hashes = report.get("input_hashes")
    if g0 != "PASS":
        if status != "BLOCKED_GATE" or run is not None or input_hashes != {}:
            raise ResearchReportVerificationError("blocked G0 report contains run data or wrong status")
    elif status == "SIMULATED_NOT_VALIDATED":
        if not isinstance(run, Mapping) or not isinstance(input_hashes, Mapping):
            raise ResearchReportVerificationError("simulated report missing run or input hashes")
        for key in ("candle_csv_sha256", "data_manifest_sha256", "decision_artifact_sha256"):
            value = input_hashes.get(key)
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value.lower()):
                raise ResearchReportVerificationError("missing or invalid input hash: " + key)
        if not isinstance(run.get("accounting_reconciliation"), Mapping) or run["accounting_reconciliation"].get("status") != "PASS_ACCOUNTING_RECONCILIATION":
            raise ResearchReportVerificationError("accounting reconciliation is not PASS")
        if not isinstance(run.get("paper_ledger_integrity"), Mapping) or run["paper_ledger_integrity"].get("status") != "PASS_HASH_CHAIN":
            raise ResearchReportVerificationError("paper ledger integrity is not PASS")
    elif status == "READY_NO_RUN":
        if run is not None or not isinstance(input_hashes, Mapping) or input_hashes:
            raise ResearchReportVerificationError("READY_NO_RUN report must not contain run/input hashes")
    else:
        raise ResearchReportVerificationError("unrecognized report status/gate combination")

    entrypoint = report.get("entrypoint")
    if entrypoint is not None:
        if not isinstance(entrypoint, Mapping):
            raise ResearchReportVerificationError("entrypoint section must be an object")
        if g0 != "PASS" and (
            entrypoint.get("simulation_attempted") is not False
            or entrypoint.get("input_artifacts_inspected") is not False
            or entrypoint.get("status") != "BLOCKED_GATE"
        ):
            raise ResearchReportVerificationError("entrypoint contradicts blocked-G0 fail-closed policy")
        if entrypoint.get("status") == "SIMULATED_NOT_VALIDATED" and status != "SIMULATED_NOT_VALIDATED":
            raise ResearchReportVerificationError("entrypoint/run status mismatch")

    return {
        "schema_version": "aists.research_audit_verification.v1",
        "status": "PASS_STRUCTURAL_INTEGRITY",
        "report_sha256": report["report_sha256"],
        "run_id": run_id,
        "repository_head_sha": head.lower(),
        "gate_g0": g0,
        "report_status": status,
        "checks": [
            "canonical report hash",
            "repository-head and run-id bindings",
            "gate/status consistency",
            "safety controls",
            "input hash shape and accounting/ledger status when simulated",
        ],
        "limitations": [
            "does not authenticate gate evidence or provenance claims",
            "does not verify source file bytes unless separately supplied and hashed",
            "does not prove strategy validity or profitability",
        ],
    }


def verify_serialized_research_audit_report(
    report_path: str | Path,
    *,
    expected_repository_head_sha: str | None = None,
    expected_run_id: str | None = None,
) -> dict[str, Any]:
    """Read JSON from disk and verify its canonical report hash and structure."""
    path = Path(report_path)
    try:
        raw = path.read_bytes()
        report = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ResearchReportVerificationError(f"cannot read report: {exc}") from exc
    if not isinstance(report, dict):
        raise ResearchReportVerificationError("serialized report must be a JSON object")
    result = verify_research_audit_report(
        report,
        expected_repository_head_sha=expected_repository_head_sha,
        expected_run_id=expected_run_id,
    )
    result["serialized_file_sha256"] = hashlib.sha256(raw).hexdigest()
    return result
