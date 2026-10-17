"""Independent accounting reconciliation for simulator events and paper ledger."""
from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from aists_brain.paper_portfolio import verify_ledger


class ReconciliationError(ValueError):
    """Raised when simulator events and paper accounting do not reconcile."""


def _num(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ReconciliationError(f"{name} must be finite numeric")
    return float(value)


def reconcile_simulation_with_ledger(
    simulation: Mapping[str, Any], ledger: Mapping[str, Any], *,
    tolerance_usdt: float = 1e-8, tolerance_btc: float = 1e-12,
) -> dict[str, Any]:
    """Recompute event cash/inventory/fees and compare against two accounting paths.

    The simulator output and paper ledger must represent the same ordered fills.
    This function does not validate market data, signals, fees as exchange truth,
    or strategy profitability. Tolerances are explicit numerical comparison bounds.
    """
    if not isinstance(simulation, Mapping) or simulation.get("schema_version") != "aists.cost_aware_simulation.v1":
        raise ReconciliationError("unsupported simulator result schema")
    if simulation.get("mode") != "OFFLINE_RESEARCH_ONLY":
        raise ReconciliationError("simulator result is not offline research mode")
    if not isinstance(ledger, Mapping) or ledger.get("mode") != "PAPER_ONLY":
        raise ReconciliationError("ledger is not PAPER_ONLY")
    tolerance_usdt = _num("tolerance_usdt", tolerance_usdt)
    tolerance_btc = _num("tolerance_btc", tolerance_btc)
    if tolerance_usdt < 0 or tolerance_btc < 0:
        raise ReconciliationError("tolerances must be non-negative")

    verify_ledger(ledger)
    sim_events = simulation.get("events")
    ledger_events = ledger.get("events")
    if not isinstance(sim_events, list) or not isinstance(ledger_events, list):
        raise ReconciliationError("simulator and ledger events must be lists")
    if len(sim_events) != len(ledger_events):
        raise ReconciliationError("event count mismatch between simulator and paper ledger")

    fee_bps = _num("fee_bps_per_side", simulation.get("fee_bps_per_side"))
    slip_bps = _num("slippage_bps_per_side", simulation.get("slippage_bps_per_side"))
    if fee_bps < 0 or slip_bps < 0 or fee_bps >= 10000 or slip_bps >= 10000:
        raise ReconciliationError("simulator fee/slippage assumptions are outside valid bounds")
    fee_rate = fee_bps / 10000.0

    initial_cash = _num("initial_cash_usdt", simulation.get("initial_cash_usdt"))
    cash = initial_cash
    btc = 0.0
    fees = 0.0
    buys = sells = 0
    checks: list[dict[str, Any]] = []

    for index, (event, ledger_event) in enumerate(zip(sim_events, ledger_events), start=1):
        if not isinstance(event, Mapping) or not isinstance(ledger_event, Mapping):
            raise ReconciliationError(f"event {index} is not an object")
        side = event.get("side")
        if side not in ("BUY", "SELL"):
            raise ReconciliationError(f"unsupported simulator event side at event {index}")
        expected_side_by_action = {"BUY_CANDIDATE": "BUY", "SELL_CANDIDATE": "SELL"}
        if event.get("action") not in expected_side_by_action or expected_side_by_action[event["action"]] != side:
            raise ReconciliationError(f"simulator action/side mismatch at event {index}")
        if event.get("is_order_instruction") is not False:
            raise ReconciliationError(f"simulator event must not be an order instruction at event {index}")
        event_slippage_bps = _num(f"event_{index}_slippage_bps_per_side", event.get("slippage_bps_per_side"))
        if abs(event_slippage_bps - slip_bps) > 1e-12:
            raise ReconciliationError(f"event slippage assumption mismatch at event {index}")
        if event.get("decision_id") != ledger_event.get("decision_id"):
            raise ReconciliationError(f"decision ID mismatch at event {index}")
        if event.get("fill_open_time_ms") != ledger_event.get("timestamp_ms"):
            raise ReconciliationError(f"fill timestamp mismatch at event {index}")
        if side != ledger_event.get("side"):
            raise ReconciliationError(f"side mismatch at event {index}")
        quantity = _num(f"event_{index}_quantity", event.get("quantity_btc"))
        price = _num(f"event_{index}_price", event.get("fill_price_usdt"))
        fee = _num(f"event_{index}_fee", event.get("fee_usdt"))
        notional = _num(f"event_{index}_notional", event.get("notional_usdt"))
        if quantity <= 0 or price <= 0 or fee < 0 or notional < 0:
            raise ReconciliationError(f"invalid quantity/price/fee/notional at event {index}")
        if abs(quantity - _num("ledger_quantity", ledger_event.get("quantity_btc"))) > tolerance_btc:
            raise ReconciliationError(f"quantity mismatch at event {index}")
        if abs(price - _num("ledger_price", ledger_event.get("price_usdt"))) > tolerance_usdt:
            raise ReconciliationError(f"price mismatch at event {index}")
        if abs(fee - _num("ledger_fee", ledger_event.get("fee_usdt"))) > tolerance_usdt:
            raise ReconciliationError(f"fee mismatch at event {index}")
        if abs(notional - quantity * price) > max(tolerance_usdt, abs(notional) * 1e-12):
            raise ReconciliationError(f"notional arithmetic mismatch at event {index}")
        expected_fee = notional * fee_rate
        if abs(fee - expected_fee) > max(tolerance_usdt, abs(expected_fee) * 1e-12):
            raise ReconciliationError(f"fee arithmetic mismatch with declared fee rate at event {index}")

        if side == "BUY":
            cash -= notional + fee
            btc += quantity
            buys += 1
        else:
            if quantity > btc + tolerance_btc:
                raise ReconciliationError(f"recomputed inventory would go short at event {index}")
            cash += notional - fee
            btc -= quantity
            sells += 1
        fees += fee
        checks.append({"event_index": index, "decision_id": event["decision_id"], "status": "PASS"})

    sim_cash = _num("simulator_cash_usdt", simulation.get("cash_usdt"))
    sim_btc = _num("simulator_btc_quantity", simulation.get("btc_quantity"))
    ledger_cash = _num("ledger_cash_usdt", ledger.get("cash_usdt"))
    ledger_btc = _num("ledger_btc_quantity", ledger.get("btc_quantity"))
    ledger_fees = _num("ledger_cumulative_fees_usdt", ledger.get("cumulative_fees_usdt"))
    if abs(cash - sim_cash) > tolerance_usdt:
        raise ReconciliationError("independent cash recomputation does not match simulator")
    if abs(cash - ledger_cash) > tolerance_usdt:
        raise ReconciliationError("independent cash recomputation does not match paper ledger")
    if abs(btc - sim_btc) > tolerance_btc:
        raise ReconciliationError("independent BTC inventory does not match simulator")
    if abs(btc - ledger_btc) > tolerance_btc:
        raise ReconciliationError("independent BTC inventory does not match paper ledger")
    if abs(fees - ledger_fees) > tolerance_usdt:
        raise ReconciliationError("independent cumulative fees do not match paper ledger")

    last_close = _num("last_close_price_assumption_usdt", simulation.get("last_close_price_assumption_usdt"))
    slip_rate = slip_bps / 10000.0
    independently_marked_equity = cash + btc * last_close * (1.0 - slip_rate) * (1.0 - fee_rate)
    reported_equity = _num("equity_usdt_after_estimated_exit_costs",
                           simulation.get("equity_usdt_after_estimated_exit_costs"))
    if abs(independently_marked_equity - reported_equity) > tolerance_usdt:
        raise ReconciliationError("independent mark-to-market does not match simulator equity")
    if initial_cash <= 0:
        raise ReconciliationError("initial cash must be positive")
    expected_net_pnl = independently_marked_equity - initial_cash
    reported_net_pnl = _num("net_pnl_usdt_after_modeled_costs", simulation.get("net_pnl_usdt_after_modeled_costs"))
    if abs(expected_net_pnl - reported_net_pnl) > tolerance_usdt:
        raise ReconciliationError("net PnL summary does not match independently reconciled equity")
    expected_return_pct = (independently_marked_equity / initial_cash - 1.0) * 100.0
    reported_return_pct = _num("net_return_pct_after_modeled_costs", simulation.get("net_return_pct_after_modeled_costs"))
    if abs(expected_return_pct - reported_return_pct) > max(1e-10, abs(expected_return_pct) * 1e-12):
        raise ReconciliationError("net return summary does not match independently reconciled equity")

    return {
        "schema_version": "aists.accounting_reconciliation.v1",
        "status": "PASS_ACCOUNTING_RECONCILIATION",
        "mode": "OFFLINE_RESEARCH_ONLY",
        "event_count": len(sim_events),
        "buy_count": buys,
        "sell_count": sells,
        "independently_recomputed_cash_usdt": cash,
        "independently_recomputed_btc_quantity": btc,
        "independently_recomputed_fees_usdt": fees,
        "independently_recomputed_equity_usdt": independently_marked_equity,
        "checks": checks,
        "limitations": [
            "reconciles arithmetic only; it does not validate source provenance, signal quality or strategy performance",
            "fee and slippage rates remain simulation assumptions, not verified exchange terms",
            "paper ledger fills are hypothetical and no exchange orders are placed",
        ],
    }
