"""Append-only, local-only paper portfolio ledger.

This module accounts for caller-supplied simulated fills. It does not create
signals, obtain market prices, submit orders, or claim real execution.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any, Mapping

LEDGER_SCHEMA = "aists.paper_portfolio_ledger.v1"
GENESIS_HASH = "0" * 64


def _canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _finite_number(name: str, value: Any, *, positive: bool = False, non_negative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    number = float(value)
    if positive and number <= 0:
        raise ValueError(f"{name} must be positive")
    if non_negative and number < 0:
        raise ValueError(f"{name} must be non-negative")
    return number


def create_ledger(*, initial_cash_usdt: float, provenance_status: str = "UNVERIFIED",
                  fee_assumption_note: str = "UNVERIFIED") -> dict[str, Any]:
    """Create an empty paper ledger. Amounts are USDT; no live account is read."""
    cash = _finite_number("initial_cash_usdt", initial_cash_usdt, positive=True)
    if not isinstance(provenance_status, str) or not provenance_status:
        raise ValueError("provenance_status must be a non-empty string")
    if not isinstance(fee_assumption_note, str) or not fee_assumption_note:
        raise ValueError("fee_assumption_note must be a non-empty string")
    return {
        "schema_version": LEDGER_SCHEMA,
        "mode": "PAPER_ONLY",
        "initial_cash_usdt": cash,
        "cash_usdt": cash,
        "btc_quantity": 0.0,
        "realized_pnl_usdt": 0.0,
        "cumulative_fees_usdt": 0.0,
        "sequence": 0,
        "last_event_hash": GENESIS_HASH,
        "events": [],
        "metadata": {
            "provenance_status": provenance_status,
            "fee_assumption_note": fee_assumption_note,
            "live_signing_enabled": False,
            "public_broadcast_enabled": False,
            "binance_orders_placed": False,
        },
    }


def append_paper_fill(ledger: Mapping[str, Any], *, timestamp_ms: int, side: str,
                      quantity_btc: float, price_usdt: float, fee_usdt: float,
                      decision_id: str, reason: str) -> dict[str, Any]:
    """Return a new ledger with one caller-supplied hypothetical fill appended.

    Input ledger is never mutated. BUY consumes cash plus fee; SELL reduces BTC,
    credits proceeds less fee, and realizes proceeds minus allocated average cost.
    The function refuses shorting, overspending, malformed history and duplicate
    event IDs. It intentionally has no exchange/order API.
    """
    state = deepcopy(dict(ledger))
    if state.get("schema_version") != LEDGER_SCHEMA or state.get("mode") != "PAPER_ONLY":
        raise ValueError("unsupported or non-paper ledger schema")
    events = state.get("events")
    if not isinstance(events, list):
        raise ValueError("ledger.events must be a list")
    _verify_ledger(state)
    if isinstance(timestamp_ms, bool) or not isinstance(timestamp_ms, int) or timestamp_ms < 0:
        raise ValueError("timestamp_ms must be a non-negative integer")
    if side not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")
    qty = _finite_number("quantity_btc", quantity_btc, positive=True)
    price = _finite_number("price_usdt", price_usdt, positive=True)
    fee = _finite_number("fee_usdt", fee_usdt, non_negative=True)
    if not isinstance(decision_id, str) or not decision_id.strip():
        raise ValueError("decision_id must be non-empty")
    if any(e.get("decision_id") == decision_id for e in events):
        raise ValueError("duplicate decision_id; append-only ledger rejects duplicate IDs")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reason must be non-empty")
    if events and timestamp_ms < events[-1]["timestamp_ms"]:
        raise ValueError("paper fill timestamps must be non-decreasing")

    notional = qty * price
    cash = float(state["cash_usdt"])
    btc = float(state["btc_quantity"])
    realized = float(state["realized_pnl_usdt"])
    fees = float(state["cumulative_fees_usdt"])
    average_cost = float(state.get("average_cost_usdt_per_btc", 0.0))

    if side == "BUY":
        required = notional + fee
        if required > cash + 1e-10:
            raise ValueError("paper BUY exceeds available cash including fee")
        old_cost = btc * average_cost
        btc += qty
        average_cost = (old_cost + notional) / btc
        cash -= required
    else:
        if qty > btc + 1e-12:
            raise ValueError("paper SELL exceeds held BTC; shorting is disabled")
        if btc <= 0:
            raise ValueError("paper SELL requires an existing BTC position")
        realized += qty * (price - average_cost) - fee
        cash += notional - fee
        btc -= qty
        if btc <= 1e-12:
            btc = 0.0
            average_cost = 0.0

    event = {
        "sequence": len(events) + 1,
        "timestamp_ms": timestamp_ms,
        "decision_id": decision_id,
        "side": side,
        "quantity_btc": qty,
        "price_usdt": price,
        "notional_usdt": notional,
        "fee_usdt": fee,
        "reason": reason,
        "previous_hash": state["last_event_hash"],
    }
    event["event_hash"] = sha256(_canonical(event)).hexdigest()
    state["events"].append(event)
    state["cash_usdt"] = cash
    state["btc_quantity"] = btc
    state["average_cost_usdt_per_btc"] = average_cost
    state["realized_pnl_usdt"] = realized
    state["cumulative_fees_usdt"] = fees + fee
    state["sequence"] = len(state["events"])
    state["last_event_hash"] = event["event_hash"]
    return state


def mark_to_market(ledger: Mapping[str, Any], *, mark_price_usdt: float) -> dict[str, Any]:
    """Value holdings using a caller-supplied price; does not fetch a quote."""
    state = deepcopy(dict(ledger))
    _verify_ledger(state)
    price = _finite_number("mark_price_usdt", mark_price_usdt, positive=True)
    market_value = float(state["btc_quantity"]) * price
    equity = float(state["cash_usdt"]) + market_value
    unrealized = (price - float(state.get("average_cost_usdt_per_btc", 0.0))) * float(state["btc_quantity"])
    return {
        "schema_version": "aists.paper_mark_to_market.v1",
        "mode": "PAPER_ONLY",
        "mark_price_usdt_assumption": price,
        "cash_usdt": float(state["cash_usdt"]),
        "btc_quantity": float(state["btc_quantity"]),
        "btc_market_value_usdt": market_value,
        "equity_usdt": equity,
        "realized_pnl_usdt": float(state["realized_pnl_usdt"]),
        "unrealized_pnl_usdt": unrealized,
        "net_pnl_usdt_before_any_unrecorded_costs": equity - float(state["initial_cash_usdt"]),
        "cumulative_recorded_fees_usdt": float(state["cumulative_fees_usdt"]),
        "is_verified_market_valuation": False,
        "is_order_instruction": False,
    }


def verify_ledger(ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Public hash-chain and sequence verifier for the event journal."""
    _verify_ledger(ledger)
    return {"status": "PASS_HASH_CHAIN", "event_count": len(ledger["events"]),
            "last_event_hash": ledger["last_event_hash"], "mode": "PAPER_ONLY"}


def _verify_ledger(ledger: Mapping[str, Any]) -> None:
    if ledger.get("schema_version") != LEDGER_SCHEMA or ledger.get("mode") != "PAPER_ONLY":
        raise ValueError("unsupported or non-paper ledger schema")
    events = ledger.get("events")
    if not isinstance(events, list):
        raise ValueError("ledger.events must be a list")
    previous = GENESIS_HASH
    for index, event in enumerate(events, start=1):
        if not isinstance(event, Mapping):
            raise ValueError("ledger event must be an object")
        if event.get("sequence") != index or event.get("previous_hash") != previous:
            raise ValueError("ledger sequence or previous hash mismatch")
        content = dict(event)
        supplied_hash = content.pop("event_hash", None)
        expected_hash = sha256(_canonical(content)).hexdigest()
        if supplied_hash != expected_hash:
            raise ValueError("ledger event hash mismatch")
        previous = supplied_hash
    if ledger.get("sequence") != len(events) or ledger.get("last_event_hash") != previous:
        raise ValueError("ledger head does not match event chain")
    for field in ("initial_cash_usdt", "cash_usdt", "btc_quantity", "realized_pnl_usdt", "cumulative_fees_usdt"):
        _finite_number(field, ledger.get(field))
