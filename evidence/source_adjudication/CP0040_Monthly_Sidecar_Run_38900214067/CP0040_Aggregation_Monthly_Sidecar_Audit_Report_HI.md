# CP-0040: 11 open aggregation buckets ka monthly official checksum audit

- Status: PASS_MONTHLY_SIDECARS_MATCH_CACHED_ARCHIVE_BYTES
- Scope: official monthly checksum text only; no ZIP downloads or daily archive acquisition.
- All 11 daily roll-up comparisons previously matched daily parents, while the frozen monthly mismatch signature remained in all 11.
- Sidecar result: 14/14 official monthly checksum sidecars matched the cached monthly ZIP hashes. ZIP downloads=0; daily archive downloads=0.
- A sidecar PASS authenticates current cached monthly ZIP bytes only. It does not select a canonical source or close a bucket.
- G0 remains BLOCKED_GLOBAL; all 11 blockers remain open; canonical source NONE; no backtest or strategy promotion.
