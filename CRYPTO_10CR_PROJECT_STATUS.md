# Crypto Target Research — Current Project Status

**Last updated:** 22 October 2026  
**Repository:** [aists-btcusdt-research-runner](https://github.com/manish91082-coder/aists-btcusdt-research-runner)  
**Branch:** `main`  
**Current phase:** Research harness established; real market-data integrity pipeline is next.

## Executive status

| Workstream | Status | Verified meaning |
|---|---|---|
| Current-thread repository cleanup | **Complete** | Old tracked project files removed from current `main`; the intended current research files remain. Git history and other branches were not erased. |
| README, project details and status | **Updated** | Core project documents have a common scope and research status. |
| Compounding/target math helpers | **Implemented** | Deterministic arithmetic helpers exist; they are not a trade signal or strategy. |
| Helpers, docs and allowlist checks | **Passed** | [Expanded GitHub Actions run](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873): Python compile passed, required-doc checks passed, 17/17 tracked paths protected, 0 deletion candidates, and 5 unit tests passed. |
| Real market data for this target project | **Not yet acquired/validated** | No validated dataset or data-integrity manifest is claimed. |
| Cost-aware strategy backtest | **Not run** | No market-data performance result exists for this workstream. |
| Profitable strategy / time to target | **Not established / unknown** | No forecast or profit guarantee is justified. |
| Live exchange access, orders, funds movement | **Not authorized** | Research only. |
| Tax/TDS analysis | **Deferred** | Outside current scope until explicitly reopened. |

## Goal

Research whether an evidence-supported approach can grow an assumed initial equity of **1,000 USDT** toward **1,061,120.54 USDT**, the approximate equivalent of ₹10 crore using the recorded snapshot of ₹94.24/USDT dated 22 October 2026. This is a dated conversion assumption, not a permanent exchange rate.

“Compounding” means reinvesting **realized net profit** into equity for later position sizing. It does not require a one-hour chart or one trade every hour. The allowed strategy timeframe is open, subject to valid testing.

## Work completed in this thread

- Created the crypto-target math helper package and deterministic unit tests.
- Added a GitHub Actions smoke-test workflow.
- Added guarded repository-cleanup tooling, then completed and verified the current-thread-only cleanup.
- Recreated a current README, added the detailed project charter, and aligned the master research log, status, keep-list and cleanup utility.
- Preserved the current research source, tests, workflow and execution records. The cleanup did not erase Git history or other branches.

Execution records:
- [Cleanup outcome and verification](execution_logs/2026-10-22-cleanup-final-verification.md)
- [Current-thread-only cleanup](execution_logs/2026-10-22-current-thread-only-cleanup.md)
- [Research harness bootstrap](execution_logs/2026-10-22-research-harness-bootstrap.md)

## Evidence gates

1. **Data integrity:** source, product type, symbol, interval, timestamps, checksum, schema, duplicates, OHLCV validity and missing intervals are audited.
2. **Baseline correctness:** explicit signal time, executable fill assumption, no look-ahead, and realistic costs.
3. **Out-of-sample edge:** chronological validation/walk-forward tests versus simple baselines after costs.
4. **Risk robustness:** drawdown, tail losses, leverage/liquidation where relevant, sensitivity and ruin-risk analysis.
5. **Forward validation:** paper/forward observations before any discussion of a live stage.
6. **Explicit authorization:** live actions remain disabled unless separately requested and reviewed.

## Next step

Implement a small, auditable market-data acquisition and integrity manifest for a clearly specified BTCUSDT product and interval. First validate files and timestamps; only then build cost-aware baselines across multiple holding periods. Save each substantive run to a separate execution-log file and update the research record with exact evidence, not assumptions.

**Decision today:** Strategy edge is **NOT ESTABLISHED**. Time to target is **UNKNOWN**. No market-data backtest is claimed.


## Latest continuity checkpoint — 22 October 2026
- Current core documents, keep-list, cleanup script, workflows and research helpers are linked from `README.md`.
- Final tree audit: `execution_logs/2026-10-22-docs-final-verification.md`. The latest post-refresh `main` inventory contains 20 tracked files; all 20 are covered by the current committed keep-list and unexpected paths are 0. The CI run tested its pinned commit (`c1f7464f91816ebbffd614ba857b66aa5b69db24`), where 17 tracked files were all protected and there were 0 deletion candidates; later commits added only project execution logs and documentation-only status updates.
- Expanded documentation/allowlist smoke run passed in GitHub Actions: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873. Detailed step results: `execution_logs/2026-10-22-expanded-smoke-ci-success.md`.
- Research gate remains unchanged: market data not yet verified, no cost-aware backtest, edge NOT ESTABLISHED, target time UNKNOWN, live trading NOT AUTHORIZED, tax/TDS deferred.
