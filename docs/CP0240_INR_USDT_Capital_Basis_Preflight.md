# CP-0240 INR-to-USDT Capital Basis and Allocation Preflight

**Review date:** 2026-10-18  
**Decision:** `CP0240_CONVERSION_BASIS_NOT_FROZEN_NO_USER_CAPITAL_PNL`  
**Scope:** Prepare an evidence-safe capital convention for the ₹10,000 INR research budget. This is not a conversion instruction, trading approval, or account access.

## 1. Frozen facts versus unknowns

### Established by project scope

- Planned starting capital: `₹10,000 INR`.
- Intended research market: Binance Spot BTCUSDT.
- The old `initial_capital_usdt: 10000` diagnostic basis is not equivalent to ₹10,000 INR and must not be reused or rescaled.
- CP-0152 requires a conversion source, timestamp and convention before user-capital performance is computed. Without an admissible basis, user-capital P&L and returns are `NOT_COMPUTABLE`.
- The current BTCUSDT Spot filter evidence from CP-0239 describes operational metadata at capture time only. It does not establish the INR/USDT conversion rate.

### Not established

- No actual INR-to-USDT conversion quote, venue, execution receipt, spread, fee or timestamp is present in the inspected CP-0238 record.
- No user-specific account fee tier, BNB discount eligibility, or balance is evidenced.
- Allocation fraction and cash reserve are not approved/frozen.
- No admissible current INR-to-USDT conversion value is frozen by this record.

**Decision:** Do not invent a USDT balance. Do not infer the actual conversion rate from USD/INR alone, a generic FX rate, a stale web page, or the BTCUSDT exchange filter endpoint.

## 2. Separate two possible research bases

### Basis A — actual funded capital

Use only when a real conversion/funding event is evidenced. Preserve, at minimum:
1. Venue and exact instrument/path used to acquire USDT.
2. Quote/execution timestamp in UTC and local time zone.
3. INR amount debited, USDT amount credited, executable bid/ask or executed rate.
4. All platform, payment, transfer, conversion and network fees, with fee currency.
5. Receipt/transaction reference with sensitive identifiers redacted in public repository artifacts.
6. Raw evidence file or safe redacted receipt, SHA-256, capture time and reviewer.
7. Reconciliation equation: INR debited = INR-equivalent executed conversion + separately itemized fees, subject to the venue's documented settlement semantics.

If any critical field is absent or cannot be reconciled, user-capital P&L remains `NOT_COMPUTABLE`.

### Basis B — hypothetical research conversion

If no actual conversion has occurred, label the capital basis explicitly `HYPOTHETICAL_NOT_FUNDED`. Before any future approved evaluation:
1. Choose an admissible, reproducible quote source/path consistent with the intended capital route.
2. Record quote time, executable side, quoted rate, spread, fees, fee currency and evidence hash.
3. Use the net executable USDT amount after documented costs, not a mid-price-only estimate.
4. Declare whether the research conversion is one-time at start, and how residual INR/USDT is treated.
5. Keep the hypothetical result separate from actual account returns and never describe it as realized P&L.

A USD/INR reference rate multiplied by a USDT/USD quote is a possible cross-rate estimate, but it is not an executable INR-to-USDT conversion and cannot by itself establish the net amount received. Any such approximation would need explicit labeling and separate spread/fee assumptions; it must not silently become the primary capital basis.

## 3. Allocation and cash-reserve decision

The current proposal does not approve an allocation. No allocation is frozen by CP-0240.

For a future paper-only candidate, the CP-0152 G4 rulebook already specifies a 25% virtual allocation for its paper gate. This is a gate-specific paper setting, not blanket authorization to use 25% in historical screening, and not approval to deploy real capital. A future scope decision must explicitly state:
- screening allocation and paper allocation separately;
- cash reserve fraction and amount;
- whether fees are paid from quote proceeds or a separate fee asset;
- whether reinvestment/compounding is disabled;
- maximum position notional and quantity constraints;
- treatment of dust, rejected orders, and minimum-notional skips.

Until a versioned scope decision records these fields, capital allocation stays `NOT_FROZEN`. Do not silently assume 100% allocation or hidden leverage/compounding.

## 4. Cost model and current exchange filters

- Keep the CP-0152 9-case grid: fee 10/15/20 bps per side paired with extra slippage 5/10/20 bps per side.
- Moderate stress remains 15 bps fee + 10 bps extra slippage per side = 25 bps per side, approximately 50 bps per completed round trip. This is a scenario assumption, not measured execution cost.
- CP-0239 captured current BTCUSDT Spot filters and preserved raw payloads/manifests. They must not be backdated to earlier historical periods.
- BNB discount stays sensitivity-only until actual account eligibility and fee deduction behavior are evidenced.

## 5. Gate decision and admissible next step

- Capital conversion: `NOT_FROZEN`
- User-capital P&L/returns: `NOT_COMPUTABLE`
- Allocation/cash reserve: `NOT_FROZEN`
- Account-specific fees: `UNKNOWN`
- CP-0152 approval: `NOT_APPROVED`
- G0 historical provenance: `BLOCKED_GLOBAL`; canonical historical source: `NONE`

**Next admissible action:** only if a real funding receipt or an approved reproducible hypothetical quote source becomes available, preserve and review its evidence without exposing sensitive account identifiers. Otherwise, retain the explicit `NOT_FROZEN` status and continue independent G0 source-adjudication work. Do not run CP-0152 until the exact strategy receives explicit user approval and G0 is cleared.

No exchange account was accessed; no conversion was executed; no market archive was downloaded; no candidate, backtest or paper run was executed; no order, signature or public broadcast occurred.
