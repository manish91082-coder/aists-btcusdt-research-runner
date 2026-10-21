# Historical Binance Data Ingestion: Subtask Plan
Date: 2026-10-21
Status: HD-03 September 2026 pilot ACCEPTED; HD-04 older-month validation NEXT
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
- HD-00 [POLICY FROZEN]: Build a dynamic, point-in-time Top-10 by volume separately for Spot USDT pairs and USDⓈ-M USDT perpetuals. See [TOP10_VOLUME_UNIVERSE_SPEC.md](TOP10_VOLUME_UNIVERSE_SPEC.md). BTCUSDT is a pipeline test fixture, not the final universe.
- HD-01 [IMPLEMENTED; validated on HD-03 sample]: Single-month validator for official archive download, publisher checksum, local SHA-256, ZIP integrity, 12-column schema, timestamps, month membership, interval alignment, duplicates, ordering, gaps, close-time semantics, OHLC invariants and nonnegative volume/counts.
- HD-02 [IMPLEMENTED; run 39594637570 completed]: Manual GitHub Actions pilot for BTCUSDT Spot and USDⓈ-M Futures, one month and one interval, uploading JSON reports and source evidence as a 14-day artifact.
- HD-03 [ACCEPTED FOR BOUNDED PILOT]: September 2026 BTCUSDT 5m monthly run 39594637570 reviewed; both Spot and USDⓈ-M reports PASS at 8,640 candles each with matching official checksum/local SHA-256 and zero gaps, duplicates, malformed rows or missing expected candles. Artifact digest verified. Archive checks prove publisher byte integrity, not independent economic truth.
- HD-04 [NEXT/GATED]: Verify one older completed month in Spot + USDⓈ-M Futures to check archive path, schema and timestamp-unit conventions. Recommended 2024-01 BTCUSDT 5m, but official archive existence must be observed in the workflow reports, not assumed.
- HD-05 [GATED]: Build coverage manifest per symbol/product/interval/month: source URL, archive checksum, local hash, row count, first/last timestamps, gaps, listing start, and status.
- HD-05a [GATED]: Verify daily kline quote-volume semantics, build the eligible symbol/product inventory, then calculate point-in-time 30-day median daily USDT turnover ranks. Emit separate Spot and Futures Top-10 manifests with exclusions and overlap. No hardcoded coin list and no future-volume leakage.
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

## Capital and market-universe lock
- “Real capital market” means real official market data and realistic fees/liquidity/cost constraints; it does not authorize live-money execution.
- Research equity remains 10,000 USDT as a paper/research assumption only. Live orders, credentials and deployment remain explicitly locked.

## Pilot acceptance
Both Spot and USDⓈ-M Futures must have: successful archive download; matching official checksum; exactly one valid CSV in ZIP; valid schema; all timestamps inside requested month; correct interval alignment and close times; no duplicates, out-of-order rows or internal gaps; valid OHLC; nonnegative volumes/counts; and exact full-month row count for BTCUSDT. Two JSON reports and source evidence must be attached to the same workflow run. HD-03's artifact has now been reviewed and this bounded pilot is accepted. The wider Phase 2 coverage/cost gate remains open until HD-04 and subsequent required subtasks pass.
