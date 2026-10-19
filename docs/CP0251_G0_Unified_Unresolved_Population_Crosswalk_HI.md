# CP-0251 G0 Unified Unresolved-Population Crosswalk (Hindi)

**स्थिति:** EVIDENCE CROSSWALK ONLY; G0 `BLOCKED_GLOBAL`.  
**Parent SHA:** `bf87e4a21115f671b2b083164d97a8cd75dde73a`  
**Rulebook:** Frozen CP-0040; no acceptance-rule changes.  
**Purpose:** एक ही जगह unresolved evidence populations, overlap rules, current evidence, decision-changing closure requirement और जिम्मेदारी स्पष्ट करना। यह source adjudication, approval, quarantine application या gate pass नहीं है।

## निर्णय-सार

G0 की रुकावट checksum failure नहीं, बल्कि **historical source authority / point-in-time version provenance और material input discrepancies का adjudication** है। जाँचे गए ZIP तथा checksum sidecar का मेल byte integrity दिखाता है; वह historical publication/replacement history या disputed row की authority नहीं सिद्ध करता। कोई canonical historical source अभी स्थापित नहीं है।

## Unified population crosswalk

| Population | Frozen count / overlap rule | Verified current evidence | G0 impact | Required closure evidence | Responsible next actor |
|---|---|---|---|---|---|
| Unmatched exact-open-key rows | 909 total = 452 daily-only + 457 monthly-only | Existing exact-key crosswalks and CP-0040 rulebook; unresolved | Candidate OHLCV / signal inputs may differ by source | Per-key disposition with source identity, exact hashes, timestamps, schema/validation and reproducible authority rationale; or explicitly authorized quarantine affecting only eligible candidate inputs | Research execution: crosswalk existing row-level records; external/official evidence or authorized independent reviewer: authority decision |
| February 2018 off-grid rows | 450; **subset of the 909**, never additive | Existing archive audit; unresolved | Grid/timestamp integrity and input eligibility | Preserve exact timestamps; no rounding/shift; disposition each row and prove no material input remains unexplained | Research execution plus evidence provider/reviewer |
| Shared economic/trade-metric conflicts | 52; separate shared-key population | 33 exact paths match inspected official correction bundle to daily archive SHA; 19 have no exact path in that bundle; all unresolved | OHLCV/derived metrics can change | Per-key provenance and trade-derived reconciliation; matching a correction path alone is not a historical point-in-time publication proof | Research execution can reconcile; official provenance or independent adjudication required for authority |
| Close-time-only conflicts | 8 shared keys: 5 monthly-side and 3 daily-side boundary differences; economic fields match 8/8 | Existing exact-key diagnostics; unresolved | Candle eligibility / UTC boundary semantics | Explicit boundary contract and authoritative row/version evidence; no silent normalization | Research execution + source evidence/reviewer |
| Missing 4h slots | 17 slots total = 1 overlaps existing row case `UNMATCHED-D-4h-1504713600000` at `1504713600000` / `2017-09-06T16:00:00Z` + 16 gap-window-only keys absent from both inspected sources | CP-0206 frozen sensitivity-only policy; existing CP-0203 fail-closed gate; one daily-only row is zero-volume/zero-trade with invalid 4h close-time span | Missing/invalid intervals can alter signals, position continuity and scoring | Official key-specific historical source evidence, or an actually authorized independent review plus separate scoped application record before any permitted quarantine application; never synthesize candles or infer fills | Official evidence provider / authorized independent reviewer; assistant preserves fail-closed controls |
| Non-row aggregation blockers | 11; do not convert to row cases without evidence | CP-0112 trade-derived reconstruction: 11/11 directly reconstructed parent candles match child rollups, but cross-source aggregation/provenance blockers remain open | Multi-timeframe inputs and aggregation lineage remain unproven | Blocker-specific reproducible evidence and provenance/version linkage; successful arithmetic reconstruction alone is insufficient | Research execution to map dependencies; external provenance/reviewer for unresolved authority |
| Daily-vs-monthly aggregate divergence | 14 of 35 target bar keys divergent across 97 metric fields; overlaps underlying row/conflict populations and **must not be added as new row count** | CP-0112 trade-derived reconstruction; daily-derived bars exact 35/35, monthly-derived 21/35; source authority remains open | Source selection can change historical candidate inputs | Tie each divergence to underlying exact-key evidence and resolve authority or authorized candidate-scoped quarantine | Research execution + official provenance/reviewer |
| December 2020 residuals | 7 monthly-only keys and 9 review-required roll-ups; maintain as separate diagnostics unless a documented crosswalk proves overlap | Existing source-adjudication diagnostics; unresolved | Monthly archive lineage and roll-up integrity | Exact-key/roll-up dependency links and explicit disposition; avoid inferred deduplication | Research execution; reviewer if authority judgment is needed |

## Non-double-counting contract

1. The 450 February-2018 off-grid rows are already inside the 909 unmatched rows.
2. The 17 missing slots are not 17 new row cases: one is linked to the existing daily-only row case; only 16 are gap-window-only.
3. The 14/35 aggregate divergences, the 52 shared conflicts, and the 11 non-row blockers are different diagnostic views/populations; do not sum them into a single incident count without a row-level identity crosswalk.
4. The December 2020 residual counts stay separate until exact identity links prove overlap or disjointness.
5. A SHA-256/checksum match proves integrity against that sidecar, not historical version provenance or canonical source authority.
6. A static CI pass validates configured controls only. It cannot close source cases, approve Policy B, select a canonical source, or establish profitability.

## Gate and authorization boundary

- Canonical historical source: `NONE`
- G0: `BLOCKED_GLOBAL`
- G2: `FAIL_CURRENT_23_CANDIDATES`
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- G4: `INSUFFICIENT_EVIDENCE`
- G5: `NOT_REACHED / NOT_RUN`
- G6: `NOT_BUILT / NOT_VALIDATED`
- Policy B: `SENSITIVITY_ONLY`; no independent approval or separate scoped application record is present.
- G7 live signing / public broadcast / exchange orders: `BLOCKED`
- Profitability: `NOT_ESTABLISHED`

## Next single action

Obtain genuinely new official, key-specific historical publication/version evidence for the unresolved populations, or an authorized independent reviewer’s written adjudication. Until that exists, continue only dependency mapping and deterministic fail-closed validation; do not run a candidate market backtest or claim G0 closure.
