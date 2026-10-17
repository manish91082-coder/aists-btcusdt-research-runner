"""Append-only paper portfolio ledger with durable JSONL audit persistence.

This module accounts only for caller-supplied hypothetical fills and decisions.
It never fetches market prices, submits orders, or claims real execution.
JSONL persistence is single-writer and append-only; protect the file and backups.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Mapping

LEDGER_SCHEMA = "aists.paper_portfolio_ledger.v1"
JSONL_SCHEMA = "aists.paper_portfolio_jsonl.v1"
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


def build_decision_context(decision: Mapping[str, Any], *, brain_version: str,
                           snapshot_sha256: str, as_of_ms: int) -> dict[str, Any]:
    """Bind a paper fill to a frozen research-candidate decision and snapshot hash."""
    if not isinstance(decision, Mapping):
        raise ValueError("decision must be an object")
    if decision.get("status") != "RESEARCH_CANDIDATE_ONLY" or decision.get("selected_action") != "LONG_CANDIDATE":
        raise ValueError("paper fill requires a RESEARCH_CANDIDATE_ONLY LONG_CANDIDATE decision")
    if decision.get("is_order_instruction", False):
        raise ValueError("decision must not be an order instruction")
    if not isinstance(brain_version, str) or not brain_version.strip():
        raise ValueError("brain_version must be non-empty")
    if not isinstance(snapshot_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", snapshot_sha256):
        raise ValueError("snapshot_sha256 must be a 64-character SHA-256")
    if isinstance(as_of_ms, bool) or not isinstance(as_of_ms, int) or as_of_ms < 0:
        raise ValueError("as_of_ms must be a non-negative integer")
    timeframes = decision.get("confirming_timeframes", [])
    if not isinstance(timeframes, list) or any(not isinstance(tf, str) for tf in timeframes):
        raise ValueError("confirming_timeframes must be a list of strings")
    strategy = decision.get("selected_strategy")
    if not isinstance(strategy, str) or not strategy.strip():
        raise ValueError("selected_strategy must be non-empty")
    context = {
        "brain_version": brain_version,
        "snapshot_sha256": snapshot_sha256.lower(),
        "as_of_ms": as_of_ms,
        "decision_status": decision["status"],
        "selected_action": decision["selected_action"],
        "selected_strategy": strategy,
        "confirming_timeframes": list(timeframes),
        "is_order_instruction": False,
    }
    _canonical(context)
    return context


def append_paper_fill(ledger: Mapping[str, Any], *, timestamp_ms: int, side: str,
                      quantity_btc: float, price_usdt: float, fee_usdt: float,
                      decision_id: str, reason: str,
                      decision_context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a new ledger with one caller-supplied hypothetical fill appended.

    BUY consumes cash plus fee; SELL reduces BTC and realizes average-cost P&L.
    decision_context, when present, must be a frozen research-candidate binding.
    The function refuses shorting, overspending, malformed history and duplicate IDs.
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
    if decision_context is not None:
        if not isinstance(decision_context, Mapping):
            raise ValueError("decision_context must be an object")
        required = {"brain_version", "snapshot_sha256", "as_of_ms", "decision_status",
                    "selected_action", "selected_strategy", "confirming_timeframes", "is_order_instruction"}
        if not required.issubset(decision_context):
            raise ValueError("decision_context is missing required fields")
        if decision_context.get("decision_status") != "RESEARCH_CANDIDATE_ONLY" or decision_context.get("selected_action") != "LONG_CANDIDATE":
            raise ValueError("paper fill decision context must be an eligible research candidate")
        if decision_context.get("is_order_instruction") is not False:
            raise ValueError("decision_context cannot be an order instruction")
        if not isinstance(decision_context.get("snapshot_sha256"), str) or not re.fullmatch(r"[0-9a-fA-F]{64}", decision_context["snapshot_sha256"]):
            raise ValueError("decision_context snapshot_sha256 must be a 64-character SHA-256")
        if isinstance(decision_context.get("as_of_ms"), bool) or not isinstance(decision_context.get("as_of_ms"), int) or decision_context["as_of_ms"] > timestamp_ms:
            raise ValueError("decision context cannot be timestamped after the paper fill")
        _canonical(decision_context)

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
    if decision_context is not None:
        event["decision_context"] = deepcopy(dict(decision_context))
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


def _header_for_ledger(ledger: Mapping[str, Any]) -> dict[str, Any]:
    metadata = ledger.get("metadata", {})
    return {
        "record_type": "header",
        "schema_version": JSONL_SCHEMA,
        "ledger_schema_version": LEDGER_SCHEMA,
        "mode": "PAPER_ONLY",
        "initial_cash_usdt": ledger["initial_cash_usdt"],
        "provenance_status": metadata.get("provenance_status", "UNVERIFIED"),
        "fee_assumption_note": metadata.get("fee_assumption_note", "UNVERIFIED"),
    }


def load_ledger_jsonl(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load and reconstruct a persisted JSONL ledger, verifying every event hash."""
    target = Path(path)
    with target.open("r", encoding="utf-8") as stream:
        lines = stream.readlines()
    if not lines:
        raise ValueError("JSONL audit file is empty")
    try:
        header = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSONL header") from exc
    if header.get("record_type") != "header" or header.get("schema_version") != JSONL_SCHEMA or header.get("mode") != "PAPER_ONLY":
        raise ValueError("unsupported JSONL header or non-paper mode")
    ledger = create_ledger(
        initial_cash_usdt=header.get("initial_cash_usdt"),
        provenance_status=header.get("provenance_status", "UNVERIFIED"),
        fee_assumption_note=header.get("fee_assumption_note", "UNVERIFIED"),
    )
    for line_number, line in enumerate(lines[1:], start=2):
        if not line.endswith("\n"):
            raise ValueError(f"truncated JSONL record at line {line_number}")
        try:
            stored = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL record at line {line_number}") from exc
        if stored.get("record_type") != "event" or not isinstance(stored.get("event"), dict):
            raise ValueError(f"invalid event envelope at line {line_number}")
        event = stored["event"]
        context = event.get("decision_context")
        ledger = append_paper_fill(
            ledger,
            timestamp_ms=event.get("timestamp_ms"),
            side=event.get("side"),
            quantity_btc=event.get("quantity_btc"),
            price_usdt=event.get("price_usdt"),
            fee_usdt=event.get("fee_usdt"),
            decision_id=event.get("decision_id"),
            reason=event.get("reason"),
            decision_context=context,
        )
        if _canonical(ledger["events"][-1]) != _canonical(event):
            raise ValueError(f"persisted event does not reconcile at line {line_number}")
    verify_ledger(ledger)
    return ledger


def append_ledger_jsonl(path: str | os.PathLike[str], ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Persist only missing ledger events to a single-writer append-only JSONL file.

    Existing file history must be an exact prefix of the supplied ledger. This
    function does not claim cross-process locking or tamper-proof external storage.
    """
    _verify_ledger(ledger)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    expected_header = _header_for_ledger(ledger)
    if not target.exists():
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(expected_header, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        existing = create_ledger(
            initial_cash_usdt=ledger["initial_cash_usdt"],
            provenance_status=expected_header["provenance_status"],
            fee_assumption_note=expected_header["fee_assumption_note"],
        )
    else:
        existing = load_ledger_jsonl(target)
        if _canonical(_header_for_ledger(existing)) != _canonical(expected_header):
            raise ValueError("existing JSONL header does not match supplied ledger metadata")
    if len(existing["events"]) > len(ledger["events"]):
        raise ValueError("refusing ledger rollback: JSONL file contains newer events")
    for index, old_event in enumerate(existing["events"]):
        if _canonical(old_event) != _canonical(ledger["events"][index]):
            raise ValueError("existing JSONL history is not an exact prefix of supplied ledger")
    appended = 0
    with target.open("a", encoding="utf-8", newline="\n") as stream:
        for event in ledger["events"][len(existing["events"]):]:
            record = {"record_type": "event", "event": event}
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
            appended += 1
    verified = load_ledger_jsonl(target)
    return {
        "status": "PASS_DURABLE_JSONL_HASH_CHAIN",
        "path": str(target),
        "event_count": len(verified["events"]),
        "new_events_appended": appended,
        "last_event_hash": verified["last_event_hash"],
        "single_writer_only": True,
        "mode": "PAPER_ONLY",
    }
