# AISTS Corrected Full Pipeline Run: 38725478106

## Execution identity
- Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38725478106
- Request ID: `AISTS-LEGACY-PIPELINE-20261015-04`
- Trigger commit: `4375cf750b3c3beb01969a48d29af0a447874b22`
- Workflow: **success**. CP-0023, CP-0024, CP-0025, CP-0026, CP-0027 all exited 0; 212.41 seconds.
- Artifact ID: 11967997123; 831,616 bytes; SHA-256 `5a9b5486615571a7321b70dc4e9736a45bffad4faa5d6a5a032ae443b3dbc54f`; ZIP CRC PASS; 28 members; 7-day retention.
- This record was created after downloading the artifact and verifying its SHA-256 equals GitHub's digest and its ZIP CRC passes.

## Source lineage correction
The corrected sequence is CP-0023 → CP-0024 → CP-0025 → CP-0026 → CP-0027. CP-0025 discovers flagged dates from CP-0023 gap reports and CP-0024 strict anomaly/reconciliation reports. The prior run 38723688606 omitted those prerequisites and found 34 dates; that output is superseded for date discovery only and is kept as immutable historical evidence.

## Official archive checks
- Expected monthly ZIP/checksum pairs: 770.
- Official checksum + ZIP CRC/member inventory passed: 765.
- Five direct monthly `1mo` ZIPs returned 404: 2024-03, 2026-03, 2026-07, 2026-08, 2026-09.
- Other archive acquisition errors: 0.
- CP-0023 checksum verification: 765/765 MATCH. A checksum match proves byte integrity against the official sidecar, not economic completeness/correctness.
- CP-0023 raw interval audit: 5m 957,865 rows / 33 gaps / 1 anomaly; 15m 319,294 / 32 / 1; 30m 159,653 / 31 / 1; 1h 79,837 / 28 / 1; 4h 19,974 / 9 / 0; 1d 3,332 / 0 / 0; native 1mo 105 rows / 0 / 0.
- CP-0024: 82 exact close-time-boundary flags; 450 off-grid opens; 0 OHLC/parse anomalies; 0 invalid ZIP archives. Its 54 checksum-verified daily references revealed 41 value mismatches and 7 monthly-only rows.

## CP-0025 exact frozen counts restored
- Flagged dates: **40**; the permanent date set is in `38725478106_flagged_dates.csv`.
- Daily references: 240/240 checksum matches, zero download/checksum/read errors.
- Exact row matches: 15,319.
- Value mismatches: 60.
- Daily-only rows: 452.
- Monthly-only rows: 457.
- Unmatched rows remain OPEN: 909.
- Gate: `INVESTIGATE_BEFORE_BACKTEST`; auto-corrections 0.

## CP-0026 provisional candidate quality
Gate: `PROVISIONAL_CANDIDATE_BUILT_GAPS_RECORDED`. All seven candidate series passed structural checks for grid alignment, OHLC, duplicates and ordering. Gaps were recorded, never filled:
| Interval | Rows | Gap events | Estimated missing bars | Close-time normalized |
|---|---:|---:|---:|---:|
| 5m | 957,861 | 33 | 1,707 | 16 |
| 15m | 319,293 | 32 | 563 | 15 |
| 30m | 159,653 | 30 | 275 | 15 |
| 1h | 79,836 | 28 | 128 | 14 |
| 4h | 19,975 | 8 | 16 | 21 |
| 1d | 3,332 | 0 | 0 | 1 |
| 1mo | 110 | 0 | 0 | n/a |

The 1mo series is derived from the CP-0026 candidate 1d series; CP-0027 excludes the initial partial Aug-2017 month, leaving 109 monthly bars in its backtest.

## CP-0027 baseline result
- Original vendored CP-0027 engine completed: 105 base metric rows, 56 OOS slippage sensitivity rows.
- Fee assumption: 10 bps per side; default slippage: 5 bps per side.
- Important: engine assumes 10,000 USDT initial equity, not the user's ₹10,000 INR planning baseline. Compare percentages, not absolute cash amounts.
- The 2025-01-01 to 2026-10-01 OOS window has already been consumed; it is not an untouched holdout.

Selected OOS returns, max drawdown and closed trades:
| Interval | Strategy | Return | Max DD | Trades |
|---|---|---:|---:|---:|
| 5m | EMA_12_26 | -100.00% | -100.00% | 3,348 |
| 5m | RSI14_30_55 | -96.31% | -96.37% | 1,105 |
| 5m | DONCHIAN20_10 | -99.99% | -99.99% | 3,010 |
| 15m | EMA_12_26 | -95.68% | -96.00% | 1,095 |
| 15m | RSI14_30_55 | -70.47% | -72.47% | 369 |
| 15m | DONCHIAN20_10 | -97.22% | -97.27% | 980 |
| 30m | EMA_12_26 | -77.22% | -81.50% | 541 |
| 30m | RSI14_30_55 | -54.42% | -60.08% | 184 |
| 30m | DONCHIAN20_10 | -70.63% | -75.94% | 454 |
| 1h | EMA_12_26 | -64.53% | -73.09% | 271 |
| 1h | RSI14_30_55 | -19.84% | -42.05% | 107 |
| 1h | DONCHIAN20_10 | -52.95% | -63.04% | 229 |
| 4h | EMA_12_26 | -46.33% | -58.24% | 77 |
| 4h | RSI14_30_55 | +0.63% | -37.51% | 27 |
| 4h | DONCHIAN20_10 | -24.85% | -39.56% | 55 |
| 1d | EMA_12_26 | +2.52% | -32.27% | 13 |
| 1d | RSI14_30_55 | -13.84% | -27.54% | 4 |
| 1d | DONCHIAN20_10 | -17.25% | -38.33% | 11 |
| 1mo | EMA_12_26 | -18.60% | -49.36% | 1 |
| 1mo | RSI14_30_55 | 0.00% | 0.00% | 0 |
| 1mo | DONCHIAN20_10 | -42.32% | -42.32% | 1 |

## Decision and next task
**No strategy is promoted.** A small positive return is insufficient: 4h RSI returned +0.63% with -37.51% drawdown and 27 trades; 1d EMA returned +2.52% with -32.27% drawdown and 13 trades. Both fail the frozen risk/trade-count rules. The 1mo RSI result is a no-trade result, not profitability evidence. Most 5m–1h results show severe losses.

- 60 mismatch rows remain OPEN; 909 unmatched rows remain OPEN/quarantined.
- No canonical source was selected; no raw archives were modified or auto-repaired.
- No Binance REST market-data API, exchange credentials, orders, signing or live actions occurred.
- Next work: build an adjudication report for the 60 exact value mismatches and 909 unmatched rows, compare their source keys/hashes to the frozen CP-0040 rules, and decide source dispositions. Do not repeat the acquisition or baseline backtest unless an adjudicated candidate's bytes change.
