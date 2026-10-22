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
| Helpers, docs and allowlist checks | **Passed** | [Latest GitHub Actions run](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817387843): Python compile passed, required-doc checks passed, 21/21 tracked paths protected, 0 deletion candidates, and 5 unit tests passed. |
| Real market data for this target project | **Not yet acquired/validated** | No validated dataset or data-integrity manifest is claimed. |
| Cost-aware strategy backtest | **Not run** | No market-data performance result exists for this workstream. |
| Profitable strategy / time to target | **Not established / unknown** | No forecast or profit guarantee is justified. |
| Live exchange access, orders, funds movement | **Not authorized** | Research only. |
| Tax/TDS analysis | **Deferred** | Outside current scope until explicitly reopened. |

## Primary goal

Build a fully AI-driven autonomous trading ecosystem to research whether initial equity of **1,000 USDT** can grow toward **1,061,120.54 USDT**, the approximate USDT equivalent of **₹10 crore** at the 22 October 2026 ₹94.24/USDT snapshot. This is a dated conversion reference, not a guaranteed outcome or timeline. The 10,000,000 USDT target was entered by mistake and is not the project goal.

“Compounding” means reinvesting **realized net profit** into equity for later position sizing. It does not require a one-hour chart or one trade every hour. The allowed strategy timeframe is open, subject to valid testing.

## AI ecosystem requirement

The intended system must dynamically decide trade/no-trade, market/direction, strategy/timeframe, entry/exit, initial and trailing stop-loss, take-profit/trailing-profit, sizing, portfolio risk and regime adaptation, using current validated market conditions and net-of-cost evaluation. AI decisions must stay inside deterministic risk limits, data-quality gates, execution constraints and kill switches. The design is documented in [AI_AUTONOMOUS_TRADING_ARCHITECTURE.md](AI_AUTONOMOUS_TRADING_ARCHITECTURE.md). This architecture is documented but not yet implemented end-to-end; live trading remains unauthorized.

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

## Latest plan/CI verification
- End-to-end plan: `END_TO_END_EXECUTION_PLAN_HI.md`.
- CI: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39822482423 — `success`, tested commit `a2450df4c76fb2e88b92a14432f50d81c7bb24a1`.
- Python compilation, required plan/target checks, keep-list dry-run and 5/5 unit tests passed. This verifies repository checks only, not market data or trading edge.
- Detailed record: `execution_logs/2026-10-22-end-to-end-plan-baseline.md`.

## Next step

**Current gate: HD-03 (BLOCKED / not yet evidenced).** Implement and run a reproducible acquisition/integrity check for September 2026 BTCUSDT Spot and USDⓈ-M Futures 5-minute archives. Require source provenance, original files, SHA-256 checksums, UTC coverage, expected intervals, duplicate/gap/OHLC/schema checks and a reproducible report. No strategy/AI backtest until HD-03 passes. See `END_TO_END_EXECUTION_PLAN_HI.md`.

**Decision today:** Strategy edge is **NOT ESTABLISHED**. Time to target is **UNKNOWN**. No market-data backtest is claimed.


## Latest continuity checkpoint — 22 October 2026
- Current core documents, AI architecture, keep-list, cleanup script, workflows and research helpers are linked from `README.md`.
- End-to-end evidence-gated roadmap: `END_TO_END_EXECUTION_PLAN_HI.md`; its current single next gate is HD-03.
- Final tree audit: `execution_logs/2026-10-22-docs-final-verification.md`. The latest post-refresh `main` inventory now contains 22 tracked files; all 22 are covered by the current committed keep-list and unexpected paths are 0. The latest CI run tested its pinned commit (`67c08f8d9c370e8d1f3171f5f7175ce6db41c016`), where 21 tracked files were all protected and there were 0 deletion candidates. The newest current-tree check log is `execution_logs/2026-10-22-final-current-thread-ci-success.md`.
- Expanded documentation/allowlist smoke run passed in GitHub Actions: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873. Detailed step results: `execution_logs/2026-10-22-expanded-smoke-ci-success.md`.
- Follow-up final-document validation passed: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817044689 (20 protected files, zero deletion candidates, 5/5 unit tests); details: `execution_logs/2026-10-22-final-docs-ci-success.md`.
- Latest smoke run passed: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817387843 (21 protected files, zero deletion candidates, 5/5 unit tests); details: `execution_logs/2026-10-22-final-current-thread-ci-success.md`.
- AI architecture and corrected ₹10 crore target consistency checks passed in [GitHub Actions run 39819921442](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39819921442); details: `execution_logs/2026-10-22-ai-architecture-ci-success.md`.
- Research gate remains unchanged: market data not yet verified, no cost-aware backtest, AI trading loop not yet implemented end-to-end, edge NOT ESTABLISHED, target time UNKNOWN, live trading NOT AUTHORIZED, tax/TDS deferred.
