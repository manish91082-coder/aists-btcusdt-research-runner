# Project Status

Last updated: 2026-10-21
Status: RESEARCH-FIRST BLUEPRINT BASELINED; RESEARCH INCOMPLETE

## Current repository state
- Repository: manish91082-coder/aists-btcusdt-research-runner (rename deferred by user).
- Working/default branch: main.
- Pre-change main head verified before this blueprint update: db6fb812d911ded08f75923a57f22ea39f0611c0.
- Clean-slate commit: f52bac573c9509c71143158a7f609bd55a6a76bb.
- Previous snapshot branch: backup/pre-cleanup-2026-10-21-main-f2fcc6f, originally at f2fcc6f2e74dcd08e59cdcb811cd680d35fb1733.
- This checkpoint adds the blueprint, research workstreams, evidence source register, decision log and quality-audit checklist, and synchronises governance and continuity records.

## User requirements captured
Binance; Spot + Futures; long/short exposure; BNB fees wherever supported; AI-dynamic universe/strategy/indicator/entry/exit/stop/target/trailing choices; rolling high-volume top-ten universe; 5m/15m/1h/4h/8h/1d/1w/1M; longest verifiable historical data with ten-year target where possible; stated 10,000 USDT initial capital; zero-cost-first; evidence-based research before coding; no fake data, unsupported assertions or drift; GitHub is the project memory/continuity/log source.

## Work done in this update
- Drafted PROJECT_BLUEPRINT.md with system scope, ten proposed AI roles, deterministic Safety Kernel, multi-timeframe cadence, research methods, data controls, BNB/fee accounting, risk mathematics, dynamic exits and staged release gates.
- Added RESEARCH_REGISTER.md, EVIDENCE_REGISTER.md, DECISION_LOG.md and QUALITY_AUDIT.md.
- Recorded initial official-source findings: archive/checksum documentation, interval naming, BNB discount differences, Futures funding/commission categories, Spot Testnet reset limits, July 2017 venue launch constraint and India-specific product/tax verification gates.
- Updated README, status, memory, continuity, rules/locks, session log and changelog.

## Not done / not to imply completion
- No trading engine, strategy or model code written.
- No selected symbol's data has been downloaded or checksum-verified.
- No top-ten list chosen.
- No feature/strategy candidate empirically validated; no model trained.
- No backtest, walk-forward report, paper-trading report or exchange order test has run.
- No credentials created, funds moved, account settings changed, real order submitted or deployment enabled.
- User/account-specific Futures eligibility remains unresolved.
- No free always-on runtime has been proven to meet uptime and safety requirements.

## Next action
Work R02 and R03 first: current official Binance product/account/jurisdiction eligibility and applicable requirements; then exact per-symbol historic coverage, checksums, timestamp units and gap inventory. Do not start trading implementation until research and coverage gates pass.

## Verification rule
Use live main ref as authority. After the current write, re-fetch main, root listing and changed file contents. If a write/readback fails, record the failure rather than calling the update verified.

## 2026-10-21 strategy-focused checkpoint
- User reprioritised immediate work: defer tax/jurisdiction research for now and focus on strategies and Binance data needed to test them. Those topics remain later execution gates; no bypass is planned.
- Added STRATEGY_RESEARCH.md with 12 falsifiable strategy hypotheses, research order, minimum Binance data inventory, multi-timeframe causality rules, BNB commission accounting and test acceptance criteria.
- Official docs reviewed: Spot exchange information/current symbol rules and rate limits, Spot filters, USDⓈ-M Futures kline/market-data reference, and Binance public archives/checksums/timestamp notes.
- No strategy has been backtested, ranked by results, or approved. No data was downloaded or checksum-verified. Next task: data manifest and representative archive audit, then pre-register S-01 to S-04 experiments.


## 2026-10-21 — Master execution plan locked
- Added PLAN_AND_PHASE_LOCK.md as the binding default order of work, with 13 phases (0–12), exit gates, change control and immediate work queue.
- The plan consolidates the original scope: Binance Spot + Futures; Spot long/flat and eligible Futures long/short; up to 10 evidence-ranked liquid coins; 5m/15m/1h/4h/8h/1d/1w/monthly; longest verifiable history; AI-selected strategies/features/entries/exits/stops/targets/trailing; BNB commission payment where genuinely supported; 10,000 USDT as research/paper equity; zero-cost-first; research before code.
- Immediate next gate: download and validate a real representative official Binance archive (BTCUSDT Spot 5m plus matching Futures artifact where available), recording actual source, hashes, schema, timestamp units and data-quality findings. No audit pass is claimed yet.
- After the data audit, freeze S-01 through S-04 experiment protocols before any backtest.
- User's earlier instruction to defer tax/jurisdiction research remains active for the current strategy/data stage; it remains a mandatory later live-release gate, not waived.
- No strategy/backtest/model/paper run/live order is newly claimed. All live/execution locks remain.


## 2026-10-21 — Full requirement saturation and anti-drift audit
- Re-read the detailed user requirement against PROJECT_BLUEPRINT, PLAN_AND_PHASE_LOCK, STRATEGY_RESEARCH, MARKET_DATA_MANIFEST_SPEC and governance/continuity records.
- Expanded PLAN_AND_PHASE_LOCK.md with an explicit AI decision contract, ten logical AI roles, independent Safety Kernel, continuous multi-timeframe scanner semantics, dynamic stop/target/trailing and multiple-entry risk, zero-cost measurement, ten-year-history feasibility, fee accounting and per-response anti-drift audit.
- Linked the expanded plan from PROJECT_BLUEPRINT.md. The master plan remains the default ordered roadmap; no phase is passed by documentation alone.
- Verified strategy candidates remain hypotheses only. The representative archive audit is still not completed; no strategy/backtest/model/paper/live execution is claimed.
- Next action remains Phase 2: obtain and validate an actual official Binance archive with observed checksum/schema/timestamp/gap output. If blocked, preserve the exact blocker and investigate a verifiable zero-cost path.


## 2026-10-21 — Full requirement audit and anti-drift checkpoint
- Re-read the detailed user requirement against the blueprint, master phase lock, strategy dossier, data manifest and governance records.
- Expanded PLAN_AND_PHASE_LOCK.md with AI decision contract, ten logical AI roles plus independent Safety Kernel, multi-timeframe causality, dynamic position/exit rules, fee accounting, zero-cost feasibility and per-response anti-drift checks.
- Linked the expanded plan from PROJECT_BLUEPRINT.md. The roadmap is locked as the default sequence; documentation alone does not pass any phase.
- No representative archive audit, strategy/backtest/model/paper run or live order is newly claimed.
- Next task: Phase 2, verify an actual official Binance archive and its checksum/schema/timestamp/gap results; record blockers honestly.


## 2026-10-21 — Phase 2 archive retrieval attempt
## 2026-10-21 — Phase 2 archive retrieval blocker
- Attempted HEAD requests from the current execution container for candidate BTCUSDT Spot 5m and USDⓈ-M Futures daily archive URLs and companion `.CHECKSUM` URLs for 2026-10-20.
- All four attempts failed before receiving an HTTP response with `Temporary failure in name resolution`; the web retrieval tool also could not access the direct checksum URLs.
- This proves a current-environment retrieval blocker only. It does not prove the candidate archives exist or do not exist, and no archive bytes, checksum, schema, timestamp, row count, gap result or data-quality PASS is claimed.
- Created DATA_AUDIT_LOG.md with exact attempted URLs, observed errors, evidence boundaries and a reproducible zero-cost next route via a network-enabled user-owned runtime such as Colab.
- Phase 2 remains BLOCKED pending actual retrieval. No bulk download, strategy backtest, model training, paper run or live order was performed. Next: retrieve one real official artifact and its checksum, audit it end-to-end, then freeze S-01 to S-04 before any backtest.


## 2026-10-21 — Phase 2 audit runner prepared
- Added `tools/audit_binance_archive.py` to download one official Binance kline archive and companion checksum, calculate SHA-256, inspect ZIP/CSV schema, timestamp conventions, row order/gaps, OHLC/volume invariants, and perform bounded official API candle comparisons.
- Added `RUN_DATA_AUDIT.md` with a zero-cost Colab route and separate Spot/USDⓈ-M Futures commands. This is tooling preparation only: no archive has been downloaded or audited by this step.
- Phase 2 remains BLOCKED until actual report JSON and artifacts/evidence are returned and independently reviewed. No PASS or strategy performance claim.


## 2026-10-21 — Audit runner coverage hardening
- Hardened `tools/audit_binance_archive.py` to detect missing leading/trailing candles by checking expected UTC-day open timestamps for intervals that divide a day; report first/last event times now use minimum/maximum observed opens.
- This is a code change only. The script has not been executed against a downloaded Binance archive; Phase 2 remains BLOCKED until real artifacts and reports are reviewed.


## 2026-10-21 — Offline smoke-check workflow
Added GitHub Actions smoke checks for Python compilation, CLI help, and malformed-date rejection before network access. Workflow commit exists, but no successful run has been verified yet. These checks do not unblock Phase 2, which still requires real Spot and USDⓈ-M archive reports.


## 2026-10-21 — Phase 2 execution path
- Added manual GitHub Actions workflow `.github/workflows/phase2-binance-data-audit.yml` to run official Spot and USDⓈ-M Futures archive audits for a user-selected UTC date, symbol, and interval, then upload JSON reports and evidence artifacts.
- Runbook now points to this workflow as the preferred low-friction execution path.
- Workflow has been committed but not yet dispatched. No archive audit result exists from this workflow. Phase 2 remains BLOCKED until both actual reports are reviewed.

## 2026-10-21 — Audit status classification hardening
- Reviewed the representative archive runner and corrected API verification classification: a real API sample mismatch is FAIL; a temporary API/network verification problem is BLOCKED.
- Corrected overall gate precedence so a proven required-check FAIL cannot be hidden by another BLOCKED check. PASS is allowed only when every required check is PASS.
- Added seven unit tests for status classification and wired them into the offline smoke workflow; changed workflow path filters so changes under tests/ trigger the smoke checks.
- Re-fetched the runner, tests, workflow and audit log from main and confirmed the expected changes are present.
- Latest CI result for these newest commits has not yet been independently observed. No real Binance archive has been downloaded or checksum-verified. Phase 2 remains BLOCKED.
- Immediate next action remains: manually run the Phase 2 Spot + USDⓈ-M workflow, retrieve both reports, review evidence. Do not backtest or freeze S-01 to S-04 until this gate is resolved.

## 2026-10-21 — Per-response plan audit and continuity lock
- User instruction: check the complete locked plan every response, preserve continuity, and prevent scope drift.
- Process lock recorded in `RULES_AND_LOCKS.md` and `CONTINUITY.md`: inspect live repository state and the full master plan before selecting the next action; verify the active phase, exit gate, evidence, blockers, and downstream locks; execute only the next safe step; log material work; read back all changed files; report verification limits honestly.
- Current phase: Phase 2 representative Binance archive audit. The manual Spot + USDⓈ-M workflow has input preflight validation, but no verified dispatch or actual archive reports are present in this checkpoint. Latest CI result is also not independently verified here.
- No phase advancement. No data-quality PASS, backtest, model training, paper run, live order, or deployment is claimed.
- Exact next action: execute the manual Phase 2 workflow, retrieve both market JSON reports/evidence, independently review them, and only then decide whether the gate passes or needs blocker remediation.

## 2026-10-21 — Phase 2 parser compatibility hardening
- Code review identified that a 12-column header row, if present in an archive, would be misclassified as malformed data.
- Added exact first-nonempty-row header recognition and a `csv_header_present` report field; added four offline unit tests.
- Commits: runner `5369263058971e14fcae4db438a1e205cbb2c7ce`; tests `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- Verification state: repository writes acknowledged; CI for these changes not yet independently verified. No real archive report/checksum audit exists. Phase 2 remains BLOCKED; strategy backtesting and downstream gates remain locked.
- Exact next action: verify the smoke CI result, then run the manual Phase 2 workflow for BTCUSDT Spot 5m and USDⓈ-M Futures 5m, preserve both reports/artifacts, and independently review them.
