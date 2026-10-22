# Current Project Status — 1,000 USDT to Target USDT
**Updated:** 2026-10-22 (cleanup complete and verified)  
**Status:** LEGACY REPOSITORY CLEANUP COMPLETE; CRYPTO-TARGET FILES PRESERVED; NO PROFITABLE STRATEGY VERIFIED

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
- Added baseline math helpers/tests and CI workflow. GitHub Actions smoke run passed: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39793473617.
- No historical market data downloaded or backtest run for the 1,000 USDT target project in this checkpoint.
- Later verified cleanup removed 30 legacy tracked paths (old audit documentation, tests, scripts and obsolete workflows). The active crypto-target allowlist was preserved. Git history and other branches remain intact.

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
Next: build the real market-data manifest/acquisition validation, then run cost-aware multi-horizon baselines. Cleanup was repository housekeeping only; no market-data backtest was performed. Record every substantive execution as a separate append-only log file.


## Latest checkpoint — 2026-10-22
- Current research workstream: 1,000 USDT → 1,061,120.54 USDT target snapshot; compounding means reinvesting realized profits, not trading only on 1h candles.
- GitHub files created: `CRYPTO_10CR_RESEARCH_LOG_HI.md`, `CRYPTO_10CR_PROJECT_STATUS.md`, `crypto_target/research_math.py`, `crypto_target/__init__.py`, `tests_crypto_target/test_research_math.py`, `.github/workflows/crypto-target-smoke.yml`, and an append-only execution log under `execution_logs/`.
- Code readback verified; the crypto-target smoke-test workflow succeeded (run link above). This verifies helper/unit tests only, not market-data validation or strategy profitability.
- Next action: verify GitHub Actions run, record result in a new execution-log file, then build real data manifest and baseline backtests.


## Cleanup-script checkpoint — 2026-10-22
- Guarded script committed to `scripts/cleanup_current_project.py` on `main`.
- Commit: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/1bd521dfa8bb2739b78846c16985e103908d51e9
- Direct script link: https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/scripts/cleanup_current_project.py
- Readback verified from GitHub after commit.
- Default mode is dry-run. Applying requires `--apply` and the exact repository confirmation; it stages tracked-file deletions but does not commit/push. It preserves only the explicit allowlist and named prefixes; user must inspect preview before applying.
- At the time this script-addition checkpoint, cleanup had not yet run. The later final cleanup execution is recorded below.
- Important scope note: the script intentionally does not erase Git history or other branches and does not touch untracked/ignored files.


## Final cleanup verification — 2026-10-22
- GitHub Actions cleanup run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39806484233 (conclusion: success).
- Cleanup commit: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/0042c045702efa91a2a50d2672c6079c67edbb62; follow-up cleanup-transcript removal: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/f06eb8bb296d3e4e934bb9e40b395fac93bf352a.
- GitHub recursive tree verified 30 legacy tracked paths removed; active crypto-target files remained present.
- Final outcome log: `execution_logs/2026-10-22-cleanup-final-verification.md`. The ephemeral run transcript was removed from repository root after report artifact generation.
- Git history/other branches unchanged; no live trading and no market-data backtest performed.
- Next research step: real official market-data provenance/checksum/schema/gap validation, then cost-aware baseline tests.


## Strict current-thread-only cleanup — 2026-10-22
- User clarified that only files created for this crypto-target research thread today should remain; all pre-existing repository files should be removed.
- Removed the pre-existing `README.md` and removed it from the cleanup script and keep-list.
- GitHub recursive tree verification at main head `1a673787c62b41305a92f3c3df5be89b552902af` found exactly the 14 intended current-thread files; none missing and no unexpected files. The follow-up verification log is `execution_logs/2026-10-22-current-thread-only-cleanup.md`.
- This is a repository-scope cleanup only. Market-data acquisition/backtesting remains undone, strategy edge is NOT ESTABLISHED, time to target is UNKNOWN, live trading NOT AUTHORIZED, and tax/TDS deferred.
