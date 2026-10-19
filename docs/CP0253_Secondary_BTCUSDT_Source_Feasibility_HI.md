# CP-0253 — Secondary BTCUSDT Data Source Feasibility Review (2026-10-19)

## Purpose
Find a second downloadable source for BTCUSDT Spot historical data to cross-check Binance Vision archives without weakening frozen CP-0040 G0 rules.

## Sources checked

### A. CryptoDataDownload — Binance Spot OHLCV
- Source page: https://www.cryptodatadownload.com/data/binance/
- General catalogue: https://www.cryptodatadownload.com/data/
- The provider documents Binance Spot historical OHLCV at daily, hourly and minute granularity, with UTC timestamps, OHLC, base volume, quote/base-converted volume and trade count. It says records are updated daily from the respective exchange.
- Its public page says hourly and spot-minute downloads require a free account; the page's visible catalogue did not expose a direct BTCUSDT download URL in this review.
- Suitability: potentially useful as a second maintained copy for exact-key/value comparison. 1-minute bars can be aggregated to UTC 4-hour bars without synthetic candles only if the raw minute series is complete.
- Limitation: it is still Binance-market data and the documentation reviewed does not establish independent tick capture, immutable historical versions, or point-in-time provenance. A match is corroboration, not automatic canonical-source authority.
- No CryptoDataDownload archive was downloaded or compared in this review.

### B. Tardis.dev — independently captured Binance Spot WebSocket trades
- Binance Spot coverage: https://docs.tardis.dev/historical-data-details/binance
- Downloadable datasets: https://docs.tardis.dev/downloadable-csv-files
- Tardis documents raw exchange-native data collected from Binance real-time WebSocket feeds. Its documented high-cap pair history begins 2019-03-30; all currency pairs begin 2021-03-05. Public downloadable CSV samples without an API key are available for the first day of each month; broader historical access is subscription/API controlled.
- Suitability: a different capture path for Binance trade-tape reconstruction during available coverage, subject to actual symbol/date availability and incident checks.
- Limitation: known unresolved aggregation/gap cases include 2017 and 2018 keys, before documented Tardis BTCUSDT coverage. Tardis cannot independently resolve those early cases; it can only provide a bounded later-period cross-check.
- No Tardis dataset was downloaded or compared in this review.

## Decision
SECOND_SOURCE_IDENTIFIED_NOT_YET_CROSSCHECKED_G0_UNCHANGED

1. CryptoDataDownload is the quickest candidate for same-symbol broad historical comparison, but files must actually be obtained, hashed, and compared; its source lineage does not by itself prove point-in-time authority.
2. Tardis is the stronger independent-capture corroborator for its documented coverage, but does not cover known 2017/2018 blockers.
3. No cross-source equality or mismatch is claimed because neither dataset was downloaded in this review.
4. Do not close any source case or set canonical source based on source discovery alone. Cross-check exact UTC open keys and OHLCV/trade-count fields; rebuild 4h only from complete, grid-valid 1m/trade data; preserve raw sources and hashes; mark unavailable evidence MISSING_EVIDENCE; never shift, fill, or fabricate candles.
5. G0 remains BLOCKED_GLOBAL; canonical historical source remains NONE; all 11 non-row aggregation blockers remain open; 17 missing 4h slots retain existing dispositions; 23 current candidates remain G2 FAIL. No candidate build/backtest, strategy promotion, or live action is authorized.

## GitHub validation boundary
The existing exact-head static audit run for prior branch HEAD aa988a1d9b949176de02d5f0db4b353be9b881bb, run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39244387970, completed successfully. It validates configured code/tests only, not external-data acquisition, cross-source comparison, historical provenance, G0 clearance, or profitability. This report and the subsequent roadmap update each require their own exact-head CI verification.