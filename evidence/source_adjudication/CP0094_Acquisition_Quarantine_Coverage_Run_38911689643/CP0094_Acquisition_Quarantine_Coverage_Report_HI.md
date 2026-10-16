# CP-0094: exact-key acquisition quarantine coverage audit

Status: PASS_24_ACQUISITION_KEYS_CONFIRMED_QUARANTINED_SOURCE_AUTHORITY_OPEN

## Frozen rulebook and provenance
- Rulebook bytes verified: 10,630; SHA-256 5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0.
- CP-0040 exact-key quarantine manifest SHA-256 e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a; 1,427 rows with unique (interval, open_time_ms) keys.
- Upstream CP-0107 daily reference audit: PASS_DAILY_REFERENCE_DISCREPANCY_TRIAGE_COMPLETE_SOURCE_AUTHORITY_OPEN with 14/14 CP-0093 discrepancy triage checks; 16/16 daily ZIP/.CHECKSUM pairs and 14/14 monthly cache ZIPs already hash/CRC verified; no new download in this audit.

## Exact-key coverage
- Economic conflicts: 14/14 exact keys map to class ACQUISITION_ECONOMIC_CONFLICT, with matching CP-0107 source case ID, raw economic field list and both monthly/daily archive hash references.
- Missing expected daily-grid keys: 10/10 exact keys map to class ACQUISITION_MONTHLY_ONLY_ROW and matching CP-0107 source case ID.
- Total: 24/24 acquisition discrepancy keys explicitly covered by frozen CP-0040 quarantine.

## Decision boundary
- This proves quarantine coverage only. It does not decide which verified archive is canonical, establish same-candle equivalence, or close any conflict.
- Global G0 remains BLOCKED_GLOBAL because 11 non-row aggregation relationships and broader source-adjudication debt remain open. G2 remains FAIL for current 23 candidates; G7 remains LIVE_BLOCKED.
- No row/worklist changes, no network/archive downloads, no candidate build or backtest, no strategy promotion, no exchange action.

## Next bounded action
- Use this 24-key coverage evidence to prioritize source-authority adjudication: exact economic conflicts remain dual-source disputes; ten missing daily-grid keys remain missing-reference cases. Keep the conservative quarantine policy frozen and the builder fail-closed.
