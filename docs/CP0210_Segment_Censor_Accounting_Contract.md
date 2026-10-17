# CP-0210: Segment/censor accounting contract for gap sensitivity

## Status and scope

**Status: CONTRACT_AND_SYNTHETIC_ORACLE_ONLY; NOT IMPLEMENTED IN PRODUCTION; NOT G0 CLEARANCE.**

This document defines the accounting semantics required before a Policy B sensitivity scorer may be implemented. It is not approval to execute the policy against market data. It does not replace the CP-0040 rulebook, the frozen CP-0206 policy, CP-0203/CP-0026 fail-closed gates, source adjudication, or independent review.

Scope is the 17 exact unresolved 4h slots already pinned in CP-0206: one overlap with existing row case `UNMATCHED-D-4h-1504713600000` plus 16 gap-window-only items. A gap window is coverage [expected open, expected open + 4h), never a candle row.

## 1. Required classifications

Every strategy/evaluation-window record must have exactly one primary classification:

- `NO_GAP_IN_EVALUATION_WINDOW`: no unresolved gap intersects the window.
- `GAP_NO_POSITION_CROSSED`: a gap intersects the window, but no position episode crosses its boundary. Signals and post-gap indicator warm-up still require validation.
- `CENSORED_GAP_EXPOSED`: a position is open immediately before a non-contiguous boundary. That complete trade episode is censored from scored closed-trade statistics; do not invent a boundary exit.
- `BLOCKED_GAP_VALUATION_UNSCORABLE`: a full-window account-equity, return, or drawdown statistic depends on unobserved intragap valuation or censored inventory. Full-window acceptance remains blocked.
- `COUNTERFACTUAL_BOUNDARY_CLOSEOUT`: a separately approved hypothetical comparator only. It must be labelled counterfactual, never observed execution or the primary acceptance result.

The record must retain interval, exact missing key, coverage start/end UTC, previous/next observed keys and hashes when available, strategy, episode ID, segment ID, position-at-boundary, classification, exclusion reason, policy ID/version, and whether a metric is scored or diagnostic.

## 2. Position and fill semantics

1. No missing candle, exit price, or fill may be synthesized.
2. Pending signals are discarded at a non-contiguous boundary. A boundary row cannot originate a signal for a fill on the next row.
3. If inventory is open immediately before the gap, label that position episode `CENSORED_GAP_EXPOSED`. Do not create a sell fill at the last pre-gap close, first post-gap open, or any interpolated price.
4. The entire censored episode's realized trade P&L, win/loss outcome, holding period, and trade-level risk measures are excluded from scored trade metrics. If the eventual production-simulator sale is visible after the gap, it remains diagnostic for this sensitivity and must not re-enter scored trade totals.
5. Post-gap sensitivity segments are replayed independently from flat cash with no inherited inventory or pending signal, after strategy-specific indicator warm-up using only post-gap contiguous observations. This is a segmented sensitivity, not a claim that a real account reset occurred.
6. A modeled window-end liquidation is permitted only inside a fully observed contiguous evaluation segment under the declared execution assumptions. It is never a substitute for an unobserved gap-boundary exit.

## 3. Accounting invariants

Use Decimal-based independent arithmetic for reference fixtures. Tolerance is `<= 1e-8 USDT` for each matched accounting comparison.

- Buy: fill = reference × (1 + slippage rate); quantity = available cash / (fill × (1 + fee rate)); fee = quantity × fill × fee rate; post-fill cash must not be negative beyond tolerance.
- Sell: net proceeds = quantity × fill − fee. Net closed-trade P&L = net proceeds − entry notional − entry fee.
- Fees and estimated slippage are charged exactly once per modeled fill. Censored episodes have no fabricated exit fill, exit fee, exit slippage, or realized P&L.
- Scored segment P&L is the sum of net P&L for eligible fully closed episodes wholly contained in that contiguous segment. It must reconcile to the segment's independently computed cash delta when the segment begins and ends flat.
- Diagnostic marks may show cash + quantity × an actually observed close. They must be labelled diagnostic when they value inventory associated with a censored episode.
- Do not sum segment equity curves across gaps or report a full-window maximum drawdown/return as scored when the path depends on censored inventory. Report full-window status as `BLOCKED_GAP_VALUATION_UNSCORABLE`.
- Scored metrics must expose counts of eligible episodes, censored episodes, scored segments, unscorable segments, and excluded diagnostic P&L separately. Never silently treat excluded P&L as zero or as a realized loss/profit.

## 4. Segment boundary algorithm

For each contiguous segment:

1. Identify boundaries from timestamp continuity and the frozen gap evidence; preserve all raw rows unchanged.
2. Discard pending signals at the boundary and restart indicators with strategy-specific warm-up.
3. If a position crosses the boundary, censor its complete episode and mark the cross-gap account path unscorable.
4. Finalize only eligible closed episodes within the segment. An observed mark of an open position is not a realized exit.
5. Start the next sensitivity segment from flat initial segment capital, with no inherited position, cash balance, pending signal, or indicator state. Record this as an isolated-segment sensitivity.
6. Aggregate only eligible segment-level statistics with explicit denominators. Do not aggregate equity paths across unresolved boundaries. If any requested full-window risk statistic depends on a censored path, preserve the blocked/unscorable status.

## 5. Synthetic oracle acceptance cases

The test suite must include:

- A flat segment with eligible closed trades: Decimal cash delta equals the sum of eligible net trade P&L within tolerance.
- An open position at a gap: no fabricated sell event; its entire episode is excluded from scored trade metrics and counted as censored.
- A later observed simulator sale for that same episode: retained as diagnostic only and not added to scored P&L.
- A post-gap segment: starts flat, has no pending pre-gap signal, and requires indicator warm-up from post-gap observations only.
- Adjacent missing slots: report one coverage window while preserving every exact missing key.
- The 17-key inventory: exactly 17 unique keys, one existing-row overlap, 16 gap-only items; no synthetic row and no duplicate row case.
- Full-window risk request with censored exposure: result is `BLOCKED_GAP_VALUATION_UNSCORABLE`, not a numeric accepted return/drawdown.
- Gate guards: CP-0203 and CP-0026/CP-0040 remain before any candidate/backtest output path. No fixture can clear G0, close a source case, select a canonical source, promote a strategy, or enable live actions.

## 6. Non-effects and implementation boundary

This checkpoint does not modify CP-0027 production scoring, apply Policy B to candidates, run market data, build candidates, perform a market backtest, adjudicate sources, or authorize counterfactual Policy C. The existing production simulator still carries inventory across a gap and may report ordinary metrics; those results remain diagnostic-only and blocked from acceptance under the unresolved policy.

The CP-0206 status remains `FROZEN_FOR_SENSITIVITY_ONLY_NOT_G0_CLEARANCE`. Any production application requires a separately reviewed, append-only, hash-pinned application artifact and verified gates.

## Decision and next step

CP-0210 delivers the contract and a deterministic Decimal oracle only. After CI terminal verification, CP-0211 should review this contract against CP-0040/CP-0206 and then decide whether a separate approved Policy B sensitivity-only scorer may be implemented. Do not start that scorer or any market-data run before that decision.

Current state: canonical source `NONE`; G0 `BLOCKED_GLOBAL`; source cases closed `0`; candidate build/backtest blocked; strategy promotion false; live signing/broadcast/orders `BLOCKED`; profitability **NOT ESTABLISHED**.
