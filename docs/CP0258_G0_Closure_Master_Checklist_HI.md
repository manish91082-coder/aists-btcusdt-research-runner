# CP-0258: G0 Closure Master Checklist and Batch Execution Plan (Hindi)

**स्थिति:** EXECUTION CHECKLIST; G0 अभी `BLOCKED_GLOBAL`। यह दस्तावेज़ gate closure नहीं है।  
**Frozen rulebook:** CP-0040 `evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md`, blob `f0d0e81ea6708a0abeb34676f3ff12859080a3c7`; package-member SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.  
**Baseline branch at checklist creation:** `cp-0165-4h-archive-audit`; main must remain unchanged without authorized review/merge.

## A. G0 बंद करने की पूरी प्रक्रिया: 8 gates

ये 8 gates पूरे G0 closure workflow हैं। Gate 1, 2 और 7 के repository-internal हिस्से batch में चल सकते हैं। Gate 3 से पहले कोई valid source/reviewer evidence उपलब्ध न हो तो Gate 4-6 में कोई adjudication या quarantine approval कल्पना से नहीं बनाई जा सकती। Gate 8 अंतिम decision है, कोई अलग coding shortcut नहीं।

| Gate | आवश्यक कार्य | एक साथ हो सकता है? | Closure proof | वर्तमान स्थिति |
|---|---|---|---|---|
| 1. Freeze & identity | CP-0040 hash, active branch/main/PR, all population manifests, exact keys, source hashes और current gate state freeze/verify; duplicate population counting रोकना | Gate 2 के साथ batch | exact commit/blob/hash inventory | Current state reverified; every run requires refresh |
| 2. Unified unresolved-input matrix | सभी populations को एक identity-preserving matrix में link करना: exact key/timeframe, archive/member/sidecar hashes, row counts, conflicts, affected signal/position/valuation input, existing disposition | Gate 1 और deterministic tests के साथ batch | every population has exact evidence links; absent fields explicitly `MISSING_EVIDENCE` | Partial; CP-0251/CP-0257 exist, broader key-level impact still unresolved |
| 3. Valid evidence intake | सिर्फ genuinely new official key-specific historical publication/version/correction evidence या authorized independent reviewer evidence स्वीकारना; same exhausted scans दोहराना नहीं | यह gate prerequisite है; evidence मिलने पर सभी submitted evidence को एक batch में validate किया जा सकता है | source/reviewer identity, authority, exact keys, hashes, timestamps, independently verifiable provenance | BLOCKED: qualifying new evidence/review not present in current record |
| 4. Clause-by-clause adjudication | Frozen G0-A through G0-E के विरुद्ध प्रत्येक population का disposition: `ADJUDICATED`, `QUARANTINED_WITH_AUTHORIZED_POLICY`, या `UNRESOLVED`; no inferred precedence | Gate 3 के evidence पर सभी populations को एक batch में review किया जा सकता है, लेकिन reviewer must decide | signed/traceable decision, exact scope, unresolved remainder and rationale | NOT PERFORMED; execution must not impersonate reviewer |
| 5. Authorized quarantine path, if chosen | Policy B sensitivity-only से authorized application तक तभी जाए जब actual independent authority और separate scoped application record मौजूद हों; exact exclusion/censor/warm-up/valuation behavior prove हो | Gate 4 approval के बाद all approved cases can be applied together | signed authority + separate scope/application record + hash-bound policy/input manifest | NOT AUTHORIZED; no Policy B application |
| 6. Candidate-input impact and accounting proof | Only after valid dispositions: prove each unresolved item excluded from active signal/position/valuation inputs OR covered by authorized policy; verify exact final input hashes, no synthetic rows/fills, cash/quantity/fees/P&L/equity reconciliation and segment accounting | Candidate dependency and accounting tests can be batched after Gates 4-5; cannot precede them as acceptance proof | reproducible exact-input dependency report and independent accounting checks | BLOCKED on valid disposition; existing comparator result alone is insufficient |
| 7. Exact-head verification | targeted tests, fail-closed G0/candidate/backtest gate, CI terminal result on exact new HEAD, then re-read branch/main/PR/files/hashes | Tests and repository reconciliation can be batched per final candidate evidence bundle | exact-head CI success plus content/hash reconciliation; CI is not source authority | Repeat only after a decision-changing evidence/code update; latest report/roadmap CI was successful before this checklist commit |
| 8. Final G0 decision | Re-evaluate all G0-A–G0-E and all active input dependencies against frozen rulebook; set PASS only for proven exact declared scope, otherwise remain BLOCKED with named residuals | Must be last, after Gates 3-7 | independently verifiable rulebook-compliant decision record | BLOCKED_GLOBAL |

## B. Full frozen blocker population register

Counts are evidence views, not additive incident counts. Preserve exact-key links and overlap relationships.

| Population | Frozen count / known fact | Minimum closure requirement | Current default |
|---|---|---|---|
| Daily/monthly unmatched exact-open-key rows | 909 = 452 daily-only + 457 monthly-only | Per-key disposition and candidate-input impact; no inferred source precedence | OPEN |
| February 2018 off-grid rows | 450, subset of 909 | Explicit exact-row disposition; raw timestamps unchanged | OPEN |
| Shared economic/trade-metric conflicts | 52 | Authoritative version/correction proof or authorized quarantine for each material dependency | OPEN |
| Close-time-only conflicts | 8 | Boundary-specific rulebook disposition and input-impact proof | OPEN |
| Cross-interval aggregation conflicts | 11: AGG-01…AGG-11 | Exact child/parent lineage plus historical source authority or authorized case disposition | OPEN |
| Missing 4h slots | 17: one overlaps existing daily-only row case; 16 are gap-window-only | Exact-key official evidence or authorized quarantine; no synthetic candles/intragap fills | OPEN |
| Daily-only 4h placeholder | 2017-09-06T16:00:00Z; zero-trade flat OHLC and invalid 4h close-time span | Valid authoritative evidence or explicit rulebook-bound disposition; presence in daily file is not sufficient | OPEN |
| December 2020 residuals | 7 monthly-only keys + 9 review-required rollups | Exact crosswalk to prove overlap/disjointness and each case disposition | OPEN |
| Archive/version historical authority | Existing checksums prove bytes match recorded sidecars, not historical publication/version authority | Official key-specific publication/version/correction metadata OR authorized independent written adjudication | NONE |
| Policy B authority | Sensitivity-only; no authorized application record | Actual authorized independent approval and separate scoped application record | NOT AUTHORIZED |

**Non-double-counting rules:** the 450 February off-grid rows are included in 909 unmatched rows; one of 17 gap slots overlaps an existing row case; 14/35 aggregate divergence views, 52 shared conflicts and 11 non-row relationships must not be added without exact identity crosswalk; December 2020 residuals remain separate until linked.

## C. Batch plan and sequential dependencies

### Batch 1: Repository-internal, safe to do together
- Re-read execution rules and current branch/main/PR/CI.
- Validate the unified population crosswalk against existing committed evidence and frozen CP-0040.
- Correct/report missing matrix fields as `MISSING_EVIDENCE`; detect duplicate identities without merging cases.
- Run deterministic tests for matrix consistency and fail-closed gate invariants.
- Append only verified findings to the roadmap; verify exact HEAD and terminal CI.

### Gate 3: External decision-changing dependency
Stop the closure path here if neither of the following exists:
1. New admissible official key-specific historical publication/version/correction evidence; or
2. An actually authorized independent reviewer’s written, traceable adjudication of the frozen evidence.

Do not repeat exhausted archive/checksum/correction scans. Do not contact/post to an external issue or claim a reviewer is authorized without permission. Do not fill reviewer fields on their behalf.

### Batch 2: Only after Gate 3 supplies qualifying evidence
- Validate all evidence and reviewer authority in one intake batch.
- Have the authorized reviewer disposition all relevant populations clause-by-clause.
- If and only if a quarantine path is explicitly approved, create its separate scope/application record and verify policy hashes.
- Run candidate-input impact and independent accounting tests on the exact authorized input set.
- Run final exact-head CI, reconcile artifacts/hashes, and make the final G0-A–G0-E decision.

## D. Non-negotiable stop rules

- No canonical source selected by convenience.
- No inferred approval, fabricated provenance, synthetic candle, timestamp shifting/rounding, source replacement, or inferred fill.
- No silent CP-0040 rulebook edit.
- No production candidate build, acceptance-grade market backtest, strategy promotion, profitability claim, live signing, public broadcast, or exchange order before all required gates actually pass.
- A static CI success is implementation-control evidence only; it does not close any source case or establish G0.
- If any required field/evidence is absent, record `MISSING_EVIDENCE` / `UNRESOLVED` and keep G0 blocked.

## E. Current autonomous decision

**Next action:** execute Batch 1's remaining population-level identity/dependency reconciliation against existing committed evidence, then exact-head verify. Do not repeat source scans. The external evidence/reviewer gate is the only known decision-changing dependency; when qualifying evidence appears, Batch 2 can be run as one bounded closure package.

Current gates: canonical source `NONE`; G0 `BLOCKED_GLOBAL`; source cases closed `0` unless separately proven otherwise; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; profitability `NOT_ESTABLISHED`; live actions `BLOCKED`.
