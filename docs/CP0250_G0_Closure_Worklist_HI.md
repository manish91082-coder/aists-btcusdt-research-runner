# G0 Closure Worklist and Responsibility Matrix (Hindi)

**स्थिति:** ACTIVE WORKLIST; G0 अभी BLOCKED_GLOBAL है।  
**Canonical repository:** manish91082-coder/aists-btcusdt-research-runner  
**Active branch baseline:** 11131cc0286a4f36edb1951476e3e4ea1380e9f5  
**Rulebook:** CP-0040 frozen Strategy Acceptance Rulebook, blob f0d0e81ea6708a0abeb34676f3ff12859080a3c7  
**Scope:** BTCUSDT Spot historical source/data eligibility only. This document is an execution plan, not a source adjudication, approval, or gate pass.

## 1. G0 में असली समस्या

यह सिर्फ checksum की समस्या नहीं है। उपलब्ध ZIPs के checksums integrity बताते हैं कि जाँचे गए bytes recorded sidecars से मेल खाते हैं; वे यह साबित नहीं करते कि historical समय पर कौन-सा version प्रकाशित था, क्या पुराने versions बदले गए थे, या disputed row authoritative है।

Current decision-changing blockers:
1. Historical archive-version/publication/replacement provenance for disputed exact keys is not established.
2. The daily-only 2017-09-06T16:00:00Z row has OHLC all 4619.43, zero volume/trades, and invalid 4h close-time span. It is not accepted as a valid candle.
3. Sixteen other missing 4h slots are absent from both inspected monthly and daily sources; the 17-slot population includes one exact-key overlap with an existing row case, not 17 new row cases.
4. Other unresolved input populations remain: 909 unmatched rows (452 daily-only + 457 monthly-only); 450 February-2018 off-grid rows are a subset of those 909; 52 shared economic/trade-metric conflicts; 8 close-time-only conflicts; 11 non-row aggregation blockers. These populations must not be double-counted.
5. Existing CP-0119 exact-key archive-version review found no historical version hash/timestamp linkage for its 11 aggregation relationships. CP-0245/0246 correction-route investigations are exhausted; do not repeat absent genuinely new evidence.
6. Candidate-specific quarantine diagnostic status does not clear global G0. CP-0212 remains a readiness checklist, not independent approval or Policy B application authorization.

## 2. G0 pass rule (frozen, no weakening)

CP-0040 G0 may pass only when:
- Every active input has exact SHA-256, row count, schema, UTC boundary, OHLCV validation and provenance manifest.
- Hashes and input identities reconcile exactly; no unexplained duplicate, off-grid, impossible OHLC, invalid numeric, or close-time-boundary rows remain.
- Every daily/monthly exact-open disagreement, unmatched row, February-2018 off-grid row, shared conflict, close-time-only conflict, missing interval, and cross-timeframe aggregation blocker has an explicit disposition.
- Either all items that could affect the chosen candidate's signal/position/valuation inputs are adjudicated, OR each remaining item is explicitly quarantined and the candidate's final metrics are computed under that authorized, frozen quarantine policy.
- The candidate-specific decision is not misrepresented as global source authority. If the rulebook's conditions are not met, G0 remains blocked.

No timestamp rounding/shifting, synthetic candles, inferred fills, silent source precedence, or retrospective policy weakening is permitted.

## 3. Responsibility split

### Assistant / research execution responsibilities
- Preserve the frozen evidence populations and exact-key crosswalks; do not re-scan exhausted sources without new input.
- Inspect any genuinely new official source artifact or reviewer-submitted evidence against exact keys, archive hashes, timestamps, schema and reproducibility.
- Maintain the source-adjudication matrix and identify exactly which candidate inputs each unresolved case can affect.
- Keep fail-closed builder/backtest gates intact and run targeted deterministic tests when code changes are justified.
- For each execution, reread this repository's execution rules, inspect live branch/main/PR/CI, make one bounded evidence-producing change, then verify exact HEAD and terminal CI.
- Never impersonate an independent reviewer, fabricate source authority, or claim G0 PASS from green CI.

### GitHub / repository responsibilities
- Persist immutable evidence, manifests, decision matrices, tests and exact commit/CI references on the feature branch.
- Run the configured workflow on the exact new head and retain terminal logs/artifacts; a previous commit's green run does not validate a newer SHA.
- Keep PR #3 open/unmerged until review and authorization conditions are satisfied; do not merge to manufacture progress.
- Preserve main unchanged unless an explicitly reviewed and authorized merge is made.
- GitHub cannot itself manufacture Binance's historical version history or an independent human adjudication. A green workflow proves only the configured checks.

### External evidence / authorized human responsibility
At least one gate-changing path is required:
A. **Official provenance path:** official, reproducible, key-specific evidence linking disputed archive bytes/rows to historical version/publication/replacement/correction metadata; or
B. **Independent review path:** an actually authorized independent reviewer inspects the frozen exact-key evidence, records a traceable decision and limits, and identifies which items can be adjudicated or must remain quarantined. Any Policy B application additionally requires a separate scoped application record and explicit authorization.

The existing PR #3 conversation contains a read-only reviewer request, but the live PR review-submission list was empty when checked. A request/comment is not a completed review. No reviewer is assumed approved or available.

## 4. Closure matrix

| Population / dependency | Current known evidence | Closure requirement | Current disposition |
|---|---|---|---|
| 17 missing 4h slots | 1 overlap with existing row case + 16 absent from both inspected sources | Exact-key source evidence or explicit permitted quarantine with candidate-input impact and reproducible metrics | OPEN |
| Daily-only placeholder at 2017-09-06 16:00 UTC | Zero-trade OHLC placeholder; invalid 4h close span | Official key-specific evidence or independent documented adjudication; never accept merely because present in daily file | OPEN |
| 909 unmatched rows | Frozen row/manifest linkage audited; 452 daily-only + 457 monthly-only | Exact-key disposition and proof each unresolved item is excluded from active inputs or validly adjudicated | OPEN |
| 450 February-2018 off-grid rows | Subset of the 909, not an extra population | Explicit exact-row disposition; preserve raw timestamps, no rounding/shift | OPEN |
| 52 shared economic/trade-metric conflicts | 33 correction-bundle paths were observed; 19 lacked exact paths; none thereby closed | Key-specific authoritative correction/version provenance or explicit permitted quarantine | OPEN |
| 8 close-time-only conflicts | Economic fields match, boundary metadata differs | Explicit policy-compliant boundary disposition and proof it cannot silently affect active inputs | OPEN |
| 11 non-row aggregation blockers | CP-0119 exact-key provenance relationships not reproducibly attributed to historical versions | Reproducible bucket-by-bucket input lineage and resolution/quarantine compatible with frozen rulebook | OPEN |
| Policy B authorization | CP-0212 says approval/application record absent | Independent approval plus separate scoped application record, only if this path is chosen | NOT AUTHORIZED |
| Global source authority | No admissible version-history proof establishing a canonical source | Rulebook-bound final adjudication across all active input dependencies | NONE / G0 BLOCKED |

## 5. Ordered execution gates

1. **Freeze baseline:** hash the rulebook, current manifests, exact-key populations and current decision; verify no overlap double-counting.
2. **Build one unified dependency matrix:** each unresolved case → exact key/interval → archive SHA(s) → affected candidate signal/position/valuation inputs → adjudication or quarantine status. Link existing ledgers; do not copy or create duplicate cases.
3. **Evidence intake only:** accept genuinely new official version/correction metadata or a properly authorized independent review. Do not repeat exhausted correction-directory/checksum/cache scans.
4. **Rulebook-bound decision:** for each frozen population, decide ADJUDICATED, QUARANTINED_WITH_AUTHORIZED_POLICY, or UNRESOLVED; preserve source and reviewer provenance. Missing evidence stays unresolved.
5. **Candidate-specific impact proof:** only after a valid disposition path exists, verify active inputs exclude unresolved material items or apply the separately authorized policy; reconcile exact final metrics and independent accounting.
6. **Exact-head verification:** targeted tests, GitHub Actions terminal result on the exact head SHA, re-read branch/main/PR state, inspect changed files and hashes.
7. **Global G0 decision:** only a verified rulebook-compliant result may change BLOCKED_GLOBAL. Otherwise record the specific remaining blockers and stop before candidate/backtest output.

## 6. Current stop conditions

- Canonical historical source: NONE.
- G0: BLOCKED_GLOBAL.
- G2: FAIL_CURRENT_23_CANDIDATES.
- G3: BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT.
- G4: INSUFFICIENT_EVIDENCE.
- G6: NOT_BUILT / NOT_VALIDATED.
- G7: LIVE_BLOCKED.
- Profitability: NOT_ESTABLISHED.

No candidate build, market backtest, strategy promotion, Policy B application, live signing, public broadcast, or exchange order is authorized by this worklist.

## 7. Per-response progress contract

Every response in this project must state:
1. What execution rule and live GitHub state were reread.
2. What concrete G0 action was performed or why the next gate is externally blocked.
3. Exact changed file/commit/CI/PR identifiers only after live verification.
4. The next single atomic G0 action.
5. Mission Navigation with gate state and blocker; no invented progress percentage.

This worklist is meant to drive execution and prevent loops. It does not itself close any case or clear G0.
