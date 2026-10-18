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
    authentication = report.get("gate_evidence_authentication")
    expected_g0_classification = (
        "SUPPLIED_PASS_CLAIM_NOT_AUTHENTICATED" if gates["G0"] == "PASS"
        else "SUPPLIED_NONPASS_STATE"
    )
    if (
        not isinstance(authentication, Mapping)
        or authentication.get("status") != "NOT_AUTHENTICATED"
        or authentication.get("scope") != "SUPPLIED_GATE_SNAPSHOT"
        or authentication.get("g0_classification") != expected_g0_classification
    ):
        raise ResearchReportVerificationError(
            "gate evidence authentication must remain explicitly NOT_AUTHENTICATED"
        )

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
        simulation = run.get("simulation")
        if not isinstance(simulation, Mapping) or simulation.get("status") != "SIMULATED_NOT_VALIDATED":
            raise ResearchReportVerificationError("simulated report has invalid nested simulation status")
        events = simulation.get("events")
        skipped = simulation.get("skipped_decisions")
        event_count = simulation.get("event_count")
        round_trips = simulation.get("closed_round_trips")
        round_trip_count = simulation.get("closed_round_trip_count")
        if not isinstance(events, list) or isinstance(event_count, bool) or not isinstance(event_count, int) or event_count != len(events):
            raise ResearchReportVerificationError("nested simulation event count mismatch")
        if not isinstance(skipped, list) or report.get("skipped_decisions") != skipped:
            raise ResearchReportVerificationError("skipped decision summary mismatch")
        if any(
            not isinstance(item, Mapping) or item.get("is_order_instruction") is not False
            for item in skipped
        ):
            raise ResearchReportVerificationError(
                "nested simulation contains an actionable skipped decision"
            )
        if not isinstance(round_trips, list) or isinstance(round_trip_count, bool) or not isinstance(round_trip_count, int) or round_trip_count != len(round_trips):
            raise ResearchReportVerificationError("nested simulation round-trip count mismatch")
        if any(not isinstance(event, Mapping) or event.get("is_order_instruction") is not False for event in events):
            raise ResearchReportVerificationError("nested simulation contains an invalid or actionable event")
        accounting = run.get("accounting_reconciliation")
        if not isinstance(accounting, Mapping) or accounting.get("status") != "PASS_ACCOUNTING_RECONCILIATION":
            raise ResearchReportVerificationError("accounting reconciliation is not PASS")
        if accounting.get("event_count") != event_count:
            raise ResearchReportVerificationError("accounting event count does not match nested simulation")
        if not isinstance(run.get("paper_ledger_integrity"), Mapping) or run["paper_ledger_integrity"].get("status") != "PASS_HASH_CHAIN":
            raise ResearchReportVerificationError("paper ledger integrity is not PASS")
    elif status == "BLOCKED_INPUT":
        if run is not None or input_hashes != {}:
            raise ResearchReportVerificationError("BLOCKED_INPUT report must not contain run/input hashes")
        blocked_entrypoint = report.get("entrypoint")
        if not isinstance(blocked_entrypoint, Mapping):
            raise ResearchReportVerificationError("BLOCKED_INPUT report requires an entrypoint section")
        if blocked_entrypoint.get("status") != "BLOCKED_INPUT":
            raise ResearchReportVerificationError("BLOCKED_INPUT report requires matching entrypoint status")
        reason = blocked_entrypoint.get("blocked_reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ResearchReportVerificationError("BLOCKED_INPUT entrypoint requires a blocked reason")
        attempted = blocked_entrypoint.get("simulation_attempted")
        inspected = blocked_entrypoint.get("input_artifacts_inspected")
        if not isinstance(attempted, bool) or not isinstance(inspected, bool):
            raise ResearchReportVerificationError("BLOCKED_INPUT entrypoint inspection flags must be boolean")
        if attempted and not inspected:
            raise ResearchReportVerificationError("simulation attempted without input-artifact inspection")
        if not attempted and (inspected or reason != "REQUIRED_INPUT_ARGUMENT_MISSING"):
            raise ResearchReportVerificationError("missing-argument BLOCKED_INPUT telemetry mismatch")
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
        if status == "SIMULATED_NOT_VALIDATED" and entrypoint.get("status") != "SIMULATED_NOT_VALIDATED":
            raise ResearchReportVerificationError("simulated report requires matching entrypoint status")
        if entrypoint.get("status") == "BLOCKED_INPUT" and status != "BLOCKED_INPUT":
            raise ResearchReportVerificationError("entrypoint/report blocked-input status mismatch")
        if entrypoint.get("simulation_attempted") is True and entrypoint.get("input_artifacts_inspected") is not True:
            raise ResearchReportVerificationError("simulation attempted without input-artifact inspection")

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
