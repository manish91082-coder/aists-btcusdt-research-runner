# CP-0118: Daily and monthly internal parent-child rollup audit

Status: PASS_MONTHLY_PARENT_CHILD_INTERNAL_ROLLUP_AUDIT_SOURCE_AUTHORITY_OPEN

- Frozen CP-0107 RowEvidence was grouped by exact blocker case and source. Decimal arithmetic was used for economic numeric fields and integer arithmetic for trade count; no source data was changed.
- Daily rows reconcile internally: all 11/11 parent candles reproduce the child-rollup OHLC, volume, quote volume, trade count and taker-buy metrics across all nine fields.
- Monthly rows do not reconcile internally: 0/11 parent rows match all nine metrics rolled up from the monthly child rows. There are 58 per-case field-mismatch memberships over the 11 buckets; these memberships overlap and are not the CP-0113 deduplicated 97-field total.
- Volume, quote_asset_volume and number_of_trades mismatch in all 11 monthly buckets. Taker-buy base/quote fields each mismatch in 8/11 and 8/11. Individual OHLC field frequencies are in the summary.
- CP-0112 showed 35/35 daily bars and 315/315 daily fields match verified trade reconstruction, while the monthly rows match 21/35 bars and 218/315 fields. CP-0118 independently establishes an exact arithmetic failure inside the stored monthly parent-child relationships for every frozen bucket.
- This localizes the observed inconsistency to the current monthly archive's own parent-child row relationship in these exact windows. It does not prove whether the cause is historical revision, publication/version skew, processing differences or another root cause; provenance stays open.

| Case | Child -> parent | Daily rollup | Monthly rollup | Monthly mismatches | Child volume sum | Parent volume | Child trades sum | Parent trades |
|---|---|---|---|---|---:|---:|---:|---:|
| AGG-01-5m-15m-2017-12-04T09:00:00Z | 5m -> 15m | 9/9 | 2/9 | low;close;volume;quote_asset_volume;number_of_trades;taker_buy_base_asset_volume;taker_buy_quote_asset_volume | 5.55522600 | 13.00336300 | 46 | 106 |
| AGG-02-5m-15m-2017-12-04T09:15:00Z | 5m -> 15m | 9/9 | 2/9 | open;high;volume;quote_asset_volume;number_of_trades;taker_buy_base_asset_volume;taker_buy_quote_asset_volume | 9.12557700 | 14.26337200 | 101 | 237 |
| AGG-03-5m-15m-2018-02-05T10:00:00Z | 5m -> 15m | 9/9 | 6/9 | volume;quote_asset_volume;number_of_trades | 242.19697100 | 243.06506800 | 2859 | 2891 |
| AGG-04-5m-15m-2018-03-04T14:30:00Z | 5m -> 15m | 9/9 | 2/9 | high;low;volume;quote_asset_volume;number_of_trades;taker_buy_base_asset_volume;taker_buy_quote_asset_volume | 21.24696600 | 43.22829200 | 411 | 659 |
| AGG-05-5m-15m-2018-03-04T14:45:00Z | 5m -> 15m | 9/9 | 1/9 | open;high;low;volume;quote_asset_volume;number_of_trades;taker_buy_base_asset_volume;taker_buy_quote_asset_volume | 40.85844400 | 140.41819800 | 423 | 1512 |
| AGG-06-5m-15m-2018-09-05T09:45:00Z | 5m -> 15m | 9/9 | 4/9 | volume;quote_asset_volume;number_of_trades;taker_buy_base_asset_volume;taker_buy_quote_asset_volume | 3381.68797900 | 3397.27107400 | 15486 | 15587 |
| AGG-07-15m-30m-2017-12-04T09:00:00Z | 15m -> 30m | 9/9 | 4/9 | volume;quote_asset_volume;number_of_trades;taker_buy_base_asset_volume;taker_buy_quote_asset_volume | 27.26673500 | 55.98498500 | 343 | 526 |
| AGG-08-15m-30m-2018-02-07T06:30:00Z | 15m -> 30m | 9/9 | 6/9 | volume;quote_asset_volume;number_of_trades | 679.18968500 | 679.96609600 | 6481 | 6503 |
| AGG-09-15m-30m-2018-03-04T14:30:00Z | 15m -> 30m | 9/9 | 4/9 | volume;quote_asset_volume;number_of_trades;taker_buy_base_asset_volume;taker_buy_quote_asset_volume | 183.64649000 | 209.50825600 | 2171 | 2448 |
| AGG-10-15m-30m-2018-06-20T03:30:00Z | 15m -> 30m | 9/9 | 6/9 | volume;quote_asset_volume;number_of_trades | 279.26867100 | 285.74902900 | 2277 | 2292 |
| AGG-11-30m-1h-2018-03-20T03:00:00Z | 30m -> 1h | 9/9 | 4/9 | volume;quote_asset_volume;number_of_trades;taker_buy_base_asset_volume;taker_buy_quote_asset_volume | 1916.02266500 | 1917.75233400 | 11745 | 11760 |

## Interpretation boundary

The audit proves arithmetic inconsistency between each current monthly parent row and the nine-field rollup of its own current monthly child rows for these 11 windows. It does not prove a historical version timeline or explain the cause. Current official checksum sidecars authenticate the current bytes, not the byte version available at historical decision time. Do not infer global daily-over-monthly precedence.

## Disposition and gates

- Keep all 11 non-row blockers open; canonical source NONE; source cases closed 0.
- G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G7 LIVE_BLOCKED.
- No network/archive downloads, source mutation, timestamp shifts/rounding, synthetic source candles, production candidate build, backtest, strategy promotion, signing, broadcast or orders.

## Next bounded step

Compare these exact monthly internal mismatches with any dated correction/version evidence tied to the exact daily and monthly archive hashes. Until rulebook-accepted source adjudication or a formally frozen conservative quarantine policy with actual candidate-specific final metrics exists, keep all 11 blockers open.
