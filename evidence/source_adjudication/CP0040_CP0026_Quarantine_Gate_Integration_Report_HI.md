# CP-0040 / CP-0026 Quarantine Gate Integration — 2026-10-16

## परिणाम
**PASS: builder gate integration and fail-closed regression tests. Candidate build remains BLOCKED.**

## Published exact-key manifest
- Build workflow: [GitHub Actions run 38882377148](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38882377148), terminal `success`.
- Manifest validation: 17/17 checks PASS.
- Row-level manifest: 969 rows and 969 unique exact `(interval, open_time_ms)` keys.
- Class counts: 452 daily-only, 457 monthly-only, 52 shared economic conflicts, 8 close-time-only.
- The 450 off-grid February-2018 rows are a subset of the 909 unmatched rows and were not double-counted.
- Separate non-row blocker ledger: 27 rows, comprising 11 residual aggregation buckets and 16 missing daily-reference acquisition records.
- Manifest SHA-256: `d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819`.
- Non-row blocker ledger SHA-256: `d0126152a58baecd8f61bcdcc21286ecffacba6427e7b09696ca63db33c1f0d0`.
- Evidence directory: `evidence/source_adjudication/CP0040_Run_38882377148/`.

## CP-0026 builder changes
- Added a fail-closed manifest gate to `scripts/AISTS_CP0026_Research_Candidate_Builder.py`.
- Before candidate data processing, the builder validates manifest presence, summary status, byte SHA-256, row count, schema, exact-key uniqueness, case-class counts, open case status, and canonical source NONE.
- Any non-row blockers or a non-ready gate status stops the build before candidate output is created.
- When eligibility is later approved, exact-key matches from selected source rows are excluded from candidate output and written to `cp0026_quarantined_candidate_rows.csv` with case IDs and source provenance. No timestamp rounding or row mutation is used by the partition helper.
- The current manifest and blocker files must be placed under the configured data root's `reports/` directory before a normal Colab builder invocation; missing gate files fail closed.

## Verification
- Builder gate test workflow: [GitHub Actions run 38882676704](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38882676704), terminal `success`.
- Runner checks: 11/11 PASS.
- Builder gate regression tests: 5/5 PASS, including actual manifest/hash/count preflight, fail-closed refusal due to 27 non-row blockers, exact-key exclusion, one-millisecond non-match, cross-interval non-match, and raw-token preservation.
- All 23 Python sources parsed successfully in the runner preflight.
- Artifact ZIP CRC: PASS; runner and child summary JSON parsed from the downloaded artifact.

## Explicit limits
- No candidate dataset was built.
- No market-data backtest was run.
- The builder's full market-data path and output quarantine audit were not exercised, because the eligibility gate correctly refuses to proceed with 27 unresolved non-row blockers.
- This manifest re-hashes the published compressed index and validates the linked evidence matrices; it is not a fresh re-hash of the original CP-0041 package/rulebook raw bytes.
- No canonical source was selected; no source case was closed; no strategy was promoted. Live signing, public broadcast, and exchange orders remain blocked.

## Next bounded action
Resolve or formally disposition the 27 non-row blockers using exact source evidence, refresh the manifest/status without inventing timestamps, then run the gate regression again. Do not build a candidate or backtest until the gate reports candidate eligibility ready.
