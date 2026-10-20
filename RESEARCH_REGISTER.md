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
| R03 | Historical data feasibility | VERIFIED-PARTIAL | Official archive/checksum and timestamp-unit documentation reviewed; exact symbol/product dates, representative checksum run and gaps pending |
| R04 | Top-10 universe | NOT-STARTED | Point-in-time eligibility, liquidity/spread/impact and data-quality ranking; snapshot reproducible |
| R05 | Timeframe/candle consistency | VERIFIED-PARTIAL | Horizons and monthly archive label noted; aggregation and timestamp tests pending |
| R06 | Fees, BNB and futures carry | VERIFIED-PARTIAL | Published guides reviewed; account rate, wallet, discount and funding histories pending |
| R07 | Feature/indicator/pattern registry | NOT-STARTED | Versioned definitions, units, warm-up, missingness, provenance and leakage tests |
| R08 | Strategy catalogue/mathematical hypotheses | VERIFIED-PARTIAL | STRATEGY_RESEARCH.md registers 12 falsifiable hypotheses and a research order; no strategy has been tested or ranked empirically |
| R09 | AI model/brain architecture | VERIFIED-PARTIAL | Ten proposed roles and safety kernel documented; model-family comparison pending |
| R10 | Risk/sizing/exits/portfolio maths | NOT-STARTED | Unit-checked equations, assumptions, edge cases, stress scenarios and independent tests |
| R11 | Backtesting/statistical audit | NOT-STARTED | Causal replay, costs, chronological walk-forward, leakage and holdout protocol proven |
| R12 | Zero-cost compute/storage/runtime | NOT-STARTED | Measured needs and current free-tier terms, persistence and uptime recorded |
| R13 | Execution/security/operations | NOT-STARTED | Least privilege, timeout/partial-fill/reconnect/reconciliation/kill-switch tests |
| R14 | Shadow/paper acceptance | NOT-STARTED | Pre-registered observation period and metrics from real market inputs, virtual fills labelled |
| R15 | Research coverage and final go/no-go | NOT-STARTED | Required gates evidenced; still not live authorization |

## Current priority override (user-confirmed 2026-10-21)
Taxation/jurisdiction research is deferred to a later stage. Immediate focus is strategy hypotheses and the Binance data needed to test them. This does not remove later live-execution gates or authorise bypassing restrictions.

## Suggested sequence
The current binding order is PLAN_AND_PHASE_LOCK.md. Respect the user's 2026-10-21 priority override:
1. Audit one real official Binance archive end-to-end (R03), including checksum, schema, timestamp unit and data-quality output.
2. Freeze S-01 to S-04 experiment protocols and benchmarks before any backtest (R08/R11).
3. Build the exact historical coverage inventory (R03/R05), then evidence-rank the top-10 universe (R04).
4. Complete feature registry and leakage checks (R07), fee/funding/BNB ledger (R06), and risk/portfolio mathematics (R10).
5. Validate the backtest/statistical framework (R11) before comparing strategy results.
6. Choose model families from evidence and measured compute (R09), then evaluate resource feasibility (R12).
7. Perform execution/security/operations and shadow/paper acceptance (R13-R14) only after prior gates.
8. Complete current product/account/jurisdiction eligibility and applicable requirements before any live release (R02/R15). Tax/jurisdiction research is deferred from the current strategy/data stage, not waived.

## Stop conditions
Stop and preserve a blocker when product access is unclear/prohibited, required data is missing, checksum/schema fails, leakage is unresolved, cost modelling is incomplete, compute cannot meet cadence, risk limits are undefined, or any AI role bypasses the Safety Kernel.

## Phase 2 latest attempt (2026-10-21)
- R03 remains BLOCKED for the representative archive run: the current runtime failed DNS resolution for the candidate official archive/checksum URLs. Official archive documentation is available, but documentation is not a downloaded/validated artifact. See [DATA_AUDIT_LOG.md](DATA_AUDIT_LOG.md).


## Phase 2 tooling handoff (2026-10-21)
- Added a standard-library archive auditor and a Colab runbook to support R03 using a network-enabled zero-cost runtime. This improves reproducibility but does not change R03 to PASS: no artifact was downloaded or validated in the current environment.
- Required next evidence: Spot and USDⓈ-M report JSON, official checksum match, schema/timestamp/gap checks, and bounded official API spot-check results.
