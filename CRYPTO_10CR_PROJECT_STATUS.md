# Current Project Status — 1,000 USDT to Target USDT
**Updated:** 2026-10-22 (cleanup-script checkpoint)  
**Status:** RESEARCH HARNESS ADDED; CLEANUP SCRIPT COMMITTED; CLEANUP NOT RUN; NO PROFITABLE STRATEGY VERIFIED

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


## Latest checkpoint — 2026-10-22
- Current research workstream: 1,000 USDT → 1,061,120.54 USDT target snapshot; compounding means reinvesting realized profits, not trading only on 1h candles.
- GitHub files created: `CRYPTO_10CR_RESEARCH_LOG_HI.md`, `CRYPTO_10CR_PROJECT_STATUS.md`, `crypto_target/research_math.py`, `crypto_target/__init__.py`, `tests_crypto_target/test_research_math.py`, `.github/workflows/crypto-target-smoke.yml`, and an append-only execution log under `execution_logs/`.
- Code readback verified; automated workflow result still pending verification. No market-data or strategy performance result claimed.
- Next action: verify GitHub Actions run, record result in a new execution-log file, then build real data manifest and baseline backtests.


## Cleanup-script checkpoint — 2026-10-22
- Guarded script committed to `scripts/cleanup_current_project.py` on `main`.
- Commit: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/1bd521dfa8bb2739b78846c16985e103908d51e9
- Direct script link: https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/scripts/cleanup_current_project.py
- Readback verified from GitHub after commit.
- Default mode is dry-run. Applying requires `--apply` and the exact repository confirmation; it stages tracked-file deletions but does not commit/push. It preserves only the explicit allowlist and named prefixes; user must inspect preview before applying.
- Cleanup has **not** been executed. No old files were deleted by this step.
- Important scope note: the script intentionally does not erase Git history or other branches and does not touch untracked/ignored files.
