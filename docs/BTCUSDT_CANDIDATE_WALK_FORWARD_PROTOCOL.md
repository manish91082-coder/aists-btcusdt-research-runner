# BTCUSDT Candidate Baselines: Preregistered Walk-Forward Protocol

**Version:** 1.0  
**Created:** 2026-10-23  
**Status:** Protocol locked for research execution; no candidate is selected  
**Scope:** BTCUSDT Spot candidate baselines first; Futures is a separate later gate  
**Research target:** 1,000 USDT toward 1,061,120.54 USDT, without any return guarantee or time-to-target claim

## 1. Why this protocol exists

The initial SMA 12/48 and mean-reversion z48 candidates were run on July-September 2026 and both lost substantially under illustrative costs. That sample is now a development sample, not an untouched holdout. Do not relabel it as out-of-sample, and do not tune parameters to improve those reported numbers.

## 2. Frozen candidate definitions

1. **Trend:** Spot long/flat. At a completed candle close, desired position is long when trailing SMA(12) is strictly greater than SMA(48), otherwise cash. Execute the decision at the next candle open.
2. **Mean reversion:** Spot long/flat. Calculate z-score from the trailing 48 completed closes using the population standard deviation. Enter long at z <= -1.5; while long, remain long only while z < 0, otherwise return to cash. Execute at the next candle open.
3. **No trade:** Keep all starting quote-currency equity in cash.
4. **Buy and hold:** Buy at the first eligible open and liquidate at the evaluation window's last close.

No short positions, leverage, parameter optimization, or AI selection in this phase. Any change to these rules creates a new experiment version and must not overwrite this record.

## 3. Data acquisition and split policy

The current validated aligned sample covers July-September 2026 only. A source-availability inventory is not a substitute for downloading and validating monthly archive content. Before the historical walk-forward run:

- Acquire official monthly BTCUSDT Spot and USDⓈ-M Futures 5-minute archives and the applicable funding archives for January 2020 through September 2026.
- Validate each downloaded archive using the source checksum sidecar, ZIP CRC, schema, expected row count, UTC grid, timestamp boundaries, duplicates, missing intervals, numeric fields, OHLC consistency, and funding schema. Keep raw archives and normalized outputs separate.
- Fail closed on missing months or unexpected gaps. Do not silently forward-fill missing candles. Publish an explicit coverage manifest.
- The July-September 2026 sample is already inspected and remains a **development / implementation-check sample**. It must not be called the final holdout.

Chronological development schedule after monthly history passes validation:

| Segment | Period | Permitted use |
|---|---|---|
| Initial training | 2020-01 through 2022-12 | Implement and inspect accounting; no future observations |
| Validation | 2023-01 through 2024-12 | Compare frozen candidates and validate metric calculation |
| Historical test | 2025-01 through 2025-12 | Report once after all rules and cost assumptions are frozen |
| Development / recent-regime diagnostic | 2026-01 through 2026-09 | Diagnostic only; includes the already-inspected Jul-Sep sample |
| Forward holdout | From 2026-10-24 onward | Untouched, chronological paper/research evaluation; do not tune against these results |

The 2025 historical test is chronologically later than training and validation, but repeated inspection still consumes it. If its results drive rule changes, it becomes development data and a later forward holdout is required. The only holdout that remains untouched by the current July-September run is the future forward period.

## 4. Walk-forward mechanics

- Use an expanding-window walk-forward: fit/initialize only on data available before each test month, then evaluate the next calendar month. The candidate rules in this version have fixed parameters, so "fit" means computing indicators from past candles, not fitting a model.
- At each window boundary, reset equity to the predeclared 1,000 USDT for comparable per-window metrics, and also report a stitched sequential-equity view only if compounding is explicitly simulated without resetting positions or using future information.
- Signals are computed from completed candles. The earliest permitted execution is the next candle open.
- At each test window end, liquidate any open Spot position with the same modeled execution costs and include the liquidation in final equity.
- Never let indicator windows consume data from the future side of a boundary. Warm-up candles may come from the preceding training history, but PnL is scored only inside the test window.
- Report each month separately and the aggregate across all test windows. Do not hide weak months behind the aggregate.

## 5. Cost scenarios

Base assumptions remain illustrative and fixed for the first comparison:

- Fee: 10 basis points per fill.
- Full spread: 2 basis points.
- Slippage: 5 basis points per fill.

Run independent sensitivity cases at 0.5x, 1.0x, 1.5x and 2.0x each of those assumptions. A zero-cost run may be reported only as an upper-bound diagnostic, never as the headline result. These assumptions are not a verified user/account fee schedule.

## 6. Required metrics and comparators

For each candidate, month, aggregate window, and cost scenario report:

- Gross and net return, initial/final equity, maximum drawdown, and exposure fraction.
- Fill count, round trips, turnover, fees paid, modeled spread/slippage costs, and realized final liquidation costs.
- Buy-and-hold and no-trade results on the identical timestamps and cost assumptions where applicable.
- Month-by-month distribution, worst month, and whether results remain positive under increased costs.
- Input dataset hash, source archive hashes, code commit, rule version, cost configuration, start/end timestamps, and machine-readable report.

No candidate advances based on return alone. Drawdown, turnover, cost sensitivity, and month-level stability must be reviewed together. Do not calculate a time-to-target estimate unless a robust out-of-sample net edge and risk model are established.

## 7. Exit criteria

This gate passes only when:

1. Every required monthly archive is content-validated or explicitly marked unavailable, with no silent gap-filling.
2. Unit tests prove next-open execution, prefix-only signals, boundary isolation, cost accounting, and final-equity reconciliation.
3. Walk-forward outputs are reproducible from the recorded commit, dataset hashes, and frozen configuration.
4. Baselines and all cost scenarios are reported, including losses and negative months.
5. The forward holdout remains untouched by tuning and is logged separately.

Passing this protocol or producing a green CI run does not establish profitability. No live exchange orders, API secrets, or funds movement are part of this phase.
