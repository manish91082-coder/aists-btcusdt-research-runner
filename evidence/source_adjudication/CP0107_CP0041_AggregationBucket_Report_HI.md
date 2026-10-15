# CP-0107: CP-0041 residual aggregation bucket overlay

Status: PASS_AGGREGATION_BUCKET_DAILY_SOURCE_REVIEW; checks 12/12 PASS.

## Evidence scope

- 11 residual aggregation buckets were read from a committed snapshot linked to CP-0041 package SHA-256 23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc and member SHA-256 aba8bfeca2ea62f576075faf926e4c425c862d50428cd59732ab9db88a64442a.
- Daily/monthly source rows were joined only by exact interval, UTC date and open-time key from the already-verified CP-0107 acquisition run. No downloads occurred in this task.
- The overlay recomputes child OHLCV, quote volume, trade count and taker-buy sums for monthly and daily source rows, comparing them with the corresponding parent row.

## Diagnostic results

- Buckets reviewed: 11; raw source-row links: 78.
- Daily roll-up statuses: {"DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT": 11}.
- Frozen monthly primary-mismatch signature reproduced from the row-level comparison: 11/11. Exact numeric child-volume sum equality with frozen aggregate text: 10/11. Differences are exposed per bucket rather than normalized.

## Disposition

All 11 buckets remain UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT. Suggested dispositions are review-only. No canonical source selected; no cases closed; no raw archive or timestamp changes; no synthetic candles, backtest rerun or strategy promotion.
