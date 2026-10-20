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
