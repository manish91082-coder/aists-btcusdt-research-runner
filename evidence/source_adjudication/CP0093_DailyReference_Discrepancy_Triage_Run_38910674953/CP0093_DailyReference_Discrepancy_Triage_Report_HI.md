# CP-0093: Daily-reference discrepancy triage

Status: PASS_DAILY_REFERENCE_DISCREPANCY_TRIAGE_COMPLETE_SOURCE_AUTHORITY_OPEN

## Evidence integrity
- Source audit: PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED, checks 98/98 PASS.
- Daily references: 16 ZIP/.CHECKSUM pairs reused from previous Actions artifact 11993600932; archive hashes matched sidecar tokens and ZIP CRC passed 16/16. This triage downloaded zero new archives.
- Monthly archives: 14 cached ZIPs matched the frozen CP-0041 manifest and CRC; downloads=0.

## Raw-row results (exact open-time key; raw tokens preserved)
- Union rows: 1992; shared keys: 1982; exact raw pairs: 1550; divergent raw pairs: 432.
- Divergence classes: 415 ignore-only rows; 3 close_time-plus-ignore rows; 14 economic-field divergent rows.
- Daily-only keys: 0; monthly-only keys: 10; absent expected-grid keys: 10. Coverage review is required for the two 2017-12-04 periods at 5m and 15m.
- Economic field counts: {"close": 14, "high": 7, "low": 8, "number_of_trades": 14, "open": 4, "quote_asset_volume": 14, "taker_buy_base_asset_volume": 11, "taker_buy_quote_asset_volume": 11, "volume": 14}.

## Decision boundary
- All 16 target cases remain open for source-authority review. Canonical source NONE; cases closed=0.
- The original worklist and market-data rows are not mutated. No timestamp shifting/rounding, row merge/replacement/deletion, synthetic candles, backtest or strategy promotion.
- Global G0 remains BLOCKED_GLOBAL; G2 remains FAIL for the current 23 candidates; G7 remains LIVE_BLOCKED.

## Next bounded action
- Review the 14 exact-key economic conflicts and 10 monthly-only keys against the frozen CP-0040 rulebook, one evidence-linked case at a time. Do not auto-prefer the daily or monthly archive.
