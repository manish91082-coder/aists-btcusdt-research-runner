"""Fail-closed guard for historical execution while trusted G0 receipt verification is absent.

This is an execution-entrypoint policy guard, not an adjudicator. Do not remove
or bypass it based on a caller-supplied PASS string. Re-enable protected tasks
only after a separately trusted G0 receipt verifier is integrated and tested.
"""
from __future__ import annotations


G0_PROTECTED_TASKS = frozenset({
    "historical_reference_replay",
    "monthly_derived_replay",
    "legacy_pipeline",
    "cp0027_baseline_backtest",
    "cp0040_quarantine_sensitivity_run",
    "cp0026_candidate_builder",
})


class G0ExecutionBlocked(RuntimeError):
    """Raised when a historical simulation task lacks authenticated G0 authority."""


def is_g0_protected_task(task: object) -> bool:
    return isinstance(task, str) and task in G0_PROTECTED_TASKS


def require_authenticated_g0(task: str) -> None:
    if is_g0_protected_task(task):
        raise G0ExecutionBlocked(
            "G0_EVIDENCE_NOT_AUTHENTICATED: "
            f"{task} is blocked until a trusted independent G0 receipt verifier exists"
        )
