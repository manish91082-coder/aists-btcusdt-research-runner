# CP-0238 Capital and Cost Evidence Preflight (Hindi-first)

**Review date:** 2026-10-18  
**Decision:** `CP0238_PREFLIGHT_PARTIAL_EVIDENCE_CAPTURED_EXECUTION_BLOCKED`  
**Scope:** ₹10,000 INR starting capital, Binance Spot BTCUSDT research only. This is an evidence preflight, not approval to build or run CP-0152.

## 1. What the sources support

### Binance Spot fee reference (current public page, not account verification)
The Binance fee page currently displays the Regular User baseline as **0.100% maker / 0.100% taker** and the BNB-fee column as **0.07500% / 0.07500%**. Binance's support explanation says fees apply on each successful Spot trade and that the fee asset depends on the asset received; fee tiers and promotions can vary. Sources:
- https://www.binance.com/en-IN/fee/trading
- https://www.binance.com/en-IN/support/faq/detail/e85d6e703b874674840122196b89780a

**Interpretation boundary:** these are public reference rates, not proof of this user's actual fee tier, account eligibility, pair-specific promotion, fee-token balance, or BNB discount being enabled. Do not bake the BNB rate into the primary result. Keep it as a sensitivity only after account eligibility is evidenced. The public fee page is a reference captured on the review date; archive a dated copy/hash before a later execution decision.

### Exchange filters
Binance's developer documentation describes symbol filters such as `PRICE_FILTER`, `LOT_SIZE`, `MARKET_LOT_SIZE`, and notional filters, which constrain price/quantity increments and minimum/maximum order value. Reference:
- https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/ws-api/account
- https://developers.binance.com/zh-CN/docs/products/derivatives-trading-usds-futures/common-definition

**Important:** the second URL is a derivatives definition page, not evidence of current BTCUSDT Spot filter values. No dated BTCUSDT Spot `exchangeInfo` snapshot and content hash was captured in this preflight. Therefore actual Spot tick size, step size, min/max quantity, and notional limits remain **UNKNOWN / NOT FROZEN**. A current endpoint response, if later collected, must be timestamped, saved with provenance and hashed; do not use today's values as historical values for earlier dates.

## 2. Frozen research stress grid versus actual user costs

The already-proposed CP-0152 research grid is retained as a **scenario grid only**:

| Fee assumption per side | Extra slippage per side | Combined cost assumption per side | Approx. round-trip combined cost |
|---:|---:|---:|---:|
| 10 bps | 5 bps | 15 bps | 30 bps (0.30%) |
| 10 bps | 10 bps | 20 bps | 40 bps (0.40%) |
| 10 bps | 20 bps | 30 bps | 60 bps (0.60%) |
| 15 bps | 5 bps | 20 bps | 40 bps (0.40%) |
| 15 bps | 10 bps | 25 bps | 50 bps (0.50%) |
| 15 bps | 20 bps | 35 bps | 70 bps (0.70%) |
| 20 bps | 5 bps | 25 bps | 50 bps (0.50%) |
| 20 bps | 10 bps | 30 bps | 60 bps (0.60%) |
| 20 bps | 20 bps | 40 bps | 80 bps (0.80%) |

These totals are arithmetic scenario assumptions (fee + additional slippage per side, then two sides), not measured execution costs or a claim that slippage is constant. The proposed moderate stress remains **15 bps fee + 10 bps extra slippage per side = 25 bps per side, approximately 50 bps per completed round trip** before any other excluded costs. This table does not authorize a backtest.

## 3. Capital and conversion status

- Starting amount is **₹10,000 INR**, not 10,000 USDT.
- INR→USDT conversion: **NOT FROZEN**. No conversion venue/source, quote timestamp/timezone, executable bid/ask or conversion convention, spread, transfer/fiat fees, or receipt evidence was captured here. Do not invent a USDT amount or silently use a generic FX rate.
- Allocation fraction and cash reserve: **NOT FROZEN**. The CP-0152 proposal's capital management conditions still need an explicit documented decision. Do not assume 100% allocation.
- BNB fee payment: **sensitivity only**, not primary-case assumption, until actual eligibility and fee deduction behavior are evidenced.
- Dated BTCUSDT Spot filters: **NOT CAPTURED**.
- No actual account fee statement, conversion receipt, exchange order, or trade was accessed or created.

## 4. Required evidence before any candidate evaluation

1. Choose and record the legitimate conversion source/venue and the exact quote time; preserve the quoted rate, bid/ask or executable conversion, spread, fees, and receipt/provenance. The conversion method must match the intended capital path.
2. Explicitly freeze allocation fraction and cash reserve in the scope record, without exceeding ₹10,000 INR-equivalent capital.
3. Capture the current official BTCUSDT Spot symbol/filter payload with UTC retrieval time, source URL, raw response, and SHA-256. Do not backdate current filters.
4. Evidence the user's actual applicable fee tier and whether BNB fee payment is enabled; otherwise retain conservative/base fee sensitivity and mark actual rate unknown.
5. Preserve the complete fee/slippage scenario grid and apply costs on both entry and exit in any future approved evaluation.
6. Separately resolve G0 source provenance and the partial material-quarantine issue, and obtain explicit user approval of the exact CP-0152 proposal. This preflight does not override either gate.

## 5. Decision and safety

`CP0238_PREFLIGHT_PARTIAL_EVIDENCE_CAPTURED_EXECUTION_BLOCKED`

Public fee references and a scenario grid are documented; actual INR→USDT conversion, account-specific fees, dated Spot filters, allocation and cash reserve are not yet evidenced/frozen. This step did **not** download market archives, build a candidate, run a backtest or paper test, promote a strategy, place an order, sign, or broadcast anything.

- G0: `BLOCKED_GLOBAL`; canonical source: `NONE`
- G2: `FAIL_CURRENT_23_CANDIDATES`; CP-0152 remains a proposal, not an evaluated candidate
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- G4: `INSUFFICIENT_EVIDENCE`
- G6: `NOT_BUILT` for validated adaptive AI
- G7: `LIVE_BLOCKED`
- Profitability: `NOT ESTABLISHED`

No backtest or candidate implementation is admissible until explicit CP-0152 approval **and** G0 clearance, with the remaining evidence prerequisites satisfied.
