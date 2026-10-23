# Crypto Target Research — Current Project Status

**Last updated:** 22 October 2026  
**Repository:** [aists-btcusdt-research-runner](https://github.com/manish91082-coder/aists-btcusdt-research-runner)  
**Branch:** `main`  
**Current phase:** HD-03 passed for the initial BTCUSDT slice; HD-04 universe snapshot remains blocked by current Futures API response issues. The official archive probe verified three historical files; its validation now explicitly checks expected CSV header shape and data-row counts. Smoke CI passed on commit `1197e7592c79b0f4cf8440af5bf8f59a74690bdc`.

## Executive status

| Workstream | Status | Verified meaning |
|---|---|---|
| Current-thread repository cleanup | **Complete** | Old tracked project files removed from current `main`; the intended current research files remain. Git history and other branches were not erased. |
| README, project details and status | **Updated** | Core project documents have a common scope and research status. |
| Compounding/target math helpers | **Implemented** | Deterministic arithmetic helpers exist; they are not a trade signal or strategy. |
| Helpers, docs and allowlist checks | **Passed** | [Latest GitHub Actions run](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817387843): Python compile passed, required-doc checks passed, 21/21 tracked paths protected, 0 deletion candidates, and 5 unit tests passed. |
| HD-03 September 2026 BTCUSDT 5m Spot/Futures slice | **PASS, scope-limited** | 8,640 candles each, zero reported integrity anomalies, Binance sidecar checksums match; see execution log and run artifact. |
| Cost-aware strategy backtest | **Not run** | No market-data performance result exists for this workstream. |
| Profitable strategy / time to target | **Not established / unknown** | No forecast or profit guarantee is justified. |
| Live exchange access, orders, funds movement | **Not authorized** | Research only. |
| Tax/TDS analysis | **Deferred** | Outside current scope until explicitly reopened. |

## Primary goal

Build a fully AI-driven autonomous trading ecosystem to research whether initial equity of **1,000 USDT** can grow toward **1,061,120.54 USDT**, the approximate USDT equivalent of **₹10 crore** at the 22 October 2026 ₹94.24/USDT snapshot. This is a dated conversion reference, not a guaranteed outcome or timeline. The 10,000,000 USDT target was entered by mistake and is not the project goal.

“Compounding” means reinvesting **realized net profit** into equity for later position sizing. It does not require a one-hour chart or one trade every hour. The allowed strategy timeframe is open, subject to valid testing.

## AI ecosystem requirement

The intended system must dynamically decide trade/no-trade, market/direction, strategy/timeframe, entry/exit, initial and trailing stop-loss, take-profit/trailing-profit, sizing, portfolio risk and regime adaptation, using current validated market conditions and net-of-cost evaluation. AI decisions must stay inside deterministic risk limits, data-quality gates, execution constraints and kill switches. The design is documented in [AI_AUTONOMOUS_TRADING_ARCHITECTURE.md](AI_AUTONOMOUS_TRADING_ARCHITECTURE.md). This architecture is documented but not yet implemented end-to-end; live trading remains unauthorized.

## Work completed in this thread

- Created the crypto-target math helper package and deterministic unit tests.
- Added a GitHub Actions smoke-test workflow.
- Added guarded repository-cleanup tooling, then completed and verified the current-thread-only cleanup.
- Recreated a current README, added the detailed project charter, and aligned the master research log, status, keep-list and cleanup utility.
- Preserved the current research source, tests, workflow and execution records. The cleanup did not erase Git history or other branches.

Execution records:
- [Cleanup outcome and verification](execution_logs/2026-10-22-cleanup-final-verification.md)
- [Current-thread-only cleanup](execution_logs/2026-10-22-current-thread-only-cleanup.md)
- [Research harness bootstrap](execution_logs/2026-10-22-research-harness-bootstrap.md)

## Evidence gates

1. **Data integrity:** source, product type, symbol, interval, timestamps, checksum, schema, duplicates, OHLCV validity and missing intervals are audited.
2. **Baseline correctness:** explicit signal time, executable fill assumption, no look-ahead, and realistic costs.
3. **Out-of-sample edge:** chronological validation/walk-forward tests versus simple baselines after costs.
4. **Risk robustness:** drawdown, tail losses, leverage/liquidation where relevant, sensitivity and ruin-risk analysis.
5. **Forward validation:** paper/forward observations before any discussion of a live stage.
6. **Explicit authorization:** live actions remain disabled unless separately requested and reviewed.

## Latest plan/CI verification
- End-to-end plan: `END_TO_END_EXECUTION_PLAN_HI.md`.
- CI: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39822482423 — `success`, tested commit `a2450df4c76fb2e88b92a14432f50d81c7bb24a1`.
- Python compilation, required plan/target checks, keep-list dry-run and 5/5 unit tests passed. This verifies repository checks only, not market data or trading edge.
- Detailed record: `execution_logs/2026-10-22-end-to-end-plan-baseline.md`.

## Next step

**HD-03: PASS (scope-limited).** Both September 2026 BTCUSDT Spot and USDⓈ-M Futures 5-minute archives passed the current validator: 8,640 rows each; no missing/duplicate/off-grid/out-of-month timestamps or numeric/OHLC/close-time issues; Binance checksum sidecars matched. Evidence: [Actions run/artifact](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39823937420), `execution_logs/2026-10-22-hd03-data-integrity-pass.md`. **HD-04 remains BLOCKED.** The first real snapshot attempt hit HTTP 451 on `https://api.binance.com/api/v3/exchangeInfo`; a later attempt did not pass completeness. This is source-access failure, not evidence about listings. See `execution_logs/2026-10-22-hd04-initial-attempt.md`. No strategy edge is established.

**Decision today:** Strategy edge is **NOT ESTABLISHED**. Time to target is **UNKNOWN**. No market-data backtest is claimed.


## Latest continuity checkpoint — 22 October 2026
- Current core documents, AI architecture, keep-list, cleanup script, workflows and research helpers are linked from `README.md`.
- End-to-end evidence-gated roadmap: `END_TO_END_EXECUTION_PLAN_HI.md`; its current single next gate is HD-03.
- Final tree audit: `execution_logs/2026-10-22-docs-final-verification.md`. The latest post-refresh `main` inventory now contains 22 tracked files; all 22 are covered by the current committed keep-list and unexpected paths are 0. The latest CI run tested its pinned commit (`67c08f8d9c370e8d1f3171f5f7175ce6db41c016`), where 21 tracked files were all protected and there were 0 deletion candidates. The newest current-tree check log is `execution_logs/2026-10-22-final-current-thread-ci-success.md`.
- Expanded documentation/allowlist smoke run passed in GitHub Actions: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873. Detailed step results: `execution_logs/2026-10-22-expanded-smoke-ci-success.md`.
- Follow-up final-document validation passed: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817044689 (20 protected files, zero deletion candidates, 5/5 unit tests); details: `execution_logs/2026-10-22-final-docs-ci-success.md`.
- Latest smoke run passed: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817387843 (21 protected files, zero deletion candidates, 5/5 unit tests); details: `execution_logs/2026-10-22-final-current-thread-ci-success.md`.
- AI architecture and corrected ₹10 crore target consistency checks passed in [GitHub Actions run 39819921442](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39819921442); details: `execution_logs/2026-10-22-ai-architecture-ci-success.md`.
- Research gate remains unchanged: market data not yet verified, no cost-aware backtest, AI trading loop not yet implemented end-to-end, edge NOT ESTABLISHED, target time UNKNOWN, live trading NOT AUTHORIZED, tax/TDS deferred.

## Latest next action (23 October 2026)

- Hardened `scripts/probe_hd04_archive_sources.py` to distinguish header rows from data rows and require exactly 8,640 Spot candles, 8,640 USD-M Futures candles, and 90 funding rows for the September 2026 probe, in addition to official ZIP checksum matches.
- Smoke CI passed on the exact commit: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39887371687.
- This change has not yet been rerun through the HD-04 workflow. Next: run the updated archive probe through HD-04 and confirm row-count assertions, then focus solely on a verifiable source for current product listings and separate Spot/Futures volume rankings. HD-04 remains BLOCKED until those are evidenced.


## HD-04 rerun after archive-row validation hardening (23 October 2026)

- Run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39887437784
- Exact tested commit: `986479a2bea5f5ae645b17cfb5feda3ceebcec07`.
- Archive probe: PASS; all 3 expected checksum, header-shape and data-row-count assertions passed (Spot 8,640; USD-M Futures 8,640; funding 90).
- Compile and deterministic eligibility tests: PASS.
- Current universe snapshot: FAIL at official USD-M Futures `/fapi/v1/exchangeInfo`; response was not parseable JSON across the configured official hosts. Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39887437784/artifacts/12473615465.
- HD-04 remains BLOCKED. Next research task: test an independent venue-pair discovery source (e.g. CoinGecko exchange/derivatives listings) as a corroborating cross-check, while preserving Binance's own listing/status metadata as the required exchange-specific authority. Do not treat an aggregated source as a replacement for exact Binance tradability or Futures contract metadata.


## Independent exchange-source probe added (23 October 2026)

- Added `scripts/probe_hd04_coingecko_source.py` to test CoinGecko's Binance Spot and Binance Futures exchange endpoints independently, preserving endpoint-level errors, response hashes, returned ticker count, and a bounded ticker summary.
- The probe explicitly labels CoinGecko as corroboration only. It does not replace Binance's official symbol status, complete exchangeInfo universe, contract metadata, or per-symbol USDT quote-volume ranking.
- The HD-04 workflow now compiles and runs this probe and preserves its JSON report in the workflow artifact. An optional `COINGECKO_DEMO_API_KEY` environment variable may be configured as a GitHub Actions secret; no key is committed or required in source code.
- Current verification status: code has been committed, but the workflow result is pending. HD-04 remains BLOCKED until evidence confirms current listing/volume coverage and the primary snapshot gate passes.


## CoinGecko corroboration probe result and refinement (23 October 2026)

- Workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39888051398. Tested workflow commit: `2665814b9eb56fc0ffe1462f3e5def377922997f`.
- The public API probe succeeded without a configured key for both `/exchanges/binance` and `/derivatives/exchanges/binance_futures`. Spot endpoint returned 100 tickers; the derivatives exchange detail endpoint returned zero pair tickers while reporting exchange-level volume. This confirms API reachability, not complete universe coverage.
- The Spot endpoint's reported exchange volume is denominated in BTC and its ticker sample includes non-USDT pairs. Do not use it as Binance per-symbol USDT quoteVolume ranking.
- Probe refined in commit `385d3dd7437ce9516f9e1a2168bac9e20db8a117` to also query the global `/derivatives` ticker endpoint and filter records whose market label identifies Binance Futures. This result is pending a new workflow run.
- Primary Binance universe snapshot still fails on non-JSON response from official USD-M Futures `exchangeInfo`. HD-04 remains BLOCKED.


## CoinGecko expanded derivatives probe result (23 October 2026)

- Run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39888143324; tested commit `385d3dd7437ce9516f9e1a2168bac9e20db8a117`.
- Independent-source probe: 3/3 endpoints succeeded. Spot exchange endpoint returned 100 tickers; exchange-detail endpoint for Binance Futures returned 0 pair tickers; global `/derivatives` endpoint returned 27,951 records, of which 823 had a market label containing Binance and Futures.
- This is useful independent corroboration for a separate derivatives data slice, but does not prove all Binance contracts are represented, does not establish official Binance contract status, and does not replace exchangeInfo. The spot endpoint is also limited to 100 tickers and is not a complete universe.
- The same run's primary snapshot still failed at official Binance USD-M Futures `exchangeInfo`. Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39888143324/artifacts (use the run's artifact section; artifact is named `hd04-market-universe-39888143324`).
- HD-04 remains BLOCKED. Next: make the CoinGecko-derived candidate list explicit, normalize pair symbols without assuming equivalence, retain raw records and timestamp/hash, and compare any overlap against the verified historical archive set; continue investigating a primary-source path for Binance current status.


## Candidate symbol reconciliation added (23 October 2026)

- Updated `scripts/probe_hd04_coingecko_source.py` (commit `fd0e1e75d2d33269eeac4e85796a59ffd1b1ed5f`) to preserve each external raw symbol and add a conservative candidate only for alphanumeric symbols ending in recognized quote suffixes (USDT, USDC, BUSD, USD). Nonmatching symbols remain unmapped rather than guessed.
- Report now includes unique candidate count, duplicate candidate symbols, unmapped count and an explicit overlap check against BTCUSDT, the only symbol in the current verified archive probe.
- Added deterministic unit tests in commit `bae405f87b0148bf5e7bbdf658d6f1d3558dd4ed`. HD-04 workflow is triggered by the script and test paths; verification pending.
- This is a candidate-reconciliation layer, not Binance listing verification. HD-04 remains BLOCKED pending workflow evidence and a primary current-contract source.


## Candidate-symbol reconciliation verification (23 October 2026)

- Workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39889218198; tested commit `bae405f87b0148bf5e7bbdf658d6f1d3558dd4ed`.
- Smoke workflow: PASS at the same commit: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39889218167.
- CoinGecko probe results in the workflow log: 27,978 global derivatives ticker records; 824 Binance (Futures) labeled records; 779 unique conservative symbol candidates; 45 unmapped records; no duplicate normalized candidates; overlap with the only verified historical archive symbol BTCUSDT = BTCUSDT.
- The HD-04 job still concludes FAILURE because the primary Binance Futures `exchangeInfo` request returns non-JSON. The candidate layer is evidence and a reconciliation aid only. HD-04 remains BLOCKED.
- Next bounded step: create a historical archive availability matrix for a small, explicitly selected sample of CoinGecko USDT-quoted candidates, checking official archive existence/checksum and keeping missing archives as coverage debt. Do not probe all 779 symbols blindly or assume candidates are listed/active at Binance.


## Continuity update — 23 October 2026: bounded HD-04 candidate archive probe
- Added `scripts/probe_hd04_candidate_archive_coverage.py` to choose at most 10 unique, conservatively mapped USDT candidates from the CoinGecko Binance-Futures-labeled aggregator records, ranked by source-reported `volume_24h` with deterministic tie-breaking.
- The probe checks September 2026 5-minute Spot and USDⓈ-M Futures archive URLs separately and compares each available ZIP SHA-256 against the official `.CHECKSUM` sidecar. It writes `artifacts/hd04/hd04-candidate-archive-coverage.json`, which the HD-04 workflow artifact retains.
- Missing archive URL (HTTP 404) is classified as `NOT_AVAILABLE_OR_NOT_LISTED`; it is not treated as proof that a symbol was never listed or is inactive. Checksum match proves object integrity only, not schema/continuity or current listing status.
- Added deterministic unit tests for unique USDT filtering, volume ranking, and tie-breaking; added the script to `CURRENT_PROJECT_KEEP_PATHS.txt` and the HD-04 workflow.
- **Gate state remains BLOCKED until the workflow evidence is inspected and the official Binance Futures `exchangeInfo` snapshot succeeds.** CoinGecko candidate records are not authoritative Binance listing metadata. Strategy/backtest remains prohibited before data gates pass; no trading edge or timeline is established.


## HD-04 candidate archive probe execution verified; primary snapshot still blocked (23 October 2026)

- Latest HD-04 workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39890523651 (commit `c14041b7398b40e9406c8857493d1c3e59067c69`).
- Compile and deterministic eligibility tests passed. Official monthly archive probe passed; CoinGecko corroboration passed; bounded candidate archive coverage probe passed; its report was preserved in artifact `hd04-market-universe-39890523651` (artifact ID `12474726467`, SHA-256 `d1898d7fe5530346380dff22497118fc0623a7339a520f0c36b1c131efb00f28`).
- Bounded archive result: 20 Spot/Futures archive checks across 10 candidates; 14 ZIP/checksum matches; 6 HTTP 404s recorded as `NOT_AVAILABLE_OR_NOT_LISTED`; zero network/other errors. Candidate symbols: BTCUSDT, ETHUSDT, SOXLUSDT, XAUUSDT, SNDKUSDT, ZECUSDT, SKHYNIXUSDT, KORUUSDT, SPCXUSDT, SOLUSDT. These are aggregator-derived candidates, not proof of official active Binance listings.
- Overall workflow correctly remains FAILURE/BLOCKED because `https://fapi.binance.com/fapi/v1/exchangeInfo` returned a non-JSON/empty response. Failure occurred in `scripts/build_hd04_universe_snapshot.py`; this is an unresolved primary-source access/response issue, not evidence that candidate archive checks failed.
- Next action: diagnose the official current-contract metadata access separately and preserve source provenance. Do not weaken the completeness gate or promote CoinGecko candidates into official listings. No strategy/backtest, profitability, or live trading is authorized.


## Independent historical data provider selected for bounded evaluation (23 October 2026)

- Selected Tardis.dev as the next independent-provider candidate to evaluate for historical Spot and derivatives data. Official docs describe multi-exchange historical feeds and downloadable daily CSV datasets for trades, order books, quotes and derivatives data including funding, mark/index price and liquidations. OHLCV can be derived client-side from trades; do not assume Tardis daily tick files are ready-made monthly 5-minute candles.
- Docs: https://docs.tardis.dev/downloadable-csv-files ; https://docs.tardis.dev/faq/data ; https://docs.tardis.dev/downloadable-csv-files/api
- Some first-day-of-month historical datasets are accessible without an API key, but this is not evidence of full free historical coverage. Paid plans and historical retention/coverage must be checked before selecting it as a durable dependency.
- Next bounded test: inspect documented exchange/data-type coverage for an alternate exchange's Spot and perpetual Futures, then validate one small identical time window against a trusted candle source: timestamps, OHLCV aggregation, gaps, symbol/contract mapping and funding fields. Treat Tardis as an independent provider, not as proof of official Binance contract status. HD-04 remains BLOCKED until primary universe metadata and coverage criteria are satisfied.
