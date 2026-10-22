# Crypto Target Research — Project Details

**Repository:** [manish91082-coder/aists-btcusdt-research-runner](https://github.com/manish91082-coder/aists-btcusdt-research-runner)  
**Default branch:** `main`  
**Last reviewed:** 22 October 2026  
**Project phase:** Research harness and repository governance; market-data integrity work is next.

## 1. Mission

Conduct reproducible, evidence-first research into whether a strategy or portfolio of strategies can grow an initial 1,000 USDT toward a USDT amount equivalent to ₹10 crore. The research must optimize for a defensible opportunity, not promise a return or a deadline.

## 2. Target and terminology

- Initial equity assumption: **1,000 USDT**.
- Working target: **1,061,120.54 USDT**, the approximate equivalent of ₹100,000,000 at the recorded snapshot of ₹94.24/USDT dated 22 October 2026.
- Required growth multiple: approximately **1,061.12×**. The INR/USDT conversion may change, so the target amount is a reference that must be refreshed deliberately rather than silently.
- Realized-profit compounding: realized net P&L is added to equity and may inform later position sizing. It does not mandate hourly bars or hourly trades.
- Starting equity and target are research assumptions, not evidence that the target can be reached.

## 3. Scope

Included:
- Multiple timeframes and holding periods, including intraday, multi-hour, daily and multi-day methods.
- Simple baselines first, then trend/momentum, breakout, regime-filtered mean reversion, volatility/event methods, and carefully modeled spot/perpetual carry or basis strategies when data supports them.
- Realistic transaction costs and execution constraints.
- Reproducible historical testing, out-of-sample evaluation, sensitivity checks, drawdown and ruin-risk analysis.
- Officially sourced market data with integrity metadata.

Excluded or gated:
- No assumed deposit beyond the starting 1,000 USDT.
- No live order placement, exchange credential handling, or funds movement.
- No strategy will be labeled profitable based only on an in-sample result or a theoretical compounding curve.
- Tax/TDS work is deferred until the user reopens that scope.
- Alternative coins/venues may be added only with explicit universe rules and source/data validation, not by silently expanding the universe.

## 4. Evidence and data requirements

Every dataset must record, at minimum:
- Exchange/source and product type (spot or derivatives).
- Symbol, interval, start/end timestamps and timezone conventions.
- Original URL/object path and retrieval timestamp.
- File size and cryptographic checksum when available.
- Expected schema, row count, duplicate timestamps, ordering, invalid OHLCV relationships, missing intervals and unexplained gaps.
- Known publication delays, corrections, delistings, contract changes and other source limitations.

Do not replace missing records with fabricated prices or fills. Any exclusion, repair or resampling must be documented and tested.

Reference entry points:
- Binance public historical-data repository: https://github.com/binance/binance-public-data
- Binance public data archive: https://data.binance.vision/

These are source entry points only. No data is considered acquired or validated until a logged run records its actual objects, checksums and validation results.

## 5. Strategy research protocol

1. Freeze the hypothesis, signals, universe, execution timing, parameters and evaluation metrics before evaluating the held-out period.
2. Use only information available at the decision time. A signal that uses a candle close must not assume a fill at that same close unless an executable mechanism justifies it.
3. Model fees, bid/ask spread, slippage, funding, borrowing, partial fills, latency, leverage and liquidation constraints where applicable.
4. Split data chronologically. Keep training, validation and final test roles distinct; use walk-forward evaluation and record experiment/selection history.
5. Compare with simple baselines and a no-trade benchmark. Prefer fewer, interpretable parameters until complexity demonstrates robust incremental value.
6. Evaluate across market regimes and parameter/cost perturbations. Report failure cases rather than selectively showing good periods.
7. A historical backtest is not live validation. Paper/forward observation is a separate evidence gate.

Minimum performance report:
- Net and gross return, annualized metrics only when appropriate.
- Equity curve, maximum drawdown and recovery period.
- Trade count, exposure, turnover, holding period and concentration.
- Fees, spread, slippage and funding contribution.
- Tail losses, losing streaks, leverage/liquidation assumptions and risk-of-ruin scenarios.
- Out-of-sample results, comparison baselines, parameter/cost sensitivity and reproducibility identifiers.

## 6. Acceptance gates

| Gate | Required evidence | Current status |
|---|---|---|
| G0: Scope and code harness | Versioned math helpers, explicit rules, deterministic tests | **Implemented; earlier CI run passed** |
| G1: Data provenance and integrity | Actual source objects, hashes, schemas, timestamps, duplicate/gap/validity report | **Not started for this target workstream** |
| G2: Baselines | Reproducible no-look-ahead baseline with realistic costs | **Not started** |
| G3: Out-of-sample edge | Walk-forward, cost-adjusted evidence vs. baselines | **Not established** |
| G4: Risk robustness | Drawdown, tail-risk, sensitivity and ruin-risk checks | **Not started** |
| G5: Forward validation | Paper/forward results with known execution assumptions | **Not started** |
| G6: Live stage | Explicit user approval plus separate safety/compliance review | **Not authorized** |

## 7. Current repository components

- `crypto_target/research_math.py`: target multiple, geometric hurdle, compounding path and maximum drawdown helpers.
- `tests_crypto_target/test_research_math.py`: five deterministic unit tests.
- `.github/workflows/crypto-target-smoke.yml`: Python compilation, helper tests and core-document checks.
- `scripts/cleanup_current_project.py`: guarded cleanup helper; default mode is dry-run.
- `CURRENT_PROJECT_KEEP_PATHS.txt`: protected-path inventory that must be kept aligned with the script.
- `CRYPTO_10CR_RESEARCH_LOG_HI.md`: master record.
- `CRYPTO_10CR_PROJECT_STATUS.md`: concise verified checkpoint.
- `execution_logs/`: append-only historical records.

## 8. Current truth state

- Target arithmetic is a defined planning reference.
- The helper code does not implement a trade signal, execution simulator, or profitable strategy.
- Real market data for this target workstream has not yet been acquired and validated.
- No cost-adjusted market backtest has been completed for this workstream.
- Strategy edge: **NOT ESTABLISHED**.
- Time to target: **UNKNOWN**.
- Live trading: **NOT AUTHORIZED**.
- Tax/TDS: **DEFERRED**.

## 9. Immediate next step

Build a small, auditable data-acquisition and integrity pipeline for an explicitly chosen BTCUSDT product/interval. It must save a manifest with provenance, checksum, schema and integrity outcomes and fail closed on unexplained data defects. Only after its tests pass should the project run simple, cost-aware baseline strategies across multiple horizons.
