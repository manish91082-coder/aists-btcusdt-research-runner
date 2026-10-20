"""Conservative shared snapshot across all supported AISTS timeframes."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .market_context import TIMEFRAMES

SNAPSHOT_SCHEMA = "aists.multi_timeframe_snapshot.v1"
BULLISH = {"BREAKOUT_UP_CANDIDATE", "TRENDING_BULLISH"}
BEARISH = {"BREAKDOWN_CANDIDATE", "TRENDING_BEARISH"}


def build_multi_timeframe_snapshot(
    contexts: Mapping[str, Mapping[str, Any]],
    regimes: Mapping[str, Mapping[str, Any]],
    *,
    as_of_ms: int | None = None,
) -> dict[str, Any]:
    """Join supplied completed-candle analyses; never fills or resamples data.

    Inputs are keyed by timeframe. Missing or limited frames force a NO_TRADE
    readiness state. The caller must establish candle completion, timestamps,
    gap checks and provenance before calling this function.
    """
    unknown_contexts = sorted(set(contexts) - set(TIMEFRAMES))
    unknown_regimes = sorted(set(regimes) - set(TIMEFRAMES))
    if unknown_contexts or unknown_regimes:
        raise ValueError(
            f"unsupported timeframe keys: contexts={unknown_contexts}, regimes={unknown_regimes}"
        )
    if as_of_ms is not None and (isinstance(as_of_ms, bool) or not isinstance(as_of_ms, int) or as_of_ms < 0):
        raise ValueError("as_of_ms must be a non-negative integer or None")

    frames: dict[str, Any] = {}
    missing: list[str] = []
    limited: list[str] = []
    bullish: list[str] = []
    bearish: list[str] = []
    neutral: list[str] = []
    conflicts: list[str] = []

    for timeframe in TIMEFRAMES:
        context = contexts.get(timeframe)
        regime = regimes.get(timeframe)
        if context is None or regime is None:
            missing.append(timeframe)
            frames[timeframe] = {
                "status": "MISSING",
                "context": deepcopy(context) if context is not None else None,
                "regime": deepcopy(regime) if regime is not None else None,
            }
            continue
        if context.get("timeframe") != timeframe or regime.get("timeframe") != timeframe:
            raise ValueError(f"timeframe key does not match payload for {timeframe}")
        ready = context.get("data_status") == "READY" and regime.get("regime") != "INSUFFICIENT_DATA"
        frames[timeframe] = {
            "status": "READY" if ready else "LIMITED",
            "context": deepcopy(dict(context)),
            "regime": deepcopy(dict(regime)),
        }
        if not ready:
            limited.append(timeframe)
            continue
        label = str(regime.get("regime"))
        if label in BULLISH:
            bullish.append(timeframe)
        elif label in BEARISH:
            bearish.append(timeframe)
        else:
            neutral.append(timeframe)

    if bullish and bearish:
        alignment = "MIXED_CONFLICT"
        conflicts.append("bullish and bearish regimes coexist across timeframes")
    elif bullish and not bearish:
        alignment = "BULLISH_BIAS"
    elif bearish and not bullish:
        alignment = "BEARISH_BIAS"
    else:
        alignment = "NEUTRAL_OR_UNRESOLVED"

    complete = not missing and not limited
    return {
        "schema_version": SNAPSHOT_SCHEMA,
        "as_of_ms": as_of_ms,
        "expected_timeframes": list(TIMEFRAMES),
        "frames": frames,
        "missing_timeframes": missing,
        "limited_timeframes": limited,
        "directional_counts": {
            "bullish": len(bullish), "bearish": len(bearish), "neutral": len(neutral)
        },
        "bullish_timeframes": bullish,
        "bearish_timeframes": bearish,
        "neutral_timeframes": neutral,
        "alignment": alignment,
        "conflicts": conflicts,
        "readiness": "READY" if complete else "NO_TRADE_INCOMPLETE_TIMEFRAME_EVIDENCE",
        "is_trade_signal": False,
        "limitations": [
            "requires caller-verified completed candles, source provenance and gap handling",
            "no missing timeframe is forward-filled or synthesized",
            "directional alignment is descriptive and is not a calibrated probability",
            "this snapshot does not select an executable action or place orders",
        ],
    }
