# CP-0291 — Multi-timeframe Candidate Contract Hardening (Hindi)

**Checkpoint:** CP-0291  
**Implementation/test HEAD:** `def8a9208cf2ae1bae9b6a5f0980e24be43abbfb`  
**Exact-HEAD CI:** [GitHub Actions run 39390227679](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39390227679), terminal `success`.  
**Branch:** `cp-0120-ai-brain-foundation`  
**PR #2:** open, unmerged.

## 1. Goal-directed finding

The multi-timeframe selector previously treated an unrecognized candidate action as if it were simply ineligible, and accepted any non-empty strategy-family string. That could silently hide malformed candidate-evaluation output and allow an unsupported strategy label to enter a consensus result. It also rejected only truthy `is_order_instruction` values, rather than enforcing a strict boolean false contract.

This was a concrete G1 decision-boundary weakness that could affect G2 candidate eligibility. It could be corrected without accessing historical market data, altering CP-0040, promoting a candidate, or running a backtest.

## 2. Implemented

In `aists_brain/multi_timeframe_selector.py`:

- Reject non-mapping candidate evaluations.
- Require `is_order_instruction` to be exactly boolean `False` when supplied; malformed values fail closed.
- Accept only `NO_TRADE` or `LONG_CANDIDATE` as candidate actions; unknown values raise an error rather than silently disappearing from consensus.
- Require `NO_TRADE` entries to have no selected strategy.
- Allow only the three declared strategy families: `TREND_FOLLOWING`, `BREAKOUT`, and `MEAN_REVERSION`.
- Preserve existing abstention on missing timeframe evidence, directional conflict, strategy-family disagreement, weak confirmation, and strategy conflict.

Regression tests added in `tests/test_market_multitimeframe_selector.py` for unknown action, unsupported strategy, inconsistent NO_TRADE, non-boolean order flag, and non-mapping candidate. The existing weak-confirmation fixture was corrected to represent a valid NO_TRADE record.

## 3. Verification

- First test run [39390168852](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39390168852) failed on a stale expected error-message substring. The log was inspected, the assertion was corrected, and the suite was rerun.
- Final exact-HEAD run [39390227679](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39390227679): terminal `success`.
- Python compile step: PASS.
- Brain unit tests: **231 passed**.
- CP-0026 exact-key quarantine enforcement tests: **11 passed**.
- The regression tests explicitly passed in the final log.

## 4. Gate effect and limitations

This is software-contract hardening only. It does not establish strategy edge, historical eligibility, data provenance, quarantine clearance, or profitability.

- G0: `BLOCKED_GLOBAL`, parked and unchanged; canonical historical source remains `NONE`.
- G1: improved selector input validation; overall status remains `PARTIAL_SYSTEM_LEVEL`.
- G2: all 23 existing historical candidates remain `FAIL / NOT PROMOTED`. No candidate was promoted.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`, unchanged.
- G4: `INSUFFICIENT_EVIDENCE`.
- G5: `NOT_RUN`.
- G6: `NOT_BUILT / NOT_VALIDATED`.
- G7: `LIVE_BLOCKED`.
- Profitability: `NOT ESTABLISHED`.

No real market data was read, no candidate build/backtest/paper session was run, CP-0040 was not modified, and no signing, broadcast, exchange order, or automatic SL/TP was enabled.

## 5. Next goal-directed step

Continue the G1–G3 audit from this verified point. Prioritize the next concrete defect in causal decision/eligibility/quarantine wiring. Do not reopen G0 source discovery unless genuinely new admissible evidence appears; do not treat this selector fix as a historical gate pass.
