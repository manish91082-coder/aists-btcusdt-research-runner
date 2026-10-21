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
**Current status:** 12 hypotheses are registered. S-01 through S-04 protocols are frozen in `S01_S04_PREREGISTRATION.md` under the documented Phase 2 blocker contingency; none has been backtested. Remaining hypothesis protocols and tests are not yet frozen.

### Phase 2 — Representative Binance data audit
**Purpose:** prove the end-to-end ingestion and validation path on real official files before bulk collection.
**First target:** BTCUSDT Spot 5m and a matching USDⓈ-M Futures artifact, kept as separate datasets. Confirm exact archive paths and periods before download.
**Checks:** official monthly archive URL; adjacent official checksum versus local SHA-256; ZIP integrity; 12-column schema; timestamp unit/timezone; requested-month membership; interval cadence; duplicates; gaps; ordering; OHLC invariants; nonnegative volume/counts; full-month row count where the symbol is known to have full-month history; and continuity across adjacent chunks.
**Deliverables:** source-linked chunk manifest, validator, machine-readable reports, checksums, exceptions and a pass/fail decision. REST API comparisons are optional diagnostics, not a prerequisite for accepting historical archives.
**Exit gate:** the representative Spot and USDⓈ-M Futures monthly archive pilot passes all required checks, followed by an older-month check for timestamp/path conventions. No bulk-data claim or backtest before this gate.
**Current status (verified 2026-10-21):** HD-03 was run and accepted for the bounded September 2026 BTCUSDT 5m monthly archive pilot: GitHub Actions run `39594637570`, artifact `12343236522`. Both Spot and USDⓈ-M Futures reports were independently inspected; each passed official publisher checksum/local SHA-256, ZIP/schema/timestamp/OHLC/volume checks and full-month coverage at 8,640 rows, with zero malformed/duplicate/gap/missing rows. Artifact SHA-256 matched GitHub's digest. This is archive-integrity/candle-quality evidence, not independent economic truth or an API comparison. **Phase 2 as a whole remains open. Next: HD-04 older-month conventions check for both products**, proposed `2024-01`, `BTCUSDT`, `5m`, using official archives and a separate report for each market. Then coverage manifest and volume-semantics work. No bulk-history completeness, strategy performance, backtest or trading readiness is claimed. See `HISTORICAL_DATA_INGESTION_SUBTASKS.md`.

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

 
## G. Full AI system requirements traceability (expanded 2026-10-21)

This section makes the user's detailed scope explicit. It supplements, rather than silently replaces, the existing blueprint.

### G1. Autonomous decision contract
AI owns dynamic interpretation and selection among validated choices: eligible asset/universe proposal; timeframe context; feature/indicator subset; strategy/model selection; long/short/flat/no-trade proposal; entry timing and allowed order style; risk-bounded size proposal; initial stop, target, time stop, trailing/gain-lock exit and position adjustment proposal. Every proposal must include as-of timestamps, data/model/config versions, uncertainty, expected net return after costs, risk impact, rationale trace and required supporting evidence.

AI may not invent unregistered features or formulas directly into production. A newly discovered strategy/formula is a research hypothesis, not an executable rule, until versioned, independently checked, tested on chronological unseen data and explicitly promoted. The system must permit NO TRADE when evidence, data quality, net expectancy or uncertainty fails its hurdle.

### G2. Logical AI brain plan
The ten logical roles below are architecture candidates, not a commitment to ten expensive LLMs or ten processes. Choose actual model families only after comparative research and measured resource needs.

1. Universe & Liquidity Brain: ranks eligible candidates from point-in-time evidence; records inclusion/exclusion reasons.
2. Data Quality & Anomaly Brain: interprets deterministic validator outputs; cannot waive hard data failures.
3. Market Regime Brain: estimates trend/range/volatility/liquidity/funding regime with uncertainty.
4. Multi-Timeframe Context Brain: reconciles completed 5m/15m/1h/4h/8h/1d/1w/monthly bars and conflicts.
5. Feature/Indicator Selector Brain: chooses only registered features and tested feature bundles.
6. Strategy Discovery/Tournament Brain: compares only eligible, preregistered, validated candidates with walk-forward evidence.
7. Signal/Probability Brain: estimates directional and return/risk distributions; proposes long/short/flat/no-trade with calibration.
8. Portfolio/Sizing Brain: proposes allocation using total equity, existing positions, correlated risk, available margin and hard limits.
9. Execution/Cost Brain: proposes among permitted order types/timing using measured spread, impact, fees and rate limits; never bypasses exchange filters.
10. Position Supervision/Learning Brain: proposes exits, monotonic trailing updates, alerts, drift reviews and retraining requests.

The deterministic Safety Kernel is an independent mandatory control, not one of the predictive brains. It validates schemas and freshness, product/account eligibility, filters, exposure/loss caps, position/order reconciliation, protection coverage, kill switch and live-authorisation state. It can veto any AI output and cannot be overridden. An independent audit/test function challenges evidence and mathematics. Prefer deterministic/numerical inference for frequent market decisions; use LLMs for bounded research, explanation and hypothesis generation only where measured value justifies cost/latency.

### G3. Timeframe and continuous scanner contract
Required horizons are 5m, 15m, 1h, 4h, 8h, 1d, 1w and monthly (API/archive token may be 1mo). Each feature records its source horizon and last available timestamp. Use only completed bars for close-based signals; join slower horizons as-of, not from future closes. A signal cannot fill at a price that was only knowable after the decision. Fast safety/position monitoring is event-driven and independent from slow model inference. Scanner cadence, stale-data thresholds and resource budgets must be measured and pre-registered; "continuous" is not claimed until the runtime demonstrates it.

### G4. Dynamic position and exit contract
Every new entry and add-on recomputes aggregate worst-case risk across existing positions, pending orders, Spot inventory and Futures exposures. No martingale, unbounded averaging down, or unbounded pyramiding. Stops are not guaranteed execution prices; gaps, slippage, trigger source and liquidation sensitivity must be modelled. Long trailing stops may stay or rise, never loosen downward; short trailing stops may stay or fall, never loosen upward. Any change logs source price, timestamp, reason, model version, prior/new protection, cost and risk impact. No model may override hard caps.

### G5. Data and learning claims
The "past ten years" request is interpreted as the longest verifiable history per asset/product, not an invented uniform decade. Binance launched in 2017, and individual listings/contracts may have shorter histories. Current top-ten winners must not be back-projected into history. Other-venue data, if later approved, is labelled and evaluated separately. All indicators, candle patterns and line/OHLC chart structures need explicit numerical definitions; no vague visual labels or claim that every known pattern is profitable. AI-generated mathematics must pass dimensional checks, independent tests, ablations, leakage review and unseen-data evaluation.

### G6. Fees and initial equity
10,000 USDT is the initial research/paper accounting value until a separate live release. Record gross PnL, each entry/exit commission, actual fee asset and BNB amount/value when deducted, spread, slippage, impact, funding paid/received, rejected/missed/partial orders and other realised costs. Verify BNB deduction from account/fill evidence and current product support. Never assume funding, spread, slippage, impact or liquidation costs can be paid in BNB.

### G7. Zero-cost feasibility contract
Prefer public official data, open-source tools and free compute. Measure data volume, disk, RAM, CPU/GPU, runtime, bandwidth, model inference latency, persistence, scheduler limits and outage recovery. Do not commit huge raw archives to Git by default; preserve source paths, retrieval timestamps, checksums, manifest and audit reports. If reliable always-on operation cannot be proven at zero cost, report that limitation rather than quietly buying services or claiming full automation.

### G8. Per-response and per-change anti-drift audit
Before each substantive response/action:
1. Re-read the user's final goal and current request.
2. Fetch live GitHub main and compare with the last verified head.
3. Identify the active phase, its entry criteria, current evidence and blockers.
4. Check scope, dependency order, data/math quality, security and no-code/live locks.
5. Work only on the next gate unless the user explicitly reprioritises.
6. Log actual work, failures, changes and the exact next action.
7. Read back every changed file and verify the new main head before saying it was saved.
8. End the user-facing report with current mission status and what remains unverified.

A response cannot literally prove zero error in advance; it must demonstrate checks performed and state their limits. Never claim persistent model memory was changed by a chat response. Durable project continuity is maintained in these GitHub files.

### G9. Requirement-to-phase map
- Binance Spot + Futures, long/short, BNB fees, 10,000 USDT, timeframes, dynamic management: Phases 0, 6, 9, 11, 12.
- Historical learning and exact archive availability: Phases 2–3.
- Evidence-ranked top ten: Phase 4.
- All indicators/patterns/strategies as formal candidates: Phases 1 and 5.
- AI selection/training/multiple verification: Phases 1, 7 and 8.
- Dynamic entry/exit/stops/targets/trailing/multiple entries: Phases 6–9.
- Zero-cost full automation: Phases 9–11, with measured limitations.
- No fabrication, no drift, audit trail, GitHub log and continuity: all phases and the change-control protocol.

### G10. Efficiency, bounded verification and anti-loop protocol (active 2026-10-21)
Follow EFFICIENCY_NO_DRIFT_PROTOCOL.md. Every response must check mission, live main SHA, active phase/gate, latest decisive evidence, blockers and next permitted action. Avoid unnecessary repeat reads by reusing the last verified full-plan checkpoint unless the plan/head/phase/scope/gate/continuity changed. Resolve one decision per tool pass. Do not rerun completed audits without a material code/config/input/protocol change, a correctable committed defect, an incomplete required run, or a documented decision-relevant environment change. For HTTP 451/access restrictions, test only official documented permitted options; never bypass restrictions. If the same blocker persists without a material change, stop endpoint cycling and log the blocker and exact next decision. Update durable records only when there is new evidence, a material change, a changed blocker, or a changed next action. This protocol does not waive any phase exit gate.


### G11. New-thread handoff integrity (2026-10-21)
A copy-ready handoff is maintained in `NEW_CHAT_CONTINUITY_PROMPT.md`. A new thread must verify the live main SHA and relevant files/reports before relying on the handoff SHA. Current code CI success is not market-data evidence. HD-03 September 2026 monthly archive pilot is accepted for the bounded sample after run `39594637570` and artifact `12343236522` were reviewed. The next gate is HD-04 older-month path/schema/timestamp validation for both products, proposed `2024-01` BTCUSDT `5m`. Full Phase 2 coverage/cost gate remains open; no backtest or trading is authorised. This section does not relax any exit gate or authorise backtesting/trading.
