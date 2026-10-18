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
