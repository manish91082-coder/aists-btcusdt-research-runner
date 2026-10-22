# HD-03 data acquisition and integrity result — 2026-10-22

## Outcome
**HD-03 PASS** for September 2026 BTCUSDT 5-minute Binance Spot and USDⓈ-M Futures monthly archives.

- Workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39823937420
- Tested commit: `95bdf820f783e0423911243c2a466b71af410966`
- Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39823937420/artifacts/12445537564
- Artifact name: `hd03-btcusdt-september-2026-39823937420`
- Artifact contains both original ZIPs and `hd03-integrity-report.json`. The artifact is retained by GitHub Actions for 30 days; download and preserve externally if longer retention is required.
- Retrieval window: 2026-10-22T17:34:53Z to 2026-10-22T17:34:55Z.
- Expected candles per product: 8,640, covering 2026-09-01 00:00 UTC through 2026-09-30 23:55 UTC.

## Source and checksum evidence

| Product | Source | Bytes | SHA-256 | Binance sidecar |
|---|---|---:|---|---|
| Spot | https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2026-09.zip | 444,933 | `4106fc73698fd1851b1821cd0293adc6304f86f0c2e72244e15c41f63c2bde08` | Available; matched |
| USDⓈ-M Futures | https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2026-09.zip | 389,713 | `3a2d163a2bd28ca614fa0840a92ecbcde0d9c4962b278dd619d5bf81a9918e26` | Available; matched |

## Validation results

Both products passed all current checks:
- Actual/expected rows: 8,640 / 8,640.
- First and last open times: 2026-09-01 00:00 UTC and 2026-09-30 23:55 UTC.
- Missing intervals: 0.
- Duplicate open timestamps: 0.
- Off-grid timestamps: 0.
- Timestamps outside the requested month: 0.
- Numeric/trade-count issues: 0.
- OHLC consistency issues: 0.
- Close-time bound issues: 0.
- Errors: none.

Deterministic synthetic tests also passed: complete month accepted; injected duplicate/missing interval rejected.

## Scope limits
This validates only these two BTCUSDT monthly 5-minute archives and the checks implemented in this validator. It does **not** establish broader symbol/timeframe coverage, strategy performance, profitable edge, future live data quality, funding/fees, realistic fills or target timeline. Data archives and JSON report were preserved in the run artifact; they were not committed as large binary files to the repository.

## Decision and next gate
HD-03 is closed as PASS. Next gate is **HD-04**: build a source-verifiable market-universe snapshot and coverage plan, including Spot and USDⓈ-M eligibility/listings, separately ranked volume universes, product metadata, historical funding-rate availability and fee assumptions. Preserve historical membership where possible to reduce survivorship bias. No strategy ranking until the relevant input coverage passes.
