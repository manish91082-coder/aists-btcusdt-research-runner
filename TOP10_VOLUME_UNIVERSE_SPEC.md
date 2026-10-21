# Dynamic Top-10 Volume Universe Specification
Date: 2026-10-21
Status: POLICY FROZEN FOR IMPLEMENTATION; NO UNIVERSE RESULT CLAIMED

## Goal
Research only real Binance-listed instruments selected from verified market data. The Top 10 must be dynamic and point-in-time, not a hardcoded list. Historical ranking must use only data that would have been available at each historical decision time. No future volume leakage.

## Separate product universes
Maintain separate rankings for:
1. Binance Spot USDT-quoted symbols.
2. Binance USDⓈ-M Futures USDT-margined perpetual contracts.

Do not mix Spot turnover with Futures turnover. Report overlap between the two lists, but do not force a shared list unless later evidence shows that is required by the strategy design.

## Ranking rule
- Primary metric: daily USDT quote turnover from completed 1d klines (quote-asset volume / equivalent verified notional field).
- At each monthly rebalance timestamp, calculate each eligible symbol's median daily quote turnover across the preceding 30 completed UTC daily candles. Use only candles fully closed before the ranking timestamp.
- Sensitivity checks must compare 7-day, 30-day and 90-day completed-candle turnover windows when history permits. The 30-day median is the preregistered primary rule; sensitivity results must not be used to select the best-looking backtest after seeing outcomes.
- Rank descending by this metric; use symbol ascending as deterministic tie-breaker. Document a ranking buffer/hysteresis rule before historical simulation so small rank fluctuations do not silently churn membership.
- Select the first 10 eligible symbols per product. If fewer than 10 pass the eligibility and history rules, return fewer and explicitly report why. Never pad with guessed symbols.
- The latest 24h ticker volume may be used for current operational discovery only, not substituted into historical backtests as if it were known in the past.
- Save the exact input candle timestamps, per-symbol volume observations, metric, rank, selection timestamp, source URL/hash, exclusions and reason in an immutable point-in-time manifest.

## Eligibility and safety filters
- Only symbols whose quote asset and product semantics are verified as USDT-denominated and whose official archive metadata/product rules confirm the instrument type.
- Exclude stablecoin-to-stablecoin pairs, leveraged tokens, wrapped/tokenized equity or synthetic products, and symbols whose instrument semantics cannot be verified.
- For Futures, include only USDⓈ-M perpetual contracts for the initial universe. Exclude delivery contracts and COIN-M products from this universe.
- Require 30 complete daily observations before a symbol can be ranked. If a new listing lacks this history, mark it HISTORY_INSUFFICIENT and do not silently substitute data.
- Require an explicit product listing/contract status record at selection time. Do not assume present-day listings existed historically.
- Keep symbols with real but low volume only if they actually rank in the eligible Top 10; never inflate volume or invent liquidity.

## Capital, liquidity and execution realism
- Historical market data and turnover observations must be real official exchange data, not synthetic/simulated candles.
- Research equity remains 10,000 USDT as a PAPER/research assumption only unless the user explicitly authorizes a different capital amount and live-trading scope. “Real capital markets/data” does not itself authorize real-money orders.
- Apply verified symbol-specific tick size, lot size, minimum notional, taker fees, funding history, and conservative slippage assumptions where relevant. Do not infer historical fees/funding from current values without documenting the limitation.
- A high-turnover rank is not a guarantee of depth or low slippage. Add order-book/depth evidence before any execution-quality or live-tradability claim.
- Never place orders, connect trading credentials, deploy or enable live trading without explicit separate authorization.

## Data integrity and point-in-time safeguards
- Spot and Futures data are separate ledgers and separate ranking inputs.
- Use completed candles only; rank at a fixed, documented monthly UTC timestamp using the prior 30 complete days.
- Record missing candles, listing start, archive checksum, local SHA-256 and coverage. A missing or unverified input means the rank is BLOCKED, not estimated.
- Historical archive integrity does not prove completeness of a symbol's listing history. Maintain first/last observed timestamps and cross-check against official product/listing evidence.
- Delisted symbols and historical membership must be represented where official evidence permits; current survivors-only universe is not an acceptable substitute for a historical universe.

## Implementation tasks
- U-01: verify daily kline quote-volume semantics for Spot and USDⓈ-M Futures against official Binance documentation, including whether the Futures quote-volume field is directly comparable in USDT notional terms.
- U-02: build eligible-symbol/product inventory and verified USDT/product-type filters.
- U-03: derive daily quote turnover and calculate 30-day median ranks with point-in-time cutoff and deterministic ties.
- U-04: emit separate Spot/Futures Top-10 manifests plus overlap/exclusion reports.
- U-05: test with frozen fixtures for no lookahead, ties, missing candles, new listings, exclusions, and separate product ranking.
- U-06: validate a current snapshot for operational discovery, labelled CURRENT_ONLY; do not confuse it with a historical backtest universe.
- U-07: integrate the historical monthly membership manifest into backtesting only after archive coverage, listing history and cost gates pass.

## Acceptance
A universe build passes only when all selected symbols have traceable source data and hashes, complete prior 30-day observations, verified product semantics, no lookahead, deterministic ranks, and documented exclusions. An empty or incomplete evidence set is BLOCKED, not a fake Top 10.
