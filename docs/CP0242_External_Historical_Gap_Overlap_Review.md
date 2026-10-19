# CP-0242 — External historical gap overlap review

Recorded: 2026-10-19  
Workstream: Historical source adjudication / BTCUSDT Spot 4h  
Decision: `CP0242_EXTERNAL_GAP_CORROBORATION_G0_STILL_BLOCKED`  
Mode: Read-only review of existing public Binance Public Data issue records and frozen project findings. No archive download, API query, candidate build, or backtest.

## 1. Purpose

Check whether public reports of missing BTCUSDT Spot data overlap the already frozen 4h gap/source dispositions. Distinguish timestamp overlap and community corroboration from an official source decision.

## 2. External evidence

### Issue #374 — BTCUSDT Spot 1m data gap on 2017-09-06

URL: https://github.com/binance/binance-public-data/issues/374  
Observed current state: OPEN; one comment; last updated 2024-11-20.

The issue author identifies the daily Spot archive `BTCUSDT-1m-2017-09-06.zip` and reports missing data from Unix millisecond timestamp `1504713600000` through `1504738800000`. The first timestamp converts to `2017-09-06T16:00:00Z`, exactly matching the project's existing 4h source-key discrepancy `UNMATCHED-D-4h-1504713600000`. In the project’s frozen CP-0198/0199 disposition, the daily 4h reference contains a zero-trade placeholder with invalid 4h close-time span at that key; it is not accepted as a valid market candle.

The only issue comment advises sorting by open_time and is not a Binance maintainer response. The report concerns a 1m archive and does not independently reproduce the exact 4h row, prove the reason for its placeholder, or identify a canonical 4h source.

### Issue #379 — BTCUSDT Spot 1m data on 2018-02-08

URL: https://github.com/binance/binance-public-data/issues/379  
Observed current state: OPEN; two comments; last updated 2026-06-19.

The author reports missing daily 1m data for 2018-02-08. One commenter says only 29 records were present; another asserts “Binance was down that day.” These are community comments, not official confirmation. This is period-level corroboration of a possible coverage issue, not an exact-key reproduction of the project’s 4h gap windows or a source-authority ruling.

## 3. Mapping to frozen project evidence

- CP-0200 records 17 missing 4h open-time slots: 16 `UNRESOLVED_MISSING_KEY_BOTH_SOURCES` and one `UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT`.
- CP-0201 identifies the exact-key overlap `UNMATCHED-D-4h-1504713600000`; the remaining 16 items are gap-window-only and must not be fabricated into row cases.
- Issue #374's reported 1m missing range begins at the same Unix timestamp as the already-recorded 4h placeholder conflict. This is a useful cross-interval lead, but not independent validation of the 4h record or evidence that fills the missing 4h slot.
- Issue #379 is consistent with historical coverage risk around February 2018, but the public report/comment does not supply the exact 4h keys needed to map or close any of the 16 gap-window-only items.
- Both issues remain community evidence. Neither includes a Binance maintainer’s canonical-source decision, point-in-time version receipt, or official explanation of the project’s 4h values.

## 4. Decision

`CP0242_EXTERNAL_GAP_CORROBORATION_G0_STILL_BLOCKED`

This review adds a timestamp-level cross-interval lead for the 2017-09-06 placeholder conflict. It does not close any source case, accept a placeholder as a candle, fill any 4h gap, authorize candidate construction, or clear G0/G3. Canonical historical source remains `NONE`.

## 5. Next admissible action

Seek either (a) an official maintainer response or documented source/version guarantee, or (b) an authorized independent reproduction against the project's preserved raw inputs that records exact timestamps, fields, hashes, and a separately scoped policy application. Do not substitute current API values silently for historical point-in-time values, repeat cache/checksum-only scans, or implement/backtest CP-0152 before explicit approval and gate clearance.

No market-data archive was downloaded, no market-data API was queried, no candidate/backtest/paper run was executed, and no exchange account/order/signature/broadcast action occurred.
