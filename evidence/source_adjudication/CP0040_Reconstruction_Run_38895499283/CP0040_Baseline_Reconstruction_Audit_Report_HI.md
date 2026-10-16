# CP-0040 Baseline Reconstruction Audit

- Status: `PASS_BASELINE_INPUTS_RECONSTRUCTED`
- The 4h and 1d inputs were reconstructed in an isolated temporary directory using cached monthly archives and cached daily references.
- The 1mo series was re-derived from the reconstructed daily candidate using the same reviewed CP-0026 serialization helper.
- Monthly ZIPs used: 220; daily reference ZIPs used: 80; daily .CHECKSUM sidecars verified: 80.
- Network/archive acquisition: none. Raw cache archives were read-only.

## Exact decompressed-content checks
- 4h: `19975` rows; reconstructed CSV SHA-256 `1c7377e3dc26c791133d2ea0bf0a8b46cbec4287f4dc37a6032c79044c4ed357`; frozen anchor `1c7377e3dc26c791133d2ea0bf0a8b46cbec4287f4dc37a6032c79044c4ed357`; match=True.
- 1d: `3332` rows; reconstructed CSV SHA-256 `8cefa74df159591f87cdcfcd203ed53d35562fea041332645c1f478b53a24556`; frozen anchor `8cefa74df159591f87cdcfcd203ed53d35562fea041332645c1f478b53a24556`; match=True.
- 1mo: `110` rows; reconstructed CSV SHA-256 `09c4a052cd879cac035c6fdbe61e830947c4bc5f09d14017168dcc2af38f9278`; frozen anchor `09c4a052cd879cac035c6fdbe61e830947c4bc5f09d14017168dcc2af38f9278`; match=True.

## Gate
- This is an input reproducibility audit only, not a backtest or candidate-promotion event.
- G0 remains `BLOCKED_GLOBAL`; the 11 non-row aggregation blockers remain open.
- Canonical source remains `NONE`; promotion and live exchange actions remain blocked.
