"""Deterministic end-to-end audit report for offline AISTS research runs.

This module formats evidence and gate states; it does not authenticate them,
generate signals, or promote a strategy. Blocked gates fail closed.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


class AuditReportError(ValueError):
    """Raised when an audit report would be incomplete or misleading."""


_REQUIRED_GATES = ("G0", "G2", "G3", "G4", "G6", "G7")
_FORBIDDEN_LIVE = ("live_signing", "public_broadcast", "exchange_orders")


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                         allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_research_audit_report(
    *,
    gate_snapshot: Mapping[str, Any],
    run_result: Mapping[str, Any] | None = None,
    run_id: str,
    repository_head_sha: str,
) -> dict[str, Any]:
    """Build a hash-addressed report, including a gate-blocked report without a run.

    gate_snapshot must contain current explicit states for G0/G2/G3/G4/G6/G7.
    A G0 state other than PASS forbids embedding a simulated run result. Even when
    G0 is PASS, a harness result remains SIMULATED_NOT_VALIDATED, never accepted
    historical performance. This function does not authenticate gate evidence.
    """
    if not isinstance(gate_snapshot, Mapping):
        raise AuditReportError("gate_snapshot must be an object")
    if not isinstance(run_id, str) or not run_id.strip():
        raise AuditReportError("run_id must be a non-empty string")
    if not isinstance(repository_head_sha, str) or len(repository_head_sha) != 40 or any(
        char not in "0123456789abcdef" for char in repository_head_sha.lower()
    ):
        raise AuditReportError("repository_head_sha must be a 40-character git SHA")
    missing = [gate for gate in _REQUIRED_GATES if gate not in gate_snapshot]
    if missing:
        raise AuditReportError("missing gate states: " + ", ".join(missing))
    if any(not isinstance(gate_snapshot[gate], str) or not gate_snapshot[gate].strip()
           for gate in _REQUIRED_GATES):
        raise AuditReportError("all gate states must be non-empty strings")

    g0 = gate_snapshot["G0"]
    if g0 != "PASS" and run_result is not None:
        raise AuditReportError("G0 is not PASS; a simulation result cannot be attached")
    if run_result is not None:
        if not isinstance(run_result, Mapping):
            raise AuditReportError("run_result must be an object")
        if run_result.get("status") != "SIMULATED_NOT_VALIDATED":
            raise AuditReportError("run_result must remain SIMULATED_NOT_VALIDATED")
        if run_result.get("mode") != "OFFLINE_RESEARCH_ONLY":
            raise AuditReportError("run_result must be OFFLINE_RESEARCH_ONLY")
        for key in ("data_input", "decision_input", "simulation",
                    "accounting_reconciliation", "paper_ledger_integrity"):
            if key not in run_result:
                raise AuditReportError("run_result missing required section: " + key)
        if run_result["accounting_reconciliation"].get("status") != "PASS_ACCOUNTING_RECONCILIATION":
            raise AuditReportError("accounting reconciliation is not PASS")
        if run_result["paper_ledger_integrity"].get("status") != "PASS_HASH_CHAIN":
            raise AuditReportError("paper ledger hash-chain verification is not PASS")

    payload: dict[str, Any] = {
        "schema_version": "aists.end_to_end_research_audit.v1",
        "run_id": run_id,
        "repository_head_sha": repository_head_sha.lower(),
        "mode": "OFFLINE_RESEARCH_ONLY",
        "status": ("BLOCKED_GATE" if g0 != "PASS" else
                   "SIMULATED_NOT_VALIDATED" if run_result is not None else "READY_NO_RUN"),
        "gate_snapshot": {key: gate_snapshot[key] for key in _REQUIRED_GATES},
        "input_hashes": ({
            "candle_csv_sha256": run_result["data_input"].get("csv_sha256"),
            "data_manifest_sha256": run_result["data_input"].get("manifest_sha256"),
            "decision_artifact_sha256": run_result["decision_input"].get("artifact_sha256"),
        } if run_result is not None else {}),
        "run": ({
            "symbol": run_result["data_input"].get("symbol"),
            "market": run_result["data_input"].get("market"),
            "interval": run_result["data_input"].get("interval"),
            "row_count": run_result["data_input"].get("row_count"),
            "brain_version": run_result["decision_input"].get("brain_version"),
            "decision_count": run_result["decision_input"].get("decision_count"),
            "simulation": run_result["simulation"],
            "accounting_reconciliation": run_result["accounting_reconciliation"],
            "paper_ledger_integrity": run_result["paper_ledger_integrity"],
            "limitations": list(run_result.get("limitations", [])),
        } if run_result is not None else None),
        "skipped_decisions": (
            list(run_result["simulation"].get("skipped_decisions", []))
            if run_result is not None else []
        ),
        "controls": {
            "live_signing": "BLOCKED",
            "public_broadcast": "BLOCKED",
            "exchange_orders": "BLOCKED",
            "automatic_stop_loss": "NOT_IMPLEMENTED_BY_DESIGN",
            "automatic_take_profit": "NOT_IMPLEMENTED_BY_DESIGN",
        },
        "interpretation": (
            "G0 is not PASS; no simulation or historical performance claim is permitted."
            if g0 != "PASS" else
            "Offline simulation and accounting consistency only; not strategy acceptance, "
            "not independently authenticated provenance, and not a profitability claim."
            if run_result is not None else
            "G0 claims PASS in the supplied snapshot, but no run result was attached; "
            "this report does not authenticate gate evidence."
        ),
    }
    payload["report_sha256"] = _canonical_sha256(payload)
    return payload


def serialize_research_audit_report(report: Mapping[str, Any]) -> str:
    """Serialize a report deterministically as UTF-8-compatible JSON text."""
    if not isinstance(report, Mapping) or report.get("schema_version") != "aists.end_to_end_research_audit.v1":
        raise AuditReportError("unsupported audit report schema")
    expected = report.get("report_sha256")
    unsigned = dict(report)
    unsigned.pop("report_sha256", None)
    if not isinstance(expected, str) or _canonical_sha256(unsigned) != expected:
        raise AuditReportError("report hash mismatch")
    return json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
