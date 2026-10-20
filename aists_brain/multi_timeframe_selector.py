"""Conservative multi-timeframe research candidate consensus."""
from __future__ import annotations

from typing import Any, Mapping

from .market_context import TIMEFRAMES


def select_multi_timeframe_candidate(
    snapshot: Mapping[str, Any],
    candidates_by_timeframe: Mapping[str, Mapping[str, Any]],
    *,
    min_confirming_timeframes: int = 3,
) -> dict[str, Any]:
    """Require complete snapshot and same-family confirmation across timeframes.

    This emits a research candidate only. It is not an order instruction, and
    does not override source-data, paper-trading, or live-readiness gates.
    """
    if min_confirming_timeframes < 1 or min_confirming_timeframes > len(TIMEFRAMES):
        raise ValueError("min_confirming_timeframes must be between 1 and 8")
    unknown = sorted(set(candidates_by_timeframe) - set(TIMEFRAMES))
    if unknown:
        raise ValueError(f"unsupported candidate timeframe keys: {unknown}")
    if snapshot.get("schema_version") != "aists.multi_timeframe_snapshot.v1":
        raise ValueError("unsupported or missing multi-timeframe snapshot schema")
    if snapshot.get("readiness") != "READY":
        return _abstain("ABSTAIN_INCOMPLETE_SNAPSHOT", "snapshot is not ready")
    if snapshot.get("alignment") != "BULLISH_BIAS":
        return _abstain("ABSTAIN_DIRECTIONAL_CONFLICT", "timeframes do not show a clean bullish bias")
    missing = sorted(set(TIMEFRAMES) - set(candidates_by_timeframe))
    if missing:
        return _abstain("ABSTAIN_MISSING_CANDIDATE_EVALUATIONS",
                        "candidate evaluations are missing for: " + ", ".join(missing))

    supported_strategies = {"TREND_FOLLOWING", "BREAKOUT", "MEAN_REVERSION"}
    eligible: list[tuple[str, str]] = []
    for timeframe in TIMEFRAMES:
        candidate = candidates_by_timeframe[timeframe]
        if not isinstance(candidate, Mapping):
            raise ValueError(f"candidate evaluation for {timeframe} must be a mapping")
        if candidate.get("is_order_instruction", False) is not False:
            raise ValueError("candidate evaluation must explicitly remain non-order-instruction")
        action = candidate.get("selected_action")
        strategy = candidate.get("selected_strategy")
        if action == "NO_TRADE":
            if strategy is not None:
                raise ValueError(f"NO_TRADE candidate must not select a strategy for {timeframe}")
            if candidate.get("status") == "CONFLICT_ABSTAIN":
                return _abstain("ABSTAIN_STRATEGY_CONFLICT",
                                f"strategy-family conflict at {timeframe}")
            continue
        if action != "LONG_CANDIDATE":
            raise ValueError(f"unsupported candidate action for {timeframe}: {action!r}")
        if strategy not in supported_strategies:
            raise ValueError(f"unsupported or missing strategy for {timeframe}: {strategy!r}")
        eligible.append((timeframe, strategy))

    if not eligible:
        return _abstain("NO_ELIGIBLE_MULTI_TIMEFRAME_CANDIDATE", "no timeframe supplied an eligible long candidate")
    strategies = {strategy for _, strategy in eligible}
    if len(strategies) != 1:
        return _abstain("ABSTAIN_STRATEGY_FAMILY_DISAGREEMENT",
                        "eligible timeframes disagree on strategy family")
    strategy = next(iter(strategies))
    confirming = [timeframe for timeframe, _ in eligible]
    if len(confirming) < min_confirming_timeframes:
        return _abstain("ABSTAIN_WEAK_TIMEFRAME_CONFIRMATION",
                        f"{len(confirming)} timeframes confirm; {min_confirming_timeframes} required")

    return {
        "schema_version": "aists.multi_timeframe_candidate.v1",
        "status": "RESEARCH_CANDIDATE_ONLY",
        "selected_strategy": strategy,
        "selected_action": "LONG_CANDIDATE",
        "confirming_timeframes": confirming,
        "confirmation_count": len(confirming),
        "minimum_confirmation_count": min_confirming_timeframes,
        "is_order_instruction": False,
        "limitations": [
            "deterministic consensus heuristic, not trained or calibrated AI",
            "no expected return or profitability claim is made",
            "not a final buy/sell decision and cannot authorize live trading",
        ],
    }


def _abstain(status: str, reason: str) -> dict[str, Any]:
    return {
        "schema_version": "aists.multi_timeframe_candidate.v1",
        "status": status,
        "selected_strategy": None,
        "selected_action": "NO_TRADE",
        "confirming_timeframes": [],
        "confirmation_count": 0,
        "is_order_instruction": False,
        "reason": reason,
    }
