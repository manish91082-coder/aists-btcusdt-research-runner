# CP-0264: FETCHREF row-key to aggregation/candidate dependency reconciliation (Hindi)

**स्थिति:** EXACT-KEY CROSS-LEDGER RECONCILIATION COMPLETED FOR 24 TARGET ROWS; SOURCE CASES STILL OPEN; G0 STILL `BLOCKED_GLOBAL`.
**Branch:** `cp-0165-4h-archive-audit`
**Frozen CP-0040 rulebook SHA-256:** `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`

## 1. Scope and reproducible inputs

No archive was downloaded or rescanned. This bounded reconciliation parsed existing committed evidence:

- Daily-reference raw row comparison: `evidence/source_adjudication/CP0107_Run_38909366995/CP0107_CP0041_DailyReference_RawRow_Comparison.csv`, blob SHA `1fa303ba60a6fdbee009435db2bba0f3fc788406` (1,992 data rows).
- Aggregation candidate relevance matrix: `evidence/source_adjudication/CP0040_Candidate_Input_Relevance_Run_38901790221/CP0040_Candidate_Input_Relevance_Matrix.csv`, blob SHA `2ae5c36aa1f370cb143f8a30d5a61f41be0d60eb` (11 aggregation rows).
- Shared-52 exact-key dependency matrix: `evidence/source_adjudication/CP0107_Shared52_Candidate_Input_Dependency_Run_38902949514/CP0107_Shared52_Candidate_Input_Dependency_Matrix.csv`, blob SHA `196bdb50546e184b755151fc4e14b5b7246267e4` (52 conflict rows).
- Candidate interval exposure crosswalk: `evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Crosswalk.csv`, blob SHA `cdecff27f2472a59d91470cfd9ae774128ed0b37`.

The 24 target rows are the union of 10 `MONTHLY_ONLY_KEY` rows and 14 rows with `economic_differing_field_count > 0` in the FETCHREF daily-reference package. Matching used exact interval and exact open-time key; UTC string formatting was normalized only to compare equivalent `.000Z` and `Z` representations. No timestamp was rounded or shifted.

## 2. Exact aggregation-case joins

| FETCHREF row | Exact interval/open time | Matching aggregation case(s) |
|---|---|---|
| `FETCHREF-15m-2017-12-04` | 15m, 2017-12-04 09:00Z | `AGG-01-5m-15m-2017-12-04T09:00:00Z`; `AGG-07-15m-30m-2017-12-04T09:00:00Z` |
| `FETCHREF-15m-2018-02-07` | 15m, 2018-02-07 06:30Z | `AGG-08-15m-30m-2018-02-07T06:30:00Z` |
| `FETCHREF-15m-2018-03-04` | 15m, 2018-03-04 14:30Z | `AGG-04-5m-15m-2018-03-04T14:30:00Z`; `AGG-09-15m-30m-2018-03-04T14:30:00Z` |
| `FETCHREF-15m-2018-06-20` | 15m, 2018-06-20 03:30Z | `AGG-10-15m-30m-2018-06-20T03:30:00Z` |
| `FETCHREF-30m-2018-03-20` | 30m, 2018-03-20 03:00Z | `AGG-11-30m-1h-2018-03-20T03:00:00Z` |
| `FETCHREF-5m-2017-12-04` | 5m, 2017-12-04 09:15Z | `AGG-02-5m-15m-2017-12-04T09:15:00Z` |
| `FETCHREF-5m-2018-03-04` | 5m, 2018-03-04 14:45Z | `AGG-05-5m-15m-2018-03-04T14:45:00Z` |

**Result:** 7 distinct FETCHREF row keys link to 9 aggregation-case edges. The 10 monthly-only keys have no exact-key match in the 11-row aggregation matrix. The other 7 economic-difference rows also have no exact-key match in that matrix. No edge is inferred from nearby time or count.

The two rows that link to two aggregation cases do not become two source conflicts: they remain one FETCHREF row each with two cross-interval relationships.

## 3. Candidate interval exposure

Interval-only candidate exposure, using the frozen CP-0115 candidate universe, is:

- 5m rows (including eight monthly-only keys and nine economic-divergence keys): `CP0027_5m_EMA_12_26`, `CP0027_5m_RSI14_30_55`, `CP0027_5m_DONCHIAN20_10`.
- 15m rows (two monthly-only keys and four economic-divergence keys): `CP0027_15m_EMA_12_26`, `CP0027_15m_RSI14_30_55`, `CP0027_15m_DONCHIAN20_10`.
- 30m row (one economic-divergence key): `CP0027_30m_EMA_12_26`, `CP0027_30m_RSI14_30_55`, `CP0027_30m_DONCHIAN20_10`.

This is **interval exposure only**, not proof that the production builder actually consumed these exact rows or that any signal/position/valuation changed. CP-0115's 23-candidate universe is unchanged.

## 4. Cross-check against Shared-52 and limits

- Exact `(interval, open_time_ms)` join of these 24 FETCHREF target rows to the separate CP-0107 Shared-52 matrix: **0 matches**.
- This means these target keys are not duplicates of the 52 listed Shared-52 conflict keys. It does not prove the populations are globally disjoint in other ways or authorize source selection.
- The 11 aggregation matrix rows each retain `UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT`. Their frozen relevance assessment says no direct interval overlap with the MTF_BREAKOUT_4H_D1 comparator. This does not clear the lower-timeframe candidate families or the global G0 gate.
- All 24 target rows remain `OPEN_REVIEW_REQUIRED`; all relevant aggregation cases remain open; canonical source remains `NONE`.

## 5. Decision and next atomic action

Resolved: exact-key relationships for the 24 targeted FETCHREF rows are now distinguished from the 52 Shared-52 keys, and seven row keys are linked to nine existing aggregation edges without double-counting.

Not resolved: historical publication/version authority, source-case adjudication, all remaining unmatched-row dependencies, full builder consumption, G0-A through G0-E.

No source was selected; no case was closed; Policy B was not applied; no raw data or frozen rulebook changed; no candidate build/backtest was run; profitability remains unestablished; live signing/broadcast/orders remain blocked.

**Next atomic action:** extend the same exact-key join to the 909 unmatched-row census against the 11 aggregation buckets and CP-0115 candidate interval universe, but only for keys that are present in the source worklist. Avoid re-counting the seven FETCHREF row keys already linked here. This is the next internal dependency gap that can be closed without external authority. The ultimate G0 closure still requires admissible official key-specific historical-version evidence or actually authorized independent written adjudication.
