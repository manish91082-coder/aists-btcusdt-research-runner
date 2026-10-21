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


## 2026-10-21 — Audit runner handoff
- Current environment could not resolve `data.binance.vision`; the blocker is recorded in `DATA_AUDIT_LOG.md`.
- To move forward without inventing evidence, `tools/audit_binance_archive.py` and `RUN_DATA_AUDIT.md` provide a zero-cost, network-enabled Colab route. Fetch live `main`, review both files, run separate Spot and USDⓈ-M audits, then request the JSON reports and any failure output for independent review.
- Phase 2 is still BLOCKED until real archive bytes, checksum results and data-quality outputs are observed. Do not start strategy backtests before the representative data gate and S-01 to S-04 preregistration.


## 2026-10-21 — Audit runner coverage hardening
- Runner now checks UTC-day expected opens for intervals that tile a day, detecting missing first/last candles in addition to gaps between observed rows. Reported first/last timestamps use min/max observed open times.
- This improvement has not been exercised on real Binance archive bytes. Phase 2 remains BLOCKED until the documented Colab run produces reports and they are independently reviewed.

## 2026-10-21 Phase 2 continuity checkpoint — audit runner hardening
- Current focus remains the locked Phase 2 representative Binance archive audit, not strategy implementation or backtesting.
- Latest changes: API sample mismatch -> FAIL; API/transport verification issue -> BLOCKED; overall proven FAIL takes precedence over BLOCKED; PASS requires every required check to PASS.
- Seven classification unit tests are committed and included in the smoke workflow. Workflow path filters include `tests/**`.
- Current CI result for the latest commits has not yet been independently verified. Do not describe these tests as passing until actual output is observed.
- No real Spot or USDⓈ-M archive has been downloaded or checksum-verified. Phase 2 is BLOCKED.
- Immediate next action: user must manually dispatch [Phase 2 Binance archive audit](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/workflows/phase2-binance-data-audit.yml), download the artifact, and provide both `.report.json` files for review. Do not proceed to S-01..S-04 backtesting before the gate is resolved.

## 2026-10-21 — Per-response plan and continuity lock
- User explicitly requires the plan to be checked end-to-end on EVERY response, with no drift and no continuity break. This is a binding process lock, not a request for reassurance alone.
- Mandatory per-response sequence: (1) restate/check the final mission and latest request; (2) fetch live main/current changed files; (3) read the full `PLAN_AND_PHASE_LOCK.md`; (4) read status, rules/locks, continuity, latest session/audit logs, and the evidence directly relevant to the active gate; (5) identify phase, exit criteria, actual evidence, blockers, and prohibited downstream work; (6) perform the next safe action rather than merely repeat instructions; (7) update durable records for material work; (8) read back every changed file and verify branch state; (9) report what changed, what was verified, what remains unverified, and the exact next action.
- Current active gate remains Phase 2: actual official BTCUSDT Spot 5m and corresponding USDⓈ-M Futures archive/checksum reports. The manual workflow is prepared and input-validated but has not been dispatched in the verified evidence available here. The default date is only a candidate.
- Do not start backtesting, model training, paper trading, live trading, bulk data collection, or top-10 claims ahead of their dependency gates. S-01 to S-04 protocols must be frozen before any backtest, after the representative data gate is resolved.
- Continuity source of truth is live GitHub state plus primary evidence, not a promise that chat memory alone is permanent.

## 2026-10-21 — Resume checkpoint after optional-header hardening
- Live main was re-read before work; the locked mission and full phase plan remain unchanged.
- Active gate: Phase 2 representative official Binance archive audit. No real archive/checksum report has passed.
- Code review added exact optional 12-column kline header detection on the first non-empty CSV record and a `csv_header_present` report field. Four unit tests cover supported header spellings, ordinary data, and invalid header width.
- Commits: runner `5369263058971e14fcae4db438a1e205cbb2c7ce`; tests `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- Status/log records are being synchronised. CI for the latest change remains unverified; do not treat code-write acknowledgement as test success.
- Next: check current smoke CI evidence if available, then manually dispatch the Phase 2 workflow and inspect both Spot and USDⓈ-M reports. No backtest until the representative data gate and S-01..S-04 preregistration gate are satisfied.

## 2026-10-21 — CI evidence checkpoint
- Verified smoke run [39488166620](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39488166620) succeeded on test commit `d0ec62150078b6cf210609dfff24bc6bbdbff579`; its job steps include compilation, unit tests, CLI help and invalid-date rejection.
- This does not verify any real Binance archive, checksum or API spot-check.
- The latest 100 workflow runs inspected did not show a Phase 2 manual audit run. Active gate remains Phase 2. Next action: user dispatches the manual workflow and shares both Spot/Futures JSON reports plus evidence artifact for independent review.

## 2026-10-21 — Resume verification: no Phase 2 run found
- Re-read live `main` and the locked plan/rules/status/continuity/runbook/audit log/runner/tests/workflow. Current main ref is `ba547c6e18db46d4032757dc3ee4af89099c40bd`.
- Smoke CI success remains verified at [run 39488166620](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39488166620).
- Latest 100 workflow runs inspected: no Phase 2 Binance archive audit run. Current GitHub tool integration exposes no workflow-dispatch action, so manual dispatch is still a user-side dependency.
- Active gate unchanged: Phase 2 representative real-data audit. Next: dispatch workflow manually, share both JSON reports/artifact, independently review before advancing. Do not backtest yet.

## Current checkpoint — 2026-10-21
- Main head before continuity sync: ed008bac70e7331e8b73d452fed08471b044d2a1.
- S01_S04_PREREGISTRATION.md now freezes the first four BTCUSDT 5m pilot protocols under D-018, using the documented blocker contingency to avoid an idle loop.
- Phase 2 remains BLOCKED. No real Spot/Futures archive audit has been verified and no backtest is authorised.
- Next action: run the existing Phase 2 workflow once, provide the artifact, and independently review both reports. Do not run backtests until exact data and cost gates pass.

## 2026-10-21 — Latest audit-trigger checkpoint
- Main includes the push-trigger workflow adjustment and marker `tools/phase2-audit-trigger.txt`, but the latest Actions query showed no Phase 2 audit run after the marker commit.
- Automatic dispatch is unverified. Do not treat this as an audit result; Phase 2 remains BLOCKED.
- Next: manually dispatch the existing Phase 2 workflow once and inspect the Spot/Futures artifact. Avoid more marker commits or repeated trigger experiments.

## 2026-10-21 — Verified checkpoint: no-loop protocol adopted
- Live Phase 2 run [39496937998](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496937998) completed; Spot official API samples PASS via `https://data-api.binance.vision/api/v3/klines`; USDⓈ-M Futures API samples BLOCKED (primary HTTP 451, numbered hosts HTTP 202). Artifact [12297349529](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496937998/artifacts/12297349529). The daily/monthly consistency checks passed but are not independent evidence.
- Bounded official-documentation review did not establish a separate documented public USDⓈ-M Futures REST base for klines. No repeat audit was launched because no material code/input/environment change occurred.
- Durable process lock created: `EFFICIENCY_NO_DRIFT_PROTOCOL.md`; `RULES_AND_LOCKS.md` R-035–R-037; `PLAN_AND_PHASE_LOCK.md` G10. Every response checks mission/phase/gate and live main; evidence collection is targeted; repeated audits require a material reason; no access restriction bypass; unchanged long files are not repeatedly fetched without cause.
- Phase 2 remains BLOCKED. Next decision only: whether an official Futures WebSocket market-data candle check is allowed to substitute for the locked REST comparison. Do not implement that substitution without an explicit protocol decision. No backtest, training, paper trading, live order or deployment.

## 2026-10-21 — Checkpoint after one-pass alternative review
- Official-documentation search did not establish a supported historical USDⓈ-M Futures WebSocket kline request suitable to verify the same 2026-10-15 sample. REST gate remains locked; no substitution or repeat audit.
- Active Phase 2 blocker: Futures official API returns HTTP 451 on primary and HTTP 202 on numbered hosts. Spot passes through official Binance market-data API.
- Resume condition: new official documentation or a materially different compliant execution environment. Then perform one targeted check only. Until then, do not cycle endpoints, rerun unchanged audits, or start downstream backtests/training/paper trading/live deployment.


## 2026-10-21 — GitHub-only execution route reaffirmed
- User explicitly instructed that project work and execution remain on GitHub, without Colab or Google Drive.
- The repository already has a manual GitHub Actions Phase 2 workflow. The current chat GitHub connector can read repository state and workflow evidence but has no workflow-dispatch action, so I must not claim to have started the workflow from this session.
- The previous assistant's Colab/Drive JSON-job route was unnecessary and is withdrawn. The authoritative next step is one manual dispatch of the existing Phase 2 workflow from GitHub Actions UI, then review the Spot/Futures reports and artifact.
- No new audit was run; Phase 2 remains BLOCKED until actual reports satisfy the gate. Do not add marker commits or repeat unchanged checks.


## 2026-10-21 — Archive-first ingestion checkpoint
- Adopted official monthly Spot and USDⓈ-M Futures archives as the primary historical-data source. REST API access is optional diagnostic evidence, not a prerequisite for archive validation.
- Read `HISTORICAL_DATA_INGESTION_SUBTASKS.md` for HD-01 through HD-10.
- Pilot: BTCUSDT, 2026-09, 5m; expected 8,640 candles per market if full month. Validator, tests, manual workflow and runbook are committed.
- Next: run the workflow in GitHub Actions UI and inspect both JSON reports/artifact. The chat connector cannot dispatch workflows. Until then Phase 2 remains BLOCKED.
- Raw data is not committed to Git; Actions artifacts expire after 14 days. Binance-only history does not reach 10 years as of 2026-10.


## 2026-10-21 — User clarified final universe and capital realism
- Target: dynamically selected Top 10 by verified real trading volume, not a hardcoded list. BTCUSDT is only the archive pipeline pilot.
- Added `TOP10_VOLUME_UNIVERSE_SPEC.md` and linked its requirements into the historical ingestion plan.
- Separate Spot USDT and USDⓈ-M USDT perpetual universes; rank eligible symbols monthly using median turnover from the prior 30 completed UTC daily candles, with point-in-time membership and no future-volume leakage.
- Use real official market data and realistic costs. 10,000 USDT remains research/paper equity only; user has not authorized live-money execution.
- Next: the monthly archive pilot remains the immediate gate. After pilot and older-month check, implement/verify daily quote-turnover semantics and build the eligible-symbol inventory before calculating Top 10. No Top-10 results claimed yet.


## 2026-10-21 — New-thread continuity checkpoint
- Added `NEW_CHAT_CONTINUITY_PROMPT.md`, a copy-ready handoff with mission locks, verified checkpoint, repository links, dependency order, no-drift protocol, and required response format.
- Monthly archive regression-test change is on main at commit `9ff54223401c20cb4e923650a3d1f4f4f41e986a`; smoke run `39565549581` succeeded. This is code/test CI evidence only, not proof that real market archives pass.
- Active gate remains HD-03: run and review the official monthly BTCUSDT 5m Spot + USDⓈ-M Futures archive pilot for 2026-09. No market-data pass or backtest is claimed.
- New thread must verify live main and current reports rather than trusting this checkpoint blindly. See `NEW_CHAT_CONTINUITY_PROMPT.md`.
