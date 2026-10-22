# Crypto Target Research

**Purpose:** Evidence-first research into whether a reproducible, cost-aware trading approach can grow 1,000 USDT toward the USDT amount equivalent to ₹10 crore. This repository is a research workspace, not a proven trading system.

## Current state

- **Repository cleanup:** completed; current-thread research files retained and verified.
- **Math helpers and unit tests:** implemented. The earlier GitHub Actions smoke run passed: [run details](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39793473617).
- **Real market-data validation for this target project:** not yet completed.
- **Cost-aware strategy backtest:** not yet completed.
- **Profitable strategy / time to target:** not established / unknown.
- **Live trading:** not authorized.

Read [Project Status](CRYPTO_10CR_PROJECT_STATUS.md) for the current checkpoint, [Project Details](CRYPTO_10CR_PROJECT_DETAILS.md) for the scope and rules, and [Master Research Log](CRYPTO_10CR_RESEARCH_LOG_HI.md) for the research record.

## Goal definition

The working reference is 1,000 USDT initial equity and **1,061,120.54 USDT** as the approximate ₹10 crore equivalent using the recorded 22 October 2026 snapshot of ₹94.24 per USDT. The conversion is a dated reference, not a permanent exchange rate.

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

The same smoke checks run in GitHub Actions on relevant code/workflow changes. See [all workflow runs](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions).

## Research rules

1. Do not claim edge or forecast time-to-target without reproducible evidence.
2. Use actual, source-traceable market data; record download URL, period, symbol, interval, checksum, schema, duplicates, gaps, and timezone/clock assumptions.
3. Prevent look-ahead and survivorship/selection bias; use chronological validation and walk-forward evaluation.
4. Include fees, spread, slippage, funding, and execution assumptions as relevant.
5. Report net returns together with drawdown, tail losses, exposure, turnover, costs, and risk-of-ruin scenarios.
6. Validate out-of-sample performance and then paper/forward-test before considering any live stage.
7. No exchange credentials, live orders, or movement of funds are permitted by this research setup. Tax/TDS analysis is deferred by scope.

## Next milestone

Implement and test the real market-data acquisition/integrity manifest for the initial BTCUSDT research universe, then establish simple cost-aware baselines across multiple holding horizons. Keep every run reproducible and create a separate execution log for each substantive run.

**Important:** A math unit-test pass confirms only those helper functions. It does not confirm market-data quality or profitability.
