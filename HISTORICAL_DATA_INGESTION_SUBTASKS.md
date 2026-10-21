# Historical Binance Data Ingestion: Subtask Plan
Date: 2026-10-21
Status: pilot IMPLEMENTED; real data run NOT YET VERIFIED
Workspace: GitHub repository + GitHub Actions only

## Decision
Use Binance's official monthly Spot and USDⓈ-M Futures kline archives as the primary historical source. API access is not a prerequisite for validating archived historical candles. REST API checks remain optional diagnostics, clearly separated from archive acceptance.

Official primary source: https://github.com/binance/binance-public-data
Archive root: https://data.binance.vision/
Spot monthly klines: `https://data.binance.vision/data/spot/monthly/klines/<SYMBOL>/<INTERVAL>/<SYMBOL>-<INTERVAL>-YYYY-MM.zip`
USDⓈ-M Futures monthly klines: `https://data.binance.vision/data/futures/um/monthly/klines/<SYMBOL>/<INTERVAL>/<SYMBOL>-<INTERVAL>-YYYY-MM.zip`
Each ZIP is checked against its adjacent `.CHECKSUM` file and local SHA-256.

## History limit
Binance launched in 2017. As of October 2026, Binance-only data cannot provide 10-15 years of history. Use the longest verified history actually available for each symbol/product; never invent pre-listing candles or silently splice another venue. Spot and Futures listing dates may differ.

## Subtasks
- HD-01 [IMPLEMENTED, NOT RUN]: Single-month validator for official archive download, publisher checksum, local SHA-256, ZIP integrity, 12-column schema, timestamps, month membership, interval alignment, duplicates, ordering, gaps, close-time semantics, OHLC invariants and nonnegative volume/counts.
- HD-02 [IMPLEMENTED, NOT RUN]: Manual GitHub Actions pilot for BTCUSDT Spot and USDⓈ-M Futures, one month and one interval, uploading JSON reports and source evidence as a 14-day artifact.
- HD-03 [NEXT]: Run September 2026, 5m pilot. Both market reports must PASS and be inspected. Expected count is 8,640 candles per market for a complete month.
- HD-04 [GATED]: Verify one older completed month to check archive path and timestamp-unit conventions.
- HD-05 [GATED]: Build coverage manifest per symbol/product/interval/month: source URL, archive checksum, local hash, row count, first/last timestamps, gaps, listing start, and status.
- HD-06 [GATED]: Add bounded resumable multi-month chunks (initial maximum three months per job), idempotent chunk IDs and explicit transient retry policy.
- HD-07 [GATED]: Process chunks chronologically, verify boundaries between adjacent months, keep Spot/Futures separate, and persist derived outputs plus provenance.
- HD-08 [GATED]: Verify official Futures mark-price, index-price, premium-index and funding-history archives before modelling these costs. Contract klines alone do not establish funding.
- HD-09 [GATED]: Build point-in-time asset/product history coverage matrix before universe ranking.
- HD-10 [GATED]: Backtests remain locked until required history, data quality, cost inputs, and S-01 to S-04 dependencies pass.

## Chunk and storage rules
- Current pilot handles one symbol × market × interval × month. Keep chunks small and resumable; do not create one giant all-history job.
- GitHub Actions runner storage is ephemeral. Raw ZIP/CSV files are not committed to Git history.
- The Actions artifact is temporary staging and expires after 14 days. Durable GitHub records are code, manifests, hashes, reports, coverage summaries and decisions, not bulk raw archives.
- Later jobs may re-download official chunks as needed unless a separate durable storage design is justified and approved.
- Measure archive sizes, runtime, output size and runner limits before scaling. Zero-cost does not mean unlimited Actions capacity.
- No credentials, trading, paper run, training, live orders or deployment are part of this ingestion pilot.

## Pilot acceptance
Both Spot and USDⓈ-M Futures must have: successful archive download; matching official checksum; exactly one valid CSV in ZIP; valid schema; all timestamps inside requested month; correct interval alignment and close times; no duplicates, out-of-order rows or internal gaps; valid OHLC; nonnegative volumes/counts; and exact full-month row count for BTCUSDT. Two JSON reports and source evidence must be attached to the same workflow run. Until an actual artifact is reviewed, the pilot is NOT PASS and Phase 2 stays BLOCKED.
