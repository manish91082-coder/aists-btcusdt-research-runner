# AI-Driven Autonomous Trading Ecosystem — Architecture and Control Plan

**Status:** Proposed research architecture; not yet implemented as an end-to-end trading system.  
**Last updated:** 22 October 2026  
**Repository:** https://github.com/manish91082-coder/aists-btcusdt-research-runner

## 1. Mission and target hierarchy

The user's explicit primary target for this workstream is **1,000 USDT initial equity → 10,000,000 USDT**. This is a 10,000× increase, or a 999,900% gain over starting equity, before considering the uncertainty of future market returns. It is an objective for research and planning, not a promise or forecast.

A previously tracked goal was the USDT equivalent of ₹10 crore, approximately 1,061,120.54 USDT at a dated ₹94.24/USDT snapshot. That is a distinct, lower reference target and must not be silently conflated with the now-explicit **10M USDT primary target**. Keep it as a historical/secondary milestone unless the user explicitly changes the target hierarchy.

“Compounding” means adding realized net profits to equity before subsequent risk sizing. It does not prescribe hourly bars or mandatory hourly trading.

The AI system should seek the fastest evidence-supported route to the target while optimizing for survival, net-of-cost returns, controlled drawdowns and robust performance. It must not maximize raw backtest return at the expense of blow-up risk or misrepresent a desired return as an achievable expectation.

## 2. Fully AI-driven decisions, with bounded authority

The intended live decision loop is autonomous: no manual selection of each trade, entry, exit or stop adjustment. AI/model outputs may dynamically adapt to current market conditions, but only inside a deterministic risk and execution envelope.

The system should decide or recommend, as appropriate to its validated capability:
- Whether to trade, remain flat, or reduce exposure.
- Market/universe selection based on a documented, point-in-time eligible universe and verified liquidity.
- Direction (long/short where the instrument permits), strategy family and timeframe.
- Entry trigger, order type and invalidation conditions.
- Initial stop-loss, stop distance, position size and leverage constraints.
- Take-profit, partial exit, trailing stop-loss and trailing-profit/exit logic.
- Whether to tighten, loosen, replace or cancel an order, subject to risk invariants.
- Exposure across correlated instruments, capital allocation and portfolio-level risk.
- Regime classification, uncertainty estimates and when to abstain.
- Post-trade attribution: signal quality, execution costs, slippage, missed fills and model drift.

AI may optimize within constraints; it must never override hard risk limits, data-integrity checks, exchange filters, kill switches or account-level safety controls. “No manual trading decisions” does not mean “no human governance”: deployment, capital permissions, policy changes and emergency review remain separately authorized gates. No live orders, exchange credentials or funds movement are authorized by this research plan.

## 3. Layered system architecture

1. **Data and provenance layer**
   - Ingest exchange data and market metadata with source URLs, retrieval time, checksums, schema, timestamps, gap/duplicate checks and product-specific constraints.
   - Keep raw immutable inputs separate from normalized features.
   - Point-in-time universe membership; do not use future listing, delisting or volume information.
   - Detect stale, missing, malformed, delayed or conflicting feeds; fail closed.

2. **Market-state / feature layer**
   - Multi-timeframe price, volume, volatility, liquidity, spread, order-book and derivatives features only where validated data exists.
   - Regime and event context, funding/basis where relevant, cross-asset/correlation features where source quality supports them.
   - Every feature must be reproducible and available at the simulated/live decision timestamp.

3. **AI research and ensemble layer**
   - Separate models for regime detection, direction/return distribution, volatility/risk, execution-cost estimation and trade/no-trade decisions.
   - Compare learned models against transparent baselines; use calibrated uncertainty and abstention.
   - Ensemble/voting or meta-controller only when it demonstrates out-of-sample improvement after costs.
   - Maintain model/version registry, training-data lineage, feature definitions and experiment logs.
   - No unvalidated LLM free-form output may directly submit exchange orders. Use typed, schema-validated actions and deterministic policy checks.

4. **Decision and portfolio layer**
   - Convert forecasts and uncertainty into expected net edge, risk-adjusted sizing and portfolio constraints.
   - Estimate expected fees, spread, slippage, funding/borrow costs, impact and liquidation risk before accepting a trade.
   - Reject trades when expected edge is not sufficiently positive after costs, uncertainty is high, or risk budget is exhausted.
   - Position size is derived from equity, stop distance, volatility, liquidity and aggregate risk budget, not confidence language alone.

5. **Execution layer**
   - Exchange adapter, precision/tick/step-size validation, minimum notional checks, idempotent order intents, partial-fill reconciliation and retry limits.
   - Use limit/market/other supported order types only after execution research; model latency and adverse selection.
   - Reconcile exchange state against internal state continuously. Unknown order state triggers safe reconciliation, not duplicate orders.

6. **Risk engine and kill switches**
   - Deterministic pre-trade, intratrade and portfolio-wide controls that AI cannot bypass.
   - Hard limits for maximum position/leverage, per-trade risk, aggregate exposure, daily/rolling drawdown, correlated exposure, liquidity, stale data and order rate.
   - Stop new entries on feed/model/exchange anomalies, repeated rejected orders, unexplained P&L mismatch or risk-limit breach.
   - Emergency flattening is not always safe in illiquid/failed markets; define a tested incident policy rather than assuming one action fits every state.

7. **Evaluation and learning loop**
   - Record every signal, model version, feature snapshot, proposed action, policy decision, order, fill, fee, funding payment and realized/unrealized P&L.
   - Attribute net results to alpha, costs, sizing, exits and execution; detect drift.
   - Models are retrained or promoted only through reproducible walk-forward evaluation and controlled promotion gates. No uncontrolled online self-modification in live trading.

## 4. Dynamic entry, exit and profit-protection logic

The goal is not to hard-code one universal stop or take-profit. Candidate policies should be evaluated per strategy/regime:
- **Entry:** require a time-valid signal, adequate expected net edge, liquidity and risk capacity. AI can choose abstention.
- **Initial stop:** anchored to explicit invalidation and a volatility/liquidity-aware risk budget; include gap and slippage stress.
- **Trailing stop:** candidate rules may use volatility bands, swing structure or regime-aware thresholds. Only ratchet behavior and modifications that preserve approved risk invariants are allowed; avoid accidental widening that increases total risk.
- **Take-profit:** evaluate fixed, scale-out, distribution-based and risk/reward-conditioned exits net of costs.
- **Trailing profit:** activate only under a defined, tested rule; account for fee/spread and avoid giving back more than the policy allows.
- **Exit/reversal:** require a valid signal/position-state transition; do not flip repeatedly because of noisy model outputs.
- **No-trade:** a valid first-class decision when net edge is weak, uncertainty is high or market data/execution is unreliable.

These are research candidates, not proven optimal rules. Do not deploy a parameter merely because it performs best on the same sample used to tune it.

## 5. Net economics and objective function

All performance must be assessed after relevant costs: trading fees, spread, slippage/market impact, funding, borrowing, conversion, exchange constraints and failed/partial execution. Keep gross and net P&L separate.

The decision objective should be multi-objective and constrained, not simply “maximize profit”:
- Maximize robust, out-of-sample expected log-equity growth / net return where statistically defensible.
- Penalize drawdown, tail loss, turnover and fragile parameter dependence.
- Enforce hard limits on risk of ruin, leverage, liquidity and operational failure.
- Account for uncertainty, costs and capacity; abstain when the estimate is unreliable.
- Report target-progress metrics but never distort signals just to force progress toward 10M.

## 6. Research and deployment gates

| Gate | Required evidence | Status |
|---|---|---|
| A0 — repository / math harness | Versioned helpers, deterministic tests, core docs | Current smoke tests pass |
| A1 — data integrity | Reproducible real data, provenance/checksums, schema and gap audit | Not started for target workstream |
| A2 — baseline simulator | No-look-ahead signals, realistic orders/fills/costs | Not started |
| A3 — AI model validation | Chronological splits, walk-forward, calibration, leakage and ablation checks | Not started |
| A4 — portfolio/risk validation | Drawdown, tail risk, ruin analysis, correlation and stress scenarios | Not started |
| A5 — execution simulation | Latency, spread, partial fills, rejected orders and reconciliation tests | Not started |
| A6 — paper/forward test | Frozen model/policy, realistic paper execution and monitoring | Not started |
| A7 — limited live pilot | Explicit user authorization, separate secrets/security review, strict caps and rollback | **Not authorized** |
| A8 — scale-up | Repeated live evidence, capacity and risk review | Not eligible |

No gate may be skipped because the target is urgent. Promotion criteria must be defined before evaluating results.

## 7. Required scorecard

Track initial/current equity, target multiple, net and gross returns, geometric growth, drawdown and recovery, tail loss, risk of ruin, exposure, leverage, turnover, win/loss distribution, expectancy, cost breakdown, fill quality, strategy/regime attribution, model calibration/drift, rejected-trade reasons, uptime and safety-trigger counts. Publish failed runs and negative results as well as successes.

## 8. Governance and security

- Current stage is research only. No exchange API secrets in source code, logs, notebooks, issue text or artifacts.
- Never grant withdrawal permission to a trading key. When a future live stage is explicitly approved, use least-privilege keys, IP restrictions where supported, environment secrets, separate paper/live accounts and strict capital caps.
- Risk limits and kill switches are deterministic and outside model authority.
- No automatic strategy promotion or live-policy mutation without a verified release gate.
- Tax/TDS remains deferred per current scope.
- Each substantive run gets a separate execution log; master research log and status are updated with exact evidence and commit/run links.

## 9. Immediate implementation roadmap

1. Confirm this architecture in the repository and preserve the 10M USDT target as the primary goal.
2. Build a source-traceable BTCUSDT data acquisition/integrity manifest.
3. Implement deterministic fee-aware backtesting and order/fill simulation before advanced AI.
4. Establish no-trade, buy-and-hold where appropriate, trend and simple rule baselines.
5. Add AI components one at a time: regime, forecast distributions, cost model, policy/portfolio controller; compare each against baselines out of sample.
6. Build a hard-risk policy engine and test adversarial/operational failures.
7. Run walk-forward, stress, ablation and paper/forward evaluation; do not claim profitability until evidence supports it.
8. Keep live trading disabled until separate explicit authorization and safety review.

## 10. Non-negotiable truth statement

The architecture above is a design plan, not an already functioning autonomous trading bot. Current code does not yet fetch/validate market data, generate AI signals, simulate realistic fills, manage exchange orders or prove a profitable edge. The 10M USDT target is aspirational and highly uncertain; no timeline or return is guaranteed.
