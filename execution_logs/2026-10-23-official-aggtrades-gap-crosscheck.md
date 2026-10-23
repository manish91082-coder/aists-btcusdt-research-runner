# Official Spot aggTrades gap cross-check

**Date:** 23 October 2026  
**Branch:** `research/full-history-validation`  
**Workflow run:** [39970944134](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39970944134)

## Purpose
Independently check whether official Spot BTCUSDT aggregate-trade records exist inside the exact UTC windows where the official Spot 1m and 5m kline archives have timestamp gaps.

## Implementation
- Added `scripts/audit_btcusdt_spot_aggtrades_in_gaps.py`.
- Downloads official monthly Spot `aggTrades` ZIP files and their `.CHECKSUM` sidecars for the 12 affected months.
- Verifies SHA256 and counts aggregate-trade rows within the previously recorded UTC gap windows.
- Emits a JSON report and per-month log lines; never fills, reconstructs, or drops candles.
- Added the script to `CURRENT_PROJECT_KEEP_PATHS.txt` and wired a separate workflow job plus artifact upload.

## CI correction notes
An intermediate workflow edit accidentally introduced a literal escaped newline in the path filter, making that workflow revision invalid. The path filter was corrected. An interim smoke test also failed because the new script had not yet been added to the protected keep-list; the script was then added. These were workflow/governance failures, not market-data findings. Final run status must be checked before interpreting any results.

## Evidence status
At the time of this record, run `39970944134` was in progress. No aggTrades count or cause-of-gap conclusion is claimed yet.

## Decision
Keep the archive gate closed. A positive aggTrades count inside a gap would show that trades occurred there, but a zero count alone does not prove archive completeness or justify relaxing the kline continuity rule. No candle synthesis, silent exclusions, walk-forward research, PR merge, or live trading.
