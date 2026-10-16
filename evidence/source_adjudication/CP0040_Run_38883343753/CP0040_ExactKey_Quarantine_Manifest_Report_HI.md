# CP-0040 Exact-Key Quarantine Manifest: Acquisition Extension

**PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN** — 19/19 checks PASS.

- Prior manifest: 969 rows; acquisition evidence reviewed: 442 open row keys.
- New unique exact keys added: 442; existing keys enriched with acquisition provenance: 0.
- Final manifest: 1411 rows / 1411 unique (interval, open_time_ms) keys; SHA-256 d62c30c8ac7a4e5241b48e79884e68395fd1904826cfd70549886876269642b2.
- Acquisition comparison: 1,550 exact raw pairs, 432 divergent raw pairs (14 economic-field divergent; 418 non-economic raw-field divergent), 10 monthly-only keys, 0 daily-only keys.
- The 10 absent expected-grid keys match the 10 monthly-only keys exactly; they are represented as open row-level quarantine cases, not synthetic candles.
- All 16 official daily ZIP/.CHECKSUM pairs were already acquired and hash-verified in the prior audit; no downloads were performed by this extension task.
- The 16 archive-acquisition blockers were replaced by row-level evidence. Remaining non-row blockers: 11 residual aggregation buckets. No canonical source chosen; no source cases closed.

## Gate decision
Candidate eligibility remains BLOCKED by the 11 unresolved cross-interval aggregation buckets. No candidate dataset or backtest was run. No timestamps were shifted or rounded, no rows were merged/replaced/deleted, and no synthetic candles were created.
