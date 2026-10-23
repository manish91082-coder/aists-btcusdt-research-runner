# Crypto Target Research — Current Project Status

**Last updated:** 23 October 2026, evening update  
**Repository:** [aists-btcusdt-research-runner](https://github.com/manish91082-coder/aists-btcusdt-research-runner)  
**Working branch:** `research/full-history-validation` (PR #17 remains draft; not merged)  
**Latest implementation:** [PR #16 merged](https://github.com/manish91082-coder/aists-btcusdt-research-runner/pull/16) at merge commit `581c97978d0845036c9cff8f2be71d7018f84aa5`  
**Current phase:** HD-03 initial slice passed; HD-04 broad-universe snapshot remains blocked. Multi-month BTCUSDT history for July-September 2026 passed integrity/normalization. Initial cost-aware Spot candidate baselines have been run and both produced negative net returns under illustrative costs. A preregistered walk-forward protocol is now committed; the next gate is month-by-month validation of the longer 2020-2026 history. Smoke CI passed on [run 39947549808](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947549808); candidate run [39947542681](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947542681).

## Executive status

| Workstream | Status | Verified meaning |
|---|---|---|
| Current-thread repository cleanup | **Complete** | Old tracked project files removed from current `main`; the intended current research files remain. Git history and other branches were not erased. |
| README, project details and status | **Updated** | Core project documents have a common scope and research status. |
| Compounding/target math helpers | **Implemented** | Deterministic arithmetic helpers exist; they are not a trade signal or strategy. |
| Helpers, docs and allowlist checks | **Passed** | [Latest GitHub Actions run](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817387843): Python compile passed, required-doc checks passed, 21/21 tracked paths protected, 0 deletion candidates, and 5 unit tests passed. |
| HD-03 September 2026 BTCUSDT 5m Spot/Futures slice | **PASS, scope-limited** | 8,640 candles each, zero reported integrity anomalies, Binance sidecar checksums match; see execution log and run artifact. |
| Cost-aware baseline and initial candidates | **Run; no edge established** | Jul-Sep 2026, 26,496 aligned 5m rows. Buy-and-hold benchmark +42.19%; SMA 12/48 candidate -68.03%, mean-reversion z48 candidate -58.94% under illustrative costs. Same sample is not an untouched holdout. |
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
- Added deterministic long/flat Spot candidate baselines (SMA trend and trailing z-score mean reversion), explicit next-open fills/cost assumptions, output verification, and unit tests. The candidate-baseline implementation and its records are merged in PR #16.

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

## Latest candidate-baseline evidence (23 October 2026)
- Multi-month run [39947542681](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947542681) succeeded on 26,496 aligned BTCUSDT 5m rows (July-September 2026); 276 funding events were retained in the normalized dataset. Candidate output verifier passed and both equity curves contain 26,496 rows. [Artifact](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947542681/artifacts/12498179453).
- Under illustrative fee 10 bps/fill, full spread 2 bps, and slippage 5 bps/fill: SMA 12/48 net return -68.03%, max drawdown -68.52%, 742 fills; mean-reversion z48 net return -58.94%, max drawdown -59.48%, 652 fills. These are in-sample initial candidate results, not out-of-sample evidence or recommendations.
- Smoke CI [39947549808](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947549808) passed after fixing and testing final-equity curve consistency. Detailed log: [candidate-baseline execution record](execution_logs/2026-10-23-btcusdt-candidate-baselines-initial.md).

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


## Zero-cost independent source shortlist (23 October 2026)

Three candidates beyond Binance and Tardis have been reviewed for bounded evaluation:

1. **Bybit official public market API** — no account key needed for public market-data endpoints. Spot and linear/inverse contract klines share `/v5/market/kline`; response is paginated (up to 1,000 bars per request) and reverse chronological. Separate endpoints document instrument metadata and funding history. Sources: https://bybit-exchange.github.io/docs/v5/market/kline ; https://bybit-exchange.github.io/docs/v5/market/instruments-info ; https://bybit-exchange.github.io/docs/v5/market/funding/history . This is the first source to probe.
2. **OKX official public data/API** — historical-data page offers downloads for trade history (from Sep 2021), candles (from Jul 2023), funding history (from Mar 2022), and L2 order book (from Mar 2023). Public REST API separately exposes historical candles, instruments and funding. Sources: https://www.okx.com/historical-data ; https://app.okx.com/docs-v5/en/ . Check regional availability, instrument differences and download limits before relying on it.
3. **CryptoDataDownload free CSVs** — documented no-login free OHLCV downloads at daily/hourly/1-minute granularity across several Spot venues, useful as an independent Spot cross-check; not selected as a full Futures/funding source. Source: https://www.cryptodatadownload.com/ .

Zero-cost scope means public endpoints/downloads without a paid plan or key where supported; it does not mean unlimited requests, guaranteed historical depth, or all symbols/data types. The next step is a small read-only probe of Bybit and OKX for the same UTC window: BTCUSDT Spot and perpetual contract candles, instrument metadata, and funding history. Validate HTTP/JSON success, symbol/instrument mapping, timestamps, interval continuity, OHLCV numeric rules and funding schema. CryptoDataDownload will be considered only for Spot cross-check where an exact comparable file exists. No API keys, account actions or trading endpoints are required.


## Alternate zero-cost source probe implementation — 23 October 2026

- Branch: `research/hd04-alternate-source-probe`.
- Added `scripts/probe_hd04_alternate_sources.py` for bounded read-only public endpoint checks against Bybit V5 and OKX V5: BTCUSDT Spot and linear perpetual candles, instrument metadata and funding history; OKX BTC-USDT Spot and BTC-USDT-SWAP candles, instrument metadata and funding history.
- Fixed UTC probe window: 2026-09-01 00:00–01:00 UTC. Responses and errors are written to `artifacts/hd04/hd04-alternate-sources.json`; no API keys or trading endpoints are used.
- HD-04 workflow now compiles and runs the probe, and the script is protected in `CURRENT_PROJECT_KEEP_PATHS.txt`.
- This is an implementation change only. The probe has not yet been executed in GitHub Actions, so no provider reachability, schema, or candle-validation result is claimed. The Binance authoritative current-universe gate remains BLOCKED; strategy/backtest and live-trading authorization remain closed.


## Alternate-source probe: first live result and boundary fix (23 October 2026)

- Initial bounded run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39901520198 ; artifact id 12479136008. Bybit's five public endpoint checks returned HTTP 403 from this runner. This is an access/reachability failure, not proof that Bybit lacks the data.
- OKX Spot and Swap instrument metadata passed. Both candle endpoints returned 11 rows because the lower time boundary excluded the exact start candle; funding history also returned an empty list with the initial boundary.
- Corrected the OKX history query to use `before=START-1ms` on branch commit `e8998d20d761bf8fc6c4a1fbe088a9744afebdff`.
- Re-run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39902158479 ; artifact id 12479226388. Report summary: 5/10 checks passed. OKX Spot candles and Swap candles each returned exactly 12 unique, continuous 5-minute candles inside the fixed hour; Spot/Swap instrument metadata passed; Swap funding returned one row. Bybit's five checks remain HTTP 403.
- This verifies a narrow OKX sample only. It does not establish full historical depth, universe coverage, or Binance listing authority. Bybit remains unresolved due to HTTP 403; investigate alternate official host / network restrictions only as a separate bounded task. Keep Binance HD-04 authoritative-universe gate BLOCKED, do not merge PR #13 yet, and do not begin strategy/backtesting or live trading.


## Scope decision to prevent HD-04 from stalling the project (23 October 2026)

**Decision:** Do not let broad-universe discovery block the stated BTCUSDT-focused research objective. The blocked endpoint problem is real, but it is only critical for claims about the full current Binance symbol universe, ranking, or expanding to other symbols. It is not a prerequisite for historical research on the explicitly fixed BTCUSDT instrument.

- Rename the unresolved scope conceptually as `HD-04-BROAD-UNIVERSE = DEFERRED/BLOCKED`. Do not claim it passed.
- Resume the critical path with multi-month BTCUSDT historical data: official Binance monthly Spot and USD-M Futures archives, official checksum sidecars, funding history, strict schema/time-grid/gap/duplicate/finite-OHLCV validation, provenance manifest and reproducible coverage report.
- The existing September 2026 slice proves only one month of 5-minute BTCUSDT data and is insufficient by itself for a robust backtest. Expand history before strategy evaluation.
- OKX probe evidence is a data-source cross-check only; it cannot establish Binance's current universe. Bybit HTTP 403 is an access failure from the runner, not evidence of missing data.
- No live trading, credentials, or funds movement. No profitability/time-to-target claim. Strategy evaluation begins only after a sufficiently broad, integrity-checked BTCUSDT history and explicit cost model exist.


## Execution logging rule (standing requirement)

- Every script/workflow action that reads, validates, transforms, uploads, or writes research data must leave a traceable execution record in GitHub.
- Each run record must identify UTC start/end, repository, commit SHA, Actions run ID/attempt, requested inputs, per-step status, exit code, counts/bytes/checksums where applicable, skipped steps and reasons, and output/manifest paths.
- Store detailed console output and machine-readable manifests in the run artifact; write a concise summary to the GitHub Actions Step Summary. Read these logs before reporting a run result. Never log API keys, service-role keys, tokens, or other secrets.
- For BTCUSDT full-history collection, this is implemented in commit [bbabd2c1e1e1302c389d8e75ee95205341724b7c](https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/bbabd2c1e1e1302c389d8e75ee95205341724b7c): execution.log plus btc-usdt-archive-collection-manifest.json are retained with the GitHub artifact for 30 days; the Actions Step Summary links to the run and names the outputs. This logging change is committed but not yet runtime-verified. Durable logs must later be retained in private Supabase Storage only after a canary confirms configuration and upload success.

## Immediate verification status

- Binance connector is available in this conversation and can help with live market snapshots, klines, order book, funding and secondary cross-checks. For long-range reproducible historical acquisition, continue to treat official Binance archive ZIPs and their .CHECKSUM sidecars as the primary source; connector availability does not itself verify archive history.
- The full-history collection workflow remains manual-dispatch only on the research branch. Do not claim that it has executed or that Supabase persistence is active until an actual Actions run log and uploaded object/catalog evidence are inspected.
- Live trading, order placement and funds movement remain unauthorized.


## Official BTCUSDT archive coverage inventory — 23 October 2026

- URL-level HEAD inventory for 2017-08 to 2026-09: 330 monthly archive records; 272 AVAILABLE, 58 UNAVAILABLE, 0 FAIL.
- Spot 1m monthly URLs: all 110 months available from 2017-08 through 2026-09.
- UM Futures 1m and UM funding: 81 months each available from 2020-01 through 2026-09; the earlier 29 tested months return 404 at the exact monthly archive URLs.
- Combined reported compressed archive Content-Length estimate: 386,850,489 bytes (~386.9 MB decimal). HEAD inventory only; this is not full archive validation.
- Verified canaries: 2026-09 all 3 datasets PASS; 2020-01 all 3 PASS; 2019-09 Spot PASS and UM Futures/funding URLs UNAVAILABLE (404).
- Next gate: confirm intended Supabase project before any durable upload. The listed project name does not clearly match this BTCUSDT project. No Supabase data writes have occurred.

## Next gate: longer historical data validation

- Locked protocol: [BTCUSDT candidate walk-forward protocol](docs/BTCUSDT_CANDIDATE_WALK_FORWARD_PROTOCOL.md).
- Acquire and content-validate official BTCUSDT Spot, USDⓈ-M Futures and funding monthly archives for January 2020 through September 2026. The prior HTTP HEAD inventory is availability evidence only, not proof that archive contents validate.
- Preserve the July-September 2026 sample as development data; do not call it an untouched holdout. Forward holdout begins 24 October 2026 under the protocol.
- Do not tune candidates or claim out-of-sample edge until the full data manifest and chronological evaluation gates pass.


## Latest checkpoint — Spot 1m gap audit queued by implementation (23 October 2026)

- Long-history run [39954840075](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39954840075) completed with **231/243 archive checks passing, 12 failed** across 81 months. No combined normalized dataset was emitted. All 243 raw archives are now recorded in the manifest after the preservation-reporting fix.
- Smoke CI [39954846287](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39954846287) passed after the manifest/reporting fixes.
- Fixed two workflow/report issues on `research/full-history-validation`: failed manifest JSON newline encoding and manifest omission of preserved raw archive names on content-validation failures.
- Added `scripts/audit_btcusdt_spot_1m_gap_months.py` to checksum-verify and content-validate official Spot 1m archives for the 12 months whose Spot 5m checks failed. It does not reconstruct or fill 5m candles. The audit is being wired into CI; results are not yet available.
- **Current gate: FAIL / unresolved.** Do not merge PR #17, build the full normalized aggregate, run walk-forward metrics on this dataset, or claim an edge until each failed month is understood and any reconstruction has independent tests/provenance.
- Next action: run the 1m audit; inspect monthly row counts, exact timestamp gaps, OHLC/close-time anomalies and checksum evidence; then decide whether a deterministic 5m reconstruction is supportable for each month.

- CI maintenance note: the first smoke run after adding the 1m audit correctly caught that the new script had not yet been added to the cleanup keep-list. The script is now protected in `CURRENT_PROJECT_KEEP_PATHS.txt`; the subsequent smoke run is pending verification.


## Independent goal-alignment audit and Spot 1m result — 23 October 2026

**Decision: project direction is sound, but the historical-data gate is blocked.** Do not interpret workflow failure as a profitable-strategy failure; it is a data-integrity gate, and the validator itself still needs review.

- Long-history run [39956450372](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39956450372): 81 months, 243 Spot 5m / UM Futures 5m / funding checks; 231 pass, 12 fail; no full normalized dataset emitted. Raw archives/reports were uploaded as artifact [12502203715](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39956450372/artifacts/12502203715).
- Official Spot 1m audit within the same run: **0/12 passed**. All 12 monthly ZIP hashes matched their official .CHECKSUM sidecars, but all had incomplete row counts and timestamp gaps; 2020-12 additionally had one close-time anomaly. Exact row counts and gap timestamps are in the run log and artifact [12501649832](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39956450372/artifacts/12501649832).
- The 12 audited months: 2020-02 (41,346/41,760 rows, 2 gaps), 2020-03 (44,512/44,640, 1 gap), 2020-04 (43,050/43,200, 1), 2020-06 (42,990/43,200, 1), 2020-11 (43,140/43,200, 1), 2020-12 (44,350/44,640, 2 gaps + 1 close-time anomaly), 2021-02 (40,241/40,320, 1), 2021-03 (44,550/44,640, 1), 2021-04 (42,766/43,200, 2), 2021-08 (44,370/44,640, 1), 2021-09 (43,080/43,200, 1), 2023-03 (44,560/44,640, 1).
- Smoke CI after keep-list fix [39956536485](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39956536485) passed. This verifies repository checks, not archive integrity or strategy edge.
- **Goal alignment review:** the target arithmetic/scope is consistent (1,000 USDT toward ~1,061,120.54 USDT, the dated ₹10 crore equivalent), realized-net-profit compounding is correctly defined, candidate results are honestly negative/limited, and tax remains out of scope. However, there is no demonstrated profitable edge or defensible time-to-target yet.
- **Next action:** audit validator assumptions and inspect the exact failed source rows/gaps. Do not reconstruct, interpolate, silently omit, merge PR #17, or run walk-forward until the discrepancy is explained. Any later reconstruction must use only complete, consecutive valid 1m bars, be separately labeled/provenanced, and be reconciled against the official 5m source where available.


## Next sequence action started — official Spot 1m/5m gap reconciliation (23 October 2026)

- Decision: do not reconstruct candles yet. The 12 checksum-valid Spot 1m archives are incomplete under a strict one-row-per-minute assumption; this alone does not prove whether the source archive omitted bars or the validator's continuity assumption is inappropriate for the data.
- Added `scripts/reconcile_btcusdt_spot_1m_5m_gaps.py`. It independently downloads official Spot 1m and Spot 5m monthly ZIPs for the 12 affected months, verifies each official SHA-256 sidecar, counts rows, extracts timestamp discontinuities, and records exact gap spans for comparison.
- Added the script to `CURRENT_PROJECT_KEEP_PATHS.txt` and wired it into the long-history workflow. The audit step is configured to continue to reconciliation even when the 1m audit reports known gaps; artifact upload retains both reports.
- Workflow wiring was corrected after reviewing the YAML; final workflow commit: `d6d2237067d9fd693eae6decade6fdcc733f0187`. Runtime verification is pending.
- **Gate remains BLOCKED:** no candles filled/reconstructed, no failed month silently omitted, no full-history walk-forward, and PR #17 remains unmerged. Next decision depends on exact 1m vs 5m gap evidence.


## Spot 1m/5m reconciliation runtime result (23 October 2026)

- Workflow run [39957820308](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39957820308), commit `d6d2237067d9fd693eae6decade6fdcc733f0187`: the `spot-1m-gap-audit` job completed SUCCESS; Python compilation passed; the 1m audit itself reported 0/12 PASS as expected and was allowed to continue; reconciliation completed for 12/12 months with 0 script errors; combined artifact [12502189825](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39957820308/artifacts/12502189825) uploaded successfully (26,780,461 bytes, 30-day retention).
- Key finding: all 12 months also contain Spot 5m timestamp gaps. In the reported summaries, the 5m gap count matches the 1m gap count for each month; 1m row deficits are multiples of 5m row deficits (e.g. 2020-02: 414 missing 1m rows vs 82 missing 5m rows; 2020-11: 60 vs 12). This points to overlapping missing-data spans rather than a 1m-only discrepancy, but the diagnostic summary does not yet establish the cause or whether gaps represent absent trades, source omissions, or validator assumptions.
- The diagnostic output labels all months `INSPECT`; it does not certify data integrity. It is a descriptive span comparison and does not synthesize or exclude candles. 2020-12 still has the previously observed 1m close-time anomaly.
- The separate `long-history-validation` job in run 39957820308 was still in progress at the time this update was written; no final full-history result is claimed from that run.
- **Next gate:** inspect raw 1m/5m rows around exact gap boundaries and audit validator assumptions against official Binance kline semantics. No reconstruction/interpolation, no silent omission, no walk-forward on incomplete aggregates, no PR #17 merge, no live trading.


## Raw gap-boundary inspection instrumentation (23 October 2026)

- The completed reconciliation run [39957820308](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39957820308) confirms the diagnostic completed, but the separate `long-history-validation` job ultimately failed again. This preserves the blocked data gate; no aggregate/backtest approval follows.
- Updated `scripts/reconcile_btcusdt_spot_1m_5m_gaps.py` to include raw OHLCV rows immediately around detected timestamp discontinuities for both Spot 1m and Spot 5m, while retaining the descriptive-only policy. The report is intended to expose boundary context, not reconstruct candles or prove root cause.
- New commit: `397f2aa8a5d78dc5dd6fa061e82f45275b540058`. GitHub Actions run [39959416562](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39959416562) was queued when recorded; runtime output is pending.
- Next decision depends on reviewing the new report, checking 1m/5m boundary timestamps and auditing validator assumptions. No reconstruction/interpolation, no silent omission, no walk-forward on incomplete history, PR #17 remains unmerged, and live trading remains unauthorized.


## Gap-boundary inspection follow-up (23 October 2026)
- Run [39959416562](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39959416562) completed with **FAIL**: long-history validation remains 231/243 archive checks passed, 12 Spot 5m monthly archives failed strict integrity checks, and normalized aggregate was correctly withheld.
- The new raw boundary-candle instrumentation compiled successfully, but the spot-1m-gap-audit job was **SKIPPED** because its condition matched only three specific commit-message phrases; the actual commit message did not match. Therefore no boundary-candle output was generated by this run and no root-cause conclusion is available yet.
- Fixed the workflow condition to run the diagnostic job on any commit message containing gap at commit d2c083e74a43fe7a9e2f49f19aea42ae7d588e7f. Await the resulting Actions run before interpreting boundary data.
- Do not synthesize/fill candles, change validator rules, start walk-forward testing, or merge PR #17 until the evidence gate is resolved. No live trading authorized; tax/TDS remains out of scope.


## Gap reconciliation runtime (23 October 2026)
- Run [39960237333](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39960237333): diagnostic job **PASS**, all 12 affected months inspected, report artifact uploaded. Full-history validation still **FAIL** at 231/243 checks; normalized full-history aggregate remains withheld.
- Evidence now confirms all 12 affected months have timestamp discontinuities in both official Spot 1m and Spot 5m archives, with matching gap counts per month. Example: 2020-02 has 2 gaps in each interval; 2020-11 has 1 in each. This is consistent with shared missing time spans, but does not establish whether these are no-trade periods, archive omissions, or an incorrect strict-continuity assumption.
- The audit artifact is uploaded, but the connector cannot decode its binary ZIP. The workflow log currently prints gap spans but not the newly captured boundary OHLCV rows. Updated the script to print the boundary context in the next run, commit f93b385225d9384c8060d727f0df9a5773788e82.
- 2020-12 still has one reported 1m close-time anomaly in addition to two gaps. Need boundary output and direct close-time validation before any conclusion. No reconstruction, validator weakening, walk-forward, merge, or live trading. Tax/TDS deferred.


## Diagnostic trigger correction (23 October 2026)
- The first boundary-output change commit triggered the long-history workflow, but the diagnostic job was skipped again because its commit message did not contain the keyword gap. The diagnostic workflow condition is now removed entirely, so any push that triggers this workflow runs the gap diagnostic job. Workflow commit: ea717f631404a4b372ec36e3848e9ae133c68813.
- Await run evidence before concluding boundary-candle review. Full-history validation remains blocked by 12 Spot 5m archive checks; no normalized full-history aggregate, no candle reconstruction, no walk-forward, no PR merge, no live trading. Tax/TDS deferred.


## Gap-boundary evidence review (23 October 2026)
- Workflow run [39968448783](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39968448783) completed: diagnostic job **PASS**, long-history validation **FAIL**. Diagnostic artifact uploaded; full history still has 12 failed Spot 5m month checks among 243 expected archive checks, so no normalized aggregate was released.
- Parsed boundary context from all 12 affected months. Official Spot 1m and 5m archives have matching gap windows/counts, but this is not proof of why bars are absent. Some gap boundaries follow flat, zero-volume bars; several rows have nonstandard raw close-time values (notably 2020-12, also observed in other months). Other boundaries have active volume immediately before gaps. Thus “no trades” is not a sufficient general explanation, and checksum match alone does not establish continuity.
- Decision: **do not relax the validator, synthesize candles, or exclude intervals**. Next evidence step is an independent source-level check of the exact gap windows and anomalous close-time rows, preferably against official Spot trade/aggregate-trade records where available, while retaining raw archives and exact UTC spans. Only after cause is evidenced should validator policy be considered.
- Walk-forward research remains blocked by the full-history gate. PR #17 remains unmerged; live trading remains unauthorized; tax analysis remains deferred.


## Independent trade-level gap cross-check added (23 October 2026)
- Added `scripts/audit_btcusdt_spot_aggtrades_in_gaps.py`, which downloads official Binance Spot monthly BTCUSDT aggTrades archives for the 12 affected months, verifies official SHA256 sidecars, and counts trade records inside each exact UTC gap window. It is diagnostic only and never reconstructs candles.
- Wired a separate `spot-aggtrade-gap-audit` job into the long-history workflow and protected the script in `CURRENT_PROJECT_KEEP_PATHS.txt`. Workflow: [run 39970944134](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39970944134). At documentation time the run was still in progress; no trade-level findings are claimed until its logs/artifact are inspected.
- Workflow authoring caused interim CI failures: an escaped newline in the path filter made the workflow invalid, and the smoke allowlist initially did not include the new script. Both were corrected in subsequent commits; final CI status still needs confirmation. Do not treat the early failed runs as research-data results.
- Next gate: verify the latest workflow YAML parses, the smoke keep-list check passes, then inspect the official aggTrades audit for all gaps. Zero trade counts alone do not authorize relaxing continuity checks; unresolved results remain fail-closed.


## aggTrades audit rerun after cancellation (23 October 2026)
- Run [39970944134](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39970944134) did not complete the monthly aggTrades audit: the runner received a shutdown/cancellation signal after logging six months (2020-02, 2020-03, 2020-04, 2020-06, 2020-11, 2020-12). For those six months the monthly archives passed official SHA256 sidecar checks and the script reported zero aggregate-trade rows in each configured gap window. This is provisional diagnostic evidence only, not proof that kline gaps are valid or that archives are complete.
- The long-history validation job independently failed closed; full-history gate remains blocked. The aggTrades job was rerun as job 120561639973 and is in progress at documentation time. Verify all 12 months and its artifact before recording final counts.
- No validator change, synthetic candles, silent exclusions, walk-forward, PR #17 merge, or live trading. Tax remains out of scope.


## Daily aggTrades gap cross-check result (23 October 2026)
- Workflow run [39997643479](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39997643479) completed. The targeted daily-archive `spot-aggtrade-gap-audit` job passed and verified SHA256 sidecars for every daily archive it inspected. All 12 affected months and all 15 configured gap windows reported **zero aggregate-trade rows** inside the exact half-open UTC intervals. The JSON report was uploaded as artifact `btcusdt-spot-aggtrade-gap-audit`.
- This is evidence only that the downloaded, checksum-matching daily aggTrades archives contain no parsed rows within those exact intervals. It does **not** establish archive completeness, prove that no trades occurred, explain the kline timestamp discontinuities, or resolve the 2020-12 close-time anomaly. Keep the validator fail-closed.
- Same run's full-history job remains **FAIL: 231/243 checks passed, 12 Spot 5m monthly checks failed**; normalized full-history dataset was not built. Spot 1m gap audit passed. No candle reconstruction/filling, no silent exclusions, no walk-forward, and PR #17 remains unmerged. No live trading. Tax remains out of scope.
- Implementation was optimized to fetch only daily aggTrades archives overlapping known gap windows rather than large monthly archives; source comments were corrected to reflect daily archives. Next step: independently validate aggTrades row parsing/schema and investigate the December 2020 close-time anomaly against raw kline rows, without relaxing validation rules.


## Hourly aggTrades coverage sanity check and latest full-history rerun (23 October 2026)
- Commit `27a79e89f2cb1f1cdce5b64066fc85c6235cfba4` corrects `first_timestamp_ms` to report the actual first parsed timestamp instead of UTC day start. Smoke tests passed: [run 40000660516](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/40000660516).
- Latest long-history run [40000657494](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/40000657494) completed with failure. Full-history validation still failed closed: 243 expected archive checks, 12 Spot 5m monthly failures; `normalized_dataset_built=false`. The raw archive/report artifact is `btcusdt-long-history-validation` (artifact ID `12522815424`).
- The corrected daily aggTrades audit job passed and its artifact is `btcusdt-spot-aggtrade-gap-audit` (ID `12521393428`). All 15 configured gap windows still report zero parsed trade rows. Hourly counts show zero-trade hours overlapping the gap windows, while adjacent hours have trade rows; this strengthens the need for independent coverage/source verification but does not prove no trades occurred or establish archive completeness.
- The 2020-12 invalid close-time failure persists (row 5930 in the monthly validator report); other listed failures remain timestamp-gap/ordering errors in the affected Spot 5m archives. No policy relaxation, candle reconstruction, silent exclusions, walk-forward, PR #17 merge, or live trading. Tax remains out of scope.
- Next step: independently inspect the raw ZIP rows and trade timestamp distribution around each exact gap, with special focus on 2020-12-21 and the invalid close-time row, then add regression tests that fail if the audit's gap counts contradict independently computed interval coverage.
