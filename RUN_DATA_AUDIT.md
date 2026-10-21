# Run the monthly Binance history chunk audit in GitHub Actions

Historical archive files are now the primary source for historical data verification. REST API access is not required to validate an official monthly archive. All project work stays on GitHub; do not use Colab or Google Drive.

## Pilot
1. Open [Monthly Binance history chunk audit](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/workflows/monthly-binance-history-chunk.yml).
2. Click **Run workflow**.
3. Select completed month `2026-09` and interval `5m`.
4. Inspect both Spot and USDⓈ-M Futures JSON reports and the artifact.
5. Accept only if both reports PASS and each contains 8,640 BTCUSDT candles for September 2026.

## Evidence rules
- Each market downloads its official monthly ZIP and adjacent .CHECKSUM file.
- Preserve source URL, publisher checksum, local SHA-256, row count, timestamps, quality checks, and run ID.
- Missing/unreachable archive is BLOCKED; checksum mismatch or proven data-quality defect is FAIL.
- The artifact is temporary evidence staging and expires after 14 days. Never commit raw ZIP/CSV data to Git.
- One run handles one symbol, interval, month and both markets. Scale only after the pilot passes, with resumable chunks and a coverage manifest.
- Binance began in 2017, so Binance-only history cannot span 10-15 years as of October 2026. Use longest verified history per product.
- The available GitHub connector cannot dispatch Actions from this chat, so no run is claimed.
