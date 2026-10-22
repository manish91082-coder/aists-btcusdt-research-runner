# End-to-End Execution Plan: ₹10 Crore-Equivalent AI Trading Research

**Version:** 1.0  
**Plan date:** 22 October 2026  
**Status:** Approved planning baseline; implementation is evidence-gated  
**Primary goal:** Start with **1,000 USDT** and research a path toward **1,061,120.54 USDT**, the approximate ₹10 crore equivalent at the recorded 22-Oct-2026 snapshot of ₹94.24/USDT.  
**Target multiple:** 1,061.12054× equity (not 10,000×).  
**Important:** The conversion amount is a dated reference, not a permanent FX rate. No return, strategy edge, or timeline is established.

## 1. Locked objective and operating constraints

1. Keep the final goal above as the only primary goal until the user explicitly changes it.
2. Build a **fully AI-driven autonomous trading ecosystem**. The AI should dynamically decide trade/no-trade, eligible market/product, permitted direction, strategy and timeframe, entry, exit, initial stop-loss, trailing stop, take-profit/trailing profit, sizing, portfolio allocation and regime adaptation.
3. Initial research scope is Binance Spot and USDⓈ-M Futures, with long/short only where the product supports it and applicable constraints allow it. Explore 5-minute through monthly horizons; a horizon is not a requirement to trade at that frequency.
4. “Hourly compounding” means reinvesting realized net profits into equity for later sizing. It does **not** mean forcing one trade every hour or assuming profits occur hourly.
5. Every result must account for trading fees, spread, slippage/market impact, funding, borrowing where relevant, conversion costs, partial/failed fills, precision, lot/notional limits and other applicable exchange constraints. Report gross and net results separately.
6. Prefer free/zero-cost data and compute resources where practical. Record any unavoidable costs or service limitations; never silently assume unlimited free compute/data.
7. No fabricated data, look-ahead leakage, cherry-picked periods, unlogged parameter changes, or profitability claims without evidence.
8. Hard risk controls must be deterministic and non-bypassable by the AI. No API secrets, live orders, or movement of funds without separate explicit user authorization and a reviewed deployment gate. Tax/TDS is deferred as previously requested, not silently solved.
9. Every substantive response/action updates GitHub status, master log and a distinct execution log, and verifies the result. Keep this plan as the continuity anchor.

## 2. Current evidence baseline

- Repository, research math helpers, cleanup protection and deterministic smoke checks exist.
- The latest target-correction smoke workflow passed at commit `d7fe335acd83d5b5ac5a1cab5dacd16f595b7331`: [GitHub Actions run](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39820508068).
- That CI validates documentation, helper compilation/tests and repository protections. It **does not** validate market data, strategy performance, AI quality, execution realism or profitability.
- Current research gate: **real market-data acquisition/provenance/integrity has not yet been evidenced in the project logs; no cost-aware strategy backtest or validated trading edge has been established.**
- The earlier planned HD-03 checkpoint is September 2026 BTCUSDT Spot and USDⓈ-M Futures 5-minute archive validation. Each full calendar month should contain 8,640 five-minute intervals if the venue data and session coverage are complete. This is an expected-count check, not proof that the archive is present or correct.

## 3. Ordered execution roadmap and exit gates

### Step 0 — Lock governance and reproducibility
**Deliverables:** This plan, target constants, data/experiment naming convention, decision log, protected paths and CI assertions.  
**Pass criteria:** Correct target is consistent; code/data/model/parameter versions and every run are traceable; no live credentials/orders.  
**Current status:** Planning baseline written; repository smoke checks pass.  
**Do not:** Treat CI green as market or profitability evidence.

### Step 1 — HD-03: Acquire and validate the first market-data slice
**Scope:** September 2026, BTCUSDT Spot and BTCUSDT USDⓈ-M Futures, 5-minute candles.  
**Deliverables:** Source URLs/endpoints, retrieval timestamp, original file(s), SHA-256 checksum(s), parser/version, normalized schema, UTC timestamp convention, validation report and run log. Preserve original files and derived data separately.  
**Checks:** Source/provenance; expected interval count; first/last timestamp and coverage; timestamp alignment/order; duplicates; missing intervals; malformed/non-finite/negative values; OHLC consistency; volume fields; Spot/Futures schema differences; product metadata and contract conventions. Distinguish genuine missing data from exchange closures or source-format differences. Do not silently fill gaps.  
**Pass criteria:** Re-downloadable source is documented; checksum reproduces; all anomalies are counted and explained; acceptance/rejection is explicit; independent audit can reproduce the report. A file merely existing is not a pass.  
**Failure path:** Stop downstream experiments, fix ingestion/validation, rerun, log both failure and resolution.

### Step 2 — HD-04: Expand the research data universe
**Deliverables:** Repeatable historical acquisition for required timeframes, a coverage matrix by symbol/product/timeframe, symbol-list snapshot and timestamp, exchange metadata, funding-rate history for Futures, and fee assumptions/sources.  
**Universe rule:** Build the candidate universe from source-verifiable exchange listings and volume snapshots, then derive Spot and Futures Top-10 separately using a predeclared volume measure and cutoff. Avoid survivorship bias: retain delisted/ineligible symbols and historical universe membership where data permits. BTCUSDT remains the first validation instrument, not an excuse to assume every symbol has identical quality.  
**Pass criteria:** Coverage and exclusions are measurable; each market-data partition has provenance, checksum and quality status. No strategy ranking until the relevant input data pass.

### Step 3 — Data contracts and leak-proof dataset builder
**Deliverables:** Versioned schemas, UTC canonical timestamps, deterministic joins/resampling, feature/label lineage, corporate/product metadata where applicable, and train/validation/test split manifest.  
**Checks:** No future data in features; no labels overlapping split boundaries; no duplicate leakage across products; resampling rules are explicit; gaps remain visible; all transformations reproducible.  
**Pass criteria:** Automated tests catch deliberately injected duplicates, gaps, timestamp shifts, look-ahead and schema errors.

### Step 4 — Cost-aware simulator and baseline strategies
**Deliverables:** Event-driven or equivalently justified backtester with position/accounting ledger, realistic order/fill assumptions, fees, spread, slippage, funding/borrow costs, precision/minimum-notional rules, partial fills and rejected orders.  
**Baselines:** Cash/no-trade; buy-and-hold for relevant Spot windows; simple transparent trend/momentum and mean-reversion baselines. Register hypotheses and metrics before examining held-out results.  
**Metrics:** Net return, drawdown, volatility, Sharpe/Sortino with caveats, profit factor, turnover, exposure, win/loss distribution, tail loss, capacity/sensitivity, time in market, fees/funding share and stability across regimes.  
**Pass criteria:** Accounting reconciliation tests pass; known toy cases produce hand-verifiable outcomes; gross/net P&L reconcile; the baseline report is reproducible. No AI model before this gate passes.

### Step 5 — Preregistered strategy experiments S-01 onward
**Process:** Freeze hypothesis, symbols, dates, timeframes, features, costs, metrics and acceptance thresholds before each run. Use chronological train/validation/test and rolling walk-forward evaluation. Keep a final untouched holdout. Correct for multiple comparisons and record all failed experiments.  
**Candidate families:** Transparent trend/momentum, mean reversion, regime filters and risk overlays. These are hypotheses to test, not assumed profitable strategies.  
**Pass criteria:** Performance survives realistic costs, walk-forward windows, parameter perturbation, market regimes and a final untouched holdout; confidence/uncertainty and failure cases are reported. If no candidate passes, do not promote it.

### Step 6 — AI decision layer, introduced incrementally
**Components:** (a) regime/state estimation, (b) probabilistic return/risk forecasts with calibration, (c) transaction-cost and fill-quality estimates, (d) trade/no-trade policy, (e) portfolio allocator. The AI may dynamically select product, permitted direction, strategy/horizon, entry/exit, initial and trailing SL, TP/trailing profit and sizing, but only inside hard risk limits.  
**Required comparisons:** Each component versus simple baselines and ablations; chronological out-of-sample and walk-forward tests; calibration, uncertainty, drift and robustness. Keep model registry, training data, features, code, parameters and random seeds.  
**Pass criteria:** Incremental net-of-cost value versus baseline is repeatable on unseen data and not explained by leakage, excess turnover, one symbol or one regime. A complex model that does not beat a simpler baseline is rejected.

### Step 7 — Independent risk engine and adversarial stress tests
**Controls:** Maximum position/gross/net exposure, leverage caps, per-trade and daily loss limits, drawdown stop, concentration limits, stale/missing data blocks, order-rate/error limits, liquidation-distance checks, volatility/correlation shocks, kill switch and restart/reconciliation rules. Exact numerical limits must be justified, versioned and tested before paper deployment, not invented after seeing results.  
**Stress tests:** Fees/slippage multiplied, delayed/stale data, gaps, extreme candles, funding spikes, partial/rejected orders, exchange outage, clock drift, model failure and rapid regime change.  
**Pass criteria:** Risk limits cannot be bypassed by model output; every failure mode has a tested safe state and auditable event.

### Step 8 — Execution simulator and accounting reconciliation
**Deliverables:** Paper exchange adapter, order-state machine, idempotency, retry rules, precision/filters, partial fills, rejected/cancelled orders, fees/funding ledger and reconciliation against exchange-like events. No private keys required.  
**Pass criteria:** Simulated account state reconciles after restarts and injected failures; no duplicate order intent; all decisions and fills are traceable.

### Step 9 — Paper / forward testing
**Rule:** Run frozen candidate(s) on unseen live market data without real orders. Record predictions before outcomes and include realistic simulated costs. Define minimum duration/sample size and stop conditions before starting.  
**Pass criteria:** No critical safety/reconciliation defects; data freshness maintained; forward results and drawdowns remain within preregistered tolerances; paper outcomes do not materially contradict backtest assumptions. A short winning streak is not sufficient evidence.

### Step 10 — Deployment authorization gate (not authorized now)
Requires a separate explicit user approval, security review, exchange permission review, documented capital-at-risk cap, rollback plan, monitoring/alerting, incident playbook and a tiny limited pilot. Keep withdrawals disabled and never commit credentials. If any requirement is missing, remain in research/paper mode. This plan does not authorize live trading.

### Step 11 — Scale only after measured evidence
Scale in small, reversible increments based on forward-tested capacity, drawdown and execution quality. Reassess model drift, costs and portfolio concentration continuously. Do not increase risk merely because the ₹10 crore target is far away. Reinvestment uses **realized net** P&L after costs; compounding does not justify increasing risk limits automatically.

## 4. Experiment/run record required every time

Each substantive run must log:
- Run ID, UTC start/end, operator/agent and exact purpose.
- Git commit, code version, config/parameters, dependencies and random seeds.
- Data source, time range, symbol/product/timeframe, source checksum and validation report.
- Hypothesis preregistered before run; train/validation/test boundaries.
- Costs/fill assumptions, metrics, benchmark comparison, uncertainty and failure cases.
- PASS/FAIL/BLOCKED decision, evidence links/artifacts, deviations and next single gate.

Never overwrite a failed result. Fixes create a new run linked to the failed run. A changed hypothesis or threshold requires a new preregistration.

## 5. Zero-drift response and repository protocol

For every substantive response/action:
1. State the locked goal and current gate briefly.
2. Use repository evidence before claiming current status; do not infer that an unrun workflow or missing artifact succeeded.
3. Work on the **single next gate** unless its evidence reveals a documented blocker.
4. Update the relevant implementation/docs, Project Status, Hindi Master Research Log and a separate dated execution log.
5. Update the keep-list for new persistent paths and add/adjust deterministic tests where possible.
6. Run CI, inspect its final result and tested commit, then verify changed files on `main`.
7. Report exact changed paths, commit/run links, evidence, remaining blocker and next step.
8. If no code/data artifact was actually produced, say so. Do not label a plan as implementation, a CI pass as trading proof, or a backtest as live performance.
9. Memory continuity: this repository plan and logs are the durable project record. Do not claim an account-level memory write unless a supported memory operation actually confirms it.

## 6. Immediate next action

**Only next gate: HD-03.** Inspect the existing repository and available public Binance archive/download mechanism, implement a small deterministic acquisition/validation tool for September 2026 BTCUSDT Spot and USDⓈ-M Futures 5-minute data, then run it and preserve the real outputs/checksums/report. Do not move to AI strategy research until this gate passes.

## 7. Current gate ledger

| Gate | State | Evidence / exit condition |
|---|---|---|
| G0 — Repository/math harness | PASS for current smoke checks | CI run #39820508068; not trading evidence |
| HD-03 — BTCUSDT Sep-2026 5m data integrity | BLOCKED / not yet evidenced | Actual source files + checksums + reproducible validation report |
| HD-04 — Broader product/symbol coverage | NOT STARTED | Provenance/coverage matrix passes |
| Simulator + cost model | NOT STARTED | Accounting/fill/cost tests pass |
| Baselines + preregistered experiments | NOT STARTED | Reproducible walk-forward/holdout evidence |
| AI decision layer | NOT STARTED | Incremental out-of-sample net benefit |
| Risk/execution simulator | NOT STARTED | Stress tests and reconciliation pass |
| Paper/forward testing | NOT STARTED | Predeclared forward gate passes |
| Live pilot | NOT AUTHORIZED | Separate explicit approval and safety/security gate |

**Truth statement:** The target is a research objective. Profitability, a path to the target, and time-to-target remain unproven and unknown.