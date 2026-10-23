# Crypto Target Research

**Purpose:** Build an evidence-first, fully AI-driven autonomous trading ecosystem researching whether 1,000 USDT can grow toward **1,061,120.54 USDT**, the working USDT equivalent of ₹10 crore at the dated conversion snapshot recorded below, through net-of-cost, risk-controlled compounding. This repository is a research workspace, not a proven trading system.

## Current state

- **Latest full smoke-test run:** [GitHub Actions run 39819921442](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39819921442) passed after the AI architecture and 10M target checks were added. It verified target consistency, architecture-file presence, cleanup allowlist, Python compilation and all five unit tests. [Full run log](execution_logs/2026-10-22-ai-architecture-ci-success.md).

- **Repository cleanup:** completed; current-thread research files retained and verified.
- **Math helpers, docs and cleanup allowlist smoke checks:** passed in [expanded GitHub Actions run](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873). This run compiled both Python helpers, checked the core documents, found zero deletion candidates, and passed five unit tests. See the [detailed execution log](execution_logs/2026-10-22-expanded-smoke-ci-success.md).
- **Final-document verification:** also passed in [the follow-up run](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817044689), which checked 20/20 protected tracked files, zero deletion candidates, stale-status prevention, and five passing unit tests. See [the follow-up execution log](execution_logs/2026-10-22-final-docs-ci-success.md).
- **Real market-data validation for this target project:** not yet completed.
- **Cost-aware strategy backtest:** not yet completed.
- **Profitable strategy / time to target:** not established / unknown.
- **Live trading:** not authorized.

Read [Project Status](CRYPTO_10CR_PROJECT_STATUS.md) for the current checkpoint, [Project Details](CRYPTO_10CR_PROJECT_DETAILS.md) for the scope and rules, [Master Research Log](CRYPTO_10CR_RESEARCH_LOG_HI.md) for the research record, and [AI Autonomous Trading Architecture](AI_AUTONOMOUS_TRADING_ARCHITECTURE.md) for the AI decision, risk and execution design. The latest repository/document consistency audit is [here](execution_logs/2026-10-22-docs-final-verification.md).

## Primary goal definition

The corrected primary target is **1,000 USDT → 1,061,120.54 USDT**, the approximate USDT equivalent of **₹10 crore** at the recorded snapshot of ₹94.24/USDT on 22 October 2026. The 10,000,000 USDT target was entered by mistake and is not the project goal.

“Compounding” means adding realized net trading profit to equity before subsequent position sizing. It does **not** require trading only on a one-hour chart or placing a trade every hour. Strategy timeframe and trading frequency must be determined by evidence.

## Repository layout

- `CRYPTO_10CR_PROJECT_DETAILS.md`: scope, definitions, research process, and acceptance gates.
- `CRYPTO_10CR_PROJECT_STATUS.md`: current verified state and next step.
- `CRYPTO_10CR_RESEARCH_LOG_HI.md`: master research log and decision history.
- `CURRENT_PROJECT_KEEP_PATHS.txt`: human-readable protected-path inventory mirrored by the cleanup script.
- `crypto_target/research_math.py`: deterministic math helpers; not a trading strategy.
- `tests_crypto_target/test_research_math.py`: unit tests for those helpers.
- `scripts/cleanup_current_project.py`: guarded dry-run-by-default repository cleanup utility.
- `execution_logs/`: timestamped execution and verification records.
- `.github/workflows/crypto-target-smoke.yml`: compile and unit-test workflow.
- `.github/workflows/repository-cleanup-preview.yml`: manual, read-only cleanup preview workflow.

## Run the local unit tests

From the repository root with Python 3.12 or compatible Python installed:

```bash
python -m py_compile crypto_target/research_math.py scripts/cleanup_current_project.py
python -m unittest discover -s tests_crypto_target -v
```

The same smoke checks run in GitHub Actions on relevant code/workflow changes. See [the verified run](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873) or [all workflow runs](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions).

## AI autonomy goal

The intended system autonomously evaluates market state and decides trade/no-trade, eligible markets, direction, strategy/timeframe, entries, exits, initial/trailing stop-loss, take-profit/trailing-profit, position sizing, portfolio allocation and risk-aware adaptation. AI decisions must stay inside deterministic risk limits, data-integrity gates, execution controls and kill switches. Live trading is not authorized. The design plan is in [AI_AUTONOMOUS_TRADING_ARCHITECTURE.md](AI_AUTONOMOUS_TRADING_ARCHITECTURE.md).

## Research rules

1. Do not claim edge or forecast time-to-target without reproducible evidence.
2. Use actual, source-traceable market data; record download URL, period, symbol, interval, checksum, schema, duplicates, gaps, and timezone/clock assumptions.
3. Prevent look-ahead and survivorship/selection bias; use chronological validation and walk-forward evaluation.
4. Include fees, spread, slippage, funding, and execution assumptions as relevant.
5. Report net returns together with drawdown, tail losses, exposure, turnover, costs, and risk-of-ruin scenarios.
6. Validate out-of-sample performance and then paper/forward-test before considering any live stage.
7. No exchange credentials, live orders, or movement of funds are permitted by this research setup. Tax/TDS analysis is deferred by scope.

## Next milestone

Follow `END_TO_END_EXECUTION_PLAN_HI.md` without scope drift. The current gate is HD-04 source access. An archive-first probe now checks official Binance Spot/Futures monthly kline ZIPs and the Futures monthly funding-rate archive with checksum verification before attempting the API universe snapshot. The full universe remains blocked until complete, timestamped listing and volume evidence passes. Strategy research remains blocked until required coverage passes. Do not start strategy/AI evaluation until this data gate passes.

**Important:** A math unit-test pass confirms only those helper functions. It does not confirm market-data quality, AI decision quality, profitable edge, or an operational autonomous bot.


## Latest data gate result
- HD-03 passed for September 2026 BTCUSDT Spot and USDⓈ-M Futures 5-minute archives: 8,640 rows per product, zero reported integrity issues, and Binance checksum sidecars matched. [Run/artifact](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39823937420); [execution log](execution_logs/2026-10-22-hd03-data-integrity-pass.md).
- HD-04 implementation exists, but current gate is BLOCKED: GitHub Actions received HTTP 451 from the official public Spot exchange-info endpoint; no complete universe snapshot accepted. See `execution_logs/2026-10-22-hd04-initial-attempt.md`. No strategy edge is established.

## Latest plan verification
- End-to-end plan baseline CI passed: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39822482423 (tested commit `a2450df4c76fb2e88b92a14432f50d81c7bb24a1`). This is repository/plan validation, not trading evidence.
