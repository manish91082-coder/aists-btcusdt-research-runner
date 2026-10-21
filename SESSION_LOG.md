## 2026-10-21 | Market-data manifest specification
- Added MARKET_DATA_MANIFEST_SPEC.md with one-row-per-artifact provenance, checksum, timestamp-unit, schema, row/gap and validation fields.
- Proposed BTCUSDT Spot 5m plus matching USDⓈ-M Futures archive as the first representative audit target. This is only a proposed target; no file was downloaded and no checksum was run.
- README links the strategy dossier and market-data manifest spec.
- Next step: execute the representative archive audit through an available reliable download path; if unavailable in the current environment, report the blocker rather than pretend validation passed.

---

## 2026-10-21 | Strategy research focus and Binance data requirements

### User direction
Defer tax/jurisdiction research to a later stage; focus the immediate work on strategies and the Binance data required to test them. BNB commission payment remains a requirement wherever the product/account supports it. This is a sequencing change, not a waiver of later execution gates.

### Research performed
- Reviewed official Binance Spot exchange-information and rate-limit documentation.
- Reviewed official Spot symbol filter documentation.
- Reviewed official USDⓈ-M Futures market-data/kline reference.
- Rechecked official public archive documentation for requested kline intervals, checksums and Spot timestamp-unit handling.
- Created STRATEGY_RESEARCH.md with 12 testable hypotheses: trend, mean reversion, breakout, momentum, regime selection, candle features, funding-aware filtering, liquidity filtering, cross-asset context, supervised probability, portfolio allocation and exit-policy tournament.

### Honest status
No strategy was run or proven profitable. No archive was downloaded, no checksum was executed, no model trained, no backtest/paper run occurred, and no live order was sent. Strategy hypotheses are registered only.

### Next task
Build a reproducible market-data manifest design and audit one representative archive end-to-end; then pre-register S-01 to S-04 experiments before any backtest.

---

# Session Log

Newest entries first. Record verified facts, not intentions as completed work.

## 2026-10-21 | AI trading charter and research baseline

### User-confirmed requirements
- Binance Spot and Futures, long/short exposure, AI-driven dynamic market/strategy/feature/entry/exit/stop/target/trailing management and continuous scanner.
- Timeframes: 5m, 15m, 1h, 4h, 8h, 1d, 1w and 1M.
- Evidence-backed top-ten high-volume universe, exact list to be decided by research.
- 10,000 USDT stated initial capital; BNB fees where genuinely supported.
- Longest available historical learning data, with no fabricated data/results.
- Zero-cost-first resources, research before coding and GitHub-based memory/status/continuity/rules/logging.

### Research completed in this response
- Reviewed official Binance Public Data repository for archives, supported markets, interval labels and checksum instructions.
- Reviewed official Spot API docs, symbol filters and Spot Testnet documentation; testnet has virtual funds and periodic reset limitations.
- Reviewed Binance BNB fee FAQ (page last updated 2026-02-17): published maxima differ for Spot/Margin and Futures and require balance/settings.
- Reviewed Binance Futures fee FAQ (page last updated 2026-01-05): commission, funding and liquidation-related costs are distinct; USDⓈ-M BNB deduction requires enough BNB in the Futures wallet.
- Reviewed official Binance launch announcement (14 July 2017): complete ten-year Binance-only historical coverage cannot exist as of this checkpoint.
- Reviewed Binance India KYC announcement, official FIU-IND order and official Income Tax Department pages on sections 115BBH and 194S. Account-specific Futures access remains unresolved and is a gate, not an assumption.
- Findings and limitations are registered in EVIDENCE_REGISTER.md.

### Repository actions planned in this checkpoint
- Add master blueprint, research register, evidence register, decision log and quality audit.
- Update README, status, durable memory, continuity, rules/locks, session log and changelog.
- Proposed ten AI roles plus independent deterministic Safety Kernel; these are design proposals, not implemented agents.
- Record explicit restrictions: no coding/live trade before research gates and approvals.

### Explicitly not performed
No code, datasets, checksum run, top-ten selection, trained model, backtest, paper-trading session, real order, credential creation, fund transfer or deployment.

### Next action
Start R02 product/jurisdiction/account eligibility and R03 exact per-symbol historical coverage/checksum/timestamp/gap inventory. Keep all gates fail-closed.

---

## 2026-10-21 | Clean-slate and continuity foundation
- User confirmed clean-slate deletion of the 692 tracked files from old main snapshot f2fcc6f2e74dcd08e59cdcb811cd680d35fb1733.
- Backup branch backup/pre-cleanup-2026-10-21-main-f2fcc6f was created at that snapshot.
- Clean-slate commit f52bac573c9509c71143158a7f609bd55a6a76bb moved to main; GitHub Contents API returned an empty list at that point.
- Initial governance/continuity documents were created and verified.
- User deferred repository rename. No trading code/backtest/paper/live order was performed.

## 2026-10-21 | User-requested master plan and phase lock
### Action
- Reviewed the current master blueprint, project memory, continuity protocol, rules/locks, strategy dossier, research register and current status.
- Added PLAN_AND_PHASE_LOCK.md with the full dependency-ordered roadmap, explicit phase exit gates, change-control protocol and immediate work queue.
- Locked this plan as the default project sequence in RULES_AND_LOCKS.md and updated status/continuity records.

### Current truth
- 12 strategy candidates are registered but not empirically tested.
- Market-data manifest specification exists, but no representative archive download/checksum/audit has been verified.
- No top-10 universe, trained model, backtest, paper run, trading engine, real order or deployment is claimed.
- Live trading, credentials, withdrawals, production deployment and real capital remain locked.

### Next action
1. Audit a real official Binance archive end-to-end; do not claim PASS until the artifact and validation output are observed.
2. Freeze S-01 to S-04 experiment protocols before backtesting.
3. Continue the phase gates in PLAN_AND_PHASE_LOCK.md without silent skipping.


## 2026-10-21 | Detailed user requirement audit and plan saturation
### Full requirement
Binance Spot + Futures; long/short; BNB commission where supported; 5m/15m/1h/4h/8h/1d/1w/monthly; evidence-selected top ten; longest verifiable history; dynamic strategy/indicator/algorithm, entries/exits/sizing/SL/TP/trailing and position changes; 10,000 USDT research equity; zero-cost-first; no fake evidence or drift; research before code.

### Repository changes
- Expanded PLAN_AND_PHASE_LOCK.md with AI decision contract, ten bounded logical roles, independent Safety Kernel, scanner/timeframe causality, dynamic position/exit rules, zero-cost measurement, fee accounting and requirement-to-phase traceability.
- Linked the master plan from PROJECT_BLUEPRINT.md and synchronised status, governance and continuity.

### Verification truth
The documents were written and read back from GitHub. This verifies repository documentation only. No representative archive audit, backtest, model training, paper run or live order is newly claimed.

### Next gate
Phase 2: actual official Binance archive download/verification and data-quality audit. Preserve blockers; never fabricate PASS.


## 2026-10-21 | Phase 2 retrieval blocker
## 2026-10-21 — Phase 2 archive retrieval blocker
- Attempted HEAD requests from the current execution container for candidate BTCUSDT Spot 5m and USDⓈ-M Futures daily archive URLs and companion `.CHECKSUM` URLs for 2026-10-20.
- All four attempts failed before receiving an HTTP response with `Temporary failure in name resolution`; the web retrieval tool also could not access the direct checksum URLs.
- This proves a current-environment retrieval blocker only. It does not prove the candidate archives exist or do not exist, and no archive bytes, checksum, schema, timestamp, row count, gap result or data-quality PASS is claimed.
- Created DATA_AUDIT_LOG.md with exact attempted URLs, observed errors, evidence boundaries and a reproducible zero-cost next route via a network-enabled user-owned runtime such as Colab.
- Phase 2 remains BLOCKED pending actual retrieval. No bulk download, strategy backtest, model training, paper run or live order was performed. Next: retrieve one real official artifact and its checksum, audit it end-to-end, then freeze S-01 to S-04 before any backtest.


## 2026-10-21 | Phase 2 audit runner and zero-cost handoff
### Work performed
- Added `tools/audit_binance_archive.py`, a standard-library Python audit utility for official daily kline ZIP/checksum retrieval, SHA-256, ZIP/CSV structure, timestamp normalization, duplicate/order/gap checks, OHLC/volume invariants and up to three official API spot checks.
- Added `RUN_DATA_AUDIT.md` with reproducible Colab instructions and separate Spot and USDⓈ-M Futures commands.
- Re-read the new files and recorded this work as a prepared route, not an executed data audit.

### Honest status
The current execution environment still cannot resolve the Binance archive host. No downloaded archive, official checksum match, row count, API comparison or data-quality PASS is available. Phase 2 remains BLOCKED pending the reports from a network-enabled runtime.

### Next action
Run the documented audit for a completed candidate UTC date in Colab; preserve both market reports and any failure output. Independently review the evidence. Only after the representative data gate is resolved, freeze S-01 to S-04 protocols before any backtest.


## 2026-10-21 | Audit runner coverage hardening
- Code-reviewed the archive audit runner and found that row-to-row gap detection alone would miss absent first/last candles.
- Added expected UTC-day open coverage checks for intervals that divide a day, included missing-open examples in JSON, and made reported first/last event timestamps order-independent.
- Readback from GitHub is required; no market-data artifact was downloaded and this change does not pass Phase 2.

## 2026-10-21 | Audit classification and CI regression tests
- Reviewed `tools/audit_binance_archive.py` for fail-closed status semantics.
- Added separate API-sample classification: mismatches are FAIL; inability to verify due to API/transport errors is BLOCKED.
- Corrected overall status precedence: any proven required-check FAIL wins; otherwise a required BLOCKED check keeps the audit BLOCKED; PASS requires every required check to pass.
- Added seven unit tests in `tests/test_audit_status_classification.py`; smoke workflow runs unittest discovery and now triggers on test-file changes.
- Commits: runner `1a393f1dce292b182f021607f202279acf6fc010`; regression test `c596fa9f242e97594aa32e34ae84ff5147f24b57`; CI path-filter update `4908b2ac25ba9edee679475b69e60402fe8078b0`. Audit log also records these corrections.
- Readback confirmed the latest code/test/workflow/docs are present. CI execution result still unverified, and no real market archive has been audited.
- Phase 2 remains BLOCKED. Next: run the manual Spot + USDⓈ-M archive audit and review both reports before any strategy backtest.

## 2026-10-21 | Per-response end-to-end plan audit lock
### User instruction
Check the complete plan every response, prevent drift strictly, preserve continuity, and select the next step only after reviewing the whole plan and current evidence.

### Durable action
- Recorded the process lock in `RULES_AND_LOCKS.md`, `CONTINUITY.md`, `PROJECT_STATUS.md`, and `PROJECT_MEMORY.md`.
- Required per-response review of the full `PLAN_AND_PHASE_LOCK.md`, current main state, active gate, evidence, blockers, and no-code/no-live locks.
- Required actual next-step work where possible, durable logging, readback of changed files, and truthful separation of documentation, code, CI, data-audit, backtest, paper and live evidence.

### State after this process lock
- This lock does not mark Phase 2 complete.
- Manual Phase 2 workflow is prepared with input validation but has not been verified as dispatched in this checkpoint.
- No real archive/checksum audit, strategy backtest, model training, paper run or live order is claimed.
- Next safe action remains running the manual Phase 2 audit and reviewing both actual market reports.

## 2026-10-21 | Phase 2 optional CSV-header compatibility hardening
### Review finding and change
- Reviewed the live audit runner against the locked Phase 2 gate and official kline schema. A potential archive-compatibility issue was that any leading 12-column header would be parsed as malformed data.
- Added exact 12-column header recognition on the first non-empty record; records `csv_header_present` in each report. Added four unit tests covering space-separated labels, snake_case labels, normal data and wrong-width rows.
- Runner commit: `5369263058971e14fcae4db438a1e205cbb2c7ce`; test commit: `d0ec62150078b6cf210609dfff24bc6bbdbff579`.

### Verification limits
- GitHub acknowledged both file writes. The resulting smoke CI run has not yet been independently checked.
- No official archive was downloaded or checksum/API/data-quality audited. Phase 2 remains BLOCKED.
- No strategy backtest, model training, paper run, real order or deployment occurred.

### Exact next action
Check whether GitHub Actions has a successful smoke run for the latest runner/tests. Then run the manual Phase 2 workflow for BTCUSDT Spot 5m and USDⓈ-M Futures 5m and independently review both report JSON files before deciding whether the gate passes.

## 2026-10-21 | Offline smoke CI result independently verified
- Retrieved the GitHub Actions run metadata and job steps for [run 39488166620](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39488166620), on commit `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- Conclusion: `success`. Python compilation, unittest discovery, CLI help and malformed-date preflight all completed successfully.
- Evidence boundary: offline smoke checks only. No real archive/checksum/API comparison is implied.
- The latest 100 repository workflow runs inspected did not show a manual Phase 2 audit run. Next: user dispatches Phase 2 workflow and shares both reports/artifact for review.

## 2026-10-21 | Phase 2 workflow-state recheck
- Revalidated live main ref and the master plan/current gate. Main: `ba547c6e18db46d4032757dc3ee4af89099c40bd`.
- Confirmed the smoke CI run remains successful. Searched the latest 100 workflow runs; no Phase 2 Binance archive audit was found.
- No dispatch was made because the available GitHub connector provides no workflow-dispatch action. This is a tool boundary, not evidence of archive availability or failure.
- Next task: user manually dispatches the Phase 2 workflow and shares the Spot and USDⓈ-M JSON reports plus evidence artifact. Phase 2 stays BLOCKED; strategy backtests remain locked.

## 2026-10-21 | S-01 to S-04 preregistration frozen under blocker contingency
- Added S01_S04_PREREGISTRATION.md and D-018 after rechecking the live repository and workflow state.
- This avoids an idle process loop while preserving the real-data gate. Phase 2 remains BLOCKED; no archive/checksum/API comparison has been verified.
- Protocols freeze causal timing, next-bar entries, costs, chronological splits, benchmarks and bounded sensitivity grids. No backtest, model training, paper run or live execution has occurred.
- Next dependency: existing Phase 2 workflow artifact and independent review of both Spot and USDⓈ-M reports.

## 2026-10-21 | Automatic Phase 2 trigger attempt
- Modified the existing audit workflow to accept a path-filtered push trigger for `tools/phase2-audit-trigger.txt`, with defaults `2026-10-15`, `BTCUSDT`, `5m`, and committed the marker.
- Rechecked Actions after the marker commit: no Phase 2 audit run appeared in the latest 100 runs. The automatic trigger attempt is unverified and did not provide audit output.
- Do not claim a run or data pass. Avoid further trigger commits; next dependency is one manual dispatch of the existing workflow and review of its artifact.


## 2026-10-21 — GitHub-only execution route reaffirmed
- User explicitly instructed that project work and execution remain on GitHub, without Colab or Google Drive.
- The repository already has a manual GitHub Actions Phase 2 workflow. The current chat GitHub connector can read repository state and workflow evidence but has no workflow-dispatch action, so I must not claim to have started the workflow from this session.
- The previous assistant's Colab/Drive JSON-job route was unnecessary and is withdrawn. The authoritative next step is one manual dispatch of the existing Phase 2 workflow from GitHub Actions UI, then review the Spot/Futures reports and artifact.
- No new audit was run; Phase 2 remains BLOCKED until actual reports satisfy the gate. Do not add marker commits or repeat unchanged checks.


## 2026-10-21 — Manual-only Phase 2 workflow lock
- Repository audit found a stale push-path trigger and marker file alongside the documented manual-dispatch procedure. Removed the marker-based/push-trigger route to prevent unintended or repetitive real-data audits on code pushes.
- Phase 2 workflow now starts only through its existing GitHub Actions `workflow_dispatch` input form. This session cannot dispatch it through the available connector. No archive audit was run; Phase 2 remains BLOCKED.


## 2026-10-21 — New-chat handoff and monthly test regression
- Added `NEW_CHAT_CONTINUITY_PROMPT.md` with the locked mission, dependency roadmap, safety constraints, anti-drift rules, current gate and verification requirements.
- Updated `tests/test_audit_binance_monthly_archive.py` at commit `9ff54223401c20cb4e923650a3d1f4f4f41e986a`: corrected the newline fixture and added a regression test for missing candles/gaps under full-month coverage.
- Verified GitHub Actions smoke run `39565549581` completed successfully for that commit. This is CI evidence only.
- Monthly real-data pilot has not yet been run/reviewed; Phase 2 remains BLOCKED. No backtest, training, paper trading, live order or deployment has occurred.

## 2026-10-21 — Continuity reconciliation and next action
- Revalidated live `main` at `e5bc11161e4392de3f84c7e1652fdcd6119714ae` before this documentation reconciliation. Read the current status/continuity records, locked master plan, rules, efficiency protocol and canonical new-thread handoff.
- Reconciled the authoritative next action in `PROJECT_STATUS.md`, `CONTINUITY.md` and this log: the latest monthly-archive-first HD-03 decision supersedes older historical notes about the daily/API-required route, Colab/Drive, stale main SHAs and the former Futures REST blocker. Historical notes were not deleted.
- Latest observed smoke CI [39565549581](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39565549581) succeeded on `9ff54223401c20cb4e923650a3d1f4f4f41e986a`; no real monthly archive PASS is inferred.
- Workflow-dispatch action is not available in this connector, so no dispatch is claimed. Active gate remains HD-03, `2026-09` BTCUSDT `5m`, both Spot and USDⓈ-M Futures monthly archive reports required. Exact next action: manually dispatch the existing GitHub Actions workflow and independently inspect both reports plus the evidence artifact.
- No backtest, model training, paper run, live order or deployment was performed or unlocked. After writing, read back all changed files and verify the resulting main SHA.

## 2026-10-21 — Monthly workflow shell-input hardening
- Audited the active monthly archive workflow before the next data-gate attempt. Found direct `inputs.month` and `inputs.interval` interpolation inside shell command text.
- Fixed the two archive steps to pass those inputs through step environment variables and quote shell expansions. Commit: `7b8a21ea4759fa381e8847a3ae9a0657ba522df1`.
- The smoke workflow path filter includes `.github/workflows/monthly-binance-history-chunk.yml`; the resulting CI status has not yet been observed. No workflow dispatch or market-data report is claimed. HD-03 remains BLOCKED.
- Next action: inspect the targeted smoke CI result once; if successful, manually dispatch the September 2026 BTCUSDT 5m monthly pilot and review both market reports plus the evidence artifact.

## 2026-10-21 — Workflow safety fix smoke result
- Observed GitHub Actions run [39567909921](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39567909921): conclusion `success`, head commit `7b8a21ea4759fa381e8847a3ae9a0657ba522df1`. This verifies configured smoke CI after the monthly workflow input-safety fix only.
- No monthly archive pilot has been dispatched or reviewed. HD-03 remains BLOCKED. Next action: manual dispatch for `2026-09`, `5m`, BTCUSDT and inspect Spot + USDⓈ-M Futures reports and artifact.


## 2026-10-21 — Independent evidence artifact review
- Downloaded prior Phase 2 artifact ID `12297349529` from run [39496937998](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39496937998); local SHA-256 matched GitHub's reported artifact digest.
- Reviewed embedded reports: 2026-10-15 Spot 5m daily archive PASS including bounded official Spot API sample; USDⓈ-M Futures archive integrity/schema/daily candle checks PASS but API sample remains BLOCKED. The 2026-09-15 daily-vs-monthly diagnostic matched all 288 candles for each market with zero mismatches and valid publisher checksums; this is same-publisher consistency only.
- Active HD-03 is still the separate September 2026 full-month archive pilot. No dispatch was possible through the current connector, no HD-03 pass is claimed, and no backtest/trading gate is unlocked.

## 2026-10-21 — Positive-price validator fix and CI verification
- Added `positive_prices` to the monthly archive quality checks because OHLC ordering alone does not reject zero/negative prices. Added regression cases for both invalid-price classes.
- CI run [39584538161](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39584538161) completed successfully on test commit `0200cf024c0b4db0e3add7d696db19391ce1b1b2`; compile, unittest discovery, CLI help and invalid-date preflight passed.
- This was code/test hardening, not market-data acceptance. HD-03 remains BLOCKED pending actual September monthly Spot + USDⓈ-M Futures reports.
