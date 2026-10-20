"""Causal feature/snapshot producer from already-cleared candle rows.

For each candle close, computes market context from the prefix ending at that
candle only. It emits NO_TRADE records because feature production is not a
strategy signal generator. The caller must separately pass the provenance gate.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from aists_brain.decision_lineage import DECISION_SCHEMA, canonical_sha256
from aists_brain.market_context import TIMEFRAMES, analyze_market_context
from aists_brain.provenance_input import ProvenanceGateError, load_provenance_cleared_candles


_INTERVAL_MS = {
    "5m": 300_000, "15m": 900_000, "30m": 1_800_000,
    "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000,
    "1w": 604_800_000, "1mo": 2_592_000_000,
}
_CONTEXT_NUMERIC = (
    "latest_close", "latest_volume", "ema20", "ema50", "rsi14",
    "momentum_10_bar_pct", "atr14", "atr14_pct",
    "volume_median_prior", "volume_ratio_vs_prior_median",
    "prior_resistance", "prior_support",
)


class FeatureProducerError(ValueError):
    """Raised when candle rows cannot support deterministic causal snapshots."""


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_candles_sha256(candles: Sequence[Mapping[str, Any]]) -> str:
    try:
        raw = json.dumps(list(candles), sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise FeatureProducerError("candle prefix must be finite JSON-compatible data") from exc
    return _sha256_bytes(raw)


def produce_causal_feature_snapshots(
    candles: Sequence[Mapping[str, Any]],
    *,
    timeframe: str,
    candle_csv_sha256: str,
    brain_version: str,
    strategy_version: str,
) -> dict[str, Any]:
    """Produce a versioned NO_TRADE decision artifact with prefix-only features.

    Input candles must already be provenance-cleared, completed, contiguous
    OHLCV records with open_time_ms and close_time_ms. This function does not
    authenticate their provenance or repair missing intervals.
    """
    if timeframe not in TIMEFRAMES or timeframe not in _INTERVAL_MS:
        raise FeatureProducerError(f"unsupported timeframe: {timeframe}")
    if not isinstance(candle_csv_sha256, str) or len(candle_csv_sha256) != 64 or any(
        c not in "0123456789abcdef" for c in candle_csv_sha256
    ):
        raise FeatureProducerError("candle_csv_sha256 must be lowercase SHA-256")
    if not isinstance(brain_version, str) or not brain_version.strip():
        raise FeatureProducerError("brain_version must be non-empty")
    if not isinstance(strategy_version, str) or not strategy_version.strip():
        raise FeatureProducerError("strategy_version must be non-empty")
    if not isinstance(candles, Sequence) or not candles:
        raise FeatureProducerError("candles must be a non-empty sequence")

    interval_ms = _INTERVAL_MS[timeframe]
    normalized: list[dict[str, Any]] = []
    previous_open = None
    for index, raw in enumerate(candles):
        if not isinstance(raw, Mapping):
            raise FeatureProducerError(f"candle {index} must be an object")
        open_ms, close_ms = raw.get("open_time_ms"), raw.get("close_time_ms")
        if isinstance(open_ms, bool) or not isinstance(open_ms, int) or open_ms < 0:
            raise FeatureProducerError(f"candle {index} open_time_ms invalid")
        if isinstance(close_ms, bool) or not isinstance(close_ms, int) or close_ms != open_ms + interval_ms - 1:
            raise FeatureProducerError(f"candle {index} close_time_ms invalid")
        if previous_open is not None:
            if open_ms <= previous_open:
                raise FeatureProducerError("candle open times must be strictly increasing")
            if open_ms != previous_open + interval_ms:
                raise FeatureProducerError("candle series has a gap; producer never repairs gaps")
        row = {"open_time_ms": open_ms, "close_time_ms": close_ms}
        for field in ("open", "high", "low", "close", "volume"):
            value = raw.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise FeatureProducerError(f"candle {index} {field} must be finite numeric")
            row[field] = float(value)
        normalized.append(row)
        previous_open = open_ms

    decision_timeframe = "1M" if timeframe == "1mo" else timeframe
    decisions = []
    for index, candle in enumerate(normalized):
        prefix = normalized[:index + 1]
        context = analyze_market_context(prefix, timeframe)
        observations = []
        prefix_hash = _canonical_candles_sha256(prefix)
        for feature_name in _CONTEXT_NUMERIC:
            value = context.get(feature_name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                continue
            observations.append({
                "feature_name": feature_name,
                "timeframe": decision_timeframe,
                "observed_close_time_ms": candle["close_time_ms"],
                "source_sha256": prefix_hash,
                "value": float(value),
            })
        snapshot = {
            "as_of_ms": candle["close_time_ms"],
            "brain_version": brain_version,
            "strategy_version": strategy_version,
            "feature_observations": observations,
            "feature_status": context["data_status"],
            "context_schema_version": context["schema_version"],
            "input_prefix_sha256": prefix_hash,
        }
        decisions.append({
            "decision_id": f"{brain_version}:{timeframe}:{candle['close_time_ms']}",
            "as_of_ms": candle["close_time_ms"],
            "action": "NO_TRADE",
            "snapshot": snapshot,
            "snapshot_sha256": canonical_sha256(snapshot),
        })

    return {
        "schema_version": DECISION_SCHEMA,
        "status": "PASS",
        "source_csv_sha256": candle_csv_sha256,
        "brain_version": brain_version,
        "strategy_version": strategy_version,
        "timeframe": timeframe,
        "decision_count": len(decisions),
        "decisions": decisions,
        "producer_status": "FEATURES_ONLY_NO_TRADE",
        "limitations": [
            "every snapshot uses only the candle prefix ending at its decision close",
            "all actions are NO_TRADE; this producer does not implement strategy signals",
            "input source provenance must be cleared by an independent gate before use",
            "feature source hashes identify prefix bytes in canonical JSON, not an external archive",
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
    """Load only through the fail-closed provenance gate, then produce snapshots.

    This function never bypasses G0. Manifest PASS remains an external claim
    that this loader cannot authenticate; unresolved project provenance must stay
    blocked and should not be relabelled PASS to run this function.
    """
    try:
        loaded = load_provenance_cleared_candles(
            csv_path, manifest_path, expected_interval=expected_interval
        )
    except (ProvenanceGateError, OSError, ValueError) as exc:
        raise FeatureProducerError(f"provenance gate rejected feature input: {exc}") from exc
    return produce_causal_feature_snapshots(
        loaded["candles"],
        timeframe=loaded["interval"],
        candle_csv_sha256=loaded["csv_sha256"],
        brain_version=brain_version,
        strategy_version=strategy_version,
    )
