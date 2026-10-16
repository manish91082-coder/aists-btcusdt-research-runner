# CP-0107 Shared-52 candidate-input dependency audit

Status: PASS_SHARED52_CANDIDATE_INPUT_DEPENDENCY_MAP_COMPLETE_NOT_G0_APPROVAL

## Frozen comparator and direct-input overlap
- Comparator: MTF_BREAKOUT_4H_D1; direct intervals are 4h local bars and completed 1d regime.
- Shared-52 economic conflicts: 52. Direct-input overlaps: 4 (2 x 4h, 2 x 1d); remaining 48 are in other intervals and are not direct inputs for this comparator.
- All 52 exact (interval, open_time_ms) keys join the frozen CP-0040 quarantine manifest by key/case ID and remain unresolved, canonical source NONE, case_closed false.

| Case | Interval | UTC open | Official update bundle exact daily path | Exact-key quarantined | Disposition |
|---|---|---|---|---|---|
| SHARED-1d-1611187200000 | 1d | 2021-01-21T00:00:00Z | False | True | OPEN |
| SHARED-4h-1611216000000 | 4h | 2021-01-21T08:00:00Z | False | True | OPEN |
| SHARED-1d-1640304000000 | 1d | 2021-12-24T00:00:00Z | False | True | OPEN |
| SHARED-4h-1640304000000 | 4h | 2021-12-24T00:00:00Z | False | True | OPEN |

## Already-published full-manifest sensitivity
- Exact-key rows removed: 4h=6, 1d=3, 1mo=0; replacements added=0.
- Return delta: TRAIN -15.891741 percentage points; DEVELOPMENT_CHECK 0.000000; CONSUMED_OOS_DIAGNOSTIC 0.000000.
- These are full-manifest results; impact attributable to only the four direct Shared-52 cases is NOT_ESTABLISHED because a four-row ablation was not run.

## Official correction-package limit
- The previously verified official 2022-08-08 correction bundle has 2 non-directory members, no target monthly archive members, 0 target filename text references and 0 current frozen monthly SHA token references.
- For Shared-52, the bundle has exact daily paths for 33 cases and none for 19. All four direct 4h/1d cases fall in the no-exact-path group.
- Bundle-path absence is not evidence that the archive never existed; New checksum matches for 33 other cases are provenance evidence only.

## Decision
- Keep all 52 cases open; no canonical source selected; root cause OPEN_NOT_ESTABLISHED; all 11 non-row aggregation blockers open; G0 BLOCKED_GLOBAL.
- Next: verify the frozen CP-0040 rulebook bytes against the original source pack and make a rulebook-bound candidate eligibility decision. Do not weaken the CP-0026 builder gate.
- No network, archive download, data edits, candidate build, backtest rerun, strategy promotion or live actions occurred.
