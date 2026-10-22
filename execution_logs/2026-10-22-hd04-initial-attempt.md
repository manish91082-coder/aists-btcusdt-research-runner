# HD-04 initial implementation attempt — 2026-10-22

## Goal alignment
Primary target remains 1,000 USDT → 1,061,120.54 USDT (approx. ₹10 crore at the recorded dated FX snapshot). This run advances the single planned HD-04 gate, market-universe/coverage mapping; it does not start strategy research.

## Implementation
- Added `scripts/build_hd04_universe_snapshot.py`: public endpoint snapshot of Spot eligible USDT pairs and USDⓈ-M USDT perpetuals, separate 24-hour quote-volume rankings, exchange metadata/filters, canonical-JSON hashes, top-10 funding-history endpoint checks, and explicit account-specific fee uncertainty.
- Added `.github/workflows/hd04-universe-snapshot.yml` to run the capture and preserve its JSON artifact.
- Added `tests_crypto_target/test_hd04_universe.py` for Spot/Futures eligibility filtering and stable digest.
- Added the new files to the repository keep-list and smoke-test compilation/test coverage.

## Evidence and blocker
- First attempt failed at the public Spot `/api/v3/exchangeInfo` endpoint with HTTP 451 in the GitHub-hosted runner; no valid universe snapshot was produced. Run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39824506960
- A subsequent attempt got through source capture but the final completeness gate still failed; the log indicates the same endpoint access issue. Run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39824521991
- This is a real environment/source-access blocker, not evidence that the market universe is empty. HD-04 remains BLOCKED until a reproducible source snapshot is successfully captured.
- A transient smoke-test failure occurred on a commit before the latest keep-list update; subsequent smoke runs must be checked on their actual tested commits before claiming current CI green.

## Next action
Fix source access with an official alternate Binance API edge or an independently verifiable official public data source, while preserving the original error in the log. Rerun HD-04 and only mark it PASS when the report contains eligible listings, separate Top-10 rankings, source hashes, timestamped retrieval, and funding endpoint coverage status. Do not start strategy/backtest work until the required coverage evidence is present.
