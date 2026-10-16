# CP-0110: Official Spot daily-trades checksum-sidecar preflight
**Date:** 2026-10-16
**Status:** `PASS_ALL_7_OFFICIAL_TRADE_SIDECARS_AVAILABLE`
**Scope:** seven fixed UTC dates from the 11 frozen aggregation buckets; metadata-only check.

## 1. Execution evidence
- Repository: `manish91082-coder/aists-btcusdt-research-runner`
- GitHub Actions run: [38922212821](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38922212821)
- Executed commit: `0bf724d4b8ee2274295c186a6cd94ce00bbfdc81`
- Workflow result: `success`
- Runner result: `PASS`, 11/11 runner checks PASS.
- Child task result printed by runner: `PASS_ALL_7_OFFICIAL_TRADE_SIDECARS_AVAILABLE`.
- Child summary SHA-256 recorded by the runner: `31f12fdea950949ab5ecb6645d018e3bd55d71ec14f006b50462cc592e387100`.
- GitHub Actions artifact: [download artifact 12054562639](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38922212821/artifacts/12054562639); artifact ZIP SHA-256 shown in Actions logs: `78c9323ca221e2956db6d7c6a6626fe31a828c90797a3e6d51ccaab87034ff59`. The artifact retention is seven days.

## 2. Target-by-target result

The successful run returned a valid, correctly named SHA-256 sidecar from the allowlisted HTTPS host for all seven target dates. That implies HTTP 200, a parseable single SHA-256 token, the matching archive filename in the body, and successful byte-preserving save/read-back for each sidecar.

| UTC date | Exact checksum sidecar filename | Official sidecar URL | Result |
|---|---|---|---|
| 2017-12-04 | `BTCUSDT-trades-2017-12-04.zip.CHECKSUM` | [Open sidecar](https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2017-12-04.zip.CHECKSUM) | AVAILABLE_VALID_CHECKSUM_SIDECAR |
| 2018-02-05 | `BTCUSDT-trades-2018-02-05.zip.CHECKSUM` | [Open sidecar](https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2018-02-05.zip.CHECKSUM) | AVAILABLE_VALID_CHECKSUM_SIDECAR |
| 2018-02-07 | `BTCUSDT-trades-2018-02-07.zip.CHECKSUM` | [Open sidecar](https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2018-02-07.zip.CHECKSUM) | AVAILABLE_VALID_CHECKSUM_SIDECAR |
| 2018-03-04 | `BTCUSDT-trades-2018-03-04.zip.CHECKSUM` | [Open sidecar](https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2018-03-04.zip.CHECKSUM) | AVAILABLE_VALID_CHECKSUM_SIDECAR |
| 2018-03-20 | `BTCUSDT-trades-2018-03-20.zip.CHECKSUM` | [Open sidecar](https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2018-03-20.zip.CHECKSUM) | AVAILABLE_VALID_CHECKSUM_SIDECAR |
| 2018-06-20 | `BTCUSDT-trades-2018-06-20.zip.CHECKSUM` | [Open sidecar](https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2018-06-20.zip.CHECKSUM) | AVAILABLE_VALID_CHECKSUM_SIDECAR |
| 2018-09-05 | `BTCUSDT-trades-2018-09-05.zip.CHECKSUM` | [Open sidecar](https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2018-09-05.zip.CHECKSUM) | AVAILABLE_VALID_CHECKSUM_SIDECAR |

The per-target checksum tokens, sidecar body hashes, response headers, and persisted sidecar bodies are carried in the linked Actions artifact. They are not duplicated into this compact checkpoint because they were not individually emitted in the runner log.

## 3. Interpretation

**Established:** all seven official sidecar endpoints are available and structurally valid for the fixed dates. This enables planning the next isolated archive-integrity step.

**Not established:** archive ZIP bytes have not been downloaded or independently hashed in this checkpoint. A checksum token is a reported expected hash, not proof that the ZIP is complete or that trades reconstruct any particular kline. Sidecar availability does not identify a canonical daily/monthly kline source, explain the residual cross-interval mismatches, or close any case.

The official data repository documents its data distribution as daily/monthly downloadable archives and `.CHECKSUM` files. Its open historical-provenance issue asks whether old versions and replacement timestamps are retained; no maintainer confirmation was captured in this checkpoint. The separate 2018-02-08 trade-archive missing-data report is a reason to explicitly validate whole-day coverage for any trade-derived reconstruction, not evidence that these seven target dates are incomplete.

## 4. Scope and safety facts
- Checksum-sidecar GET requests: 7, all against `https://data.binance.vision`.
- Daily trade ZIP downloads: 0.
- Binance market-data REST API calls: 0.
- Exchange credentials used: false.
- Raw kline archives modified: false.
- Timestamp shifting/rounding or synthetic candles: false.
- Canonical source selected: false.
- Source cases closed: 0.
- Candidate build, backtest, or strategy promotion: not performed.
- Live signing/public broadcast/Binance orders: remain blocked.

## 5. Next bounded step

Use the seven expected SHA-256 tokens from the CP-0110 artifact to drive a new, isolated download-and-integrity check of only these seven official Spot daily-trades ZIPs. Before treating trade rows as adjudication evidence, verify byte hashes against the sidecars, ZIP CRC/schema, timestamp coverage over each complete UTC day, first/last trade IDs and time bounds, and whether any incomplete-day/maintenance signature appears. If integrity or coverage is insufficient, do not reconstruct candles from that date and do not close its bucket.

Even if all trade archives verify, reconstructed OHLCV is independent diagnostic evidence only until the frozen CP-0040 authority and coverage requirements are satisfied. Keep G0 blocked, G2 failing for the current 23 candidates, G7 live blocked, and all 11 aggregation blockers unresolved.
