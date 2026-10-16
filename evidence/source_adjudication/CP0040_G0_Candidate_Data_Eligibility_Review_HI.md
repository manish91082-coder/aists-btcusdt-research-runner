# CP-0040 G0 Candidate-Data Eligibility Review (Hindi)

**तारीख:** 16 अक्टूबर 2026  
**निर्णय:** `BLOCKED` for the existing CP-0026 candidate-builder policy. No candidate dataset is newly approved by this review.

## 1. Frozen acceptance rule used

CP-0040 rulebook exact bytes were reverified inside the CP-0041 source package:
- Rulebook size: 10,630 bytes
- SHA-256: `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`
- Rule: G0 requires every active input to have exact provenance/schema/boundary validation, zero unexplained structural errors, and unresolved items that could affect signals must either be adjudicated or explicitly quarantined with final metrics based on that quarantine policy.

## 2. Code evidence: current CP-0026 builder does not enforce CP-0107 row-level quarantine

Reviewed `scripts/AISTS_CP0026_Research_Candidate_Builder.py`, Git blob `3ef0376ff4d8e6f6cfd6550512029e75d99ad75b`.

- The documented source policy chooses a checksum-verified daily archive for all CP-0025 flagged UTC dates and monthly archives for other dates.
- In the inspected builder loop (lines 230-280), monthly rows on flagged dates are suppressed; each row from the selected daily archive is then appended to the candidate without a lookup against the CP-0107 row-level unmatched/conflict disposition records.
- The builder therefore does not explicitly exclude the 452 daily-only unmatched rows or the 52 shared economic-conflict keys from the selected daily rows. The code does not show a CP-0107 row-level exclusion list or matching quarantine gate.
- This is a source-code inspection result. No CP-0026 candidate build was run in this checkpoint, and no claim is made about any uninspected existing output bytes.

## 3. Relevant frozen evidence coverage

- **909 unmatched exact-open-key rows:** 452 daily-only, 457 monthly-only. Independent frozen-ledger hash and 909/909 row-reference checks PASS. All 909 remain `UNMATCHED_ROW_QUARANTINE_PENDING_SOURCE_ATTRIBUTION`; canonical source NONE; root cause OPEN_NOT_ESTABLISHED; case_closed FALSE.
- **52 shared economic/trade-metric conflicts:** matrix joins 52/52 to both source crosswalks. 33 rows have exact daily paths in the inspected official correction bundle and New File Checksum equals frozen daily archive SHA for 33/33; 19 rows have no exact path in that one bundle. All 52 remain unresolved; no canonical source.
- **8 shared close-time-only metadata cases:** economic fields match 8/8, but five monthly and three daily close-time boundary values differ. All remain `OPEN_REVIEW_REQUIRED_NO_CANONICAL_SOURCE`.
- **450 February-2018 off-grid monthly rows** are part of the unmatched-key population, not an additional 450 to add to 909. They are already extracted and quarantined in the derived disposition view; their exact open keys have zero exact matches to the daily reference rows. No rounding or timestamp shifting is permitted.
- December 2020 residual 7 monthly-only keys and 9 review-required roll-ups retain their separate open diagnostics. No child bars were synthesized.

## 4. G0 decision

**G0 = BLOCKED_GLOBAL.** The existing CP-0026 policy is date-level source selection, not the required row-level quarantine policy for CP-0107 unresolved conflicts. Official checksums establish byte identity/provenance, not canonical-source authority. The current source evidence does not justify silently choosing daily or monthly for the 52 economic-conflict keys.

This review does not assert that no research dataset can ever be built. It says the existing candidate-builder policy has not been shown to exclude every unresolved signal-influencing row. A separate candidate build using a frozen row-level quarantine manifest may be eligible for G0 review only after its inputs, exclusions, coverage/gaps, code/config hashes, and resulting dataset hashes are independently validated.

## 5. Required next implementation gate

Before any CP-0026 candidate rebuild:
1. Freeze a row-level exclusion manifest keyed by exact interval + raw `open_time` token/key, sourced from the verified CP-0041 worklist and CP-0107 derived disposition view.
2. Exclude all unresolved exact-key conflicts from signal, position, and valuation inputs; do not substitute a counterpart row and do not shift timestamps. Keep 450 off-grid monthly rows, 452 daily-only rows, 7 residual monthly-only rows, 52 economic conflicts, and 8 close-time-only cases separately traceable. Avoid double-counting overlapping cases.
3. Make the builder fail closed if an unresolved key is present in the candidate, if any exclusion cannot be joined exactly, or if gap/coverage/accounting checks fail.
4. Run deterministic tests against known fixtures, then build the candidate only from the already available verified archives. Record code/config/input/exclusion/output hashes and coverage/gap counts.
5. Re-run backtest only if the candidate dataset bytes change, as required by the existing project workflow. Historical results must be relabelled to the exact candidate hash and quarantine policy.

## 6. Current gate states and safety

G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.

No candidate rebuild or backtest was run. No raw archive was fetched or changed; no timestamps shifted/rounded; no rows merged/replaced/deleted; no synthetic candles; no source case closed; no strategy promoted. Live signing, public broadcast, and exchange orders remain blocked.
