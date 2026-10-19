# CP-0261: 909-row unmatched population to candidate-interval dependency crosswalk (Hindi)

**स्थिति:** INTERVAL-LEVEL CANDIDATE DEPENDENCY RECONCILED; EXACT-KEY CONSUMPTION UNVERIFIED; G0 STILL `BLOCKED_GLOBAL`.  
**Branch:** `cp-0165-4h-archive-audit`  
**Frozen CP-0040 rulebook SHA-256:** `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.  
**Inputs:** CP-0260 exact interval census; CP-0115 candidate universe interval exposure crosswalk (blob `cdecff27f2472a59d91470cfd9ae774128ed0b37`); current CP-0026 builder source.

## 1. Why this bounded reconciliation matters

CP-0259 marked the 909-row per-key candidate impact as `MISSING_EVIDENCE`. CP-0260 now establishes the population's exact interval distribution. This checkpoint joins that distribution to the 23-candidate interval universe so we can identify which candidate intervals are exposed without claiming row-by-row runtime consumption.

## 2. Exact interval to candidate-universe mapping

| Unmatched interval | Rows in CP-0260 | Matching local-interval candidates in CP-0115 | Candidate IDs |
|---|---:|---:|---|
| 5m | 486 | 3 | `CP0027_5m_EMA_12_26`, `CP0027_5m_RSI14_30_55`, `CP0027_5m_DONCHIAN20_10` |
| 15m | 163 | 3 | `CP0027_15m_EMA_12_26`, `CP0027_15m_RSI14_30_55`, `CP0027_15m_DONCHIAN20_10` |
| 30m | 172 | 3 | `CP0027_30m_EMA_12_26`, `CP0027_30m_RSI14_30_55`, `CP0027_30m_DONCHIAN20_10` |
| 1h | 87 | 3 | `CP0027_1h_EMA_12_26`, `CP0027_1h_RSI14_30_55`, `CP0027_1h_DONCHIAN20_10` |
| 4h | 1 | 4 | `CP0027_4h_EMA_12_26`, `CP0027_4h_RSI14_30_55`, `CP0027_4h_DONCHIAN20_10`, `CP0031_MTF_BREAKOUT_4H_D1` |
| 1d | 0 | 3 interval-universe candidates, but no 909-worklist row at this interval | `CP0027_1d_EMA_12_26`, `CP0027_1d_RSI14_30_55`, `CP0027_1d_DONCHIAN20_10` |
| 1mo | 0 | 3 interval-universe candidates, but no 909-worklist row at this interval | `CP0027_1mo_EMA_12_26`, `CP0027_1mo_RSI14_30_55`, `CP0027_1mo_DONCHIAN20_10` |

The interval universe also includes `CP0031_MTF_BREAKOUT_1D_1MO`; it has no direct 1d/1mo row from the 909-worklist. That statement is limited to this population only. Other frozen populations, including four shared 4h/1d economic conflicts and three 4h close-time conflicts, remain independent blockers.

## 3. Runtime reachability and exact-row limitation

Static source inspection of `scripts/AISTS_CP0026_Research_Candidate_Builder.py` confirms the main execution sequence:

1. Resolve local/Drive root and CP-0200/0201 gap evidence paths.
2. Call `load_gap_policy_gate(...)`.
3. Only if that call returns, load the CP-0040 row-level gate.
4. Only after both gates, read flagged dates/manifests, create candidate output directories and call `audit_and_write_interval(...)`.

The current CP-0203 gate validates frozen evidence and then deliberately raises `G0_BLOCKED_GAP_POLICY_UNRESOLVED` while the gap/source items remain unresolved. Therefore the real candidate-building loop is currently unreachable through the normal `main()` path. This is the intended fail-closed behavior, not a successful candidate build.

The function `partition_candidate_rows` uses exact `(interval, open_time_ms)` keys, but its existence and synthetic fixtures do not prove how each of the 909 source keys would flow through the full builder after an authorized gate transition. CP-0115 also marks exact row consumption as `NOT_VERIFIED_NO_NEW_CANDIDATE_BUILD`.

## 4. Decision boundary

This checkpoint upgrades the prior unknown from “no interval-level mapping” to “interval-level candidate dependencies identified.” It does **not** establish:
- which conflicting source is historically authoritative;
- whether every unmatched key changes a strategy signal, position, or valuation;
- that every key is excluded by an approved frozen policy;
- that G0-A through G0-E pass.

No source was selected, no case closed, no policy applied, no row changed, no candidate built and no backtest run.

## 5. Current gates and next step

- Canonical historical source: `NONE`
- G0: `BLOCKED_GLOBAL`
- G2: all 23 candidates `FAIL`
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- Candidate build / acceptance-grade market backtest: `BLOCKED`
- Profitability: `NOT ESTABLISHED`
- Live signing / broadcast / orders: `BLOCKED`

**Next atomic action:** exact-head verify CP-0261 and roadmap CI, then do not spend another turn on interval mapping. The remaining G0 closure hinge is admissible official key-specific historical-version evidence or an actually authorized independent written adjudication. Once it exists, adjudicate the full frozen population in one bounded batch and verify exact row/candidate impact under the approved disposition.
