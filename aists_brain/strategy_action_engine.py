"""Deterministic signal-to-action adapter for offline research only.

This converts existing strategy-family eligibility into explicit next-bar
candidate actions for the cost-aware simulator. It is not trained AI, does not
prove an edge, and never emits exchange orders or automatic SL/TP instructions.
"""
from __future__ import annotations

from typing import Any, Mapping

from aists_brain.strategy_candidates import evaluate_strategy_candidates

ENGINE_VERSION = "aists.strategy_action_engine.v1"
SUPPORTED_STRATEGIES = {"TREND_FOLLOWING", "BREAKOUT", "MEAN_REVERSION"}


class StrategyActionError(ValueError):
    """Raised when the signal/action state contract is invalid."""


def generate_research_action(
    context: Mapping[str, Any],
    regime_context: Mapping[str, Any],
    *,
    position_open: bool,
    position_strategy: str | None = None,
) -> dict[str, Any]:
    """Return BUY_CANDIDATE, SELL_CANDIDATE, or NO_TRADE from completed-bar context.

    The caller must supply causally computed context for the just-completed bar.
    Any resulting action is intended to be filled only at the next contiguous
    bar open by the offline simulator. No price/quantity/order is produced.

    Strategy exits are ordinary rule exits, not stop-loss or take-profit orders:
    - TREND_FOLLOWING: exit when bullish trend is no longer confirmed or momentum
      is missing/non-positive.
    - BREAKOUT: exit when close falls below the prior-lookback support reference.
    - MEAN_REVERSION: exit when RSI reaches 55 or regime becomes bearish.
    """
    if not isinstance(position_open, bool):
        raise StrategyActionError("position_open must be boolean")
    if position_open:
        if position_strategy not in SUPPORTED_STRATEGIES:
            raise StrategyActionError("an open position requires a supported position_strategy")
        action, reason = _exit_rule(context, regime_context, position_strategy)
        return _result(action, position_strategy, reason, "OPEN_POSITION_RULE_EXIT")
    if position_strategy is not None:
        raise StrategyActionError("position_strategy must be absent when no position is open")

    candidate = evaluate_strategy_candidates(context, regime_context)
    if candidate.get("selected_action") != "LONG_CANDIDATE":
        return _result("NO_TRADE", None,
                       candidate.get("status", "NO_ELIGIBLE_STRATEGY"),
                       candidate.get("status", "NO_ELIGIBLE_STRATEGY"))
    strategy = candidate.get("selected_strategy")
    if strategy not in SUPPORTED_STRATEGIES:
        raise StrategyActionError("candidate selected an unsupported strategy")
    return _result(
        "BUY_CANDIDATE",
        strategy,
        candidate.get("candidates", [{}])[0].get("reason", "eligible candidate"),
        "ENTRY_CANDIDATE",
    )


def _exit_rule(
    context: Mapping[str, Any],
    regime_context: Mapping[str, Any],
    strategy: str,
) -> tuple[str, str]:
    required = ("trend_state", "momentum_10_bar_pct", "rsi14", "latest_close", "prior_support", "data_status")
    missing = [field for field in required if field not in context]
    if missing:
        raise StrategyActionError("market context missing required fields: " + ", ".join(missing))
    if "regime" not in regime_context:
        raise StrategyActionError("regime context missing required field: regime")
    if context["data_status"] != "READY" or regime_context["regime"] == "INSUFFICIENT_DATA":
        return "NO_TRADE", "data not ready; abstain rather than infer an exit"

    if strategy == "TREND_FOLLOWING":
        momentum = context["momentum_10_bar_pct"]
        if context["trend_state"] != "BULLISH" or momentum is None or momentum <= 0:
            return "SELL_CANDIDATE", "bullish trend or positive momentum no longer confirmed"
    elif strategy == "BREAKOUT":
        support = context["prior_support"]
        close = context["latest_close"]
        if support is not None and close is not None and float(close) < float(support):
            return "SELL_CANDIDATE", "close fell below prior-lookback support reference"
    elif strategy == "MEAN_REVERSION":
        rsi = context["rsi14"]
        if (rsi is not None and float(rsi) >= 55) or regime_context["regime"] == "TRENDING_BEARISH":
            return "SELL_CANDIDATE", "mean-reversion exit threshold or bearish regime reached"
    return "NO_TRADE", "strategy exit condition not met"


def _result(action: str, strategy: str | None, reason: str, status: str) -> dict[str, Any]:
    return {
        "schema_version": ENGINE_VERSION,
        "status": status,
        "action": action,
        "selected_strategy": strategy,
        "reason": reason,
        "fill_timing": "NEXT_CONTIGUOUS_BAR_OPEN" if action != "NO_TRADE" else "NONE",
        "is_order_instruction": False,
        "automatic_stop_loss": False,
        "automatic_take_profit": False,
        "mode": "OFFLINE_RESEARCH_ONLY",
        "limitations": [
            "deterministic unvalidated rules, not trained or calibrated AI",
            "candidate actions are not exchange orders",
            "performance remains blocked by historical source and strategy gates",
        ],
    }
