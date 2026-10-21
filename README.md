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


## Mandatory execution order
Read [PLAN_AND_PHASE_LOCK.md](PLAN_AND_PHASE_LOCK.md) before any new task. It contains the locked phase sequence, AI decision contract, logical brain roles, exit gates, change control and anti-drift protocol. [PROJECT_BLUEPRINT.md](PROJECT_BLUEPRINT.md) remains the full durable project specification. Documentation is not implementation evidence.


## Current phase status (2026-10-21)
- Official daily archive integrity/candle checks and Spot API sample checks passed in a prior GitHub Actions run. The former Futures REST comparison was blocked, but the historical-data gate has since been redesigned to use official monthly archives as primary evidence.
- The monthly archive validator and manual GitHub Actions pilot are implemented, but the September 2026 BTCUSDT 5m pilot has NOT been run/reviewed from this chat. Phase 2 remains BLOCKED until both Spot and USDⓈ-M Futures reports pass.
- See [Historical Data Ingestion Subtasks](HISTORICAL_DATA_INGESTION_SUBTASKS.md), [Monthly archive runbook](RUN_DATA_AUDIT.md), and [Data Audit Log](DATA_AUDIT_LOG.md). No Colab or Drive workflow is part of the project.

## Dynamic Top-10 universe
- [Top-10 Volume Universe Specification](TOP10_VOLUME_UNIVERSE_SPEC.md) freezes a dynamic, point-in-time selection policy using verified volume data. Spot USDT pairs and USDⓈ-M USDT perpetuals are ranked separately.
- BTCUSDT is a pipeline pilot only, not a hardcoded final universe. No Top-10 ranking has been calculated or claimed yet.
- Research capital remains 10,000 USDT paper equity only. Real data and realistic costs are required, but live orders/credentials/deployment remain locked.

## Preregistered strategy protocols
- [S-01 to S-04 Experiment Preregistration](S01_S04_PREREGISTRATION.md) freezes the first four research pilots before performance results. It is not a backtest report.
- The representative Spot/Futures archive audit remains BLOCKED; do not run experiments until the exact data and cost gates pass.
