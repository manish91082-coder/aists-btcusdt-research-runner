# Rules, Locks, and Operating Constraints

These rules are mandatory until the user explicitly changes them. Any change must be recorded in this file and the session log.

## R-001: Git is the source of truth
Project status, durable memory, continuity, rules, locks, decisions, and session history must live in this repository. Chat context alone is not the authoritative checkpoint.

## R-002: Direct repository workflow
Make project changes directly in GitHub. Do not substitute external workspaces or cloud drives unless the user explicitly authorizes a change.

## R-003: Verify before acting
Fetch the live branch SHA and inspect relevant paths before edits. Use expected-SHA/lease protections when available. If the branch head unexpectedly changed, stop and re-review rather than overwrite.

## R-004: Verify after acting
After every repository write, verify the resulting branch head, commit, file contents, and test results relevant to the change. Distinguish attempted from completed and verified.

## R-005: No fabricated state
Never invent files, test results, data provenance, strategy performance, exchange status, or successful execution. Record uncertainty explicitly.

## R-006: Secrets never enter Git
Never commit API keys, private keys, passwords, access tokens, account identifiers, or other secrets. Use documented secret-management mechanisms only after a deployment design is agreed.

## R-007: No live trading without explicit authorization
Do not connect to a live exchange, submit real orders, enable withdrawals, or deploy an autonomous live trader without explicit user authorization for that exact stage and a reviewed risk-control plan.

## R-008: Safe development progression
Prefer staged development: requirements → architecture → data validation → deterministic tests → historical backtests with fees/slippage assumptions → paper trading → limited, explicitly approved live execution. Do not skip gates silently.

## R-009: Risk controls are required before execution
Before any order-execution implementation is enabled, define and test position sizing, maximum exposure, per-trade and daily loss limits, stale-data handling, order rejection handling, duplicate-order prevention, kill switch, and safe restart/reconciliation behavior.

## R-010: Evidence and provenance
Record the source, timestamp, timezone, symbol/market, data interval, transformation, and validation outcome for trading data and research claims. Separate raw data from derived results.

## R-011: Reproducibility
Record relevant code revision, configuration, data window, dependencies, and random seeds where applicable for experiments and backtests.

## R-012: Least privilege
Use the minimum required permissions. Trading credentials, if later needed, must not have withdrawal permission unless a separately justified and explicitly approved requirement exists. Never expose credentials in logs.

## R-013: Preserve history and unrelated work
Do not delete the repository, historical commits, backup branch, or unrelated branches/PRs unless the user explicitly instructs that specific action.

## R-014: Continuity synchronization
After substantive work, synchronize status, memory, continuity, session log, and changelog. Update rules/locks when they change. Verify all updates on GitHub.

## R-015: Scope and approval
When a change is destructive, financially consequential, externally visible, or irreversible, summarize the exact scope and obtain explicit confirmation before execution.

## Lock register

- **LIVE-TRADING LOCK: LOCKED.** No real orders or autonomous live execution authorized.
- **EXCHANGE-CREDENTIALS LOCK: LOCKED.** No credentials configured or to be committed.
- **WITHDRAWALS LOCK: LOCKED.** No withdrawal functionality authorized.
- **PRODUCTION-DEPLOYMENT LOCK: LOCKED.** No production deployment authorized.
- **STRATEGY/PARAMETER LOCK: UNDEFINED.** Strategy and parameters are not yet agreed; do not guess.
- **REPOSITORY RENAME: PENDING USER.** Current repository name remains unchanged until the user performs or authorizes the rename.

Unlocking a lock requires a dated decision, explicit scope, relevant safety review, and updated evidence in this repository.