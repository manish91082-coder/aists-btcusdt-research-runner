# CP-0113: Field-level trade corroboration and source-disposition audit
**Date:** 2026-10-16
**Status:** `PASS_FIELD_LEVEL_CROSSWALK_SOURCE_AUTHORITY_OPEN`
**Scope:** exact join over frozen CP-0107 RowEvidence and CP-0112 trade-derived results. No source selection or case closure.

## 1. Execution evidence
- GitHub Actions run: [38939841877](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38939841877)
- Executed commit: `6af3b705bb0344e4b20e18ec90f533c104b1c6bd`
- Workflow conclusion: `success`; runner status `PASS`, 11/11 checks PASS.
- Child status: `PASS_FIELD_LEVEL_CROSSWALK_SOURCE_AUTHORITY_OPEN`.
- Child summary SHA-256: `b20e30d6a631ca2ac6e9caf5c30c3abd9353d865189e5bf55b782b393992e588`.
- Actions artifact: [12062382111](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38939841877/artifacts/12062382111), 23,043 bytes, ZIP SHA-256 `88213c8b1f9e753a289c3a0cf10702e23d6bf3b76db1f9ab8146b1a31043a8f7`, seven-day retention.

## 2. Frozen source identity and integrity reconciliation
- CP-0040 rulebook SHA-256 was verified before the audit: `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
- CP-0107 RowEvidence: 78 records; daily and monthly contexts each deduplicate to 35 unique `(interval, open_time_ms)` rows. Four repeated daily and four repeated monthly contexts were consistent; conflicting duplicate rows: 0.
- Exact official daily kline archive manifest: 16/16 records pass HTTP 200, ZIP CRC, `.CHECKSUM` token-to-ZIP SHA-256 linkage and the committed row-evidence archive-hash join.
- Exact official monthly kline archive set: 14/14 records pass HTTP 200, ZIP CRC, exact checksum sidecar filename, official checksum token to cached ZIP SHA-256, and row-evidence archive-hash join.
- Coverage of the 35 target `(interval, open_time_ms)` keys in both source sides: 35/35; missing daily/monthly rows: 0/0. Raw `open_time` and `close_time` match the exact expected boundaries for every row.
- CP-0112 pointer and its linked report blob SHA-1 were re-verified; the CP-0112 reconstructed result is 35/35 daily bars, 315/315 daily fields, 21/35 monthly bars, 218/315 monthly fields and 11/11 parent-child rollups.

## 3. Deduplicated result
| Measure | Verified result |
|---|---:|
| Unique candle keys in scope | 35 |
| Economic metric fields per key | 9 |
| Daily values matching trade-derived reconstruction | 315/315 fields |
| Monthly values matching daily/trade-derived values | 218/315 fields |
| Exact monthly-divergent keys | 14 |
| Monthly-divergent fields | 97 |
| Boundary issues | 0 |
| Conflicting duplicate evidence rows | 0 |
| Source cases closed by CP-0113 | 0 |

## 4. Exact monthly-divergent keys

| Interval | Open time (UTC) | Different fields | Fields |
|---|---|---:|---|
| 15m | 2017-12-04T09:00:00.000Z | 7 | `high; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 5m | 2017-12-04T09:05:00.000Z | 7 | `low; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 5m | 2017-12-04T09:10:00.000Z | 8 | `open; high; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 5m | 2017-12-04T09:15:00.000Z | 9 | `open; high; low; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 5m | 2018-02-05T10:05:00.000Z | 4 | `close; volume; quote_asset_volume; number_of_trades` |
| 15m | 2018-02-07T06:30:00.000Z | 4 | `close; volume; quote_asset_volume; number_of_trades` |
| 15m | 2018-03-04T14:30:00.000Z | 7 | `low; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 5m | 2018-03-04T14:35:00.000Z | 8 | `high; low; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 5m | 2018-03-04T14:40:00.000Z | 8 | `high; low; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 5m | 2018-03-04T14:45:00.000Z | 9 | `open; high; low; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 5m | 2018-03-04T14:50:00.000Z | 9 | `open; high; low; close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 30m | 2018-03-20T03:00:00.000Z | 6 | `close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |
| 15m | 2018-06-20T03:30:00.000Z | 5 | `low; close; volume; quote_asset_volume; number_of_trades` |
| 5m | 2018-09-05T09:50:00.000Z | 6 | `close; volume; quote_asset_volume; number_of_trades; taker_buy_base_asset_volume; taker_buy_quote_asset_volume` |

The complete CSV values, including daily/monthly archive filenames and SHA-256 identities for every key and raw field, are in the workflow artifact.

## 5. Disposition under frozen CP-0040
The bounded evidence supports this exact-scope finding: on the 35 target keys, the daily kline row metrics are corroborated field-for-field by the current checksum-verified Spot trade-stream reconstruction. Fourteen monthly rows diverge on 97 fields, and monthly ZIP identity, ZIP CRC and official `.CHECKSUM` tokens were also verified. This is stronger independent corroboration of the daily values for these keys, but it is not proof of the historical version timeline or a rule that daily data universally outranks monthly data.

CP-0040 requires unresolved signal-affecting source items to remain `UNRESOLVED` unless they are adjudicated or isolated under an accepted conservative quarantine. The rulebook has no mechanical daily-over-monthly precedence rule. Therefore CP-0113 proposes the bounded field label `DAILY_TRADE_CORROBORATED_MONTHLY_FIELDS_CONFLICT`, not final canonical-source authority.

**Final authority remains open:** canonical source `NONE`; historical archive-version provenance `OPEN_NOT_ESTABLISHED`; 11 aggregation blockers still open; source cases closed `0`. G0 remains `BLOCKED_GLOBAL`, G2 remains `FAIL_CURRENT_23_CANDIDATES`, and G7 remains `LIVE_BLOCKED`.

## 6. Output checksums from the run artifact
| Output | Bytes | SHA-256 |
|---|---:|---|
| `CP0113_FieldLevel_Trade_Corroboration_Crosswalk.csv` | 20,132 | `1e5ba8e8dc380eef4cc597102ed77ccc1ce768989c076504b78bc43ae298ec80` |
| `CP0113_Monthly_FieldMismatch_Detail.csv` | 27,913 | `221e456e5eaee33f3e49e112efa177b411cbb8702a3d048c57a36f12cca1ad6e` |
| `CP0113_FieldLevel_Trade_Corroboration_Report_HI.md` | 5,035 | `3d9382c6fbaeae57a6d71e229df4dcf72cac377a83f13e4da6f21c5e9b04b557` |

## 7. Non-actions
- No raw monthly or daily kline archives edited, replaced, or normalized.
- No Binance market-data REST API, no exchange credentials, no live signing/broadcast/orders.
- No timestamp shift/rounding, synthetic research candle, candidate build, backtest, or strategy promotion.
- All 11 aggregation blockers remain unresolved; no source cases closed.

## 8. Next bounded step
Review the 14 exact keys with the G0 candidate-input/quarantine dependency map. Determine which keys can influence the current candidates and whether the already accepted conservative quarantine policy fully isolates those inputs. Do not change source bytes and do not create a new daily-over-monthly precedence rule.
