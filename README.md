# AISTS BTCUSDT Research Runner

Standalone GitHub Actions runner for the actual AISTS historical pipeline.

## Primary task: `legacy_pipeline`
One run performs, in order:
1. Revalidates official SHA-256 sidecars and downloads/reuses the official Spot monthly ZIPs for 5m, 15m, 30m, 1h, 4h, 1d and 1mo, 2017-08 through 2026-09.
2. Runs CP-0023 forensic checksum/row/gap scan to generate the required `forensic_gap_events.csv` and source manifest.
3. Runs CP-0024 strict close-time/open-grid audit and selected daily/monthly exact row comparison.
4. Runs CP-0025 flagged-date discovery using CP-0023/24 reports, official daily-reference checksum validation and exact-time reconciliation.
5. Runs CP-0026 provisional candidate construction and the original CP-0027 deterministic gap-aware backtest engine.
6. Exports a compact evidence ZIP plus run summary and file hashes. Raw ZIPs and full candidate datasets are excluded from artifacts.

## Integrity/safety
- Only official `data.binance.vision` public downloadable archive and `.CHECKSUM` objects, with redirect host/path allowlisting.
- No Binance market-data REST API, credentials, orders, signing, or transaction broadcast.
- Raw source ZIPs are never repaired or replaced in place; candidate timestamp normalization is only what the original CP-0026 code already implements.
- Workflow permission is `contents: read`; no arbitrary inline Python or scheduled live-price jobs.
- SHA-256/checksum pass means byte integrity only. It does not assign canonical-source authority.
- CP-0027 is vendored unchanged; its hard-coded starting capital assumption is 10,000 USDT. This is not the user's ₹10,000 INR capital baseline, so absolute amounts require separate recalibration. Percent returns and drawdowns are the primary legacy comparison metrics.
- A completed run is research evidence, not strategy approval. All candidates remain unpromoted pending the frozen rulebook and out-of-sample adjudication.

## Other allowlisted tasks
`smoke`, `historical_reference_replay`, and `monthly_derived_replay` are retained for isolated diagnostics. The primary request should use `legacy_pipeline`.

## Cost/retention
Public repository with standard GitHub-hosted runners. Artifact retention is 7 days. Monthly archive cache is versioned and source bytes are revalidated against fresh official sidecars before reuse. Raw market archives and candidate files are kept in the job workspace/cache, not the artifact.

## Evidence
Each run captures its exact commit SHA, Actions run ID, stage logs, source archive hashes/sidecars, CP-0025 reconciliation outputs, CP-0026 candidate manifest and CP-0027 backtest metrics.
MIT License.
