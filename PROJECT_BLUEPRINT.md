# Full AI Crypto Trading Bot 21 OCT: Master Project Blueprint

Version: 0.1 | Updated: 2026-10-21 | Mode: RESEARCH FIRST, NO TRADING CODE OR LIVE EXECUTION AUTHORIZED

## 1. Mission and definition of success

Design, research, validate and later implement an AI-assisted Binance crypto trading system that scans an evidence-selected universe of up to 10 liquid coins; evaluates 5m, 15m, 1h, 4h, 8h, 1d, 1w and 1M horizons; and chooses whether to trade, which validated model/strategy/features to use, direction, order style, risk-bounded size, stop-loss, take-profit, trailing protection and exit. Spot and Futures risk must be aggregated at portfolio level. Trading commissions should be paid in BNB wherever the current Binance product/account rules actually support it.

Success does not mean a high win rate, a good-looking chart, an attractive selected backtest or a directional prediction. It means reproducible data provenance, correct net-of-cost accounting, leakage-resistant out-of-sample evidence, working risk and execution controls, monitored shadow/paper evidence, and explicit authorisation before any real orders. The valid AI decision can be NO TRADE. No result guarantees future returns.

## 2. User requirements captured

1. Binance as target venue.
2. Spot and Futures both in scope, with long and short exposure.
3. Stated initial capital: 10,000 USDT.
4. BNB for fees wherever eligible and enabled.
5. AI dynamically selects market universe, strategy, indicators/algorithms, entries, exits, size within limits, initial stops, targets and trailing/gain-locking logic.
6. Scan a high-volume top-10 universe. Exact coins must come from evidence, not memory or guesswork.
7. Horizons: 5m, 15m, 1h, 4h, 8h, 1d, 1w and 1M/monthly.
8. Learn from the longest verifiable history available, aiming at ten years only where the venue/source actually has that much data.
9. Research each component before coding and audit evidence/data/math independently.
10. Prefer free and open-source resources without claiming free always-on hosting or unlimited training compute.
11. GitHub must hold project blueprint, decisions, evidence index, rules/locks, memory, status, continuity and project log.
12. No fake data, invented fills/PnL, unsupported claims, rubber stamping, silent drift or claims that paper fills are real fills.

## 3. Feasibility limits that must remain visible

### 3.1 Ten-year Binance history

Binance's official launch announcement gives 14 July 2017 as the exchange launch date. As of 2026-10-21, ten full calendar years of Binance-only history are not available as a venue-wide dataset. Individual Spot pairs and Futures contracts may have started later, shortening history further.

Therefore, primary evaluation uses the longest verified Binance history per asset/market. A dataset inventory must record exact start/end timestamps per symbol, market, interval and archive. Never fabricate earlier bars or silently splice another venue's prices into Binance data. Data from another exchange, if later approved, must stay separately labelled and separately evaluated with venue/basis differences disclosed.

Evidence: https://www.binance.com/en-IN/support/announcement/detail/115000599831

### 3.2 Spot versus short exposure

Ordinary Spot BUY/SELL trades use owned balances and do not create a native naked short. In the proposed scope, Spot is long/flat inventory trading. Short exposure belongs to an eligible Futures contract; it must not be falsely labelled as a Spot short. Spot Margin borrowing/shorts are excluded from initial release unless separately researched and approved.

### 3.3 AI autonomy and deterministic safety

AI must own market interpretation, strategy selection and adaptive trade proposals. An independent deterministic Safety Kernel must retain veto power and must not be overrideable by a model. It enforces loss/exposure limits, stale-data blocks, exchange filters, product eligibility, kill switch, account/order reconciliation and explicit live-trading authorisation. A self-modifying unbounded executor would be unauditable and unsafe. Models are adaptive; the safety envelope is not.

### 3.4 Fees are not a single constant

Binance support pages reviewed for this plan describe up to 25% Spot/Margin and up to 10% USDⓈ-M Futures fee savings for eligible BNB fee payment, subject to balance and configuration. Actual maker/taker rate, VIP tier, pair promotion, product, fill, fee asset and account settings must be verified. Futures funding is a separate cash flow, and forced liquidation may create additional costs. Never permanently hardcode a current maximum discount.

Sources:
- https://www.binance.com/en-IN/support/faq/detail/115000583311
- https://www.binance.com/en/support/faq/detail/98488a516eb84e3eb34605683dffd554

### 3.5 Free does not mean costless or always available

Public archives, APIs and open-source libraries can reduce cash cost, but multi-year trade/depth data, 10 symbols across many intervals, training and reliable 24/7 operation consume storage, bandwidth, electricity and compute. Measure the resource footprint and verify current free-tier terms. Do not presume GitHub Actions is a reliable always-on trading host or that GPU training is free. Zero-cost is an optimisation constraint, not permission to fabricate capabilities.

## 4. Scope boundaries

Research scope: Binance Spot and candidate USDⓈ-M Futures data, official historical archives and real-time streams, universe selection, feature/indicator/pattern definitions, strategy registry, ML and ensemble research, portfolio/risk mathematics, fees/funding, execution-cost models, history replay, shadow/paper operation, monitoring and cost feasibility.

Not authorised merely by this blueprint: real orders; production deployment; money movement; BNB purchase; account-setting changes; withdrawals; paid services; bypass of country/product restrictions; unapproved margin borrowing; options, COIN-M Futures, Spot Margin shorts or cross-exchange routing in the first release. An LLM may not invent and submit an unvalidated exchange order payload.

## 5. Proposed architecture

1. Market Data Plane: archive ingestion, WebSocket streaming, REST bootstrap/reconciliation, server clock and symbol metadata.
2. Data Quality Gate: checksums, schema, gaps, duplicates, impossible OHLC, timestamp units, incomplete candles and freshness.
3. Feature/Indicator Registry: versioned definitions, parameters, lookback/warm-up, units, missing-value rules and leakage tests.
4. Universe Scanner: eligible product, rolling quote volume, spread/depth/impact when observable, listing age, history quality and exclusion reason.
5. Feature/Regime Service: per-asset and cross-asset data, volatility/trend/liquidity/funding regime.
6. AI Brain Layer: narrow role-specific contracts described below.
7. Candidate/Ensemble Selector: compare only reviewed models/strategies using walk-forward evidence, uncertainty and calibration; allow NO TRADE.
8. Portfolio Allocator: combined Spot/Futures exposure, correlations, available equity, loss budget and capital proposals.
9. Deterministic Safety Kernel: veto malformed or excessive proposals.
10. Order Manager: current exchange filters, eligible orders, unique client IDs, partial-fill state, safe cancel/replace, rate-limit and timeout handling.
11. Position Supervisor: manage confirmed filled positions and protection orders.
12. Ledger/Monitoring: actual order events, fees in native asset and USDT equivalent, PnL, model versions, rejects and incidents.
13. Offline Learning Loop: data labels, experiments, reproducible backtests, model promotion and drift monitoring. Observation can be continuous; live weights cannot silently change.

## 6. Proposed ten AI brains

A brain is a specialised model/service, not necessarily an independent LLM. Ten LLM calls on every candle would be costly, slow and less reproducible than numerical inference. Use bounded services and share compute as measured.

| ID | Brain | Job | Output | Hard boundary |
|---|---|---|---|---|
| B1 | Universe & Liquidity | Determine eligible high-liquidity assets | Ranked universe with reasons | Cannot add stale or ineligible products |
| B2 | Data Quality & Anomaly | Assess missing, stale, abnormal feeds | Quality flags and confidence | Deterministic data checks take precedence |
| B3 | Market Regime | Assess trend/range/volatility/liquidity/funding state | Regime distribution and uncertainty | Uncertainty may force NO TRADE |
| B4 | Multi-Timeframe Context | Compare the eight requested horizons | Agreement/conflict map | Never treat unfinished candle as closed |
| B5 | Feature/Indicator Selector | Choose among registered, versioned features | Feature set and ablation reference | Cannot introduce untested maths into execution |
| B6 | Strategy Discovery/Tournament | Rank validated strategy candidates | Cost-adjusted ranking and evidence | Cannot promote based on in-sample results alone |
| B7 | Signal/Probability | Estimate return/risk distribution | Long/short/flat/NO TRADE proposal | Calibrated uncertainty and cost hurdle required |
| B8 | Portfolio/Sizing | Allocate exposure to fit portfolio constraints | Target exposure and risk proposal | Safety Kernel limits override |
| B9 | Execution/Cost | Propose allowed order/timing for low cost | Structured order proposal and cost estimate | No bypass of filters or permissions |
| B10 | Position Supervision/Learning | Propose exit/trailing changes and monitor drift | Exit updates, alerts, retraining request | Cannot loosen hard caps or silently mutate live model |

The independent **Safety Kernel** is additional to these ten roles and is mandatory. An audit function independently tests research claims. These are control functions, not extra prediction brains.

## 7. Dynamic timeframe cadence

Required horizons: 5m, 15m, 1h, 4h, 8h, 1d, 1w and 1M (monthly; Binance archive tooling represents the monthly interval as 1mo).

Use event-driven rather than wasteful constant full-model inference:
- Feed health and position safety: continuous/event-driven.
- 5m/15m: closed-bar decisions plus separately governed safety monitoring.
- 1h/4h/8h: relevant close or material market event.
- 1d/1w/1M: on each horizon close and scheduled portfolio review.
- Protective position/order state: monitored independently from slow timeframe model inference.

Normalise timestamps internally to UTC and optionally display Asia/Kolkata. A signal calculated from a bar close cannot be filled at that same already-known close unless a causal and feasible execution assumption proves it. Use 1m/trade data or more granular evidence when needed to assess intrabar stop behavior; OHLC bars alone cannot prove precise queue position or fill quality.

## 8. Top-10 universe methodology (exact coins not yet chosen)

1. Query current official Spot and Futures exchange information and each product's eligibility.
2. Start with USDT-quoted assets with required Spot/Futures markets if paired market exposure is part of the first release.
3. Rank by rolling quote-volume/liquidity over multiple windows; one 24-hour spike is not enough.
4. Evaluate spread, depth and market impact where reliable observations exist; quote volume alone is insufficient.
5. Exclude delisted, suspended, leveraged-token, ambiguous-metadata or poor-quality-data products under documented rules.
6. Apply minimum history and data-completeness requirements and show which candidates fail.
7. Use a rank buffer/hysteresis and controlled update schedule to avoid universe churn.
8. Reconstruct point-in-time membership for historical tests. Backtesting today's winners over earlier years causes survivorship bias.
9. Record timestamp, ranks, input data, exclusions and reason codes.
10. Produce an evidence-backed candidate list for user review before freezing the initial universe.

## 9. Feature and strategy catalogue

Do not claim to implement literally every indicator or chart pattern. Create a versioned, auditable candidate registry across:
- Returns, momentum, trend slopes, moving-average families and crossovers.
- Volatility, ranges, ATR-like measures and volatility-of-volatility.
- Volume, quote volume, volume profile approximations, trade imbalance and taker flow where source fields support them.
- Mathematically defined candle geometry and candlestick pattern rules.
- Numeric price/volume structures from line/OHLC charts; no subjective visual chart label without a formal rule.
- Support/resistance and breakout features with strict lookback cutoff.
- Trend following, momentum, breakout, mean-reversion, volatility-aware sizing, funding/carry, Spot/Futures basis and microstructure candidates.
- Regime classification, change-point/anomaly measures, cross-asset correlations, market breadth and concentration.
- Derivatives-only funding, mark/index basis, open interest/liquidations only when history and timestamp availability are verified.
- Spread/depth/impact features when observed and stored; do not invent historical order-book data.

Each feature needs a definition, units, version, parameters, lookback/warm-up, missingness behavior, source, leakage tests, cost and ablation outcome. Each strategy is a falsifiable hypothesis with a benchmark and failure conditions. More features do not automatically improve a system.

## 10. Learning and model promotion

Research ladder:
1. No-trade baseline and simple deterministic benchmark strategies.
2. Feature/strategy ablations and statistical review.
3. Supervised classification/regression/quantile or distribution models using chronological splits.
4. Regime-conditioned selection and calibrated ensembles.
5. Champion/challenger comparison with uncertainty-aware abstention.
6. Reinforcement learning and automated mathematical hypothesis generation only as research experiments until they outperform credible baselines under the same strict protocol.
7. Shadow predictions and paper observation with real market input and virtual execution.
8. Versioned promotion review with reproducible evidence and rollback.

LLMs can summarise evidence, catalogue candidate ideas and propose hypotheses. They are not market data and do not guarantee correct mathematics. A formula proposed by AI must be defined with units, independently checked, tested, benchmarked and evaluated on unseen data. Live model weights may not update silently. Any model promotion must be explicit, versioned and reversible.

## 11. Data acquisition and integrity

Primary source candidate: https://github.com/binance/binance-public-data . The official archive documents daily/monthly data and checksum files for available markets. Limit downloads to a justified initial universe and intervals. Do not commit large raw archives to Git by default; commit manifests, source URL, source period, checksums, local hashes, schema and audit output. If raw data lives elsewhere, record exact location and access assumptions.

Controls:
- Verify official checksum before extracting where available and calculate local SHA-256.
- Record source URL, retrieval time, file size, row count, schema and exact timestamps.
- Record the exact time unit/timezone and handle documented Spot timestamp-unit changes for data from 2025 onward; never infer a unit silently.
- Test duplicate/missing/non-monotonic timestamps, impossible OHLC, malformed rows, zero/negative fields where invalid, volume anomalies, close-time alignment and partial final candle.
- Compare selected archive samples to current official API responses.
- Distinguish trade/close price from contract price, mark price, index price and funding.
- Preserve point-in-time symbol listing/delisting/status.
- Missing data remains missing; block any test that requires unavailable inputs.
- Report when historical depth/order-book data is absent; don't infer precise liquidity or fill quality from candles alone.

Suggested data fidelity tiers:
A. Complete OHLCV archives with provenance.
B. Trade/aggregate-trade detail where available.
C. Historical funding and mark/index series where verified.
D. Historical depth snapshots only when a verifiable archive exists; never assume decade-long depth history.

## 12. Fees, BNB and capital accounting

Treat 10,000 USDT as research/paper initial equity. It is not evidence of exchange balance and does not authorise deposit or trading. Before live setup, decide whether a separate BNB fee reserve sits inside or outside that 10,000 USDT.

Record:
- gross realised/unrealised PnL;
- entry/exit commission on every actual or simulated partial fill, with maker/taker assumptions disclosed;
- whether BNB was actually deducted and the native fee amount/USDT-equivalent value;
- BNB inventory mark-to-market if included in total equity;
- spread, slippage, impact, latency, rejected/missed orders and partial fills;
- actual funding cash flows at contract-specific timestamps;
- borrow/interest only for a separately approved borrowing product;
- liquidation-related costs, transfers/conversions and other realised trading costs.

Net PnL = Gross Trading PnL - Entry/Exit Commission - Spread/Slippage/Impact - Funding Paid + Funding Received - Borrow/Interest - Other Realised Trading Costs.

No assumed maximum BNB discount is applied unless current account/product settings and realised fill records prove it. Fee discount does not make trading free, remove funding or guarantee positive expectancy.

## 13. Risk and sizing mathematics

All equations below are candidates for research and independent tests. They are not approved live risk settings.

Let E be total equity in USDT after balance/position reconciliation; r an approved maximum trade-loss fraction; R = E × r the planned risk budget; Pin estimated entry price; Pstop initial stop price; d = abs(Pin - Pstop) plus expected per-unit exit/fee/slippage cost. For a linear base-quantity instrument and d > 0, Qrisk = R / d. Actual Q is the minimum permitted by Qrisk, available balance, symbol filters, gross/net exposure, portfolio/correlation caps and liquidity/impact constraints. Notional ≈ Q × Pin for a linear instrument; use contract multiplier and instrument-specific equations where necessary. Round quantity down to the current step size, then recheck minimum quantity, notional, price tick and full planned risk. Reject if constraints fail.

Leverage does not increase the permitted loss budget; it changes initial margin and liquidation sensitivity. Stops are not guaranteed prices. Model gaps, slippage, trigger source, maintenance margin and protection-order state.

Portfolio checks must include risk for existing positions and pending orders, cross-asset correlation, total gross/net exposure across Spot and Futures, available balance, maintenance margin, drawdown/daily loss, funding/cost drag, liquidity, multiple-entry cumulative risk and stale feed/metadata.

No martingale, unbounded averaging down or unbounded pyramiding. Every proposed additional entry must recalculate combined worst-case risk including existing positions and pending orders. Initial numerical caps must be selected only after stress research and review; none is approved for live use.

## 14. Dynamic stops, take-profit and trailing protection

AI may propose initial stop, target, time stop, volatility-aware trail, break-even shift, scale-out and gain-locking exit. Each change must include triggering observations, model version, source price, reason and risk impact.

- A stop may tighten or remain unchanged; it may not move farther away simply to avoid realising loss unless a separately reviewed policy proves why this is permitted.
- Trailing protection is monotonic toward lower risk: a long stop must not decrease; a short stop must not increase.
- Define "trailing profit" as a gain-locking exit policy with a precise formula, not a vague label.
- Avoid cancel/replace churn using thresholds, idempotent identifiers and tested recovery.
- For Futures, verify mark-price/contract-price trigger semantics, close/reduce-only restrictions, position mode and current conditional-order documentation.
- Never assume the same trailing feature exists or behaves the same on Spot and Futures.
- If connectivity or order state is ambiguous, stop opening new risk; reconcile positions and protective orders first.

## 15. Historical validation protocol

Use chronological train/validation/test windows and rolling or anchored walk-forward tests. Keep a final untouched holdout. Avoid random time-series shuffling for primary claims. Every feature is limited to information available at decision time.

Model costs and execution: historical/current fee assumptions, maker/taker sensitivity, spread, slippage/market impact, funding at actual times, latency, missed/partial fills, exchange filters, conservative stop-gap treatment, maintenance margin/liquidation and BNB-fallback fee behavior.

Report net return, drawdown and duration, volatility, Sharpe/Sortino with caveats, profit factor, expectancy, turnover, exposure, worst trade/day, tail outcomes, fee/funding share, fill rate and stability by symbol/timeframe/regime. Win rate alone is not enough.

Use no-trade and simple baselines, feature ablation, parameter sensitivity, multiple-testing awareness, purged/embargoed splits if labels overlap, uncertainty estimates and failure analysis. A candidate that works only in a narrow window or fails after realistic costs does not pass promotion.

Historical replay is a model of execution assumptions. Paper trading uses market data but virtual orders/fills. Both must be labelled honestly and never reported as actual live fills. No synthetic prices or convenient invented PnL.

## 16. Research and release gates

- G0 Charter: scope, assumptions, unresolved decisions and locks recorded.
- G1 Jurisdiction/product: applicable rules and account-specific Spot/Futures eligibility checked; restriction bypass forbidden.
- G2 API/fees/contracts: official endpoints, symbol filters, BNB settings, funding and order semantics evidenced.
- G3 Data feasibility: exact symbol-by-symbol coverage, checksums and known gaps documented.
- G4 Universe: point-in-time ranking method and candidate assets proven.
- G5 Maths/risk: formula units, portfolio accounting and stress tests reviewed.
- G6 Research protocol: baselines, candidate hypotheses, features and success/failure criteria pre-registered.
- G7 Backtest: leakage, fees, walk-forward, robustness and untouched holdout pass.
- G8 Shadow/paper: feed resilience, risk vetoes, reconciliation and metrics observed for a pre-registered period.
- G9 Security/cost: secret management, restart/kill-switch and actual resource/uptime profile pass.
- G10 Live readiness: all earlier gates pass, remaining risks documented and user explicitly authorises exact limited live scope. This blueprint does not authorise G10.

A failed gate blocks progression. Narrative alone cannot pass a gate; attach data, source documents, test output or reproducible audit results.

## 17. Zero-cost strategy

Prefer open-source Python tools, public Binance archives/API, GitHub for source/specifications/manifests and CPU-first research until measured requirements justify another choice. Keep datasets and compute bounded. Record the actual free-service terms, quotas, persistence, uptime, commercial/trading restrictions and exit plan. Do not store secrets or large raw archives in Git. GitHub Actions is not assumed to offer persistent 24/7 trading uptime. If zero-cost infrastructure cannot meet a safety requirement, remain non-live and report the blocker rather than relaxing the requirement.

## 18. Implementation sequence after research

1. Governance, manifests and automated audits.
2. Data coverage inventory, checksums and deterministic validators.
3. Exchange metadata and point-in-time universe snapshots.
4. Time-series store, timezone normalisation and timeframe-parity tests.
5. Feature registry, mathematical definitions and leakage tests.
6. Baselines and event-driven backtester.
7. Fees, funding, liquidation and execution-cost modules.
8. Experiment registry, walk-forward validation and model versions.
9. AI brains in shadow-only proposals with schema validation.
10. Independent risk kernel and kill switch, tested without AI.
11. Paper order management with explicit virtual-fill labelling.
12. Live-feed shadow monitoring and operational resilience tests.
13. Supported test environment, with reset limitations documented.
14. Independent security, compliance and quality audit.
15. Only after separate explicit approval, consider a limited live stage.

## 19. Open decisions

- Verify current Binance Futures eligibility for this account/jurisdiction and applicable requirements.
- Rank and review candidates before choosing the top ten.
- Decide whether BNB fee reserve is inside or outside the 10,000 USDT budget.
- Confirm first-release Futures product (recommendation: study USDⓈ-M perpetual first); COIN-M and Spot Margin remain outside initial scope by default.
- Choose numerical research risk limits after stress tests; no live parameters are approved.
- Measure available CPU/storage/network and find a realistic zero-recurring-cost setup.
- Decide whether any non-Binance history is permitted as a separately labelled supplemental research set.

## 20. Current status

This is a research specification, not trading software. Preliminary source review confirms official Binance archive/checksum documentation, requested interval naming, different published BNB fee discounts, separate Futures funding costs, Spot Testnet reset behavior, and a ten-year Binance-only history limit. Symbol-level data coverage, exact account/product access, final coin universe, strategy evidence, math tests and all implementation remain pending. See RESEARCH_REGISTER.md, EVIDENCE_REGISTER.md, DECISION_LOG.md and QUALITY_AUDIT.md.

## 15. Binding execution plan and expanded AI requirements

The authoritative numbered roadmap, phase exit gates, full AI decision contract, ten logical brain roles, continuous-scanner rules, dynamic position/exit rules, zero-cost feasibility contract and per-response anti-drift audit are maintained in [PLAN_AND_PHASE_LOCK.md](PLAN_AND_PHASE_LOCK.md). Read that file before selecting any new task. Keep this Blueprint as the enduring complete project specification and update it when requirements, architecture or verified constraints change. A plan or role description is not evidence of implementation.

User's AI-autonomy requirement means AI dynamically selects among evidence-validated options and can abstain; it does not mean an untested model can bypass deterministic risk, product, data-quality or execution controls. All eight requested horizons, Spot/Futures distinctions, BNB commission verification, point-in-time top-ten membership, full net-cost accounting and 10,000 USDT paper-equity semantics remain mandatory.
