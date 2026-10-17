"""Rule-based market-regime labels derived from market_context features.

Labels are descriptive context for the future strategy selector. They are not
buy/sell signals, forecasts, or proof of a profitable edge.
"""
from __future__ import annotations

from typing import Any, Mapping


def classify_market_regime(
    context: Mapping[str, Any],
    *,
    high_volume_ratio: float = 1.5,
    low_volume_ratio: float = 0.7,
    high_atr_percentile: float | None = None,
) -> dict[str, Any]:
    """Classify a single timeframe context without inventing missing evidence.

    high_atr_percentile is optional and must be computed causally by the caller
    from historical ATR% observations. It is intentionally not inferred from a
    single absolute ATR% value.
    """
    if high_volume_ratio <= 0 or low_volume_ratio < 0 or low_volume_ratio >= high_volume_ratio:
        raise ValueError("volume thresholds must satisfy 0 <= low < high")
    if high_atr_percentile is not None and not 0 <= high_atr_percentile <= 100:
        raise ValueError("high_atr_percentile must be between 0 and 100")

    required = ("trend_state", "latest_close", "prior_resistance", "prior_support",
                "momentum_10_bar_pct", "volume_ratio_vs_prior_median", "data_status")
    missing = [key for key in required if key not in context]
    if missing:
        raise ValueError(f"context missing required fields: {', '.join(missing)}")

    if context["data_status"] != "READY" or context["trend_state"] == "INSUFFICIENT_HISTORY":
        return {
            "schema_version": "aists.market_regime.v1",
            "timeframe": context.get("timeframe"),
            "regime": "INSUFFICIENT_DATA",
            "confidence": "UNASSESSED",
            "evidence": ["history is not marked READY"],
            "volume_state": "UNKNOWN",
            "volatility_state": "UNKNOWN" if high_atr_percentile is None else (
                "HIGH" if high_atr_percentile >= 80 else "NOT_HIGH"
            ),
            "is_trade_signal": False,
        }

    close = float(context["latest_close"])
    resistance = context["prior_resistance"]
    support = context["prior_support"]
    momentum = context["momentum_10_bar_pct"]
    volume_ratio = context["volume_ratio_vs_prior_median"]
    trend = context["trend_state"]
    evidence: list[str] = []

    if volume_ratio is None:
        volume_state = "UNKNOWN"
    elif volume_ratio >= high_volume_ratio:
        volume_state = "HIGH"
        evidence.append("latest volume is elevated versus prior median")
    elif volume_ratio <= low_volume_ratio:
        volume_state = "LOW"
        evidence.append("latest volume is subdued versus prior median")
    else:
        volume_state = "NORMAL"

    if high_atr_percentile is None:
        volatility_state = "UNASSESSED"
    elif high_atr_percentile >= 80:
        volatility_state = "HIGH"
        evidence.append("causal historical ATR percentile is at least 80")
    else:
        volatility_state = "NOT_HIGH"

    if resistance is not None and close > float(resistance):
        regime = "BREAKOUT_UP_CANDIDATE"
        evidence.append("latest close is above prior-lookback resistance")
    elif support is not None and close < float(support):
        regime = "BREAKDOWN_CANDIDATE"
        evidence.append("latest close is below prior-lookback support")
    elif trend == "BULLISH" and momentum is not None and momentum > 0:
        regime = "TRENDING_BULLISH"
        evidence.append("close/EMA trend and 10-bar momentum are bullish")
    elif trend == "BEARISH" and momentum is not None and momentum < 0:
        regime = "TRENDING_BEARISH"
        evidence.append("close/EMA trend and 10-bar momentum are bearish")
    else:
        regime = "RANGE_OR_MIXED"
        evidence.append("trend and momentum do not jointly confirm a direction")

    if volume_state == "HIGH":
        evidence.append("volume confirmation is elevated, not proof of breakout validity")
    elif volume_state == "LOW":
        evidence.append("low volume may reduce setup quality")

    return {
        "schema_version": "aists.market_regime.v1",
        "timeframe": context.get("timeframe"),
        "regime": regime,
        "confidence": "RULE_BASED_UNCALIBRATED",
        "evidence": evidence,
        "volume_state": volume_state,
        "volatility_state": volatility_state,
        "is_trade_signal": False,
        "limitations": [
            "heuristic regime label; not a trained or calibrated AI model",
            "breakout labels are candidates and can be false breakouts",
            "volatility state requires causal historical ATR percentile input",
            "does not select a strategy or place an order",
        ],
    }
