"""Manifest-driven, fail-closed integration harness for offline research simulation.

This is an integration boundary, not an adjudicator or signal generator.
It requires provenance_input's explicit external PASS claim, verifies decision
artifact binding, and runs only the existing offline simulator. No networking,
exchange interaction, data repair, or live orders.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

from aists_brain.accounting_reconciliation import reconcile_simulation_with_ledger
from aists_brain.decision_lineage import DECISION_SCHEMA, DecisionLineageError, validate_causal_decision_artifact
from aists_brain.cost_aware_simulator import simulate_next_open
from aists_brain.paper_portfolio import append_paper_fill, create_ledger, verify_ledger
from aists_brain.provenance_input import (
    ProvenanceGateError,
    load_provenance_cleared_candles,
)

class ResearchHarnessError(ValueError):
    """Raised when inputs are incomplete, unbound, or fail closed."""


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_manifest_driven_simulation(
    csv_path: str | Path,
    manifest_path: str | Path,
    decisions_path: str | Path,
    *,
    expected_interval: str,
    initial_cash_usdt: float,
    allocation_fraction: float = 0.25,
    fee_bps_per_side: float = 10.0,
    slippage_bps_per_side: float = 5.0,
    symbol_filters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run offline simulation only when data, decisions, and exchange filters pass.

    Decision JSON contract:
      schema_version='aists.causal_research_decisions.v1',
      status='PASS', source_csv_sha256=<exact manifest CSV hash>,
      brain_version and strategy_version=<nonempty version identifiers>,
      decisions=[{decision_id, as_of_ms, action, snapshot, snapshot_sha256}, ...].
    Each snapshot contains timestamped, hash-referenced feature observations; the
    lineage validator rejects feature timestamps later than the decision cutoff.
    A PASS is an external assertion, not proof of the decision producer's quality.
    """
    if symbol_filters is None:
        raise ResearchHarnessError("verified symbol_filters are required before simulation")
    if not isinstance(symbol_filters, Mapping):
        raise ResearchHarnessError("symbol_filters must be a mapping")

    try:
        loaded = load_provenance_cleared_candles(
            csv_path, manifest_path, expected_interval=expected_interval
        )
    except (ProvenanceGateError, OSError, ValueError) as exc:
        raise ResearchHarnessError(f"historical data gate rejected input: {exc}") from exc

    try:
        decision_artifact = json.loads(Path(decisions_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ResearchHarnessError(f"cannot read decision artifact: {exc}") from exc
    if not isinstance(decision_artifact, dict):
        raise ResearchHarnessError("decision artifact must be a JSON object")
    try:
        lineage = validate_causal_decision_artifact(
            decision_artifact,
            candle_csv_sha256=loaded["csv_sha256"],
            candle_close_times_ms=[candle["close_time_ms"] for candle in loaded["candles"]],
        )
    except DecisionLineageError as exc:
        raise ResearchHarnessError(f"causal decision lineage rejected input: {exc}") from exc
    brain_version = lineage["brain_version"]
    strategy_version = lineage["strategy_version"]
    decisions = lineage["decisions"]

    try:
        simulation = simulate_next_open(
            loaded["candles"], decisions,
            interval_ms=loaded["interval_ms"],
            initial_cash_usdt=initial_cash_usdt,
            allocation_fraction=allocation_fraction,
            fee_bps_per_side=fee_bps_per_side,
            slippage_bps_per_side=slippage_bps_per_side,
            symbol_filters=symbol_filters,
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise ResearchHarnessError(f"decision/simulation contract rejected input: {exc}") from exc

    paper_ledger = create_ledger(
        initial_cash_usdt=initial_cash_usdt,
        provenance_status="EXTERNAL_PASS_CLAIM_NOT_AUTHENTICATED",
        fee_assumption_note=(
            f"simulator assumptions: fee_bps_per_side={fee_bps_per_side}; "
            f"slippage_bps_per_side={slippage_bps_per_side}"
        ),
    )
    for event in simulation["events"]:
        paper_ledger = append_paper_fill(
            paper_ledger,
            timestamp_ms=event["fill_open_time_ms"],
            side=event["side"],
            quantity_btc=event["quantity_btc"],
            price_usdt=event["fill_price_usdt"],
            fee_usdt=event["fee_usdt"],
            decision_id=event["decision_id"],
            reason="offline simulator event reconciliation",
        )
    accounting = reconcile_simulation_with_ledger(simulation, paper_ledger)
    ledger_integrity = verify_ledger(paper_ledger)

    return {
        "schema_version": "aists.manifest_research_harness.v1",
        "status": "SIMULATED_NOT_VALIDATED",
        "mode": "OFFLINE_RESEARCH_ONLY",
        "data_input": {
            "symbol": loaded["symbol"],
            "market": loaded["market"],
            "interval": loaded["interval"],
            "csv_sha256": loaded["csv_sha256"],
            "manifest_sha256": _sha256(manifest_path),
            "row_count": loaded["row_count"],
            "external_adjudication_claim": "PASS",
            "global_g0_claim": "PASS",
        },
        "decision_input": {
            "artifact_sha256": _sha256(decisions_path),
            "brain_version": brain_version,
            "strategy_version": strategy_version,
            "decision_count": len(decisions),
            "causal_lineage_status": lineage["status"],
            "lineage_limitations": lineage["limitations"],
            "external_status_claim": "PASS",
        },
        "simulation": simulation,
        "accounting_reconciliation": accounting,
        "paper_ledger_integrity": ledger_integrity,
        "limitations": [
            "PASS statuses are externally asserted and are not independently authenticated by this harness",
            "decision generation, causal feature lineage and strategy acceptance are not implemented here",
            "fees and slippage are assumptions supplied to the simulator",
            "symbol_filters are caller-supplied and must be independently evidence-backed for the intended historical period",
            "this result is not a validated historical performance claim or paper acceptance",
            "no automatic stop-loss/take-profit and no live exchange action",
        ],
    }

def run_manifest_driven_simulation_from_stored_features(
    csv_path: str | Path,
    manifest_path: str | Path,
    stored_artifact_path: str | Path,
    *,
    expected_interval: str,
    initial_cash_usdt: float,
    allocation_fraction: float = 0.25,
    fee_bps_per_side: float = 10.0,
    slippage_bps_per_side: float = 5.0,
    symbol_filters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify a create-only stored feature artifact, then use it in the harness.

    The data provenance gate is checked before the artifact is trusted. The
    store reload verifies envelope/payload hashes and causal lineage against
    candle close times. The underlying harness repeats the data and decision
    checks before simulation. A synthetic PASS manifest in tests is only a
    software fixture and is not real-world adjudication evidence.
    """
    try:
        loaded = load_provenance_cleared_candles(
            csv_path, manifest_path, expected_interval=expected_interval
        )
    except (ProvenanceGateError, OSError, ValueError) as exc:
        raise ResearchHarnessError(
            f"historical data gate rejected stored-feature input: {exc}"
        ) from exc
    try:
        from aists_brain.feature_artifact_store import (
            FeatureArtifactStoreError, load_feature_artifact,
        )
        stored = load_feature_artifact(
            stored_artifact_path,
            candle_close_times_ms=[candle["close_time_ms"] for candle in loaded["candles"]],
        )
    except (FeatureArtifactStoreError, OSError, ValueError) as exc:
        raise ResearchHarnessError(
            f"stored feature artifact integrity gate rejected input: {exc}"
        ) from exc
    if stored["artifact"].get("source_csv_sha256") != loaded["csv_sha256"]:
        raise ResearchHarnessError("stored feature artifact is bound to a different candle CSV")
    result = run_manifest_driven_simulation(
        csv_path, manifest_path, stored_artifact_path,
        expected_interval=expected_interval,
        initial_cash_usdt=initial_cash_usdt,
        allocation_fraction=allocation_fraction,
        fee_bps_per_side=fee_bps_per_side,
        slippage_bps_per_side=slippage_bps_per_side,
        symbol_filters=symbol_filters,
    )
    result["decision_input"]["stored_artifact_integrity_status"] = stored["status"]
    result["decision_input"]["stored_artifact_payload_sha256"] = stored["payload_sha256"]
    result["decision_input"]["stored_artifact_file_sha256"] = stored["file_sha256"]
    result["decision_input"]["stored_artifact_store_schema"] = stored["schema_version"]
    result["limitations"].append(
        "stored-artifact wrapper validates hashes and causal contract, not independent source provenance"
    )
    return result
