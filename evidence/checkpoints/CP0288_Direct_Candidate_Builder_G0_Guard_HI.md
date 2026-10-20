# CP-0288: Direct Candidate Builder G0 Guard (Hindi)

**Checkpoint:** CP-0288  
**Implementation HEAD before this report:** `10e81d92acb144f1dd370c370dd5f7cc05fcb87c`  
**Verified CI on implementation HEAD:** [Run 39382585466](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39382585466), terminal `success`.

## 1. Inspection finding

CP-0286 guarded historical replay, legacy pipeline, baseline backtest, and quarantine sensitivity tasks. A static entrypoint audit found that `scripts/AISTS_CP0026_Research_Candidate_Builder.py` had a production `main()` path that did not call the shared G0 execution guard. Its own CP-0040 manifest/quarantine checks are not a substitute for global G0 authorization. This was a potential policy bypass even though the candidate builder was not run.

## 2. Change implemented

- Added `cp0026_candidate_builder` to `G0_PROTECTED_TASKS` in `scripts/g0_execution_guard.py`.
- The production branch of `AISTS_CP0026_Research_Candidate_Builder.py` now calls `require_authenticated_g0("cp0026_candidate_builder")` after the explicit `--gate-self-test` branch returns and before reading the data root or writing candidate artifacts.
- The synthetic/manifest-only `--gate-self-test` path remains available for deterministic safety testing; it does not invoke a production candidate build.
- Extended `tests/test_market_g0_execution_guard.py` to assert that the candidate-builder task is protected and that its direct production entrypoint calls the guard after the self-test early return.

## 3. Verification

Exact implementation HEAD: `10e81d92acb144f1dd370c370dd5f7cc05fcb87c`

- [GitHub Actions run 39382585466](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39382585466): terminal `success` on the exact implementation HEAD.
- `Compile brain modules`: PASS.
- Brain unit tests: 226 passed.
- CP-0026 exact-key quarantine enforcement tests: 11 passed.
- The new regression assertions `test_all_historical_simulation_entrypoints_are_protected` and `test_direct_cli_entrypoints_call_guard_before_work` passed.
- Earlier intermediate commits in the same edit sequence produced failing CI because the guard-set test had not yet been updated. Those failures were inspected; the final implementation HEAD above is the tested, passing state.

## 4. Scope boundary

No candidate builder production run, market-data download, historical replay, backtest, paper session, Binance order, signing, or broadcast was executed. No data artifact was created or modified. This is an authorization hardening change, not a G0 adjudication and not evidence of strategy profitability.

## 5. Gate and PR state

- G0: `BLOCKED_GLOBAL`; canonical historical source: `NONE`.
- G1: `PARTIAL_SYSTEM_LEVEL`.
- G2 candidates: `FAIL / NOT PROMOTED`.
- G3: blocked pending adjudication and quarantine-effect reconciliation.
- G4: `INSUFFICIENT_EVIDENCE`.
- G5: `NOT_RUN`.
- G6: `NOT_BUILT / NOT_VALIDATED`.
- G7: `LIVE_BLOCKED`.
- Profitability: `NOT ESTABLISHED`.
- PR #2 remains open and unmerged by design.

**Mission navigation:** CP-0288 closes a discovered direct candidate-build guard gap at code level. The external source-authority/adjudication dependency remains unresolved. Next admissible work must produce genuinely new, clause-eligible evidence or an authorized independent decision; no synthetic G0 PASS is allowed.
