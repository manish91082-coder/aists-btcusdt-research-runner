# Rules, Constitution, Locks and Operating Constraints

Mandatory until explicitly changed. Every change must be dated and logged.

## Constitution
1. Evidence before assertion.
2. Research before implementation.
3. Planned, attempted, completed and verified are separate states.
4. GitHub is the project source of truth.
5. Independently verify important evidence, data, mathematics and Git writes.
6. Tie every task to the final goal and current research gate; no silent drift.
7. Fail closed when data, product eligibility, account/order state or risk is uncertain.
8. Reproducibility for every experiment.
9. Research never authorises moving funds or placing orders.
10. Material actions, failures, decisions and next steps must be logged.

## Rules
- R-001 Git is the source of truth for status, memory, continuity, rules, evidence and logs.
- R-002 Make project changes directly in GitHub unless user explicitly changes this instruction.
- R-003 Verify live branch head before acting; stop and re-review unexpected changes.
- R-004 Verify resulting commit and file contents after every substantive change.
- R-005 Never fabricate data, provenance, tests, performance or exchange status.
- R-006 Never commit keys, tokens, passwords, private keys or secrets.
- R-007 No live orders or autonomous execution without explicit authorisation for that exact stage.
- R-008 Stage progression: research, data validation, deterministic tests, historical analysis, shadow/paper, security review, then optional separately approved limited live stage.
- R-009 Before execution, require sizing, max exposure/loss, stale-data handling, duplicate prevention, kill switch and restart reconciliation.
- R-010 Store source, timestamp, timezone, symbol/market, interval, transforms and validation status for trading data.
- R-011 Record code revision, config, data window, dependencies and random seeds where applicable.
- R-012 Least privilege; withdrawals disabled by default; secrets never in logs.
- R-013 Preserve history, backup and unrelated branches unless exact scoped approval says otherwise.
- R-014 Synchronise status/memory/continuity/logs after substantive actions.
- R-015 Obtain explicit confirmation for destructive, financially consequential, externally visible or irreversible actions.
- R-016 No trading implementation until relevant research acceptance gates are satisfied and documented.
- R-017 AI may propose; deterministic Safety Kernel has final veto and cannot be overridden.
- R-018 Real archives/live feeds must be source-verified; missing values stay missing; replay/paper fills must be labelled as estimated/virtual.
- R-019 Measure storage/compute/uptime and verify free-tier terms before relying on any free resource.
- R-020 Verify current account/product eligibility and applicable requirements before Futures execution; never bypass restrictions.
- R-021 Chronological splits, leakage checks, point-in-time universe and multiple-testing awareness are required for performance claims.
- R-022 Include actual fees, BNB deductions, Futures funding and measurable execution costs in net PnL.
- R-023 Protective stops/trailing must have tested monotonicity and reconciliation; AI cannot loosen hard caps.
- R-024 Every substantive project task/response must leave a dated status/log checkpoint; record failure and unresolved issue.
- R-025 An AI-generated formula or strategy requires dimensional review, independent tests and unseen-data validation before promotion.

## Lock register
- LIVE TRADING: LOCKED. No real order/autonomous live execution authorised.
- EXCHANGE CREDENTIALS: LOCKED. None configured; none may be committed.
- WITHDRAWALS: LOCKED.
- PRODUCTION DEPLOYMENT: LOCKED.
- FUTURES ACCOUNT/JURISDICTION ELIGIBILITY: BLOCKED pending verification.
- TRADING CODE: LOCKED until research gates complete.
- REAL CAPITAL: LOCKED. 10,000 USDT is a paper/research assumption only.
- STRATEGY AND LIVE RISK PARAMETERS: NOT APPROVED.
- TOP-10 COINS: NOT SELECTED; evidence-backed ranking required.
- BNB FEE CONFIG: NOT VERIFIED for an actual account.
- COMPUTE/HOSTING: no paid service authorised; zero-cost feasibility must be measured.
- REPOSITORY RENAME: pending user; keep current name.
- ZIP BACKUP: not created; historical preservation uses Git history and backup branch.

To unlock any lock, record a dated decision, evidence, risk review, user approval where needed and synchronise this file with SESSION_LOG.md.

## 2026-10-21 — Master plan lock
- R-026: Follow PLAN_AND_PHASE_LOCK.md as the default dependency-ordered roadmap. Do not skip phases or mark a phase passed without its documented evidence and exit gate. Any reprioritisation must be recorded and must not waive safety/data/live-approval gates.
- MASTER EXECUTION PLAN: LOCKED as the default sequence; changes require the change-control protocol in PLAN_AND_PHASE_LOCK.md.
- Immediate work queue: representative official Binance archive audit; then freeze S-01 through S-04 experiments before any backtest.
- This plan lock does not unlock trading code, credentials, live orders, withdrawals, production deployment or real capital.


## 2026-10-21 — Expanded anti-drift and AI decision contract
- R-027: Before each substantive action, check the final goal, live GitHub head, active phase, acceptance gate, evidence and blockers. Work only on the next gate unless the user explicitly changes priority.
- R-028: AI may dynamically choose among validated features/strategies and propose entries, exits, size, SL/TP and trailing changes, but cannot introduce untested mathematics into execution or override the independent Safety Kernel.
- R-029: Continuous scanning, dynamic decisions and full automation may be claimed only to the extent demonstrated by measured runtime and verified tests; a plan is not implementation.
- R-030: Every material response/action must report actual changes, verification limits, unresolved blockers and the exact next task; do not claim zero error or persistent model-memory changes without evidence.


## 2026-10-21 — Expanded anti-drift and AI decision contract
- R-027: Before each substantive action, check the final goal, live GitHub head, active phase, acceptance gate, evidence and blockers. Work only on the next gate unless the user explicitly changes priority.
- R-028: AI may dynamically choose among validated features/strategies and propose entries, exits, size, SL/TP and trailing changes, but cannot introduce untested mathematics into execution or override the independent Safety Kernel.
- R-029: Continuous scanning, dynamic decisions and full automation may be claimed only to the extent demonstrated by measured runtime and verified tests; a plan is not implementation.
- R-030: Every material response/action must report actual changes, verification limits, unresolved blockers and the exact next task. Do not claim zero error or persistent model-memory changes without evidence.

## 2026-10-21 — Per-response end-to-end plan audit lock
- R-031: Before EVERY response in this project, including a short “next” turn, review the user's locked mission and request against the complete current `PLAN_AND_PHASE_LOCK.md`, then inspect current `PROJECT_STATUS.md`, `CONTINUITY.md`, `RULES_AND_LOCKS.md`, relevant evidence, and the live GitHub main state before choosing an action.
- R-032: No drift: choose work only from the current phase's documented next safe action and exit gate. Do not repeat the previous instruction as a substitute for work; continue safe work where possible. Do not skip a gate, silently change scope, or start downstream work while a prerequisite is blocked.
- R-033: Treat continuity as a verified checkpoint, not chat recollection. Record changes, evidence, blockers, exact next action, and verification limits in repository records; read back every modified file and verify the new branch state before claiming a write is complete.
- R-034: Report only observed facts. Explicitly separate repository-documentation changes, code/test changes, CI results, real market-data audit results, backtests, paper trading, and live execution. One category never proves another. Never promise zero errors; state what was checked and what remains unverified.
- This is a process lock. It does not change the project goal or advance any phase. Phase 2 remains blocked until the actual representative Spot and USDⓈ-M Futures reports are independently reviewed.

## 2026-10-21 — R-035 to R-037: efficiency and anti-loop lock
- R-035: Apply EFFICIENCY_NO_DRIFT_PROTOCOL.md to every substantive response/action. Define the single decision to resolve, use one targeted evidence pass, reuse valid prior evidence, and do not repeat completed audits or polls without a material reason.
- R-036: Rerun CI/data audits only after relevant code/config/input/protocol changes, a correctable committed defect, an incomplete required run, or a documented decision-relevant environment change. Repeated same-blocker results with no material change require stopping, not another retry.
- R-037: For access/jurisdiction restrictions such as HTTP 451, never use VPN/proxy/identity or technical bypasses. Consult official documentation once for supported permitted alternatives; if none is evidenced, preserve BLOCKED and request only the narrow decision/environment change needed. Never silently replace a locked check with weaker evidence.
- Efficiency clarification to R-031: perform the mission/phase/gate check on every response using the last verified full-plan checkpoint; re-fetch all unchanged long files only when the main head, plan, phase, scope, gate understanding or continuity context requires it. This is an anti-duplication rule, not a relaxation of the per-response responsibility check.
