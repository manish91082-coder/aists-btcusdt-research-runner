# CP-0272: CP-0040 Quarantine Gate CI Coverage (Hindi)

**Date:** 2026-10-19  
**Branch:** `cp-0272-cp0040-gate-ci-coverage`  
**Scope:** independent engineering safety coverage only  
**Global G0:** `BLOCKED_GLOBAL` (unchanged)

## Why this checkpoint exists

The repository already contains `scripts/AISTS_CP0040_Quarantine_Gate.py`, but its exact-key manifest gate did not have a dedicated unit-test file wired into the static CI workflow. This checkpoint adds deterministic regression coverage and makes the workflow run those tests when the gate or tests change.

## Changes

- Added `tests/test_cp0040_quarantine_gate.py`.
- Added checks for the frozen manifest SHA-256 and 969-row population, fail-closed behavior on a hash mismatch, exact interval + exact integer-millisecond matching, rejection of fractional/negative timestamp tokens, rejection of unsupported intervals, duplicate case IDs, and any manifest claiming a closed case or selected canonical source.
- Updated `.github/workflows/cp0165-4h-audit-tests.yml` to compile the CP-0040 gate, execute its dedicated tests, and include the gate/test paths in both pull-request and main-push trigger filters.
- This is a test-coverage change only. It does not edit CP-0040 rulebook, manifests, dispositions, strategy code, or gate decisions.

## Validation boundary

The workflow must run on the exact final branch HEAD before this checkpoint is called CI-verified. A green result will prove only that the bounded static/regression suite passes; it will not adjudicate any source case, authorize quarantine application, close G0, validate a strategy, or establish profitability.

No candidate build, acceptance-grade market backtest, source promotion, or live signing/broadcast/order action is authorized or performed by CP-0272.

## Gate status

- Frozen CP-0040 rulebook: unchanged.
- Canonical historical source: `NONE`.
- Global G0: `BLOCKED_GLOBAL`.
- G2 current 23 candidates: remain `FAIL`.
- Profitability: `NOT_ESTABLISHED`.
- Live signing / public broadcast / exchange orders: `BLOCKED`.

## Next

Verify the terminal CI result against the exact final commit SHA. If a test fails, inspect the actual failing step and make the smallest evidence-backed correction. Do not weaken the frozen gate or change expected rulebook identity/population to make tests green.
