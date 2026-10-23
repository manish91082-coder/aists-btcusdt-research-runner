# BTCUSDT Multi-Month History Integrity Checkpoint

Date: 2026-10-23
Branch: research/hd04-alternate-source-probe
Run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39904158657
Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39904158657/artifacts/12479684213
Commit under test: 131123adb55e5b9100e663d1686baff27d9cba5b

## Verified result

- Requested months: 2026-07, 2026-08, 2026-09 (UTC).
- Expected archive files: 9.
- Passed archive files: 9.
- Failed archive files: 0.
- Overall validator result: PASS.
- GitHub Actions job and artifact upload both succeeded.
- Official Binance archive .CHECKSUM sidecars matched for every passing archive, and CSV schema/time-grid/data checks passed as implemented in scripts/acquire_validate_btcusdt_history.py.

The archives cover monthly BTCUSDT Spot 5m candles, USDⓈ-M Futures 5m candles, and USDⓈ-M funding records for each requested month.

## Important scope limits

- This validates these nine archive files and the validator's defined checks. It is not full-universe exchange metadata verification.
- Three months is a useful pipeline checkpoint, not sufficient evidence of robust strategy performance across regimes.
- No strategy profitability, future returns, or target timeline has been established.
- No live trading, credentials, or funds movement is authorized.

## Next gate: canonical research dataset

1. Build a deterministic preparation step that reads the downloaded ZIP archives and creates normalized Spot candles, Futures candles, and funding CSV outputs without silently dropping rows.
2. Normalize all timestamps to UTC milliseconds, preserve original source timestamps and archive SHA-256 provenance, and verify exact month row counts / expected 5-minute grids for both candle venues.
3. Validate funding timestamps, rates and interval fields against the actual archive schema; do not assume a fixed funding cadence or fill missing funding values silently.
4. Add an explicit alignment report for Spot vs Futures timestamps and document how funding is applied in a backtest without look-ahead bias.
5. Add synthetic tests for timestamp units, both known funding schemas, duplicate/gap detection, and funding alignment.
6. Only after this gate passes, run a baseline backtest with fee, spread, slippage, funding, precision and partial-fill assumptions; separate development and out-of-sample periods.

Do not mark the strategy gate PASS based on data integrity alone.
