# CP-0107: आठ close-time-only conflicts, joined evidence

Diagnostic checks: 5/5 PASS.
Frozen CP-0040 rulebook SHA-256: `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
CP-0041 pack SHA-256: `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`; ZIP CRC PASS, 19 members, payload hashes 18/18 PASS.
CP-0041 shared ledger SHA-256: `ad5fce519de380468999aa7ef98fb7397d3b74e4283013dfac5596e4de68a19e`.
CP-0106 verified source manifest SHA-256: `015709030834ec87c6d76a0b0a4e892650bf7e0949cfc6e6d61ea8659a35a5a1`.

| Date | Interval | Expected close (UTC) | Monthly delta | Daily delta | Proposal |
|---|---|---|---:|---:|---|
| 2017-09-06 | 5m | 15:59:59.999 | +1 ms | 0 ms | Monthly close_time only |
| 2017-09-06 | 15m | 15:59:59.999 | +1 ms | 0 ms | Monthly close_time only |
| 2017-09-06 | 30m | 15:59:59.999 | +1 ms | 0 ms | Monthly close_time only |
| 2017-09-06 | 1h | 15:59:59.999 | +1 ms | 0 ms | Monthly close_time only |
| 2017-09-06 | 4h | 15:59:59.999 | +1 ms | 0 ms | Monthly close_time only |
| 2018-02-08 | 4h | 03:59:59.999 | 0 ms | -12,705,211 ms | Daily close_time only |
| 2018-02-08 | 1d | 23:59:59.999 | 0 ms | -84,705,211 ms | Daily close_time only |
| 2019-11-25 | 4h | 03:59:59.999 | 0 ms | -7,200,000 ms | Daily close_time only |

All eight keys and monthly/daily archive plus sidecar hashes match CP-0041 and CP-0106 evidence. Selected economic fields match 8/8. In the five 2017 rows the non-economic `ignore` field differs; it is not the selected conflict field.
Only the close_time metadata field gets a proposal; archive acceptance is NOT_ASSESSED. All cases remain OPEN_REVIEW_REQUIRED_NO_CANONICAL_SOURCE; root cause OPEN. No source bytes or timestamps changed; no backtest or promotion.

CSV: `evidence/source_adjudication/CP0107_CloseTimeOnly_FieldDisposition_Final.csv`; 8 rows, 7664 characters, SHA-256 `473b149630edb6ee86b1720e2ffa4dd1afa7f022894bf5951ca398199319731c`.

Global gates unchanged: G0 BLOCKED_GLOBAL; G1 PARTIAL_SYSTEM_LEVEL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL; G4 INSUFFICIENT_EVIDENCE; G5 NOT_RUN; G6 NOT_BUILT; G7 LIVE_BLOCKED.
