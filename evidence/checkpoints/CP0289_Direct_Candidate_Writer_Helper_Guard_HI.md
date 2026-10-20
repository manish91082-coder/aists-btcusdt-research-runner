# CP-0289: Direct Candidate Writer Helper Guard Audit (Hindi)

**Checkpoint:** CP-0289  
**Implementation/test HEAD:** `1fa01f7053384ac370a452025019c0fcdbd78c01`  
**Exact-HEAD CI:** [GitHub Actions run 39383135220](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39383135220), terminal `success`.

## 1. Finding

CP-0288 protected the direct CLI production path for CP-0026 candidate generation. A follow-on static inspection found two imported callable helpers that write candidate artifacts:
- `audit_and_write_interval(...)` writes interval candidate CSV.GZ files.
- `create_monthly_from_daily(...)` writes the derived 1mo candidate CSV.GZ.

Relying only on `main()`'s guard would leave these public helper entrypoints callable directly by another Python module. The helper APIs therefore needed their own fail-closed authorization boundary.

## 2. Implemented change

- Public `audit_and_write_interval(...)` now invokes `require_authenticated_g0("cp0026_candidate_builder")` before delegating to `_audit_and_write_interval_test_only(...)`.
- Public `create_monthly_from_daily(...)` now invokes the same guard before delegating to `_create_monthly_from_daily_test_only(...)`.
- The existing production `main()` guard remains in place, so authorization is checked before reading the data root or writing candidate artifacts.
- The explicit `--gate-self-test` route remains separate and returns before the production guard; it exercises only the quarantine gate with supplied test fixtures, not a market-data candidate build.
- Synthetic quarantine unit tests were updated to call the explicitly named test-only monthly implementation. These test-only helpers are not trusted authorization and must never be used for a production candidate build.
- Static AST regression coverage now verifies the guard appears at the start of each public writer helper and in the production entrypoint.

## 3. CI evidence and correction history

- Intermediate CI attempts failed while this refactor was being completed. One run exposed two synthetic quarantine tests calling the now-guarded public monthly writer; another exposed a test's AST assertion not accounting for the wrapper docstring. Both issues were inspected and corrected.
- Final implementation/test HEAD: `1fa01f7053384ac370a452025019c0fcdbd78c01`.
- [Exact-HEAD run 39383135220](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39383135220): terminal `success`.
- Compile step: PASS.
- Brain unit tests: 226 passed.
- CP-0026 exact-key quarantine enforcement tests: 11 passed.
- New guard regression test `test_direct_cli_entrypoints_call_guard_before_work`: PASS.

## 4. Scope boundary

No production candidate build, market-data acquisition, historical replay, backtest, or paper session was run. No candidate dataset was written. No exchange order, signing, or broadcast was attempted. This change hardens an execution boundary; it does not adjudicate G0 or establish profitability.

## 5. Current mission state

- G0: `BLOCKED_GLOBAL`; canonical historical source: `NONE`.
- G1: `PARTIAL_SYSTEM_LEVEL`.
- G2: candidates `FAIL / NOT PROMOTED`.
- G3: blocked pending adjudication and quarantine-effect reconciliation.
- G4: `INSUFFICIENT_EVIDENCE`.
- G5: `NOT_RUN`.
- G6: `NOT_BUILT / NOT_VALIDATED`.
- G7: `LIVE_BLOCKED`.
- Profitability: `NOT ESTABLISHED`.
- PR #2 remains open and unmerged.

**Mission navigation:** CP-0289 closes the direct-import writer-helper gap at the public API boundary. G0 remains blocked for lack of independent clause-level source-authority adjudication. The next task must pursue genuinely new authoritative evidence or an authorized reviewer decision, not manufacture a PASS or repeatedly rescan unchanged evidence.
