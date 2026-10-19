# CP-0248: Official Historical Provenance Status Check

**Date:** 2026-10-19  
**Repository:** `manish91082-coder/aists-btcusdt-research-runner`  
**Branch:** `cp-0248-official-provenance-status`  
**Purpose:** Record a bounded, targeted check for new official point-in-time provenance relevant to the unresolved BTCUSDT Spot historical-source gate. This is an evidence-status record, not a source adjudication or policy application.

## Executive decision

**NO_NEW_DISPOSITIVE_OFFICIAL_PROVENANCE_FOUND. G0 REMAINS BLOCKED.**

A targeted check found a public question in Binance's `binance-public-data` repository, issue [#504: Spot historical data provenance: previous versions, corrections and point-in-time reconstruction](https://github.com/binance/binance-public-data/issues/504). The issue is open, has no assignee, and had zero comments when checked on 2026-10-19. It asks whether previous archive versions, publication/replacement timestamps, complete checksum history, and point-in-time reconstruction are available. It contains questions from a community user, not answers or an official maintainer determination. It therefore supplies no new provenance for this project's disputed historical keys.

The official repository [README](https://github.com/binance/binance-public-data/blob/master/README.md) states that public market data is published as daily/monthly files and lists archive update entries with old/new checksums. That confirms archive replacements can occur and that some updates are documented. It does not establish that every prior version is retained, provide a complete per-version publication timeline, or reconstruct what was available at a historical timestamp.

A separate open report, [issue #505](https://github.com/binance/binance-public-data/issues/505), describes an internally inconsistent close-time in a checksum-matching BTCUSDT 5m monthly archive. It is another community report, not a maintainer ruling and not evidence about the project's 2017 disputed 4h row. It reinforces only the narrow distinction that checksum matching establishes downloaded-byte integrity, not semantic correctness or historical version authority.

## Project-specific unresolved evidence

The currently documented source conflicts remain unresolved:

- Provisional daily-only key: **2017-09-06 16:00 UTC**. Its recorded OHLC values are all 4619.43 with zero volume and zero trades; this does not establish that it is a valid 4h candle.
- The 4h archive audit recorded **9 exact gap events containing 17 missing 4h open-time slots**; 16 of those keys were absent from the inspected monthly and daily sources.
- The cross-source aggregation review recorded **14 of 35 daily-vs-monthly bar keys divergent across 97 metric fields**, with 11 non-row aggregation blockers still open.
- The CP-0245 correction-package probe and CP-0246 public correction-directory inventory did not yield a matching correction for the unresolved key. They are not repeated here.

These are carried forward from existing project evidence, not newly recomputed in this checkpoint.

## Evidence classification

| Evidence | What it supports | What it does not support |
|---|---|---|
| Binance Public Data README and listed update log | Published archive layout; documented examples of archive updates and old/new checksums | Complete version retention, complete correction history, exact first-publication/replacement timestamps, or point-in-time reconstruction |
| Public issue #504, checked 2026-10-19 | The provenance/version-history question remains publicly raised; issue open, no comments, no maintainer answer observed | Any official answer or source decision |
| Public issue #505, checked 2026-10-19 | A community report that checksum-valid data may still have a semantic timestamp defect | A maintainer-confirmed defect, a correction for this project's key, or canonical source authority |
| CP-0247 October daily acquisition | 108/108 October 2026 daily archive checksums matched their filename-bound sidecars | Resolution of 2017 historical-source conflicts; the date ranges do not overlap |

## Gate decision and permitted next action

- **G0:** `BLOCKED_GLOBAL`; canonical historical source remains `NONE`.
- **G2:** `FAIL_CURRENT_23_CANDIDATES`.
- **G3:** `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- **G4:** `INSUFFICIENT_EVIDENCE`.
- **G6:** `NOT_BUILT`.
- **G7:** `LIVE_BLOCKED`.
- **Profitability:** `NOT_ESTABLISHED`.
- **CP-0152 strategy proposal:** `PENDING_EXPLICIT_APPROVAL`.

No source case is closed, no historical value is selected, no quarantine policy is applied, and no candidate/backtest is run.

The next admissible gate-changing input remains one of:
1. New official, key-specific historical-version/correction provenance for the disputed archive bytes/rows and 4h gaps; or
2. An explicitly authorized independent reviewer, followed by a separate, scoped review/application record where required.

No comment was posted to Binance's repository, no reviewer was invited, and no external issue or PR was modified. Those actions are not authorized by this task.

## Verification boundary

This checkpoint records the observed public status as of 2026-10-19. A community issue remaining unanswered is not proof that no private/internal record exists; it means no public official answer was available in the checked evidence. No claim of complete internet-wide discovery is made.


## Addendum: related public gap reports found during the bounded follow-up

A targeted follow-up surfaced two additional open community reports in the official `binance/binance-public-data` issue tracker:

- [Issue #365: Missing Klines for BTC USDT between 2017-2024 (1 sec interval)](https://github.com/binance/binance-public-data/issues/365), opened 2024-11-01, label `reviewing`, still open with zero comments as checked on 2026-10-19. Its author lists a gap beginning at **2017-09-06 16:00 UTC** in monthly Spot 1-second kline data, alongside other gaps. This timestamp overlaps the project's disputed key, but the reported interval is 1-second data, not a direct finding about the project's 4h candle.
- [Issue #374: Incomplete historic data for BTCUSDT spot klines 1m interval](https://github.com/binance/binance-public-data/issues/374), opened 2024-11-16, label `reviewing`, still open as checked on 2026-10-19. It reports missing 1-minute data on 2017-09-06. Its one comment is a community suggestion to sort rows, not an official maintainer response.

**Interpretation:** These are independent community reports that corroborate a public-data coverage concern around the same historical date. They are not official Binance confirmations, do not establish the disputed 4h row's correctness, and do not provide old archive versions, point-in-time publication metadata, or a correction for the exact key. They are therefore context evidence only; they do not change the gate.

No comments were posted and no external issue was modified. No old scans were repeated. G0 remains `BLOCKED_GLOBAL`; no source case is closed and no candidate/backtest is authorized.
