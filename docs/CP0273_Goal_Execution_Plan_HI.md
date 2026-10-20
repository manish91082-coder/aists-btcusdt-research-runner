# CP-0273 onwards: Goal Execution Plan (Hindi)

**Canonical repository:** `manish91082-coder/aists-btcusdt-research-runner`  
**Active AI implementation branch:** `cp-0120-ai-brain-foundation`  
**Plan status:** Ordered execution plan, not gate approval  
**Frozen decision:** G0 remains `BLOCKED_GLOBAL`; CP-0040 acceptance rules are unchanged.

## Mission

Build a reproducible BTCUSDT Spot research and paper-decision system that can establish, rather than assume, risk-adjusted net profitability on the user's ₹10,000 INR capital basis. Binance public downloadable archives remain the primary historical source. No automatic stop-loss/take-profit, live signing, public broadcast or exchange orders.

## Ordered plan and exit criteria

| Phase | Work | Exit evidence | Gate boundary |
|---|---|---|---|
| 0. Current-state integrity | Verify exact branch/PR/CI state and frozen rules | Live GitHub refs and terminal run results | Never infer PASS from queued runs |
| 1. Research-engine safety | Harden decision/simulator boundary; test abstention, causality, costs, accounting and no-order invariants | Exact-head unit CI and regression tests | Synthetic fixtures are software tests only |
| 2. AI decision integration | Verify causal feature → regime → selector → action → decision artifact lineage and deterministic replay | Hash-linked artifacts, no-lookahead tests, reproducible replay | No market performance claim |
| 3. Capital/cost contract | Keep ₹10,000 INR as the source capital; specify FX, allocation, fee tier, slippage, BNB fee economics and minimum-order filters as explicit evidence-backed inputs | Versioned capital assumptions and scenario report with unknowns preserved | No invented FX/fee/filter values; no automatic SL/TP |
| 4. Source authority dependency | Keep G0 frozen; only record genuinely new official historical-version evidence or an actually authorized independent adjudication | Clause-specific evidence and authorized decision record | No repeat scans without changed evidence; no inferred reviewer approval |
| 5. Candidate-specific authorization | Re-evaluate CP-0152 only after its exact approval and all applicable prerequisites; inspect production input exclusions and dependency crosswalk | Explicit approval plus exact-hash candidate-input verification | G0 and frozen gates still control |
| 6. Historical validation | Only after the applicable gates legitimately allow it, run chronological train/validation/OOS evaluation with leakage controls, costs, benchmarks, regime slices, drawdown and accounting reconciliation | Reproducible run, hashes, independent verifier, predeclared acceptance thresholds | No tuning on consumed OOS; no synthetic market candles |
| 7. Adaptive learning | After baseline evidence exists, implement versioned training/search ledger, calibration, drift checks and benchmark comparisons | Reproducible training and independent out-of-sample evidence | No self-promotion |
| 8. Paper evaluation | Only after explicit strategy approval and permitted data gate, run frozen decisions into append-only paper ledger | Multi-period paper evidence and reconciled accounting | Research-only; no exchange orders |
| 9. Final acceptance review | Reconcile all gates, capital basis, costs and independent evidence | Signed/authorized acceptance decision with complete lineage | Profitability remains unestablished until proven |

## Stop conditions

- G0 remains `BLOCKED_GLOBAL`; canonical historical source remains `NONE`.
- G2: 23 current historical candidates remain FAIL/not promoted.
- G3 remains blocked; G4 remains insufficient; G6 adaptive AI remains not built/validated; G7 live actions remain blocked.
- No production candidate build, market backtest or paper trading while G0 is blocked or before required explicit strategy approval.
- No changes to CP-0040, no synthetic/filled candles, no timestamp shifting, no fake PASS manifest, no live signing/broadcast/orders, and no automatic SL/TP.
- A green CI result validates only the code/tests it actually ran. It does not validate data provenance or profitability.

## CP-0273 first action

A source-code review found that the offline simulator accepted optional decision metadata flags such as `is_order_instruction=true`, `live_signing_enabled=true`, or automatic SL/TP flags without rejecting them. Although the simulator itself does not send orders, accepting contradictory instruction metadata weakens the contract. CP-0273 rejects any supplied true safety-forbidden flag and rejects non-boolean values. Targeted tests are required before the checkpoint is verified.
