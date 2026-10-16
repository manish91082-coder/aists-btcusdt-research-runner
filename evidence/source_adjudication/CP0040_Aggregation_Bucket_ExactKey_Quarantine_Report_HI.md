# CP-0040 Aggregation-Bucket Exact-Key Quarantine Extension — 2026-10-16

## परिणाम
**PASS: 14/14 aggregation extension checks; CP-0026 gate regression 5/5. Candidate build remains BLOCKED.**

## Exact-key coverage
- Manifest extension/publish: [GitHub Actions run 38883792900](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883792900), terminal success.
- Row evidence: 78 records across 11 aggregation buckets and 35 unique exact keys.
- Before this extension, 19 of those 35 keys were already quarantined. Added the remaining 16 exact keys from the committed row-evidence CSV. All 35 parent/child keys are now represented in the current manifest.
- Current manifest: 1,427 rows / 1,427 unique keys.
- Manifest SHA-256: `e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a`.
- Current pointer: `evidence/source_adjudication/CP0040_Current_Manifest.json`.
- Evidence directory: `evidence/source_adjudication/CP0040_Run_38883792900/`.

## What this proves, and what it does not
- All row keys present in the aggregation bucket evidence have exact interval + millisecond timestamp identities and are represented in the quarantine manifest.
- Daily child rollups match daily parents in all 11 buckets; the frozen monthly mismatch signature persists in all 11.
- No parent/child values were reconciled, no canonical source was selected, and no root cause was declared.
- The 11 cross-interval aggregation relationships remain open. Their exact rows are quarantined, but that does not automatically establish that CP-0040 G0 may be opened. The acceptance decision remains blocked until the unresolved relationship cases receive an explicit rulebook-aligned disposition.

## CP-0026 gate regression
- [GitHub Actions run 38883871540](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883871540), terminal success.
- Runner checks: 11/11 PASS.
- Gate tests: 5/5 PASS against the current 1,427-key manifest.
- The builder correctly refuses to proceed because 11 aggregation relationship blockers remain.

## Explicit limits
No candidate dataset or backtest was run. No source case was closed; no strategy was promoted. Live signing, public broadcast and exchange orders remain blocked.
