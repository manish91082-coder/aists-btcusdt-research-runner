# Representative Binance Archive Audit Log

Updated: 2026-10-21
Project phase: Phase 2 — representative archive audit
Overall status: BLOCKED in the current execution environment; archive existence and contents are NOT VERIFIED.

## 1. Purpose and target

The locked first target is BTCUSDT Spot 5m, with a corresponding USDⓈ-M Futures kline artifact kept as a separate dataset. This attempt used candidate daily paths for 2026-10-20 only to test access. A candidate URL is not proof that the archive exists.

- Spot candidate archive: https://data.binance.vision/data/spot/daily/klines/BTCUSDT/5m/BTCUSDT-5m-2026-10-20.zip
- Spot candidate checksum: https://data.binance.vision/data/spot/daily/klines/BTCUSDT/5m/BTCUSDT-5m-2026-10-20.zip.CHECKSUM
- USDⓈ-M Futures candidate archive: https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/5m/BTCUSDT-5m-2026-10-20.zip
- USDⓈ-M Futures candidate checksum: https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/5m/BTCUSDT-5m-2026-10-20.zip.CHECKSUM

## 2. Attempts and observed outcomes

1. A HEAD request was attempted from the current container runtime against each of the four URLs above.
2. All four attempts failed before an HTTP response with the runtime error: `URLError: <urlopen error [Errno -3] Temporary failure in name resolution>`.
3. The web retrieval tool also reported the direct Spot and Futures checksum URLs as inaccessible.
4. The official Binance Public Data README was accessible through web retrieval. It documents archive paths, daily/monthly availability, kline schemas, supported intervals, Spot timestamp microseconds from 2025-01-01 onward, and the use of companion `.CHECKSUM` files. Source: https://github.com/binance/binance-public-data/

## 3. What this does and does not prove

**Proven:** The current execution environment could not resolve/retrieve the tested data.binance.vision URLs. The official repository documentation is accessible and describes the expected archive/checksum workflow.

**Not proven:** Whether any candidate archive URL exists; HTTP status or server response; downloaded bytes; file size; SHA-256; official checksum match; ZIP integrity; schema; row count; timestamp unit of the actual file; first/last candle; duplicates; gaps; OHLC validity; API cross-check; or Spot/Futures data quality.

No manifest row is created for a downloaded artifact because no artifact was retrieved. Do not mark the archive audit PASS or FAIL based only on a DNS/access failure. Current audit outcome is BLOCKED.

## 4. Next reproducible route

Use a network-enabled, zero-cost environment already available to the user (for example, their own Google Colab session) to retrieve the exact official URLs and companion checksum files. Do not add credentials or exchange API keys. The first successful run must preserve:
- exact URL and UTC retrieval time;
- original ZIP bytes and byte count;
- unmodified official checksum file and checksum verification output;
- local SHA-256;
- extracted CSV schema and row count;
- raw and normalised timestamps with unit evidence;
- first/last candle, cadence/gap/duplicate/out-of-order counts, malformed rows and OHLC/volume invariant results;
- bounded comparison against the official public API;
- exact runtime/tool versions and a machine-readable report.

If the daily candidate is unavailable, discover a real period from the official directory/listing or use a clearly bounded monthly archive. Confirm existence before treating any path as a dataset. Keep Spot and Futures separate. Do not fabricate a file, checksum, audit output, or PASS.

## 5. Gate status

- Phase 2 archive audit: BLOCKED pending retrieval from a network-enabled environment.
- Bulk download: NOT AUTHORIZED by the phase sequence yet.
- S-01 to S-04 preregistration: NEXT after the representative data audit is actually completed or a durable blocker decision is recorded.
- Strategy backtests, model training, paper trading, live trading: NOT PERFORMED in this audit attempt.


## Audit runner review update (2026-10-21)
- Reviewed the committed runner after initial creation and identified that gap counting between observed rows alone would not detect missing first/last candles of a UTC day.
- Added a UTC-day expected-open coverage check for intervals that tile a day; the JSON report now includes expected count and missing-open examples. First/last event timestamps now use minimum/maximum observed open time rather than row-order endpoints.
- This is a code review/change, not a real-data test. No downloaded archive or audit PASS is claimed. The runner itself still needs execution in a network-enabled runtime and independent review of both market reports.


## Offline CI smoke checks added (2026-10-21)
Added `.github/workflows/audit-runner-smoke.yml`. On relevant pushes/pull requests it checks Python compilation, CLI help, and that a malformed date exits with an argparse error before any archive/network request. This workflow has been committed but its run result has not yet been observed; do not treat it as passed. It does not download or validate market data.


## Offline CI smoke run verified (2026-10-21)
- GitHub Actions run [39485541588](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39485541588) completed with conclusion `success` for commit `e61aab2ec8fd77d345d6652ea2205c562dfe4a90`.
- This verifies the offline smoke checks (Python compile, CLI help, malformed-date rejection) only. It does not download or validate Binance market data, so Phase 2 remains BLOCKED.


## Timestamp validation smoke run verified (2026-10-21)
- GitHub Actions run [39485863361](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39485863361) completed with `success` for auditor commit `d7478dfb4e2b64b309b4640ceee76b18f20b600b`.
- Verified steps: Python compilation, CLI help, and malformed-date rejection. The runner now also contains archive-date membership, interval-aligned open-time, and inclusive close-time checks.
- These are offline/smoke checks only. No archive was downloaded; checksum and real market-data quality remain unverified, and Phase 2 stays BLOCKED.


## Manual Phase 2 workflow added (2026-10-21)
- Added [manual GitHub Actions workflow](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/workflows/phase2-binance-data-audit.yml) to run Spot and USDⓈ-M Futures audits together and upload reports/evidence artifacts for 14 days. No API keys are used; no trading orders are possible from this workflow.
- The workflow has not been manually dispatched yet. Its default date `2026-10-15` is only a candidate input, not verified archive availability. Phase 2 remains BLOCKED until both reports are downloaded and reviewed.
- A smoke workflow run was triggered to verify the repository changes, but at this log entry its latest status had not yet been confirmed.

## Audit status classification correction (2026-10-21)
- Code review found that a temporary public API verification error could be collapsed into a generic audit failure even when no data mismatch had been established.
- Updated `tools/audit_binance_archive.py` so an actual API sample mismatch is `FAIL`, an API transport/availability problem is `BLOCKED`, and the overall audit is `BLOCKED` when a required check is blocked and no required check has established a failure.
- Added unit tests in `tests/test_audit_status_classification.py` and added them to the offline smoke workflow.
- Commits: runner correction `eba227503489c201f99b3a5e6d3a8642b80ede50`; tests `ecf45484be7784aa5a0b044a7f0494396d1f6dcd`; CI test wiring `52b02b398c9fbaa350064fbd1606868c9a45e6e1`.
- These changes require the triggered CI run to be observed and the tests reviewed. This is not a real archive audit. No checksum or dataset PASS is claimed; Phase 2 remains BLOCKED pending both actual market reports.

## Follow-up audit-gate precedence correction (2026-10-21)
- A second review found that a required `BLOCKED` API check could mask a separate, already-proven required-check `FAIL`. The overall status now prioritizes a proven failure, then a blocker, and returns PASS only when every required check is PASS.
- Removed the now-unused API aggregate flag and added a regression test for mixed `FAIL` + `BLOCKED` results.
- Commits: `1a393f1dce292b182f021607f202279acf6fc010` (runner); `c596fa9f242e97594aa32e34ae84ff5147f24b57` (regression test).
- The repository CI result for these latest commits still needs to be observed. This is code/test hardening only; no real Binance archive was downloaded or audited, and Phase 2 remains BLOCKED.
