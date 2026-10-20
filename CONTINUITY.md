# Session and Chat Continuity Protocol

Use after a pause, context loss, new thread or uncertain prior state.

## Mandatory resume sequence
1. Fetch the live GitHub main ref and write down its current SHA.
2. Read README, PROJECT_STATUS, PROJECT_MEMORY, CONTINUITY, RULES_AND_LOCKS, PROJECT_BLUEPRINT, RESEARCH_REGISTER, EVIDENCE_REGISTER, DECISION_LOG, QUALITY_AUDIT, SESSION_LOG and CHANGELOG.
3. Compare branch/head and contents with the last checkpoint; an SHA in an old chat message is not proof of current state.
4. Identify last verified research gate, remaining blockers and next safe action.
5. If chat memory conflicts with GitHub, explain the difference and follow verified GitHub state plus the current user instruction; do not overwrite unexpected changes silently.
6. Refresh official source pages if product terms, APIs, fees, availability or regulations may have changed.

## End-of-substantive-work
1. Record what actually changed and what remains unverified.
2. Update PROJECT_STATUS, this file, SESSION_LOG and CHANGELOG; update PROJECT_MEMORY for new durable facts/decisions; update RULES_AND_LOCKS when a rule changes; update the blueprint/research/evidence/decision/audit files relevant to the task.
3. Mark items USER-CONFIRMED, RECOMMENDED-PENDING-APPROVAL, RESEARCH-OPEN, BLOCKED or VERIFIED-PARTIAL as appropriate.
4. Prefer one coherent checkpoint commit. Use expected-SHA/lease protection to avoid overwriting unexpected main changes.
5. Re-fetch the new branch head, root listing and every changed path. Only then report completion.
6. If a write or readback fails, disclose it clearly.

## Current checkpoint
The clean-slate main is transitioning into a research-first architecture. Blueprint, research, source and audit records are being established. Research is incomplete and trading implementation has not begun. Fetch the live head next session.

## Immediate next work
R02: verify current official Binance product/jurisdiction/account eligibility and applicable requirements without bypassing restrictions.
R03: inventory historic coverage, source paths, checksums, timestamp units, row counts and gaps per selected symbol/market.
Then R04: evidence-based top-ten ranking. No trading code before applicable gates pass.

## Context priority
1. Current verified GitHub state and primary evidence.
2. Repository blueprint, rules, source register and decision log.
3. Current user instructions.
4. Earlier chat recollection only if consistent.

## Anti-drift locks
No feature is complete because it was planned. No test is PASS without observed output. No paper/synthetic result may be represented as real execution. LLM output is not source evidence. Never commit secrets. Live trading stays locked until all gates and exact-scope authorisation are complete.

## 2026-10-21 next-session strategy checkpoint
- Latest work focus: strategy hypotheses and Binance market-data needs, per user's explicit prioritisation. Tax/jurisdiction research deferred, not removed from later live-readiness gates.
- Read STRATEGY_RESEARCH.md first, then fetch live main SHA and read status/register/evidence/log.
- Immediate next task: design the market-data manifest and verify one representative archive end-to-end (source path, checksum, schema, timestamp unit, first/last timestamps, gaps). No bulk dataset claims until this passes.
- Freeze S-01 through S-04 experiments before backtesting. No strategy is proven profitable or live-approved.


## 2026-10-21 — Locked master plan checkpoint
- Read PLAN_AND_PHASE_LOCK.md before selecting the next task. It is the default dependency-ordered roadmap; it does not mark any gate passed.
- Current immediate action: representative official Binance archive audit (BTCUSDT Spot 5m and matching USDⓈ-M Futures data if the exact artifact is available), with actual checksum/schema/timestamp/gap verification. If blocked, document the observed blocker and a verifiable zero-cost alternative.
- After the archive audit, freeze S-01 to S-04 preregistered experiments before any backtest.
- Continue respecting the current user priority: strategy/data now; tax/jurisdiction review later as a mandatory live gate. Never bypass product eligibility.
- At resume, fetch current main head and read back PLAN_AND_PHASE_LOCK.md, PROJECT_STATUS.md, RULES_AND_LOCKS.md, STRATEGY_RESEARCH.md, MARKET_DATA_MANIFEST_SPEC.md, SESSION_LOG.md and CHANGELOG.md.


## 2026-10-21 — Full AI requirements saturation checkpoint
- Read PLAN_AND_PHASE_LOCK.md as the master roadmap and PROJECT_BLUEPRINT.md as the enduring project specification.
- The plan now makes explicit: ten logical AI roles plus independent Safety Kernel; model selection after data and benchmark evidence; dynamic entries/exits/stops/targets/trailing and multiple entries bounded by aggregate risk; eight horizons; point-in-time top ten; BNB commission only when verified; zero-cost feasibility measured.
- At each substantive response, re-fetch live main, identify active phase/gate, check evidence and locks, do only the next safe task, then log and read back repository changes.
- Current phase: Phase 2 representative archive audit. No actual archive checksum/audit is verified. Do not jump to code or backtest.


## 2026-10-21 — Phase 2 retrieval blocker
## 2026-10-21 — Phase 2 archive retrieval blocker
- Attempted HEAD requests from the current execution container for candidate BTCUSDT Spot 5m and USDⓈ-M Futures daily archive URLs and companion `.CHECKSUM` URLs for 2026-10-20.
- All four attempts failed before receiving an HTTP response with `Temporary failure in name resolution`; the web retrieval tool also could not access the direct checksum URLs.
- This proves a current-environment retrieval blocker only. It does not prove the candidate archives exist or do not exist, and no archive bytes, checksum, schema, timestamp, row count, gap result or data-quality PASS is claimed.
- Created DATA_AUDIT_LOG.md with exact attempted URLs, observed errors, evidence boundaries and a reproducible zero-cost next route via a network-enabled user-owned runtime such as Colab.
- Phase 2 remains BLOCKED pending actual retrieval. No bulk download, strategy backtest, model training, paper run or live order was performed. Next: retrieve one real official artifact and its checksum, audit it end-to-end, then freeze S-01 to S-04 before any backtest.
