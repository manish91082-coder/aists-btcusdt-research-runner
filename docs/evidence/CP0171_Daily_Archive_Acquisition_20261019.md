# CP-0171: Official BTCUSDT Spot Daily Archive Acquisition

**Date:** 2026-10-19  
**Repository:** \`manish91082-coder/aists-btcusdt-research-runner\`  
**Branch:** \`cp-0171-daily-archive-acquisition\`  
**Workflow run:** [39223659657](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39223659657)  
**Run commit:** \`c2a4c72f42944980c523cb514e81135b18c68f09\`

## Decision

**PASS_INTEGRITY.** The bounded acquisition downloaded and verified all 108 expected daily archives for BTCUSDT Spot from 2026-10-01 through 2026-10-18 across 5m, 15m, 30m, 1h, 4h and 1d. All 108 downloaded archive SHA-256 values matched a filename-bound official \`.CHECKSUM\` sidecar. ZIP CRC, one-CSV-member, parse, duplicate-open-time, interval-grid, UTC-date and expected per-day row-count checks reported zero review rows and zero integrity failures.

This establishes byte integrity and basic structural validity for the downloaded files. It does **not** establish canonical historical source authority or clear G0.

## Frozen acquisition scope and counts

| Interval | Daily rows expected | Days | Rows validated |
|---|---:|---:|---:|
| 5m | 288 | 18 | 5,184 |
| 15m | 96 | 18 | 1,728 |
| 30m | 48 | 18 | 864 |
| 1h | 24 | 18 | 432 |
| 4h | 6 | 18 | 108 |
| 1d | 1 | 18 | 18 |
| **Total** |  |  | **8,334** |

- Expected archive count: 108.
- Status counts: \`DOWNLOADED_HASH_MATCH=108\`.
- Filename-bound official sidecar SHA-256 matches: 108/108.
- Integrity failure rows: 0.
- Review-required rows: 0.
- Self-tests: 8/8 PASS.
- Unit tests: 5/5 PASS.
- Acquisition runtime reported by the workflow: about 15.4 seconds.
- No Binance REST API, Colab, candidate build, backtest, paper run, or exchange action was used.

## Evidence artifact

- [Download the CP-0171 raw archives and verification evidence](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39223659657/artifacts/12172662597)
- Artifact ID: \`12172662597\`.
- Artifact size: 524,391 bytes.
- Artifact ZIP SHA-256 digest reported by GitHub: \`643ad33b015e4778d03e5d295b0b187e5b649d0cbe31847afaec1a1e8f36ebc2\`.
- Artifact contains 108 raw ZIP archives, 108 official sidecars, the CSV manifest and JSON summary (218 files total).
- Manifest SHA-256: \`c768c2cb04a9fa68386e76a0ae0295288ee53f881ed0280def2aa2ea85067d9d\`.
- GitHub artifact retention expiry: 2026-11-18 08:34 UTC. Download it and retain it in Drive if the raw archive bundle is needed beyond that date. Raw market data was deliberately not committed to Git.

## Locked gates, unchanged

- G0: \`BLOCKED_GLOBAL\`; canonical historical source: \`NONE\`.
- G2: \`FAIL_CURRENT_23_CANDIDATES\`.
- G3: \`BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT\`.
- G4: \`INSUFFICIENT_EVIDENCE\`.
- G6: \`NOT_BUILT\`.
- G7: \`LIVE_BLOCKED\`.
- Profitability: \`NOT_ESTABLISHED\`.
- CP-0152 strategy proposal: pending explicit approval.

No missing bar was fabricated, no source case was closed, and no data-selection policy was applied. The newly acquired October daily archives are an additional verified source snapshot, not permission to rewrite the provisional candidate or run a backtest.

## Next admissible step

Reconcile this new daily snapshot with the frozen monthly inventory by exact archive/date keys and report only new conflicts or coverage changes. Do not rerun the completed checksum scan. Do not build a candidate or backtest while G0 remains blocked and CP-0152 remains unapproved.
