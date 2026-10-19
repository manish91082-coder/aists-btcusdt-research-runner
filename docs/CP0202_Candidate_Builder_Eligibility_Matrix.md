# CP-0202: Candidate Builder Eligibility Matrix (Source-Code-Only Review)

- Checkpoint: CP-0202
- Branch: `cp-0165-4h-archive-audit`
- Scope: inspect existing code and frozen evidence only; no candidate build, backtest, source promotion, network request, archive download, or live action.
- Decision: **DO NOT BUILD OR BACKTEST. G0 remains BLOCKED_GLOBAL.**
- Profitability: **NOT ESTABLISHED.**

## 1. Evidence reconciliation before code review

CP-0199 execution artifact from [run 39062258502](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39062258502) was downloaded and inspected.

- `CP0199_ExactKey_SourceConflict_Matrix.csv`: 17 target keys; 16 `ABSENT_FROM_BOTH_CACHED_ARCHIVES`; 1 `DAILY_PRESENT_MONTHLY_MISSING_SOURCE_CONFLICT`.
- `CP0199_Archive_Integrity_Manifest.csv`: 20/20 archives report `VALID`, inventory SHA status `MATCH`, zero off-grid rows and zero duplicate open times.
- Monthly archives: 10/10 SHA-256 and byte counts match the CP-0165 details/inventory; 10/10 retain `checksum_status=MATCH` and `zip_crc=PASS`.
- Daily-reference archives: 10/10 SHA-256 and byte counts match the CP-0198 manifest; 10/10 have `zip_crc=PASS` and inventory SHA/byte status `MATCH`.
- Sole conflict: `2017-09-06T16:00:00Z`. The daily raw row has OHLC all `4619.43000000`, zero volume/trades, and close-time token equal to open-time token. It is a `ZERO_TRADE_PLACEHOLDER`, not an accepted candle or a canonical-source decision.
- CP-0200 classifies 16 keys as `UNRESOLVED_MISSING_KEY_BOTH_SOURCES` and one as `UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT`.
- CP-0201 finds one overlap with the existing CP-0040 row-level quarantine case `UNMATCHED-D-4h-1504713600000`; the other 16 are gap-window-only items. No duplicate row case was created and the recommendation has not been applied to the builder.

The artifact establishes archive integrity and exact-key observations for this bounded scope. It does **not** establish source authority, completeness of every source, or strategy profitability.

## 2. Eligibility matrix

| Requirement | Existing implementation and evidence | Status | Gap / risk |
|---|---|---|---|
| Fail closed when gate files are missing | `scripts/AISTS_CP0026_Research_Candidate_Builder.py:135-140` raises when the manifest, non-row blocker file, or summary is absent. | IMPLEMENTED | This guard must remain mandatory. |
| Validate manifest schema, exact key tokens, uniqueness, case state, and summary consistency | `AISTS_CP0026_Research_Candidate_Builder.py:142-180` checks allowed statuses, manifest SHA against the supplied summary, row count, schema, valid interval/integer token, unique exact keys, class-count consistency, unresolved source state, and non-row blockers. | PARTIAL | The builder checks a manifest hash against a hash in the same mutable summary, not against a separately pinned frozen expected SHA/receipt. It likewise validates internal counts rather than independently pinning the expected case-class inventory. A co-edited manifest and summary could satisfy these self-consistency checks. The current 11 non-row blockers correctly keep the gate closed today. |
| Exact `(interval, open_time_ms)` row exclusion without rounding or source mutation | `AISTS_CP0026_Research_Candidate_Builder.py:182-190`; `scripts/AISTS_CP0040_Quarantine_Gate.py:21-29,74-80`. | IMPLEMENTED, INTEGRATION NOT VERIFIED | Exact-key behavior is present. It excludes only rows whose exact key is listed; it does not represent gap windows as such. |
| Deterministic tests for exact-key behavior | CP-0026 has an in-script synthetic self-test at `AISTS_CP0026_Research_Candidate_Builder.py:192-218`; CP-0040 gate has synthetic tests at `AISTS_CP0040_Quarantine_Gate.py:82-110`. | PARTIAL | Current static workflow `.github/workflows/cp0165-4h-audit-tests.yml:62-77` does not compile or invoke CP-0026 or CP-0040 gate tests. Current green CI therefore does not verify this production integration path. |
| Detect structural gaps and preserve them without synthesis | `AISTS_CP0026_Research_Candidate_Builder.py:399-423` records gap events and estimated missing intervals; it states gaps are never interpolated or silently filled. | IMPLEMENTED FOR DETECTION ONLY | Detection/reporting is not the same as eligibility enforcement. Structural status can be `PASS_STRUCTURAL_GAPS_RECORDED` when gaps exist, provided other structural checks pass. |
| Apply CP-0200's 17 gap dispositions before candidate eligibility | CP-0200 explicitly records `quarantine_applied_to_candidate_builder=False` at `scripts/AISTS_CP0200_G0_Rulebook_Bound_Gap_Disposition.py:83-101`. CP-0201 also records `False` at `scripts/AISTS_CP0201_Gap_Quarantine_Overlap_Crosswalk.py:112-124`. | MISSING | CP-0026 does not accept the CP-0200 gap recommendation or CP-0201 crosswalk as a mandatory gate input. The 16 absent-key gap windows are not exact source rows and cannot be safely represented by fabricating 16 row cases. |
| Preserve overlap semantics and prevent double-counting | `scripts/AISTS_CP0201_Gap_Quarantine_Overlap_Crosswalk.py:26-37,64-124`. | IMPLEMENTED IN CROSSWALK; NOT WIRED INTO BUILDER | The 2017-09-06 key links to its existing row-level quarantine case. The other 16 remain gap-policy items. The builder does not consume this distinction. |
| Apply frozen G0 policy to unresolved sources and gaps | Frozen rulebook G0 requires unresolved signal/position/valuation inputs to be marked unresolved and quarantined; see `evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md:14-19`. CP-0200's classification is at `AISTS_CP0200_G0_Rulebook_Bound_Gap_Disposition.py:29-44`. | NOT SATISFIED FOR GAP WINDOWS | The builder's gap report does not itself block signal/position/valuation use across unresolved gap windows. No canonical source may be selected from timestamp agreement alone. |
| Preserve existing broader blocker families without double-counting | Roadmap inventory: 909 unmatched rows, 52 shared economic conflicts, 8 close-time-only cases, 450 February-2018 off-grid rows, plus the CP-0201 gap crosswalk. | PARTIAL / NEEDS PINNED CROSSWALK | The builder can consume an exact-key row manifest, but the reviewed gate code does not independently prove that every expected frozen family/count is present and that overlapping cases are counted once. Existing ledgers must remain the authority for membership and overlap, not new inferred rows. |
| Candidate build authorization while unresolved non-row blockers remain | `AISTS_CP0026_Research_Candidate_Builder.py:173-180,494-512`. | IMPLEMENTED FAIL-CLOSED FOR CURRENT BLOCKERS | Current rulebook-bound evidence records 11 non-row blockers; the gate must continue to reject the build. Do not remove or waive blockers merely to obtain a successful run. |
| Live execution safety | Builder and audit summaries preserve no live actions; project restriction is live signing/broadcast/orders blocked. | BLOCKED AS REQUIRED | No live order path is authorized. |

## 3. Decision

1. **No CP-0026 candidate build or backtest.** G0 is still globally blocked; the CP-0200 gap recommendation is not wired into candidate eligibility.
2. Preserve exact row-level quarantine semantics. Keep the one overlapping 2017-09-06 row linked to its existing case; do not create a duplicate.
3. Keep the 16 gap-window-only items as gap-policy records, not fabricated candle rows.
4. Before any future build is permitted, add a fail-closed, independently hash-pinned gate for the frozen gap-policy manifest and its crosswalk. The gate must require the expected 17 dispositions, preserve the overlap/gap-only distinction, and block eligibility unless the rulebook-required conservative gap policy is explicitly represented in the candidate eligibility evidence.
5. Add regression tests for missing gap manifest, hash mismatch, row/count mismatch, the single overlap, 16 gap-only items, and attempted candidate execution while gap policy remains unresolved. Wire those tests into static CI. Do not relax the existing 11-blocker gate.
6. Only after the gap-policy decision and matrix review should code changes be made. No strategy optimization, backtest, source promotion, or live activation is in scope.

## 4. Checkpoint boundary

- Code changes: none.
- Candidate build: not run.
- Backtest: not run.
- Network/data downloads: none for CP-0202.
- Canonical source: `NONE`.
- G0: `BLOCKED_GLOBAL`.
- Live signing/broadcast/orders: `BLOCKED`.
- Profitability: `NOT ESTABLISHED`.


## Addendum — current-HEAD reconciliation (2026-10-19)

This addendum preserves the original CP-0202 snapshot and records later repository state observed at branch HEAD `c16a4a37580970c7d2a9cbcd7338fcec37ff94e2`. It does not change the frozen CP-0040 acceptance rulebook or authorize candidate execution.

- The original CP-0202 statements that CP-0200/0201 gap evidence is not wired into candidate eligibility and that CP-0203 tests are absent from static CI are historical snapshot statements, not accurate descriptions of the current branch.
- Current `scripts/AISTS_CP0026_Research_Candidate_Builder.py` integration is asserted by `tests/test_cp0203_gap_policy_gate.py::test_candidate_builder_invokes_gate_before_candidate_output`: the test checks that `load_gap_policy_gate()` occurs before the row gate and candidate output path.
- Current `.github/workflows/cp0165-4h-audit-tests.yml` includes `scripts/AISTS_CP0203_GapPolicy_Gate.py` and `tests/test_cp0203_gap_policy_gate.py` in its path filters, compiles the gate, and runs the CP-0203, CP-0204 and CP-0206 tests.
- The current CP-0203 gate is intentionally fail-closed: it validates the frozen 17-key gap evidence and then raises `G0_BLOCKED_GAP_POLICY_UNRESOLVED`; it returns no candidate eligibility PASS. Policy B remains sensitivity-only, and the current gate state remains G0 `BLOCKED_GLOBAL`.
- This reconciliation corrects the current-state description only. It does not resolve historical source authority, the 909 unmatched rows, 52 shared economic conflicts, 8 close-time conflicts, 11 non-row aggregation relationships, or the independent-review requirement. No candidate build/backtest is authorized by this addendum.
