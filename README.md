# AISTS BTCUSDT Research Runner

Standalone GitHub Actions execution environment for evidence-first BTCUSDT historical research.

- Public repository; standard GitHub-hosted runners.
- Allowlists: `smoke`, `historical_reference_replay`.
- Historical replay pulls only official Binance Spot monthly kline ZIPs and sibling `.CHECKSUM` objects; redirect targets are restricted to allowlisted distribution hosts and exact object paths.
- No Binance market-data REST API, exchange secrets, live orders, signing, raw repair, source selection, or strategy promotion.
- Only `contents: read` workflow permission; arbitrary inline Python and recurring live-price workflows removed.
- Results separate infrastructure success from data/research status; each artifact includes request ID, commit/run identity, input hashes, archive manifest, content issues, gap events and reference metrics.
- Reference strategies: EMA 12/26, RSI14 (30 entry/55 exit), Donchian 20/10; 4h, 1d, 1mo from 2017-08 through 2026-09; fees 10/15/20 bps and slippage 5/10/20 bps per side.
- This is an independent baseline, not a bit-identical replay of old CP-0027, and cannot promote candidates.

A change to `requests/current.json` on `main` runs the declared task. Manual runs are in Actions. Artifacts retain 7 days; verified monthly ZIPs are cached on the runner and are rechecked against freshly fetched official checksums before reuse.

Standard GitHub-hosted runner usage is free/unlimited for public repositories under GitHub's published terms; do not assume all artifact/cache services have unlimited retention/storage.

MIT License.


## CP-0026-aligned monthly derivation
The `monthly_derived_replay` task builds monthly bars from the hash/CRC/content-validated 1d archive series and compares them field-by-field to available official 1mo archives. It does not overwrite the direct archive or declare it canonical.
