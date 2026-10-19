# CP-0274 — Synthetic-only decision-pipeline integration check

**Status:** Implementation committed; exact-head CI and test result pending.  
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

The new test file was committed, but this checkpoint is not complete until GitHub Actions runs against the exact resulting branch head and its terminal result, test count, and PR state are inspected. If the synthetic integration test fails, fix only the demonstrated defect and rerun exact-head CI. Do not convert synthetic test outcomes into market-performance claims.
