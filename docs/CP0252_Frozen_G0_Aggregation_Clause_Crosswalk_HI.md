# CP-0252 Frozen G0 Clause-to-Aggregation-Blocker Crosswalk (Hindi)

**स्थिति:** CLAUSE-LEVEL EVIDENCE MAPPING ONLY; G0 `BLOCKED_GLOBAL`.  
**Parent HEAD:** `7139d3ce4f080b14902b0804a4f9d7ce3dd171b9`  
**Frozen rulebook:** `CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md`, Git blob `f0d0e81ea6708a0abeb34676f3ff12859080a3c7`; frozen package-member SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.  
**Input ledger:** `CP0040_Run_38883792900/CP0040_NonRow_Blockers.csv`, Git blob `d3fca23bac424fa8c8b187434e8c63e8d188a0e1`.  
**Rule:** यह document source adjudication, quarantine authorization, G0 PASS, source selection या candidate build की अनुमति नहीं देता।

## 1. Frozen G0 clauses applied

Frozen CP-0040 Rulebook, Section 2 / G0 के लागू clauses:

- **G0-A / active input evidence:** हर active input का exact SHA-256, row count, schema, UTC boundary, OHLCV validation और provenance manifest होना चाहिए; hashes exact match हों।
- **G0-B / unresolved structural defects:** duplicate/open-time, out-of-grid, impossible OHLC, invalid numeric या close-time-boundary errors में zero unexplained rows; real missing intervals log हों, synthetic bars नहीं।
- **G0-C / source disagreement disposition:** monthly/daily exact-open disagreements, daily-only/monthly-only rows, February-2018 shifted rows और cross-timeframe aggregation conflicts का disposition होना चाहिए। Unadjudicated inputs `UNRESOLVED` रहें और signal-influencing research run से अलग quarantine sensitivity में जाएँ।
- **G0-D / PASS criterion:** चुने गए candidate के actual signal/position/valuation inputs को प्रभावित करने वाले unresolved items शून्य हों, या हर remaining item स्पष्ट रूप से quarantined हो और final metrics उसी authorized quarantine policy के आधार पर हों।
- **G0-E / no silent repair:** raw archives immutable; कोई rounding, timestamp shifting, gap filling या automatic source replacement नहीं।

## 2. Exact 11 relationship cases

Verified CP-0040 current ledger में 11 `RESIDUAL_AGGREGATION_BUCKET` cases हैं। हर case का frozen disposition `UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT` है और reason बताता है कि frozen minimal index में exact row open-key नहीं है। CP-0107 diagnostic overlay में 11/11 daily child rollups daily parent से match हुए, जबकि monthly mismatch signature 11/11 में बना रहा। यह arithmetic diagnostic है, canonical source authority नहीं।

| Case | Relationship | Exact UTC anchor | G0 clause | Current disposition | Evidence needed to close |
|---|---|---|---|---|---|
| AGG-01 | 5m → 15m | 2017-12-04 09:00Z | G0-A, G0-C, G0-D | OPEN | Exact parent/child input lineage, immutable archive/version provenance and a reproducible reconciliation or authorized candidate-specific exclusion proof |
| AGG-02 | 5m → 15m | 2017-12-04 09:15Z | G0-A, G0-C, G0-D | OPEN | Same requirements, with this bucket's exact source rows and metrics explicitly linked |
| AGG-03 | 5m → 15m | 2018-02-05 10:00Z | G0-A, G0-C, G0-D | OPEN | Exact-key child/parent linkage and source/version evidence; do not infer a timestamp shift from nearby February off-grid rows |
| AGG-04 | 5m → 15m | 2018-03-04 14:30Z | G0-A, G0-C, G0-D | OPEN | Exact source lineage, parent/child metrics and historical-version authority |
| AGG-05 | 5m → 15m | 2018-03-04 14:45Z | G0-A, G0-C, G0-D | OPEN | Exact source lineage, parent/child metrics and historical-version authority |
| AGG-06 | 5m → 15m | 2018-09-05 09:45Z | G0-A, G0-C, G0-D | OPEN | Exact source lineage and decision-changing provenance or independently authorized candidate-scoped exclusion |
| AGG-07 | 15m → 30m | 2017-12-04 09:00Z | G0-A, G0-C, G0-D | OPEN | Exact parent/child lineage and historical-version authority; do not close because AGG-01 shares the UTC anchor |
| AGG-08 | 15m → 30m | 2018-02-07 06:30Z | G0-A, G0-C, G0-D | OPEN | Exact parent/child lineage and historical-version authority; no implicit February alignment correction |
| AGG-09 | 15m → 30m | 2018-03-04 14:30Z | G0-A, G0-C, G0-D | OPEN | Exact source lineage and metric reconciliation; do not close based only on another relationship at the same time |
| AGG-10 | 15m → 30m | 2018-06-20 03:30Z | G0-A, G0-C, G0-D | OPEN | Exact source lineage, parent/child metrics and historical-version authority |
| AGG-11 | 30m → 1h | 2018-03-20 03:00Z | G0-A, G0-C, G0-D | OPEN | Exact source lineage, parent/child metrics and historical-version authority |

**Identity guard:** Equal UTC anchors in different interval relationships are not the same case. Do not deduplicate AGG-01/AGG-07 or AGG-04/AGG-09 solely by timestamp. Current case IDs and relationship identities remain authoritative for the ledger.

## 3. Why existing row quarantine does not close these cases

1. The frozen ledger explicitly says these relationship cases have no exact row open-key in the frozen minimal index. A row-level exclusion manifest alone cannot demonstrate that a parent/child aggregation relationship has been resolved.
2. CP-0107 reviewed 78 linked source-row records across 11 buckets; daily child rollups matched daily parents in all 11, while the monthly mismatch signature persisted in all 11. This establishes a reproducible discrepancy pattern, not which archive was historically authoritative.
3. CP-0112 trade-derived reconstruction validates 11/11 directly reconstructed parent candles against child rollups, but does not establish monthly archive version/publication provenance. Arithmetic agreement of a reconstructed daily source does not prove historical source authority.
4. The original frozen rulebook says unresolved items affecting actual signal/position/valuation inputs must be adjudicated or explicitly quarantined under the applicable authorized policy. Policy B remains sensitivity-only absent independent approval and a separate scoped application record.
5. A candidate-specific quarantine, if later properly authorized and computed, would not by itself establish global canonical source authority.

## 4. Responsibility and exact closure evidence

**Research execution can do now**
- Keep the 11 exact case IDs stable and link each to the existing 78-row evidence records and current candidate-input dependency matrix.
- Verify per-case row/parent/child hashes, source archive identity, UTC boundary, metric deltas and reproduction command against already committed evidence.
- Preserve fail-closed builder/backtest gates; no synthetic candles, timestamp normalization or source precedence.

**External / authorized decision dependency**
- Official key-specific historical publication/version/correction evidence that resolves the source authority question; OR
- A real independent reviewer’s written adjudication, plus a separate scoped Policy B application record explicitly authorizing any candidate-specific quarantine application where required.

Neither a green CI run nor this clause crosswalk supplies that external evidence or approval.

## 5. Verified current gate state

- Canonical historical source: `NONE`
- G0: `BLOCKED_GLOBAL`
- All 11 aggregation relationship cases: `OPEN_NOT_ESTABLISHED`
- Source cases closed by this crosswalk: `0`
- Candidate build/backtest: `NOT RUN / BLOCKED`
- Policy B: `SENSITIVITY_ONLY; NOT AUTHORIZED FOR APPLICATION`
- G2: `FAIL_CURRENT_23_CANDIDATES`
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- G4: `INSUFFICIENT_EVIDENCE`
- G6: `NOT_BUILT / NOT_VALIDATED`
- G7 live signing/public broadcast/exchange orders: `BLOCKED`
- Profitability: `NOT ESTABLISHED`

## 6. Next single action

Cross-check the 11 case IDs against the committed CP-0107 78-row evidence and CP-0040 candidate-input relevance matrix, producing exact per-case source hash / metric-delta / candidate-dependency links where already supported. If a field is absent, mark it `MISSING_EVIDENCE`; do not infer it. This can improve traceability but cannot clear G0 without source authority or properly authorized adjudication.
