# Project documentation and safety refresh — 2026-10-22

## Changes made
- Recreated `README.md` for this current-thread research project and added `CRYPTO_10CR_PROJECT_DETAILS.md` as the detailed project charter.
- Rewrote `CRYPTO_10CR_PROJECT_STATUS.md` as the current factual checkpoint and consolidated `CRYPTO_10CR_RESEARCH_LOG_HI.md` to version 1.5.
- Clarified the working target (1,000 USDT initial equity to 1,061,120.54 USDT at the recorded 22-Oct-2026 ₹94.24/USDT reference snapshot), and clarified that compounding means reinvesting realized net profit, not trading every hour.
- Reconciled all core files on the research truth state: real market-data integrity for this workstream is not verified, a cost-aware backtest has not been run, edge is not established, target time is unknown, live trading is not authorized, and tax/TDS is deferred.
- Updated `CURRENT_PROJECT_KEEP_PATHS.txt` to protect README, project details/status/log, code, tests, scripts, workflows and all execution logs.
- Refactored `scripts/cleanup_current_project.py` to read the committed keep-list, validate required paths, and fail closed if the list is missing, empty, or does not protect required files.
- Converted `.github/workflows/repository-cleanup-preview.yml` to a manual, read-only preview. It can no longer automatically commit or push deletions.
- Extended `.github/workflows/crypto-target-smoke.yml` to compile the maintenance helper, check required documents and target consistency, run the cleanup preview expecting zero deletion candidates, and execute unit tests.

## Verification initiated
- Workflow: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873
- Commit containing the updated CI checks: `c1f7464f91816ebbffd614ba857b66aa5b69db24`
- At the time this log was written, GitHub Actions had accepted the run but it was still queued; its final result must be reported only after polling GitHub.
- Code, workflow and documentation contents were read back from GitHub after the changes.

## Research boundary
This documentation/safety refresh has not downloaded market data and has not run a strategy backtest. No profitability or target-timeline claim is made. The next substantive research gate remains real BTCUSDT data acquisition and integrity validation.
