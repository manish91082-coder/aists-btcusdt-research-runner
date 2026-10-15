# CP-0107: seven residual December 2020 monthly-only rows

Status: PASS_SEVEN_RESIDUAL_EXACT_KEY_AUDIT; checks 30/30 PASS.

## Sources verified

- Original CP-0041 worklist member SHA-256: f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f; package SHA-256: 23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc.
- The seven target row snapshots are exact CP-0041 worklist entries, and their 12 raw tokens were matched against the monthly archive rows.
- Four monthly and four daily ZIPs were reused from the pre-existing cache. Every ZIP SHA-256 and CRC was checked against the frozen 66-source manifest. Cached sidecar bytes, where present, were also rehashed; absent sidecar bytes are explicitly marked reference-only without network retrieval.

## Exact key result

- Seven exact monthly rows audited; daily exact-open counterparts found: 0; absent from verified daily archive bytes: 7.
- All monthly rows have flat OHLC 22646.53000000 with zero volume/trades; the shared close-time anomaly token is preserved as raw evidence where present.

## Disposition

All seven remain OPEN_REVIEW_REQUIRED. No canonical source or root cause selected; no cases closed. No timestamp shift/rounding, row edit, merge, synthetic candle, backtest rerun or strategy promotion.
