# CP-0040 Rulebook-bound eligibility decision

Status: PASS_RULEBOOK_BOUND_DECISION_GLOBAL_GATES_REMAIN_BLOCKED

## Original frozen rulebook verification
- Exact frozen rulebook member verified from two separately packaged source packs: 10,630 bytes; SHA-256 5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0.
- Runner recomputed the repository copy hash before this decision.

## G0: candidate-specific vs global
- The frozen G0 clause permits candidate-specific PASS when unresolved candidate input rows are explicitly quarantined and final metrics are computed under that quarantine policy.
- For MTF_BREAKOUT_4H_D1, the direct 4h/1d input rows have 9 exact-key manifest entries (4h=6, 1d=3). All 9 were removed with no replacements; baseline anchors passed and quarantine metrics are available.
- The 11 relationship blockers are in lower intervals and have no direct interval overlap with this comparator.
- Candidate-specific diagnostic assessment: PASS_QUARANTINE_BRANCH_FOR_THIS_FROZEN_DIAGNOSTIC_COMPARATOR_ONLY. This is not global G0 PASS or production-builder authorization.

## Gates that remain closed
- Global G0: BLOCKED_GLOBAL. The 11 non-row relationship blockers remain open and CP-0026 builder remains fail-closed.
- G3: BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT. The full-manifest quarantine scenario changes TRAIN net return by -15.891741 percentage points; source-policy stability/adoption is not cleared.
- G2 remains FAIL / NOT PROMOTED per frozen rulebook Section 3. The consumed OOS diagnostic remains negative and cannot be relabelled pristine OOS.
- Canonical source NONE; cases closed=0; live signing, public broadcast and exchange orders BLOCKED.

## Next action
- Do not weaken the builder gate or repeat completed archive-provenance checks. Continue to a rulebook-registered diagnostic review of the candidate's remaining G2/G3 research debt; keep all source cases open until independent source authority is established.
