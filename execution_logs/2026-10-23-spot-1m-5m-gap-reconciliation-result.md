# Execution log — Spot 1m/5m gap reconciliation runtime result
**Date:** 2026-10-23  
**Branch:** research/full-history-validation  
**Workflow:** [39957820308](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39957820308)  
**Workflow commit:** `d6d2237067d9fd693eae6decade6fdcc733f0187`

## Runtime result
- Job `spot-1m-gap-audit`: SUCCESS.
- Python compilation of both audit/reconciliation scripts: PASS.
- Strict Spot 1m monthly audit: 0/12 PASS, expected given previously reported gaps; the step was allowed to continue solely to run reconciliation.
- Spot 1m/5m comparison: 12/12 months processed, 0 script errors.
- Combined artifact: [12502189825](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39957820308/artifacts/12502189825), 26,780,461 bytes, expires 2026-11-22.

## Findings
All 12 affected months have timestamp gaps in the official Spot 5m archive as well as the official Spot 1m archive. The per-month summaries report matching 1m/5m gap counts; missing-row deficits are compatible with shared gap intervals (e.g. 2020-02 has 414 fewer 1m rows and 82 fewer 5m rows; 2020-11 has 60 and 12 respectively). All monthly statuses are `INSPECT`, not PASS. The script's output is descriptive and does not establish why those intervals are absent, nor whether the correct interpretation is no trades, source omissions, or a validator assumption issue. The known 2020-12 close-time anomaly remains unresolved.

## Decision
Do not reconstruct, interpolate, or silently omit data. The next task is to inspect the raw rows around the exact missing-span boundaries for both intervals and review the validator's assumptions against official Binance kline semantics. Only after that review can a data policy be proposed.

## Scope / limitations
- No candles were synthesized or excluded.
- No strategy backtest or walk-forward was run from this diagnostic.
- The separate `long-history-validation` job in the same workflow was still in progress at the time of this record; its final outcome is not claimed here.
- PR #17 remains unmerged. No live trading or funds movement.
