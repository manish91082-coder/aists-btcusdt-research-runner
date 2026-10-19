# CP-0256 — 4h OOS Trade-Ledger Risk Diagnostic (Exploratory Only)

- Date: 2026-10-19
- Scope: re-analysis of the already completed CP-0027 baseline trade ledger from workflow run 38725478106. No new market backtest was executed.
- Status: `EXPLORATORY_PROVISIONAL_NOT_ACCEPTANCE_GRADE`
- G0: `BLOCKED_GLOBAL`; canonical source: `NONE`; candidate promotion: `NOT_AUTHORIZED`; profitability: `NOT_ESTABLISHED`.

## Artifact identity and integrity

- Source workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38725478106
- Artifact ID: `11967997123`; artifact name: `aists-run-38725478106-attempt-1`.
- Downloaded outer ZIP SHA-256 verified against the run summary: `5a9b5486615571a7321b70dc4e9736a45bffad4faa5d6a5a032ae443b3dbc54f`; outer ZIP integrity test passed.
- Nested evidence ZIP SHA-256: `08de714ee71c2e976cecc02fe0938f8d8eb8d7a4d064d812a51f0560acbe8d42`; integrity test passed.
- OOS trade ledger: `cp0027/oos_trades_5bps.csv.gz`; SHA-256 `ed79deef5997d38199496acbf00f152a5e95cdd28edbe96d0c861bdeca305d15`.
- Filter: `interval=4h`, `period=OOS`; OOS dates 2025-01-01 UTC through before 2026-10-01 UTC. This window has already been consumed and is not an untouched holdout.

## Results from existing trade ledger

The ledger's `net_trade_pnl` values were summed by strategy and reconciled to the existing CP-0027 summary metrics. The baseline assumes 10,000 USDT starting equity, 10 bps fee per side and 5 bps slippage per side; actual account fees/BNB discount and execution are not verified.

| Strategy | Trades | Wins / losses | Net trade P&L (USDT) | Profit factor | Average win (USDT) | Average loss (USDT) | Worst trade (USDT) |
|---|---:|---:|---:|---:|---:|---:|---:|
| EMA_12_26 | 77 | 19 / 58 | -4,632.87 | 0.5722 | 326.15 | -186.72 | -1,036.74 |
| RSI14_30_55 | 27 | 19 / 8 | +62.68 | 1.0085 | 391.20 | -921.26 | -2,376.78 |
| DONCHIAN20_10 | 55 | 20 / 35 | -2,484.99 | 0.7015 | 291.99 | -237.85 | -519.12 |

## Decision-changing interpretation

1. The 4h RSI baseline's small positive net P&L is fragile in this already-used OOS window: profit factor is only 1.0085, and its worst recorded trade is approximately 23.77% of the assumed initial 10,000 USDT. This is consistent with the already-reported +0.63% return and -37.51% maximum drawdown; it is not a risk-adjusted acceptance.
2. EMA and Donchian are materially negative in this baseline under its assumed fees/slippage.
3. A high win rate alone is not sufficient: RSI has 19 wins out of 27 but eight losses aggregate to about -7,370.05 USDT against about +7,432.73 USDT in winning-trade P&L.
4. These are descriptive diagnostics of a provisional, disputed-source candidate. They do not validate source authority, fix gap valuation, establish independent out-of-sample performance, or justify parameter tuning against the consumed OOS window.

## Boundary and next action

- No raw candle was changed or synthesized; no new backtest or strategy optimization was run.
- No stop-loss/take-profit rule was added or inferred.
- No candidate was promoted; no live signing, broadcast, or exchange orders occurred.
- This diagnostic does not resolve G0. The immediate G0 blocker remains an authorized independent adjudication or genuinely new, admissible key-specific historical-version provenance. Do not repeat archive scans or treat this analysis as a substitute for that dependency.
