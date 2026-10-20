# Full AI Crypto Trading Bot 21 OCT

This repository is the durable source of truth for requirements, research, evidence, decisions, rules/locks, status, continuity and session history.

## Current stage

**Research first. No trading implementation is authorised yet.** The target is an AI-assisted Binance Spot + Futures system with long/short exposure, dynamic multi-timeframe decisions, BNB fee payment where supported, and evidence-backed portfolio risk controls. There is no claim of trading performance or live readiness.

## Start here
- [Market Data Manifest Specification](MARKET_DATA_MANIFEST_SPEC.md) — schema, checksum, timestamp, gap and validation requirements before data can be used in strategy tests.
- [Strategy Research Dossier](STRATEGY_RESEARCH.md) — falsifiable strategy hypotheses, Binance data requirements, cost accounting and test protocol. None is claimed profitable until tested.
- [Master Project Blueprint](PROJECT_BLUEPRINT.md) — full requirements, proposed ten AI roles, risk math, data, testing and staged implementation.
- [Project Status](PROJECT_STATUS.md) — last verified state and next action.
- [Project Memory](PROJECT_MEMORY.md) — durable user requirements and confirmed facts.
- [Decision Log](DECISION_LOG.md) — user-confirmed versus proposed/open decisions.
- [Research Register](RESEARCH_REGISTER.md) — research workstreams and acceptance criteria.
- [Evidence Register](EVIDENCE_REGISTER.md) — official source links, supported findings and limits.
- [Quality Audit](QUALITY_AUDIT.md) — source, data, leakage, mathematical and safety checks.
- [Rules and Locks](RULES_AND_LOCKS.md) — constitution and non-negotiable controls.
- [Continuity Protocol](CONTINUITY.md) — resume instructions after context loss or thread changes.
- [Session Log](SESSION_LOG.md) — dated work and verification record.
- [Changelog](CHANGELOG.md) — repository changes.

## Non-negotiable process

At each session, fetch the live GitHub main head and read the status/continuity/governance documents. Research precedes code. After substantive work, synchronise applicable documents, commit the checkpoint and read back GitHub state to verify it. Finding a source is not proof of a broader claim; preserve evidence limits. AI cannot override the independent Safety Kernel. This document does not authorise live trading.

## Master execution plan
- [Master Execution Plan and Phase Lock](PLAN_AND_PHASE_LOCK.md) — binding default roadmap, numbered phases 0–12, phase exit gates, change control and the next verified action. A written plan is not evidence that any phase passed.
