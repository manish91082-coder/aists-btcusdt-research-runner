# AISTS CP-0107: Row-by-row source disposition draft (Hindi)

## Execution and parent evidence
- Parent run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38730420808
- Parent commit: `b6ddcc9ed6c486570dc0c2da8857dd013cba18ae`; `main` HEAD observed at resume: `a78b6e0dd531484a0d7f3e1345c420a76c115237`. Current HEAD is a descendant with CP-0106 evidence persistence. Do not equate the run checkout SHA with current HEAD.
- CP-0106 artifact: ID `11969978987`, 579,598 bytes, SHA-256 `cdddab3be37f5c593d5cd42ac6c6f72b53f5b3a3fc4dae1218c3bd833850adb4`; ZIP CRC PASS.
- CP-0106 verified 66/66 targeted source objects. Research status was `PASS_DIAGNOSTICS_ONLY`, not strategy acceptance.

## Frozen authority files
The frozen CP-0040 rulebook and current source-disposition ledger were not found in the canonical repository tree searched at CP-0107 start. This checkpoint therefore makes no claim to apply absent thresholds or formally close cases. Decisions requiring those authority rules remain OPEN.

## A. February 2018 off-grid segments
- CP-0106 reports 10 monthly off-grid segments totaling 450 rows: 5m 241, 15m 81, 30m 85, 1h 43. Remainders are 194,789 ms (5m), 794,789 ms (15m), and 1,694,789 ms (30m/1h).
- CP-0104's exact counterpart search found zero matches for OHLC, OHLC+base-volume and full economic signatures across the 909 unmatched rows. CP-0105 also found no exact numeric equality at nearest timestamp. This does not identify upstream cause or confer source authority.
- Proposed status: `QUARANTINE_REVIEW_REQUIRED` for all 10 segments. Root cause/provenance stays OPEN. No shift, rounding, merge, replacement or deletion.
- **Specific limitation:** CP-0106 committed segment inventory includes boundaries/counts, not every individual raw value/line for all 450 rows. CP-0107 does not claim row-level economic adjudication of these rows is complete. The next focused job must extract each of the 450 monthly rows and exact daily coverage with raw tokens, line numbers, ZIP SHA-256 and checksum sidecar SHA-256 from the verified cache.

## B. December 21, 2020 shared close-time and flat/zero-volume anomaly
- The checksum-verified 12:30–14:15 UTC source window contains 59 rows: 33 monthly, 26 daily, across 5m/15m/30m/1h.
- 16 monthly rows have OHLC=`22646.53`, base volume `0`, trade count `0`. Treat them as anomaly candidates requiring review, not proven corruption.
- Eight rows share close-time `1608558440521` = `2020-12-21 13:47:20.521 UTC`: 4 daily and 4 monthly. Per-row close-time deltas and OHLC/volume/trade/economic fields are in `CP0107_Dec2020_RowDisposition.csv`.
- 34 parent-child roll-up comparisons were inspected. 25 are exact on the available exact child sets; 9 are review-required due missing exact 5m children. Missing-child aggregates stay unavailable; no synthetic candle or substitute aggregate was generated.
- Common row-content/close-time anomaly is a candidate interpretation only. Upstream root cause is not established; keep OPEN/REVIEW_REQUIRED.

## C. Eight close-time-only conflicts
Frozen arithmetic reference used for this diagnostic is `expected_close_time = open_time + interval_ms - 1 ms`.
- 2017-09-06: 5m, 15m, 30m, 1h, 4h. Daily close time matches expected boundary; monthly is +1 ms. Proposed disposition is limited to the close_time metadata field: monthly value fails this boundary comparison, daily value matches.
- 2018-02-08: 4h and 1d. Monthly close time matches boundary; daily deltas are -12,705,211 ms and -84,705,211 ms.
- 2019-11-25: 4h. Monthly close time matches boundary; daily delta is -7,200,000 ms.
- All 8 exact row keys, source hashes, and sidecar hashes are in `CP0107_CloseTimeOnly_FieldDisposition.csv`. These are field-level proposals only; all cases remain OPEN. No archive acceptance or canonical-source selection is implied.

## What this checkpoint changes
This is a **draft evidence package**, not completed row adjudication. It structures evidence and proposed dispositions for the February segments, December rows/rollups, and eight close-time-only records. It does not modify raw evidence or candidate data; does not close source cases; does not select sources; and does not rerun or promote strategies.

## Next limited action
1. Locate/restore the frozen CP-0040 rulebook and authoritative source-disposition ledger.
2. Run one cache-only CP-0107 extraction for all 450 February monthly off-grid rows, including exact daily coverage and raw provenance.
3. Reconcile that evidence against the frozen rulebook/ledger before closing any case.

## Gates and safety
G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`. No Binance market-data REST API, signing, public broadcast, exchange order, raw archive repair, timestamp shift/rounding, canonical source selection, candidate promotion or backtest rerun was performed.
