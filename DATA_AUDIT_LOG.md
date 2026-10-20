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
- Added [manual GitHub Actions workflow](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/workflows/phase2-binance-data-audit.yml) to run Spot and USDⓈ-M Futures audits together and upload reports/evidence artifacts for 14 days. No API keys are used; no trading action is performed.
- The workflow has not been manually dispatched yet. Its default date `2026-10-15` is only a candidate input, not verified archive availability. Phase 2 remains BLOCKED until both reports are downloaded and reviewed.
- A smoke workflow run was triggered to verify the repository changes, but at that log entry its latest status had not yet been confirmed.

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

## Workflow input validation hardening (2026-10-21)
- Added an explicit preflight step to the manual Phase 2 workflow. It rejects non-canonical/invalid dates, symbols outside ASCII letters/digits, and intervals outside the declared options before either archive audit starts.
- Read back the committed workflow and confirmed the new validation step is present. Commit: `37526d0640bf20793274543f4106be7b5d87be15`.
- This prevents a typo from reaching the auditor's early argparse exit without reports. It does not establish that the candidate archive exists, does not verify CI status, and does not change the Phase 2 gate. The workflow still needs to be manually run and both JSON reports reviewed.

## Optional kline CSV header hardening (2026-10-21)
- During the end-to-end Phase 2 code review, identified a format-compatibility risk: the parser treated every non-empty 12-column row as data, so an archive that starts with a column-name row would be counted as malformed.
- Updated `tools/audit_binance_archive.py` to recognise only the exact documented 12-column kline header on the first non-empty record, skip that header when present, and record `csv_header_present` in the JSON report. Header-like text elsewhere is not silently skipped.
- Added four offline unit tests for space-separated and snake_case header names, a real-shaped data row, and wrong column count.
- Commits: runner `5369263058971e14fcae4db438a1e205cbb2c7ce`; tests `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- Verification limit: GitHub file writes were acknowledged, but the updated smoke workflow result has not yet been observed and no real Spot/Futures archive was downloaded. This hardening does not pass Phase 2; both real JSON reports still must be reviewed.

## Optional-header hardening CI verified (2026-10-21)
- GitHub Actions run [39488166620](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39488166620) completed with conclusion `success` on test commit `d0ec62150078b6cf210609dfff24bc6bbdbff579`.
- The run's job steps confirm successful Python compilation, unittest discovery (including the new header tests), CLI help, and malformed-date rejection before network access.
- This verifies the offline smoke suite for that commit only. It does not prove an actual archive download/checksum/API comparison or market-data quality. Phase 2 remains BLOCKED.
- The latest 100 repository workflow runs inspected contained no run named `Phase 2 Binance archive audit`; manual dispatch is not evidenced by this check. The user must run that workflow and provide both market reports/artifact for independent review.

## 2026-10-21 — Recheck of workflow state
- Current `main` ref verified as `ba547c6e18db46d4032757dc3ee4af89099c40bd`.
- Smoke CI success is verified for the offline test commit; it does not substitute for actual archive evidence.
- The latest 100 repository workflow runs inspected contained no Phase 2 archive audit run. Workflow dispatch was not performed; the available GitHub action surface in this session does not provide a dispatch operation.
- Status stays BLOCKED until the manual workflow produces both real market reports and they are reviewed.

## 2026-10-21 — Durable blocker decision and protocol-only progress
- The latest 100 Actions runs contained no Phase 2 audit run. The available GitHub connector has no workflow-dispatch action; this is a tool boundary, not evidence about archive existence or data quality.
- D-018 records the blocker as RESEARCH-OPEN. S-01 to S-04 preregistration was frozen in S01_S04_PREREGISTRATION.md under the contingency already stated in this log.
- Phase 2 remains BLOCKED. No archive/checksum/API result is verified. No backtest may run until exact datasets and cost inputs are audited and accepted.

## 2026-10-21 — Attempted automatic Phase 2 workflow trigger
- To remove the repeated manual step, added a narrowly path-filtered `push` trigger to the existing Phase 2 workflow and set explicit default inputs for push events. Then committed the one-time marker `tools/phase2-audit-trigger.txt` to main.
- Rechecked the latest 100 repository Actions runs after the marker commit. No Phase 2 archive-audit run appeared; the marker-triggered run is therefore NOT VERIFIED and must not be treated as executed.
- No data-quality inference follows from the missing run. Phase 2 remains BLOCKED. Do not create more marker commits or repeat trigger attempts blindly; use the existing workflow's manual Run workflow action once, then inspect its artifact.


## 2026-10-21 — Daily/monthly archive consistency diagnostic added
- Added `tools/compare_binance_archive_cadences.py` to download the official daily and monthly Binance archive for the same market, symbol, interval and UTC date; independently verify each published `.CHECKSUM`; validate ZIP/CSV readability; normalize Spot microsecond timestamps where applicable; and compare the target day's timestamp-keyed candle fields.
- Wired the diagnostic into the Phase 2 workflow for Spot and USDⓈ-M Futures. It is explicitly diagnostic-only: a daily/monthly match does **not** replace the REST API spot-check or promote the Phase 2 gate to PASS. A mismatch is reported as FAIL; network or HTTP availability problems are BLOCKED.
- Added the comparator to offline Python compilation in the smoke workflow. Latest observed smoke runs for these commits are still queued/in progress at the time of this log entry; CI success is not yet claimed.
- Rechecked Phase 2 run [39494153349](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39494153349): archive checksum/ZIP/schema/candle-quality checks passed, but official API comparison remains BLOCKED in this runner's network environment (Spot endpoints returned HTTP 451; Futures numbered endpoints returned HTTP 202, which is not accepted as a verified candle response). Therefore the audit workflow correctly failed its enforcement gate.
- Evidence boundary: daily/monthly cross-cadence comparison has been implemented but has not yet produced a verified report. It is the same official publisher, not an independent source. Phase 2 remains BLOCKED; no backtest, training, paper trading, live order, or deployment has occurred.


## 2026-10-21 — Archive cadence comparison hardening and execution
- Hardened `tools/compare_binance_archive_cadences.py`: identical daily/monthly rows no longer pass if both archives are missing expected candles for a UTC day. For intervals that tile a day, the diagnostic now requires the expected full-day row count as well as exact daily/monthly equality.
- Added offline tests for Spot microsecond timestamp normalization, Futures millisecond timestamps, duplicate timestamp rejection, and the 288-candle expectation for 5m data.
- Smoke run [39495002077](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39495002077) passed for the coverage-hardening commit. The run for the newly added tests and the Phase 2 audit on the same code path were still running at the time of this entry.
- Phase 2 workflow run [39495002145](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39495002145) has now been triggered by the comparator update. Its final outcome and cross-cadence reports must be checked before drawing any data conclusions.
- No protocol substitution: daily/monthly comparison is diagnostic and cannot override a blocked REST API check. Phase 2 remains BLOCKED until reports are reviewed and the locked evidence gate is satisfied.


## 2026-10-21 — Review of cadence diagnostic run and current-month archive availability
- Reviewed completed Phase 2 run [39495002145](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39495002145) and its job logs/artifact.
- For both Spot and USDⓈ-M Futures on 2026-10-15, the daily archive downloaded and its bytes matched the official `.CHECKSUM`. The corresponding October monthly archive URL returned HTTP 404, so daily-vs-monthly comparison is BLOCKED, not FAIL. The month is not complete yet, so this is consistent with a not-yet-published monthly archive; existence of the future monthly file is not inferred.
- The same run confirms the official REST API sample check remains BLOCKED: Spot requests returned HTTP 451; Futures numbered endpoints returned HTTP 202, not an accepted candle payload. Therefore Phase 2 enforcement correctly failed; no audit gate passed.
- Updated the workflow to use a date in the prior completed month for the separate daily/monthly diagnostic when the requested date falls in the current or a future month. The main daily/API audit still uses the requested date, and the diagnostic labels its selected date in logs. This avoids testing an unfinished month's monthly archive.
- Added full-day coverage enforcement to the cadence comparator and offline tests for Spot microsecond normalization, Futures millisecond timestamps, duplicate detection and 5m expected count. Smoke CI [39495002077](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39495002077) passed for the coverage fix; smoke CI [39495019823](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39495019823) passed for the added tests.
- A fresh Phase 2 run using the prior-month diagnostic date has not yet been verified. Phase 2 remains BLOCKED. No backtest, model training, paper trading, live order or deployment has occurred.
