## 2026-10-21 | Market-data manifest specification
- Added MARKET_DATA_MANIFEST_SPEC.md with one-row-per-artifact provenance, checksum, timestamp-unit, schema, row/gap and validation fields.
- Proposed BTCUSDT Spot 5m plus matching USDⓈ-M Futures archive as the first representative audit target. This is only a proposed target; no file was downloaded and no checksum was run.
- README links the strategy dossier and market-data manifest spec.
- Next step: execute the representative archive audit through an available reliable download path; if unavailable in the current environment, report the blocker rather than pretend validation passed.

---

## 2026-10-21 | Strategy research focus and Binance data requirements

### User direction
Defer tax/jurisdiction research to a later stage; focus the immediate work on strategies and the Binance data required to test them. BNB commission payment remains a requirement wherever the product/account supports it. This is a sequencing change, not a waiver of later execution gates.

### Research performed
- Reviewed official Binance Spot exchange-information and rate-limit documentation.
- Reviewed official Spot symbol filter documentation.
- Reviewed official USDⓈ-M Futures market-data/kline reference.
- Rechecked official public archive documentation for requested kline intervals, checksums and Spot timestamp-unit handling.
- Created STRATEGY_RESEARCH.md with 12 testable hypotheses: trend, mean reversion, breakout, momentum, regime selection, candle features, funding-aware filtering, liquidity filtering, cross-asset context, supervised probability, portfolio allocation and exit-policy tournament.

### Honest status
No strategy was run or proven profitable. No archive was downloaded, no checksum was executed, no model trained, no backtest/paper run occurred, and no live order was sent. Strategy hypotheses are registered only.

### Next task
Build a reproducible market-data manifest design and audit one representative archive end-to-end; then pre-register S-01 to S-04 experiments before any backtest.

---

# Session Log

Newest entries first. Record verified facts, not intentions as completed work.

## 2026-10-21 | AI trading charter and research baseline

### User-confirmed requirements
- Binance Spot and Futures, long/short exposure, AI-driven dynamic market/strategy/feature/entry/exit/stop/target/trailing management and continuous scanner.
- Timeframes: 5m, 15m, 1h, 4h, 8h, 1d, 1w and 1M.
- Evidence-backed top-ten high-volume universe, exact list to be decided by research.
- 10,000 USDT stated initial capital; BNB fees where genuinely supported.
- Longest available historical learning data, with no fabricated data/results.
- Zero-cost-first resources, research before coding and GitHub-based memory/status/continuity/rules/logging.

### Research completed in this response
- Reviewed official Binance Public Data repository for archives, supported markets, interval labels and checksum instructions.
- Reviewed official Spot API docs, symbol filters and Spot Testnet documentation; testnet has virtual funds and periodic reset limitations.
- Reviewed Binance BNB fee FAQ (page last updated 2026-02-17): published maxima differ for Spot/Margin and Futures and require balance/settings.
- Reviewed Binance Futures fee FAQ (page last updated 2026-01-05): commission, funding and liquidation-related costs are distinct; USDⓈ-M BNB deduction requires enough BNB in the Futures wallet.
- Reviewed official Binance launch announcement (14 July 2017): complete ten-year Binance-only historical coverage cannot exist as of this checkpoint.
- Reviewed Binance India KYC announcement, official FIU-IND order and official Income Tax Department pages on sections 115BBH and 194S. Account-specific Futures access remains unresolved and is a gate, not an assumption.
- Findings and limitations are registered in EVIDENCE_REGISTER.md.

### Repository actions planned in this checkpoint
- Add master blueprint, research register, evidence register, decision log and quality audit.
- Update README, status, durable memory, continuity, rules/locks, session log and changelog.
- Proposed ten AI roles plus independent deterministic Safety Kernel; these are design proposals, not implemented agents.
- Record explicit restrictions: no coding/live trade before research gates and approvals.

### Explicitly not performed
No code, datasets, checksum run, top-ten selection, trained model, backtest, paper-trading session, real order, credential creation, fund transfer or deployment.

### Next action
Start R02 product/jurisdiction/account eligibility and R03 exact per-symbol historical coverage/checksum/timestamp/gap inventory. Keep all gates fail-closed.

---

## 2026-10-21 | Clean-slate and continuity foundation
- User confirmed clean-slate deletion of the 692 tracked files from old main snapshot f2fcc6f2e74dcd08e59cdcb811cd680d35fb1733.
- Backup branch backup/pre-cleanup-2026-10-21-main-f2fcc6f was created at that snapshot.
- Clean-slate commit f52bac573c9509c71143158a7f609bd55a6a76bb moved to main; GitHub Contents API returned an empty list at that point.
- Initial governance/continuity documents were created and verified.
- User deferred repository rename. No trading code/backtest/paper/live order was performed.

## 2026-10-21 | User-requested master plan and phase lock
### Action
- Reviewed the current master blueprint, project memory, continuity protocol, rules/locks, strategy dossier, research register and current status.
- Added PLAN_AND_PHASE_LOCK.md with the full dependency-ordered roadmap, explicit phase exit gates, change-control protocol and immediate work queue.
- Locked this plan as the default project sequence in RULES_AND_LOCKS.md and updated status/continuity records.

### Current truth
- 12 strategy candidates are registered but not empirically tested.
- Market-data manifest specification exists, but no representative archive download/checksum/audit has been verified.
- No top-10 universe, trained model, backtest, paper run, trading engine, real order or deployment is claimed.
- Live trading, credentials, withdrawals, production deployment and real capital remain locked.

### Next action
1. Audit a real official Binance archive end-to-end; do not claim PASS until the artifact and validation output are observed.
2. Freeze S-01 to S-04 experiment protocols before backtesting.
3. Continue the phase gates in PLAN_AND_PHASE_LOCK.md without silent skipping.


## 2026-10-21 | Detailed user requirement audit and plan saturation
### Full requirement
Binance Spot + Futures; long/short; BNB commission where supported; 5m/15m/1h/4h/8h/1d/1w/monthly; evidence-selected top ten; longest verifiable history; dynamic strategy/indicator/algorithm, entries/exits/sizing/SL/TP/trailing and position changes; 10,000 USDT research equity; zero-cost-first; no fake evidence or drift; research before code.

### Repository changes
- Expanded PLAN_AND_PHASE_LOCK.md with AI decision contract, ten bounded logical roles, independent Safety Kernel, scanner/timeframe causality, dynamic position/exit rules, zero-cost measurement, fee accounting and requirement-to-phase traceability.
- Linked the master plan from PROJECT_BLUEPRINT.md and synchronised status, governance and continuity.

### Verification truth
The documents were written and read back from GitHub. This verifies repository documentation only. No representative archive audit, backtest, model training, paper run or live order is newly claimed.

### Next gate
Phase 2: actual official Binance archive download/verification and data-quality audit. Preserve blockers; never fabricate PASS.


## 2026-10-21 | Phase 2 retrieval blocker
## 2026-10-21 — Phase 2 archive retrieval blocker
- Attempted HEAD requests from the current execution container for candidate BTCUSDT Spot 5m and USDⓈ-M Futures daily archive URLs and companion `.CHECKSUM` URLs for 2026-10-20.
- All four attempts failed before receiving an HTTP response with `Temporary failure in name resolution`; the web retrieval tool also could not access the direct checksum URLs.
- This proves a current-environment retrieval blocker only. It does not prove the candidate archives exist or do not exist, and no archive bytes, checksum, schema, timestamp, row count, gap result or data-quality PASS is claimed.
- Created DATA_AUDIT_LOG.md with exact attempted URLs, observed errors, evidence boundaries and a reproducible zero-cost next route via a network-enabled user-owned runtime such as Colab.
- Phase 2 remains BLOCKED pending actual retrieval. No bulk download, strategy backtest, model training, paper run or live order was performed. Next: retrieve one real official artifact and its checksum, audit it end-to-end, then freeze S-01 to S-04 before any backtest.
