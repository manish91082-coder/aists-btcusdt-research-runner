# HD-04 archive-first result — 2026-10-23

## Verified source and run
- Workflow: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39886385373
- Tested commit: `018a840f9e18ff6948e99f1cf2af98fd9abde266`
- Artifact (30-day retention): https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39886385373/artifacts/12473175759
- Official source documentation: https://github.com/binance/binance-public-data/blob/master/README.md

## Results
| Archive | CSV rows reported | Header interpretation | ZIP SHA-256 | Checksum |
|---|---:|---|---|---|
| Spot BTCUSDT 5m, 2026-09 | 8,640 | 8,640 data rows | `4106fc73698fd1851b1821cd0293adc6304f86f0c2e72244e15c41f63c2bde08` | MATCH |
| USD-M Futures BTCUSDT 5m, 2026-09 | 8,641 | First row is header; 8,640 data rows | `3a2d163a2bd28ca614fa0840a92ecbcde0d9c4962b278dd619d5bf81a9918e26` | MATCH |
| USD-M Futures BTCUSDT fundingRate, 2026-09 | 91 | First row is header; 90 data rows | `913cd31b8f924a06717a2fac17f3df6132c24ccded209eb3e4ae7d83e1b247f2` | MATCH |

All three ZIP downloads and their official SHA-256 sidecars were available and matched. The funding archive provides historical settlement rows for this month, so the pipeline need not rely solely on the REST endpoint for that historical data.

## Gate decision
- **Archive access substep: PASS for these three BTCUSDT September 2026 files.**
- **HD-04 universe gate: BLOCKED.** The same run failed at current USD-M Futures `/fapi/v1/exchangeInfo` because the response could not be parsed as JSON. No current listing universe or volume ranking was produced.
- This probe is one symbol, one interval, one month and one funding archive. It is not full-universe coverage, does not establish historical universe membership and does not prove strategy profitability.

## Next action
Use the archive path for historical candle/funding ingestion and separately resolve current product-list/volume snapshot through a verifiable source. Keep historical and current universes distinct; do not infer current listings from the existence of historical ZIP files.
