# CP-0040 Exact-Key Quarantine Manifest: Aggregation Extension

**PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN** — 14/14 checks PASS.

- Prior manifest: 1411 rows; aggregation evidence contains 78 source-row records across 35 unique exact keys.
- Existing keys enriched: 19; new unique keys added: 16; final manifest: 1427 rows / 1427 unique keys.
- Manifest SHA-256: e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a; blocker ledger SHA-256: f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36.
- All 11 aggregation buckets have their parent/child exact row keys represented in the quarantine manifest. No timestamps were inferred; keys came from the committed row-level evidence file.
- The 11 aggregation relationships remain open: daily child rollups match daily parents, while the monthly frozen mismatch signature persists. This is not proof of canonical-source authority.
- Candidate eligibility remains BLOCKED until a rulebook-aligned disposition of these 11 relationships is recorded. No candidate build/backtest; no source cases closed.
