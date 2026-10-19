# CP-0271: Alternate-Source Exact-Key Corroboration Report (Hindi)

**तारीख:** 2026-10-19  
**Repository branch:** `cp-0271-alternate-source-crosscheck`  
**Probe commit tested:** `ec28036ca35347256e8cd769c36eef71299020a7`  
**GitHub Actions run:** [39292714869](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39292714869)  
**Run result:** `completed / success`  
**Artifact:** `cp0271-alternate-source-39292714869-attempt-1`  
**Artifact ID:** `12206106753`  
**Artifact SHA-256:** `0a8db13ebb87a4243011b4e9feea18c860f176cfcb1096ec0c2bd6f5fb73f477`

## उद्देश्य और सीमा

CryptoDataDownload की Binance BTCUSDT 1h CSV को transiently डाउनलोड करके, complete 1h bars से UTC-aligned 4h aggregates बनाकर, frozen CP-0040 manifest के 4h unresolved exact keys पर मौजूदा Binance monthly 4h rows से corroboration करना। यह **source-authority adjudication नहीं है और G0 closure नहीं है**। Frozen CP-0040 acceptance rulebook अपरिवर्तित है।

## Source identity

- URL: https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_1h.csv
- HTTP status: `200`
- Content type: `text/csv`
- Downloaded bytes: `8,753,754`
- SHA-256: `072ae35fcd953e11df176aed8a73a06d0698e95ef3db07d349015a5ac37174e4`
- Parsed hourly rows: `78,627`
- Parse/grid/OHLC rejects: `43`
- Observed first open: `2017-08-17T04:00:00Z`
- Observed last open: `2026-10-18T23:00:00Z`
- Complete 4h aggregates: `19,256`
- Incomplete 4h buckets excluded without filling: `543`
- Existing Binance monthly cache: `110` 4h ZIPs, `19,974` parsed rows; cache parser errors: `0`

The third-party CSV was not committed or republished. Only its URL, retrieval metadata, hash, and comparison summary are recorded.

## Frozen 4h exact-key comparison

The CP-0040 manifest contains 6 unresolved 4h exact keys. The probe compared the common keys using seven fields: OHLC, base volume, quote volume and trade count. It did **not** compare close time or taker-buy base/quote volumes.

| UTC open key | Monthly row | Third-party 4h aggregate | Probe result |
|---|---:|---:|---|
| 2017-09-06 12:00 UTC | Available | Available | All 7 compared fields match |
| 2017-09-06 16:00 UTC | Missing | Missing | No overlap; unresolved gap/placeholder case |
| 2018-02-08 00:00 UTC | Available | Unavailable | No overlap |
| 2019-11-25 00:00 UTC | Available | Unavailable | No overlap |
| 2021-01-21 08:00 UTC | Available | Available | OHLC match; base volume, quote volume and trade count differ |
| 2021-12-24 00:00 UTC | Available | Available | All 7 compared fields match |

Summary:
- Exact-key comparisons with both sources available: `3/6`
- All seven compared fields match: `2`
- At least one compared field differs: `1`
- No overlapping comparable aggregate: `3`

### Interpretation

- The 2017-09-06 12:00 UTC key is a frozen close-time-only conflict. Because close time was not compared, the matching seven fields do **not** resolve that case.
- The 2021-01-21 08:00 UTC key retains a material volume/trade-count discrepancy despite OHLC equality.
- The 2021-12-24 00:00 UTC key has seven-field corroboration, but third-party agreement alone does not establish historical publication/version authority or authorize closure under CP-0040.
- Three unresolved keys have no complete third-party 4h aggregate in this downloaded dataset. No interpolation, timestamp shifting, or synthetic bar was used.
- CryptoDataDownload is an alternative mirror/corroborator, not proven to be an immutable point-in-time source.

## Gate decision

- Global G0: `BLOCKED_GLOBAL`
- Canonical historical source: `NONE`
- Historical version provenance: `NOT_VERIFIED`
- Acceptance-grade: `false`
- Backtest approved: `false`
- Profitability established: `false`
- Live signing / public broadcast / orders: `BLOCKED`

This probe advances source comparison, but does not close any CP-0040 case. Next valid closure work remains clause-level adjudication of all frozen populations (969 exact-key rows and 27 non-row blockers), with evidence-backed dispositions, dependency/accounting reconciliation and exact-head all-scope verification. Do not claim global G0 closure from this scoped probe.
