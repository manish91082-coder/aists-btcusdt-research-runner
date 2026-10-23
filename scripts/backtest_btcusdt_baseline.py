#!/usr/bin/env python3
"""Cost-explicit deterministic Spot benchmarks for normalized BTCUSDT research data.

This is accounting infrastructure, not a trading strategy or financial advice.
No Futures positions or funding cash flows are simulated in this version.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def load_spot_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("input dataset contains no candle rows")
    normalized = []
    previous = None
    for row in rows:
        try:
            ts = int(row["open_time_ms"])
            open_price = float(row["spot_open"])
            close_price = float(row["spot_close"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid timestamp/open/close row: {row}") from exc
        if previous is not None and ts <= previous:
            raise ValueError("timestamps must be strictly increasing and unique")
        if not all(math.isfinite(x) and x > 0 for x in (open_price, close_price)):
            raise ValueError(f"prices must be finite and positive at timestamp {ts}")
        normalized.append({"timestamp_ms": ts, "open": open_price, "close": close_price})
        previous = ts
    return normalized


def max_drawdown(equity_values: list[float]) -> float:
    peak = -math.inf
    worst = 0.0
    for value in equity_values:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, value / peak - 1.0)
    return worst


def run_benchmarks(rows: list[dict], initial_equity: float, fee_bps: float,
                   spread_bps: float, slippage_bps: float) -> tuple[dict, list[dict]]:
    if not rows:
        raise ValueError("rows must not be empty")
    if not math.isfinite(initial_equity) or initial_equity <= 0:
        raise ValueError("initial equity must be finite and positive")
    for name, value in (("fee_bps", fee_bps), ("spread_bps", spread_bps),
                        ("slippage_bps", slippage_bps)):
        if not math.isfinite(value) or value < 0 or value >= 10000:
            raise ValueError(f"{name} must be finite and in [0, 10000)")
    fee = fee_bps / 10000.0
    impact = (spread_bps / 2.0 + slippage_bps) / 10000.0
    if impact >= 1:
        raise ValueError("combined half-spread and slippage must be below 10000 bps")

    # Flat/no-trade benchmark keeps cash unchanged and incurs no execution costs.
    flat_curve = [{"timestamp_ms": r["timestamp_ms"], "flat_equity": initial_equity}
                  for r in rows]

    first_open = rows[0]["open"]
    buy_fill = first_open * (1.0 + impact)
    # Allocate all capital including entry fee, so equity cannot go negative at entry.
    quantity = initial_equity / (buy_fill * (1.0 + fee))
    entry_notional = quantity * buy_fill
    entry_fee = entry_notional * fee
    last_close = rows[-1]["close"]
    sell_fill = last_close * (1.0 - impact)
    exit_notional = quantity * sell_fill
    exit_fee = exit_notional * fee
    final_equity = exit_notional - exit_fee
    gross_final = quantity * last_close
    equity_curve = []
    for r in rows:
        mark_value = quantity * r["close"]
        equity_curve.append({
            "timestamp_ms": r["timestamp_ms"],
            "flat_equity": format(initial_equity, ".12g"),
            "buy_hold_mark_to_market_gross": format(mark_value, ".12g"),
            "buy_hold_equity_after_entry_costs": format(mark_value - entry_fee, ".12g"),
        })
    report = {
        "status": "PASS",
        "benchmark_only": True,
        "input_rows": len(rows),
        "first_timestamp_ms": rows[0]["timestamp_ms"],
        "last_timestamp_ms": rows[-1]["timestamp_ms"],
        "assumptions": {
            "initial_equity_quote_currency": initial_equity,
            "fee_bps_per_fill": fee_bps,
            "spread_bps_full": spread_bps,
            "slippage_bps_per_fill": slippage_bps,
            "execution_impact": "buy reference*(1 + half_spread + slippage); sell reference*(1 - half_spread - slippage)",
            "buy_hold_entry": "buy at first candle open with all initial capital including entry fee",
            "buy_hold_exit": "liquidate at last candle close including exit impact and fee",
            "funding": "not applicable to Spot benchmark; no Futures funding cash flows are simulated",
            "taxes": "excluded",
        },
        "benchmarks": {
            "flat_no_trade": {
                "initial_equity": initial_equity, "final_equity": initial_equity,
                "net_return_pct": 0.0, "max_drawdown_pct": 0.0, "trades": 0,
            },
            "spot_buy_and_hold": {
                "quantity_btc": quantity,
                "entry_reference_price": first_open,
                "entry_fill_price": buy_fill,
                "entry_fee_quote": entry_fee,
                "exit_reference_price": last_close,
                "exit_fill_price": sell_fill,
                "exit_fee_quote": exit_fee,
                "gross_final_value_before_exit_costs": gross_final,
                "final_equity_after_entry_and_exit_costs": final_equity,
                "gross_return_pct_before_costs": (gross_final / initial_equity - 1.0) * 100.0,
                "net_return_pct": (final_equity / initial_equity - 1.0) * 100.0,
                "max_drawdown_pct_gross_mark_to_market": max_drawdown([initial_equity] + [quantity * r["close"] for r in rows]) * 100.0,
                "trades": 1,
            },
        },
        "warnings": [
            "Benchmarks are not a strategy recommendation and do not establish future profitability.",
            "Spot buy-and-hold assumes an idealized full fill at the specified impacted price; partial fills and exchange filters are not modeled.",
            "The three-month sample is too short to support robust strategy claims.",
            "Funding and Futures margin/liquidation accounting are intentionally not simulated until event-time semantics and a separate Futures accounting model are validated.",
        ],
    }
    return report, equity_curve


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Normalized btc-usdt-5m-aligned.csv")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--initial-equity", type=float, required=True)
    parser.add_argument("--fee-bps", type=float, required=True, help="Fee per fill in basis points")
    parser.add_argument("--spread-bps", type=float, required=True, help="Full quoted spread in basis points")
    parser.add_argument("--slippage-bps", type=float, required=True, help="Slippage per fill in basis points")
    args = parser.parse_args()
    input_path = Path(args.input)
    rows = load_spot_rows(input_path)
    report, curve = run_benchmarks(rows, args.initial_equity, args.fee_bps,
                                   args.spread_bps, args.slippage_bps)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    report["input"] = {"file": input_path.name,
                       "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest()}
    (out / "btc-usdt-baseline-backtest-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (out / "btc-usdt-baseline-equity-curve.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(curve[0]))
        writer.writeheader()
        writer.writerows(curve)
    print(json.dumps({"status": report["status"], "input_rows": len(rows),
                      "net_return_pct": report["benchmarks"]["spot_buy_and_hold"]["net_return_pct"],
                      "report": str(out / "btc-usdt-baseline-backtest-report.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
