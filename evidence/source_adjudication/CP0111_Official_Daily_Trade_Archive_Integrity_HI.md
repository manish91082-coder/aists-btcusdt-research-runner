# CP-0111: Official Spot daily-trades archive integrity audit
**Date:** 2026-10-16
**Status:** `PASS_7_ARCHIVES_INTEGRITY_AND_BASIC_COVERAGE`
**Scope:** seven fixed daily trade archives only, corresponding to the 11 unresolved aggregation buckets.

## Execution evidence
- Workflow run: [38937879841](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38937879841)
- Executed commit: `fe075f94beb551dcc382dca3b9fd681ae6181b7b`.
- Workflow conclusion: `success`.
- Runner status: `PASS`, 11/11 runner checks PASS.
- Child summary SHA-256 recorded by runner: `6a34e04f8207356020cf9fa09731c060d9e8f92e9ab4cf2ccc85a3bdc7373728`.
- GitHub Actions artifact: [12061158412](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38937879841/artifacts/12061158412); artifact ZIP SHA-256 from workflow log: `2240ec7ffb3dffdbf9b7c41f6210ab5abb11f64cf68e8e81b26ee7e469434ef2`. Retention is seven days.

## Result
- Target dates: 2017-12-04, 2018-02-05, 2018-02-07, 2018-03-04, 2018-03-20, 2018-06-20, 2018-09-05 UTC.
- Official checksum sidecars were fetched from the allowlisted HTTPS host; all seven daily-trades ZIP downloads passed SHA-256 comparison against their sidecar token.
- All seven ZIPs passed ZIP CRC, expected member-name and seven-column Spot-trades schema checks, and all parsed trade timestamps fell inside the target UTC date.
- The child task status `PASS_7_ARCHIVES_INTEGRITY_AND_BASIC_COVERAGE` means no review flag was raised by the configured first/last-time-edge, within-file trade-ID sequence, duplicate/decreasing-ID, and timestamp-order screens. Those are anomaly screens, not a formal guarantee of completeness.
- Exact per-archive SHA-256, byte count, row count, first/last trade ID and time, gap counters, response metadata, and per-target findings are preserved in the linked workflow artifact. The compact runner log exposes the child-summary hash and overall child status; it does not print the individual rows.

## Boundaries and limitations
- This checks file bytes against the official sidecar token and basic archive/CSV/time structure. It does not prove Binance's historical trade archive is a complete or canonical representation of any historical kline.
- The official repository README identifies the seven Spot-trades columns and describes `.CHECKSUM` as a file-integrity mechanism. Open issue #316 records incomplete BTCUSDT trades on 2018-02-08, a different date; it motivates explicit coverage checks but is not evidence of a gap on these seven dates.
- No trade-to-kline reconstruction was performed in this checkpoint.
- No raw kline archive was edited; no timestamp was shifted or rounded; no synthetic candle was written; no Binance market-data REST endpoint or credential was used.
- Canonical source remains NONE; source cases closed 0; all 11 aggregation blockers remain unresolved.
- Candidate build, backtest, strategy promotion, live signing, public broadcast and Binance orders were not performed.

## Next bounded step
Use the checksum-verified daily trades only as independent diagnostic evidence: reconstruct exact OHLCV/trade-count fields for the 11 bucket windows, compare them with the frozen monthly and daily kline rows, separately record zero-trade-candle conventions, and leave source authority and case closure unchanged unless the frozen CP-0040 rulebook's evidence standard is satisfied.
