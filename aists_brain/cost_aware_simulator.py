"""Cost-aware, next-open simulator for explicit research decisions.

Offline-only. It accepts caller-supplied candles and decisions; it never creates
signals, fetches quotes, sends orders, or claims profitability. No SL/TP logic.
"""
from __future__ import annotations

import math
from decimal import Decimal, ROUND_DOWN
from typing import Any, Mapping, Sequence


def _number(name: str, value: Any, *, positive: bool = False, non_negative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite numeric")
    result = float(value)
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive")
    if non_negative and result < 0:
        raise ValueError(f"{name} must be non-negative")
    return result


def simulate_next_open(
    candles: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
    *,
    interval_ms: int,
    initial_cash_usdt: float,
    allocation_fraction: float = 0.25,
    fee_bps_per_side: float = 10.0,
    slippage_bps_per_side: float = 5.0,
    symbol_filters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Simulate explicit BUY_CANDIDATE/SELL_CANDIDATE decisions at next contiguous open.

    Each decision's as_of_ms is the close-time (inclusive) of a candle in the
    supplied series. Its eligible fill is the immediately following bar whose
    open_time_ms equals as_of_ms + 1. Gaps are not bridged and signals are skipped.
    At most one long position is held. BUY sizing uses a fraction of available cash,
    including the entry fee. If symbol_filters are supplied, BUY quantity is rounded
    down to step_size and both BUY and SELL quantities/notionals are checked against
    the supplied min_qty, optional max_qty and min_notional.
    The caller must supply evidence-backed filters; this function does not fetch them.
    SELL closes the full position. No automatic SL/TP.
    """
    if isinstance(interval_ms, bool) or not isinstance(interval_ms, int) or interval_ms <= 0:
        raise ValueError("interval_ms must be a positive integer")
    initial_cash = _number("initial_cash_usdt", initial_cash_usdt, positive=True)
    allocation = _number("allocation_fraction", allocation_fraction, positive=True)
    if allocation > 1:
        raise ValueError("allocation_fraction must be <= 1")
    fee_bps = _number("fee_bps_per_side", fee_bps_per_side, non_negative=True)
    slip_bps = _number("slippage_bps_per_side", slippage_bps_per_side, non_negative=True)
    if fee_bps >= 10000 or slip_bps >= 10000:
        raise ValueError("fee/slippage bps must be below 10000")
    if not candles:
        raise ValueError("candles must not be empty")

    filters = None
    if symbol_filters is not None:
        if not isinstance(symbol_filters, Mapping):
            raise ValueError("symbol_filters must be a mapping")
        required_filter_fields = ("min_qty", "step_size", "min_notional")
        missing_filter_fields = [name for name in required_filter_fields if name not in symbol_filters]
        if missing_filter_fields:
            raise ValueError("symbol_filters missing required fields: " + ", ".join(missing_filter_fields))
        filters = {
            "min_qty": _number("symbol_filters.min_qty", symbol_filters["min_qty"], positive=True),
            "step_size": _number("symbol_filters.step_size", symbol_filters["step_size"], positive=True),
            "min_notional": _number("symbol_filters.min_notional", symbol_filters["min_notional"], non_negative=True),
        }
        if "max_qty" in symbol_filters and symbol_filters["max_qty"] is not None:
            filters["max_qty"] = _number("symbol_filters.max_qty", symbol_filters["max_qty"], positive=True)
        if filters.get("max_qty") is not None and filters["max_qty"] < filters["min_qty"]:
            raise ValueError("symbol_filters.max_qty must be >= min_qty")

    bars = []
    by_close = {}
    previous_open = None
    for index, raw in enumerate(candles):
        if not isinstance(raw, Mapping):
            raise ValueError("each candle must be an object")
        open_ms = raw.get("open_time_ms")
        close_ms = raw.get("close_time_ms")
        if isinstance(open_ms, bool) or not isinstance(open_ms, int) or open_ms < 0:
            raise ValueError("open_time_ms must be a non-negative integer")
        if isinstance(close_ms, bool) or not isinstance(close_ms, int) or close_ms != open_ms + interval_ms - 1:
            raise ValueError("close_time_ms must equal open_time_ms + interval_ms - 1")
        if previous_open is not None and open_ms <= previous_open:
            raise ValueError("candle open times must be strictly increasing")
        op = _number("open", raw.get("open"), positive=True)
        close = _number("close", raw.get("close"), positive=True)
        bar = {"open_time_ms": open_ms, "close_time_ms": close_ms, "open": op, "close": close}
        bars.append(bar)
        if close_ms in by_close:
            raise ValueError("duplicate candle close timestamp")
        by_close[close_ms] = bar
        previous_open = open_ms

    decision_list = []
    previous_asof = None
    seen_ids = set()
    allowed = {"BUY_CANDIDATE", "SELL_CANDIDATE", "NO_TRADE"}
    for raw in decisions:
        if not isinstance(raw, Mapping):
            raise ValueError("each decision must be an object")
        asof = raw.get("as_of_ms")
        decision_id = raw.get("decision_id")
        action = raw.get("action")
        # Fail closed if a caller attempts to pass an order/live/automatic-SLTP
        # instruction through the research simulator. The simulator is paper-only.
        for flag in (
            "is_order_instruction",
            "live_signing_enabled",
            "public_broadcast_enabled",
            "binance_orders_placed",
            "automatic_stop_loss",
            "automatic_take_profit",
        ):
            if flag in raw and not isinstance(raw[flag], bool):
                raise ValueError(f"decision {flag} must be boolean when supplied")
            if raw.get(flag) is True:
                raise ValueError(f"research decision cannot enable {flag}")
        if isinstance(asof, bool) or not isinstance(asof, int) or asof < 0:
            raise ValueError("decision as_of_ms must be a non-negative integer")
        if previous_asof is not None and asof <= previous_asof:
            raise ValueError("decision as_of_ms values must be strictly increasing")
        if not isinstance(decision_id, str) or not decision_id.strip() or decision_id in seen_ids:
            raise ValueError("decision_id must be non-empty and unique")
        if action not in allowed:
            raise ValueError(f"unsupported decision action: {action!r}")
        if asof not in by_close:
            raise ValueError("each decision must reference a supplied candle close_time_ms")
        decision_list.append({"as_of_ms": asof, "decision_id": decision_id, "action": action})
        seen_ids.add(decision_id)
        previous_asof = asof

    cash = initial_cash
    quantity = 0.0
    position_cost_usdt = 0.0
    events = []
    skipped = []
    closed_round_trips = []
    fee_rate = fee_bps / 10000.0
    slip_rate = slip_bps / 10000.0
    bars_by_open = {bar["open_time_ms"]: bar for bar in bars}

    for decision in decision_list:
        action = decision["action"]
        if action == "NO_TRADE":
            continue
        expected_open = decision["as_of_ms"] + 1
        fill_bar = bars_by_open.get(expected_open)
        if fill_bar is None:
            skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                            "reason": "NO_NEXT_CONTIGUOUS_BAR", "is_order_instruction": False})
            continue
        if action == "BUY_CANDIDATE":
            if quantity > 0:
                skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                "reason": "POSITION_ALREADY_OPEN", "is_order_instruction": False})
                continue
            fill_price = fill_bar["open"] * (1.0 + slip_rate)
            budget = cash * allocation
            raw_qty = budget / (fill_price * (1.0 + fee_rate))
            qty = raw_qty
            if filters is not None:
                step = Decimal(str(filters["step_size"]))
                qty = float((Decimal(str(raw_qty)) / step).to_integral_value(rounding=ROUND_DOWN) * step)
                if qty < filters["min_qty"]:
                    skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                    "reason": "BELOW_MIN_QTY", "is_order_instruction": False})
                    continue
                if filters.get("max_qty") is not None and qty > filters["max_qty"]:
                    skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                    "reason": "ABOVE_MAX_QTY", "is_order_instruction": False})
                    continue
            notional = qty * fill_price
            if filters is not None and notional < filters["min_notional"]:
                skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                "reason": "BELOW_MIN_NOTIONAL", "is_order_instruction": False})
                continue
            fee = notional * fee_rate
            total = notional + fee
            if qty <= 0 or total > cash + 1e-10:
                skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                "reason": "INSUFFICIENT_CASH", "is_order_instruction": False})
                continue
            cash -= total
            quantity = qty
            position_cost_usdt = total
            event = {"decision_id": decision["decision_id"], "action": action,
                     "signal_as_of_ms": decision["as_of_ms"], "fill_open_time_ms": expected_open,
                     "side": "BUY", "quantity_btc": qty, "fill_price_usdt": fill_price,
                     "notional_usdt": notional, "fee_usdt": fee, "slippage_bps_per_side": slip_bps,
                     "is_order_instruction": False}
            events.append(event)
        elif action == "SELL_CANDIDATE":
            if quantity <= 0:
                skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                "reason": "NO_OPEN_POSITION", "is_order_instruction": False})
                continue
            fill_price = fill_bar["open"] * (1.0 - slip_rate)
            notional = quantity * fill_price
            if filters is not None:
                if quantity < filters["min_qty"]:
                    skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                    "reason": "SELL_BELOW_MIN_QTY", "is_order_instruction": False})
                    continue
                if filters.get("max_qty") is not None and quantity > filters["max_qty"]:
                    skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                    "reason": "SELL_ABOVE_MAX_QTY", "is_order_instruction": False})
                    continue
                if notional < filters["min_notional"]:
                    skipped.append({"decision_id": decision["decision_id"], "as_of_ms": decision["as_of_ms"],
                                    "reason": "SELL_BELOW_MIN_NOTIONAL", "is_order_instruction": False})
                    continue
            fee = notional * fee_rate
            proceeds = notional - fee
            realized = proceeds - position_cost_usdt
            cash += proceeds
            event = {"decision_id": decision["decision_id"], "action": action,
                     "signal_as_of_ms": decision["as_of_ms"], "fill_open_time_ms": expected_open,
                     "side": "SELL", "quantity_btc": quantity, "fill_price_usdt": fill_price,
                     "notional_usdt": notional, "fee_usdt": fee, "realized_net_pnl_usdt": realized,
                     "slippage_bps_per_side": slip_bps, "is_order_instruction": False}
            events.append(event)
            closed_round_trips.append({"entry_decision_id": next(e["decision_id"] for e in reversed(events[:-1]) if e["side"] == "BUY"),
                                       "exit_decision_id": decision["decision_id"],
                                       "net_pnl_usdt": realized})
            quantity = 0.0
            position_cost_usdt = 0.0

    last_close = bars[-1]["close"]
    exit_mark_price = last_close * (1.0 - slip_rate)
    marked_exit_value = quantity * exit_mark_price * (1.0 - fee_rate)
    equity = cash + marked_exit_value
    return {
        "schema_version": "aists.cost_aware_simulation.v1",
        "status": "SIMULATED_NOT_VALIDATED",
        "mode": "OFFLINE_RESEARCH_ONLY",
        "initial_cash_usdt": initial_cash,
        "cash_usdt": cash,
        "btc_quantity": quantity,
        "last_close_price_assumption_usdt": last_close,
        "equity_usdt_after_estimated_exit_costs": equity,
        "net_pnl_usdt_after_modeled_costs": equity - initial_cash,
        "net_return_pct_after_modeled_costs": (equity / initial_cash - 1.0) * 100.0,
        "fee_bps_per_side": fee_bps,
        "slippage_bps_per_side": slip_bps,
        "allocation_fraction": allocation,
        "exchange_filters_applied": filters is not None,
        "exchange_filters": filters,
        "event_count": len(events),
        "closed_round_trip_count": len(closed_round_trips),
        "events": events,
        "skipped_decisions": skipped,
        "closed_round_trips": closed_round_trips,
        "limitations": [
            "all candles and decisions are caller-supplied; data provenance is not adjudicated here",
            "not a full acceptance backtest: no coverage, regime-block, PBO/DSR or drawdown gate",
            "open position is marked using last close with estimated exit costs; it is not force-liquidated",
            "no automatic stop-loss/take-profit, no network, no exchange orders, no live account access",
            "exchange quantity/notional filters are not enforced unless caller supplies verified symbol_filters",
        ],
    }

def simulate_next_open_with_capital_cost_contract(
    candles: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
    *,
    interval_ms: int,
    capital_cost_contract: Mapping[str, Any],
    research_input_scope: str,
) -> dict[str, Any]:
    """Run a synthetic-fixture-only simulation using an evidence-gated cost contract.

    The required scope literal deliberately blocks historical-market inputs in this
    checkpoint while G0 is blocked. Fixture source references exercise contract
    wiring only; they are not external evidence, exchange terms, or market results.
    """
    from aists_brain.capital_cost_contract import CONTRACT_SCHEMA

    if research_input_scope != "SYNTHETIC_SOFTWARE_FIXTURE_ONLY":
        raise ValueError(
            "CP-0276 permits synthetic software fixtures only while G0 is blocked"
        )
    if not isinstance(capital_cost_contract, Mapping):
        raise ValueError("capital_cost_contract must be a mapping")
    if capital_cost_contract.get("schema_version") != CONTRACT_SCHEMA:
        raise ValueError("unsupported capital_cost_contract schema")
    if capital_cost_contract.get("status") != "ASSUMPTIONS_VERIFIED_FOR_MODELING_ONLY":
        raise ValueError("capital_cost_contract assumptions are blocked or unverified")
    gate_boundary = capital_cost_contract.get("gate_boundary")
    if not isinstance(gate_boundary, Mapping) or gate_boundary.get(
        "g0_must_be_independently_cleared_before_real_historical_inputs"
    ) is not True:
        raise ValueError("capital_cost_contract is missing the G0 boundary")
    if gate_boundary.get("candidate_build_backtest_or_paper_authorized_by_this_contract") is not False:
        raise ValueError("capital_cost_contract cannot authorize backtest or paper activity")
    if gate_boundary.get("live_signing_public_broadcast_exchange_orders") is not False:
        raise ValueError("capital_cost_contract safety boundary is invalid")
    if gate_boundary.get("automatic_stop_loss_take_profit") is not False:
        raise ValueError("capital_cost_contract SL/TP boundary is invalid")
    if gate_boundary.get("profitability_established") is not False:
        raise ValueError("capital_cost_contract cannot claim profitability")

    required = (
        "capital_usdt", "allocation_fraction", "fee_bps_per_side",
        "slippage_bps_per_side", "symbol_filters",
    )
    missing = [key for key in required if capital_cost_contract.get(key) is None]
    if missing:
        raise ValueError("capital_cost_contract missing usable fields: " + ", ".join(missing))
    source_fields = (
        ("fx_verified", "fx_source_ref"),
        ("allocation_fraction", "allocation_source_ref"),
        ("fee_bps_per_side", "fee_source_ref"),
        ("slippage_bps_per_side", "slippage_source_ref"),
        ("symbol_filters", "symbol_filters_source_ref"),
    )
    if capital_cost_contract.get("fx_verified") is not True:
        raise ValueError("capital_cost_contract FX is not verified")
    for value_field, source_field in source_fields:
        if capital_cost_contract.get(value_field) is None:
            raise ValueError(f"capital_cost_contract {value_field} is unavailable")
        source_ref = capital_cost_contract.get(source_field)
        if not isinstance(source_ref, str) or not source_ref.strip():
            raise ValueError(f"capital_cost_contract {source_field} is missing")
    if not isinstance(capital_cost_contract.get("symbol_filters"), Mapping):
        raise ValueError("capital_cost_contract symbol_filters must be a mapping")

    result = simulate_next_open(
        candles,
        decisions,
        interval_ms=interval_ms,
        initial_cash_usdt=capital_cost_contract["capital_usdt"],
        allocation_fraction=capital_cost_contract["allocation_fraction"],
        fee_bps_per_side=capital_cost_contract["fee_bps_per_side"],
        slippage_bps_per_side=capital_cost_contract["slippage_bps_per_side"],
        symbol_filters=capital_cost_contract["symbol_filters"],
    )
    result["capital_cost_contract_schema"] = CONTRACT_SCHEMA
    result["capital_cost_contract_status"] = capital_cost_contract["status"]
    result["execution_mode"] = "CONTRACT_BOUND_SYNTHETIC_FIXTURE_ONLY"
    result["research_input_scope"] = research_input_scope
    result["capital_cost_contract_sources"] = {
        source_field: capital_cost_contract[source_field]
        for _, source_field in source_fields
    }
    result["limitations"].append(
        "CP-0276 contract wiring was exercised with synthetic software fixtures only; "
        "fixture references are not real external evidence or market-performance results"
    )
    result["safety_boundary"] = {
        "real_historical_inputs_permitted": False,
        "candidate_build_backtest_or_paper_authorized": False,
        "live_signing_public_broadcast_exchange_orders": False,
        "automatic_stop_loss_take_profit": False,
        "profitability_established": False,
    }
    return result

