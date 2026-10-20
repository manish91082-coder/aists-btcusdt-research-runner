"""Evidence-gated capital and cost contract for INR-funded BTCUSDT research.

No exchange calls, live orders, FX lookup, or fee/filter discovery occurs here.
Unknown assumptions stay unknown. A verified contract never overrides G0 or
authorizes a candidate build, backtest, paper trading, or live activity.
"""
from __future__ import annotations

import math
from typing import Any, Mapping

CONTRACT_SCHEMA = "aists.capital_cost_contract.v1"
INITIAL_CAPITAL_INR = 10_000.0


def _number(name: str, value: Any, *, positive: bool = False,
            non_negative: bool = False, fraction: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite numeric")
    result = float(value)
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive")
    if non_negative and result < 0:
        raise ValueError(f"{name} must be non-negative")
    if fraction and not 0 <= result <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return result


def _verified_ref(verified: Any, source_ref: Any, field: str) -> bool:
    if not isinstance(verified, bool):
        raise ValueError(f"{field}_verified must be boolean")
    if source_ref is not None and (not isinstance(source_ref, str) or not source_ref.strip()):
        raise ValueError(f"{field}_source_ref must be a non-empty string when supplied")
    return verified and isinstance(source_ref, str) and bool(source_ref.strip())


def build_capital_cost_contract(
    *,
    fx_inr_per_usdt: float | None = None,
    fx_source_ref: str | None = None,
    fx_verified: bool = False,
    allocation_fraction: float | None = None,
    allocation_source_ref: str | None = None,
    allocation_verified: bool = False,
    fee_bps_per_side: float | None = None,
    fee_source_ref: str | None = None,
    fee_verified: bool = False,
    slippage_bps_per_side: float | None = None,
    slippage_source_ref: str | None = None,
    slippage_verified: bool = False,
    symbol_filters: Mapping[str, Any] | None = None,
    symbol_filters_source_ref: str | None = None,
    symbol_filters_verified: bool = False,
    bnb_fee_savings_fraction: float | None = None,
    bnb_conversion_overhead_fraction: float | None = None,
    bnb_source_ref: str | None = None,
    bnb_verified: bool = False,
) -> dict[str, Any]:
    """Return an auditable model contract; absent/unverified values stay null.

    BNB savings and conversion overhead are fractions of baseline fee cost, not
    claimed Binance rates. They require a verified source reference.
    """
    fx_ok = _verified_ref(fx_verified, fx_source_ref, "fx")
    allocation_ok = _verified_ref(allocation_verified, allocation_source_ref, "allocation")
    fee_ok = _verified_ref(fee_verified, fee_source_ref, "fee")
    slippage_ok = _verified_ref(slippage_verified, slippage_source_ref, "slippage")
    filters_ok = _verified_ref(symbol_filters_verified, symbol_filters_source_ref, "symbol_filters")
    bnb_ok = _verified_ref(bnb_verified, bnb_source_ref, "bnb")

    fx = _number("fx_inr_per_usdt", fx_inr_per_usdt, positive=True) if fx_inr_per_usdt is not None else None
    allocation = _number("allocation_fraction", allocation_fraction, positive=True, fraction=True) if allocation_fraction is not None else None
    fee = _number("fee_bps_per_side", fee_bps_per_side, non_negative=True) if fee_bps_per_side is not None else None
    slippage = _number("slippage_bps_per_side", slippage_bps_per_side, non_negative=True) if slippage_bps_per_side is not None else None
    if fee is not None and fee >= 10000:
        raise ValueError("fee_bps_per_side must be below 10000")
    if slippage is not None and slippage >= 10000:
        raise ValueError("slippage_bps_per_side must be below 10000")

    if symbol_filters is not None and not isinstance(symbol_filters, Mapping):
        raise ValueError("symbol_filters must be a mapping")
    filters = None
    if symbol_filters is not None:
        required = ("min_qty", "step_size", "min_notional")
        missing = [name for name in required if name not in symbol_filters]
        if missing:
            raise ValueError("symbol_filters missing required fields: " + ", ".join(missing))
        filters = {
            "min_qty": _number("symbol_filters.min_qty", symbol_filters["min_qty"], positive=True),
            "step_size": _number("symbol_filters.step_size", symbol_filters["step_size"], positive=True),
            "min_notional": _number("symbol_filters.min_notional", symbol_filters["min_notional"], non_negative=True),
        }
        if symbol_filters.get("max_qty") is not None:
            filters["max_qty"] = _number("symbol_filters.max_qty", symbol_filters["max_qty"], positive=True)
            if filters["max_qty"] < filters["min_qty"]:
                raise ValueError("symbol_filters.max_qty must be >= min_qty")

    bnb_savings = (_number("bnb_fee_savings_fraction", bnb_fee_savings_fraction, non_negative=True, fraction=True)
                   if bnb_fee_savings_fraction is not None else None)
    bnb_overhead = (_number("bnb_conversion_overhead_fraction", bnb_conversion_overhead_fraction, non_negative=True, fraction=True)
                    if bnb_conversion_overhead_fraction is not None else None)

    capital_usdt = INITIAL_CAPITAL_INR / fx if fx is not None and fx_ok else None
    usable_allocation = allocation if allocation is not None and allocation_ok else None
    usable_fee = fee if fee is not None and fee_ok else None
    usable_slippage = slippage if slippage is not None and slippage_ok else None
    filters_usable = filters if filters is not None and filters_ok else None
    max_allocated_usdt = capital_usdt * usable_allocation if capital_usdt is not None and usable_allocation is not None else None

    round_trip_fee_bps = usable_fee * 2 if usable_fee is not None else None
    round_trip_slippage_bps = usable_slippage * 2 if usable_slippage is not None else None
    estimated_round_trip_cost_usdt = None
    if max_allocated_usdt is not None and round_trip_fee_bps is not None and round_trip_slippage_bps is not None:
        estimated_round_trip_cost_usdt = max_allocated_usdt * (round_trip_fee_bps + round_trip_slippage_bps) / 10000.0

    bnb_inputs_complete = bnb_ok and bnb_savings is not None and bnb_overhead is not None and usable_fee is not None
    bnb_effective_fee_bps_per_side = (
        usable_fee * (1.0 - bnb_savings + bnb_overhead) if bnb_inputs_complete else None
    )

    required_verified = {
        "fx": fx is not None and fx_ok,
        "allocation": allocation is not None and allocation_ok,
        "fee": fee is not None and fee_ok,
        "slippage": slippage is not None and slippage_ok,
        "symbol_filters": filters is not None and filters_ok,
    }
    missing = [name for name, ready in required_verified.items() if not ready]
    return {
        "schema_version": CONTRACT_SCHEMA,
        "status": "ASSUMPTIONS_VERIFIED_FOR_MODELING_ONLY" if not missing else "BLOCKED_UNVERIFIED_ASSUMPTIONS",
        "initial_capital_inr": INITIAL_CAPITAL_INR,
        "capital_usdt": capital_usdt,
        "fx_inr_per_usdt_input": fx,
        "fx_source_ref": fx_source_ref,
        "fx_verified": fx_ok,
        "allocation_fraction": usable_allocation,
        "allocation_source_ref": allocation_source_ref,
        "fee_bps_per_side": usable_fee,
        "fee_source_ref": fee_source_ref,
        "slippage_bps_per_side": usable_slippage,
        "slippage_source_ref": slippage_source_ref,
        "symbol_filters": filters_usable,
        "symbol_filters_source_ref": symbol_filters_source_ref,
        "max_allocated_usdt": max_allocated_usdt,
        "estimated_round_trip_fee_bps": round_trip_fee_bps,
        "estimated_round_trip_slippage_bps": round_trip_slippage_bps,
        "estimated_round_trip_cost_usdt_at_max_allocation": estimated_round_trip_cost_usdt,
        "bnb": {
            "status": "SCENARIO_INPUTS_VERIFIED_NOT_EXCHANGE_CONFIRMED" if bnb_inputs_complete else "NOT_EVALUATED_UNVERIFIED_OR_INCOMPLETE",
            "fee_savings_fraction_of_baseline": bnb_savings if bnb_ok else None,
            "conversion_overhead_fraction_of_baseline_fee": bnb_overhead if bnb_ok else None,
            "effective_fee_bps_per_side_scenario_only": bnb_effective_fee_bps_per_side,
            "source_ref": bnb_source_ref if bnb_ok else None,
        },
        "missing_verified_inputs": missing,
        "gate_boundary": {
            "g0_must_be_independently_cleared_before_real_historical_inputs": True,
            "candidate_build_backtest_or_paper_authorized_by_this_contract": False,
            "live_signing_public_broadcast_exchange_orders": False,
            "automatic_stop_loss_take_profit": False,
            "profitability_established": False,
        },
        "limitations": [
            "INR 10,000 is the fixed source capital; USDT conversion is not guessed",
            "verified means the caller has independently checked the cited source; this module does not authenticate sources",
            "fee and slippage cost estimate is a simple notional approximation, not a fill simulation",
            "BNB economics are a scenario only and are not confirmed Binance fee terms",
            "exchange filters are unusable unless supplied with an explicit verified source reference",
            "a modeling-ready status does not override G0, CP-0040, or candidate-specific authorization",
        ],
    }
