# CP-0040 Acquisition Extension + CP-0026 Gate Regression — 2026-10-16

## परिणाम
**PASS: manifest extension 19/19 checks; CP-0026 gate regression 5/5 tests. Candidate build remains BLOCKED.**

## Current manifest
- Manifest build/publish: [GitHub Actions run 38883343753](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883343753), terminal success.
- Manifest checks: 19/19 PASS.
- Current manifest pointer: `evidence/source_adjudication/CP0040_Current_Manifest.json`.
- Current run-scoped evidence: `evidence/source_adjudication/CP0040_Run_38883343753/`.
- Final manifest: 1,411 rows / 1,411 unique exact keys.
- SHA-256: `d62c30c8ac7a4e5241b48e79884e68395fd1904826cfd70549886876269642b2`.
- Class counts: 452 daily-only, 457 monthly-only, 52 shared economic conflicts, 8 close-time-only, 14 acquisition economic conflicts, 418 acquisition raw-field conflicts, 10 acquisition monthly-only rows.
- 442 newly discovered unique exact keys were added from the already verified acquisition row comparison. Existing 969 keys did not overlap those 442 keys.
- The 450 February-2018 off-grid rows remain a subset of the original 909 unmatched rows and were not double-counted.

## Acquisition evidence reconciled
- Reused verified evidence from CP-0107 run 38776970911. No new network downloads in this extension task.
- All 16 daily ZIPs and 16 official checksum sidecars had already passed hash checks; 14 monthly archives were reused and verified.
- 1,992 row comparison records: 1,550 exact raw pairs, 432 divergent raw pairs, 10 monthly-only keys, 0 daily-only keys.
- Of the 432 divergent pairs, 14 have economic-field differences and 418 have non-economic raw-field differences. All 432 remain quarantined because raw source authority is not established.
- The 10 absent expected-grid keys match the 10 monthly-only keys exactly. No synthetic candles were created.
- The 16 acquisition-stage blockers were replaced by row-level evidence. The remaining blocker ledger has 11 unresolved residual aggregation buckets.

## CP-0026 builder gate regression
- [GitHub Actions run 38883430122](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883430122), terminal success.
- Runner checks: 11/11 PASS.
- Gate tests: 5/5 PASS against the current 1,411-key manifest.
- The builder refuses to proceed because 11 residual aggregation blockers remain.
- Exact-key quarantine, one-millisecond non-match, cross-interval non-match and raw-token preservation tests passed.

## Limits and decision
- No candidate dataset built; no backtest run.
- No canonical source selected; no source case closed; no strategy promoted.
- The original CP-0041 package/rulebook bytes were not freshly rehashed in this extension run. The published compressed index and acquisition comparison bytes were rehashed against recorded evidence.
- G0 remains BLOCKED_GLOBAL. Live signing, public broadcast and exchange orders remain blocked.

## Next bounded action
Inspect the 11 residual aggregation buckets against their committed row-level evidence and determine whether each has an exact, evidence-supported disposition. Do not invent timestamps, synthesize candles, select a canonical source automatically, or build a candidate until the gate reports candidate eligibility ready.
