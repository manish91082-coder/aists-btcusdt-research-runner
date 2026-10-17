"""Fail-closed orchestration entry point for offline AISTS research runs.

The runner never adjudicates provenance. G0 != PASS means input paths are not
opened and no simulation is attempted. Reports are create-only when persisted.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from aists_brain.research_audit_report import (
    build_research_audit_report,
    serialize_research_audit_report,
)
from aists_brain.research_harness import (
    ResearchHarnessError,
    run_manifest_driven_simulation_from_stored_features,
)


class ResearchRunEntryPointError(ValueError):
    """Raised when the runner cannot safely produce or persist a report."""


_REQUIRED_GATES = ("G0", "G2", "G3", "G4", "G6", "G7")


def _hash_report(report: dict[str, Any]) -> None:
    unsigned = dict(report)
    unsigned.pop("report_sha256", None)
    raw = json.dumps(
        unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    report["report_sha256"] = hashlib.sha256(raw).hexdigest()


def _persist_create_only(report_text: str, destination: str | Path) -> str:
    """Atomically publish report bytes without replacing an existing destination."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        fd, temporary = tempfile.mkstemp(prefix=".aists-report-", dir=str(target.parent))
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(report_text)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, target)
        os.unlink(temporary)
        temporary = None
        return hashlib.sha256(target.read_bytes()).hexdigest()
    except FileExistsError as exc:
        raise ResearchRunEntryPointError("report destination already exists; overwrite refused") from exc
    except OSError as exc:
        raise ResearchRunEntryPointError(f"create-only report publication failed: {exc}") from exc
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def run_research_entrypoint(
    *,
    gate_snapshot: Mapping[str, Any],
    run_id: str,
    repository_head_sha: str,
    csv_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    stored_artifact_path: str | Path | None = None,
    expected_interval: str | None = None,
    initial_cash_usdt: float | None = None,
    allocation_fraction: float = 0.25,
    fee_bps_per_side: float = 10.0,
    slippage_bps_per_side: float = 5.0,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run only with explicit gate snapshot and produce a hash-bound audit report.

    Gate states are supplied evidence, not authenticated here. If G0 is not PASS,
    the runner does not inspect data/manifest/artifact paths and emits no input
    hashes or simulation payload. If G0 says PASS, the existing provenance gate
    and stored-artifact harness remain mandatory. Any failure is recorded as a
    blocked entrypoint report, never as a successful simulation.
    """
    if not isinstance(gate_snapshot, Mapping):
        raise ResearchRunEntryPointError("gate_snapshot must be a mapping")
    missing = [name for name in _REQUIRED_GATES if name not in gate_snapshot]
    if missing:
        raise ResearchRunEntryPointError("missing gate states: " + ", ".join(missing))
    if any(not isinstance(gate_snapshot[name], str) or not gate_snapshot[name].strip()
           for name in _REQUIRED_GATES):
        raise ResearchRunEntryPointError("all gate states must be non-empty strings")

    run_result: dict[str, Any] | None = None
    entrypoint: dict[str, Any] = {
        "schema_version": "aists.research_run_entrypoint.v1",
        "status": "BLOCKED_GATE",
        "blocked_reason": "G0_NOT_PASS",
        "input_artifacts_inspected": False,
        "simulation_attempted": False,
        "report_persistence": "NOT_REQUESTED",
    }

    if gate_snapshot["G0"] == "PASS":
        entrypoint.update({
            "status": "BLOCKED_INPUT",
            "blocked_reason": "REQUIRED_INPUT_MISSING_OR_REJECTED",
            "input_artifacts_inspected": True,
        })
        if (csv_path is None or manifest_path is None or stored_artifact_path is None
                or not expected_interval or initial_cash_usdt is None):
            entrypoint["blocked_reason"] = "REQUIRED_INPUT_ARGUMENT_MISSING"
        else:
            entrypoint["simulation_attempted"] = True
            try:
                run_result = run_manifest_driven_simulation_from_stored_features(
                    csv_path, manifest_path, stored_artifact_path,
                    expected_interval=expected_interval,
                    initial_cash_usdt=initial_cash_usdt,
                    allocation_fraction=allocation_fraction,
                    fee_bps_per_side=fee_bps_per_side,
                    slippage_bps_per_side=slippage_bps_per_side,
                )
                entrypoint.update({
                    "status": "SIMULATED_NOT_VALIDATED",
                    "blocked_reason": None,
                })
            except (ResearchHarnessError, OSError, ValueError, TypeError) as exc:
                entrypoint["blocked_reason"] = f"{type(exc).__name__}: {exc}"

    report = build_research_audit_report(
        gate_snapshot=gate_snapshot,
        run_result=run_result,
        run_id=run_id,
        repository_head_sha=repository_head_sha,
    )
    report["entrypoint"] = entrypoint
    _hash_report(report)

    # Serializer revalidates the final report hash. For G0 != PASS, no input
    # paths, input hashes, or simulation details are included in the report.
    serialized = serialize_research_audit_report(report)
    if report_path is not None:
        entrypoint["report_persistence"] = "PERSISTED_CREATE_ONLY"
        # Re-hash after changing the persistence status, then serialize again.
        _hash_report(report)
        serialized = serialize_research_audit_report(report)
        report["report_file_sha256"] = _persist_create_only(serialized, report_path)
    return report
