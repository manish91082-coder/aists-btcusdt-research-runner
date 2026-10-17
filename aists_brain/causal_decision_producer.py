"""Causal strategy-action artifact producer for offline BTCUSDT research.

Computes each completed-candle context from its prefix only, derives a regime,
and calls the deterministic strategy action adapter. It never places orders,
adds automatic stop-loss/take-profit, or authenticates source provenance.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from aists_brain.causal_feature_producer import _INTERVAL_MS, _CONTEXT_NUMERIC
from aists_brain.decision_lineage import DECISION_SCHEMA, canonical_sha256
from aists_brain.market_context import TIMEFRAMES, analyze_market_context
from aists_brain.market_regime import classify_market_regime
from aists_brain.provenance_input import ProvenanceGateError, load_provenance_cleared_candles
from aists_brain.strategy_action_engine import ENGINE_VERSION, generate_research_action


class CausalDecisionProducerError(ValueError):
    """Raised when causal action-artifact inputs or output contracts are invalid."""


def _prefix_hash(prefix: Sequence[Mapping[str, Any]]) -> str:
    try:
        raw = json.dumps(list(prefix), sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CausalDecisionProducerError("candle prefix must be finite JSON data") from exc
    return hashlib.sha256(raw).hexdigest()


def produce_causal_strategy_decisions(
    candles: Sequence[Mapping[str, Any]],
    *,
    timeframe: str,
    candle_csv_sha256: str,
    brain_version: str,
    strategy_version: str,
) -> dict[str, Any]:
    """Produce hash-bound BUY_CANDIDATE/SELL_CANDIDATE/NO_TRADE decisions.

    The supplied candles must already be completed, contiguous and provenance-
    cleared by the caller. Each decision sees only candles up through its own
    close. A candidate action updates the *research state assumption* for the
    next decision, corresponding to a fill at the next contiguous bar open;
    this is not evidence that a real fill occurred.
    """
    if timeframe not in TIMEFRAMES or timeframe not in _INTERVAL_MS:
        raise CausalDecisionProducerError(f"unsupported timeframe: {timeframe}")
    if not isinstance(candle_csv_sha256, str) or len(candle_csv_sha256) != 64 or any(
        char not in "0123456789abcdef" for char in candle_csv_sha256
    ):
        raise CausalDecisionProducerError("candle_csv_sha256 must be lowercase SHA-256")
    if not isinstance(brain_version, str) or not brain_version.strip():
        raise CausalDecisionProducerError("brain_version must be non-empty")
    if not isinstance(strategy_version, str) or not strategy_version.strip():
        raise CausalDecisionProducerError("strategy_version must be non-empty")
    if not isinstance(candles, Sequence) or not candles:
        raise CausalDecisionProducerError("candles must be a non-empty sequence")

    interval = _INTERVAL_MS[timeframe]
    rows: list[dict[str, Any]] = []
    previous_open = None
    for index, candle in enumerate(candles):
        if not isinstance(candle, Mapping):
            raise CausalDecisionProducerError(f"candle {index} must be an object")
        open_ms, close_ms = candle.get("open_time_ms"), candle.get("close_time_ms")
        if isinstance(open_ms, bool) or not isinstance(open_ms, int) or open_ms < 0:
            raise CausalDecisionProducerError(f"candle {index} open_time_ms invalid")
        if isinstance(close_ms, bool) or not isinstance(close_ms, int) or close_ms != open_ms + interval - 1:
            raise CausalDecisionProducerError(f"candle {index} close_time_ms invalid")
        if previous_open is not None:
            if open_ms <= previous_open:
                raise CausalDecisionProducerError("candle timestamps must strictly increase")
            if open_ms != previous_open + interval:
                raise CausalDecisionProducerError("candle gap detected; no gap repair is permitted")
        row = {"open_time_ms": open_ms, "close_time_ms": close_ms}
        for field in ("open", "high", "low", "close", "volume"):
            value = candle.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise CausalDecisionProducerError(f"candle {index} {field} must be finite numeric")
            row[field] = float(value)
        if row["low"] > min(row["open"], row["close"]) or row["high"] < max(row["open"], row["close"]):
            raise CausalDecisionProducerError(f"candle {index} has invalid OHLC range")
        if row["low"] > row["high"] or row["volume"] < 0:
            raise CausalDecisionProducerError(f"candle {index} has invalid low/high/volume")
        rows.append(row)
        previous_open = open_ms

    decisions: list[dict[str, Any]] = []
    position_open = False
    position_strategy: str | None = None
    for index, candle in enumerate(rows):
        prefix = rows[:index + 1]
        context = analyze_market_context(prefix, timeframe)
        regime = classify_market_regime(context)
        action_result = generate_research_action(
            context, regime, position_open=position_open,
            position_strategy=position_strategy,
        )
        prefix_sha = _prefix_hash(prefix)
        observations = []
        for feature_name in _CONTEXT_NUMERIC:
            value = context.get(feature_name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                continue
            observations.append({
                "feature_name": feature_name,
                "timeframe": "1M" if timeframe == "1mo" else timeframe,
                "observed_close_time_ms": candle["close_time_ms"],
                "source_sha256": prefix_sha,
                "value": float(value),
            })
        snapshot = {
            "as_of_ms": candle["close_time_ms"],
            "brain_version": brain_version,
            "strategy_version": strategy_version,
            "action_engine_version": ENGINE_VERSION,
            "feature_observations": observations,
            "feature_status": context["data_status"],
            "context_schema_version": context["schema_version"],
            "regime_schema_version": regime["schema_version"],
            "regime": regime["regime"],
            "volume_state": regime["volume_state"],
            "input_prefix_sha256": prefix_sha,
        }
        action = action_result["action"]
        decision = {
            "decision_id": f"{brain_version}:{timeframe}:{candle['close_time_ms']}",
            "as_of_ms": candle["close_time_ms"],
            "action": action,
            "selected_strategy": action_result["selected_strategy"],
            "reason": action_result["reason"],
            "action_engine_version": ENGINE_VERSION,
            "is_order_instruction": False,
            "automatic_stop_loss": False,
            "automatic_take_profit": False,
            "snapshot": snapshot,
            "snapshot_sha256": canonical_sha256(snapshot),
        }
        decisions.append(decision)
        # Assumed next-open research state only. The final decision may have no
        # next candle to fill against and the downstream simulator remains authoritative.
        if action == "BUY_CANDIDATE":
            position_open = True
            position_strategy = action_result["selected_strategy"]
        elif action == "SELL_CANDIDATE":
            position_open = False
            position_strategy = None

    return {
        "schema_version": DECISION_SCHEMA,
        "status": "PASS",
        "source_csv_sha256": candle_csv_sha256,
        "brain_version": brain_version,
        "strategy_version": strategy_version,
        "timeframe": timeframe,
        "decision_count": len(decisions),
        "decisions": decisions,
        "producer_schema_version": "aists.causal_strategy_decision_producer.v1",
        "producer_status": "ACTIONS_GENERATED_UNVALIDATED",
        "mode": "OFFLINE_RESEARCH_ONLY",
        "safety": {
            "is_order_instruction": False,
            "live_signing": False,
            "public_broadcast": False,
            "exchange_order_placement": False,
            "automatic_stop_loss": False,
            "automatic_take_profit": False,
        },
        "limitations": [
            "each feature snapshot uses only the completed-candle prefix at its decision cutoff",
            "candidate state assumes next contiguous bar open only for subsequent research-state decisions",
            "action rules are deterministic and unvalidated, not trained/calibrated AI",
            "hashes identify artifacts but do not authenticate source truth or historical archive provenance",
            "real-market research remains blocked unless independent G0 and provenance requirements pass",
        ],
    }


def produce_from_provenance_cleared_csv(
    csv_path: str | Path,
    manifest_path: str | Path,
    *,
    expected_interval: str,
    brain_version: str,
    strategy_version: str,
) -> dict[str, Any]:
    """Fail-closed real-input entry point; blocked G0 manifests are rejected."""
    try:
        loaded = load_provenance_cleared_candles(
            csv_path, manifest_path, expected_interval=expected_interval
        )
    except (ProvenanceGateError, OSError, ValueError) as exc:
        raise CausalDecisionProducerError(f"provenance gate rejected decision input: {exc}") from exc
    return produce_causal_strategy_decisions(
        loaded["candles"],
        timeframe=loaded["interval"],
        candle_csv_sha256=loaded["csv_sha256"],
        brain_version=brain_version,
        strategy_version=strategy_version,
    )
