# Strategy Research Dossier v0.1

Updated: 2026-10-21
Status: HYPOTHESES REGISTERED; NOT BACKTESTED; NONE APPROVED FOR LIVE USE

## Scope and truth status
This is a falsifiable research plan, not a claim of profitability. No strategy below has been run on project data; no results are invented. The AI may choose NO TRADE. User priority: strategy research and Binance data now; taxation/jurisdiction research is deferred, not waived as a later live-execution gate.

## 1. Candidate strategy hypotheses

### S-01 Multi-timeframe trend following
Hypothesis: a slower completed timeframe's trend plus faster-timeframe confirmation may identify continuation better than unconditional entry after costs. Features: lagged returns, moving-average/slope family, realised volatility and volume. Compare each timeframe alone, pairwise stacks, and volatility-normalised vs fixed exits. Failure modes: range whipsaws, late entries, gaps and turnover costs.

### S-02 Regime-filtered mean reversion
Hypothesis: extreme deviation from a causal rolling centre may revert in a range regime before fees overwhelm the edge. Features: rolling z-score/robust dispersion, bounded momentum and volatility regime. Compare unfiltered vs range-gated variants. Failure modes: trend acceleration, structural breaks, repeated entries and funding drag.

### S-03 Volatility breakout after compression
Hypothesis: a breakout beyond a prior-window boundary after measured compression may capture expansion. Inputs: lagged rolling high/low, realised volatility/range, quote volume and trade count where available. Never use a candle's final high/low to claim an earlier fill. Failure modes: false breaks, widening spread, gaps and late execution.

### S-04 Momentum continuation
Hypothesis: lagged return persistence conditioned on volatility/liquidity may contain incremental signal after costs. Compare regularised linear/logistic models and simple thresholds before complex models. Control correlated lookbacks and multiple testing. Failure modes: reversals, crowding, turnover and regime instability.

### S-05 Regime-gated strategy selector
Hypothesis: selecting among S-01 to S-04 from as-of regime features may outperform a fixed strategy. Compare against the best fixed strategy chosen on training data only. Regime boundaries are fitted on training data, frozen within each fold, and tested walk-forward. Main risk: overfitting historical winners.

### S-06 Formal candle and price-structure features
Hypothesis: deterministic candle geometry may add incremental information conditional on regime/liquidity. Features: body/range, upper/lower wick, gap/return, inside/outside range and explicitly defined engulfing-like inequalities. Named patterns are not assumed profitable. Require ablation lift net of costs.

### S-07 Futures funding/basis-aware filter
Hypothesis: verified funding and basis data can alter the net attractiveness of directional Futures positions. Apply funding at actual event timestamps and by position direction/size. Funding is not commission and is not assumed payable in BNB. Do not test until history coverage and semantics are verified.

### S-08 Liquidity/execution-aware filter
Hypothesis: rejecting signals in wide-spread, shallow or high-impact conditions may improve net results despite fewer trades. Use observed book/trade data only; OHLCV does not reveal historical order-book depth. Compare gated and ungated signals with identical chronological splits/cost logic.

### S-09 Cross-asset confirmation and concentration
Hypothesis: point-in-time breadth/correlation context may reduce redundant correlated exposure. Reconstruct historical universe membership as of each date; today's top ten cannot be projected backward. Evaluate portfolio tail risk and drawdown, not only individual trade metrics.

### S-10 Supervised return-distribution model
Hypothesis: a calibrated model can estimate forward net-return/risk distributions better than simple baselines. Define labels, horizon, fees, barrier/exit rules and overlapping-label handling before training. Begin with regularised linear/logistic and tree models if measured compute allows; neural networks only if they add stable out-of-sample value. Output uncertainty and abstention, not a bare BUY/SELL.

### S-11 Portfolio sizing/allocation tournament
Hypothesis: risk-budget, volatility and correlation-aware sizing may improve robustness versus equal notional. Compare equal-notional, volatility-scaled and stop-risk sizing under identical hard portfolio caps. Recompute combined risk for every additional entry; no martingale or unbounded averaging down.

### S-12 Exit-policy tournament
Hypothesis: stop/target/trailing/time exits may vary by instrument/regime only if a pre-registered comparison shows stable net benefit. Compare fixed risk multiples, volatility-normalised stop, time stop, opposite-signal exit, monotonic trailing and gain-locking exits. OHLC bars cannot reliably resolve intrabar stop/target order; use conservative ambiguity treatment or finer data. Long trailing stop may only stay/rise; short trailing stop may only stay/fall.

## 2. Research order
1. No-trade and simple exposure-matched baselines.
2. S-01 trend and S-02 mean reversion.
3. S-03 breakout and S-04 momentum.
4. S-06 candle features as ablations, not assumed alpha.
5. S-05 regime selector after base strategies.
6. S-07 funding-aware Futures only after funding coverage audit.
7. S-08 liquidity filter only after defensible spread/impact observations.
8. S-09 portfolio context and S-11 allocation.
9. S-10 supervised model after clean labels and baselines.
10. S-12 exit tournament after simulator handles gaps/intrabar ambiguity.
Order reflects auditability/dependencies, not expected profitability.

## 3. Binance data needed

Official references reviewed 2026-10-21:
- Spot exchange information/current symbol rules: https://developers.binance.info/en/docs/catalog/core-trading-spot-trading/api/rest-api/general
- Spot API rate limits: https://developers.binance.info/en/docs/products/spot/rest-api
- Spot filters: https://github.com/binance/binance-spot-api-docs/blob/master/filters.md
- USDⓈ-M Futures market-data/kline reference: https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data
- Official archives, interval names, checksums and timestamp notes: https://github.com/binance/binance-public-data

Minimum manifest fields: market/product, symbol, quote asset, status, source endpoint/archive path, capture/download time, interval, first/last timestamp, row count, missing/duplicate/out-of-order counts, checksum and local SHA-256, timestamp unit/timezone, schema/version, partial-candle handling and API/archive comparison outcome. Record data availability for OHLCV, quote volume, trade count, taker-buy volume, funding, mark/index/contract prices, trades and depth.

Capture timestamped current exchange metadata; current metadata is not historical truth. Preserve point-in-time listing/status where evidence exists. Required horizons are 5m, 15m, 1h, 4h, 8h, 1d, 1w and monthly. Binance archive names monthly as 1mo rather than 1M. Official archive docs state Spot archive timestamps from 2025-01-01 onward use microseconds in documented fields; older data may use different units. Ingestion must use source/schema metadata and tests, never guessing units. Archives may be updated, so preserve archive path, retrieval date and checksum.

For Futures, separately verify funding history and mark/index/contract-price coverage before use. Current bid/ask/depth is useful for live scanner and observed execution research; it is not a substitute for historical order book data. Do not invent historical depth from candles. Kline quote volume/trade count are liquidity proxies, not a full book.

## 4. Cost-aware hurdle and BNB commission policy
ExpectedNet = ExpectedGrossMove - EntryCommission - ExitCommission - SpreadCost - SlippageImpact - ExpectedFundingCost - OtherKnownExecutionCosts.

A positive direction prediction alone is insufficient. ExpectedNet must exceed a pre-registered uncertainty/risk buffer and pass portfolio/risk gates. Cost estimates must be calibrated from observations, not set as one universal constant for all symbols, sizes and regimes.

Record commission amount, fee asset and equivalent valuation per fill. Prefer BNB commission deduction where the actual product/account supports it and sufficient BNB is available. Verify actual deduction from execution/account records; a configuration toggle alone is not proof. If BNB is insufficient or a product/fill does not support it, model and report fallback. Funding, spread, slippage, impact and liquidation are distinct costs and are not assumed payable in BNB.

## 5. Experiment protocol
For every run record strategy/version, hypothesis, falsification criteria, symbol/market/interval, data revision and dates, feature definitions/warm-up, point-in-time universe, train/validation/test boundaries, execution timing/fill assumptions, fee/BNB scenario, funding/slippage assumptions, software/config/revision/seed, gross/net results, turnover, drawdown/duration, exposure, tail loss, trade count, cost decomposition, uncertainty, per-symbol/timeframe/regime results, ablations and failures.

Acceptance:
1. No-trade and simple baselines included.
2. No future information or unfinished-candle leakage.
3. Same fair cost/fill assumptions across candidates.
4. Tuning restricted to training/validation.
5. Walk-forward separate from untouched final holdout.
6. Multiple testing/selection bias disclosed.
7. Robustness to adverse fee/slippage/funding scenarios.
8. Failed holdout candidates are not repeatedly retuned against that holdout.
9. Model can abstain when uncertain or net expectancy is below cost hurdle.
10. No PASS without reproducible test output.

## 6. Multi-timeframe causal rules
Only completed bars for close-based features. A close signal executes no earlier than a causally possible next point. Join higher-timeframe values backward/as-of; never forward-fill a future close. Eight correlated timeframes are not eight independent confirmations. Log each feature's source timeframe and age. Position safety monitoring remains independent of slow timeframe inference.

## 7. Next research actions
1. Design the market-data manifest and validator.
2. Audit one representative archive end-to-end: exact path, checksum, schema, timestamp unit, first/last bars, gaps and sample comparison to official API.
3. Verify Futures funding/mark/index history coverage.
4. Pre-register S-01 through S-04 thresholds, costs, metrics and failure criteria before backtesting.
5. Only then consider data-ingestion implementation; no strategy has been tested or approved yet.

## 8. Verdict
Twelve strategy hypotheses are specified for research only. None is backtested, ranked by empirical performance or approved for live trading.