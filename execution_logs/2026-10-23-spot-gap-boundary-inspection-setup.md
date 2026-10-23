# Execution log — Raw Spot 1m/5m gap-boundary inspection instrumentation
**Date:** 2026-10-23  
**Branch:** research/full-history-validation  
**Previous reconciliation run:** [39957820308](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39957820308)  
**Implementation commit:** `397f2aa8a5d78dc5dd6fa061e82f45275b540058`  
**Validation run:** [39959416562](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39959416562)

## Why
The prior diagnostic compared row counts and gap spans but did not preserve raw candle fields at the edges of a gap. To decide whether the validator's continuity rule is appropriate, the next report should show the last bars before and first bars after each discontinuity for both 1m and 5m.

## Change
- Updated `scripts/reconcile_btcusdt_spot_1m_5m_gaps.py` to include boundary-context rows with open time, OHLCV and raw close time around detected gaps for Spot 1m and Spot 5m.
- Kept checksum verification and explicit diagnostic-only limitations.
- No reconstruction, interpolation, gap filling, or silent candle exclusion was introduced.

## Verification status
- Prior run's `spot-1m-gap-audit` job succeeded and processed 12/12 months with zero script errors.
- In that same run, `long-history-validation` ultimately failed; full-history data gate remains blocked.
- New commit's validation run `39959416562` was queued at time of record. Do not claim the new report or code runtime has passed until job logs/artifact are inspected.

## Next
Inspect the new artifact's boundary rows and compare the exact 1m and 5m timestamps. Then review the monthly validator's assumptions and 2020-12 close-time anomaly. No walk-forward, PR merge, or live trading until the data policy is justified and full-history validation passes.
