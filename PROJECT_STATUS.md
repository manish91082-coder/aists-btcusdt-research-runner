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

## 2026-10-21 — Smoke CI verified after parser hardening
- Verified GitHub Actions smoke run [39488166620](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39488166620) succeeded for test commit `d0ec62150078b6cf210609dfff24bc6bbdbff579`. It includes compilation, unit tests, CLI help and malformed-date preflight.
- This is offline CI evidence only; it is not a real Binance archive audit.
- Latest 100 repository workflow runs inspected did not show a `Phase 2 Binance archive audit` run. Phase 2 remains BLOCKED pending manual dispatch and independent review of both Spot and USDⓈ-M JSON reports.

## 2026-10-21 — Revalidated current gate and workflow state
- Re-fetched the live `main` ref: `ba547c6e18db46d4032757dc3ee4af89099c40bd`. Re-read the master phase plan, rules, continuity, audit runbook/log, runner, tests and both relevant workflows.
- Latest verified offline smoke run remains successful: [39488166620](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39488166620), on test commit `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- Inspected the latest 100 workflow runs; none matched the Phase 2 Binance archive audit workflow. Available GitHub connector actions are read-oriented for workflow state and do not expose workflow dispatch, so I did not claim or simulate a run.
- Phase 2 remains BLOCKED. Exact next action remains manual dispatch of the existing workflow and review of both real Spot and USDⓈ-M JSON reports plus evidence artifact. No backtest or downstream gate is authorised.

## 2026-10-21 — S-01 to S-04 protocol status
- Added S01_S04_PREREGISTRATION.md; the first four BTCUSDT 5m pilot protocols and bounded sensitivity grids are frozen before any results.
- D-018 records the workflow-dispatch limitation as RESEARCH-OPEN. Phase order is unchanged and the data gate is not waived.
- Phase 2 remains BLOCKED: no real archive/checksum/API reports have been independently reviewed. No backtest, model training, paper run, live order or deployment has occurred.

## 2026-10-21 — Automated audit-trigger attempt
- Existing Phase 2 workflow now includes a narrowly path-filtered push trigger and default input fallbacks; marker file `tools/phase2-audit-trigger.txt` was committed to main to attempt a one-time run.
- After the marker commit, no Phase 2 audit run appeared in the latest 100 Actions runs. Automatic triggering is unverified; no audit artifact was produced/observed.
- Phase 2 remains BLOCKED. Avoid further trigger commits. Next step is one manual dispatch of the existing workflow and independent review of both market reports.


## 2026-10-21 — Phase 2 diagnostic result verified
- Latest Phase 2 run reviewed: [39495863321](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39495863321); evidence artifact [12298865023](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39495863321/artifacts/12298865023).
- Completed-month diagnostic selection is fixed. On 2026-09-15, Spot and USDⓈ-M Futures daily archives each matched their official monthly archive exactly after both CHECKSUM files passed; each daily 5m file had 288 candles. This is same-publisher consistency evidence only.
- Main audit date remains 2026-10-15. Both markets' daily archive checksum/ZIP/schema/candle-quality checks passed, but Spot API checks returned HTTP 451 on all five official endpoints; Futures primary returned HTTP 451 and numbered endpoints HTTP 202. API checks are BLOCKED, so overall Phase 2 enforcement correctly failed.
- Gate status: BLOCKED. No backtest, model training, paper trading, live order or deployment has occurred. Next research action is to resolve an accepted official API candle verification path within the allowed environment or explicitly document a protocol-approved alternative; do not waive the gate based solely on daily/monthly archive agreement.

## 2026-10-21 — Official Spot API endpoint coverage extended
- Added documented Binance Spot alternatives `api-gcp.binance.com` and `data-api.binance.vision/api/v3/klines` to the representative audit runner's API candidates; added offline unit tests for candidate policy.
- Commits: `5354bc1cc0f6df19a1b5ec63b5dc49b87771d986` (runner), `707b294c8d5279b40d44c1119795b8909013072c` (tests), audit-log checkpoint `a0d6ffe33832b27662f5f984c7ee4d88b143062a`.
- The latest observed smoke run `39496780166` was QUEUED when checked, so tests are not yet verified passing. Check both the smoke run and the push-triggered Phase 2 run before interpreting results.
- This is a code/test path improvement only. It does not override HTTP 451, does not bypass regional restrictions, and does not change the required gate. Phase 2 remains BLOCKED pending valid official API candle responses for both Spot and USDⓈ-M Futures.

## 2026-10-21 — Spot API check now passes; Futures remains blocked
- Phase 2 run [39496763403](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496763403) verified the updated Spot candidate path with `official_api_spot_check: PASS`. USDⓈ-M Futures remained `BLOCKED` (HTTP 451 primary, HTTP 202 numbered hosts), so Phase 2 is not passed.
- A newly added test initially failed due to an overly strict hostname assertion; after correcting it, smoke run [39496890235](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496890235) passed.
- Runner now records the exact API endpoint used for every successful sample to improve source provenance. Latest runner commit `3ce2c21e4857b01875127c8c2f55e669a2eed12a`; smoke run [39496938021](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496938021) and Phase 2 run [39496937998](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496937998) were queued when checked.
- Next: inspect both latest runs and the new report's recorded API host. Phase 2 stays BLOCKED until official Futures candle verification succeeds or an explicit protocol-approved alternative is recorded. No downstream trading research or execution has been unlocked.

## 2026-10-21 — Anti-loop protocol active; Phase 2 Futures blocker bounded
- Latest decisive run [39496937998](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496937998) is complete: Spot API check PASS via official `data-api.binance.vision`; Futures API check BLOCKED (primary HTTP 451, numbered hosts HTTP 202). Artifact [12297349529](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496937998/artifacts/12297349529).
- One bounded official-documentation review did not establish a separate documented public USDⓈ-M Futures REST base for klines beyond the documented `fapi.binance.com` base. No endpoint cycling or repeat audit was launched because neither code nor environment had materially changed.
- Added `EFFICIENCY_NO_DRIFT_PROTOCOL.md`; added R-035 to R-037 in `RULES_AND_LOCKS.md`; added G10 to `PLAN_AND_PHASE_LOCK.md`. This requires one decision-focused evidence pass, limits reruns to material reasons, and prohibits bypassing HTTP 451/access restrictions.
- Current gate: Phase 2 BLOCKED. Next action: if needed, make one explicit protocol decision on whether official USDⓈ-M Futures WebSocket market-data verification can satisfy the existing REST comparison requirement; until approved, do not change the verifier or waive the gate. No backtest, training, paper trading, live order or deployment has occurred.

## 2026-10-21 — WebSocket alternative check closed; no rerun
- One bounded official-doc search did not establish a documented historical USDⓈ-M Futures WebSocket kline request that reproduces the audit's 2026-10-15 samples. The REST gate is unchanged; no speculative substitute was implemented.
- Phase 2 remains BLOCKED: Spot official API check passes; Futures official API verification remains blocked (HTTP 451 primary, HTTP 202 numbered hosts).
- Next action is event-driven, not another loop: resume only if new official documentation for a permitted historical candle endpoint or a compliant runtime/environment becomes available. Then run one targeted verification. No backtest, training, paper trading, live order or deployment.


## 2026-10-21 — Execution route corrected to GitHub-only
- User explicitly reaffirmed that project work must stay on GitHub; Colab/Google Drive are not to be used for the next execution step.
- Repository audit confirmed the existing manual GitHub Actions workflow and GitHub-only artifact path. The session's GitHub connector is read-only for workflow dispatch, so the workflow cannot be started from this chat; this is a specific tool boundary, not a reason to move execution to Colab.
- Corrected RUN_DATA_AUDIT.md to make GitHub Actions the sole supported runbook and clarified the README reference. No data audit was run and Phase 2 remains BLOCKED.
- Next action: start the existing Phase 2 workflow once from GitHub Actions UI, then review both reports and artifact. No marker commits, repeated audits, Colab or Drive steps.


## 2026-10-21 — Manual-only Phase 2 workflow lock
- Repository audit found a stale push-path trigger and marker file alongside the documented manual-dispatch procedure. Removed the marker-based/push-trigger route to prevent unintended or repetitive real-data audits on code pushes.
- Phase 2 workflow now starts only through its existing GitHub Actions `workflow_dispatch` input form. This session cannot dispatch it through the available connector. No archive audit was run; Phase 2 remains BLOCKED.


## 2026-10-21 — Monthly archive-first ingestion
- User suggested Binance monthly archives processed in GitHub chunks; adopted official monthly Spot and USDⓈ-M Futures archives as the primary historical source. API access is not a prerequisite for historical archive validation.
- Added `tools/audit_binance_monthly_archive.py`, unit tests, manual workflow `.github/workflows/monthly-binance-history-chunk.yml`, and HD-01–HD-10 in `HISTORICAL_DATA_INGESTION_SUBTASKS.md`.
- Pilot parameters: BTCUSDT, September 2026, 5m; expected 8,640 rows per product for full-month coverage.
- IMPLEMENTED, NOT RUN from this chat. The available connector cannot dispatch workflows. Phase 2 remains BLOCKED until both real reports pass and are inspected.
- Raw files stay out of Git history; Actions artifact retention is 14 days. Binance launched in 2017, so Binance-only data cannot provide 10–15 years as of 2026.


## 2026-10-21 — Dynamic Top-10 volume requirement locked
- User clarified the final research target must use the Top 10 coins/contracts by real trading volume and real market capital conditions, not an arbitrary hardcoded list.
- Added `TOP10_VOLUME_UNIVERSE_SPEC.md`: separate Spot USDT pairs and USDⓈ-M USDT perpetual rankings, using the median quote turnover across 30 completed daily candles at each monthly point-in-time rebalance. This prevents a single noisy 24h spike and avoids future-volume leakage.
- Eligibility requires verified product semantics, 30 completed observations, listing/status evidence, and documented exclusions. Stablecoin-to-stablecoin, leveraged and synthetic/tokenized products are excluded from the initial universe.
- BTCUSDT remains only the archive pipeline pilot, not the assumed final Top-10 member.
- Capital clarification: use real official exchange data and realistic costs, but 10,000 USDT remains research/paper equity only. This is not permission for live orders or credentials.
- Next gate order: pass archive pilot, validate older-month conventions, then verify volume-field semantics and build the eligible inventory before generating any Top-10 ranks. No current or historical Top-10 result is claimed yet.


## 2026-10-21 — Continuity prompt and test CI checkpoint
- Added `NEW_CHAT_CONTINUITY_PROMPT.md` for a no-drift handoff to a fresh ChatGPT thread.
- Commit `9ff54223401c20cb4e923650a3d1f4f4f41e986a` corrected the monthly archive test fixture and added a missing-row/gap regression test. GitHub Actions smoke run `39565549581` succeeded.
- CI success verifies the test workflow only. The official September 2026 BTCUSDT 5m monthly archive pilot remains NOT RUN/REVIEWED from chat; Phase 2 / HD-03 remains BLOCKED until both Spot and USDⓈ-M Futures reports are reviewed and pass.
- Next action: verify live GitHub state, then obtain and review the monthly archive workflow artifact. Do not backtest before the data and cost gates pass.

## 2026-10-21 — Current continuity reconciliation (supersedes older next-action notes)
- Live `main` immediately before this documentation update was `e5bc11161e4392de3f84c7e1652fdcd6119714ae`; its parent is `5ccc02546948873f5de2004cd2d7d711262e084d`.
- Governing plan and canonical handoff: `PLAN_AND_PHASE_LOCK.md` and `NEW_CHAT_CONTINUITY_PROMPT.md`. Historical entries referring to the earlier daily/API-required route, Colab/Drive, older main SHAs, or the former Futures REST blocker are retained as history, but do not override the newer monthly-archive-first decision.
- Active gate remains HD-03: manually run `.github/workflows/monthly-binance-history-chunk.yml` for completed month `2026-09`, interval `5m`, symbol `BTCUSDT`; review both official monthly Spot and USDⓈ-M Futures reports and their evidence artifact. Expected full-month count is 8,640 candles per market.
- Latest verified smoke CI is [39565549581](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39565549581) on commit `9ff54223401c20cb4e923650a3d1f4f4f41e986a`. This is code/test CI only, not data acceptance. No HD-03 report is verified as passed in this checkpoint.
- The available GitHub connector exposes repository read/write tools but no workflow-dispatch action. Therefore no workflow launch is claimed. Use the existing [monthly workflow page](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/workflows/monthly-binance-history-chunk.yml) for manual dispatch; do not use Colab/Drive, marker commits, REST endpoint cycling, or access-restriction bypasses.
- Backtesting, model training, paper trading, live orders, credentials and deployment remain locked. Next action is the single manual HD-03 dispatch, followed by independent review of both real reports and the artifact.

## 2026-10-21 — Monthly workflow input-safety hardening
- Reviewed the live monthly archive workflow and found its manually supplied `month` and `interval` values were interpolated directly into shell command text. Changed both audit steps to receive inputs through environment variables and use quoted shell expansions, avoiding direct expression interpolation in shell code.
- Workflow change commit: `7b8a21ea4759fa381e8847a3ae9a0657ba522df1`. The existing `audit-runner-smoke.yml` includes this workflow path in its push filters, so CI should run; its result has not yet been verified here.
- This is workflow-input safety hardening only. No archive workflow was dispatched, no Spot/Futures report was produced or accepted, and HD-03 / Phase 2 remains BLOCKED. Next action remains manual HD-03 dispatch after the workflow change's CI result is checked.

## 2026-10-21 — Workflow safety fix CI verified
- Targeted smoke workflow [39567909921](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39567909921) completed with `success` on workflow-fix commit `7b8a21ea4759fa381e8847a3ae9a0657ba522df1`. The run validates the repository's configured smoke steps; it is not a real archive audit.
- HD-03 remains BLOCKED because no September 2026 Spot/Futures archive reports have been produced and reviewed. Next action is the one manual dispatch of the monthly archive workflow, followed by artifact review.


## 2026-10-21 — Independent review of prior Phase 2 evidence artifact
- Independently downloaded retained artifact from run [39496937998](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496937998); downloaded artifact SHA-256 matched GitHub's artifact digest.
- Prior 2026-10-15 BTCUSDT Spot 5m daily report: `PASS`, including publisher checksum, schema/candle checks and bounded Spot API sample. Prior USDⓈ-M Futures 5m report: `BLOCKED` only at the bounded official API sample check; archive checksum, ZIP, schema and 288-candle daily quality checks passed. The 2026-09-15 daily-vs-monthly archive diagnostic matched row-for-row for both markets, using the same publisher.
- This evidence improves the prior diagnostic record but does not pass the active HD-03 full-month pilot (`2026-09`, `5m`, 8,640 candles per market). No backtest, training, paper trading or live execution is unlocked.

## 2026-10-21 — Monthly candle positive-price validation hardening
- Added a strict positive-price invariant to the monthly archive validator; ordered candles containing zero or negative OHLC values now fail the quality gate. Added regression tests for both cases.
- Smoke CI [39584538161](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39584538161) succeeded on test commit `0200cf024c0b4db0e3add7d696db19391ce1b1b2`. This is code/test evidence only.
- HD-03 is still BLOCKED until the active `2026-09` BTCUSDT `5m` Spot and USDⓈ-M Futures monthly archive reports both pass and are reviewed.


## 2026-10-21 — HD-03 monthly archive pilot reviewed
- User manually dispatched the required GitHub Actions workflow: [run 39594637570](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39594637570) on main commit `72d3ab71744aa30a2a848ed24b71dee412e7ed32`, inputs `2026-09` / `5m` / BTCUSDT.
- Retrieved job logs and artifact `12343236522` (`monthly-binance-2026-09-5m-39594637570.zip`). GitHub artifact digest: `sha256:b951e65f8d35ae2a79eb8afbaec78a1923b7362bb814d9bb0d7e99e6e557f7e5`; the local downloaded ZIP's SHA-256 matched this digest.
- Independently inspected both embedded report JSON files. Spot report `spot-BTCUSDT-5m-2026-09.report.json`: PASS; 8,640 rows, zero malformed/duplicate/missing/gap rows, official checksum equals computed SHA-256 `4106fc73698fd1851b1821cd0293adc6304f86f0c2e72244e15c41f63c2bde08`; timestamp unit `us`; first open 2026-09-01T00:00:00Z and last open 2026-09-30T23:55:00Z. Futures report `usdm-BTCUSDT-5m-2026-09.report.json`: PASS; 8,640 rows, zero malformed/duplicate/missing/gap rows, official checksum equals computed SHA-256 `3a2d163a2bd28ca614fa0840a92ecbcde0d9c4962b278dd619d5bf81a9918e26`; timestamp unit `ms`; same expected first/last open times. Every reported validator check passed for both markets, including ZIP integrity, schema, ordering, timestamps, OHLC invariants, positive prices, volumes and full-month coverage.
- Evidence boundary: checksums verify publisher byte integrity, not independent economic truth. These are archive validation reports; report policy says REST API was not called. Artifacts are temporary and expire 2026-11-04.
- HD-03 monthly archive pilot is ACCEPTED for this bounded BTCUSDT 5m month under archive-first policy. This does not pass the whole Phase 2 historical coverage/cost gate and does not authorize backtesting yet.
- Next allowed step: validate an older month’s archive path/timestamp/schema conventions for Spot and USDⓈ-M Futures (recommended 2024-01 BTCUSDT 5m, subject to published archive availability), then proceed to coverage inventory and volume semantics. No backtest, model training, paper trading, credentials, live orders or deployment occurred.
