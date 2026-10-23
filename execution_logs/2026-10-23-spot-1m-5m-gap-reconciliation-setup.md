# Execution log — Spot 1m/5m gap reconciliation setup
**Date:** 2026-10-23  
**Branch:** research/full-history-validation  
**Status:** Implemented; workflow runtime verification pending.

## Reason
The long-history gate found 12 failed Spot 5m months. A separate audit found missing rows and timestamp gaps in all 12 official Spot 1m archives, despite checksum matches. A checksum proves downloaded bytes match the publisher's sidecar; it does not prove temporal completeness.

## Implementation
- Added `scripts/reconcile_btcusdt_spot_1m_5m_gaps.py`.
- For each affected month, downloads official Spot 1m and 5m monthly ZIPs and validates their official SHA-256 sidecars.
- Records row counts, expected counts, first/last timestamps, timestamp gaps/order anomalies and exact 1m missing spans.
- Does not fill rows, interpolate, reconstruct candles, or assert that missing bars are valid no-trade intervals.
- Added the script to the repository keep-list and the long-history workflow. The audit is non-blocking only so the diagnostic comparison still runs; the overall data gate remains blocked.

## Verification still required
- Confirm workflow job starts, Python compilation passes, and the diagnostic JSON artifact is uploaded.
- Inspect whether 5m gaps overlap the 1m gap spans month by month.
- Then inspect validator assumptions and official archive behavior before deciding a data policy.
- No full-history backtest, walk-forward, PR merge, or live trading authorization.
