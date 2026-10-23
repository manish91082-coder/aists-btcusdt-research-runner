# HD-04 archive-first acquisition attempt — 2026-10-23

## Decision
Use Binance's official static monthly archives first for historical candles and historical funding-rate data, because public exchange-info REST calls have been unreliable from the GitHub-hosted runner. Keep current universe/listing/volume discovery as a separate evidence requirement.

## Changes
- Added `scripts/probe_hd04_archive_sources.py` to download and inspect:
  - Spot BTCUSDT 5m monthly klines, September 2026.
  - USD-M Futures BTCUSDT 5m monthly klines, September 2026.
  - USD-M Futures BTCUSDT monthly funding-rate archive, September 2026.
- Each archive requires a successful download, corresponding `.CHECKSUM` SHA-256 match, one CSV payload inside the ZIP, and non-empty CSV rows.
- Added the archive probe before API universe capture in `.github/workflows/hd04-universe-snapshot.yml`.
- Added the script to the keep-list and smoke compilation; updated roadmap, status, README and Hindi master log.
- Official source reference: https://github.com/binance/binance-public-data/blob/master/README.md

## Status
Implementation committed, runtime result pending verification in the corresponding GitHub Actions run. Even if the three archives pass, HD-04 is not complete: current Spot/Futures listing eligibility and separate 24h quote-volume rankings still require a successful timestamped universe snapshot. No strategy research starts until the required data gates pass.
