# CP-0205: Conservative Gap-Window Quarantine Sensitivity Contract

**Checkpoint type:** source-only policy design  
**Status:** proposed contract; not applied; review required  
**Frozen rulebook:** CP-0040 SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`  
**Global gate:** `G0=BLOCKED_GLOBAL`; canonical source `NONE`; no candidate build/backtest authorized.

## 1. Purpose and non-goals

Define a reviewable policy for the 17 unresolved 4h slots without creating candles, selecting monthly vs daily as canonical, inventing fills, or hiding gap exposure. This document does not authorize a data build, performance run, source adjudication, or strategy promotion.

The CP-0203 gate remains deliberately blocking. CP-0205 defines what a future gap-policy evidence package must describe; it does not make the current recommendation eligible.

## 2. Frozen gap population and identity

The expected 4h slot beginning at UTC time `t` represents the interval `[t, t + 4 hours)`. A missing slot is a coverage fact, not a source row. Consecutive missing slots may be grouped for interval-coverage reporting, but their exact keys remain individually traceable.

| Population | Exact-key count | Required treatment |
|---|---:|---|
| `2017-09-06 16:00 UTC` | 1 | Daily archive has a zero-trade placeholder while monthly archive lacks the key. Keep linked to existing CP-0040 case `UNMATCHED-D-4h-1504713600000`; do not create a duplicate row case and do not accept the placeholder as a candle. |
| 2018-02-08 04:00 through 2018-02-09 04:00 UTC, every 4h slot | 7 | Missing from both inspected cached archives; gap-window policy item, no row to exclude or synthesize. |
| 2018-06-26 04:00 and 08:00 UTC | 2 | Two missing-key items; preserve separate exact keys. |
| 2018-07-04 04:00 UTC | 1 | Missing-key item. |
| 2018-11-14 04:00 UTC | 1 | Missing-key item. |
| 2019-03-12 04:00 UTC | 1 | Missing-key item. |
| 2019-05-15 04:00 and 08:00 UTC | 2 | Two missing-key items; preserve separate exact keys. |
| 2019-08-15 04:00 UTC | 1 | Missing-key item. |
| 2020-02-19 12:00 UTC | 1 | Missing-key item. |
| **Total** | **17** | **1 existing row-case overlap + 16 gap-window-only items.** |

CP-0200 recommendation SHA-256: `e59c95764d4db76a8a707d07526d44b2b7e3487c534687584bd9936a5742b3bf`.  
CP-0201 crosswalk SHA-256: `de8d829f405aa60f83e43744d4c281469fec6acb9bb99cfe6aa8823c8509be56`.

## 3. Source-code findings that make the policy material

In `scripts/AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py`:

- `add_features` creates new contiguous segments after missing intervals and computes indicators inside each segment.
- `simulate_strategy` only fills a pending signal when the next candle is contiguous; pending signals are cleared at a gap. No cross-gap fill is synthesized.
- However, quantity is carried through a gap and equity is marked at the next observed close (`current_equity = cash + qty * close`). The code has no observed price path for the missing intervals. Thus the endpoint mark does not establish the intragap path or a defensible maximum drawdown bound.
- Current feature windows differ: EMA uses a 26-bar slow span, RSI uses 14 bars, and Donchian uses 20-bar high / 10-bar low windows. After a segment break, each strategy must use only its own post-break contiguous warm-up; signals must not consume pre-gap indicator state.

The frozen CP-0040 rulebook requires unresolved signal/position/valuation inputs to be adjudicated or explicitly quarantined, with results based on the declared policy. Reporting gaps without handling the affected position/valuation state is insufficient for G0.

## 4. Policy options and recommendation

| Policy | Semantics | Strength | Limitation | Decision |
|---|---|---|---|---|
| A. Carry position through gap and mark at next observed close | Preserve current CP-0027 behavior. Report endpoint return and gap flag. | Keeps current simulated state. | Unknown intragap path can understate drawdown; unresolved valuation influence remains. | **Diagnostic only; cannot clear G0 or support risk-acceptance claims.** |
| B. Segment quarantine / censor gap-exposed episodes | Treat every missing slot as a segment boundary. Do not carry an unobserved position path into scored metrics. If a position is open at the boundary, mark its episode `CENSORED_GAP_EXPOSED`; do not invent an exit fill. Keep affected period `BLOCKED/UNSCORABLE` unless a separately approved accounting treatment exists. Start indicator warm-up anew in the next contiguous segment. | Does not fabricate a candle or a fill; explicitly identifies unscorable exposure. | Can make a full strategy-period ineligible; it is not a substitute for source repair/adjudication. | **Recommended primary conservative sensitivity contract.** |
| C. Hypothetical boundary closeout sensitivity | For a separately labelled counterfactual only, model liquidation at the last observed pre-gap close with declared fee/slippage, restart the next segment with cash, and report segment results independently. | Quantifies how much the gap-spanning position assumption may matter. | Closeout is a hypothetical action, not an observed execution; it must never be described as actual trading or as the sole truth. | **Optional secondary sensitivity only, after approval.** |

### Recommended rule

Adopt Policy B as the default quarantine interpretation for sensitivity reporting. Do not claim full-period strategy acceptance when an unresolved gap-exposed position makes the risk path unscorable. Policy C may be run only as a clearly separated counterfactual after a policy approval record exists. Policy A remains a comparator diagnostic, not an acceptance result.

This recommendation does **not** authorize a backtest now. The CP-0203 gate must remain closed until the policy is formally frozen and its evidence is applied and independently verified.

## 5. Required gap-impact classification

For each candidate interval and strategy, a future sensitivity package must classify:

1. `NO_GAP_IN_EVALUATION_WINDOW`: no unresolved slot intersects the evaluation window.
2. `GAP_NO_POSITION_CROSSED`: a gap exists but no position is held across it; signals and indicator warm-up still require checks.
3. `CENSORED_GAP_EXPOSED`: a position episode crosses a missing slot or unresolved placeholder boundary; no invented exit; episode excluded from scored closed-trade metrics.
4. `BLOCKED_GAP_VALUATION_UNSCORABLE`: unresolved position/equity path prevents defensible full-period drawdown/accounting acceptance.
5. `COUNTERFACTUAL_BOUNDARY_CLOSEOUT`: optional sensitivity only; hypothetical closeout assumptions and all costs disclosed.

Every record must include exact interval, expected open-time key, UTC window boundaries, previous and next observed candle keys/hashes, affected strategy, position/trade identifier if present, indicator warm-up requirement, decision, exclusion reason, and policy version. A gap-window item must never be turned into a fabricated row-level source case.

## 6. Minimum tests before any future policy execution

- The 17 exact keys reconcile 1:1 with CP-0200 and CP-0201; no missing or duplicate key.
- The 2017-09-06 placeholder links to its existing row case exactly once; no duplicate case.
- The other 16 items remain gap-window-only, never synthetic candle rows.
- Multiple adjacent missing slots form one coverage window for reporting while preserving each exact key.
- No pending order fills across a non-contiguous boundary.
- Indicator warm-up starts anew after a gap and uses only post-gap contiguous rows.
- A position held across a gap is marked censored/unscorable under Policy B; no exit price is fabricated.
- Counterfactual Policy C is labelled as hypothetical and reconciles fees, slippage, equity and segment-level P&L.
- Both the CP-0203 gap gate and CP-0040 row-level/non-row G0 gate run before any candidate/backtest outputs.
- No policy sensitivity can change `canonical_source=NONE`, close source cases, or enable live paths.

## 7. Explicit exclusions and unresolved scope

- This contract covers only the 17 CP-0200/0201 4h items. It does not resolve the 909 unmatched rows, 52 shared economic conflicts, 8 close-time-only cases, 450 February-2018 off-grid subset, 11 non-row blockers, or separate 5m/15m/30m/1h/1d/1mo coverage issues.
- The 450 February-2018 off-grid rows are part of the 909 unmatched population, not an additional 450 cases.
- Archive integrity proves byte identity against the inspected inventory, not canonical-source authority or complete intragap price paths.
- No historical return, maximum-drawdown bound, or profitability claim is established by this source-only contract.

## 8. Decision and checkpoint boundary

- CP-0205 output: this proposed policy contract only.
- Code changes: none in CP-0205.
- Candidate build/backtest: not run.
- Source adjudication/case closure: none.
- Canonical source: `NONE`.
- G0: `BLOCKED_GLOBAL`.
- Live signing/broadcast/orders: `BLOCKED`.
- Profitability: **NOT ESTABLISHED**.

Next action after review: turn the approved policy into an append-only, hash-pinned policy artifact and regression fixtures; do not implement a sensitivity runner until the contract is accepted and its accounting implications are independently checked.
