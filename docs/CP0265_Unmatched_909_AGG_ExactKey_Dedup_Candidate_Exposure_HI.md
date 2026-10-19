# CP-0265: 909 unmatched rows × 11 AGG exact-key deduplication and candidate exposure (Hindi)

**स्थिति:** EXACT-KEY JOIN COMPLETED; 0 intersections with the 11 AGG buckets; all 909 source-attribution cases remain open; G0 remains `BLOCKED_GLOBAL`.
**Branch:** `cp-0165-4h-archive-audit`
**Frozen CP-0040 rulebook SHA-256:** `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`

## 1. Scope and source identity

This checkpoint uses existing evidence only. No archive was downloaded, rescanned, or changed.

- 909-row input: Library file `CP0107_CP0041_Unmatched_909_Provenance_Audit.csv`; 963,228 bytes; SHA-256 `b8ffd2a98f9296fdb04a2296f2190caca5387bbb286185a564717aadcb40d980`. This matches CP-0107's committed summary identity.
- Input rows: 909; distinct `(interval, open_time_ms)` keys: 909.
- Aggregation cases: `evidence/source_adjudication/CP0040_Candidate_Input_Relevance_Run_38901790221/CP0040_Candidate_Input_Relevance_Matrix.csv`, blob `2ae5c36aa1f370cb143f8a30d5a61f41be0d60eb`, 11 rows.
- Candidate universe: `evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Crosswalk.csv`, blob `cdecff27f2472a59d91470cfd9ae774128ed0b37`, 23 candidates.
- Prior FETCHREF reconciliation: CP-0264, whose seven distinct FETCHREF keys already connect to nine AGG edges.

## 2. Exact-key join and deduplication

The join key was exact `(interval, open_time_ms)`. For each AGG bucket, its exact UTC bucket-open timestamp was tested only against that case's child and parent interval. No nearest-time matching, rounding, interval substitution, or date-only matching was used.

| Check | Result |
|---|---:|
| Unmatched source rows | 909 |
| Distinct unmatched exact keys | 909 |
| AGG cases tested | 11 |
| Exact unmatched-row ↔ AGG-key intersections | **0** |
| CP-0264's seven previously linked FETCHREF keys also present in the 909 census | **0** |
| New duplicate row cases created | **0** |

The zero result is a scoped key intersection finding, not proof that the populations are globally unrelated. CP-0264's seven FETCHREF keys remain seven unique row keys linked to nine AGG edges; this checkpoint does not count those edges as additional source cases. All 11 AGG cases remain `UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT`.

## 3. Exact interval exposure against CP-0115's candidate universe

The 909 census partitions as follows. Candidate counts describe interval-level exposure only, not exact row consumption by a candidate builder.

| Interval | Daily-only | Monthly-only | Total source keys | Candidate families exposed per key | Row-candidate exposure edges |
|---|---:|---:|---:|---:|---:|
| 5m | 241 | 245 | 486 | 3 | 1,458 |
| 15m | 81 | 82 | 163 | 3 | 489 |
| 30m | 86 | 86 | 172 | 3 | 516 |
| 1h | 43 | 44 | 87 | 3 | 261 |
| 4h | 1 | 0 | 1 | 4 | 4 |
| **Total** | **452** | **457** | **909** | — | **2,728** |

- 5m families: `CP0027_5m_EMA_12_26`, `CP0027_5m_RSI14_30_55`, `CP0027_5m_DONCHIAN20_10`.
- 15m families: `CP0027_15m_EMA_12_26`, `CP0027_15m_RSI14_30_55`, `CP0027_15m_DONCHIAN20_10`.
- 30m families: `CP0027_30m_EMA_12_26`, `CP0027_30m_RSI14_30_55`, `CP0027_30m_DONCHIAN20_10`.
- 1h families: `CP0027_1h_EMA_12_26`, `CP0027_1h_RSI14_30_55`, `CP0027_1h_DONCHIAN20_10`.
- The single 4h key is `UNMATCHED-D-4h-1504713600000` at `2017-09-06T16:00:00Z`; its four interval-exposure families are the three 4h local candidates plus `CP0031_MTF_BREAKOUT_4H_D1`. It is the already-known CP-0201 exact-key overlap with the invalid daily zero-trade placeholder, not a new gap case.

The 2,728 figure counts row-to-candidate interval-exposure relationships only. It is not 2,728 independent conflicts, does not prove builder consumption or signal/P&L impact, and must not be used as a source-case count.

## 4. Disposition and gate impact

- All 909 rows remain `UNMATCHED_ROW_QUARANTINE_PENDING_SOURCE_ATTRIBUTION`; counterpart status remains absent, canonical source `NONE`, root cause `OPEN_NOT_ESTABLISHED`, and `case_closed=false`.
- All 11 AGG cases remain open.
- No new duplicate cases; no source selected; no source case closed; no timestamp shift/rounding; no row merge/replacement/deletion; no Policy B application.
- No candidate build, acceptance-grade backtest, or profitability conclusion. The existing fail-closed CP-0203/CP-0026/CP-0027 path is unchanged.
- G0 `BLOCKED_GLOBAL`; G2 23 candidates `FAIL`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; profitability `NOT ESTABLISHED`; live signing, public broadcast and exchange orders remain blocked.

## 5. Decision and next atomic action

**Internal dependency gap closed:** exact-key join of the 909-row census to all 11 AGG cases, plus explicit deduplication against CP-0264's seven FETCHREF keys. Interval-level candidate exposure counts are recorded without implying production consumption.

**G0 is not closed.** This work cannot supply historical publication/version authority or independent adjudication. Do not repeat these joins or archive scans absent changed inputs. The next decision-changing dependency remains either admissible official, key-specific historical-version/correction evidence or an actually authorized independent written adjudication under the frozen CP-0040 rulebook; any Policy B application requires separate explicit scoped authorization. Keep all gates fail-closed.
