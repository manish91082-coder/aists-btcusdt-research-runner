# Documentation refresh — final repository verification — 2026-10-22

## Main-branch snapshot checked
- Repository: https://github.com/manish91082-coder/aists-btcusdt-research-runner
- Branch: `main`
- Commit at the snapshot check: `d3511f173d084c69abecf4213aa858b228cf6d43`
- Recursive GitHub tree contained 18 tracked files before this verification log was added.
- All expected core files were present: README, detailed project charter, status, master research log, keep-list, cleanup utility, helper code, unit tests, and both workflows.
- Every tracked path in that snapshot was manually matched to either an exact entry or a protected directory prefix in `CURRENT_PROJECT_KEEP_PATHS.txt`. No legacy audit documentation, tests, tools, or workflows remained in the current tree.

## Core-document consistency reviewed
- Target amount is consistently recorded as `1,061,120.54 USDT`, using the dated ₹94.24/USDT snapshot from 22 October 2026.
- Compounding is defined as reinvestment of realized net profit, not a mandatory one-hour trading timeframe.
- Research truth state is consistent across README, project details, status and master log: target-workstream market data has not yet been validated; a cost-aware market-data backtest has not been run; edge is NOT ESTABLISHED; target time is UNKNOWN; live trading is NOT AUTHORIZED; tax/TDS remains deferred.
- Cleanup workflow is manual and read-only. The cleanup script reads the committed allowlist and refuses to apply when required paths are not protected.

## Automated validation state
- Earlier deterministic helper/unit-test workflow passed: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39793473617.
- Expanded smoke/document/allowlist test run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873.
- Last GitHub API check showed this expanded run still `queued`, with no runner assigned and no final conclusion. It is deliberately recorded as PENDING, not PASS. Its checks include Python compilation, required document checks, allowlist dry-run expected to have zero deletion candidates, and the five helper unit tests.

## Boundary and next gate
This documentation refresh makes no claim that the expanded CI run has passed. No market data was downloaded and no trading strategy was backtested during this update. Once CI is confirmed successful, the next research task is a logged real-data acquisition and integrity manifest for a defined BTCUSDT product/interval.
