# CP-0107: CP-0041 996-row worklist disposition delta

Status: PASS_450_ROW_DISPOSITION_DELTA_READY; checks 11/11 PASS.

## Scope and provenance

- Original CP-0041 worklist: 996 rows; SHA-256 f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f; source package SHA-256 23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc. The worklist member is not overwritten.
- Only the 450 crosswalk case IDs are included in this append-only disposition delta. Exact case-ID mapping: 450/450; monthly archive hash matches: 450/450; all 12 monthly raw fields exact: 450/450.
- Proposed disposition for those 450 rows: QUARANTINE_REVIEW_REQUIRED. Remaining 546 original rows are explicitly unchanged.

## Evidence and unresolved conditions

- Exact daily open-time counterpart exists for 0/450 monthly rows. Fixed-shift diagnostic rows are present for 448 and absent for 2; every present mapped row differs in at least one non-open field. Open price differs in 442, close_time in 447 and volume in 448.
- Timestamp shift is diagnostic only. Original exchange-time semantics/provenance remain necessary; no canonical source selected; root cause OPEN_NOT_ESTABLISHED; cases closed 0.

## Safety / non-mutation

This is a review-only patch file, not a source archive or full-worklist replacement. No raw rows were changed, shifted, merged, replaced or deleted; no synthetic candles; no backtest rerun or strategy promotion.
