# CP-0212: Policy B approval and application-readiness checklist

## Purpose and authorization boundary

This checkpoint records what must be satisfied before a separately authorized, sensitivity-only implementation of CP-0206 Policy B can be considered. It is a readiness checklist, not an approval, policy application, production change, or permission to run candidate performance work.

**Current disposition:** `READINESS_CHECKLIST_ONLY`  
**Independent approval:** `NOT PRESENT`  
**Policy B application record:** `NOT PRESENT`  
**Policy B application:** `NOT AUTHORIZED`  
**Candidate build/backtest:** `BLOCKED`  
**Global G0:** `BLOCKED_GLOBAL`  
**Canonical source:** `NONE`

No human or independent reviewer sign-off is represented by this document. The sign-off fields below must be completed by an actually authorized reviewer in a separate, traceable approval step; an automated CI pass is not a substitute.

## Exact evidence inputs reviewed

| Evidence | Immutable identifier |
|---|---|
| CP-0040 frozen strategy acceptance rulebook Git blob | `f0d0e81ea6708a0abeb34676f3ff12859080a3c7` |
| CP-0040 current rulebook-bound decision Git blob | `a40e7f031f5b920c066a7972983c788bda1503b8` |
| CP-0206 frozen Policy B Git blob | `224deb40b9acae340103ed1acc360a2d50d971c9` |
| CP-0210 segment/censor contract Git blob | `e65a501a8a5c6d3b6a6eb5992ce109038a501087` |
| CP-0210 contract-oracle test Git blob | `8280f4a169bcb1b6fc043b34672ade122328a70a` |
| CP-0211 independent review report Git blob | `bc19d509ba191570a0aa81ff9cbb927f700c26e7` |
| CP-0211 reviewed predecessor commit | `44571732df96459067332a8b9c4fb0772a3e9a75` |
| CP-0211 checkpoint commit / current branch head at checklist start | `ee6623e9e41911e18b8c1bce0bc45a773018a88e` |

These identifiers establish traceability only. They do not establish market-data execution, production censor scoring, independent approval, or profitability.

## Required executable evidence before application can be considered

All cases below are **OPEN / NOT YET DEMONSTRATED** by the existing CP-0208/0210 fixtures. They must be implemented as deterministic synthetic tests with an independent expected ledger, then reviewed against the exact frozen inputs.

1. **Gap-boundary censor event:** open a position before a deliberately non-contiguous 4h boundary; prove the censor transition creates no synthetic candle, boundary fill, or fabricated exit price.
2. **Eventual post-gap disposition:** when the synthetic fixture later has an ordinary sale event, prove the gap-exposed episode remains diagnostic/excluded from scored trade P&L and that no earlier fictitious exit is recorded.
3. **Segment reset and warm-up:** prove the post-gap segment begins with flat cash and zero inherited quantity, pending signal, indicator state, and position; require strategy-specific warm-up before signals can become eligible.
4. **Missing-key/window grouping:** prove adjacent missing slots are represented as one coverage window while every exact missing 4h key is preserved, with no accidental merging across a real observed interval.
5. **Unscorable full-window risk:** prove any full-window return/equity/drawdown result depending on unknown intragap valuation returns an explicit blocked/unscorable status rather than a numeric scored metric.
6. **Exact CP-0206 identity:** prove all 17 keys match the frozen policy exactly: one existing row-case overlap (`UNMATCHED-D-4h-1504713600000`) plus 16 gap-window-only keys; reject missing, duplicate, altered, or extra keys.
7. **Independent event-level accounting:** reconcile each event's cash, asset quantity, fees, slippage, realized/unrealized P&L, marked equity, and segment P&L against an independently authored Decimal ledger to `<= 1e-8 USDT`; test buy/sell/mark/censor/window-end paths and fee/quantity conservation.
8. **Scored versus diagnostic isolation:** assert excluded episode P&L is reported separately and never silently added to eligible scored P&L or used to claim a full-window risk pass.
9. **Fail-closed global gate:** verify the production candidate builder and baseline backtest remain blocked before data loading, output creation, or performance computation while G0 or Policy B approval/application is unresolved.
10. **Repeatability and evidence receipts:** hash-pin fixture definitions, expected ledger outputs, frozen policy, contract, test source, and test results; ensure altered evidence is rejected and no network or market archives are needed by these synthetic tests.

## Approval and application sequence

- [ ] All required executable tests above exist and pass on a recorded commit SHA.
- [ ] Independent reviewer inspects implementation, fixtures, expected Decimal ledger, exact-key population, and test output.
- [ ] Independent reviewer records identity/role, timestamp, exact commit SHA, evidence hashes, decision, scope, limitations, and any conditions. Do not fill these fields on the reviewer's behalf.
- [ ] Separate application decision explicitly authorizes **sensitivity-only** Policy B use and names the exact allowed runner/output scope.
- [ ] Application record preserves `canonical_source=NONE`, `G0=BLOCKED_GLOBAL`, source cases closed = 0, no strategy promotion, and no live actions.
- [ ] Separate verifier checks the application record and all evidence hashes before any authorized sensitivity run.
- [ ] If any item fails or is absent, stop; do not implement/run Policy B scoring or candidate market performance.

### Independent reviewer sign-off record

- Reviewer identity and authority: **NOT PRESENT**
- Review timestamp: **NOT PRESENT**
- Exact reviewed commit SHA: **NOT PRESENT**
- Evidence hash verification result: **NOT PRESENT**
- Decision (`APPROVE` / `REJECT` / `CONDITIONAL`): **NOT PRESENT**
- Scope and conditions: **NOT PRESENT**
- Application record reference: **NOT PRESENT**

This blank record is intentional. CP-0212 does not impersonate or infer human approval.

## Unchanged global blockers and scope exclusions

- The 17-key gap population is unresolved for source eligibility.
- Other unresolved populations: 909 unmatched rows, 52 shared economic conflicts, 8 close-time-only cases, 11 non-row blockers; 450 February 2018 off-grid rows are a subset of the 909.
- All 23 previously screened strategy candidates remain historical-screen `FAIL`.
- No canonical source selected; no source cases closed.
- No candidate build, market-data backtest, strategy promotion, or profitability claim.
- No synthetic market candles, synthetic fills, or hypothetical boundary closeout.
- Live signing, public broadcast, and Binance orders remain `BLOCKED`.
- Profitability remains **NOT ESTABLISHED**.

## CP-0212 decision

`CHECKLIST_RECORDED_APPROVAL_ABSENT_APPLICATION_NOT_AUTHORIZED`

Next bounded action: implement only the missing deterministic synthetic censor-ledger tests and review their scope, without applying Policy B to production scoring or running market-data candidate performance. Reassess authorization only after the executable evidence and a real independent sign-off/application record exist.
