#!/usr/bin/env python3
"""Deterministic long/flat candidate baselines with next-open execution.

Research only. Signals use completed prior candles; orders are filled at the
next candle open with explicit half-spread, slippage, and fee assumptions.
No Futures, leverage, partial fills, or live exchange interaction.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    rows = []
    previous = None
    for row in source:
        try:
            ts = int(row["open_time_ms"])
            op = float(row["spot_open"])
            close = float(row["spot_close"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid timestamp/open/close row: {row}") from exc
        if previous is not None and ts <= previous:
            raise ValueError("timestamps must be strictly increasing and unique")
        if not all(math.isfinite(p) and p > 0 for p in (op, close)):
            raise ValueError(f"prices must be finite and positive at {ts}")
        rows.append({"timestamp_ms": ts, "open": op, "close": close})
        previous = ts
    if len(rows) < 60:
        raise ValueError("at least 60 rows are required for deterministic candidate baselines")
    return rows


def max_drawdown(values: list[float]) -> float:
    peak = 0.0
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, value / peak - 1.0)
    return worst


def sma(values: list[float], end: int, window: int) -> float:
    return sum(values[end - window + 1:end + 1]) / window


def desired_positions(closes: list[float]) -> dict[str, list[int]]:
    n = len(closes)
    trend = [0] * n
    meanrev = [0] * n
    # At candle i's close, calculate a desired position for candle i+1 open.
    fast, slow = 12, 48
    for i in range(slow - 1, n):
        trend[i] = int(sma(closes, i, fast) > sma(closes, i, slow))
    # Mean reversion uses only the trailing 48 completed closes. Enter when
    # price is <= 1.5 population standard deviations below the trailing mean;
    # exit when z-score returns to >= 0. No shorting.
    window = 48
    for i in range(window - 1, n):
        sample = closes[i - window + 1:i + 1]
        mean = sum(sample) / window
        variance = sum((x - mean) ** 2 for x in sample) / window
        sd = math.sqrt(variance)
        z = (closes[i] - mean) / sd if sd > 0 else 0.0
        if meanrev[i - 1] == 1:
            meanrev[i] = int(z < 0.0)
        else:
            meanrev[i] = int(z <= -1.5)
    return {"trend_sma_12_48": trend, "mean_reversion_z48": meanrev}


def simulate(rows: list[dict], signals: list[int], initial_equity: float,
             fee_bps: float, spread_bps: float, slippage_bps: float) -> tuple[dict, list[dict]]:
    fee_rate = fee_bps / 10000.0
    impact = (spread_bps / 2.0 + slippage_bps) / 10000.0
    cash = initial_equity
    quantity = 0.0
    fees_paid = 0.0
    turnover = 0.0
    trades = 0
    curve = []
    equity_values = []
    position = 0
    for i, row in enumerate(rows):
        # The signal is taken from the prior completed candle, never this
        # candle's close. First candle is cash-only.
        target = signals[i - 1] if i > 0 else 0
        reference = row["open"]
        if target != position:
            if target == 1:
                fill = reference * (1.0 + impact)
                qty = cash / (fill * (1.0 + fee_rate))
                notional = qty * fill
                fee = notional * fee_rate
                cash -= notional + fee
                quantity = qty
                fees_paid += fee
                turnover += notional
                trades += 1
                position = 1
            else:
                fill = reference * (1.0 - impact)
                notional = quantity * fill
                fee = notional * fee_rate
                cash += notional - fee
                fees_paid += fee
                turnover += notional
                quantity = 0.0
                trades += 1
                position = 0
        # The final curve point is recorded after a costed liquidation so
        # its equity matches the realized final equity in the report.
        if i == len(rows) - 1 and position == 1:
            fill = row["close"] * (1.0 - impact)
            notional = quantity * fill
            fee = notional * fee_rate
            cash += notional - fee
            fees_paid += fee
            turnover += notional
            trades += 1
            quantity = 0.0
            position = 0
        equity = cash + quantity * row["close"]
        if not math.isfinite(equity) or equity < -1e-8:
            raise ValueError("equity became non-finite or negative")
        equity = max(0.0, equity)
        equity_values.append(equity)
        curve.append({
            "timestamp_ms": row["timestamp_ms"],
            "equity": format(equity, ".12g"),
            "position_long": position,
            "close": format(row["close"], ".12g"),
        })
    final_equity = cash
    report = {
        "status": "PASS",
        "benchmark_only": True,
        "input_rows": len(rows),
        "first_timestamp_ms": rows[0]["timestamp_ms"],
        "last_timestamp_ms": rows[-1]["timestamp_ms"],
        "initial_equity": initial_equity,
        "final_equity_after_final_liquidation": final_equity,
        "net_return_pct": (final_equity / initial_equity - 1.0) * 100.0,
        "max_drawdown_pct_mark_to_market": max_drawdown(equity_values) * 100.0,
        "fills": trades,
        "total_fees_quote": fees_paid,
        "turnover_quote": turnover,
        "assumptions": {
            "fee_bps_per_fill": fee_bps,
            "full_spread_bps": spread_bps,
            "slippage_bps_per_fill": slippage_bps,
            "execution": "next candle open for signals from prior completed candle; final liquidation at last close",
            "position": "long/flat only; all available equity allocated when long",
            "funding": "not applicable; Spot only",
            "taxes": "excluded",
        },
    }
    return report, curve


def run(rows: list[dict], initial_equity: float, fee_bps: float,
        spread_bps: float, slippage_bps: float) -> tuple[dict, list[dict]]:
    for name, value in (("initial_equity", initial_equity), ("fee_bps", fee_bps),
                        ("spread_bps", spread_bps), ("slippage_bps", slippage_bps)):
        if not math.isfinite(value) or (value <= 0 if name == "initial_equity" else value < 0):
            raise ValueError(f"{name} has invalid value")
        if name != "initial_equity" and value >= 10000:
            raise ValueError(f"{name} must be below 10000 bps")
    closes = [r["close"] for r in rows]
    positions = desired_positions(closes)
    reports = {}
    curves = {}
    for name, signal in positions.items():
        reports[name], curves[name] = simulate(
            rows, signal, initial_equity, fee_bps, spread_bps, slippage_bps
        )
    reports["warnings"] = [
        "Candidate baselines are research hypotheses, not recommendations or evidence of future profitability.",
        "The same sample is used for initial implementation checks; no out-of-sample edge is established.",
        "All-in long/flat Spot simulation idealizes fills and excludes partial fills, exchange filters and market impact beyond fixed assumptions.",
    ]
    return reports, curves


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--initial-equity", type=float, default=1000.0)
    parser.add_argument("--fee-bps", type=float, default=10.0)
    parser.add_argument("--spread-bps", type=float, default=2.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    args = parser.parse_args()
    rows = load_rows(args.input)
    reports, curves = run(rows, args.initial_equity, args.fee_bps, args.spread_bps, args.slippage_bps)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "PASS",
        "benchmark_only": True,
        "input_file": args.input.name,
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "input_rows": len(rows),
        "assumptions": {
            "initial_equity_quote_currency": args.initial_equity,
            "fee_bps_per_fill": args.fee_bps,
            "spread_bps_full": args.spread_bps,
            "slippage_bps_per_fill": args.slippage_bps,
        },
        "candidates": reports,
    }
    (args.output_dir / "btc-usdt-candidate-baselines-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for name, curve in curves.items():
        with (args.output_dir / f"{name}-equity-curve.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["timestamp_ms", "equity", "position_long", "close"])
            writer.writeheader()
            writer.writerows(curve)
    print(json.dumps({
        "status": "PASS",
        "input_rows": len(rows),
        "candidates": {name: {
            "net_return_pct": report["net_return_pct"],
            "max_drawdown_pct_mark_to_market": report["max_drawdown_pct_mark_to_market"],
            "fills": report["fills"],
        } for name, report in reports.items() if isinstance(report, dict)},
        "warning": "initial candidate run only; out-of-sample edge not established",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
