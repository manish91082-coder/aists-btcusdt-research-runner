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

## 2026-10-21 — Phase 2 optional kline CSV header handling
- Hardened the archive auditor to recognise the exact 12-column header on the first non-empty record, if present, and report `csv_header_present`.
- Added four offline unit tests for supported header forms and false-positive rejection.
- Commits: runner `5369263058971e14fcae4db438a1e205cbb2c7ce`; tests `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- CI and real Spot/Futures archive audit remain unverified; Phase 2 is still blocked.

## 2026-10-21 — Offline smoke CI verified for optional-header tests
- GitHub Actions run [39488166620](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39488166620) succeeded on test commit `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- Verified checks: Python compilation, unit tests, CLI help and malformed-date rejection. Real Binance archive audit remains unverified and Phase 2 remains blocked.

## 2026-10-21 — Phase 2 state rechecked
- Revalidated the live main ref and inspected the latest workflow runs; no manual Phase 2 archive audit run was present in the latest 100.
- This is a status/evidence checkpoint only. The real-data audit remains blocked pending manual workflow dispatch and report review.

## 2026-10-21 — S-01 to S-04 preregistration
- Added S01_S04_PREREGISTRATION.md and D-018 under the documented Phase 2 blocker contingency.
- This freezes research definitions only. No empirical result is claimed; the real-data audit remains BLOCKED.


## 2026-10-21 — Correct execution path: GitHub Actions only
- Corrected the handoff: use the existing Phase 2 GitHub Actions workflow, not Colab/Google Drive. The current connector lacks workflow-dispatch capability; no run is claimed. Phase 2 remains BLOCKED pending the workflow artifact and independent report review.


## 2026-10-21 — Removed marker-based Phase 2 triggering
- Made the Phase 2 archive workflow manual-dispatch-only and removed the obsolete marker file. This aligns execution with the runbook and anti-loop protocol; no audit was launched by this documentation/configuration change. Phase 2 remains BLOCKED.


## 2026-10-21 — Reconciled stale phase-status summaries with latest evidence
- Updated the master plan and research register to distinguish frozen S-01 to S-04 protocols from unrun backtests, and to reflect the latest Phase 2 run: archive-integrity/candle-quality checks pass, Spot API samples pass, Futures API verification remains blocked.
- This is a documentation consistency correction only. It does not pass Phase 2 or authorise backtesting.


## 2026-10-21 — Monthly archive-first historical data pilot
- Added monthly archive validator, unit tests, and manual GitHub Actions workflow for one bounded month of BTCUSDT Spot + USDⓈ-M Futures.
- Added HD-01–HD-10 subtask plan and updated Phase 2 to accept validated official monthly archives without requiring REST API access.
- Updated smoke CI to compile and check CLI help for the new validator.
- Pilot has not been run from chat; Phase 2 remains BLOCKED and no backtests are unlocked.


## 2026-10-21 — New-thread continuity handoff
- Added `NEW_CHAT_CONTINUITY_PROMPT.md` as the canonical copy-ready prompt for a fresh thread.
- Monthly archive test hardening committed at `9ff54223401c20cb4e923650a3d1f4f4f41e986a`; smoke run `39565549581` succeeded. No real archive result is inferred from CI.
- HD-03 remains blocked pending actual 2026-09 BTCUSDT 5m Spot and USDⓈ-M Futures archive reports.

## 2026-10-21 — Continuity reconciliation
- Clarified the current authoritative gate in status, continuity and session records: HD-03 monthly archive pilot for September 2026 BTCUSDT 5m Spot + USDⓈ-M Futures. Older daily/API-required and Colab/Drive notes remain historical and are superseded by the monthly-archive-first GitHub Actions route.
- Reconfirmed smoke run 39565549581 is CI-only, not market-data acceptance. The pilot remains unrun/unreviewed from this chat; no backtest or downstream execution is unlocked.
- No workflow dispatch is claimed because the available connector does not expose that action. The exact next step remains manual dispatch of the existing workflow and review of both reports and the artifact.

## 2026-10-21 — Monthly workflow input-safety hardening
- Removed direct shell-command interpolation of manually supplied month/interval inputs in the monthly archive workflow; passed values via environment variables and quoted shell expansions.
- Smoke CI is expected from the existing workflow path filter but has not yet been verified. No real archive audit or Phase 2 gate pass is claimed.
