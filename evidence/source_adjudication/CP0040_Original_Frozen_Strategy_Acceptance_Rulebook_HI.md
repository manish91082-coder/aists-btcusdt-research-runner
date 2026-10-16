# AISTS CP-0040 — Frozen Strategy Acceptance Rulebook (HI)

Generated: 2026-10-13T19:07:49.107045Z
Status: **policy/decision-gate freeze complete; data and strategy acceptance remain open; LIVE BLOCKED**.

## 1. उद्देश्य और उपयोग

इस rulebook का उद्देश्य AISTS BTCUSDT Spot में यह रोकना है कि सिर्फ अच्छे backtest, एक-दो candle, या synthetic test पास होने पर strategy को आगे बढ़ा दिया जाए। ये thresholds **AISTS के project-defined conservative defaults** हैं, कोई universal industry/regulatory standard या लाभ की गारंटी नहीं। इन्हें किसी नतीजे को देखने के बाद ढीला नहीं किया जाएगा; बदलाव करने पर नया version, reason, prior-vs-new comparison और स्वतंत्र approval चाहिए।

Backtest selection में multiple trials/selection bias से performance बढ़ा हुआ दिख सकता है। इसलिए जहाँ पर्याप्त return observations हों वहाँ Probability of Backtest Overfitting (PBO/CSCV) और Deflated Sharpe Ratio (DSR) जैसे selection-adjusted diagnostics रखे जाएंगे; प्रकाशित शोध भी backtest-selection bias को अलग से जाँचने का कारण देता है ([Bailey et al., Probability of Backtest Overfitting](https://doi.org/10.21314/JCF.2016.322); [Bailey & López de Prado, Deflated Sharpe Ratio](https://doi.org/10.2139/ssrn.2460551)). इन diagnostics की कमी को PASS नहीं माना जाएगा।

## 2. क्रमबद्ध gates

### G0 — Source/data eligibility
- हर active input का exact SHA-256, row count, schema, UTC boundary, OHLCV and provenance manifest होना चाहिए; सभी hashes exact match हों।
- Raw source archives immutable रहेंगे। कोई rounding, timestamp shifting, gap filling या source replacement स्वतः नहीं होगा।
- Duplicate/open-time, out-of-grid, impossible OHLC, invalid numeric या close-time-boundary errors: **0 unexplained rows**। वास्तविक missing intervals को log किया जाएगा, synthetic bars नहीं बनाए जाएंगे।
- Monthly/daily exact-open disagreements, daily-only/monthly-only rows, February-2018 shifted rows और cross-timeframe aggregation conflicts का disposition होना चाहिए। जबतक किसी item का source adjudication न हो, उस input को `UNRESOLVED` चिह्नित करें और signal-influence वाले research run से अलग quarantine sensitivity चलाएँ।
- **PASS**: 0 unresolved items जो चुने गए candidate के actual signal/position/valuation inputs को प्रभावित कर सकते हों, या प्रत्येक unresolved item स्पष्ट रूप से quarantined हो और final metrics उस quarantine policy पर आधारित हों।

### G1 — Engine correctness/reproducibility
- 100% blocking deterministic/synthetic tests PASS हों; `NOT RUN` को PASS नहीं माना जाएगा।
- Lookahead, future higher-timeframe leakage, stale regime, next-contiguous-open fills, gap-crossing pending orders, costs, final liquidation और P&L reconciliation के स्वतंत्र tests होने चाहिए। P&L mismatch tolerance: **≤ 1e-8 USDT per matched accounting comparison**, और कोई tautological self-comparison assertion नहीं।
- समान inputs, rule version और costs पर reproducible result rows; input hash + code hash + config hash दर्ज हों।
- No live order, signature, private account call or public order broadcast in research/offline mode.

### G2 — Historical research screen (candidate promotion only, not live approval)
- Fixed strategy/rule-set freeze; tested parameters और सभी prior strategy trials log हों।
- Minimum sample for a statistical screen: **≥ 100 closed round trips across evaluation blocks** and at least **3 distinct time/regime blocks**. अगर sample छोटा है, status `INSUFFICIENT_EVIDENCE`, न कि PASS।
- Base case: net return after all modeled fees/slippage > 0; net profit factor ≥ **1.20**; per-trade net expectancy > 0.
- Cost stress scenarios per side: fee **10/15/20 bps** paired with additional slippage **5/10/20 bps**. Candidate must remain non-negative after costs in the pre-registered moderate stress (15 bps fee + 10 bps extra slippage). Severe stress (20 + 20 bps) may downgrade the candidate, but any loss must be explicitly risk-budgeted and never hidden.
- Full-allocation historical maximum drawdown proxy ≤ **25%** in every declared evaluation block; no window-end accounting mismatch. If the strategy breaches it, strategy fails this screen even if return is positive.
- Risk-adjusted/selection-adjusted checks: where sample supports it, DSR ≥ **0.95** and estimated PBO ≤ **20%**. Report trial count, returns distribution, confidence/uncertainty and whether assumptions for these diagnostics are met. If not computable, mark `NOT RUN/INSUFFICIENT_EVIDENCE`, not PASS.
- All old periods that have been used to choose/design the strategy remain `CONSUMED_DIAGNOSTIC`; no relabelling as pristine OOS.

### G3 — Candidate stability / stress
- Report each predeclared timeframe separately; no averaging-away of a failed interval.
- All source policy and quarantine sensitivities must be shown. Material metric differences caused by a source policy mean the data gate remains open for that candidate unless the source is adjudicated or the conservative quarantine policy is frozen.
- Year/block return concentration: no single year/block should contribute > **50% of total positive net P&L** unless explicitly justified and passed separate dependence/regime review.
- No hidden leverage, shorts, compound/reinvest assumption or synthetic data. Capital allocation, cash reserve and mark-to-market methodology must be explicit.

### G4 — Prospective forward-paper acceptance
- Frozen rules/config/data schema. Every closed candle observation, signal, decision, intended fill, quote, spread, latency, modeled fee/slippage, rejected/skipped signal, gap and resulting virtual position/equity must be append-only and timestamped.
- Minimum observation duration: **180 calendar days AND 30 closed round trips**, whichever takes longer. If fewer than 30 round trips after 180 days, continue; if 365 days pass with too few trades, classify as `INSUFFICIENT_EVIDENCE/LOW_FREQUENCY` and do not infer success.
- At least **99.5% expected closed-candle observation coverage** for the selected intervals, with every missing observation accounted for; unknown outage, duplicate runner, state rollback or P&L mismatch resets acceptance review.
- Forward-paper net P&L after the full modeled fee/slippage/spread assumptions > 0; PF ≥ **1.20**; max drawdown ≤ **10% at the frozen 25% virtual allocation**. These are project gates, not guarantees.
- No tuning, cost/parameter change, or rule selection based on the same forward period. If rules change, start a new evaluation segment/version.

### G5 — Exchange/testnet readiness (separate gate)
- Not reached yet. Before any live path: actual account fee tier and discount verified; order lifecycle tests for accepted/rejected/partial/timeout/cancel/duplicate/reconnect/insufficient balance/stale quote; virtual-vs-accounting reconciliation; kill-switch and rollback demonstrated; least-privilege API permissions, no withdrawal permission, key isolation and redaction review.
- Testnet results must not be described as real-world slippage/profit evidence. All signing/order paths remain disabled until a separate audit and explicit user authorization.

### G6 — Adaptive AI layer readiness
- Current strategy candidates are fixed deterministic rules, **not a validated adaptive AI strategy**.
- Future adaptive layer must use causal, timestamped features; train only on information available at decision time; record model/rule versions, feature lineage, calibration and abstention/no-trade decision.
- Must beat the frozen fixed-rule comparator after costs on a **new future, unconsumed evaluation period**, while satisfying every data, drawdown and forward-paper gate above. Any parameter/model search must record all trials and evaluate selection bias (PBO/DSR where applicable).

## 3. Current candidate decision under these gates

- `MTF_BREAKOUT_4H_D1`: **FAIL / NOT PROMOTED under current screen**. CP-0031 consumed diagnostic shows negative return (~−1.38% at the reported 25%-allocation base-cost scenario); prior full-allocation TRAIN drawdown proxy was severe (~−63.19% in prior CP-0028 summary; CP-0031 25%-allocation screen also had a high drawdown proxy ~−22.19%). There is no fresh OOS. It may remain a frozen research comparator, not a selected strategy.
- `MTF_BREAKOUT_1D_1MO`: **FAIL / HOLD**. TRAIN negative (~−14.45%), consumed diagnostic negative (~−3.89%), low trade sample; not promoted.
- CP-0030 monitoring had **0 closed paper trades**; it is operational smoke-test evidence only, not a forward-paper acceptance sample.
- No candidate currently passes the frozen acceptance gates. Live trading stays `BLOCKED`.

## 4. Review/change control
- Gate statuses: `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`, `INSUFFICIENT EVIDENCE` only.
- Every future checkpoint must include exact input/code/config hashes, test register, results comparison, known caveats, and clear source-policy identity.
- No silent edits, no source inference by convenience, no claimed testing that did not run. Original archives never overwritten.

## 5. Research references
- Bailey, Borwein, López de Prado & Zhu, “The Probability of Backtest Overfitting,” *Journal of Computational Finance*, 2017: https://doi.org/10.21314/JCF.2016.322
- Bailey & López de Prado, “The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality,” *Journal of Portfolio Management*, 2014: https://doi.org/10.2139/ssrn.2460551

**Frozen gate:** `DIAGNOSTIC_ONLY; SOURCE_RECONCILIATION_OPEN; STRATEGY_ACCEPTANCE_FAIL; LIVE_BLOCKED`.
