# CP-0107: CP-0041 daily-reference acquisition and raw-row audit

Status: PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED; checks 98/98 PASS.

## Scope

- All 16 queued daily ZIPs and 16 .CHECKSUM files are persisted byte-for-byte. This run reuses the exact bytes captured by prior Actions run 38775174019 rather than repeating the downloads.
- Fourteen existing monthly ZIPs were reused from GitHub Actions cache and checked against the frozen CP-0041 monthly manifest subset and ZIP CRC. Monthly ZIP downloads: zero.
- Daily ZIP/.CHECKSUM bytes were reused from prior run 38775174019 artifact 11993600932; every ZIP was rehashed against its own official sidecar token again. New daily network downloads: 0.
- Source package SHA-256: 23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc; original queue member SHA-256: b6660083860d5d90afc5d2661353ecf4c8f1aa2d355a9db99d6fc7a40e9b045d; monthly manifest member SHA-256: 1fa5c6ff022d7ff10f293c55c9fb933599c16b3d5d68adc86f2a9425c1e16b65; frozen CP-0040 rulebook SHA-256: 5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0.

## Exact-open comparison

- Union rows: 1992; shared keys: 1982; exact raw pairs: 1550; divergent raw pairs: 432.
- Daily-only keys: 0; monthly-only keys: 10; absent expected-grid keys recorded: 10.
- Periods needing coverage review: 2/16. See machine-readable period summary and row comparison.

## Disposition

Unequal or unmatched rows remain OPEN_REVIEW_REQUIRED. Exact-open equality is not source authority. Canonical source NONE; source cases closed 0. No timestamp shifting/rounding, row merge, replacement/deletion, synthetic candles, backtest rerun, or strategy promotion.
