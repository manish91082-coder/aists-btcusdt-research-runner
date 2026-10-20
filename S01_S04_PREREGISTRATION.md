# S-01 to S-04 Experiment Preregistration v1.0

Status: PREREGISTERED FOR FUTURE EXECUTION; NOT RUN; NO PERFORMANCE CLAIM.

The representative Binance Spot/Futures archive audit remains BLOCKED. This preregistration does not pass the data gate and does not authorise backtesting. No backtest may begin until the exact input archives, publisher checksums, data-quality reports, API comparisons and cost inputs are verified.

## Shared protocol
- Use completed bars only; signals at bar close may enter no earlier than the next bar open.
- Never use future information, unfinished higher-timeframe candles, or today's universe membership in historical tests.
- If OHLC bars touch both stop and target and ordering is unknown, use the adverse outcome.
- Keep Spot and USDⓈ-M Futures separate. Spot is long/flat only; short exposure is Futures-only. Apply verified Futures funding at actual event times.
- Before execution, record official product-specific commission evidence. Do not assume BNB discounts. Use taker fees as the primary conservative scenario. Report 0/5/10 basis-point slippage per fill as stress scenarios, not observed values. If funding data is missing, Futures net results are BLOCKED, not zero.
- Freeze exact chronological boundaries before the first run: earliest 60% train, next 20% validation, final 20% untouched holdout. Use rolling-origin evaluation within the first 80%, no random shuffle, and no holdout-driven tuning.
- Compare against no-trade and exposure-matched baselines. Report net/gross return, costs, trade count, exposure, drawdown, turnover, risk metrics, uncertainty and every parameter cell tried. No single metric promotes a strategy.

## S-01 Trend following
Primary 5m: EMA(20)/EMA(50), Wilder ATR(14). Long if close > EMA20 > EMA50; Futures short if close < EMA20 < EMA50. Enter next bar open. Stop 2 ATR, target 3R, exit on stop/target/opposite aligned signal/96 bars. Sensitivity: EMA pairs (10,30)/(20,50)/(50,100), stop 1.5/2 ATR, target 2R/3R. No higher-timeframe claim until its data is audited.

## S-02 Regime-filtered mean reversion
Primary 5m: z-score of close versus prior 20-bar mean and standard deviation; range gate Wilder ADX(14) <= 20. Long at z <= -2; Futures short at z >= +2. Enter next bar open; exit at |z| <= 0.25, adverse 2.5 ATR stop, or 48 bars. Compare with identical ungated rules. Sensitivity: entry z 1.5/2/2.5, exit z 0/0.25, ADX gate 15/20.

## S-03 Breakout after compression
Primary 5m: normalized ATR(14)/close at or below the 20th percentile of the prior 288 completed values; breakout beyond the prior 20-bar high/low, excluding signal bar. Enter next bar open; stop 1.5 ATR, target 3R, time stop 48 bars. Sensitivity: percentile 10/20, breakout lookback 20/40, stop 1/1.5 ATR, target 2R/3R.

## S-04 Momentum continuation
Primary 5m: 12-bar log return normalized by standard deviation of prior 12 one-bar log returns times sqrt(12). Require signal-bar quote volume at least the median of the prior 20 bars. Long at normalized momentum >= +0.5; Futures short <= -0.5. Enter next bar open; stop 2 ATR; exit on opposite signal, stop or 24 bars. No target in primary. Sensitivity: threshold 0.25/0.5/1.0, lookback 6/12/24, volume gate median/75th percentile.

All variants count toward multiple-testing awareness. Indicators and warm-up must be unit-tested. If data history, trade count, fee evidence or funding coverage is inadequate, report INSUFFICIENT_DATA/BLOCKED instead of relaxing criteria. These definitions are research hypotheses only, not evidence of profitability or live approval.

## State
Protocols are frozen for the BTCUSDT 5m pilot. Phase 2 remains BLOCKED; no archive audit has been independently verified. No backtest, model training, paper run, live order or deployment has occurred. Next dependency: run the existing Phase 2 workflow and independently review both Spot and Futures reports and artifacts.