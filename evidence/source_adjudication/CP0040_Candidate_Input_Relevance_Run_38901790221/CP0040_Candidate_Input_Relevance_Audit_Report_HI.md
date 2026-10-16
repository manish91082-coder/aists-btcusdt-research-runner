# CP-0040 Candidate-input relevance audit: MTF_BREAKOUT_4H_D1

Status: PASS_CANDIDATE_INPUT_RELEVANCE_REVIEW_COMPLETE_NOT_G0_APPROVAL

## What is now proven
- Frozen CP-0031 engine hash matches the recorded anchor; MTF_BREAKOUT_4H_D1 uses 4h local bars with completed 1d regime.
- All 11 open aggregation relationships involve only these intervals: 15m, 1h, 30m, 5m. None overlaps the comparator's direct 4h/1d interval pair.
- All 11 have both monthly/daily archive integrity authenticated; all 11 daily roll-ups match their daily parents, while the monthly mismatch signature persists.
- The complete 1,427-key quarantine manifest was applied in the previous sensitivity run: 4h removed 6 rows; 1d removed 3; 1mo removed 0; replacements added 0.
- Net-return delta from frozen baseline under exact-key quarantine: TRAIN -15.891741 percentage points; DEVELOPMENT_CHECK 0.000000; CONSUMED_OOS_DIAGNOSTIC 0.000000.

## Decision boundary
- The 11 lower-timeframe relationships have no direct interval overlap with this comparator. That is not a claim that the conflicts are solved, nor that their source authority is known.
- The exact-key sensitivity still materially changes TRAIN results. The current CP-0026 production builder continues to fail closed on any non-row blockers.
- Therefore this review does not grant G0 PASS, does not build a production candidate, and does not promote the comparator.

## Gates
- All 11 relationship cases remain open; root cause OPEN_NOT_ESTABLISHED; canonical source NONE.
- G0 BLOCKED_GLOBAL; G2 existing strategy screen still applies; live signing, broadcast and exchange orders remain BLOCKED.
- No downloads, network activity, source mutation, candidate build or backtest rerun occurred in this audit.

## Next bounded action
- Stop repeating archive-provenance checks for the same 11 buckets unless genuinely new evidence arrives.
- Resolve the frozen-rulebook decision for the full row-level quarantine policy and candidate-specific eligibility; preserve the fail-closed production gate until that decision is complete.
