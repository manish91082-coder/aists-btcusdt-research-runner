# CP-0207: Independent accounting reconciliation preflight

## Decision

**Status: ACCOUNTING_ORACLE_FIXTURES_ADDED; PRODUCTION_ACCOUNTING_NOT_END-TO-END-VALIDATED.**

CP-0207 adds an independent, standard-library-only Decimal accounting oracle and static source guards. It does not execute CP-0027 on market data, authorize a candidate build/backtest, or apply the gap-window policy. The CP-0203 and CP-0026/CP-0040 fail-closed gates remain mandatory.

## Accounting contract

For each fill, independently track cash, asset quantity, reference price, modeled fill price, notional, fee paid, modeled slippage cost, realized trade P&L, mark-to-market equity, and segment P&L.

For a buy, fill price = reference × (1 + slippage rate), quantity = available cash / (fill × (1 + fee rate)), and post-fill cash plus marked inventory plus separately disclosed fee must reconcile to pre-fill cash within **1e-8 USDT**. For a sell, net proceeds = quantity × sell fill − fee. Round-trip net P&L is net sell proceeds less entry notional and entry fee. Fees and slippage are each counted once per fill.

When a segment begins and ends flat, ending cash minus starting cash must equal the sum of net closed-trade P&L within **1e-8 USDT**. Equity at a valid mark is cash + quantity × mark. A gap-exposed episode is censored from scored metrics under Policy B until an independently approved accounting treatment makes it scorable.

## What tests establish

- Decimal-based, independently derived fixture arithmetic for buy/sell cash, quantity, fees, slippage, equity and flat-account reconciliation.
- Fixed round-trip example and segment-P&L identity.
- Static checks that CP-0027 remains blocked before manifest/output/performance work while G0 is unresolved.
- Static checks that the feature builder groups indicators by contiguous segment and specifies EMA/RSI/Donchian warm-up periods.
- Frozen CP-0206 policy still labels gap-exposed episodes `CENSORED_GAP_EXPOSED`.

## What tests do not establish

- No live or historical market-data backtest was run.
- No real CP-0027 trade ledger was reconciled end-to-end against independently generated trade-by-trade cash/quantity/fee/equity records.
- Static checks do not prove the production simulator is free of all accounting defects.
- Legacy carry-through-gap equity marking remains in CP-0027 source, but remains ineligible for scoring under the unresolved frozen gap policy.
- No source authority was selected, source case closed, or quarantine applied to the candidate builder.

## Gate state

- Canonical source: `NONE`.
- G0: `BLOCKED_GLOBAL`.
- Source cases closed: `0`.
- Candidate build/backtest: **BLOCKED**.
- Strategy promotion: `false`.
- Live signing, public broadcast and exchange orders: **BLOCKED**.
- Profitability: **NOT ESTABLISHED**.

## Next

After CP-0207 CI terminal result is verified, add an independent event-by-event reconciliation harness that consumes a deterministic synthetic event tape and compares production-simulator outputs to an independently calculated Decimal ledger. Keep it separate from market data; it cannot infer profitability or clear G0.
