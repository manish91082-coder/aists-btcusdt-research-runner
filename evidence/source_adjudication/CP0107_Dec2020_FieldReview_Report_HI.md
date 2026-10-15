# CP-0107: December 2020 raw-field / provenance classification

**Status:** `PASS_EVIDENCE_CLASSIFICATION_NOT_ROOT_CAUSE`. This analysis uses committed, hash-identified CSV evidence only. No archives were downloaded; no Actions job/backtest was run for the comparison outputs.

## Directly evidenced

- **16 shared 5m open-time keys** exist in both monthly and daily ZIP-derived extracts. Of these, **9 rows match across all compared raw fields and 7 differ**.
- The first divergence in that shared range is **2020-12-21 13:15 UTC**: open/low match, but high, close, base volume, quote volume, trade count and taker-buy metrics differ.
- At the following six shared keys, **13:20 through 13:45 UTC**, monthly rows are flat at OHLC `22646.53000000` with zero base/quote volume and zero trades, while the corresponding daily rows contain non-flat prices and nonzero trades/volume. At 13:45, the daily record also has `close_time=1608558440521`, which is earlier than its expected 5m boundary.
- The same close-time token `1608558440521` appears on **8 records** across 5m, 15m, 30m and 1h; four are monthly flat/zero rows and four are daily non-flat rows. Their open-time keys and expected close boundaries differ. This proves a repeated field value, not a common candle or the process that produced it.
- In the two SHA-verified child archives, 10 expected monthly 5m keys and 14 expected daily 5m keys are absent during the audited window. All nine roll-up cases still lack required exact child keys. No child or aggregate is synthesized.

## Row-level files

| File | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `CP0107_Dec2020_Shared_5m_RawField_Comparison.csv` | 16 | 12387 | `c89e38fc02f36c2b64b29fc46ea3d522f4f2a5972b62ac4092cc37f7859641f0` |
| `CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv` | 8 | 5671 | `8d8c3d4c2701878ac33cd37647f341c53883732bd9d15f01d82c062a8c253f12` |
| `CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv` | 24 | 9222 | `da9f1db50042054ff84e672119ec447d6d100d8b5dce7139642d33ada6652269` |

## What remains unproven

- Whether the repeated close-time value was introduced by archive generation, export/serialization, a shared upstream process or another mechanism.
- Whether the daily and monthly exports are independent, and which source has authority for disputed economic fields.
- Why the source archive rows at the missing keys are absent; this audit establishes only exact-key absence in the hash-verified ZIP bytes.
- Monthly `.CHECKSUM` sidecar bytes were not re-fetched/re-hashed in this run. The monthly ZIP SHA matches the official value in the frozen manifest and its ZIP CRC passes; daily ZIP and cached sidecar were locally rehashed/content matched.

## Disposition

All affected row/case dispositions remain `OPEN_REVIEW_REQUIRED`; root cause `OPEN_NOT_ESTABLISHED`; canonical source `NONE`; source cases closed `0`. Raw files, timestamps and field tokens remain unchanged. No backtest rerun or candidate promotion. Frozen gates remain unchanged.

Next evidence-producing step: obtain official archive-side provenance/version history and a documented explanation of the cross-interval close-time token; only then decide whether metadata-field-only disposition or continued quarantine is justified under CP-0040.
