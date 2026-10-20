# CP-0278 — Exact-Key Quarantine Enforcement Regression Tests (HI)

**Date:** 2026-10-20  
**Branch:** `cp-0120-ai-brain-foundation`  
**Final verified HEAD for this checkpoint:** `e86b145a75002caba5521d547d2d9ba035b969f8`  
**Workflow:** https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39367233474

## Work completed

1. Added `tests/test_cp0026_quarantine_enforcement.py`.
2. Added a dedicated step to `.github/workflows/cp0120-ai-brain-tests.yml` to run `python -m unittest discover -s tests -p 'test_cp0026_quarantine_*.py' -v`.
3. Re-fetched branch HEAD and workflow run from GitHub after the changes.
4. Exact-head Actions run `39367233474` completed with conclusion `success`. Job steps verified successful: compile brain modules, existing brain unit tests, and CP-0026 exact-key quarantine enforcement tests.

## Regression coverage added

- Exact interval + timestamp key is quarantined.
- Same timestamp under a different interval is not accidentally matched.
- One-millisecond differences are not rounded into a match.
- Non-integer, fractional, empty, and negative timestamp tokens fail closed.
- Manifest SHA-256 mismatch rejects the candidate gate.
- Unresolved non-row blockers reject the candidate gate.

## Scope and limitations

These are deterministic software regression tests only. They do not read market archives, build real candidate data, run historical backtests, run paper sessions, or establish strategy performance. A passing test proves only the tested behavior under the test inputs.

## Frozen gates remain unchanged

- G0: `BLOCKED_GLOBAL`
- Canonical historical source: `NONE`
- G1: `PARTIAL_SYSTEM_LEVEL`
- G2: existing 23 candidates `FAIL`; none promoted
- G3: blocked; material quarantine effects unresolved
- G4: `INSUFFICIENT_EVIDENCE`
- G5: `NOT_RUN`
- G6: adaptive AI `NOT_BUILT` / not validated
- G7: `LIVE_BLOCKED`
- Profitability: `NOT ESTABLISHED`

Independent source adjudication issue #8 and official Binance issue #504 remain required provenance paths. No source was selected, no source case was closed, and CP-0040 was not weakened.

## Next bounded action

Audit the real candidate-builder execution path for a fail-closed guarantee that its production input filtering is applied before any candidate artifact is written, including derived 1mo construction and truthful reporting of quarantined rows. Add a regression test for any confirmed gap. Do not execute the production build while G0 remains blocked. Do not rerun generic archive scans or claim real candidate filtering from the helper tests alone.

## Safety

Live signing, public broadcast, and Binance order placement remain blocked. Automatic stop-loss and take-profit are not authorized. No real trading or profitability claims are made.