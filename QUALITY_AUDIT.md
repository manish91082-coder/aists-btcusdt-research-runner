# Quality, Logic, Mathematics and Coverage Audit

Living fail-closed checklist. Mark PASS only with linked evidence; an unrun test is NOT-STARTED.

## A. Sources and evidence
- [ ] Primary publisher and canonical source URL recorded.
- [ ] Access date and document update date recorded where available.
- [ ] Claim is no broader than the source.
- [ ] Secondary sources do not close critical fee/product/legal gates.
- [ ] Conflicts or stale evidence preserved and reconciled.
- [ ] Research result has reproducible provenance.

## B. Historical data
- [ ] Exact per-symbol/per-market earliest and latest timestamps recorded.
- [ ] Source URL, archive period, size, SHA-256 and official checksum result recorded.
- [ ] Timestamp units/timezone/schema/decimal format verified.
- [ ] Duplicate, gap, out-of-order, impossible OHLC and malformed rows checked.
- [ ] Candle close time and partial-candle policy tested.
- [ ] Sample compared against official API data.
- [ ] Funding, mark and index series are distinct and joined only as-of decision time.
- [ ] Unavailable historical depth explicitly disclosed.
- [ ] Listing/delisting/status are point-in-time facts.
- [ ] Survivorship and universe look-ahead bias checked.

## C. Causal correctness / leakage
- [ ] Features are limited to data available at the decision time.
- [ ] No unfinished candle is treated as closed.
- [ ] Simulated orders fill no earlier than causally possible.
- [ ] Future high/low/close/volume is not used in earlier decisions.
- [ ] Normalisation, imputation and feature selection fit on training data only.
- [ ] Label overlap addressed with chronological/purged/embargo splits as needed.
- [ ] No random shuffle for primary time-series evaluation.
- [ ] Final holdout untouched during tuning.
- [ ] AI-proposed equations are versioned, dimensionally checked and tested.

## D. Cost and ledger
- [ ] Current fee schedule, tier, promotion and BNB deduction assumptions evidenced.
- [ ] Actual BNB deduction and fallback fee asset represented.
- [ ] Fee applied to every partial fill.
- [ ] Funding is charged/credited at correct timestamps and direction.
- [ ] Spread/slippage/impact, latency, rejects and partial fills tested.
- [ ] Gaps through stops and OHLC ambiguity treated conservatively.
- [ ] Mark-price/contract-price triggers checked from current docs.
- [ ] Maintenance margin/liquidation costs represented for Futures.
- [ ] PnL reconciles with a hand-checked trade ledger.

## E. Strategy/model validity
- [ ] No-trade and simple baselines included.
- [ ] Each hypothesis includes mechanism and failure/falsification condition.
- [ ] Multiple testing and selection bias addressed.
- [ ] Walk-forward and untouched holdout reported separately.
- [ ] Results broken down by asset, timeframe, regime and cost scenario.
- [ ] Reasonable cost and parameter stress tests passed.
- [ ] Uncertainty/calibration and abstention evaluated.
- [ ] Promotion and rollback reproducible.
- [ ] No single narrow window or unexplained outlier dominates.
- [ ] Selection follows pre-registered criteria.

## F. Risk and execution
- [ ] Size formulas have consistent units and instrument multipliers.
- [ ] Quantity rounds down and filters/risk are rechecked after rounding.
- [ ] Existing positions and pending entries included in risk.
- [ ] Cross-asset concentration and Spot/Futures aggregate exposure checked.
- [ ] Multi-entry cumulative risk limited; no unbounded martingale/pyramiding.
- [ ] Stops/trailing state persisted and monotonic in risk-reducing direction.
- [ ] Duplicate, timeout-unknown, partial-fill, cancel/replace and reconnect cases tested.
- [ ] State reconciliation required before new risk after disconnect.
- [ ] Kill switch/reject-all tested.
- [ ] AI cannot bypass Safety Kernel.

## G. Eligibility, security and cost
- [ ] Product/account eligibility under current terms verified.
- [ ] Applicable legal/tax requirements reviewed through appropriate sources/adviser.
- [ ] No restriction bypass.
- [ ] API credentials least-privilege, never in Git/logs, withdrawals disabled by default.
- [ ] Free-tier terms, persistence and uptime verified.
- [ ] 24/7 run not based on an assumed always-on free service.
- [ ] Resource use measured before choosing heavy models.

## H. Release gates
- [ ] G1 jurisdiction/product eligibility.
- [ ] G2 API/fees/contracts.
- [ ] G3 data coverage and quality.
- [ ] G4 point-in-time universe.
- [ ] G5 mathematical risk review.
- [ ] G6 pre-registered hypotheses/benchmarks.
- [ ] G7 backtest/leakage/statistical audit.
- [ ] G8 shadow/paper operation with declared limitations.
- [ ] G9 security/resilience/cost.
- [ ] G10 remains LOCKED pending explicit user authorization for exact limited live scope.

## Audit summary as of 2026-10-21
Requirements and design documented, early research only. Source reconnaissance is partial. Symbol-level data audit, empirical performance, training, backtest, paper-trading and code tests are NOT-STARTED. Live readiness is LOCKED.