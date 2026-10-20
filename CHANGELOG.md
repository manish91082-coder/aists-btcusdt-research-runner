## 2026-10-21 — Market-data manifest specification
- Added MARKET_DATA_MANIFEST_SPEC.md defining dataset provenance, checksum, schema, timestamp, gap and sample-API comparison fields.
- Specified BTCUSDT Spot 5m and matching USDⓈ-M Futures as the proposed representative audit target; no data download or checksum run is claimed.
- Linked the new document from README.

## 2026-10-21 — Strategy research dossier and Binance data requirements
- Added STRATEGY_RESEARCH.md with 12 falsifiable strategy hypotheses and a dependency-aware research order.
- Recorded official API/archive sources for Spot exchangeInfo and rate limits, symbol filters, USDⓈ-M Futures klines, archive intervals, checksums and timestamp-unit handling.
- User priority recorded: strategy/data research now; tax/jurisdiction review deferred to later stage, not waived for eventual live execution.
- No empirical strategy result, backtest, data download/checksum run, model training or live trade is claimed.

# Changelog

Newest first. Repository change log is not a performance claim.

## 2026-10-21 — Research-first blueprint baseline
- Added PROJECT_BLUEPRINT.md: user requirements, ten proposed AI roles, Safety Kernel, data feasibility, timeframes, fees/BNB, risk mathematics, validation and release gates.
- Added RESEARCH_REGISTER.md, EVIDENCE_REGISTER.md, DECISION_LOG.md and QUALITY_AUDIT.md.
- Updated README, PROJECT_STATUS, PROJECT_MEMORY, CONTINUITY, RULES_AND_LOCKS and SESSION_LOG.
- Registered official-source findings and limits for archives/checksums, fee discount differences, Futures funding, Spot Testnet resets, Binance's July 2017 launch and India product/tax review.
- No trading code, dataset run, model training, backtest, paper-trading session, live order or deployment was performed.

## 2026-10-21 — Clean slate and continuity foundation
- Created a clean-slate main commit while preserving Git history and the backup branch.
- Added initial README, project status/memory/continuity, rules/locks, session log and changelog.
- Repository rename remains pending; current name remains unchanged.

## 2026-10-21 — Master execution plan and phase lock
- Added PLAN_AND_PHASE_LOCK.md with the complete ordered phases 0–12, deliverables, exit gates, current work queue and change-control protocol.
- Locked the default phase sequence in RULES_AND_LOCKS.md and synchronised status, continuity and session logs.
- Next gate is a real representative Binance archive audit. No data audit, strategy result or trading readiness is claimed.


## 2026-10-21 — Full AI requirement and anti-drift expansion
- Expanded PLAN_AND_PHASE_LOCK.md with AI autonomy, ten logical roles plus independent Safety Kernel, dynamic multi-timeframe and position management, zero-cost feasibility, phase traceability and per-response anti-drift audit.
- Linked the locked roadmap from PROJECT_BLUEPRINT.md and synchronised status, continuity, governance and session history.
- Documentation read-back is being verified; no archive audit or strategy performance is implied.


## 2026-10-21 — Phase 2 archive retrieval blocker
## 2026-10-21 — Phase 2 archive retrieval blocker
- Attempted HEAD requests from the current execution container for candidate BTCUSDT Spot 5m and USDⓈ-M Futures daily archive URLs and companion `.CHECKSUM` URLs for 2026-10-20.
- All four attempts failed before receiving an HTTP response with `Temporary failure in name resolution`; the web retrieval tool also could not access the direct checksum URLs.
- This proves a current-environment retrieval blocker only. It does not prove the candidate archives exist or do not exist, and no archive bytes, checksum, schema, timestamp, row count, gap result or data-quality PASS is claimed.
- Created DATA_AUDIT_LOG.md with exact attempted URLs, observed errors, evidence boundaries and a reproducible zero-cost next route via a network-enabled user-owned runtime such as Colab.
- Phase 2 remains BLOCKED pending actual retrieval. No bulk download, strategy backtest, model training, paper run or live order was performed. Next: retrieve one real official artifact and its checksum, audit it end-to-end, then freeze S-01 to S-04 before any backtest.


## 2026-10-21 — Phase 2 audit runner and runbook
- Added `tools/audit_binance_archive.py` and `RUN_DATA_AUDIT.md` to enable reproducible official archive/checksum and data-quality checks in a network-enabled zero-cost runtime.
- Tooling creation is not an archive audit result. Phase 2 remains blocked until actual downloaded artifacts and report JSON are reviewed.


## 2026-10-21 — Audit runner coverage hardening
- Added UTC-day expected-open coverage checks to detect missing leading/trailing candles and made first/last event timestamps independent of row order. This is unexecuted tooling, not a data audit result.

## 2026-10-21 — Per-response plan audit lock
- Recorded the user's strict requirement to review the complete master plan and live project state before every response/action.
- Synchronized anti-drift and continuity instructions across rules, continuity, project status, memory and session log.
- This is a process/governance update only. It does not pass Phase 2 or establish a data audit, CI result, backtest, model training, paper run or live-trading readiness.
