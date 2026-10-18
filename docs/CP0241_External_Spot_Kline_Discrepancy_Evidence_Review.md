# CP-0241 — External Binance Spot Kline Discrepancy Evidence Review

Recorded: 2026-10-18  
Workstream: Historical source adjudication / BTCUSDT Spot 4h  
Decision: `CP0241_EXTERNAL_CORROBORATION_G0_STILL_BLOCKED`  
Mode: Read-only review of public Binance Public Data issue records; no archive download or market-data execution.

## 1. Purpose and scope

Check whether newly surfaced public reports provide decision-relevant evidence for the existing G0 source-provenance and cross-timeframe aggregation blockers. This review distinguishes community-submitted observations from official maintainer answers. A report on the official issue tracker is not itself a Binance-maintainer confirmation or a canonical-source declaration.

## 2. Public evidence reviewed

### Issue #475 — monthly Spot klines disagree with daily archives and API

URL: https://github.com/binance/binance-public-data/issues/475  
Observed state at review: OPEN; one comment.

The issue author reports 398 conflicting rows across multiple Spot symbols and 1m/5m/15m/1h intervals on 2020-12-21 and 2021-09-29. The author says all 398 checked rows matched the daily archive and current API/uiKlines, while monthly rows differed. This is a community-submitted claim, not a verified maintainer conclusion.

A separate commenter reports additional cross-timeframe aggregation conflicts, including BTCUSDT 4h at 2021-01-21 08:00 UTC and BTCUSDT 4h at 2022-04-13 04:00 UTC, plus other BTCUSDT/ETHUSDT 1h/4h observations. The comment says some discrepancies affect volume, quote volume, trade count and taker-volume fields; for these supplemental cases, OHLC prices were reported equal. The commenter reports unchanged hashes across 36 re-downloaded monthly ZIPs. These statements remain community evidence until independently reproduced against frozen inputs or answered by maintainers.

### Issue #505 — BTCUSDT Spot 5m malformed close_time

URL: https://github.com/binance/binance-public-data/issues/505  
Observed state at review: OPEN; zero comments.

The issue author reports a BTCUSDT 5m row in the March 2023 monthly archive whose close_time is earlier than the expected interval end, despite matching the published archive checksum. This is a 5m example, not direct evidence about the specific 4h gap keys in this project. It supports the methodological distinction between archive integrity and semantic validity, but does not determine the canonical 4h source.

### Official README boundary

URL: https://github.com/binance/binance-public-data/blob/master/README.md

The README states that Spot kline archive data is obtained from `/api/v3/klines`, provides per-ZIP checksums, and documents an archive update dated 2022-08-08 with the note “Fixed inconsistent data.” This documents a correction/update history, but does not by itself establish the exact publication time of each historical version, a complete prior-version store, or point-in-time reconstructability.

### Issue #504 — point-in-time provenance questions

URL: https://github.com/binance/binance-public-data/issues/504  
Observed state at review: OPEN; zero comments; last updated 2026-09-27.

No maintainer answer was present at this review. The requested guarantees about prior ZIP versions, exact publication/replacement timestamps, correction completeness and historical point-in-time reconstruction therefore remain unanswered in this issue.

## 3. Relevance to this project's frozen findings

- The reports are consistent with the already observed risk that checksum-valid archives can still contain semantically invalid or cross-source divergent records.
- The BTCUSDT 4h examples in the #475 comment are directly relevant to the interval family, but they concern different timestamps from the 17 missing 4h slots in the current audit. They do not fill those slots or identify a canonical source for them.
- The #475 examples primarily concern other intervals and cross-timeframe metric divergence. They do not independently reproduce all 14/35 daily-vs-monthly 4h divergences in this project's frozen evidence.
- The #505 example is 5m and must not be generalized into a claim that any specific 4h row is invalid.
- None of these records provides a verified historical point-in-time version receipt for the project's 110 monthly 4h archives.

## 4. Decision

`CP0241_EXTERNAL_CORROBORATION_G0_STILL_BLOCKED`

This review adds decision-relevant external corroboration but does not remove a gate. Canonical historical source remains `NONE`; G0 remains `BLOCKED_GLOBAL`; G3 remains `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`. No gap row is filled, no source case is closed, no quarantine is applied to production candidate scoring, and no strategy is authorized.

## 5. Next admissible action

Require one of:
1. A relevant official maintainer response or documented point-in-time/version guarantee, with scope and limits captured; or
2. An authorized independent review that reproduces the exact project-specific conflicts against preserved raw inputs and provides a separately scoped policy-application record.

Do not use current API responses as a silent substitute for historical point-in-time data. Do not treat community issue comments, checksum validity, or CI success as proof of canonical-source authority. Do not repeat the exhausted cache/checksum scans.

No archive was downloaded, no market data was queried, no candidate was built, no backtest or paper run was executed, and no exchange account/order/signature/broadcast action occurred.
