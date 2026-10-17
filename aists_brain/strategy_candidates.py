"""Transparent strategy-family eligibility and conservative candidate selection.

This is a deterministic research layer, not a trained AI or order engine.
It emits candidates for downstream backtesting; it never submits orders.
"""
from __future__ import annotations

from typing import Any, Mapping


STRATEGY_RULES = {
    "TREND_FOLLOWING": {
        "description": "Long-only continuation in confirmed bullish trend and positive momentum",
        "requires": ["trend_state=BULLISH", "momentum_10_bar_pct>0", "regime=TRENDING_BULLISH"],
        "failure_conditions": ["mixed/bearish trend", "non-positive momentum", "low relative volume"],
    },
    "BREAKOUT": {
        "description": "Potential long breakout above prior-lookback resistance with volume confirmation",
        "requires": ["regime=BREAKOUT_UP_CANDIDATE", "volume_state=HIGH or NORMAL"],
        "failure_conditions": ["close not above prior resistance", "low/unknown volume", "insufficient history"],
    },
    "MEAN_REVERSION": {
        "description": "Potential oversold bounce candidate only in a mixed/range context",
        "requires": ["rsi14<=30", "regime=RANGE_OR_MIXED"],
        "failure_conditions": ["confirmed directional trend", "RSI unavailable or above 30"],
    },
}


def evaluate_strategy_candidates(
    context: Mapping[str, Any],
    regime_context: Mapping[str, Any],
) -> dict[str, Any]:
    """Return eligible research candidates; no final buy/sell or order instruction."""
    required_context = ("trend_state", "momentum_10_bar_pct", "rsi14", "data_status")
    missing = [key for key in required_context if key not in context]
    if missing:
        raise ValueError(f"market context missing required fields: {', '.join(missing)}")
    if "regime" not in regime_context or "volume_state" not in regime_context:
        raise ValueError("regime context missing required fields: regime, volume_state")

    if context["data_status"] != "READY" or regime_context["regime"] == "INSUFFICIENT_DATA":
        return {
            "schema_version": "aists.strategy_candidates.v1",
            "status": "ABSTAIN_INSUFFICIENT_DATA",
            "candidates": [],
            "selected_strategy": None,
            "selected_action": "NO_TRADE",
            "is_order_instruction": False,
        }

    trend = context["trend_state"]
    momentum = context["momentum_10_bar_pct"]
    rsi = context["rsi14"]
    regime = regime_context["regime"]
    volume = regime_context["volume_state"]
    candidates: list[dict[str, str]] = []

    if regime == "TRENDING_BULLISH" and trend == "BULLISH" and momentum is not None and momentum > 0 and volume != "LOW":
        candidates.append({
            "strategy": "TREND_FOLLOWING",
            "candidate_action": "LONG_CANDIDATE",
            "reason": "bullish trend and positive 10-bar momentum",
        })

    if regime == "BREAKOUT_UP_CANDIDATE" and volume in ("HIGH", "NORMAL"):
        candidates.append({
            "strategy": "BREAKOUT",
            "candidate_action": "LONG_CANDIDATE",
            "reason": "close above prior resistance with non-low volume",
        })

    if regime == "RANGE_OR_MIXED" and rsi is not None and rsi <= 30:
        candidates.append({
            "strategy": "MEAN_REVERSION",
            "candidate_action": "LONG_CANDIDATE",
            "reason": "RSI is oversold in a range/mixed regime",
        })

    if len(candidates) == 1:
        status = "ONE_ELIGIBLE_CANDIDATE"
        selected_strategy = candidates[0]["strategy"]
        selected_action = candidates[0]["candidate_action"]
    elif len(candidates) > 1:
        status = "CONFLICT_ABSTAIN"
        selected_strategy = None
        selected_action = "NO_TRADE"
    else:
        status = "NO_ELIGIBLE_STRATEGY"
        selected_strategy = None
        selected_action = "NO_TRADE"

    return {
        "schema_version": "aists.strategy_candidates.v1",
        "status": status,
        "candidates": candidates,
        "selected_strategy": selected_strategy,
        "selected_action": selected_action,
        "is_order_instruction": False,
        "limitations": [
            "heuristic eligibility rules are not validated trading edge",
            "no fee/slippage-adjusted backtest is performed here",
            "candidate output is not an exchange order",
            "stop-loss/take-profit behavior is not implemented or implied",
        ],
    }
