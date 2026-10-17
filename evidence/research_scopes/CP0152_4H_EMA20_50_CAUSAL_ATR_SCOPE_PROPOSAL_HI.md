# CP-0152 — 4h EMA20/EMA50 + Causal ATR Candidate Scope Proposal (Hindi)

Date: 2026-10-17
Status: **PROPOSAL ONLY — NOT APPROVED, NOT FROZEN FOR EXECUTION**
Branch: `cp-0120-ai-brain-foundation`
Purpose: Submit a genuinely new candidate-specific scope for explicit approval without bypassing G0 or the production builder guard.

## 1. Decision boundary

This file proposes a new research candidate. It does **not** authorize a market-data run, candidate build, backtest, paper deployment, strategy promotion, or gate transition. Do not execute until the scope is explicitly approved and every required input is independently verified. G0 remains `BLOCKED_GLOBAL`; the existing production builder must remain fail-closed.

## 2. Candidate identity and frozen rule proposal

- Proposed ID: `CP0152_4H_EMA20_50_ATR_CAUSAL_LONG`
- Instrument/market: Binance Spot BTCUSDT; long-only; 4-hour completed candles.
- Signal family: EMA20/EMA50 trend crossover plus causal ATR-percentile eligibility filter. This is distinct from the existing EMA12/EMA26 candidates and the failed `MTF_BREAKOUT_4H_D1` comparator.
- Indicator definitions: EMA20 and EMA50 use only closes at or before the decision candle. ATR14 uses only completed candles at or before the decision candle. ATR% = ATR14 / close.
- Volatility filter: rank the decision candle's ATR% against the **prior 252 completed 4h observations only** (exclude the current observation from the reference distribution). Eligibility band is inclusive 20th through 90th percentile. If 252 prior valid observations are unavailable, the percentile is unavailable and the action must abstain.
- Entry: after a completed 4h candle, when EMA20 crosses from at/below EMA50 to above EMA50 and the causal ATR% percentile is within the eligibility band, emit a research BUY candidate. Hypothetical fill may occur only at the next contiguous 4h candle open.
- Exit: after a completed 4h candle, when EMA20 crosses from at/above EMA50 to below EMA50, emit a research SELL candidate. Hypothetical fill may occur only at the next contiguous 4h candle open.
- Position policy: one long position at a time; no shorts; no pyramiding; no leverage; no automatic stop-loss; no automatic take-profit; no exchange order/signing/broadcast.
- Abstention: no action on missing/invalid candles, unresolved required source inputs, missing causal history, gap at intended next-open fill, conflicting/invalid state, or uncomputable assumptions. Never fill missing candles synthetically.
- Candidate actions are research instructions only, not Binance orders.

## 3. Data eligibility and quarantine

- Use only the project's official Binance downloadable archive lineage and exact verified input hashes; do not substitute live API data.
- G0 is globally blocked today. No data or candidate run is allowed under the current status.
- Before any future candidate-specific evaluation, exact-key row exclusions must be applied and verified end-to-end, including proof of actual row consumption/exclusion by the production data path. Existing static filter tests alone are not proof.
- All 11 non-row aggregation blockers remain open. This proposal does not adjudicate them and does not choose a canonical source.
- Any candidate-specific quarantine exception must be allowed by the frozen CP-0040 rulebook, use exact frozen keys and manifest hashes, and be independently reviewed. It must not be used to relabel global G0 as PASS.
- If the unresolved source conflicts can influence candidate signals, position state, fill prices, valuation, or metrics and cannot be demonstrably quarantined under the frozen rulebook, stop and report BLOCKED. No fallback source precedence may be invented.

## 4. Capital and execution-cost contract

- User planning capital is ₹10,000 INR converted to USDT. The historic `initial_capital_usdt: 10000` anchor is not an equivalent capital basis and must not be reused or rescaled.
- Before a performance run, record an evidence-backed INR/USDT conversion source, timestamp and conversion convention; if no admissible basis is available, user-capital P&L and returns are `NOT_COMPUTABLE`.
- Record fee assumptions and source. Evaluate the frozen rulebook stress grid: fee 10/15/20 bps per side paired with extra slippage 5/10/20 bps per side. Moderate stress (15 bps fee + 10 bps extra slippage per side) is a required G2 screen.
- Record BTCUSDT Spot lot-size/step-size and minimum-notional constraints from an admissible, dated source before quantity simulation. If not verifiable, quantities and user-capital results are `NOT_COMPUTABLE`.
- BNB fee-discount economics must remain an explicit sensitivity only until the account's applicable fee tier and discount eligibility are verified. Do not assume discount.
- Allocation is not approved by this proposal. A future approved run must freeze the allocation and cash-reserve policy before looking at evaluation results; no hidden leverage or compounding.

## 5. Evaluation and acceptance

Apply the original frozen CP-0040 rulebook without relaxing thresholds after seeing results:
- G1 correctness/reproducibility: deterministic tests, causal/no-lookahead checks, next-contiguous-open behavior, gap skips, fees/slippage, final liquidation, and independent accounting reconciliation; accounting mismatch tolerance <= 1e-8 USDT per matched comparison.
- G2: >=100 closed round trips across >=3 distinct time/regime blocks; net return >0 after modeled costs; net profit factor >=1.20; net expectancy >0; non-negative result at moderate cost stress; full-allocation max drawdown proxy <=25% in every declared evaluation block. DSR >=0.95 and PBO <=20% where statistically computable; otherwise NOT RUN/INSUFFICIENT EVIDENCE, never PASS.
- G3: show each predeclared block separately, all quarantine/source-policy sensitivities, concentration and drawdown. No averaging away failed blocks.
- G4 forward paper: >=180 calendar days AND >=30 closed round trips (whichever takes longer), >=99.5% expected closed-candle coverage, net P&L >0, PF >=1.20, max drawdown <=10% at frozen 25% virtual allocation; if 365 days pass with too few trades, INSUFFICIENT_EVIDENCE/LOW_FREQUENCY.
- Old or previously viewed windows are CONSUMED_DIAGNOSTIC, not pristine OOS. A new candidate does not make already-consumed periods pristine.
- No claim of profitability unless all applicable evidence and acceptance gates pass.

## 6. Explicitly not in scope

No live account access, API key, signature, public broadcast, Binance order placement, live/testnet trading, automatic SL/TP, synthetic market bars, source mutation, timestamp repair, gate override, candidate promotion, or self-approval.

## 7. Approval required before execution

Required approval is for this exact candidate definition, ATR percentile reference window and eligibility band, entry/exit rules, evaluation scope and pre-run assumptions. Any change requires a new version and review. Approval alone does not override G0 or authorize a run while required data/capital/cost inputs remain unverified.

Approval state: `PENDING_EXPLICIT_APPROVAL`
Execution state: `NOT_AUTHORIZED`
Backtest run: `NOT_RUN`
Candidate build: `NOT_RUN`
Empirical gate changes: `NONE`

## 8. Current verified blockers

- G0: `BLOCKED_GLOBAL`; canonical source not selected.
- 11 non-row aggregation blockers remain open.
- G2: `FAIL_CURRENT_23_CANDIDATES`; this proposal is not yet a tested candidate and is not promoted.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- G4: `INSUFFICIENT_EVIDENCE`.
- G6: `NOT_BUILT` for validated adaptive AI.
- G7: `LIVE_BLOCKED`.

This proposal is a scope/decision artifact only. It is not market evidence and clears no release gate.
