# CP-0112: Trade-derived reconstruction of the 11 residual aggregation buckets
**Date:** 2026-10-16
**Status:** `PASS_TRADE_DERIVED_RECONSTRUCTION_COMPLETE_SOURCE_AUTHORITY_OPEN`
**Interpretation:** reconstruction checks passed; source authority remains open. This is not a source-selection or gate-closure checkpoint.

## 1. Execution and reproducibility
- Repository: `manish91082-coder/aists-btcusdt-research-runner`.
- GitHub Actions run: [38938706562](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38938706562), commit `60e8de9cd48412ff77f48dba37cef759fe5040a1`; conclusion `success`.
- Runner: `PASS`, 11/11 runner checks PASS. All 42 Python source files parsed successfully; workflow least-privilege check passed.
- Child summary SHA-256: `bed68b20f220d1618b4ffadf685a75b30ae8e21b088dfd854cd47ce74eaee96b`.
- Run artifact: [12061434560](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38938706562/artifacts/12061434560), ZIP SHA-256 `526b9fe75c96c7e874d81009713a99a7445fbfd03337c98463917d953db16411`, seven-day retention.
- Frozen inputs reused unchanged: CP-0107 RowEvidence CSV Git blob SHA-1 `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9` (78 records); bucket snapshot CSV Git blob SHA-1 `6e32188472ab45b43e1b90fe138399818c937277` (11 rows). The task verified the frozen CP-0040 rulebook SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0` before doing any reconstruction.

## 2. Core findings
- Seven official Spot daily-trades ZIPs fetched over HTTPS from `data.binance.vision`; all seven current `.CHECKSUM` tokens matched the downloaded ZIP SHA-256. All archives passed ZIP CRC, expected member/schema checks, and their trade timestamps were within the stated UTC day.
- Total trade rows parsed: **2,022,142** across seven complete-day files; invalid trade rows `0`; rows outside target UTC day `0`; per-file trade-ID gaps `0`, duplicate IDs `0`, decreasing IDs `0`, timestamp decreases `0`.
- Exact target candle keys reconstructed: **35** across child and parent intervals using official raw trade rows and decimal arithmetic. No OHLCV fields were rounded or normalized.
- **Daily source match:** 35/35 unique bars and 315/315 metric fields exactly match the trade-derived reconstruction. Open/close-time boundary anomalies: `0`.
- **Monthly source match:** 21/35 unique bars and 218/315 metric fields match. Monthly source mismatches remain in the same frozen bucket windows.
- **Independent trade-derived parent = child rollup:** 11/11 buckets exact across the reconstructed child-bar metrics.
- No automatic source authority was assigned: canonical source `NONE`; source cases closed `0`; all 11 aggregation blockers remain unresolved.

## 3. Per-archive identity and row coverage

| UTC date | Rows | ZIP bytes | Trade ID first–last | First trade time (ms) | Last trade time (ms) | Actual ZIP SHA-256 = sidecar |
|---|---:|---:|---|---:|---:|---|
| 2017-12-04 | 32232 | 579,516 | 1280142–1312373 | 1512345600631 | 1512431997289 | `8dcd9c1ef08f613ce651002be03d48ece483ecbcd438619f02207de6187cbc6a` |
| 2018-02-05 | 533510 | 8,456,920 | 12929682–13463191 | 1517788802147 | 1517875198645 | `0bc321baf495ea8209f2c2a008cf264cdf52bbe028a2e239030768af93da6040` |
| 2018-02-07 | 514893 | 7,941,071 | 14249188–14764080 | 1517961600653 | 1518047999827 | `799a43b609160ba1360b38b588341aabc6490c13caeb4881857c96d7e79f18eb` |
| 2018-03-04 | 168359 | 2,821,251 | 23793945–23962303 | 1520121600534 | 1520207998432 | `f995aaf33e17d5cb7cce07477bf5728981e2eca425282abf0808f4104c7165f9` |
| 2018-03-20 | 298261 | 5,131,855 | 29004938–29303198 | 1521504000380 | 1521590399645 | `7d53498704d7c7643bd4ed9c588d5458d79d8532c2662629b516d268b61ca7e0` |
| 2018-06-20 | 166074 | 2,924,166 | 52060867–52226940 | 1529452800247 | 1529539199816 | `bc8f8b82ac04a5c75ef4837918230598607067f0255b7e3e02f44a31c2b4c65e` |
| 2018-09-05 | 308813 | 5,556,939 | 68034347–68343159 | 1536105600629 | 1536191999706 | `a8ba4fb4f8088a0ff69861e84d4190fbd281757c427e1b71ad8b3eb26fefa98b` |

All seven records also reported `integrity_status=PASS`, `invalid_rows=0`, `rows_outside_day=0`, and zero trade-ID/timestamp sequence anomalies. First/last times are retained as raw Unix milliseconds to avoid formatting-dependent rounding. Sidecar-body hashes and the detailed per-archive diagnostics are in the workflow artifact and `CP0112_Trade_Archive_Integrity.csv`.

## 4. Bucket-level comparison

| Case | UTC bucket | Child → parent | Daily exact bars / compared | Monthly exact bars / compared | Reconstructed parent vs child rollup |
|---|---|---|---:|---:|---|
| AGG-01 | 2017-12-04 09:00Z | 5m→15m | 4/4 | 1/4 | PASS |
| AGG-02 | 2017-12-04 09:15Z | 5m→15m | 4/4 | 3/4 | PASS |
| AGG-03 | 2018-02-05 10:00Z | 5m→15m | 4/4 | 3/4 | PASS |
| AGG-04 | 2018-03-04 14:30Z | 5m→15m | 4/4 | 1/4 | PASS |
| AGG-05 | 2018-03-04 14:45Z | 5m→15m | 4/4 | 2/4 | PASS |
| AGG-06 | 2018-09-05 09:45Z | 5m→15m | 4/4 | 3/4 | PASS |
| AGG-07 | 2017-12-04 09:00Z | 15m→30m | 3/3 | 2/3 | PASS |
| AGG-08 | 2018-02-07 06:30Z | 15m→30m | 3/3 | 2/3 | PASS |
| AGG-09 | 2018-03-04 14:30Z | 15m→30m | 3/3 | 2/3 | PASS |
| AGG-10 | 2018-06-20 03:30Z | 15m→30m | 3/3 | 2/3 | PASS |
| AGG-11 | 2018-03-20 03:00Z | 30m→1h | 3/3 | 2/3 | PASS |

Bucket-local denominators overlap where a candle is used in more than one bucket. Therefore the per-bucket monthly exact counts in the table must not be summed to produce a unique-bar count. The deduplicated unique-target denominator is 35, with 21 unique monthly matches.

### Frozen monthly mismatch fields still present

| Case | Monthly mismatch fields from trade-derived comparison |
|---|---|
| AGG-01 | `close;high;low;number_of_trades;open;quote_asset_volume;taker_buy_base_asset_volume;taker_buy_quote_asset_volume;volume` |
| AGG-02 | `close;high;low;number_of_trades;open;quote_asset_volume;taker_buy_base_asset_volume;taker_buy_quote_asset_volume;volume` |
| AGG-03 | `close;number_of_trades;quote_asset_volume;volume` |
| AGG-04 | `close;high;low;number_of_trades;quote_asset_volume;taker_buy_base_asset_volume;taker_buy_quote_asset_volume;volume` |
| AGG-05 | `close;high;low;number_of_trades;open;quote_asset_volume;taker_buy_base_asset_volume;taker_buy_quote_asset_volume;volume` |
| AGG-06 | `close;number_of_trades;quote_asset_volume;taker_buy_base_asset_volume;taker_buy_quote_asset_volume;volume` |
| AGG-07 | `close;high;number_of_trades;quote_asset_volume;taker_buy_base_asset_volume;taker_buy_quote_asset_volume;volume` |
| AGG-08 | `close;number_of_trades;quote_asset_volume;volume` |
| AGG-09 | `close;low;number_of_trades;quote_asset_volume;taker_buy_base_asset_volume;taker_buy_quote_asset_volume;volume` |
| AGG-10 | `close;low;number_of_trades;quote_asset_volume;volume` |
| AGG-11 | `close;number_of_trades;quote_asset_volume;taker_buy_base_asset_volume;taker_buy_quote_asset_volume;volume` |

These are field-level diagnostic mismatches against the preserved row evidence. They do not, by themselves, establish historical version provenance or prove which side was originally published at an earlier point in time.

## 5. Interpretation under the frozen CP-0040 rulebook

The new evidence is stronger than a daily-vs-monthly comparison alone: all 35 target candle records' nine economic metrics match the independently checksum-verified official trade-stream reconstruction on the daily-source side, while the monthly-source side has 14 nonmatching unique bars and 97 nonmatching fields among 315 comparisons. All 11 directly reconstructed parent candles also reconcile to their reconstructed child candles.

**Disposition:** classify the daily values as `CORROBORATED_BY_VERIFIED_TRADE_ARCHIVE` for these exact 35 target keys and the monthly deviations as `CONFLICT_WITH_TRADE_DERIVED_RECONSTRUCTION` for the specific fields listed above. This is a bounded evidence disposition, not a declaration that all daily archives are globally canonical. Historical ZIP version/provenance is still not proven, and the frozen CP-0040 standard remains the authority for any final source-selection or case-closure decision. No case is closed here.

## 6. Artifact outputs and byte hashes

| Output | Bytes | SHA-256 |
|---|---:|---|
| `CP0112_Trade_Archive_Integrity.csv` | 4,806 | `5435a128c59e5917ba715ff6b8c4f1d979e3692cad974a7a3be09e6a77ab7a46` |
| `CP0112_TradeDerived_Bar_Comparison.csv` | 11,480 | `5e8c7915dacf813af7afce885287d5a017c74da52bbe70733b32ccab3ca17ac4` |
| `CP0112_Aggregation_Bucket_TradeReconstruction.csv` | 2,782 | `59929ca5de8a96b019981768f6eb6df12ea1e2cb2928d77ab68935557268a8d0` |
| `CP0112_TradeDerived_Reconstruction_Report_HI.md` | 4,304 | `6c7955695f68ebd827a826ff58803c6b762bd598dfc41339088e4131c2e5ec3c` |

## 7. Non-actions and gates
- Binance market-data REST API calls: `0`; exchange credentials: `0`.
- Raw kline archives edited/replaced: false. Timestamp shifts/rounding, row merges, synthetic source candles: none. Derived zero-trade handling, if any, exists only inside this comparison output.
- Candidate build/backtest/strategy promotion: not performed. Live signing/public broadcast/Binance orders: not performed.
- Gates unchanged: G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`.
- Shared conflicts: `60` unresolved; unmatched rows quarantined: `909`; residual aggregation blockers: `11` unresolved.

## 8. Next bounded step

Review the 14 unique monthly-mismatching bars against the exact raw monthly JSON, trade-derived bar metrics, the daily row and sidecar identities. Determine whether CP-0040 permits final per-field source dispositions from these three mutually checkable evidence sets or still requires an independent historical-version/provenance record. Do not alter source bytes, auto-select a global canonical source, or close buckets merely because reconstruction passes.
