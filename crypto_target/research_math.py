"""Deterministic math helpers for the 1,000 USDT to target-USDT research project.

No network calls, exchange orders, or profitability claims.
"""
from __future__ import annotations
from collections.abc import Iterable


def target_multiple(starting_equity: float, target_equity: float) -> float:
    if starting_equity <= 0 or target_equity <= 0:
        raise ValueError("equities must be positive")
    return target_equity / starting_equity


def required_period_return(starting_equity: float, target_equity: float, periods: int) -> float:
    """Constant geometric return per period required to reach target (not a forecast)."""
    if starting_equity <= 0 or target_equity <= 0:
        raise ValueError("equities must be positive")
    if periods <= 0:
        raise ValueError("periods must be positive")
    return (target_equity / starting_equity) ** (1.0 / periods) - 1.0


def compound_returns(starting_equity: float, net_returns: Iterable[float]) -> list[float]:
    """Return equity path after each realized net return; returns are decimals."""
    if starting_equity <= 0:
        raise ValueError("starting_equity must be positive")
    equity = starting_equity
    path = []
    for value in net_returns:
        if value < -1.0:
            raise ValueError("a period return cannot be below -100%")
        equity *= 1.0 + value
        path.append(equity)
    return path


def max_drawdown(equity_path: Iterable[float]) -> float:
    """Return maximum drawdown as a negative decimal, e.g. -0.2 for -20%."""
    peak = 0.0
    worst = 0.0
    seen = False
    for equity in equity_path:
        if equity < 0:
            raise ValueError("equity cannot be negative")
        peak = equity if not seen else max(peak, equity)
        seen = True
        if peak > 0:
            worst = min(worst, equity / peak - 1.0)
    return worst
