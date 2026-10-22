# Current Project Status — 1,000 USDT to Target USDT
**Updated:** 2026-10-22  
**Status:** RESEARCH BOOTSTRAP IN PROGRESS; NO PROFITABLE STRATEGY VERIFIED

## Goal
Turn 1,000 USDT into **1,061,120.54 USDT** (approximate ₹10 crore equivalent at the 2026-10-22 reference snapshot ₹94.24/USDT). Hourly means reinvest each realized net profit into account equity; it does not constrain the strategy to 1-hour candles.

## Active scope
- Focus on the fastest *defensible* route supported by evidence.
- Explore multiple timeframes and strategy families, not just one-hour candles.
- Include actual transaction costs and risk of ruin.
- Tax/TDS analysis deferred.
- No credentials, live orders, funds movement or production deployment.

## Repository discovery
- Public repository: https://github.com/manish91082-coder/aists-btcusdt-research-runner
- Default branch: main
- Repository already contained an established research/data-audit project with governance files, scripts, tests and GitHub Actions workflows. Existing governance explicitly requires preserving history/branches, verified writes and fail-closed research gates.
- Current verified project record before this new work: HD-03 accepted for one September 2026 BTCUSDT 5m monthly archive pilot; HD-04 older-month check was next. This is not strategy-performance evidence.

## Work in this checkpoint
- Added a dedicated USDT-target research dossier and status file.
- Added new baseline code/tests and CI workflow are planned as the next implementation checkpoint; not yet verified until GitHub Actions run is observed.
- No historical market data downloaded or backtest run for the 1,000 USDT target project in this checkpoint.
- Existing code has not yet been deleted. A safe complete file inventory and impact review are required before mass deletion, because that could remove the existing archive audit, tests and workflow used by the prior project. Git history must remain intact.

## Evidence gates
1. Code/unit tests pass in GitHub Actions.
2. Real market data provenance/checksum/schema/gap validation.
3. No-look-ahead strategy implementation.
4. Cost-adjusted walk-forward out-of-sample edge.
5. Drawdown/ruin-risk and parameter-sensitivity analysis.
6. Paper forward validation.
7. Explicitly approved live stage only, if ever.

## Current decision
**No strategy is proven profitable; time to target is unknown.** Do not turn a hypothetical compound-growth curve into a forecast.

## Next action
Create and test a small baseline harness, confirm the actual CI run, then build the data pipeline and multi-horizon strategy comparisons. Record every execution as a separate append-only log file and update this status on each substantive response.
