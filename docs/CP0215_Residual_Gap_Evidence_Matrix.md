# CP-0215: Residual Gap Evidence Matrix

## Purpose and decision boundary

This checkpoint distinguishes (a) what CP-0213/CP-0214 synthetic fixtures demonstrate, (b) what remains unverified in the production path, and (c) what requires actual independent approval/application. It is a documentation and gate-planning artifact only.

**Disposition:** `RESIDUAL_GAPS_CLASSIFIED_POLICY_B_APPLICATION_NOT_AUTHORIZED`  
**Canonical source:** `NONE`  
**G0:** `BLOCKED_GLOBAL`  
**Candidate build / market backtest:** `BLOCKED`  
**Independent approval:** `NOT PRESENT`  
**Policy B application record:** `NOT PRESENT`  
**Profitability:** `NOT ESTABLISHED`

No source case is closed by this matrix. No reviewer approval is inferred from GitHub Actions.

## Evidence classification

| Requirement | CP-0213/0214 synthetic evidence | Production-path status | Independent authorization / residual action |
|---|---|---|---|
| 1. Gap-boundary censor event creates no fabricated candle, fill, or exit price | Synthetic fixture asserts zero synthetic candles/fills and null exit price. | **NOT VERIFIED.** The fixture constructs a censor object itself; it does not invoke a production censor transition. Existing simulator behavior carries gap-exposed positions across gaps for diagnostic marking. | Production censor behavior must not be implemented/applied for scored work without actual approval and a scoped application record. |
| 2. Later ordinary sale is diagnostic-only, excluded from scored P&L | Synthetic fixture calculates diagnostic P&L separately from a hard-coded scored value and reconciles fixture arithmetic. | **NOT VERIFIED.** No production scored/diagnostic ledger path is exercised by this fixture. | After authorization, independently verify production event routing and aggregation; do not treat fixture output as production evidence. |
| 3. Post-gap replay resets to flat cash and clears position, pending signal, indicators, and warm-up | Fixture checks a newly constructed empty state and zero warm-up observations. | **NOT VERIFIED.** It does not drive the production simulator through a gap and into a new segment. | A production-path test requires explicit approved scope; strategy-specific warm-up semantics must be specified and tested. |
| 4. Adjacent missing-key grouping preserves exact keys | Synthetic helper groups supplied integer keys and rejects duplicates. | **PARTIAL / NOT END-TO-END.** The helper is not evidence that production eligibility consumes the frozen CP-0206 population correctly in all cases. | Preserve the frozen 17-key identity and verify actual consumer integration only within an authorized scope. |
| 5. Full-window metrics become unscorable when intragap valuation is unknown | Fixture returns a blocked status and null return/equity/drawdown fields. | **NOT VERIFIED.** No production metric publisher is invoked by this fixture. | Verify production output suppression under authorized tests before any sensitivity performance run. |
| 6. Exact CP-0206 population is 17 keys, with one existing-row overlap and 16 gap-window-only keys | Fixture reads the frozen policy and checks count/classification totals; helper rejects missing/duplicate/extra test keys. | **STATIC/FIXTURE EVIDENCE ONLY.** This does not independently adjudicate source eligibility or close any source case. | Keep all 17 unresolved. No canonical source selection or case closure is authorized by these tests. |
| 7. Independent event-level cash, quantity, fees, mark equity, and P&L reconciliation | A separate Decimal fixture checks BUY/MARK/SELL arithmetic and ending cash identity at the specified tolerance. | **LIMITED.** It does not cover every production event transition, gap censor path, slippage path, or window-end path. The fixture's own expected ledger is not a production run. | Expand only under the approved scope; preserve tolerance `<= 1e-8 USDT` and independently authored expectations. |
| 8. Diagnostic and scored P&L remain isolated | Synthetic fixture has distinct diagnostic and scored fields. | **NOT VERIFIED.** Production reporting/aggregation has not been shown to exclude diagnostic values in all downstream metrics. | Require production-level separation tests before any approved sensitivity runner can be considered. |
| 9. G0 fail-closed before candidate/backtest work | CP-0213/0214 source guards inspect gate placement and frozen blocked status. Existing gate wiring is intended to block unresolved evidence. | **STATIC REGRESSION EVIDENCE, NOT FULL EXECUTION PROOF.** These checks do not constitute an authorized market run and do not establish all failure paths. | G0 remains controlling. Do not execute candidate build/backtest to test this gate while unresolved. |
| 10. Repeatability, evidence hashes/receipts, and test-result provenance | Exact Git commit and CI run provide version/run traceability for the synthetic tests. | **INCOMPLETE.** A comprehensive receipt set pinning fixture definitions, expected outputs, policy/contract/test hashes, and results is not established by the synthetic assertions alone. | Add/verify deterministic evidence receipts in an appropriately scoped checkpoint; do not claim independent approval. |
| 11. Independent reviewer approval and separate Policy B application record | No synthetic test can establish human authorization. CP-0212 deliberately leaves sign-off fields blank. | **ABSENT.** Reviewer identity/authority, reviewed SHA, decision, conditions, and application record are not present. | **HARD STOP.** An actually authorized reviewer must provide a traceable decision, followed by a separately scoped application record and verification. CI success is not a substitute. |

## Production behavior known from source review

- `scripts/AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py` currently carries gap-exposed spot position across a gap and marks at the next observed close. This is diagnostic behavior, not Policy B scoring.
- CP-0209's boundary-row guard prevents a non-contiguous boundary row from originating a pending signal; it does not implement gap censoring.
- CP-0203/0204 gate wiring is intended to block candidate/backtest work while the frozen gap policy remains unresolved.
- CP-0213/0214 tests exercise in-memory synthetic fixtures and static guards. They do not prove a production censor transition or authorize a scoring-policy change.

## Decision

`CP0215_MATRIX_RECORDED_PRODUCTION_EVIDENCE_GAPS_AND_AUTHORIZATION_BLOCK`

1. Keep CP-0206 frozen for sensitivity-only reference; do not apply it to production scoring.
2. Do not implement or run a production Policy B scorer until actual independent approval and a separate, scoped application record exist.
3. Do not run a candidate build or market-data backtest while G0 is blocked.
4. Continue only with non-duplicative, deterministic documentation/static verification that does not imply authorization or profitability.
5. Any future authorization must identify the exact reviewed commit, evidence hashes, allowed scope, limitations, and independent verifier.

## Unchanged global state

- Canonical source: `NONE`; G0: `BLOCKED_GLOBAL`.
- Source cases closed: `0`.
- All 23 prior strategy candidates remain historical-screen `FAIL`.
- G4 out-of-sample evidence insufficient; G6 adaptive-AI validation not built.
- No candidate build, market-data backtest, strategy promotion, or profitability claim.
- Live signing, public broadcast, and Binance orders remain `BLOCKED`.
- Profitability: **NOT ESTABLISHED**.
