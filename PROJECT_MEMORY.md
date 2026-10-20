# Project Memory

Durable project memory. Live GitHub state and verified evidence override old chat recollection if there is a conflict.

## Identity and style
- Requested project name: Full AI Crypto Trading Bot 21 OCT.
- Current GitHub repository: manish91082-coder/aists-btcusdt-research-runner. User will rename it later.
- GitHub holds project specification, status, memory, continuity, constitution/rules/locks, evidence, decisions and project/session logs.
- Do project changes directly in GitHub. Do not substitute Colab or Drive without explicit user direction.
- Respond primarily in Hindi, using standard technical terms where helpful.
- Apply zero-trust verification; distinguish user-confirmed requirements, proposals, open research and verified completion.
- After substantive work, synchronise applicable documents, commit, and verify the live GitHub result.

## User-confirmed requirements
- Fully AI-assisted Binance crypto system across Spot and Futures; long and short exposure.
- AI dynamically chooses strategy, algorithm, indicators/features, entry, exit, initial stop, take-profit, trailing/gain-locking logic, and position adjustments.
- Requested horizons: 5m, 15m, 1h, 4h, 8h, 1d, 1w and 1M/monthly.
- Scanner over a high-volume top-ten coin universe; exact coins are not yet selected and must be evidence-ranked.
- Learn from longest verifiable historical data, with ten-year target only where data exists.
- Stated initial capital: 10,000 USDT.
- Use BNB for fees wherever actual Binance product/account rules support it.
- Prefer zero-cost/open-source resources; no fake claim that all compute or 24/7 hosting is free.
- Research first, then coding. No fake data/PnL or unverified assertion. Keep an audit trail.

## Clean-slate state
- Clean-slate main commit: f52bac573c9509c71143158a7f609bd55a6a76bb.
- Previous snapshot: f2fcc6f2e74dcd08e59cdcb811cd680d35fb1733.
- Backup branch: backup/pre-cleanup-2026-10-21-main-f2fcc6f.
- Repository and history were retained during reset.

## Architecture recommendation, not yet user-approved
- Ten bounded AI roles are proposed in PROJECT_BLUEPRINT.md.
- A deterministic Safety Kernel must always have veto authority.
- Recommend researching USDⓈ-M perpetual Futures first for USDT-denominated long/short exposure; eligibility is unresolved and must be checked.
- Treat 10,000 USDT as paper/research equity until live capital is explicitly authorised.
- Decide whether BNB fee reserve is inside or outside the stated 10,000 USDT.
- Ordinary Spot is long/flat. Short exposure should use an eligible Futures product unless Spot Margin is separately researched/approved.

## Verified facts and current gaps
- Binance launched in July 2017, making full ten-year Binance-only venue history impossible as of 2026-10-21; individual instruments may have shorter history.
- Official Binance data archive documentation describes daily/monthly archives and checksums; no symbol-level coverage has yet been audited.
- Published BNB discounts differ for Spot and USDⓈ-M Futures. Real fees depend on account/product/configuration, and Futures funding is separate.
- FIU registration alone does not establish account-specific Futures eligibility or answer all tax/legal questions. Eligibility is a mandatory gate.
- No code, trained model, verified data inventory, coin list, backtest or paper run exists on this clean-slate work branch as of this checkpoint.
- No credential, fund transfer or live trade has been authorised.

## 2026-10-21 strategy-stage priority
- User instruction: defer taxation/jurisdiction research to a later stage and focus current work on trading strategies and the Binance data they require.
- This is a sequencing deferral, not permission to bypass restrictions or execute live orders. Eligibility remains a later release gate.
- STRATEGY_RESEARCH.md registers 12 falsifiable candidates. None has empirical results yet.
- Trading commission should be paid in BNB wherever product/account settings actually support deduction. Funding, spread, slippage, impact and liquidation are separate costs, not all BNB fees.


## 2026-10-21 — User-requested roadmap lock
- PLAN_AND_PHASE_LOCK.md is the default dependency-ordered execution plan (phases 0–12) and must be read before choosing the next task.
- Current immediate priority is strategy/data: audit one real official Binance archive end-to-end, then freeze S-01 to S-04 experiment protocols before backtesting.
- Tax/jurisdiction research is deferred for the current stage per the user's instruction, but is still required before any live execution. No restrictions are bypassed.
- The plan does not imply that any gate has passed. No data audit, top-ten selection, model training, backtest, paper run, real order or deployment is claimed unless separately evidenced.


## 2026-10-21 — Full AI requirement and anti-drift lock
- User's detailed full-system requirement is consolidated in PROJECT_BLUEPRINT.md and the binding phase order is PLAN_AND_PHASE_LOCK.md.
- AI must dynamically select among validated strategies/features and propose direction, entries, risk-bounded sizing, exits, stops, targets and trailing/gain-lock changes across 5m, 15m, 1h, 4h, 8h, 1d, 1w and monthly. Ten logical AI roles are proposed; the independent deterministic Safety Kernel remains mandatory.
- Up to ten coins must be evidence-ranked with point-in-time historical membership. Use the longest verifiable history per asset/product; no invented ten-year coverage.
- BNB commission is used only where current product/account rules support it and actual records verify deduction. Funding/spread/slippage/impact remain distinct costs.
- At each substantive task, check live GitHub head, active phase, acceptance gate, evidence and blockers. Log real changes and read them back. Do not claim unverified tests, persistent model-memory changes, full uptime or zero error.
- Current next gate: representative official Binance archive audit. No data audit, backtest, model training, paper run or live trade is claimed.


## 2026-10-21 — Phase 2 blocker checkpoint
## 2026-10-21 — Phase 2 archive retrieval blocker
- Attempted HEAD requests from the current execution container for candidate BTCUSDT Spot 5m and USDⓈ-M Futures daily archive URLs and companion `.CHECKSUM` URLs for 2026-10-20.
- All four attempts failed before receiving an HTTP response with `Temporary failure in name resolution`; the web retrieval tool also could not access the direct checksum URLs.
- This proves a current-environment retrieval blocker only. It does not prove the candidate archives exist or do not exist, and no archive bytes, checksum, schema, timestamp, row count, gap result or data-quality PASS is claimed.
- Created DATA_AUDIT_LOG.md with exact attempted URLs, observed errors, evidence boundaries and a reproducible zero-cost next route via a network-enabled user-owned runtime such as Colab.
- Phase 2 remains BLOCKED pending actual retrieval. No bulk download, strategy backtest, model training, paper run or live order was performed. Next: retrieve one real official artifact and its checksum, audit it end-to-end, then freeze S-01 to S-04 before any backtest.


## 2026-10-21 — Phase 2 audit handoff
- The current runtime cannot resolve `data.binance.vision`; see `DATA_AUDIT_LOG.md`.
- A stdlib audit runner and zero-cost Colab runbook are committed as `tools/audit_binance_archive.py` and `RUN_DATA_AUDIT.md`. They are prepared but not run against real archives here.
- Current gate remains BLOCKED until Spot and USDⓈ-M reports show actual source/checksum/schema/timestamp/gap/API comparison evidence. Then independently review and freeze S-01 to S-04 before backtesting.


## 2026-10-21 — Audit runner quality note
- Added expected UTC-day candle-open coverage to the archive auditor so missing boundary candles are not missed by inter-row gap checks. This is code hardening only; no real archive audit or PASS exists yet.

## 2026-10-21 — Durable anti-drift process lock
- User explicitly requires every response to be checked against the entire locked plan, strict no-drift execution, and uninterrupted continuity.
- Operational interpretation: do not answer “next” with a generic status repeat. Re-read the complete current master plan and relevant live GitHub status/evidence each turn, identify the single next safe action, do useful work where possible, record material changes, verify readback, and clearly separate verified facts from assumptions and blockers.
- The durable source of truth is GitHub main and the evidence registers. Chat memory alone is not proof of a repository change, test result, data audit, or phase completion.
- Active gate remains Phase 2 actual Spot + USDⓈ-M representative archive audit; no strategy backtest or downstream gate may start early.

## 2026-10-21 — Phase 2 optional-header parser hardening
- During code review, addressed the risk of an optional header row in an official 12-column kline CSV being miscounted as malformed data. The runner recognises only the exact known 12-column header on the first non-empty record and records whether it was present.
- Four offline tests were added. Runner commit: `5369263058971e14fcae4db438a1e205cbb2c7ce`; test commit: `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- These are code/test changes only. CI for the latest changes and actual archive/checksum/API checks remain unverified. Phase 2 stays blocked; do not start strategy backtests.
