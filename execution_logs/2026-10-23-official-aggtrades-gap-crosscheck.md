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


## Follow-up: targeted daily archive run completed

**Workflow run:** [39997643479](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39997643479)  
**Head commit at run:** `f90242d73a68f473ebdf5c2fc6fd9a47784cbc5c`  
**Audit job:** `spot-aggtrade-gap-audit`, conclusion `success`

### Method adjustment
The first monthly-archive approach was repeatedly cancelled during execution. The script was changed to fetch only official daily Spot BTCUSDT aggTrades ZIPs for dates overlapping each pre-registered gap, plus each `.CHECKSUM` sidecar. This change made the complete 12-month diagnostic finish in about 80 seconds. Script source comments and report source metadata were subsequently corrected from “monthly” to “daily.”

### Results
- 12 of 12 affected months completed; 15 of 15 configured gap windows were evaluated.
- Every downloaded daily archive SHA256 matched its official sidecar.
- Every configured gap reported `trade_rows: 0`; `first_trade_utc` and `last_trade_utc` were null for all gaps.
- Artifact: [`btcusdt-spot-aggtrade-gap-audit`](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39997643479/artifacts/12520687183).
- These results describe the downloaded archive contents and the current parser. They do not establish that no trades occurred, that the archive is complete, or why the kline gaps exist. A checksum validates bytes against the sidecar, not market-event completeness.

### Parallel gate status
The same workflow run’s full-history validator remains failed closed at 231/243 archive checks, with 12 Spot 5m monthly checks failing. It did not emit a normalized full-history dataset. The Spot 1m diagnostic completed successfully. No continuity rule was relaxed and no candles were reconstructed or excluded.

### Next actions
1. Independently verify aggTrades CSV schema and timestamp-column interpretation against official documentation/sample rows before treating zero counts as reliable.
2. Inspect the exact raw 2020-12 anomalous close-time row (`open_time=1608559500000`, raw `close_time=1608558440521`) and its neighboring rows; preserve raw values and fail closed.
3. Re-run only after adding a parser/schema assertion or a focused test; keep PR #17 unmerged and do not start walk-forward until the full archive gate passes.
