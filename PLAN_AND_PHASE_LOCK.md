# Master Execution Plan and Phase Lock

Version: 1.0
Date: 2026-10-21
Status: USER-REQUESTED PROCESS LOCK — ACTIVE
Project: Full AI Crypto Trading Bot 21 OCT

This document turns the user-confirmed goal and existing PROJECT_BLUEPRINT.md into a dependency-ordered plan. It is the execution order of record. It does not mean any phase is complete merely because it is written here.

## A. Mission

Research, design, validate, and only after explicit release approvals implement an AI-assisted Binance Spot + Futures system that:
- Uses Spot for long/flat inventory and an eligible Futures product for long/short exposure; no Spot short is falsely represented.
- Scans an evidence-ranked, point-in-time universe of up to 10 liquid assets.
- Uses 5m, 15m, 1h, 4h, 8h, 1d, 1w and monthly (1M/1mo) horizons.
- Learns from the longest verifiable Binance history available per asset/product; never invents pre-listing history.
- Dynamically proposes strategy/features, direction, entry, size within limits, stop, target, trailing/gain-locking and exit.
- Accounts for actual commissions (BNB only where supported and observed), funding, spread, slippage, impact and other realised costs.
- Prefers zero-cost/open-source resources without pretending compute, storage or 24/7 uptime is unlimited or guaranteed free.
- Starts with 10,000 USDT as a research/paper accounting assumption, not as evidence of account balance or authorisation to move funds.

Success means robust, reproducible, net-of-cost out-of-sample evidence and fail-closed risk/execution controls, not a target win rate or a guarantee of profit. NO TRADE is a valid decision.

## B. Binding operating rules

1. GitHub main and the verified project documents are the project source of truth. Fetch the live head before work.
2. Follow the phases below in order. No phase advances on intention, an attractive chart, or an LLM assertion.
3. Every claim is labelled as user-confirmed, proposed, open, blocked, attempted, completed, or independently verified.
4. No fabricated/synthetic market data, fills, PnL, backtest results, exchange status, source provenance, or free-tier capability.
5. Research and data acceptance precede trading implementation. Tests must be reproducible with source/version/config/window/seeds recorded as applicable.
6. No secret in GitHub; no credentials, deposits, transfers, withdrawals, account-setting changes, real orders, or production deployment without exact-scope authorisation.
7. A deterministic Safety Kernel has final veto authority. AI cannot override hard risk limits, product restrictions, stale-data blocks, exchange filters, kill switch, or ambiguous account/order state.
8. Keep Spot and Futures datasets, semantics, fees, contract/mark/index prices and funding distinct. Never use future information or unfinished bars.
9. Performance claims require point-in-time universe membership, chronological walk-forward evaluation, a genuinely untouched holdout, realistic costs, uncertainty analysis and multiple-testing awareness.
10. BNB is a possible commission asset/discount only where current product/account settings support it and fills prove it. It does not pay away funding, spread, slippage or impact by assumption.
11. Any blocker, failed test, scope change, decision, next step and verified repository write must be logged.
12. Tax/jurisdiction research is explicitly deferred from the immediate strategy/data stage per the user's earlier direction, but remains a mandatory later gate before any live execution. Deferral is not a waiver.

## C. Ordered phases and exit gates

### Phase 0 — Scope, governance and feasibility lock
**Purpose:** freeze the user goal, terminology, exclusions, assumptions, and acceptance criteria.
**Deliverables:** this plan; PROJECT_BLUEPRINT; rules/locks; decision and evidence registers; unresolved-decision list.
**Exit gate:** every requirement is traceable to a document and classified as confirmed/proposed/open; destructive and financial actions remain locked.
**Current status:** baseline documents exist; this master sequence is now recorded. Some architecture details remain proposals.

### Phase 1 — Strategy research and experiment preregistration
**Purpose:** turn candidate ideas into falsifiable, comparable experiments before seeing performance results.
**Order:** (1) no-trade and simple benchmark baselines; (2) S-01 trend and S-02 regime-filtered mean reversion; (3) S-03 volatility breakout and S-04 momentum continuation; (4) formally defined candle/price-structure features; (5) regime selector; (6) Futures funding/basis only after source coverage passes; (7) liquidity/execution filters only with observed data; (8) cross-asset context and portfolio allocation; (9) supervised return-distribution models; (10) exit-policy tournament; RL/hypothesis-generating AI only after credible baselines.
**Deliverables per experiment:** hypothesis, rationale, exact formulas/units, parameters and bounded search grid, inputs and required history, baseline, cost assumptions, causal signal/fill timing, train/validation/test windows, metrics, failure criteria, leakage checks and reproducible experiment ID.
**Exit gate:** S-01 to S-04 protocols frozen before backtests; no tuning against the final holdout; no strategy is called profitable before audited results.
**Current status:** 12 hypotheses are registered; exact experiment protocols and tests are not yet frozen.

### Phase 2 — Representative Binance data audit
**Purpose:** prove the end-to-end ingestion and validation path on real official files before bulk collection.
**First target:** BTCUSDT Spot 5m and a matching USDⓈ-M Futures artifact, kept as separate datasets. Confirm exact archive paths and periods before download.
**Checks:** official checksum when supplied; local SHA-256; byte size; schema/column types; timestamp units/timezone; first/last event; expected interval cadence; duplicates; gaps; out-of-order rows; malformed records; OHLC invariants; volume validity; partial final candle; and a bounded comparison with official API responses.
**Deliverables:** source-linked manifest row, validator code/specification as permitted by the research gate, machine-readable audit output, exceptions and pass/fail decision.
**Exit gate:** the selected artifact passes documented checks or the failure is preserved as a blocker. No bulk-data or data-quality claim before this.
**Current status:** manifest specification exists; no archive download/checksum/audit is yet verified.

### Phase 3 — Historical coverage and dataset inventory
**Purpose:** establish exactly what history is available, per symbol/product/interval, before choosing the universe or claiming a 10-year sample.
**Work:** inventory Spot and eligible Futures listings, archive availability, contract start/end dates, interval coverage, missing intervals, timestamp conventions and provenance. Request only data needed for preregistered experiments. Keep raw archives outside Git unless justified; store manifests and hashes in Git.
**Exit gate:** a reproducible coverage matrix exists and each experiment's input coverage is sufficient. Missing history stays missing; other-venue data is not silently spliced into Binance history.
**Constraint:** Binance launched in 2017, so a full ten-year Binance-only history does not exist as of this plan date; each asset/contract may have less.

### Phase 4 — Evidence-based top-10 universe
**Purpose:** select up to 10 eligible assets without hindsight or survivorship bias.
**Work:** verify product eligibility and trading status; use multiple rolling quote-volume windows, spread/depth/impact where observable, listing age, data quality and sufficient history; document exclusions; apply ranking buffer/hysteresis; reconstruct point-in-time membership for backtests.
**Deliverables:** dated ranked candidate table, data lineage, inclusion/exclusion reasons, sensitivity analysis and freeze/review policy.
**Exit gate:** universe policy passes audit; historical tests use only assets eligible at each historical time. Coin names are not guessed or permanently hardcoded without evidence.

### Phase 5 — Feature, indicator and market-structure registry
**Purpose:** build an auditable feature vocabulary instead of blindly accumulating indicators.
**Work:** formally define returns, momentum/trend, moving averages, volatility/range, volume/flow, candle geometry, price structures, breakouts, regime, anomaly, correlations and supported derivatives/microstructure features.
**Each feature records:** ID/version, formula, units, parameters, lookback/warm-up, missing-value behavior, source fields, timestamp availability, causal/leakage tests, computation cost, ablation result and known failure modes.
**Exit gate:** every feature used in a test is registered, reproducible, point-in-time available and passes leakage/unit tests. No invented historical order-book or open-interest values.

### Phase 6 — Fees, accounting, risk and portfolio mathematics
**Purpose:** independently validate the net-return ledger and bounded position/risk proposals before coding the trading engine.
**Work:** per-fill maker/taker commissions; actual BNB fee deductions; native-asset and USDT-equivalent accounting; funding cash flows; spread/slippage/impact; partial fills/rejections; contract multiplier/tick/step/min-notional filters; leverage/margin/liquidation sensitivity; combined Spot/Futures exposures; correlation; multiple-entry cumulative risk; daily loss/drawdown caps; and stressed gaps.
**Exit gate:** formulas have dimensional analysis, edge-case tests and independent numerical checks; proposed numerical caps are reviewed and documented. No martingale or unbounded averaging/pyramiding.
**Important:** 10,000 USDT is only the initial research/paper equity until separately authorised.

### Phase 7 — Backtest and statistical evaluation framework
**Purpose:** ensure results are causal, comparable and resistant to overfitting.
**Work:** event-time replay; decision time versus earliest feasible fill; fees/funding and conservative execution model; intrabar stop/target ambiguity handling using sufficiently granular evidence; chronological train/validation/walk-forward windows; untouched holdout; benchmark and ablation suite; confidence intervals/uncertainty; sensitivity and multiple-testing correction; regime and drawdown analysis.
**Exit gate:** test framework itself passes synthetic unit tests (clearly labelled test fixtures, never market evidence), data invariants, leakage tests and reproducibility checks; first empirical report is independently audited. No same-bar impossible fills.
**Promotion rule:** in-sample performance alone never qualifies a strategy.

### Phase 8 — AI/model-family selection and controlled learning
**Purpose:** choose the simplest model family that adds measurable out-of-sample value within compute limits.
**Work:** compare deterministic baselines, supervised return/distribution models, regime-conditioned selection, calibrated ensembles and only later experimental RL/hypothesis generation. Evaluate calibration, uncertainty, stability, ablations, drift and inference latency.
**Exit gate:** champion/challenger protocol, immutable model/data/config versions, explicit promotion approval and rollback are working. No silent live weight updates; model may abstain/NO TRADE.
**Architecture note:** the ten AI roles in PROJECT_BLUEPRINT are proposed bounded responsibilities, not ten separate LLM calls per tick. The deterministic Safety Kernel is mandatory and independent.

### Phase 9 — Execution design, security and operations
**Purpose:** design reliable order/position handling only after earlier research gates.
**Work:** exchange metadata refresh; signed-request security and least privilege; unique client order IDs; idempotency; rate limits; clock drift; timeout/unknown-result reconciliation; partial fills; cancel/replace; protection-order coverage; reconnect/restart recovery; stale-data blocks; kill switch; audit ledger; alerts; incident response; and secrets management.
**Exit gate:** failure-injection tests prove no duplicate exposure, no unprotected state accepted silently, and safe recovery after restart. Withdrawals remain disabled. No LLM may directly invent and submit raw order payloads.

### Phase 10 — Zero-cost compute, storage and runtime feasibility
**Purpose:** test whether the intended cadence and safety controls can run within the user's zero-cost-first constraint.
**Work:** measure archive size, RAM, CPU, training/inference time, bandwidth, persistence, scheduled-job limits and restart/reliability. Verify current free-tier terms from primary sources. Separate research batch compute from any live runtime.
**Exit gate:** a measured resource budget and failure-mode report exist. If reliable operation cannot be achieved at zero cost, disclose the limitation; do not silently incur charges or promise 24/7 uptime.

### Phase 11 — Shadow and paper acceptance
**Purpose:** observe the full pipeline on real market inputs without sending real orders.
**Work:** log timestamped model proposals, vetoes, virtual orders/fills (clearly labelled), actual market conditions, estimated costs, missed/partial-fill scenarios, drift, outages, latency, risk events and reconciliation.
**Exit gate:** a preregistered observation duration and acceptance metrics pass, with no critical safety incident and independently reviewed logs. Paper performance is not real execution and does not guarantee future returns.

### Phase 12 — Final release review and optional limited live stage
**Purpose:** consider live trading only after every mandatory gate and a separate explicit user approval.
**Mandatory checks:** current account/product/jurisdiction eligibility and applicable requirements; account-specific fee/BNB settings; least-privilege API key; withdrawals disabled; reviewed capital and BNB-reserve semantics; risk limits; independent code/security audit; monitoring and kill switch; rollback/incident runbook; final go/no-go report.
**Exit gate:** all required evidence is PASS, blockers are resolved, and the user explicitly authorises the exact live scope. This plan itself grants no live permission. If any gate fails, remain in research/shadow mode.

## D. Immediate work queue (binding order)

1. Re-fetch current GitHub main and the strategy/data documents.
2. Execute the representative official archive audit, starting with BTCUSDT Spot 5m and matching Futures data; verify actual files and hashes. If download/verification cannot be done, record the precise blocker and use a verifiable zero-cost route, not a fabricated PASS.
3. Freeze S-01 through S-04 experiment specifications and benchmarks before any backtest.
4. Build exact historical coverage inventory and timestamp-aware validators.
5. Rank the top-10 universe from observed evidence.
6. Continue phases in order; do not skip gates for convenience.

## E. Change-control protocol

This plan is locked as the default sequence. Any change must:
1. State the exact phase/step affected and why.
2. Preserve the prior rule and evidence trail.
3. Record the change in DECISION_LOG.md as USER-CONFIRMED, RECOMMENDED-PENDING-APPROVAL, or RESEARCH-OPEN.
4. Update this plan and the relevant status, continuity, memory, rules, research and session-log files.
5. Be committed and read back from GitHub before being reported as saved.
A user may explicitly reprioritise a phase. A reprioritisation does not silently waive safety, eligibility, data integrity or live-approval gates.

## F. Definition of current state

- This plan is now the ordered project roadmap; it is not evidence that phases have passed.
- Strategy dossier: 12 candidates registered, not empirically tested.
- Data manifest specification: written; no representative archive audit is yet verified.
- Top-10 universe: not selected.
- Trading code/model/backtest/paper run/live order: not performed in this checkpoint.
- Live trading, credentials, withdrawals, deployment and real capital remain locked.
