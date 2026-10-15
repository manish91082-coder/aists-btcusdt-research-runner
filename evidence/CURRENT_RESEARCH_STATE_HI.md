# AISTS Current Resume State (Hindi)

Updated: 2026-10-15 after CP-0103 signature diagnostics.

## Last verified execution
- Full source-lineage pipeline CP-0023 → CP-0024 → CP-0025 → CP-0026 → CP-0027 succeeded: run 38725478106.
- Latest focused source-adjudication run succeeded: run 38728831256.
- Focused run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38728831256
- Artifact ID 11969112194; 173,038 bytes; SHA-256 `e2d1de5ad50348ecb357c5e7a003dfa2fd3607f43877190c1aa2a3a728af5386`; seven-day Actions retention.
- Permanent report: `evidence/source_adjudication/CP0103_Run_38728831256_HI.md`
- Permanent CSVs: `CP0103_Economic_Signature_Summary.csv`, `CP0103_Partial_Signature_Summary.csv`, `CP0103_CloseTime_Only_Review.csv`, all under `evidence/source_adjudication/`.
- All source ZIP work ran in GitHub Actions. No Colab interaction required.

## Latest source evidence
- CP-0025 frozen reference set correctly restored: 40 flagged UTC dates, 240 daily archive references, all official-checksum matched.
- 60 daily/monthly shared-open value mismatches: 8 close_time-only; 52 economic/trade-metric.
- 909 unmatched keys: 452 daily-only, 457 monthly-only.
- CP-0103 focused target: 66/66 source archive objects verified, no source/archive errors, 5/5 self tests pass.
- Within the 909 unmatched rows, exact matching count is zero for full economic fields, OHLC-only fields, and OHLC + base volume. This does **not** prove no systematic timestamp alignment issue, but it does not support simply shifting timestamps to recover identical rows.
- 2018-02-09 through 2018-02-11 contains 897/909 unmatched rows (447 daily-only, 450 monthly-only); 450 monthly rows are off-grid with systematic fractional timestamp suffix. Do not round/shift/merge.
- CP-0103 checked 8 close_time-only shared-key cases. Expected-boundary differences are quantified; all 8 remain formally OPEN.
- 2020-12-21 roll-up checks: 34 rows, 25 exact, 9 review-required due missing exact 5m children in source variants. No child candles were filled.
- There are 0 canonical source selections, 0 source case closures, 0 auto-repairs, 0 strategy promotions, and no backtest rerun in CP-0103.

## Research gate state
- G0 BLOCKED_GLOBAL
- G1 PARTIAL_SYSTEM_LEVEL
- G2 FAIL_CURRENT_23_CANDIDATES
- G3 BLOCKED_PARTIAL
- G4 INSUFFICIENT_EVIDENCE
- G5 NOT_RUN
- G6 NOT_BUILT
- G7 LIVE_BLOCKED

## Resume instructions / no drift
1. Do not repeat 770 monthly archive acquisition or the CP-0027 baseline backtest.
2. Next investigate the source-row content/coverage around the 2020-12-21 missing-child window (roughly 13:45–14:55 UTC), using already verified archives. Then formalize disposition evidence for the 52 economic conflicts and 909 unmatched rows.
3. Keep original raw keys and values intact. No source is canonical until an explicit, evidence-backed disposition is recorded.
4. Only if an adjudicated candidate dataset changes bytes should CP-0026/CP-0027 be rerun; then compare with the frozen CP-0040 acceptance rules.
5. Trading strategy/live gate remains blocked. Legacy CP-0027 assumed 10,000 USDT, not the user's ₹10,000 INR planning capital; do not use its absolute currency results as INR projections.


## Cross-thread continuity reconciliation - CP-0107 (2026-10-15)

This append-only note supersedes the CP-0103-only latest-run line above; historical evidence remains unchanged.

### Latest focused runner evidence
- Latest Actions run at audit time: CP-0106, run 38730420808, completed success. Run checkout commit: b6ddcc9ed6c486570dc0c2da8857dd013cba18ae; current main HEAD at inspection: a78b6e0dd531484a0d7f3e1345c420a76c115237.
- CP-0106 artifact ID 11969978987; 579,598 bytes; SHA-256 cdddab3be37f5c593d5cd42ac6c6f72b53f5b3a3fc4dae1218c3bd833850adb4; ZIP CRC PASS; 66/66 scoped source archive/checksum objects verified. Status is PASS_DIAGNOSTICS_ONLY, not research-gate acceptance.
- CP-0107 draft lives on branch cp-0107-row-disposition; it is not merged to main and no CP-0107 Actions job has run.
- CP-0107 evidence covers 10 February off-grid segments/450 rows, 59 December 2020 raw rows, 34 roll-up comparisons with 9 review-required, and eight close-time-only field proposals. Individual raw February row details are still not exported and require another bounded cache-only extraction. No root cause asserted; no source-authority case closed.

### Cross-thread checkpoint alignment and persistence limits
- A separate current-state tracker in the conversation Library reached CP-0092 on 2026-10-15. It records 16 exact official daily ZIP + .CHECKSUM pairs still 0/16 acquired and 0 target bytes; its Colab acquisition cell was prepared but not executed.
- CP-0106's 66/66 result is scoped to objects in the dedicated runner's available archive cache. It does not satisfy or supersede the other track's 16 missing daily ZIP/checksum pairs. Keep these facts separate until exact official bytes and matching sidecars are present and validated.
- Historical project-status and Library artifacts describe the frozen CP-0040 strategy acceptance policy and CP-0041 row worklists, but the full CP-0040 rulebook and authoritative CP-0041 ledger are not present as standalone files in this repository tree. Do not invent thresholds or claim live-ledger reconciliation; locate exact versions before closing cases.
- CP-0100 Drive-save manifest entries were marked LOCAL_BYTES_HASHED_NOT_UPLOADED; no Google Drive upload was evidenced. GitHub commits are not Google Drive backups. The complete four conversation transcripts were not available here for verbatim audit, so this is artifact/checkpoint-level continuity verification, not line-by-line transcript certification.

### Next bounded action to avoid timeout
1. Locate exact CP-0040 rulebook and CP-0041 ledger paths/versions.
2. Run one cache-only GitHub Actions task that streams concise progress and exports all 450 February raw rows with exact source hashes, CSV line numbers and daily coverage; keep output compact and upload CSV/report artifacts.
3. Verify the eight close-time proposals and the 59-row/34-roll-up December files against the 66-object source manifest. Do not run the legacy full pipeline, broad archive acquisition, baseline backtest or any exchange action.
4. Update the gate ledger only after evidence-backed disposition. G0 remains BLOCKED_GLOBAL; all 23 G2 candidates FAIL; G7 remains LIVE_BLOCKED.


## Final CP-0107 extraction and durable-persistence result — 2026-10-15

- Focused GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38735418645. Trigger commit `a59b33464582474719fdaa5e2fc1115443b2ef84`; run completed `success`. Main task runner PASS 11/11; CP-0107 child task `PASS_CACHE_ONLY_EXTRACTION` 9/9.
- A dedicated `publish_cp0107_evidence` job passed output hash/row-count validation and persisted the final outputs to `evidence/source_adjudication/CP0107_Run_38735418645/`. Post-publish `main` commit: `b35953da0d12a84d52429a9dd064842900e0107e`.
- Extraction scope: February 9–11, 2018; intervals 5m, 15m, 30m and 1h. The existing Actions archive cache was restored successfully. No market-data request/network operation was performed by the extraction script; no Binance market-data REST API or strategy/backtest task was used.
- Verified and exported 450/450 monthly off-grid rows, including 12 raw kline fields as text and CSV line numbers; 1,167 daily coverage rows; 10 actual off-grid segments represented in 12 date/interval coverage rows; and 16/16 scoped source objects. Exact daily open-key counterparts for the 450 off-grid rows: 0. Raw source bytes and timestamps were not mutated.
- Output SHA-256: Off-grid raw rows `379b1b9b258eed3fa55dfc95238e43e849300b14b85dd7643c0034befd841d64` (367,591 bytes); daily coverage `5dd5f5b314ff8518f06f6370db5502c79c3fd2a110653b05822921ff2b5dbcde` (638,834 bytes); segment coverage `652562ecd179896e0ecd48f2d434be3c5b81bf139d2ac4098062e43f38caf200` (5,364 bytes); source verification `3692b0dc2378e5115326834a2b09a625341aa245396a4cca8ac1670474ae19b5` (8,050 bytes).
- Hash scope qualification: each monthly ZIP matched its official SHA-256 value recorded in the frozen CP-0106 verification manifest, but this run did not re-fetch/recompute the monthly .CHECKSUM sidecar bytes; their hashes remain parent-manifest references. All 12 daily ZIPs and cached same-directory .CHECKSUM sidecars were locally rehashed and content-matched.
- The pre-run draft file `CP0107_Feb2018_OffGrid_RowDisposition.csv` contains hash cells that were not reliably revalidated and must not be used as the hash authority. Use only the run-scoped `CP0107_Feb2018_SourceVerification.csv`, row export, and persistent output manifest under `CP0107_Run_38735418645/` for row-level hashes.
- This is evidence extraction, not source adjudication: source authority is NOT ASSIGNED, case closures 0, canonical source selection 0, backtest rerun false, candidate promotion false. Gates remain G0 BLOCKED_GLOBAL, G1 PARTIAL_SYSTEM_LEVEL, G2 FAIL_CURRENT_23_CANDIDATES, G3 BLOCKED_PARTIAL, G4 INSUFFICIENT_EVIDENCE, G5 NOT_RUN, G6 NOT_BUILT, G7 LIVE_BLOCKED.
- Cross-thread distinction: the CP-0092 tracker’s separate 16 official daily ZIP+ .CHECKSUM requests remain recorded as 0/16 acquired. CP-0107’s 16/16 is the scoped February segment verification set (4 monthly plus 12 daily objects); it does not clear the separate 0/16 acquisition blocker.
- Frozen CP-0040 rulebook and authoritative CP-0041 ledgers are still not standalone files in this GitHub tree. Historical Library/status documents summarize some policy; no missing threshold or source precedence has been invented. Find the exact authoritative versions and reconcile them before formally closing any source case.
- Failed attempts are retained: run 38734568132 failed due to the script entrypoint typo; run 38735309185 had extraction 9/9 PASS but runner validation failed because request purpose length exceeded 240 characters. Both are diagnostic history, superseded for execution status by run 38735418645; failures have not been erased.

### Next bounded action
Locate exact frozen CP-0040 rulebook and CP-0041 authoritative source ledgers in the Library/project records, then use the durable CP-0107 raw row export to perform row-by-row disposition without timestamp changes or source selection. Separately continue December 2020 and eight close-time metadata cases. Do not download the 770 archive set, rerun the baseline backtest, or change the separate official 0/16 status absent verified acquired bytes.


## CP-0107 × CP-0041 exact source crosswalk — 2026-10-15

- Located and validated the exact CP-0041 authority package from the project Library: ZIP SHA-256 `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`, CRC PASS, 19 members, embedded payload checks 18/18 PASS. The frozen CP-0040 rulebook inside it has SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`; the CP-0041 unmatched ledger SHA-256 is `11eb82994d5a17469eefee9f14d360537d5871c19d303ed0466c5df4f6c34021`.
- Crosswalk result: 450/450 new CP-0107 monthly rows match CP-0041 on interval/open-time key, monthly archive SHA-256 and every one of the 12 raw kline fields; 0 unmatched/new-only keys; 0 row-value mismatches; 0 archive-hash mismatches. Local crosswalk CSV `CP0107_CP0041_Row_Crosswalk.csv`, 452,986 bytes, SHA-256 `5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b`.
- For the 450 timestamp-displacement diagnostics, offsets are 105,211 ms (407 rows) and 1,905,211 ms (43 rows). Daily-row comparison shows 448 mapped keys present in CP-0107 official daily coverage and 2 absent; 442 mapped daily rows have raw-field differences. The old CP-0041 candidate/override diagnostic listed 8 fixed-shift rows with no counterpart; 6 of those keys are found in CP-0107's reverified official daily coverage, while two (5m and 15m, monthly open `2018-02-10T05:58:14.789Z`, mapped target `06:00:00Z`) remain absent. This resolves an evidence-scope distinction, not source causality.
- CP-0040 G0 frozen rulebook requires unexplained/signal-influencing source conflicts to remain unresolved or be explicitly quarantined. Therefore all 450 rows remain `QUARANTINE_REVIEW_REQUIRED`; timestamp shifts remain diagnostic only, root cause OPEN, canonical source NONE, no case closed, no source bytes changed, no backtest rerun, no strategy promoted.
- Full row crosswalk is retained locally as a downloadable working artifact; its SHA-256 is recorded in the canonical GitHub summary JSON. The run-scoped raw rows and source verification remain permanently in `evidence/source_adjudication/CP0107_Run_38735418645/`.
- Separate global gates are unchanged. In particular, the separate CP-0092 official daily ZIP + `.CHECKSUM` acquisition queue remains 0/16; this CP-0107 targeted source crosswalk is not that acquisition task.
