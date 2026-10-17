"""Capital sizing and cost-sensitivity planner for long-only Spot research.

Planning only: no exchange filters, balances, fee tier, or FX rate are fetched.
No stop-loss/take-profit is assumed, and no order is created.
"""
from __future__ import annotations

import math
from typing import Any

RISK_SCHEMA = "aists.capital_plan.v1"


def build_capital_plan(
    *,
    capital_inr: float,
    inr_per_usdt: float,
    allocation_pct: float = 25.0,
    position_pct: float = 10.0,
    fee_bps_per_side: float = 10.0,
    slippage_bps_per_side: float = 5.0,
    bnb_fee_discount_pct: float = 0.0,
) -> dict[str, Any]:
    """Return a transparent hypothetical sizing/cost plan, never an order.

    FX, fee, slippage, allocation, position and BNB discount values are
    assumptions supplied by the caller; defaults are not verified live terms.
    """
    values = {
        "capital_inr": capital_inr,
        "inr_per_usdt": inr_per_usdt,
        "allocation_pct": allocation_pct,
        "position_pct": position_pct,
        "fee_bps_per_side": fee_bps_per_side,
        "slippage_bps_per_side": slippage_bps_per_side,
        "bnb_fee_discount_pct": bnb_fee_discount_pct,
    }
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
    if capital_inr <= 0 or inr_per_usdt <= 0:
        raise ValueError("capital_inr and inr_per_usdt must be positive")
    if not 0 < allocation_pct <= 100:
        raise ValueError("allocation_pct must be in (0, 100]")
    if not 0 < position_pct <= 100:
        raise ValueError("position_pct must be in (0, 100]")
    if fee_bps_per_side < 0 or slippage_bps_per_side < 0:
        raise ValueError("fee and slippage assumptions must be non-negative")
    if not 0 <= bnb_fee_discount_pct <= 100:
        raise ValueError("bnb_fee_discount_pct must be between 0 and 100")

    capital_usdt = capital_inr / inr_per_usdt
    allocation_budget = capital_usdt * allocation_pct / 100.0
    position_notional = min(allocation_budget, capital_usdt * position_pct / 100.0)
    fee_rate = (fee_bps_per_side / 10_000.0) * (1.0 - bnb_fee_discount_pct / 100.0)
    slippage_rate = slippage_bps_per_side / 10_000.0
    entry_fee = position_notional * fee_rate
    exit_fee = position_notional * fee_rate
    entry_slippage = position_notional * slippage_rate
    exit_slippage = position_notional * slippage_rate
    total_round_trip_cost = entry_fee + exit_fee + entry_slippage + exit_slippage
    break_even_move_bps = (total_round_trip_cost / position_notional * 10_000.0) if position_notional else None

    return {
        "schema_version": RISK_SCHEMA,
        "status": "PLANNING_ONLY_UNVERIFIED_ASSUMPTIONS",
        "capital_inr": float(capital_inr),
        "inr_per_usdt_assumption": float(inr_per_usdt),
        "capital_usdt_estimate": capital_usdt,
        "allocation_pct": float(allocation_pct),
        "allocation_budget_usdt": allocation_budget,
        "position_pct_of_total_capital": float(position_pct),
        "position_notional_usdt": position_notional,
        "unallocated_capital_usdt": capital_usdt - position_notional,
        "cost_assumptions": {
            "fee_bps_per_side": float(fee_bps_per_side),
            "bnb_fee_discount_pct_assumption": float(bnb_fee_discount_pct),
            "slippage_bps_per_side": float(slippage_bps_per_side),
            "fee_tier_verified": False,
            "bnb_discount_eligibility_verified": False,
        },
        "estimated_costs_usdt": {
            "entry_fee": entry_fee,
            "exit_fee": exit_fee,
            "entry_slippage": entry_slippage,
            "exit_slippage": exit_slippage,
            "round_trip_total": total_round_trip_cost,
            "break_even_price_move_bps_approx": break_even_move_bps,
        },
        "controls": {
            "spot_long_only": True,
            "automatic_stop_loss": False,
            "automatic_take_profit": False,
            "is_order_instruction": False,
            "live_signing_enabled": False,
            "public_broadcast_enabled": False,
            "binance_orders_placed": False,
        },
        "limitations": [
            "INR/USDT conversion is caller-supplied and not a live quote",
            "fee, BNB discount, slippage and sizing percentages are assumptions, not verified account/exchange terms",
            "exchange minimum notional, precision, available balance and fee asset are not checked",
            "cost estimate is a simple notional approximation, not a fill simulation or profitability estimate",
            "no stop-loss or take-profit rule is added",
        ],
    }
