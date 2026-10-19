# CP-0274 — Synthetic-only decision-pipeline integration check

**Status:** First exact-head run failed on a test assertion contract; assertion corrected; run 39310148650 completed successfully on test commit `c3c4d8d71cf1f4fc85fbd52827f6d9eebef0ed8a` with 203 tests passing. Final verification: run [39310290550](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39310290550) completed successfully on test commit `8265776eb57b878004a40aaca73440859f8dafce`; compile passed and all 203 tests passed (`OK`).  
**Branch:** `cp-0120-ai-brain-foundation`  
**Scope:** Software integration only. No real BTCUSDT data or performance evaluation.

## Change

Added `tests/test_market_synthetic_pipeline_integration.py` to exercise the existing causal decision producer, offline next-open simulator, paper ledger, and independent accounting reconciliation in one deterministic software test path.

The fixtures are generated in test code, carry an explicitly synthetic source hash, and must not be interpreted as market evidence. The test checks decision schema/safety metadata, offline-only simulator status, and arithmetic reconciliation. A second test confirms a timestamp gap is rejected rather than repaired.

## Gate and safety boundary

- G0 remains `BLOCKED_GLOBAL`; canonical historical source remains `NONE`.
- No production candidate build, historical backtest, paper trading session, or profitability evaluation was run.
- This test does not adjudicate provenance, authenticate any external G0 claim, or validate strategy quality.
- Live signing, public broadcast, exchange orders, and automatic SL/TP remain disabled/not implemented.
- CP-0040 frozen rulebook and quarantines are unchanged.
- PR #2 remains open and unmerged.

## Verification required

Run 39309983355 exposed one test-only mismatch: `verify_ledger()` returns a status mapping, not boolean `True`. The assertion was corrected to require `PASS_HASH_CHAIN`; run 39310148650 then completed successfully, with compile success and `Ran 203 tests ... OK`. Final exact test-code head `8265776eb57b878004a40aaca73440859f8dafce` passed run 39310290550 with 203 tests (`OK`), including both new integration tests. PR #2 was confirmed open. This closes CP-0274 as a software-integration checkpoint only; no market-performance gate is changed. Do not convert synthetic test outcomes into market-performance claims.
