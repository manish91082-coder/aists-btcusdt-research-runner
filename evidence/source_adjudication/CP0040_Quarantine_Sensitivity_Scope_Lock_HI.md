# CP-0040 Quarantine Sensitivity Scope Lock — 2026-10-16

## Decision
Lock a **separate, diagnostic-only source-quarantine sensitivity** as the next research experiment. This is not candidate approval, does not open G0, and must not bypass the production CP-0026 builder gate.

## Frozen basis
- Rulebook SHA-256: `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
- G0 §18 requires unresolved source conflicts to remain `UNRESOLVED` and quarantine sensitivity to be separate from signal-influence research.
- G0 §19 permits a quarantine-based PASS only when unresolved items are explicitly quarantined and final metrics are based on that policy.
- G3 §38 requires source-policy/quarantine sensitivity reporting; material source-policy effects keep the data gate open unless source authority is adjudicated or the conservative quarantine policy is frozen.
- Current manifest: 1,427 unique exact keys, SHA-256 `e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a`.
- Eleven relationship-level blockers remain open; all 35 exact parent/child keys are represented, but exact-date official daily evidence is unavailable for all 11 cases.
- Existing frozen research decision: `MTF_BREAKOUT_4H_D1` is a research comparator only and failed the existing screen; no strategy currently passes the frozen acceptance gates. It is **not** being designated a selected or promoted strategy.

## Diagnostic scope
1. Comparator: `MTF_BREAKOUT_4H_D1` only, explicitly labelled consumed diagnostic / non-promotional comparator. Do not expand the strategy universe or tune parameters.
2. Compare the already recorded baseline source policy against the current exact-key quarantine policy. Use identical engine, fees, slippage, capital assumptions, date ranges, warm-up, and evaluation partitions where source evidence permits.
3. Apply the 1,427-key manifest by exact `(interval, open_time_ms)` identity only. Preserve raw timestamp tokens; no rounding, shifting, merging, gap filling, synthetic candles, or source canonicalization.
4. Report both signal/input-impact and metric deltas. Any unavailable inputs or non-comparable baseline outputs must be reported as `NOT_COMPUTABLE`, never inferred.
5. Do not write a production candidate dataset, change the CP-0026 builder's fail-closed behavior, remove any non-row blocker, or interpret the diagnostic as G0 PASS.
6. Required output: manifest and source hashes, exact row counts before/after quarantine by interval and class, signal/position change counts, baseline-versus-quarantine metrics and deltas if reproducible, tests, and an explicit limitations/decision section.
7. Do not use the result to promote the comparator. G0 remains blocked until the frozen rulebook conditions are actually satisfied; all 11 relationship cases remain open unless independent source evidence supports closure.

## Execution guard
The current production builder intentionally refuses candidate construction while 11 non-row blockers remain. The diagnostic must therefore be implemented as a **separate, explicitly named diagnostic path** with its own tests, not by weakening or overriding the production gate. If exact baseline candidate inputs/metrics cannot be reproduced from committed evidence and verified caches without re-running acquisition, stop with `BLOCKED_INPUTS_NOT_REPRODUCIBLE` and publish that result rather than inventing a comparison.

## Current status
- Scope locked: YES.
- Diagnostic implementation/execution: NOT YET RUN.
- Candidate build/backtest through production path: NOT RUN.
- G0: `BLOCKED_GLOBAL`.
- Strategy promotion/live actions: BLOCKED.
