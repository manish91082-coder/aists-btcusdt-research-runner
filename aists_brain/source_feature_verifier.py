"""Independent verification that decision features derive from actual candle prefixes.

This is a software integrity gate, not market-data provenance or profitability evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping, Sequence

from aists_brain.decision_lineage import DecisionLineageError
from aists_brain.market_context import TIMEFRAMES, analyze_market_context


_NUMERIC_CONTEXT_FIELDS = (
    "latest_close", "latest_volume", "ema20", "ema50", "rsi14",
    "momentum_10_bar_pct", "atr14", "atr14_pct",
    "volume_median_prior", "volume_ratio_vs_prior_median",
    "prior_resistance", "prior_support",
)


class SourceFeatureVerificationError(ValueError):
    """Raised when a feature snapshot does not match the supplied source candles."""


def _normalized_candles(candles: Sequence[Mapping[str, Any]], timeframe: str) -> list[dict[str, Any]]:
    interval_ms = {
        "5m": 300_000, "15m": 900_000, "30m": 1_800_000,
        "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000,
        "1w": 604_800_000, "1mo": 2_592_000_000,
    }.get(timeframe)
    if interval_ms is None:
        raise SourceFeatureVerificationError(f"unsupported source timeframe: {timeframe}")
    if not isinstance(candles, Sequence) or not candles:
        raise SourceFeatureVerificationError("source candles must be a non-empty sequence")
    rows = []
    previous_open = None
    for index, candle in enumerate(candles):
        if not isinstance(candle, Mapping):
            raise SourceFeatureVerificationError(f"source candle {index} must be an object")
        open_ms, close_ms = candle.get("open_time_ms"), candle.get("close_time_ms")
        if isinstance(open_ms, bool) or not isinstance(open_ms, int) or open_ms < 0:
            raise SourceFeatureVerificationError(f"source candle {index} open timestamp invalid")
        if isinstance(close_ms, bool) or not isinstance(close_ms, int) or close_ms != open_ms + interval_ms - 1:
            raise SourceFeatureVerificationError(f"source candle {index} close timestamp invalid")
        if previous_open is not None and open_ms != previous_open + interval_ms:
            raise SourceFeatureVerificationError("source candle prefix is not contiguous")
        row = {"open_time_ms": open_ms, "close_time_ms": close_ms}
        for field in ("open", "high", "low", "close", "volume"):
            value = candle.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise SourceFeatureVerificationError(f"source candle {index} {field} must be finite numeric")
            row[field] = float(value)
        rows.append(row)
        previous_open = open_ms
    return rows


def _prefix_sha256(prefix: Sequence[Mapping[str, Any]]) -> str:
    raw = json.dumps(
        list(prefix), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verify_features_against_source_candles(
    artifact: Mapping[str, Any],
    *,
    candles: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Recompute each decision's exact candle prefix hash and numeric context features."""
    timeframe = artifact.get("timeframe")
    if timeframe not in TIMEFRAMES:
        raise SourceFeatureVerificationError("artifact timeframe is missing or unsupported")
    rows = _normalized_candles(candles, timeframe)
    closes = {row["close_time_ms"]: index for index, row in enumerate(rows)}
    decisions = artifact.get("decisions")
    if not isinstance(decisions, list):
        raise SourceFeatureVerificationError("artifact decisions must be a list")
    decision_timeframe = "1M" if timeframe == "1mo" else timeframe

    for decision_index, decision in enumerate(decisions):
        if not isinstance(decision, Mapping):
            raise SourceFeatureVerificationError(f"decision {decision_index} must be an object")
        as_of_ms = decision.get("as_of_ms")
        if isinstance(as_of_ms, bool) or not isinstance(as_of_ms, int) or as_of_ms not in closes:
            raise SourceFeatureVerificationError(f"decision {decision_index} cutoff does not match a source candle close")
        candle_index = closes[as_of_ms]
        prefix = rows[:candle_index + 1]
        expected_hash = _prefix_sha256(prefix)
        snapshot = decision.get("snapshot")
        if not isinstance(snapshot, Mapping):
            raise SourceFeatureVerificationError(f"decision {decision_index} snapshot missing")
        if snapshot.get("input_prefix_sha256") != expected_hash:
            raise SourceFeatureVerificationError(
                f"decision {decision_index} input prefix hash does not match actual source candles"
            )
        context = analyze_market_context(prefix, timeframe)
        observations = snapshot.get("feature_observations")
        if not isinstance(observations, list) or not observations:
            raise SourceFeatureVerificationError(f"decision {decision_index} feature observations missing")
        observed_names = set()
        for feature in observations:
            if not isinstance(feature, Mapping):
                raise SourceFeatureVerificationError(f"decision {decision_index} feature must be an object")
            name = feature.get("feature_name")
            if name not in _NUMERIC_CONTEXT_FIELDS or name in observed_names:
                raise SourceFeatureVerificationError(
                    f"decision {decision_index} contains unknown or duplicate feature {name!r}"
                )
            observed_names.add(name)
            if feature.get("timeframe") != decision_timeframe:
                raise SourceFeatureVerificationError(f"decision {decision_index} feature timeframe mismatch")
            if feature.get("observed_close_time_ms") != as_of_ms:
                raise SourceFeatureVerificationError(f"decision {decision_index} feature cutoff mismatch")
            if feature.get("source_sha256") != expected_hash:
                raise SourceFeatureVerificationError(f"decision {decision_index} feature source hash mismatch")
            expected_value = context.get(name)
            actual_value = feature.get("value")
            if expected_value is None or isinstance(actual_value, bool) or not isinstance(actual_value, (int, float)):
                raise SourceFeatureVerificationError(f"decision {decision_index} feature {name} is not independently reproducible")
            if not math.isfinite(actual_value) or float(actual_value) != float(expected_value):
                raise SourceFeatureVerificationError(
                    f"decision {decision_index} feature value mismatch for {name}"
                )
        expected_names = {
            name for name in _NUMERIC_CONTEXT_FIELDS
            if isinstance(context.get(name), (int, float))
            and not isinstance(context.get(name), bool)
            and math.isfinite(context[name])
        }
        if observed_names != expected_names:
            raise SourceFeatureVerificationError(
                f"decision {decision_index} feature set does not match recomputed market context"
            )

    return {
        "schema_version": "aists.source_feature_verification.v1",
        "status": "PASS_SOURCE_FEATURE_RECOMPUTATION",
        "decision_count": len(decisions),
        "candle_count": len(rows),
        "timeframe": timeframe,
        "mode": "OFFLINE_RESEARCH_ONLY",
        "limitations": [
            "verifies feature derivation from the supplied candle rows, not external source provenance",
            "does not validate strategy quality, profitability, or live readiness",
        ],
    }
