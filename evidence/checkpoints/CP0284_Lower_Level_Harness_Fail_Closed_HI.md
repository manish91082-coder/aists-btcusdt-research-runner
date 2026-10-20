# CP-0284: Lower-Level Harness Fail-Closed Authorization Boundary (Hindi)

तिथि: 2026-10-20  
Canonical branch: `cp-0120-ai-brain-foundation`  
Code/test HEAD verified before this report: `333ab6a5c3f6c410702f5750bfe736a6fa8f501f`  
Scope: offline code and synthetic unit tests only. No candidate build, historical backtest, paper session, real market-data run, or exchange action.

## 1. Problem

CP-0283 found that the lower-level public functions in `aists_brain/research_harness.py` could accept caller-supplied PASS claims and proceed to simulation after input validation. CP-0282 guarded the orchestration entrypoint, but did not independently guard direct calls to these lower-level functions.

## 2. Change

- Renamed the existing simulation implementations to explicitly test-only private helpers:
  - `_run_manifest_driven_simulation_test_only`
  - `_run_manifest_driven_simulation_from_stored_features_test_only`
- The public `run_manifest_driven_simulation(...)` API now immediately raises `ResearchHarnessError` with `G0_EVIDENCE_NOT_AUTHENTICATED`.
- The public `run_manifest_driven_simulation_from_stored_features(...)` API does the same before opening input paths or loading stored artifacts.
- Synthetic fixture tests were redirected to the explicitly test-only helpers; they do not authenticate source authority or authorize production execution.
- Added direct-call regression tests for both public APIs using nonexistent input paths. Both assert the unauthenticated G0 block occurs first.
- No production candidate build, backtest, paper session, source selection, candidate promotion, or exchange action was run.

## 3. Exact-head CI evidence

- Code/test HEAD: `333ab6a5c3f6c410702f5750bfe736a6fa8f501f`
- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39379492240
- Terminal conclusion: `success`.
- Brain unit suite: 222 tests passed.
- CP-0026 exact-key quarantine suite: 11 tests passed.
- Compile step: success.
- Direct public-call regressions passed for both regular and stored-feature APIs.
- Earlier intermediate commits in this patch series had failing CI due to a stale test callsite. That callsite was corrected; the final exact-head run above is the successful result.

## 4. Security boundary and limitation

This change disables the public simulation APIs until a trusted, independently verified G0 receipt verifier is integrated. The underscore-prefixed helpers are intended solely for synthetic software tests; Python naming is not a cryptographic security boundary and should not be described as one. The next integration must not make a caller-provided string or Boolean PASS sufficient authorization. No trusted G0 receipt verifier has been implemented by this checkpoint.

## 5. Gate status (unchanged)

- G0: `BLOCKED_GLOBAL`; canonical historical source: `NONE`.
- G1: `PARTIAL_SYSTEM_LEVEL`.
- G2: current 23 candidates `FAIL`; none promoted.
- G3: blocked; material quarantine effects unresolved.
- G4: `INSUFFICIENT_EVIDENCE`.
- G5: `NOT_RUN`.
- G6: adaptive AI `NOT_BUILT / NOT_VALIDATED`.
- G7: `LIVE_BLOCKED`; live signing and public broadcast remain blocked.
- Profitability: `NOT ESTABLISHED`.

## 6. Next bounded action

Continue source inventory for any other public simulation or execution primitives that can bypass these public wrappers, especially direct calls to the simulator. Then design an independently verifiable G0 authorization receipt that is bound to the frozen CP-0040 hashes and unresolved-population status. Do not run production research until that authority is independently adjudicated and G0 is formally closed.
