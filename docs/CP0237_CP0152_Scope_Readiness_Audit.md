# CP-0237 — CP-0152 Strategy Scope Implementation-Readiness Audit

Recorded: 2026-10-18  
Workstream: AI Brain / candidate scope preflight  
Status: **READ-ONLY REVIEW COMPLETE — EXECUTION NOT AUTHORIZED**  
Scope proposal: [CP-0152 EMA20/EMA50 + causal ATR proposal](evidence/research_scopes/CP0152_4H_EMA20_50_CAUSAL_ATR_SCOPE_PROPOSAL_HI.md)  
Proposal blob SHA: `164ec5d3cec592ad403e0eb9f1724a4cdff31850`

## 1. Decision

CP-0152 is **not implementation-ready for a valid candidate run**, even apart from the global G0 block. The current AI Brain code does not implement the exact proposed EMA20/EMA50 crossover candidate end-to-end, and required capital/cost/filter inputs are not frozen with admissible evidence.

Decision: `CP0237_SCOPE_PREFLIGHT_BLOCKED_NOT_EXECUTED`.

This review does not approve CP-0152, change any gate, build a candidate, run a backtest, or authorize live/paper execution.

## 2. Exact code findings

Read-only inspection of branch `cp-0120-ai-brain-foundation`:

- `aists_brain/strategy_action_engine.py`, blob SHA `ce1a3fc665a1fe5111bf9e537e3d2515baca2ba9`: `SUPPORTED_STRATEGIES` is only `TREND_FOLLOWING`, `BREAKOUT`, and `MEAN_REVERSION`. It does not implement the proposed EMA20/EMA50 cross state or the ATR-percent eligibility rule.
- `aists_brain/strategy_candidates.py`, blob SHA `dc3330c44759d1d21e54211161df756e0fa93258`: candidate selection is deterministic heuristic eligibility for those three strategy families, not the CP-0152 candidate and not trained/adaptively validated AI.
- `aists_brain/causal_volatility.py`, blob SHA `f31609ee1f2d36c6e28079199795ae207a85551d`: causal percentile utility excludes the current observation, but defaults are `min_observations=30`, `lookback=100`. CP-0152 requires the caller to explicitly enforce 252 prior completed observations. The helper alone cannot prove upstream ATR observations came from completed, gap-validated candles.
- `aists_brain/research_harness.py`, blob SHA `2d168c8c6adb272d073cf90980e242e683202611`: the harness explicitly treats provenance PASS as an external claim and symbol filters as caller-supplied. It does not independently authenticate source authority or exchange-filter provenance.
- `scripts/AISTS_CP0026_Research_Candidate_Builder.py`, blob SHA `06e9f292603b1f4755bea4c28ef027a01e2226d1`: the builder fails closed while non-row blockers remain; the current G0 status therefore forbids a candidate build.

## 3. Preconditions still missing

1. G0 must be legitimately cleared through admissible provenance evidence or an authorized independent review and separately scoped application record. Static CI or checksum integrity is not a substitute.
2. The exact CP-0152 scope needs explicit approval before implementation/execution: completed 4h candles, EMA20/EMA50 crossover, ATR14/close ranked only against the prior 252 completed observations, inclusive 20–90 percentile band, next-contiguous-open hypothetical fills, long-only, one position, no leverage, no automatic SL/TP.
3. Capital basis must use the user's ₹10,000 INR planning amount. The legacy 10,000 USDT anchor is not equivalent. Record an admissible INR/USDT source, timestamp and convention; otherwise user-capital outputs stay `NOT_COMPUTABLE`.
4. Freeze the fee/slippage grid required by CP-0152 (10/15/20 bps fee per side paired with 5/10/20 bps extra slippage per side); BNB discount remains sensitivity-only unless eligibility is verified.
5. Record dated BTCUSDT Spot lot-size, step-size and minimum-notional evidence. If not verifiable, quantity and capital-based results stay `NOT_COMPUTABLE`.
6. Freeze allocation and cash-reserve policy before evaluation; this proposal has not approved either.
7. Prove exact-key exclusion and gap/quarantine lineage are consumed by the actual production path. Existing static unit tests do not by themselves prove this integration.

## 4. Permitted next action

After explicit CP-0152 approval and only after G0 and required inputs are independently satisfied, implement a dedicated candidate-specific causal signal path and tests, including the 252-observation rule, next-contiguous-open behavior, abstention on gaps, and no exchange-order side effects. Then independently verify the exact-head CI before considering any bounded historical evaluation.

Until those conditions hold: no candidate build, no market backtest, no strategy promotion, no paper deployment, and no live exchange action.

## 5. Gate status at this review

- G0: `BLOCKED_GLOBAL`
- G2: `FAIL_CURRENT_23_CANDIDATES`; CP-0152 is a proposal, not a tested candidate
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- G4: `INSUFFICIENT_EVIDENCE`
- G6: `NOT_BUILT` for validated adaptive AI
- G7: `LIVE_BLOCKED`
- Canonical source: `NONE`
- Profitability: `NOT ESTABLISHED`

No market data was downloaded, no candidate was built, no backtest was run, no source case was closed, and no live action was performed.
