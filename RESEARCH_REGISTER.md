# Research Register and Phase Tracker

Updated: 2026-10-21. A source found is not the same as a question fully resolved.

## Status meanings
- VERIFIED-PARTIAL: official source supports a limited finding; conditions remain.
- NOT-STARTED: no adequate evidence packet yet.
- BLOCKED: a prerequisite prevents safe continuation.
- PASS: criteria met with linked/reproducible evidence.
- FAIL: criteria not met; preserve failure evidence and resolve.

| ID | Workstream | Status | Required output / acceptance |
|---|---|---|---|
| R00 | Scope/requirements/safety charter | VERIFIED-PARTIAL | Blueprint captures user requirements and unresolved decisions; no strategy invented |
| R01 | Official source/fee/archive reconnaissance | VERIFIED-PARTIAL | Evidence register with primary sources and limits; actual account fees still pending |
| R02 | Product/jurisdiction eligibility | NOT-STARTED | Current terms, account-specific Spot/Futures availability and applicable requirements evidenced; no restriction bypass |
| R03 | Historical data feasibility | VERIFIED-PARTIAL | Archive/checksum process confirmed; ten Binance-only calendar years impossible; exact symbol/product dates pending |
| R04 | Top-10 universe | NOT-STARTED | Point-in-time eligibility, liquidity/spread/impact and data-quality ranking; snapshot reproducible |
| R05 | Timeframe/candle consistency | VERIFIED-PARTIAL | Horizons and monthly archive label noted; aggregation and timestamp tests pending |
| R06 | Fees, BNB and futures carry | VERIFIED-PARTIAL | Published guides reviewed; account rate, wallet, discount and funding histories pending |
| R07 | Feature/indicator/pattern registry | NOT-STARTED | Versioned definitions, units, warm-up, missingness, provenance and leakage tests |
| R08 | Strategy catalogue/mathematical hypotheses | NOT-STARTED | Formal hypotheses, baselines, costs, falsification criteria and evidence |
| R09 | AI model/brain architecture | VERIFIED-PARTIAL | Ten proposed roles and safety kernel documented; model-family comparison pending |
| R10 | Risk/sizing/exits/portfolio maths | NOT-STARTED | Unit-checked equations, assumptions, edge cases, stress scenarios and independent tests |
| R11 | Backtesting/statistical audit | NOT-STARTED | Causal replay, costs, chronological walk-forward, leakage and holdout protocol proven |
| R12 | Zero-cost compute/storage/runtime | NOT-STARTED | Measured needs and current free-tier terms, persistence and uptime recorded |
| R13 | Execution/security/operations | NOT-STARTED | Least privilege, timeout/partial-fill/reconnect/reconciliation/kill-switch tests |
| R14 | Shadow/paper acceptance | NOT-STARTED | Pre-registered observation period and metrics from real market inputs, virtual fills labelled |
| R15 | Research coverage and final go/no-go | NOT-STARTED | Required gates evidenced; still not live authorization |

## Suggested sequence
1. R02: current product/jurisdiction rules and account availability.
2. R03: exact archive coverage, checksums, timestamp units, rows and gaps per candidate symbol/market.
3. R04: point-in-time top-10 ranking policy and observed candidates.
4. R06: full fee/funding/BNB ledger.
5. R07-R08: feature, indicator, chart-pattern and strategy research.
6. R10: risk formulas and stress cases.
7. R11: backtest method and acceptance gates before empirical comparisons.
8. R09: choose model families based on data, evidence and measured compute; do not guess.
9. R12-R14: cost, security and operations after earlier gates.

## Stop conditions
Stop and preserve a blocker when product access is unclear/prohibited, required data is missing, checksum/schema fails, leakage is unresolved, cost modelling is incomplete, compute cannot meet cadence, risk limits are undefined, or any AI role bypasses the Safety Kernel.