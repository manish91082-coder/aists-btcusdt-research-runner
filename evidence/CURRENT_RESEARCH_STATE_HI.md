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


## Row-level mapped-field count correction — CP-0107 (2026-10-15)

- Corrected crosswalk counts from actual 450-row CSV: 448 mapped daily targets present, 2 absent; all 448 present rows have at least one non-open-field difference; 442 rows differ in the open-price field; 447 in close_time; 448 in volume. The former summary's generic `442 mapped-field differences` label was ambiguous/mislabeled and is superseded by field-specific counts.
- Evidence reference remains crosswalk CSV SHA-256 `5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b`. This correction does not alter any raw bytes or disposition: 450/450 remain QUARANTINE_REVIEW_REQUIRED.


## Final CP-0107 February quarantine overlay — run 38742035787 (2026-10-15)

- Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38742035787. Runner PASS 11/11; overlay research task PASS 6/6; separate publisher PASS `PASS_HASH_AND_ROW_COUNT_VALIDATED`.
- Durable output folder: `evidence/source_adjudication/CP0107_Run_38742035787/`.
- Row-level file: `CP0107_Feb2018_Disposition_Overlay.csv`, 450 data rows, 1,036,405 bytes, SHA-256 `3fa8cd5e17718dfe3069aab0b1d55fbf990723f1865c77412a957dd63f898a0f`. Persistent manifest independently records the same SHA-256 and byte count.
- CP-0041 crosswalk result is exact for all 450 monthly rows: interval/open key, monthly source archive SHA-256 and all 12 raw kline values match the frozen CP-0041 unmatched ledger/crosswalk. Crosswalk CSV SHA-256 `5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b`; CP-0040 rulebook SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
- Final mapped-daily counts: 448 target rows present and 2 absent. All 448 present targets differ in at least one non-open field; 442 differ in `open`, 447 in `close_time`, and all 448 in `volume`. No exact daily open-key counterpart exists for the 450 original off-grid timestamps.
- Metric correction audit: earlier successful run 38741774289 had a summary wording/count defect (it reported 442 as the total mapped non-open differences and claimed 6 records matched on those fields). Run 38742035787 and its persistent summary supersede that statement: row-level evidence shows 448 non-open-field-difference rows; 442 is specifically the `open`-field-difference count. Earlier run and failure history remain preserved, not erased.
- All 450 rows remain `QUARANTINE_REVIEW_REQUIRED`; root cause OPEN, canonical source NONE, source cases closed 0. No archive bytes changed, no timestamps shifted/rounded, no synthetic candles, no backtest, no strategy promotion. Frozen gates remain unchanged.
- Next bounded checkpoint: exact field-level disposition for the 8 close-time-only conflicts, then December-2020 row/roll-up disposition. No acquisition of the 770 archive set or baseline backtest rerun.


## CP-0107 eight close-time-only joined dispositions — 2026-10-15

- Final joined CSV: `evidence/source_adjudication/CP0107_CloseTimeOnly_FieldDisposition_Final.csv`, 8 rows, SHA-256 `473b149630edb6ee86b1720e2ffa4dd1afa7f022894bf5951ca398199319731c`. Each row now includes expected boundary, raw monthly/daily close_time, selected economic values, monthly/daily archive SHA-256 and checksum-sidecar SHA-256.
- Frozen CP-0040 rulebook SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`; CP-0041 pack SHA-256 `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`; CP-0106 manifest SHA-256 `015709030834ec87c6d76a0b0a4e892650bf7e0949cfc6e6d61ea8659a35a5a1`.
- Five 2017-09-06 rows: monthly close_time +1 ms, daily matches boundary. Three later rows: monthly matches boundary, daily is early by 12,705,211 ms, 84,705,211 ms and 7,200,000 ms. Economic fields match 8/8; 2017 `ignore` field differs but is not the selected conflict.
- All eight remain OPEN_REVIEW_REQUIRED_NO_CANONICAL_SOURCE; root cause OPEN; archive acceptance not assessed, canonical source selected false, cases closed 0. No raw mutation, timestamp shifting, backtest or strategy promotion.


## CP-0107 final path verification and December 2020 disposition sync — 2026-10-15

- The eight close-time joined artifacts already exist under the `_Final` names: `CP0107_CloseTimeOnly_FieldDisposition_Final.csv`, `_Final_Summary.json`, and `_Final_Report_HI.md`. The earlier `_v3` lookup returned 404 only because the expected filename differed; it did not mean the final artifacts were absent. Verified CSV has 8 rows; stored summary records 5/5 diagnostic checks PASS, 5 monthly boundary mismatches, 3 daily mismatches, and economic-field exact matches 8/8. All eight cases remain open, canonical source none.
- December window source detail was rechecked: 59 rows (33 monthly, 26 daily); 16 monthly flat OHLC/zero-base-volume/zero-trade rows; close-time fingerprint `1608558440521` appears in 8 rows; 4 of the flat-zero monthly rows overlap the fingerprint. Existing source-row disposition has 20 `OPEN_REVIEW_REQUIRED` records and 39 `OBSERVED_CONTEXT_ONLY`.
- Parent-child roll-up table was rechecked: 34 comparisons, 25 `EXACT_MATCH` for complete child sets, and 9 `REVIEW_REQUIRED` when exact 5m children are missing. No synthetic aggregates/candles were created.
- Interpretation is diagnostic only. The shared fingerprint does not establish root cause or source authority. All flagged December rows remain open; root cause `OPEN_NOT_ESTABLISHED`; canonical source `NONE`. No archive re-download, raw mutation, timestamp shift, backtest or strategy promotion.


## CP-0107 December 2020 full-cache 5m child audit — run 38756665405

- Focused Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38756665405; runner PASS 11/11, child audit PASS 5/5, publisher PASS. Durable output folder: `evidence/source_adjudication/CP0107_Run_38756665405/`.
- Monthly 5m source ZIP SHA-256 `c169b2a72cc188c8089abc9f3c6f9699e4759a5e7d0d7a7c69d9117b0da68049`, CRC PASS, equals CP-0106 official SHA recorded in source manifest. Monthly `.CHECKSUM` sidecar bytes were not re-fetched/rehashed; sidecar SHA remains the CP-0106 manifest reference. Daily 5m ZIP SHA-256 `b21d0cdd4d29b8a8cfbfbaafd9f926e12989233290daeb0f4977eefb6489525b`, CRC PASS; its cached `.CHECKSUM` was rehashed and content-matched (sidecar SHA `a4aabf08bf9c231daf643071dd531f1f814a7fbdea86b4e8c38a7ce795f13962`).
- Full 2020-12-21 12:30–14:55 UTC exact-grid scan: 30 expected keys per source. Monthly ZIP has 20 exact keys/10 absent; daily ZIP has 16 exact keys/14 absent in this window. The actual raw rows and all 60 per-source expected-key checks are persisted.
- All 9 formerly review-required parent roll-ups were rechecked against the full verified 5m archive bytes. Every case remains `CHILD_KEYS_MISSING_IN_VERIFIED_ARCHIVE`; each prior missing-key list still has its flagged keys absent, with no previously flagged missing key found in the full archive. Exact details are in `CP0107_Dec2020_ReviewRollup_ChildCoverage.csv`.
- This proves exact-key absence in the selected hash-verified ZIP bytes, not why the rows are absent. Root cause OPEN, canonical source NONE, source cases closed 0. No downloads, raw mutation, timestamp shift, synthetic children/aggregates, backtest or strategy promotion.
- Output SHA-256: actual source rows `f397756fb22a267db0e9d2fe96a7bcadab8f4d29c8cd24b1c9397f3bbb89ce37`; 60-key coverage `dcfecaff37f53a017304603d696f6f84c35cdef60941abb59ad8dfa0936f8dc4`; nine-roll-up child coverage `5aed8326dd38921323e6ed6cf6590ec6dd5f73279187f522e4e0509c4dcee9ca`; source verification `daab391c7680ca4e468ff344ffacbcad367be77958aea56519245ff1d207e7d7`.
- Gate states unchanged: G0 BLOCKED_GLOBAL; G1 PARTIAL_SYSTEM_LEVEL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL; G4 INSUFFICIENT_EVIDENCE; G5 NOT_RUN; G6 NOT_BUILT; G7 LIVE_BLOCKED.


## CP-0107 December raw-field and provenance classification — 2026-10-15

- Reconciled 16 common exact 5m open-time keys from committed monthly/daily source rows: 9 exact raw-field pairs, 7 divergent pairs. First economic divergence is 13:15 UTC; six shared keys 13:20–13:45 show monthly flat OHLC `22646.53000000`/zero volume/zero trades versus daily non-flat rows with trades. Source rows are compared field-by-field in `CP0107_Dec2020_Shared_5m_RawField_Comparison.csv`.
- The repeated close-time token `1608558440521` (13:47:20.521 UTC) appears on 8 rows across 5m/15m/30m/1h with different open keys and expected boundaries. Four are monthly flat/zero rows; four are daily non-flat rows. This is an anomaly fingerprint only, not proven upstream cause. Exact raw values and archive references are in `CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv`.
- Full verified archives still lack 10 monthly and 14 daily expected 5m keys in the audited window; all 9 roll-up cases have missing required child keys. Detailed source-specific missing keys are in `CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv`.
- Provenance gaps remain: no documented process/source explains the duplicated close-time token; relationship/independence of daily/monthly exports remains unknown; monthly sidecar bytes were not rehashed in the last run. All affected cases remain OPEN, source NONE, root cause OPEN; no data repair or backtest/promotion. Outputs are in `evidence/source_adjudication/`; their SHA-256 values are in `CP0107_Dec2020_FieldReview_Summary.json`.


## Field-review output integrity metadata correction — 2026-10-15

- Corrected shared 5m comparison CSV no longer includes the misleading boundary-label column. Its current Git blob SHA-1 is `92c9e97f5c4baea175f89e7b36493a18e0934829`; 16 rows.
- The local SHA-256 routine failed its `abc` self-test. Therefore earlier SHA-256 values for the three derived CSVs and summary are superseded and not verified; the JSON now records `sha256: null`, verified Git blob SHA-1, byte count, row count, and an explicit recomputation status. Do not treat the old SHA-256 values as valid.
- Evidence findings unchanged: 16 shared keys, 9 exact raw pairs, 7 mismatches, 8 shared close-time fingerprint rows, monthly 10 and daily 14 missing source keys, 9 affected parent roll-ups. All affected decisions remain OPEN.


## CP-0107 trusted-runner field-review hash audit 38771142900

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38771142900; status PASS_FIELD_REVIEW_HASH_RECOMPUTED, checks 9/9 PASS.
- CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv: rows=8, bytes=5671, SHA-256 b2aa529e3d1e6bd03717507be650b660e712826b1994f9c2619bc47064af509d, Git blob SHA-1 f16e44d15cdec9bf47d974acd85e54d2d8361e7c.
- CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv: rows=24, bytes=9222, SHA-256 cd659b18d996a9ea4d86dba50e07c8c116fc57188f77d5cda07eb9b261ef4110, Git blob SHA-1 4ce746db8ae8f9e6f1622e4c0bae17bf975348c1.
- CP0107_Dec2020_Shared_5m_RawField_Comparison.csv: rows=16, bytes=12019, SHA-256 530d120984e88d37a7993c80151482d8b75677bbec9d04fa31a927373a55aca0, Git blob SHA-1 92c9e97f5c4baea175f89e7b36493a18e0934829.
- Row comparison: 9/16 raw-field exact pairs, 7/16 divergent pairs; close-time fingerprint 8 rows; missing exact child keys monthly 10, daily 14. These findings remain diagnostic, not source acceptance. Root cause OPEN; canonical source NONE; cases closed 0.
- Hashes recomputed by Python hashlib in GitHub Actions. No archive downloads, raw source mutations, backtest or strategy promotion.


## CP-0107 official monthly/daily .CHECKSUM provenance audit 38771593935

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38771593935; status PASS_OFFICIAL_SIDECAR_PROVENANCE; checks 10/10 PASS.
- MONTHLY BTCUSDT-5m-2020-12.zip: official .CHECKSUM fetched from data.binance.vision; sidecar SHA-256 0db24ee3bb2a29cfd9971949837eab439c3226666bb2b00c458aaa16eb249667; checksum token matches frozen archive SHA True; sidecar manifest SHA match True.
- DAILY BTCUSDT-5m-2020-12-21.zip: official .CHECKSUM fetched from data.binance.vision; sidecar SHA-256 a4aabf08bf9c231daf643071dd531f1f814a7fbdea86b4e8c38a7ce795f13962; checksum token matches frozen archive SHA True; sidecar manifest SHA match True.
- Only the two small .CHECKSUM text files were requested. No ZIP archives or market-data REST endpoints were requested. Root cause OPEN; canonical source NONE; no cases closed, no backtest or strategy promotion.


## CP-0107 CP-0041 exact-date daily-reference acquisition and raw-row audit 38775666304

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38775666304; status PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED; checks 98/98 PASS.
- Exact scope: 16 queued official daily ZIPs + 16 .CHECKSUM files. The 14 associated monthly ZIPs were reused from cache and verified against the frozen CP-0041 subset; monthly ZIP downloads: 0.
- Union key rows 1992; shared 1982; exact raw pairs 1550; divergent pairs 432; daily-only 0; monthly-only 10.
- All unequal/missing rows remain OPEN_REVIEW_REQUIRED. Canonical source NONE, cases closed 0, no timestamp shifts/rounding/merge/replace/delete, no synthetic bars/backtest/promotion.
- CP-0041 package SHA-256 23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc; queue member SHA-256 b6660083860d5d90afc5d2661353ecf4c8f1aa2d355a9db99d6fc7a40e9b045d; rulebook SHA-256 5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0.


## CP-0107 CP-0041 11-bucket daily/monthly roll-up overlay 38776970911

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38776970911; status PASS_AGGREGATION_BUCKET_DAILY_SOURCE_REVIEW; checks 12/12 PASS.
- Input row comparison SHA-256 ac08f6839e172919634d2823ae1f6df4d74613e473419b8c00881527e40906ba, source member SHA-256 aba8bfeca2ea62f576075faf926e4c425c862d50428cd59732ab9db88a64442a, frozen CP-0040 rulebook SHA-256 5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0.
- 11 residual buckets checked by exact open-time key across daily and monthly child/parent rows. Daily roll-up status counts: {"DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT": 11}.
- Every bucket stays UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT; source authority NONE, cases closed 0. No raw edits, timestamp normalization, synthetic candles, backtest or strategy promotion.


## CP-0107 CP-0041 450-row worklist disposition delta 38777979719

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38777979719; status PASS_450_ROW_DISPOSITION_DELTA_READY; checks 11/11 PASS.
- Frozen source member: CP-0041 996-row worklist SHA-256 f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f; source package SHA-256 23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc.
- Exact delta: 450/450 crosswalk row IDs matched. Proposed disposition only: QUARANTINE_REVIEW_REQUIRED for those 450 rows. The other 546 rows remain unchanged in the original worklist.
- Daily mapped records: 448 present with non-open-field differences, 2 absent; exact daily open-key counterparts 0/450. All remain quarantined, canonical source NONE, root cause OPEN_NOT_ESTABLISHED, no cases closed.
- This is an append-only delta artifact; the original 996-row worklist/source pack is not rewritten. No timestamps shifted, no raw row replacement/merge/delete, no synthetic candles/backtest/promotion.


## CP-0107 seven residual December 2020 monthly-only exact-key audit 38779041545

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38779041545; status PASS_SEVEN_RESIDUAL_EXACT_KEY_AUDIT; checks 30/30 PASS.
- Seven residual CP-0041 worklist rows individually revalidated against cached monthly archive row tokens and cached daily archive exact open-time keys; archive SHA/CRC checked. Daily exact-key counterparts present: 0; absent: 7.
- All seven monthly rows are flat OHLC 22646.53000000, zero volume/trades. The repeated close-time token and raw row snapshots are retained; nearest timestamps remain diagnostic only.
- All seven remain OPEN; canonical source NONE; root cause OPEN_NOT_ESTABLISHED; cases closed 0. No raw modification, time shifting, synthetic candles, backtest rerun or promotion.


## CP-0107 evidence-index reconciliation (2026-10-15)

- Updated summary: `evidence/source_adjudication/CP0107_Summary.json`; SHA-256 b1c87a81e9ec06448dc8de246214ec6e7a11a4393f3148a01719e956048a55e4; bytes 8601. Consolidated Hindi report: `evidence/source_adjudication/CP0107_Current_Evidence_Reconciliation_Report_HI.md`; SHA-256 b2b2399eba2d2d5c18ee85e565559c4d9a2e68c0299b523ba1eae5927d80cb48; bytes 3235.
- Previous draft preserved at `evidence/source_adjudication/CP0107_Summary_PreAcquisitionDraft_20261015.json`; original blob SHA-1 a5562fcc2cb233110441e9014e1eb8394ee77f8a. Old `0/16` source status is historical and superseded by verified run 38775666304.
- Newest verified runs: 38775666304 (98/98), 38776970911 (12/12), 38777979719 (11/11), 38779041545 (30/30). All source cases remain open.
- Gates unchanged; no canonical source, no case closure, no backtest/promotion.


## CP-0107 derived 996-row worklist integrity (2026-10-15)

- Derived output validated 22/22 checks: 450 crosswalk-backed dispositions changed to QUARANTINE_REVIEW_REQUIRED; 546 other rows remained unchanged. All 996 non-disposition field sets and raw-source JSON hashes are unchanged.
- Full derived view SHA-256 `137ad77bfafa7f7cd788db6f744e5567ad7dba889048b58feb743a34b863d9cb`; row audit SHA-256 `717125e5abd83f987139d76df7ba245b972ad52438d4c64bb2e8bf06901012aa`. Full files, summary, Hindi report and compact index saved in `/AISTS/CP0107/derived_worklist/`.
- Original CP-0041 source pack/worklist/crosswalk/delta are unmodified; no source authority selected, no case closed, and no backtest or strategy promotion.


## CP-0107 unmatched-909 provenance audit (2026-10-15)

- Result: PASS_UNMATCHED_909_MANIFEST_PROVENANCE_AUDIT; 13/13 checks PASS; exact case ID/key/raw JSON matches 909/909; monthly archive manifest references 909/909; daily archive/sidecar/manifest references 909/909; original dispositions preserved 909/909.
- Full audit CSV SHA-256 `b8ffd2a98f9296fdb04a2296f2190caca5387bbb286185a564717aadcb40d980`, 963,228 bytes, 909 rows. Library path `/AISTS/CP0107/unmatched_provenance/CP0107_CP0041_Unmatched_909_Provenance_Audit.csv`.
- This is frozen-ledger/manifest-reference consistency, not a fresh re-download of all source archives. No source cases closed; canonical source NONE; root cause OPEN_NOT_ESTABLISHED. No backtest or strategy promotion.


## CP-0107 shared-60 raw-field provenance audit (2026-10-15)

- PASS_SHARED_60_RAW_FIELD_PROVENANCE_AUDIT; 13/13 checks. 52 economic/trade-metric divergent rows and 8 metadata close-time rows were reproduced from frozen raw tokens; all 60 monthly and daily manifest/hash references and original worklist key/raw JSON links match.
- Full audit CSV SHA-256 7647e5f72f4ee212e2d67aff0dd9851e2556b32e1f882da1dd290b3df1076187, 179,989 bytes, 60 rows. Library path /AISTS/CP0107/shared_conflicts/CP0107_CP0041_Shared_60_Raw_Field_Provenance_Audit.csv.
- No source choice, disposition change, closure, raw repair or backtest. Next: official source archive-version/provenance research for the 52 economic conflicts; gates remain blocked.


## CP-0107 derived 996-row disposition view (2026-10-16)

- Status `PASS_DERIVED_996_ROW_VIEW_VALIDATED`; 22/22 checks PASS. Source pack/worklist/crosswalk/delta hashes verified.
- Derived 996-row view: exactly 450 verified target dispositions set to `QUARANTINE_REVIEW_REQUIRED`; 546 untouched rows; non-disposition fields and raw-source JSON hashes identical 996/996. Originals not modified.
- Full derived worklist SHA-256 `137ad77bfafa7f7cd788db6f744e5567ad7dba889048b58feb743a34b863d9cb`; per-row audit SHA-256 `717125e5abd83f987139d76df7ba245b972ad52438d4c64bb2e8bf06901012aa`. Files stored under persistent Library `/AISTS/CP0107/derived_worklist/` and indexed in GitHub.
- No canonical source or closed cases. G0 remains `BLOCKED_GLOBAL`; no backtest/promotion. Next: remaining 452 daily-only rows and 52 shared economic conflicts.

## CP-0107 final continuity reconciliation and GitHub index publication — 2026-10-16

- Read-only repository verification found `main` HEAD `7c99ebb6ad1db0e9cae110b17e2a559e87d761d9`. At that HEAD, the compact CP-0107 GitIndex payload was absent from the repository tree even though the Library copies existed. This is a publication-state correction, not a research-data change.
- Published the existing verified compressed minimal index at `evidence/source_adjudication/CP0107_CP0041_Derived_996_Row_GitIndex_Minimal.csv.gz` in commit `ecde99840fefa91027145720025f615680b963af`. Git blob SHA-1 `95dec028cb6fc7787990950a55a21cb67c9ffdc8`; 7,282 bytes; source compressed SHA-256 `a3a961a3e3ff0783c1cfed6efafddef313f7c455148a9a5174e95feef80062bf`. Decompressed 996-row CSV SHA-256 `072009025272fcba372b820a2ecbd1c65f5938138c5206f19e7cfcdf83ecc39b`; 185,941 bytes. GitHub branch/tree fetch-back confirmed the path, blob SHA-1, mode `100644` and size.
- Independent current-output validation: **56/56 PASS** across SHA-256 and byte-size checks for the materialized derived worklist, audit, view, summary, report, crosswalk and minimal index; row counts/unique IDs; exact 450-row crosswalk membership and changed-row set; 546 unchanged dispositions/hashes; non-disposition and raw-source-JSON unchanged flags; view/index reconciliation; compressed/decompressed byte equality; summary and gate consistency.
- Validation scope limit: this recheck verified the current materialized output bytes and their internal audit/crosswalk consistency. The original CP-0041 ZIP/worklist and frozen CP-0040 rulebook bytes were not available in the checked repository paths and relevant current Library retrieval results for a fresh raw-byte rehash. Their recorded expected hashes remain references, but **fresh source-pack/rulebook byte re-verification = NOT_VERIFIED**. Do not upgrade this to a full independent source-input reproduction.
- Latest known Actions run at the time of the read-only check was run `38779041545` (success, artifact `11994173921`, 172,937 bytes), checked out commit `17bedc3151fff525c4d58f58a196ccca4fc2c2c6`. It predates the later main commits and is not validation of the current HEAD. The evidence-only index publication does not match the workflow's automatic `requests/**` push trigger; no new run is claimed for it.
- Disposition/authority did not change: 450 crosswalk-target monthly-only rows remain `QUARANTINE_REVIEW_REQUIRED`; 546 rows remain unchanged. Canonical source `NONE`; closed source cases 0; root cause `OPEN_NOT_ESTABLISHED`. No timestamps shifted/rounded, rows merged/replaced/deleted, synthetic candles, backtest rerun or strategy promotion. Gates remain G0 `BLOCKED_GLOBAL`, G1 `PARTIAL_SYSTEM_LEVEL`, G2 `FAIL_CURRENT_23_CANDIDATES`, G3 `BLOCKED_PARTIAL`, G4 `INSUFFICIENT_EVIDENCE`, G5 `NOT_RUN`, G6 `NOT_BUILT`, G7 `LIVE_BLOCKED`.
- Next bounded research objective: evidence-led provenance/version adjudication for the 52 shared economic/trade-metric conflicts, reusing verified CP-0107 snapshots and official checksum evidence. No broad archive refetch, candidate promotion or backtest rerun unless frozen rules require it after a proven candidate-dataset byte/hash change.
- Companion records: `evidence/source_adjudication/CP0107_Final_Continuity_Reconciliation_Summary.json` and `evidence/source_adjudication/CP0107_Final_Continuity_Reconciliation_Report_HI.md`.


## CP-0107 official correction-bundle audit 38862388896

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38862388896; status PASS_OFFICIAL_UPDATE_PACKAGE_INSPECTED_SOURCE_AUTHORITY_OPEN; checks 7/7 PASS.
- Official Git blob SHA-1 90631298cf50ac2e1ee8372a087767b010d78a21; bundle SHA-256 1404dbfb3d62534b2576a6c0c046826fe652f895b9bebfe4c13df58bc8cf6240; bytes 6653240; ZIP CRC PASS.
- Checked 33 CP-0041 monthly archive targets. Exact archive-member hits=0; text-name references=0; frozen current SHA-token hits=0.
- Package matches are version/provenance evidence only. Canonical source NONE; cases closed 0; root cause OPEN_NOT_ESTABLISHED. No Binance market-data REST API, no row edits, no backtest or strategy promotion.


## CP-0107 official correction-bundle audit 38863550950

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38863550950; status PASS_OFFICIAL_UPDATE_PACKAGE_INSPECTED_SOURCE_AUTHORITY_OPEN; checks 13/13 PASS.
- Official Git blob SHA-1 90631298cf50ac2e1ee8372a087767b010d78a21; bundle SHA-256 1404dbfb3d62534b2576a6c0c046826fe652f895b9bebfe4c13df58bc8cf6240; bytes 6653240; ZIP CRC PASS.
- Checked 33 CP-0041 monthly archive targets. Exact archive-member hits=0; text-name references=0; frozen current SHA-token hits=0.
- Shared-52 daily-path crosswalk: 33/52 exact paths across 14 daily archive objects; New checksum equals frozen daily SHA for 33 rows; Original checksum equals it for 0; no exact bundle path for 19 rows. These are version diagnostics only; source authority NONE and cases stay OPEN.
- Package matches are version/provenance evidence only. Canonical source NONE; cases closed 0; root cause OPEN_NOT_ESTABLISHED. No Binance market-data REST API, no row edits, no backtest or strategy promotion.

## CP-0107 shared-52 crosswalk root-publication correction — 2026-10-16

- Run [38863550950](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38863550950) completed SUCCESS in both the research runner and `publish_cp0107_evidence` jobs. The official correction-bundle audit passed **13/13 checks**.
- Publisher initially persisted the 52-row crosswalk in the run-specific evidence folder but its explicit `git add` list omitted the root convenience copy. The output bytes were not regenerated or edited: the root copy was published from the run-specific file in commit `83cd7f203cdd9a995d2f2ef9c9025a2e78731fe9`, and fetch-back confirmed identical Git blob SHA-1 `718c2ac990d9fb5d9c731fdda4fc92657d375ad2`, 39,723 bytes and 52 data rows.
- Workflow staging corrected in commit `17913bfcf67782dcb8f808609b3c54a0e9204d39` to include the root crosswalk on future runs.
- Research outcome remains version provenance only: 33 exact daily paths across 14 official daily archive objects; frozen current daily SHA equals New File Checksum for 33/33 matched conflict rows and Original File Checksum for 0/33; 19/52 rows have no exact bundle path. All 52 cases remain OPEN, canonical source NONE, source cases closed 0, root cause OPEN_NOT_ESTABLISHED. No source-selection decision, source mutation, backtest or strategy promotion.


## CP-0107 Shared-52 raw-value / official checksum crosswalk — 2026-10-16

- Added focused artifact `evidence/source_adjudication/CP0107_Shared52_RowValue_VersionCrosswalk.csv`: 52 economic rows, 30 columns, 116236 bytes, SHA-256 `6a4175567f2af0d0a7e6cf45b76485f496faa680a7248f30e118e55bb2ed0af9`. It preserves both source raw-row JSON tokens and field-level differences per case.
- Input raw-field provenance file independently rehashed on the exact materialized bytes: 179,989 bytes; SHA-256 `7647e5f72f4ee212e2d67aff0dd9851e2556b32e1f882da1dd290b3df1076187`. Official crosswalk blob SHA-1 `718c2ac990d9fb5d9c731fdda4fc92657d375ad2`, 52 rows.
- Exact case join 52/52; exact official daily-path matches 33/52 across 14 archives; no exact path in this bundle 19/52. New checksum equals frozen daily SHA for 33/33 path-matched rows; Original checksum equals frozen daily SHA for 0/33. Every case stays unresolved and no-auto-correction.
- Summary: `evidence/source_adjudication/CP0107_Shared52_RowValue_VersionCrosswalk_Summary.json`; Hindi report: `evidence/source_adjudication/CP0107_Shared52_RowValue_VersionCrosswalk_Report_HI.md`. This is not a full archive refetch/reparse. CP-0040 full standalone raw-byte verification remains `NOT_VERIFIED`.
- Gates unchanged: G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.


## CP-0107 Shared-52 official-bundle no-path triage — 2026-10-16

- Read-only triage report: `evidence/source_adjudication/CP0107_Shared52_NoPath_Triage_Report_HI.md`; source crosswalk Git blob SHA-1 `acbdf6fc6e161cbf18abde221a050701e88a9c01`.
- Reclassified the 19 cases with no exact daily archive path in the single inspected official correction bundle into five UTC-date groups: 2018-02-11 (1), 2020-12-21 (13), 2021-01-21 (2), 2021-09-23 (1), 2021-12-24 (2). These sum to 19/19.
- This is bundle coverage only, not archive nonexistence, source authority, or root-cause proof. All 19 retain `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION`; canonical source NONE; root cause OPEN_NOT_ESTABLISHED; cases closed 0.
- No market archives fetched; no raw rows changed; no timestamps shifted/rounded; no merge/replace/delete; no synthetic candles; no backtest or strategy promotion. Standalone CP-0040 rulebook fresh raw-byte verification remains NOT_VERIFIED.
- Report commit: `253360f9e9813b173fe8fae2496442e46fa96d47`; report blob SHA-1 after fetch-back: `7d4a22b61304a500b17defee57816a557fa4d186`; fetched content exact-match: PASS.
- Research gates unchanged: G0 BLOCKED_GLOBAL; G1 PARTIAL_SYSTEM_LEVEL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL; G4 INSUFFICIENT_EVIDENCE; G5 NOT_RUN; G6 NOT_BUILT; G7 LIVE_BLOCKED.


## CP-0107 frozen-input fresh raw-byte reverification addendum — 2026-10-16

- Freshly materialized Library source package `/AISTS_CP0041_Row_Level_Evidence_Disposition_Pack.zip`: 317,677 bytes; SHA-256 `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`; ZIP CRC PASS; 19 members; embedded manifest 18/18 payload byte-count and 18/18 SHA-256 checks PASS.
- Independently rehashed embedded CP-0040 rulebook: 10,630 bytes; SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`; CP-0041 original 996-row worklist: 2,111,342 bytes; SHA-256 `f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f`; 909-row unmatched ledger: 1,850,523 bytes; SHA-256 `11eb82994d5a17469eefee9f14d360537d5871c19d303ed0466c5df4f6c34021`.
- Materialized CP-0107 crosswalk independently rehashed: 450 rows, 452,986 bytes, SHA-256 `5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b`. Derived worklist SHA-256 `137ad77bfafa7f7cd788db6f744e5567ad7dba889048b58feb743a34b863d9cb` (996 rows); row audit SHA-256 `717125e5abd83f987139d76df7ba245b972ad52438d4c64bb2e8bf06901012aa` (996 rows); Library summary SHA-256 `31bf7846d3429e6590724250459bf2fc1317dcabccf71cca8c21b5ed575fee96`.
- Fresh row comparison: 996/996 unique IDs exact; changed IDs 450/450 equal crosswalk IDs; only `current_disposition` changed on those 450; 546 rows fully unchanged; zero non-disposition changes. Crosswalk reports 450/450 monthly archive hash matches and 12-field raw equality flags. Audit invariants: 996/996 non-disposition unchanged and original-source-row-JSON unchanged.
- Targeted verification register: **23/23 PASS, 0 FAIL**. This fresh evidence supersedes the earlier CP-0107 note saying the standalone frozen raw-byte rehash was NOT_VERIFIED, limited to the source package, embedded rulebook, original worklist, unmatched ledger and materialized derived/crosswalk files named in the addendum.
- GitHub addendum report: `evidence/source_adjudication/CP0107_Frozen_Input_Reverification_Addendum_HI.md`; companion JSON: `evidence/source_adjudication/CP0107_Frozen_Input_Reverification_Addendum_Summary.json`. Raw-URL and GitHub contents fetch-back exact text comparisons: report PASS, JSON PASS.
- Publication commits: report correction `333314c040369efca07e6cd1fcde841753ce7cb2`; summary `eb5f3191fdf9ce45cb70ad9faa42961e273af106`. Current main HEAD at this check: `eb5f3191fdf9ce45cb70ad9faa42961e273af106`.
- No Actions run was triggered for this addendum; do not claim CI validation. Latest visible workflow run remains #47 / 38863550950, success on older SHA `3150359d658a7a2011b3458f6b4e0ffe3ae88aa9`, not current HEAD.
- Decisions/gates unchanged: canonical source NONE; cases closed 0; root cause OPEN_NOT_ESTABLISHED; G0 BLOCKED_GLOBAL; G1 PARTIAL_SYSTEM_LEVEL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL; G4 INSUFFICIENT_EVIDENCE; G5 NOT_RUN; G6 NOT_BUILT; G7 LIVE_BLOCKED. No raw-source mutation, timestamp shift, synthetic candles, backtest rerun, strategy promotion or exchange action.
- Next bounded objective: adjudicate the 52 shared economic/trade-metric conflicts against the already inspected official correction-bundle version evidence, keeping the 33 path matches as provenance-only and 19 no-path cases unresolved. No broad archive refetch.



## CP-0107 Shared-52 evidence-linked matrix independent verification — 2026-10-16

- Independently fetched and parsed the committed matrix `evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Matrix.csv`: Git blob SHA-1 `8e727ea57035240a912040972e73a3ed12c2a653`, 112,361 bytes, 52 rows, 26 columns.
- Compared each of the 52 matrix case IDs to both committed crosswalks: exact joins 52/52 to `CP0107_Shared52_RowValue_VersionCrosswalk.csv` (blob `acbdf6fc6e161cbf18abde221a050701e88a9c01`) and 52/52 to `CP0107_Official_Update_Package_Shared52_DailyCrosswalk.csv` (blob `718c2ac990d9fb5d9c731fdda4fc92657d375ad2`). No duplicate or missing matrix case IDs.
- Matrix-vs-raw-crosswalk equality checks for monthly/daily raw-row JSON, raw-row hashes, monthly/daily archive hashes, official bundle path, exact-path flag, and Original/New official checksums: 0 mismatches. Exact-path status agrees with official crosswalk 52/52.
- Evidence classification: 33 rows have exact official daily path and New File Checksum equals frozen daily SHA for 33/33; 19 rows have no exact path in this one inspected bundle. Original File Checksum matches frozen daily SHA for 0/33 matched rows.
- All 52 dispositions remain `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION`; canonical source NONE 52/52; root cause OPEN_NOT_ESTABLISHED 52/52; case_closed FALSE 52/52. Matrix decision-state/join issues: 0. This validates matrix integrity, not source authority or root cause.
- Report: `evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Matrix_Report_HI.md`; companion JSON: `evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Matrix_Summary.json`. Raw-URL vs GitHub contents fetch-back exact comparison: report PASS, summary PASS.
- No Actions run was triggered for this report; CI is not claimed. No market archives were fetched, no raw data altered, no backtest rerun, no strategy promoted, no source case closed. Gates unchanged: G0 BLOCKED_GLOBAL; G1 PARTIAL_SYSTEM_LEVEL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL; G4 INSUFFICIENT_EVIDENCE; G5 NOT_RUN; G6 NOT_BUILT; G7 LIVE_BLOCKED.
- Next: inspect only the already committed official correction-package inventory/manifest for further authoritative evidence. If it contains none, record a documented limitation and move to the next global blocker. Do not repeat the same 52-case crosswalk checks or fetch broad archives.


## CP-0107 Shared-52 evidence-linked disposition matrix — 2026-10-16

- Published `evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Matrix.csv` (52 rows, 26 columns, 112,361 bytes; Git blob SHA-1 `8e727ea57035240a912040972e73a3ed12c2a653`). It joins the existing raw-value crosswalk (blob `acbdf6fc6e161cbf18abde221a050701e88a9c01`) to the official-update crosswalk (blob `718c2ac990d9fb5d9c731fdda4fc92657d375ad2`) by exact case ID.
- Fresh matrix verification: 52/52 unique IDs; 52/52 joins; 15 row-level identity/hash/disposition invariants per case = 780/780 comparisons PASS after normalizing the official CSV's boolean text casing (`False` vs matrix `FALSE`). The JSON summary records per-field counts and the result.
- 33/52 cases: official correction bundle `New File Checksum` equals frozen daily archive SHA-256; `Original File Checksum` equals frozen daily SHA-256 for 0/33. These are version-provenance results only, not a universal canonical-source decision. The other 19/52 only lack an exact path in this inspected bundle.
- Case-linked report: `evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Report_HI.md`; summary: `evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Summary.json`.
- Candidate dependency focus: the 52-case matrix has four unresolved higher-timeframe rows directly relevant to current named multi-timeframe candidates: `SHARED-4h-1611216000000` (2021-01-21 08:00 UTC), `SHARED-4h-1640304000000` (2021-12-24 00:00 UTC), `SHARED-1d-1611187200000` (2021-01-21 00:00 UTC), and `SHARED-1d-1640304000000` (2021-12-24 00:00 UTC). Their listed differences are volume, quote volume, trade count and taker-buy volume fields; OHLC fields are not listed as different for these four. All four remain open because source authority is not established. Whether these metrics influence a candidate must be checked against the actual frozen strategy implementation/config before any G0 quarantine-exemption decision.
- Current disposition remains unchanged: all 52 unresolved; canonical source NONE; root cause OPEN_NOT_ESTABLISHED; cases closed 0. No source mutation, timestamp shift, synthetic bars, broad archive refetch, backtest rerun or strategy promotion.
- Gates unchanged: G0 BLOCKED_GLOBAL; G1 PARTIAL_SYSTEM_LEVEL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL; G4 INSUFFICIENT_EVIDENCE; G5 NOT_RUN; G6 NOT_BUILT; G7 LIVE_BLOCKED.
- No Actions run was triggered for this matrix. CI success is not claimed for this commit.
- Next bounded step: inspect the actual frozen candidate code/config and build a dependency map for these four 4h/1d cases first, then other cases only for the intervals/features those candidates consume. Use the frozen CP-0040 G0 quarantine rule; do not fetch archives again unless a specific missing evidence item is identified.



## CP-0107 unmatched-909 distribution and gate triage — 2026-10-16

- Materialized Library audit bytes independently hashed: `/AISTS/CP0107/unmatched_provenance/CP0107_CP0041_Unmatched_909_Provenance_Audit.csv`, 963,228 bytes; SHA-256 `b8ffd2a98f9296fdb04a2296f2190caca5387bbb286185a564717aadcb40d980`; matches the existing summary hash.
- Parsed 909 rows / 909 unique IDs: 452 daily-only and 457 monthly-only. All 909 monthly manifest hash references, daily manifest/sidecar references, source-row JSON references, frozen worklist key/raw JSON, and existing disposition checks match. All 909 remain exact-counterpart-absent, quarantine-pending-source-attribution, canonical source NONE, root cause OPEN_NOT_ESTABLISHED, case_closed FALSE; no-shift/round/merge/replace/delete flag true.
- Distribution: 2017-09-06=5 daily-only; 2018-02-09=266 daily-only + 270 monthly-only; 2018-02-10=168+168; 2018-02-11=13+12; 2020-12-21=0+7. February 9-11 account for 897/909 (98.68%) of unmatched keys. This is exact-key distribution only, not permission to timestamp-shift.
- Published report `evidence/source_adjudication/CP0107_Unmatched_909_Distribution_Gate_Triage_HI.md` and summary `evidence/source_adjudication/CP0107_Unmatched_909_Distribution_Gate_Triage_Summary.json`. Raw-URL vs GitHub contents fetch-back exact comparisons: report PASS, summary PASS. Publication commits report `f677429e8e6f23ac0654b4e3df50aff5faf9993c`, summary `b13bbb5c6ab0f5fc211bb20bafc754c6ab57227a`.
- Decision: stop repeating the same 909-row provenance audit and stop reprocessing the same 2022-08-08 official correction bundle. The available evidence proves ledger/manifest consistency only; it does not select a canonical source. Treat unmatched keys as quarantined documented data limitations unless distinct official source/version evidence is already available. G0 remains BLOCKED_GLOBAL. No new archive fetched, no source mutation, no backtest rerun, no strategy promotion; live actions remain blocked.
- Next bounded task: frozen-CP0040 candidate-data eligibility review, explicitly excluding quarantined rows, and determine whether any research-eligible dataset remains. If none, report a hard BLOCKED decision instead of looping.


## CP-0040 G0 candidate-data eligibility review — 2026-10-16

- Frozen rulebook reverified from CP-0041 package: 10,630 bytes, SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
- Inspected `scripts/AISTS_CP0026_Research_Candidate_Builder.py` (Git blob `3ef0376ff4d8e6f6cfd6550512029e75d99ad75b`). Its source selection is date-level: daily archives for CP-0025 flagged dates, monthly otherwise. In the inspected candidate loop, every row from the selected daily archive is appended without an exact-key lookup against CP-0107's 909 unmatched / 52 shared economic-conflict dispositions. Thus the existing builder has not demonstrated required row-level quarantine for unresolved signal-influencing rows.
- Decision: existing CP-0026 candidate policy is not G0-eligible as currently evidenced; G0 remains BLOCKED_GLOBAL. No CP-0026 build was run and no candidate-output status is asserted.
- Unresolved evidence kept distinct: 909 unmatched exact-open-key rows (452 daily-only, 457 monthly-only); 52 shared economic conflicts (33 official New-checksum provenance matches, 19 no-path in the inspected bundle); 8 close-time-only cases (economic fields exact, five monthly and three daily boundary mismatches). The 450 February-2018 off-grid monthly rows are a subset of the 909, not an additional count; exact daily open-key matches are zero. December residual 7 and 9 review-required roll-ups remain open.
- Report `evidence/source_adjudication/CP0040_G0_Candidate_Data_Eligibility_Review_HI.md`; JSON `evidence/source_adjudication/CP0040_G0_Candidate_Data_Eligibility_Review_Summary.json`. Raw-URL vs GitHub contents fetch-back: report PASS, summary PASS. Commits: report `f8817b2398f438800571c7b1b8b5d988512a9f90`, summary `bd48ef09588c0f00012010d9b744f3a266f2424e`.
- Next required implementation gate: create an exact-key row-level quarantine manifest, patch the candidate builder to fail closed if unresolved keys survive, test deterministic fixtures, then build and hash the quarantined candidate. Re-run historical backtest only if the candidate bytes change. No raw archive edits, no timestamp shifts, no source cases closed, no strategy promotion, and no live actions.
- Gates remain G0 BLOCKED_GLOBAL; G1 PARTIAL_SYSTEM_LEVEL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL; G4 INSUFFICIENT_EVIDENCE; G5 NOT_RUN; G6 NOT_BUILT; G7 LIVE_BLOCKED. CI was not run for this review.


## CP-0040 exact-key quarantine gate self-test — 2026-10-16

- Added `scripts/AISTS_CP0040_Quarantine_Gate.py`: exact `(interval, open_time_ms)` key validation and quarantine partition primitives. Timestamp tokens are not rounded; fractional timestamp tokens are rejected; row objects are not mutated.
- Added allowlisted runner task `cp0040_quarantine_gate_tests`; it uses Python standard library only and does not trigger market-data downloads or backtests.
- Local deterministic self-test: 7/7 PASS; Python compile PASS.
- GitHub Actions run [38874755147](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38874755147) on commit `15a2f1826e27e7bbccde74ffafc035b645a594ea`: terminal `completed/success`; runner checks 11/11 PASS; task summary 7/7 PASS. Downloaded artifact ZIP CRC PASS and summary bytes were parsed.
- Published report `evidence/source_adjudication/CP0040_ExactKey_Quarantine_Gate_SelfTest_HI.md` (commit `c81cef287ed738b2994b97cc10ca2275368b2a62`) and JSON `evidence/source_adjudication/CP0040_ExactKey_Quarantine_Gate_Summary.json` (commit `6352b6bb6ab5592c342d8536937ac74e374e3817`).
- Scope is strictly synthetic tests. This does not validate the actual market-data manifest, does not build/filter candidate data, and does not run a backtest. The new primitive is not yet integrated into CP-0026. G0 remains `BLOCKED_GLOBAL`; strategy approval and all live actions remain blocked.
- Next bounded action: build and verify the complete frozen exact-key quarantine manifest, then integrate the gate into CP-0026 with fail-closed completeness/count/hash checks. Do not build a candidate until the full manifest is proven complete.


## CP-0040 exact-key quarantine manifest run 38882377148

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38882377148; status PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN; checks 17/17 PASS.
- Row-level exact-key manifest: 969 rows / 969 unique keys. Classes: {"CLOSE_TIME_ONLY": 8, "DAILY_ONLY_ROW": 452, "MONTHLY_ONLY_ROW": 457, "SHARED_ECONOMIC_CONFLICT": 52}.
- The 450 off-grid rows are a subset of the 909 unmatched rows and were not double-counted. Shared-52 plus close-time-only 8 cover the 60 shared conflict records.
- Separate non-row blockers: 27 (11 aggregation buckets, 16 missing daily-reference acquisition cases). Candidate eligibility remains BLOCKED.
- Manifest SHA-256 d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819; blocker ledger SHA-256 d0126152a58baecd8f61bcdcc21286ecffacba6427e7b09696ca63db33c1f0d0. The published frozen index was re-hashed; the original CP-0041 package/rulebook bytes were not freshly re-hashed in this run.
- No canonical source selected, no cases closed, no candidate build/backtest, no strategy promotion, live actions remain BLOCKED.


## CP-0040 manifest + CP-0026 fail-closed builder integration — 2026-10-16

- Manifest workflow [38882377148](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38882377148) completed successfully; 17/17 manifest checks passed and scoped evidence publisher committed run-scoped evidence under `evidence/source_adjudication/CP0040_Run_38882377148/`.
- Exact row-level manifest: 969 rows / 969 unique (interval, open_time_ms) keys. Counts: 452 daily-only, 457 monthly-only, 52 shared economic conflicts, 8 close-time-only. The 450 off-grid rows are a subset of the 909 unmatched rows and were not double-counted.
- Manifest SHA-256 `d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819`; separate blocker ledger SHA-256 `d0126152a58baecd8f61bcdcc21286ecffacba6427e7b09696ca63db33c1f0d0`.
- 27 non-row blockers remain: 11 residual aggregation buckets + 16 missing daily-reference acquisition cases. They have no exact row keys in the frozen minimal index; no timestamps were guessed. Candidate eligibility remains BLOCKED.
- Integrated the manifest gate into `scripts/AISTS_CP0026_Research_Candidate_Builder.py`: verifies summary status, manifest SHA/rows/schema/key uniqueness/class counts, open status and canonical source NONE; refuses to proceed while any non-row blocker remains; exact-key filtering records quarantined selected-source rows to a separate audit output when eligibility is eventually ready.
- Regression workflow [38882676704](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38882676704) completed successfully: runner 11/11 PASS, builder-gate tests 5/5 PASS, 23 Python sources parse successfully. The actual manifest was read and the gate refused build because 27 blockers remain.
- Report: `evidence/source_adjudication/CP0040_CP0026_Quarantine_Gate_Integration_Report_HI.md`; summary: `evidence/source_adjudication/CP0040_CP0026_Quarantine_Gate_Integration_Summary.json`.
- No candidate dataset build, no backtest, no canonical source selection, no case closure, no strategy promotion. Live signing, public broadcast and exchange orders remain BLOCKED.
- Next: resolve or formally disposition the 27 non-row blockers with exact evidence, update manifest/gate state, and rerun regression checks before considering a candidate build.


## CP-0040 exact-key quarantine manifest run 38883343753

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883343753; status PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN; checks 19/19 PASS.
- Row-level exact-key manifest: 1411 rows / 1411 unique keys. Classes: {"ACQUISITION_ECONOMIC_CONFLICT": 14, "ACQUISITION_MONTHLY_ONLY_ROW": 10, "ACQUISITION_RAW_FIELD_CONFLICT": 418, "CLOSE_TIME_ONLY": 8, "DAILY_ONLY_ROW": 452, "MONTHLY_ONLY_ROW": 457, "SHARED_ECONOMIC_CONFLICT": 52}.
- The 450 off-grid rows are a subset of the 909 unmatched rows and were not double-counted. Shared-52 plus close-time-only 8 cover the 60 shared conflict records.
- Separate non-row blockers: 11; counts={"RESIDUAL_AGGREGATION_BUCKET": 11}. Candidate eligibility remains BLOCKED.
- Manifest SHA-256 d62c30c8ac7a4e5241b48e79884e68395fd1904826cfd70549886876269642b2; blocker ledger SHA-256 f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36. The published frozen index was re-hashed; the original CP-0041 package/rulebook bytes were not freshly re-hashed in this run.
- Acquisition extension reviewed 1992 raw row pairs: 432 divergent pairs, 14 economic-field divergences, and 10 monthly-only keys. Newly added unique keys=442; overlapping keys enriched=0. No new downloads.
- No canonical source selected, no cases closed, no candidate build/backtest, no strategy promotion, live actions remain BLOCKED.


## CP-0040 acquisition extension and current CP-0026 gate regression — 2026-10-16

- Extended the row-level quarantine manifest using the committed CP-0107/CP-0041 acquisition comparison after verifying its recorded SHA-256 and row count. No new network downloads.
- Latest current manifest pointer: `evidence/source_adjudication/CP0040_Current_Manifest.json`; run-scoped evidence: `evidence/source_adjudication/CP0040_Run_38883343753/`.
- Manifest is now 1,411 rows / 1,411 unique exact keys, SHA-256 `d62c30c8ac7a4e5241b48e79884e68395fd1904826cfd70549886876269642b2`. Added 442 unique keys from the acquired daily-reference comparison: 432 shared raw-divergent pairs (14 economic-field and 418 non-economic raw-field divergences) plus 10 monthly-only keys. The 10 absent expected-grid keys exactly match the 10 monthly-only keys.
- The 16 daily archive acquisition cases were removed from the non-row blocker ledger only after their 16 ZIPs/sidecars were verified and their row-level comparisons were incorporated. This does not close source cases or choose a canonical source.
- Remaining non-row blockers: 11 residual aggregation buckets. No timestamps guessed, no synthetic candles, no source cases closed.
- CP-0026 builder gate regression [run 38883430122](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883430122): runner 11/11 PASS; gate tests 5/5 PASS against the current 1,411-key manifest; builder refuses candidate processing due to the 11 unresolved buckets.
- Report: `evidence/source_adjudication/CP0040_Acquisition_Extension_And_Gate_Regression_Report_HI.md`; summary: `evidence/source_adjudication/CP0040_Acquisition_Extension_And_Gate_Regression_Summary.json`.
- No candidate dataset or backtest was run. G0 remains `BLOCKED_GLOBAL`; strategy approval and all live actions remain blocked.
- Next bounded action: inspect the 11 residual aggregation buckets against committed row-level evidence and determine whether any can be dispositioned without source inference or timestamp repair.


## CP-0040 exact-key quarantine manifest run 38883792900

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883792900; status PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN; checks 14/14 PASS.
- Row-level exact-key manifest: 1427 rows / 1427 unique keys. Classes: {"ACQUISITION_ECONOMIC_CONFLICT": 14, "ACQUISITION_MONTHLY_ONLY_ROW": 10, "ACQUISITION_RAW_FIELD_CONFLICT": 418, "AGGREGATION_BUCKET_ROW_QUARANTINE": 16, "CLOSE_TIME_ONLY": 8, "DAILY_ONLY_ROW": 452, "MONTHLY_ONLY_ROW": 457, "SHARED_ECONOMIC_CONFLICT": 52}.
- The 450 off-grid rows are a subset of the 909 unmatched rows and were not double-counted. Shared-52 plus close-time-only 8 cover the 60 shared conflict records.
- Separate non-row blockers: 11; counts={"RESIDUAL_AGGREGATION_BUCKET": 11}. Candidate eligibility remains BLOCKED.
- Manifest SHA-256 e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a; blocker ledger SHA-256 f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36. The published frozen index was re-hashed; the original CP-0041 package/rulebook bytes were not freshly re-hashed in this run.
- Aggregation-bucket quarantine coverage: 11 open bucket relationships, 35 unique parent/child row keys represented; new keys added=16. The 11 relationship cases remain blockers and source authority remains NONE.
- No canonical source selected, no cases closed, no candidate build/backtest, no strategy promotion, live actions remain BLOCKED.


## CP-0040 aggregation bucket exact-key quarantine extension — 2026-10-16

- Added the 16 previously missing exact keys identified by the committed CP0107 aggregation-bucket row evidence. Across 11 buckets, 78 row-evidence records cover 35 unique interval/open_time_ms keys; 19 were already quarantined and 16 were added.
- Current manifest pointer `evidence/source_adjudication/CP0040_Current_Manifest.json`; latest manifest run `CP0040_Run_38883792900`; 1,427 rows / 1,427 unique keys; SHA-256 `e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a`.
- All 35 parent/child exact keys from the aggregation evidence are now represented in the quarantine manifest. The 11 aggregation relationship cases remain open; daily child rollups match daily parents in 11/11, while the frozen monthly mismatch signature remains in 11/11. No canonical source selected, no root cause established, no case closed.
- CP-0026 gate regression [run 38883871540](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883871540): runner 11/11 PASS; gate tests 5/5 PASS; builder correctly refuses candidate processing because the 11 relationship blockers remain.
- Report: `evidence/source_adjudication/CP0040_Aggregation_Bucket_ExactKey_Quarantine_Report_HI.md`; summary: `evidence/source_adjudication/CP0040_Aggregation_Bucket_ExactKey_Quarantine_Summary.json`.
- No candidate build/backtest; G0 remains `BLOCKED_GLOBAL`; no strategy promotion or live actions.
- Next: obtain a rulebook-aligned disposition for the 11 aggregation relationships. Exact-key quarantine alone does not authorize opening G0.


## CP-0040 aggregation relationship hold decision — 2026-10-16

- Published `evidence/source_adjudication/CP0040_Aggregation_Relationship_Hold_Decision_HI.md` (commit `24f3374727b00669bfbaa8ce5753ff2cd06e4d78`).
- Decision: HOLD all 11 cross-interval aggregation relationship cases as `OPEN_NOT_ESTABLISHED`; G0 remains `BLOCKED_GLOBAL`; candidate eligibility remains BLOCKED.
- Basis: 1,427/1,427 unique manifest keys; all 35 parent/child keys from the 11 buckets are represented; daily child rollups match daily parents in 11/11, but the monthly mismatch signature persists in 11/11. The non-row blocker ledger still contains 11 `RESIDUAL_AGGREGATION_BUCKET` cases.
- The known frozen rulebook hash remains `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`. This checkpoint does not claim a fresh clause-by-clause verification of the original package; row-level quarantine is not treated as authority to close relationship-level blockers.
- Root cause NOT ESTABLISHED; source authority NONE; canonical source selections 0; cases closed by this checkpoint 0.
- Candidate build/backtest NOT RUN; strategy promotion NOT performed; live signing, public broadcast and exchange orders remain BLOCKED.
- Next bounded action: retrieve the exact frozen CP-0040 rulebook bytes from the verified CP-0041 authority package and record a clause-level G0 crosswalk for each of the 11 relationship cases. If exact bytes are unavailable, preserve HOLD and do not infer clearance.


## CP-0040 rulebook clause crosswalk amendment — 2026-10-16

- Recovered the exact frozen rulebook from conversation file `AISTS_CP0041_Row_Level_Evidence_Disposition_Pack.zip`; package SHA-256 `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`, ZIP CRC PASS, embedded rulebook SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0` verified exact.
- Clause crosswalk: G0 §18 requires unresolved cross-timeframe conflicts be marked `UNRESOLVED` and quarantine sensitivity run separately; G0 §19 permits quarantine-based PASS only when each unresolved item is explicitly quarantined AND final metrics are based on that quarantine policy; G3 §38 requires source-policy/quarantine sensitivities and keeps the data gate open for material differences unless adjudicated or conservative quarantine is frozen.
- Actual CP-0041 aggregation disposition CSV: 11/11 cases remain `UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT`; exact-date official daily ZIP/checksum availability is FALSE for 11/11. Evidence grades: 3 `SAME_DATE_CONTEXT_ONLY`, 2 `MONTH_CONTEXT_ONLY`, 6 `NO_MATCH`. Monthly archives/raw rows are verified, but this is not exact-date child/parent independent attribution.
- Consequence: exact-key quarantine coverage is necessary but not sufficient for G0 PASS because final metrics under this quarantine manifest have not been run. No candidate build/backtest authorized by this checkpoint. G0 stays `BLOCKED_GLOBAL`; all 11 relationship blockers remain OPEN; no root cause, source selection or closure.
- Amended report: `evidence/source_adjudication/CP0040_Aggregation_Relationship_Hold_Decision_HI.md` (rulebook clause crosswalk appended).
- Next bounded action: preserve this HOLD and decide, under the frozen research workflow, whether to run a separately labelled quarantine-sensitivity diagnostic using the exact current manifest after required strategy/research scope is frozen; do not change source data or promote a candidate.


## CP-0040 quarantine sensitivity scope lock — 2026-10-16

- Published `evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Scope_Lock_HI.md` (commit `116b6693d48d8d58da3104294559418e2adb81c1`).
- Locked next experiment to one frozen comparator only: `MTF_BREAKOUT_4H_D1`, explicitly as a consumed diagnostic comparator, not a selected/promoted strategy. No parameter tuning or strategy-universe expansion.
- Planned comparison: baseline source policy versus current exact-key quarantine manifest (1,427 keys; SHA-256 `e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a`), using exact `(interval, open_time_ms)` matching only; report signal/input impact and metric deltas if baseline inputs are reproducible.
- Implementation guard: a separate diagnostic path must not weaken or override the production CP-0026 gate. If baseline inputs/metrics cannot be reproduced from committed evidence and verified cache without repeating acquisition, stop with `BLOCKED_INPUTS_NOT_REPRODUCIBLE`; do not invent comparisons.
- No diagnostic implementation/execution yet; no production candidate build/backtest. G0 remains `BLOCKED_GLOBAL`; all 11 relationship blockers remain open; strategy promotion and live actions remain blocked.


## CP-0040 quarantine-sensitivity baseline verification — 2026-10-16

- **Checkpoint ID:** `CP0040-QS-BASELINE-VERIFIED-20261016-01`
- **Decision:** `BASELINE_REPRODUCIBLE` from already existing, previously verified project evidence. This decision certifies the historical baseline inputs/results and their hashes; it does not claim the inputs are already present in the current GitHub Actions workspace or that the quarantine-sensitivity diagnostic has run.
- **Runner preflight:** Actions run [38890325530](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38890325530) completed `success` against commit `b7204d3bab674a6d68e3690f22b98b424c8a0d39`; 11/11 runner checks passed, task exit code 0, no market-data network request/download, candidate build, backtest, or strategy promotion. Artifact ID `12041381968`; ZIP SHA-256 `239123393358d581783057f45d8398f67be2f1b42999b2be8458b51f63c6b7ce`; ZIP integrity check PASS. Child-summary SHA-256 `7a695e9350f8e2feff529e86532488ddf1b9459e656b8793c623793e56d0165e`.
- **Restored cache evidence:** monthly archive cache contains 765 ZIPs (83,576,856 bytes); daily-reference cache contains 240 ZIPs and 240 checksum sidecars (922,669 bytes of ZIPs). The Actions cache restore is verified. Cache presence by itself is not treated as baseline reproducibility.
- **Existing historical input bundle:** `AISTS-20261013T133241Z-1-001.zip`, 192,946,548 bytes, SHA-256 `7a75a0f030886980b03db92bd8182c0274d1f64ff805f3975445a3f5325c52de`; ZIP integrity PASS; 1,338 members. This is the already-existing project evidence bundle, inspected read-only; it was not newly acquired.
- **Baseline input manifest:** `AISTS/market_data/binance_spot/BTCUSDT/reports/cp0026_research_candidate_manifest.json`; SHA-256 `baf72b07d2dd9e970ada0dc18eece57cab066a4a375b62e628938dba3fb7b6de`. The manifest records a source-selection policy tied to the existing monthly-source checksum evidence and daily-reference archive evidence; raw archives remain immutable and gaps are recorded, not filled.
- **Frozen comparator inputs validated against that manifest and the original CP-0031 input-quality rows:**
  - 4h: 19,975 rows; SHA-256 `989a4c2023a28b991455b9bb4149dd0a0a56e6435b34f805f56de5e888d907e1`; 8 gap events / 16 estimated missing bars, none filled.
  - 1d: 3,332 rows; SHA-256 `dc9a4cb53818ed6ffed10825989cb621c0ec4306c316b15fa8136010601fb76b`; no gap events recorded in that candidate.
  - 1mo: 110 manifest rows; 109 used after excluding one partial month; SHA-256 `2fb1005954d2dab96fe1c848a06bd7c5044547a531f208f81c630bea5866f1a0`; derived from the candidate 1d series.
- **Original baseline output bundle:** `AISTS_CP0031_Offline_Replay_Risk_Stress_Bundle.zip`; SHA-256 `e6998e59cd50683a3f3b92f1bd9afee0c6bbb44714d87893b33d33e4e83936f`; ZIP integrity PASS; all seven member hashes match the existing complete internal member manifest. Original `cp0031_summary.json` SHA-256 `c133ccd820c3b3bd46f69f316f171bd1d1707907ea71150b8dc7644bb30a8dd3`; input-quality CSV SHA-256 `33db145e6f8a3d486d89d714c485ba740eb6fff98415d7f4bd257d4879b87364`; original CP-0031 result bundle contains 180 stress-result rows and 164 trade-log rows.
- **Engine/rule identity evidence:** existing frozen engine file `AISTS_CP0031_Research_Engine_R1.py` SHA-256 `6b92b0956522ad6e6a7bdcaa364ee677c97b8926e3705d6250866c17cc70ceec`; its candidate-rule fingerprint matches the original protocol `8e499d4d230dbb6dc7e1aa9d18ba1e9408a003eb7589a091b0f3c0b5867e75dc`. Comparator remains the single locked `MTF_BREAKOUT_4H_D1`, not an approved/promoted strategy.
- **Pre-existing baseline assumptions and recorded outcomes (not recomputed in this checkpoint):** 10,000 USDT initial capital; baseline trade-log scenario uses 25% allocation, 10 bps fee per side and 5 bps additional slippage per side. TRAIN ends before 2023-01-01 UTC; DEVELOPMENT_CHECK is 2023-01-01 through 2024-12-31 UTC; 2025-01-01 onward is consumed diagnostic, not pristine OOS. `MTF_BREAKOUT_4H_D1` recorded TRAIN return +81.993135%, development-check +24.343646%, and consumed diagnostic return -1.384621% (24 round trips; profit factor 0.846407; max intrabar drawdown proxy -5.297173%). These are audited pre-existing figures, not new sensitivity results.
- **Execution caveat:** the current GitHub Actions cache holds raw archive caches, while the three candidate inputs, exact CP-0026 manifest, frozen CP-0031 engine and original CP-0031 result bundle were validated from the existing project Library bundle. They are not yet staged as a dedicated immutable baseline snapshot in the GitHub runner workspace. The sensitivity diagnostic has **not** been implemented or run.
- **Open blockers/gates:** the exact-key manifest remains 1,427 rows with declared SHA-256 `e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a`; all 11 residual aggregation relationship blockers remain open. G0 remains `BLOCKED_GLOBAL`. No G0 PASS, production candidate build, gate bypass, strategy promotion, live signing, public broadcast, or Binance order is authorised.
- **Next exact step:** create a separately labelled, evidence-only immutable baseline snapshot from the already-verified CP-0031 artifacts (do not rebuild or alter candidates), including the 4h/1d/1mo candidate files, CP-0026 manifest, source-engine fingerprint and original baseline-output manifest. Verify every staged byte/hash against the existing verified bundle, then implement only the scope-locked isolated sensitivity diagnostic with exact-key quarantine. Do not run a comparison until staging integrity and the same-engine/assumptions check pass.


## CP-0040 baseline snapshot evidence packaging — 2026-10-16

- **Checkpoint ID:** `CP0040-QS-BASELINE-SNAPSHOT-20261016-01`.
- **Local snapshot package:** `AISTS_CP0040_Baseline_Snapshot_20261016.zip`; 1,884,382 bytes; SHA-256 `1e5f528d1c09fb8b598e75f5c08b23530f0073882553cb272558aa89b047981f`; ZIP integrity PASS; 22 members. Embedded `SNAPSHOT_MANIFEST.json` SHA-256 `30099220a75dedc8e0cde3d52d55e3b96f3de45f35cbdf3bb4c3d3859c5b56d3`. Every packaged file's byte count and SHA-256 were rechecked against the embedded manifest.
- **Source bundle verification:** `AISTS-20261013T133241Z-1-001.zip`, 192,946,548 bytes, SHA-256 `7a75a0f030886980b03db92bd8182c0274d1f64ff805f3975445a3f5325c52de`; ZIP integrity PASS; 1,338 members. The original source bundle was read-only.
- **Exact candidate bytes preserved:** 4h (19,975 rows, SHA-256 `989a4c2023a28b991455b9bb4149dd0a0a56e6435b34f805f56de5e888d907e1`), 1d (3,332 rows, SHA-256 `dc9a4cb53818ed6ffed10825989cb621c0ec4306c316b15fa8136010601fb76b`), 1mo (110 manifest rows, 109 usable after partial-month exclusion, SHA-256 `2fb1005954d2dab96fe1c848a06bd7c5044547a531f208f81c630bea5866f1a0`). All three compressed candidate-file hashes match both CP-0026 manifest and CP-0031 input-quality records.
- **Baseline engine/result bytes:** frozen `AISTS_CP0031_Research_Engine_R1.py` SHA-256 `6b92b0956522ad6e6a7bdcaa364ee677c97b8926e3705d6250866c17cc70ceec`; original result bundle SHA-256 `e6998e59cd50683a3f3b92b1fbd9afee0c6bbb44714d87893b33d33e4e83936f`; ZIP integrity PASS and all seven original result members match the complete internal member manifest.
- **Quarantine bytes preserved:** 1,427 manifest rows / 1,427 unique exact keys; SHA-256 `e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a`. Case classes: 14 acquisition economic conflicts, 10 acquisition monthly-only, 418 acquisition raw-field conflicts, 16 aggregation-bucket keys, 8 close-time-only, 452 daily-only, 457 monthly-only, and 52 shared economic conflicts. Non-row blocker ledger remains 11 rows, SHA-256 `f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36`.
- **GitHub metadata record:** `evidence/source_adjudication/CP0040_Baseline_Snapshot_Manifest.json` was committed and must be read as a checksum/provenance record, not as the binary package. Metadata commit: `29212ac5d522497bdfefc659b55da7c3798718bd`.
- **Explicit limitation:** the 1.88 MB ZIP exists as a validated artifact in this conversation's working environment; the binary has not been committed to GitHub and has not been staged in Actions. The available repository connector can commit text metadata but does not provide a direct local-file-to-GitHub binary upload operation. No signed temporary URL or credential was put into the public request history. The next execution prerequisite is a controlled binary handoff to the runner or another authorised staging surface, then verify the staged bytes against this manifest before running the diagnostic.
- **No research execution performed:** no new data acquisition, production candidate build, backtest, signal/position comparison, or quarantine sensitivity was run while making this package. The original CP-0031 metrics remain historic outputs only.
- **Gate remains unchanged:** G0 `BLOCKED_GLOBAL`; all 11 aggregation relationship blockers remain open; candidate promotion, live signing, broadcast, and Binance orders remain blocked.


## CP0040-QS-HANDOFF-CAPABILITY-AUDIT-20261016-01

- Date: 2026-10-16. Read-only inspection of the current GitHub connector, repository workflow, runner, and latest verified preflight artifact.
- Actions run `38890325530` has only artifact `12041381968`, size 7,997 bytes, SHA-256 `239123393358d581783057f45d8398f67be2f1b42999b2be8458b51f63c6b7ce`. It is preflight evidence, not the baseline snapshot. Run HEAD was `b7204d3bab674a6d68e3690f22b98b424c8a0d39`; later docs-only HEAD changes do not inherit that run's CI result.
- The validated local snapshot remains `AISTS_CP0040_Baseline_Snapshot_20261016.zip`, 1,884,382 bytes, SHA-256 `1e5f528d1c09fb8b598e75f5c08b23530f0073882553cb272558aa89b047981f`, 22 members. It has not been uploaded to the repository or staged in Actions.
- Capability audit: the available GitHub connector exposes text-file create/update, a blob API that requires the full caller-supplied UTF-8/base64 string, and workflow-artifact download/list operations. It does not expose a local-file upload, release-asset upload, artifact upload, or workflow-dispatch action. No local-file-to-blob transport was available in this turn.
- `.github/workflows/python-runner.yml` restores source caches, but the existing legacy acquisition path calls official `.CHECKSUM` URLs and can fetch missing/mismatched ZIPs. It is therefore not an acceptable way to claim a network-free, cache-only reconstruction under the frozen CP-0040 scope.
- Google Drive integration is disabled by admin. Dropbox integration is listed as available but is not installed/authorized; it was not used and no external share link was created.
- **Decision: `BLOCKED_BINARY_HANDOFF_UNAVAILABLE`.** No diagnostic, candidate build, backtest, new source acquisition, or strategy comparison was run. `requests/current.json` was not changed to trigger a run.
- **Gates unchanged:** CP-0040 comparator remains diagnostic-only; G0 `BLOCKED_GLOBAL`; all 11 non-row aggregation blockers remain open; no canonical source selection, candidate promotion, live signing, public broadcast, or Binance order placement.
- **Next prerequisite:** establish an authorised binary handoff that the Actions runner can read, or separately implement and verify a genuinely offline, hash-anchored cache reconstruction. Before the sensitivity calculation, verify the staged/input bytes against the frozen CP-0040 snapshot manifest.



## CP-0040 baseline reconstruction audit run 38895499283

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38895499283; task status PASS_BASELINE_INPUTS_RECONSTRUCTED; runner commit 8200077aca3a375c91d6b9f620f8338cbba10eee.
- Scope is temporary cache-only reconstruction of the frozen CP-0031 candidate input content; network/acquisition count=0; production candidate build=False; backtest=False.
- Monthly archives used=220; daily reference archives used=80; official daily sidecars verified=80.
- 1d reconstructed decompressed SHA-256 8cefa74df159591f87cdcfcd203ed53d35562fea041332645c1f478b53a24556; frozen anchor 8cefa74df159591f87cdcfcd203ed53d35562fea041332645c1f478b53a24556; match=True.
- 1mo reconstructed decompressed SHA-256 09c4a052cd879cac035c6fdbe61e830947c4bc5f09d14017168dcc2af38f9278; frozen anchor 09c4a052cd879cac035c6fdbe61e830947c4bc5f09d14017168dcc2af38f9278; match=True.
- 4h reconstructed decompressed SHA-256 1c7377e3dc26c791133d2ea0bf0a8b46cbec4287f4dc37a6032c79044c4ed357; frozen anchor 1c7377e3dc26c791133d2ea0bf0a8b46cbec4287f4dc37a6032c79044c4ed357; match=True.
- Input content anchors reproduced. This is not a backtest, signal-impact calculation, canonical-source decision, or promotion approval.
- G0 remains BLOCKED_GLOBAL; all 11 non-row aggregation blockers remain open; canonical source remains NONE; live signing/broadcast/orders remain blocked.


## CP-0040 quarantine sensitivity audit run 38897836116

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38897836116; task status `PASS_QUARANTINE_SENSITIVITY_DIAGNOSTIC_COMPLETE`; runner commit 93bfcc8913467839160e394399f81d2b23657bf3.
- Frozen comparator: `MTF_BREAKOUT_4H_D1`; scope exact-key removal by (interval, open_time_ms) only; no row replacement, no market-data downloads.
- Baseline metric gate: PASS; production candidate build=False; strategy promotion=False.
- 4h: rows removed=6; rows retained=19969.
- 1d: rows removed=3; rows retained=3329.
- 1mo: rows removed=0; rows retained=110.
- CONSUMED_OOS_DIAGNOSTIC: baseline return=-1.3846214314251704%; quarantine return=-1.3846214314251704%.
- DEVELOPMENT_CHECK: baseline return=24.343646291056565%; quarantine return=24.343646291056565%.
- TRAIN: baseline return=81.99313544472133%; quarantine return=66.1013946162224%.
- G0 remains BLOCKED_GLOBAL; 11 aggregation relationship blockers remain open; canonical source remains NONE; live signing/broadcast/orders remain BLOCKED.


## CP-0040 aggregation monthly sidecar audit run 38900214067

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38900214067; status PASS_MONTHLY_SIDECARS_MATCH_CACHED_ARCHIVE_BYTES; runner commit 33dd389d09cb8107076dfe0bb806b34d8dfc5483.
- Official monthly .CHECKSUM text requests=14; verified=14; failed/unavailable=0. Monthly ZIP downloads=0; daily archive downloads=0; Binance market-data REST calls=0.
- This confirms sidecar-token/cache-ZIP hash linkage only; it does not adjudicate which interval is canonical.
- The 11 cross-interval aggregation blockers remain open; G0 BLOCKED_GLOBAL; canonical source NONE; no backtest or strategy promotion; live actions BLOCKED.


## CP-0040 official archive integrity conflict matrix run 38900802182

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38900802182; status PASS_OFFICIAL_ARCHIVE_INTEGRITY_CONFLICT_MATRIX_COMPLETE; runner commit 748b6f9feadc0fb0cfe4e6661707a259ddb07148.
- Source crosswalk: buckets=11; raw row links=78; monthly sidecars=14/14; daily archive records=16.
- Both monthly/daily archive sets authenticated=11/11; daily roll-up matched and frozen monthly mismatch remained=11/11.
- Interpretation: official archive-byte integrity confirmed but source authority unresolved; all 11 buckets remain open; G0 BLOCKED_GLOBAL; canonical source NONE. No ZIP downloads, repairs, backtest or promotion.


## CP-0040 candidate input relevance audit run 38901790221

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38901790221; status PASS_CANDIDATE_INPUT_RELEVANCE_REVIEW_COMPLETE_NOT_G0_APPROVAL; runner commit 57db5dabf4a1341b47ffc798107881d9d14eb65e.
- Frozen comparator MTF_BREAKOUT_4H_D1 direct intervals 4h/1d; open aggregation relationships with direct interval overlap=0/11.
- Exact-key quarantine impact: 4h removed=6; 1d removed=3; 1mo removed=0; TRAIN net-return delta pp=-15.89174082849894.
- This is input-relevance evidence, not source authority or G0 approval. All 11 relationship cases remain open; G0 BLOCKED_GLOBAL; canonical source NONE; production candidate build/backtest/promotional actions remain blocked.


## CP-0107 Shared-52 candidate input dependency audit run 38902949514

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38902949514; status PASS_SHARED52_CANDIDATE_INPUT_DEPENDENCY_MAP_COMPLETE_NOT_G0_APPROVAL; runner commit febdbc3ae2ec6b35f1261007b7537b2a5e683c90.
- Shared-52 rows=52; conflicts intersecting frozen MTF_BREAKOUT_4H_D1 direct inputs=4 (4h=2, 1d=2); remaining intervals=48. All 52 exact keys matched the CP-0040 quarantine manifest.
- Official correction package supplied no exact daily path for the four direct cases. Full-manifest sensitivity: TRAIN delta pp=-15.89174082849894; no 4-row causal attribution was run.
- This is dependency evidence, not source adjudication or G0 approval. All 52 cases remain open; the 11 relationship blockers remain open; G0 BLOCKED_GLOBAL; canonical source NONE.


## CP-0040 rulebook-bound eligibility decision run 38904743112

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38904743112; status PASS_RULEBOOK_BOUND_DECISION_GLOBAL_GATES_REMAIN_BLOCKED; runner commit ca5b237443b83da03ee2f24e99b649beccac9fcd.
- Frozen rulebook verified: 10,630 bytes, SHA-256 5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0, member confirmed in CP-0041 and CP-0046 packs.
- Candidate-specific quarantine criterion=PASS_QUARANTINE_BRANCH_FOR_THIS_FROZEN_DIAGNOSTIC_COMPARATOR_ONLY; direct exact keys removed=9/9; replacements=0. Global G0 remains BLOCKED_GLOBAL.
- G3=BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; TRAIN net-return delta pp=-15.89174082849894; G2 remains FAIL/NOT PROMOTED. CP-0026 builder stays fail-closed; no build or backtest.
- All 11 relationship blockers remain open; canonical source NONE; no cases closed; live signing, broadcast and orders BLOCKED.


## CP-0092 correction archive binary route probe run 38905894400

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38905894400; route status PASS_CORRECTION_ARCHIVE_BINARY_ACQUIRED_AND_VERIFIED; runner commit 4ccfb7f8a9311bf6cffcb9abae1fe19a1e00b262.
- Binary route: GitHub REST Git Blobs API with application/vnd.github.raw+json; bytes=6653240; Git blob SHA-1=90631298cf50ac2e1ee8372a087767b010d78a21; ZIP CRC=PASS.
- Exact target basename matches=0/16; daily ZIP+.CHECKSUM pairs acquired=0. Archive acquisition alone does not adjudicate source authority.
- 60 shared conflicts, 909 unmatched rows, 11 aggregation blockers remain open; G0 BLOCKED_GLOBAL; G2 all 23 candidates FAIL; G7 LIVE_BLOCKED. No canonical source selection or case closure.


## CP-0107 CP-0041 exact-date daily-reference acquisition and raw-row audit 38909366995

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38909366995; status PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED; checks 98/98 PASS.
- Exact scope: 16 queued official daily ZIPs + 16 .CHECKSUM files. The 14 associated monthly ZIPs were reused from cache and verified against the frozen CP-0041 subset; monthly ZIP downloads: 0.
- Union key rows 1992; shared 1982; exact raw pairs 1550; divergent pairs 432; daily-only 0; monthly-only 10.
- All unequal/missing rows remain OPEN_REVIEW_REQUIRED. Canonical source NONE, cases closed 0, no timestamp shifts/rounding/merge/replace/delete, no synthetic bars/backtest/promotion.
- CP-0041 package SHA-256 23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc; queue member SHA-256 b6660083860d5d90afc5d2661353ecf4c8f1aa2d355a9db99d6fc7a40e9b045d; rulebook SHA-256 5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0.


## CP-0093 daily-reference discrepancy triage 38910674953

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38910674953; status PASS_DAILY_REFERENCE_DISCREPANCY_TRIAGE_COMPLETE_SOURCE_AUTHORITY_OPEN; checks 14/14 PASS.
- Existing CP-0107 acquisition run 38909366995: 16/16 daily ZIP/.CHECKSUM pairs and 14/14 monthly cache archives revalidated; this triage used existing artifacts, no downloads.
- Raw comparison: 1,992 union rows; shared 1,982; exact 1,550; divergent 432; economic-field divergent 14; monthly-only 10; daily-only 0.
- All 16 target cases remain open; canonical source NONE; cases closed 0. Global G0 BLOCKED_GLOBAL; G2 current 23 candidates FAIL; G7 LIVE_BLOCKED. No market data edits, synthetic candles, backtest or promotion.


## CP-0094 exact-key acquisition quarantine coverage 38911689643

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38911689643; status PASS_24_ACQUISITION_KEYS_CONFIRMED_QUARANTINED_SOURCE_AUTHORITY_OPEN; checks 15/15 PASS.
- Frozen CP-0040 manifest: 1427 unique keys; CP-0093 inputs remained hash-verified. Exact-key quarantine coverage: economic conflicts 14/14; missing daily-grid keys 10/10.
- This verifies conservative quarantine coverage only. Source authority NONE; all 24 cases remain open; 11 non-row aggregation blockers remain open; global G0 BLOCKED_GLOBAL; G2 current 23 candidates FAIL; G7 LIVE_BLOCKED. No source selection, raw data change, candidate build or backtest.


## CP-0095 official correction target mapping 38912641513

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38912641513; status PASS_OFFICIAL_CORRECTION_CSV_HAS_NO_EXACT_PATHS_FOR_16_TARGETS_SOURCE_AUTHORITY_OPEN; checks 9/9 PASS.
- Reused verified correction ZIP SHA-256 1404dbfb3d62534b2576a6c0c046826fe652f895b9bebfe4c13df58bc8cf6240; correction CSV rows=73234. No new download.
- Exact correction paths for 16 daily targets=0/16; basename matches=0/16. Correction bundle provides no mapping for this target set.
- Source authority remains UNDETERMINED; no case closed; 60 source conflicts, 909 unmatched rows and 11 aggregation blockers remain open; G0 BLOCKED_GLOBAL; G2 current 23 candidates FAIL; G7 LIVE_BLOCKED.


## CP-0096 correction checksum crosswalk 38913040361

- GitHub Actions run https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38913040361; status PASS_CHECKSUM_CROSSWALK_NO_ARCHIVE_HASH_HITS_SOURCE_AUTHORITY_OPEN; checks 11/11 PASS.
- Compared every correction CSV Original/New SHA-256 field against 16 verified daily ZIP hashes and 14 verified monthly ZIP hashes. Daily hits=0/16; monthly hits=0/14. No new download.
- Source authority remains UNDETERMINED; no case closed; 60 source conflicts, 909 unmatched rows and 11 aggregation blockers remain open; G0 BLOCKED_GLOBAL; G2 current 23 candidates FAIL; G7 LIVE_BLOCKED.


## CP-0097 official Binance correction-route closure

- Official Binance Public Data README at `binance/binance-public-data:master/README.md` preserved byte-identically at `evidence/source_adjudication/CP0097_Official_Binance_Public_Data_README_master.md`; official and preserved Git blob SHA-1 both `e01e34a0b0cd91d62386a5a237190a3167138bae`. The documented exhaustive Updates table lists one kline correction bundle: `2022-08-08_kline_updates.zip`; the other listed update is for aggregate trades.
- CP-0095 exact path/basename mapping for 16 daily targets: 0/16 and 0/16. CP-0096 correction Original/New SHA-256 crosswalk hits: daily 0/16, monthly 0/14. No new archive download.
- Decision: close only this official correction-search route for the frozen target set. This does not adjudicate daily versus monthly candle values. Canonical source NONE; cases closed 0; 60 source conflicts, 909 unmatched rows quarantined and 11 non-row aggregation blockers remain open.
- Global gates unchanged: G0 `BLOCKED_GLOBAL`; G2 current 23 candidates `FAIL`; G7 `LIVE_BLOCKED`. No raw data mutation, worklist mutation, candidate build, backtest, or strategy promotion.
- CP-0097 report: `e0d19fcbdfd288148a3a45e8a4e4feb0da06dddd`; current pointer: `084a401073c573fb80d005d6982cb955c737b841`; official README snapshot: `e01e34a0b0cd91d62386a5a237190a3167138bae`.


## CP-0108 residual aggregation blocker evidence-boundary decision — 2026-10-16

- **Checkpoint:** `CP-0108`; status `BLOCKED_NO_NEW_AUTHORITY_EVIDENCE_FOR_11_RESIDUAL_AGGREGATION_BUCKETS`. This is an evidence-only decision from the committed source set, not a new data run, backtest, CI result, or strategy gate.
- **Inspection baseline:** `main` most-recent commit returned before checkpoint writes: `9cc1e532df745a5a04de91ea0d7a7d185e1d4490`. Continuity file blob read immediately before append: `5770fcf0a2d96f4e03d7c745af75413cfcab0e48`.
- **Aggregation evidence reused, not rebuilt:** frozen blocker ledger 11 rows (blob `d3fca23bac424fa8c8b187434e8c63e8d188a0e1`); CP-0107 bucket snapshot 11 rows (blob `6e32188472ab45b43e1b90fe138399818c937277`); comparison 11 rows (blob `5dae35e8d420b3997be90cabc263825e98b8b918`); row evidence 78 rows (blob `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9`); summary 12/12 diagnostic checks PASS (blob `08221ec6baab7257b61f803fe78064cc26717ef5`).
- **Findings:** daily exact-key child-parent rollup matches 11/11; monthly mismatches 11/11; volume sum numeric representation check matches 10/11. CP-0107 explicitly withholds source-authority attribution. AGG-10 values `279.26867100000004` and `279.26867100` were not normalized.
- **Official-source scope reconciliation:** CP-0097's route closure remains scoped to its frozen set (report blob `e0d19fcbdfd288148a3a45e8a4e4feb0da06dddd`, pointer blob `084a401073c573fb80d005d6982cb955c737b841`). The preserved official README blob is `e01e34a0b0cd91d62386a5a237190a3167138bae`; current public README check shows only the 2022-08-08 kline-correction entry in its Updates table. Do not generalize CP-0097 to every source conflict.
- **Separate shared-52 crosswalk:** blob `718c2ac990d9fb5d9c731fdda4fc92657d375ad2`; 52 rows, 33 exact official daily paths, 33 replacement SHA-256 matches. All 52 remain `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION`, canonical source `NONE`, and not closed. No UTC-date overlap exists between those 52 rows and the exact 11 aggregation bucket dates; this crosswalk does not close these 11 cases.
- **Decision:** all 11 aggregation blockers remain open; no canonical source selected; 0 source cases closed. Required missing evidence is authoritative archive-version/provenance or another allowed independently verifiable primary-source record applicable to the exact child/parent archive bytes and frozen UTC keys.
- **No actions beyond evidence persistence:** no archive download, raw data mutation, timestamp adjustment, synthetic candles, workflow dispatch, candidate build, backtest, strategy promotion, signing, public broadcast, or Binance order.
- **Gates unchanged:** G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; 60 shared conflicts; 909 unmatched rows quarantined; 11 non-row aggregation blockers remain unresolved.
- **Report:** `evidence/source_adjudication/CP0108_Residual_Aggregation_Blocker_Decision_HI.md` (blob SHA-1 `e14f5840b476b1a87f865274c998b6850049a2ca`).
- **Current pointer:** `evidence/source_adjudication/CP0108_Residual_Aggregation_Blocker_Decision_Current.json` (blob SHA-1 `d3582268bfbc511dc59fb7cd297e18095b251899`).
- **Next bounded step:** search only for genuinely new, exact-scope official provenance/version evidence covering the frozen 11 child/parent archive keys. Skip the already-exhausted correction-bundle route and re-use CP-0107 artifacts. If no distinct applicable evidence is found, keep all 11 blockers open.


## CP-0109 official correction-route linkage to all 11 aggregation buckets — 2026-10-16

- **Checkpoint:** `CP-0109`; status `BLOCKED_OFFICIAL_CORRECTION_ROUTE_EXHAUSTED_FOR_11_AGGREGATION_BUCKETS_SOURCE_AUTHORITY_OPEN`. Evidence-only linkage audit. No repeated correction search, archive download, data run, backtest, or gate pass.
- **Exact daily target-set join:** CP-0107 RowEvidence blob `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9` has 16 unique daily archive filenames. CP-0095 matrix blob `53f98b0c68abcd6bb62d31ddd73415fa62d5d3ba` has the same 16 names and the same `source_archive_sha256` / `verified_daily_zip_sha256` mapping for 16/16. No missing, extra, or hash-mismatched name.
- **Exact monthly target-set join:** CP-0107 has 14 unique monthly archive filenames. CP-0096 crosswalk blob `7e7b00dc9f38897349682dce0807b0e599ee180f` has the same 14 names and the same per-filename archive SHA-256 mapping for 14/14. CP-0096 daily targets also match CP-0107's 16 daily filename/hash pairs.
- **Correction-route result for these exact 30 archive files:** CP-0095 recorded exact correction paths 0/16 and basename matches 0/16. CP-0096 parsed the 73,234-row correction CSV and matched neither Original nor New checksum against any of the 16 daily and 14 monthly archive SHA-256 values (daily hits 0/16; monthly hits 0/14). CP-0097's reviewed README snapshot blob is `e01e34a0b0cd91d62386a5a237190a3167138bae` and documents one kline correction bundle, `2022-08-08_kline_updates.zip`.
- **Decision:** CP-0097's exhausted correction route is directly applicable to the exact archive set behind all 11 CP-0107 aggregation buckets, verified by filename-set and per-filename SHA-256 equality. Do not rerun that same correction bundle against the unchanged target set. This is not source-authority attribution: daily rollups match for 11/11 buckets but monthly mismatches remain 11/11; canonical source NONE and cases closed 0.
- **Gates and ledger unchanged:** G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; shared conflicts 60; unmatched rows quarantined 909; aggregation blockers 11 open.
- **No mutation or execution:** no archive download, raw source edits, timestamp shifts/rounding, synthetic candles, workflow dispatch, candidate build, backtest, strategy promotion, live signing, public broadcast, or Binance orders.
- **Report:** `evidence/source_adjudication/CP0109_Official_Correction_Route_Linkage_To_11_Aggregation_Buckets_HI.md`, Git blob SHA-1 `0a9ec9f025976a87885776ae3c61c9fcc6c1a0aa`.
- **Current pointer:** `evidence/source_adjudication/CP0109_Official_Correction_Route_Linkage_Current.json`, expected report blob linkage `0a9ec9f025976a87885776ae3c61c9fcc6c1a0aa`.
- **Next bounded step:** pursue only a distinct, independently verifiable source-authority or archive-version provenance source permitted by the frozen rulebook for the exact child/parent archive bytes and UTC keys. Do not repeat the exhausted correction bundle or the daily rollup arithmetic. If no applicable authority evidence exists, keep all 11 blockers open.


## CP-0110 official daily-trades checksum-sidecar preflight — 2026-10-16

- **Checkpoint result:** `PASS_ALL_7_OFFICIAL_TRADE_SIDECARS_AVAILABLE`. This was a metadata-only preflight, not an archive download or source-adjudication pass.
- **Workflow:** [GitHub Actions run 38922212821](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38922212821), executed commit `0bf724d4b8ee2274295c186a6cd94ce00bbfdc81`. Workflow conclusion `success`; runner `PASS`, 11/11 checks PASS.
- **Target UTC dates:** 2017-12-04, 2018-02-05, 2018-02-07, 2018-03-04, 2018-03-20, 2018-06-20, 2018-09-05. All seven fixed Binance Spot daily-trades `.CHECKSUM` sidecar endpoints returned structurally valid sidecars from HTTPS `data.binance.vision`.
- **Artifact:** [run artifact 12054562639](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38922212821/artifacts/12054562639), archive SHA-256 `78c9323ca221e2956db6d7c6a6626fe31a828c90797a3e6d51ccaab87034ff59`, retention 7 days. Child summary SHA-256 `31f12fdea950949ab5ecb6645d018e3bd55d71ec14f006b50462cc592e387100`. Per-sidecar tokens and body hashes are preserved in this artifact; they were not individually emitted in the workflow log.
- **Report:** `evidence/source_adjudication/CP0110_Official_Daily_Trades_Sidecar_Preflight_HI.md`, Git blob SHA-1 `a1803161fb26ab9ee6dc4a1b01e424a19c8f4a9d`.
- **Current pointer:** `evidence/source_adjudication/CP0110_Official_Daily_Trades_Sidecar_Preflight_Current.json`. Its expected report Git blob SHA-1 is `a1803161fb26ab9ee6dc4a1b01e424a19c8f4a9d`.
- **Interpretation boundary:** a valid `.CHECKSUM` tells us the expected ZIP digest, not that the ZIP has been downloaded, complete, or authoritative for kline rows. No trade ZIP was downloaded here. Binance's open historical-provenance issue #504 asks whether previous ZIP versions and replacement timestamps are retained; no maintainer confirmation is recorded in this checkpoint. Issue #316 describes incomplete BTCUSDT Spot trade data on 2018-02-08, a separate date that reinforces the need for complete-day validation but does not demonstrate a gap on these seven dates.
- **Non-actions:** market-data REST API calls 0; trade ZIP downloads 0; source bytes modified false; timestamp shift/rounding false; synthetic candles false; candidate build/backtest/strategy promotion not performed; source cases closed 0; canonical source NONE.
- **Gates and unresolved state remain:** G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; 60 shared conflicts unresolved; 909 unmatched rows quarantined; all 11 aggregation blockers open.
- **Next bounded action:** use the seven sidecar digests to verify only the corresponding daily-trades ZIPs, then inspect ZIP integrity, exact CSV schema, full UTC-day time bounds, first/last trade IDs and completeness anomalies. Do not reconstruct candles for a date if coverage is uncertain. Even a successful trade-derived reconstruction is diagnostic evidence until it satisfies the frozen CP-0040 source-authority requirements; it does not automatically close cases or promote a strategy.


## CP-0111 official daily Spot-trades archive integrity audit — 2026-10-16

- **Checkpoint result:** `PASS_7_ARCHIVES_INTEGRITY_AND_BASIC_COVERAGE`. The successful workflow run verified the seven fixed daily-trades ZIPs against their sidecar SHA-256 tokens, tested ZIP CRC, expected member name, seven-column Spot-trades CSV schema, and in-day UTC timestamps.
- **Workflow:** [GitHub Actions run 38937879841](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38937879841), commit `fe075f94beb551dcc382dca3b9fd681ae6181b7b`; conclusion `success`; runner `PASS`, 11/11 checks PASS.
- **Child summary SHA-256:** `6a34e04f8207356020cf9fa09731c060d9e8f92e9ab4cf2ccc85a3bdc7373728`.
- **Artifact:** [12061158412](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38937879841/artifacts/12061158412); artifact ZIP SHA-256 `2240ec7ffb3dffdbf9b7c41f6210ab5abb11f64cf68e8e81b26ee7e469434ef2`, retention 7 days. It contains the per-date archive hashes, byte counts, row counts, first/last trade IDs and times, schema/CRC results and coverage diagnostics.
- **Report:** `evidence/source_adjudication/CP0111_Official_Daily_Trade_Archive_Integrity_HI.md`, Git blob SHA-1 `0c22d8c17c6941a70dc31fdbae0ff79590c04836`.
- **Current pointer:** `evidence/source_adjudication/CP0111_Official_Daily_Trade_Archive_Integrity_Current.json`; expected report Git blob SHA-1 `0c22d8c17c6941a70dc31fdbae0ff79590c04836`.
- **Scope:** 7/7 archive SHA/sidecar matches, ZIP CRC and expected 7-column schema passed; all parsed timestamps were inside the named UTC date; no basic edge-gap/ID-sequence/timestamp-order review flags were raised by the configured screen.
- **Important limitation:** the configured coverage checks are anomaly screens, not a maintainer-backed completeness guarantee or proof that trade archives reproduce canonical historical klines. No kline reconstruction was run in CP-0111, and no authority is assigned from this result.
- **Non-actions:** Binance market-data REST API calls 0; exchange credentials 0; raw kline archives modified false; no timestamp change or synthetic candles; candidate build/backtest/strategy promotion not performed; source cases closed 0.
- **Gates and blockers unchanged:** G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; 60 shared conflicts unresolved; 909 unmatched rows quarantined; 11 aggregation blockers remain open; canonical source NONE.
- **Next bounded step:** reconstruct OHLCV, quote volume, trade count and taker-buy metrics from the checksum-verified trade archives for only the unique exact child/parent candle keys referenced by the 11 frozen CP-0107 buckets. Compare those derived values with the already committed daily/monthly raw rows. Treat this only as an independent diagnostic; the CP-0040 source-authority standard still controls all source disposition, and no bucket auto-closes.


## CP-0112 trade-derived reconstruction of the 11 residual aggregation buckets — 2026-10-16

- **Checkpoint:** `CP-0112`; task status `PASS_TRADE_DERIVED_RECONSTRUCTION_COMPLETE_SOURCE_AUTHORITY_OPEN`. Reconstruction completed; source authority remains open.
- **Workflow:** [GitHub Actions run 38938706562](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38938706562), executed commit `60e8de9cd48412ff77f48dba37cef759fe5040a1`; conclusion `success`; runner `PASS`, 11/11 checks; all 42 Python source files passed syntax parsing. Combined status query returned no status entries, so no separate CI status is inferred beyond the workflow/job success.
- **Artifact:** [12061434560](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38938706562/artifacts/12061434560), artifact ZIP SHA-256 `526b9fe75c96c7e874d81009713a99a7445fbfd03337c98463917d953db16411`, retention 7 days. Child summary SHA-256 `bed68b20f220d1618b4ffadf685a75b30ae8e21b088dfd854cd47ce74eaee96b`.
- **Frozen inputs:** CP-0107 RowEvidence blob SHA-1 `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9` (78 records); bucket snapshot blob SHA-1 `6e32188472ab45b43e1b90fe138399818c937277` (11 cases); CP-0040 frozen rulebook SHA-256 verified as `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
- **Seven current official trade archives:** downloaded only the seven exact BTCUSDT Spot daily-trades ZIPs named in CP-0110, verified each downloaded ZIP SHA-256 against its current official `.CHECKSUM`, then streamed trades to reconstruct exact target keys. Total parsed rows `2,022,142`; invalid rows 0; rows outside named UTC day 0; trade-ID gaps/duplicates/decreases and timestamp decreases all 0 for each target file. ZIPs remained in temporary working storage and were not committed as raw project inputs.
- **Key finding:** 35 unique target candle bars reconstructed across the child/parent intervals. Daily kline row metrics match the trade-derived values exactly for `35/35` bars and `315/315` of the nine compared metric fields. Monthly rows match `21/35` unique bars and `218/315` compared fields. Every independently reconstructed parent candle matches the rollup of its reconstructed child candles for `11/11` buckets. Open/close-boundary issues: 0.
- **Bucket comparison nuance:** bucket-local matching counts overlap when a candle participates in more than one bucket; only the deduplicated unique target bar denominator (35) is suitable for aggregate daily/monthly counts. Monthly mismatches remain in the exact fields recorded in the CP-0112 report and comparison CSV.
- **Report:** `evidence/source_adjudication/CP0112_TradeDerived_Aggregation_Reconstruction_HI.md`, Git blob SHA-1 `7b9e05b9796eb61677537d38460e5f8cd77c4bc8`.
- **Current JSON pointer:** `evidence/source_adjudication/CP0112_TradeDerived_Aggregation_Reconstruction_Current.json`, report blob SHA-1 linkage `7b9e05b9796eb61677537d38460e5f8cd77c4bc8`.
- **Output SHA-256:** `CP0112_Trade_Archive_Integrity.csv` = `5435a128c59e5917ba715ff6b8c4f1d979e3692cad974a7a3be09e6a77ab7a46`; `CP0112_TradeDerived_Bar_Comparison.csv` = `5e8c7915dacf813af7afce885287d5a017c74da52bbe70733b32ccab3ca17ac4`; `CP0112_Aggregation_Bucket_TradeReconstruction.csv` = `59929ca5de8a96b019981768f6eb6df12ea1e2cb2928d77ab68935557268a8d0`; run's comparison report = `6c7955695f68ebd827a826ff58803c6b762bd598dfc41339088e4131c2e5ec3c`.
- **Evidence-bound disposition:** classify daily values as `CORROBORATED_BY_VERIFIED_TRADE_ARCHIVE` for these exact 35 target keys, and monthly divergences as `CONFLICT_WITH_TRADE_DERIVED_RECONSTRUCTION` for the specific fields listed in the report. This is not a global canonical-source selection. Historical ZIP version provenance remains `OPEN_NOT_ESTABLISHED`; cases remain open pending the frozen CP-0040 authority standard.
- **Gates and blockers unchanged:** G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; 60 shared conflicts unresolved; 909 unmatched rows quarantined; all 11 aggregation blockers remain open; canonical source NONE; cases closed 0.
- **Non-actions:** no Binance market-data REST API calls, no exchange credentials, no source kline edits/replacements, no timestamp shifts/rounding, no synthetic candle written into research inputs, no candidate build/backtest/promotion, no live signing/broadcast/orders.
- **Next bounded action:** review the 14 unique monthly-mismatching bars against the exact preserved monthly JSON, trade-derived values, daily rows and their archive/sidecar identities. Decide whether CP-0040 allows field-level disposition from the three-way evidence or still requires independent historical-version/provenance evidence. Do not close cases automatically.


## CP-0113 field-level trade corroboration and monthly conflict crosswalk — 2026-10-16

- **Checkpoint:** `CP-0113`; status `PASS_FIELD_LEVEL_CROSSWALK_SOURCE_AUTHORITY_OPEN`. This is an evidence-only source-identity and field-level crosswalk; it does not select a canonical source or close any case.
- **Workflow:** [GitHub Actions run 38939841877](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38939841877), executed commit `6af3b705bb0344e4b20e18ec90f533c104b1c6bd`; workflow conclusion `success`; runner `PASS`, 11/11 checks.
- **Artifact:** [12062382111](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38939841877/artifacts/12062382111), ZIP SHA-256 `88213c8b1f9e753a289c3a0cf10702e23d6bf3b76db1f9ab8146b1a31043a8f7`, 23,043 bytes, 7-day retention. Child summary SHA-256 `b20e30d6a631ca2ac6e9caf5c30c3abd9353d865189e5bf55b782b393992e588`.
- **Frozen rulebook:** SHA-256 checked against `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`; CP-0112 pointer/report linkage also passed.
- **Source archive integrity:** daily kline target manifest 16/16 passes official HTTP, ZIP CRC, `.CHECKSUM` token-to-archive SHA-256 and exact row-evidence archive-hash mapping. Monthly source set 14/14 passes HTTP, ZIP CRC, exact checksum filename, official token versus cached ZIP hash and row-evidence archive-hash mapping. The current sidecars prove these exact bytes, not the historical version timeline.
- **Unique-row reconciliation:** CP-0107 RowEvidence 78 contextual records deduplicated to 35 unique daily and 35 unique monthly candle keys. Four duplicate daily and four duplicate monthly contexts were consistent; conflicting duplicate values 0; missing rows daily/monthly 0/0; exact raw opening/closing time boundaries had 0 issues.
- **Trade corroboration carried forward from CP-0112:** 35/35 daily bars and 315/315 daily economic metric fields match the current checksum-verified trade-derived reconstruction; trade-derived child-parent rollup checks were 11/11. Monthly source exactly matches 21/35 unique bars and 218/315 metric fields.
- **Field-level difference result:** 14 unique monthly-divergent keys and 97 differing economic metric fields were reproduced against the exact frozen raw row evidence. Per-key mismatching field lists and both archive filenames/hashes are in the report and workflow artifact.
- **Report:** `evidence/source_adjudication/CP0113_FieldLevel_Trade_Corroboration_Disposition_HI.md`, Git blob SHA-1 `50973223cbb94eb1889f946d51369f7e7c5c63a5`.
- **Current pointer:** `evidence/source_adjudication/CP0113_FieldLevel_Trade_Corroboration_Disposition_Current.json`, report Git blob SHA-1 linkage `50973223cbb94eb1889f946d51369f7e7c5c63a5`.
- **Artifact output hashes:** crosswalk CSV (20,132 bytes) `1e5ba8e8dc380eef4cc597102ed77ccc1ce768989c076504b78bc43ae298ec80`; monthly mismatch detail CSV (27,913 bytes) `221e456e5eaee33f3e49e112efa177b411cbb8702a3d048c57a36f12cca1ad6e`; run report (5,035 bytes) `3d9382c6fbaeae57a6d71e229df4dcf72cac377a83f13e4da6f21c5e9b04b557`. CSVs are retained in the linked workflow artifact.
- **Disposition:** for these exact 35 candle keys, daily values are `CORROBORATED_BY_CURRENT_CHECKSUM_VERIFIED_TRADE_ARCHIVE`; monthly differences are `FIELD_LEVEL_CONFLICT_WITH_TRADE_DERIVED_RECONSTRUCTION` on the 14 keys/97 fields. This is bounded current-byte corroboration, not global canonical-source authority. CP-0040 specifies no mechanical daily-over-monthly precedence and requires signal-affecting unresolved items to remain unresolved unless adjudicated or fully quarantined under an accepted conservative policy.
- **Gates and blockers unchanged:** G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; 60 shared conflicts unresolved; 909 unmatched rows quarantined; all 11 aggregation blockers open; canonical source `NONE`; source cases closed 0; historical archive-version provenance `OPEN_NOT_ESTABLISHED`.
- **Non-actions:** no raw archive edits/replacements, no timestamp shift/rounding, no synthetic research candle, no Binance market-data REST call, no exchange credentials, no candidate build/backtest/strategy promotion, no signing/broadcast/orders.
- **Next bounded action:** crosswalk these 14 keys against the existing CP-0040 G0 candidate-input/quarantine dependency map. Confirm whether any key still influences a current candidate or whether all relevant fields are fully quarantined under the accepted conservative policy. Do not change source bytes or invent a new source-precedence rule.


## CP-0114 exact-key quarantine overlap and G0 impact audit — 2026-10-16

- **Checkpoint:** `CP-0114`; status `PASS_MANIFEST_OVERLAP_AUDIT_G0_STILL_BLOCKED`. This confirms manifest overlap and quarantine-application scope; it is not a G0 pass.
- **Workflow:** [GitHub Actions run 38940457832](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38940457832), commit `95d01d16e36505a4b207775b16394d3bddcdcbac`; workflow conclusion `success`; runner `PASS`, 11/11 checks PASS.
- **Artifact:** [12062208828](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38940457832/artifacts/12062208828), 9,906 bytes, ZIP SHA-256 `45fe350b7770f69276f2eb18ba2f70d6497ec2df19e2143872964f7046467434`; retention 7 days. Child summary SHA-256 `1f33e12681a4be4f0280ac27a25f112714dd1e5555ca253fcb6ad58e39e3d1f0`.
- **Inputs verified:** CP-0107 row evidence 78 contextual rows (blob `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9`); exact-key manifest 1,427 unique keys (blob `8d956499b8f5053335b738cc408ca8859d326a3d`); CP-0040 candidate-input relevance matrix (blob `2ae5c36aa1f370cb143f8a30d5a61f41be0d60eb`); sensitivity applied-key list (blob `e4163cf24c4c78495a63ae85003a464ece360f43`) and input-impact file (blob `294605dbec00fe314a641885c2454994be5909f0`); frozen rulebook hash matches expected.
- **35 exact target keys:** all 35/35 are present in the frozen exact-key manifest; all have disposition `OPEN_REVIEW_REQUIRED`. Class counts: 14 `ACQUISITION_ECONOMIC_CONFLICT`, 5 `ACQUISITION_RAW_FIELD_CONFLICT`, and 16 `AGGREGATION_BUCKET_ROW_QUARANTINE`.
- **14 monthly-divergent keys / 97 fields:** all 14 are explicitly classed as `ACQUISITION_ECONOMIC_CONFLICT`, all remain open and source `NONE`; no case closed. They reproduce CP-0113's 14/97 result.
- **Critical application gap:** CP-0040 sensitivity applied-key list has nine exact keys (six 4h and three 1d). The overlap with CP-0113's 35 target keys is `0/35`, including `0/14` monthly-divergent keys. Input impact: 4h removed rows 6/19,975; 1d 3/3,332; 1mo 0/110. Presence in the manifest is therefore not evidence that the sensitivity filter actually removed these 5m/15m/30m/1h keys from candidate inputs.
- **Comparator boundary:** the 11-bucket relevance matrix reports no direct interval overlap with the single frozen `MTF_BREAKOUT_4H_D1` comparator (target intervals are 5m/15m/30m/1h). This does not prove irrelevance for every one of the 23 candidates currently failing G2.
- **Report:** `evidence/source_adjudication/CP0114_Quarantine_Overlap_G0_Impact_Report_HI.md`, Git blob SHA-1 `1546408f8b6c77b21a62fbd92fa9aceebdfcbe25`.
- **Current pointer:** `evidence/source_adjudication/CP0114_Quarantine_Overlap_G0_Impact_Current.json`. Pointer input hashes have been corrected to the actual current Git blob identities, and its report link is expected to match the report blob above.
- **Artifact output hashes:** `CP0114_Quarantine_Overlap_G0_Impact_Crosswalk.csv` 12,212 bytes SHA-256 `3028e71be4dedebbdae8c1ce475936b5475bacc32689ff6e70569454d468bed3`; `CP0114_MonthlyConflict_Quarantine_Overlap.csv` 5,913 bytes SHA-256 `ed1ea276992c40cd2826ec67c328c4be52d85295cc47bfc8d7815900164a21c7`; generated report artifact 2,041 bytes SHA-256 `5d4e1d42b24a3d15a561768e2228e67eb5861a8ccd9f4497b08b26f81a09f82b`.
- **Decision:** accepted candidate quarantine coverage for these exact keys is **not proven**. Do not upgrade G0 or treat manifest presence as applied quarantine. G0 remains `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; canonical source `NONE`; source cases closed 0; all 11 aggregation blockers open.
- **Non-actions:** no network/archive downloads, raw archive mutation, timestamp adjustment, synthetic candles, candidate build, backtest, strategy promotion, live signing, public broadcast or order placement.
- **Next bounded step:** map the 14 monthly conflict keys against the frozen candidate builder inputs for the current 23-candidate universe. Prove whether each key is active in any signal input or is actually excluded by the accepted policy. Do not edit source data or invent source precedence.


## CP-0115 candidate-universe interval exposure audit — 2026-10-16

- **Checkpoint:** `CP-0115`; status `PASS_CANDIDATE_INTERVAL_OVERLAP_AUDIT_G0_STILL_BLOCKED`. This is an interval-level exposure map, not proof of exact-key consumption or quarantine application.
- **Candidate universe evidence:** CP-0043 matrix `AISTS_CP0043_Candidate_G0_G1_Eligibility_Matrix.csv`, Library file id `file_00000000aa3081f4ab84c946ccf18812`, 33,602 bytes; SHA-256 `e18d0a2bbf6e724eb11507b35b3c0c4dfebbc5bfeda3c310c3f9e1b9f15b01c9`, as recorded in the CP-0045 package integrity record; 23 matrix rows.
- **Monthly conflict set from CP-0113:** 14 keys / 97 fields. Interval counts: 5m = 9, 15m = 4, 30m = 1; no exact monthly-divergent key is at 1h/4h/1d/1mo.
- **Direct interval-overlap candidates:** 9 configurations, each using the same local interval as a monthly-divergent key: `CP0027_5m_EMA_12_26`, `CP0027_5m_RSI14_30_55`, `CP0027_5m_DONCHIAN20_10`; `CP0027_15m_EMA_12_26`, `CP0027_15m_RSI14_30_55`, `CP0027_15m_DONCHIAN20_10`; `CP0027_30m_EMA_12_26`, `CP0027_30m_RSI14_30_55`, `CP0027_30m_DONCHIAN20_10`.
- **Candidate-scoped G0/G2 from CP-0043 matrix:** 12 candidates at local intervals 5m/15m/30m/1h have G0 BLOCKED; 11 at 4h/1d/1mo or multi-timeframe have candidate-scoped G0 PASS. G2 remains FAIL for 23/23. These are earlier candidate-scoped matrix values and do not change the current global G0.
- **Three 1h candidates:** no direct monthly-divergent key is at 1h in the CP-0113 14-key set; nevertheless, they remain candidate-scoped G0 BLOCKED because the broader low-timeframe source policy and cross-interval relationship blockers remain unresolved.
- **Exact key consumption and quarantine:** the crosswalk records `NOT_VERIFIED_NO_NEW_CANDIDATE_BUILD`. CP-0114 found zero overlap between the 14 conflicts and CP-0040's actual sensitivity applied-key list. Matching an interval indicates a potential/direct interval dependency, not proof that a specific exact row was consumed or successfully excluded by the current builder.
- **Report:** `evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Report_HI.md`, Git blob SHA-1 `2e29d2aa1b64f9a11451464897e4a6f9d0d80f75`.
- **Crosswalk CSV:** `evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Crosswalk.csv`, 23 rows, 5,261 bytes, Git blob SHA-1 `cdecff27f2472a59d91470cfd9ae774128ed0b37`.
- **Current pointer:** `evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Current.json`; report/crosswalk identities are bound in that pointer.
- **Decision:** no new evidence justifies upgrading global G0, selecting a canonical source, or closing a case. G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; canonical source NONE; cases closed 0; 11 aggregation blockers unresolved.
- **Non-actions:** no network requests or archive downloads; raw source bytes unchanged; no candidate build/backtest/promotion, timestamp shift, synthetic candle, signing, public broadcast or Binance order.
- **Next bounded action:** inspect the frozen CP-0026 candidate-builder and its exact-key quarantine-loading path. Establish from static code whether rows in the accepted manifest are excluded before signals are produced, and which G0 guard prevents the production build. Do not bypass the guard or declare a passing result without a rulebook-permitted reproducible proof.


## CP-0116 candidate-builder exact-key filter static audit — 2026-10-16

- **Checkpoint:** `CP-0116`; status `PASS_STATIC_AND_SYNTHETIC_KEY_FILTER_AUDIT_G0_STILL_BLOCKED`. This verifies code structure and synthetic function behavior; it is not a production build or G0 pass.
- **Workflow:** [GitHub Actions run 38942395977](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38942395977), head commit `d4ed30d0f7cecd9480c17e24cc79ec2a22fc96ac`; workflow and primary job `success`; runner `PASS`, 11/11; task-specific audit `PASS`, 20/20.
- **Artifact:** [12063652242](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38942395977/artifacts/12063652242), 9,113 bytes, ZIP SHA-256 `d257f101fb1af7d11ed64e831e62705a3c40315cc75a7591f317f16f13b58042`, seven-day retention. Child summary SHA-256 `aa8c903ecdd5b876355b389d3846aace6444e5b8770721ae6d69ec496d287242`.
- **Frozen source identity checks:** CP-0026 builder Git blob SHA-1 `06e9f292603b1f4755bea4c28ef027a01e2226d1`; CP-0040 quarantine helper `ff756af2f27d307779cde92f41a842467ada2d77`; manifest `8d956499b8f5053335b738cc408ca8859d326a3d`; manifest summary `964197632042dd3c761ab25cf32921601ed74e4f`; non-row blockers `d3fca23bac424fa8c8b187434e8c63e8d188a0e1`. CP-0040 rulebook SHA-256 again matched `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
- **Manifest state:** 1,427 rows / 1,427 unique exact keys; CP-0113's 35 exact target keys all exist in the manifest. The gate summary remains `PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN`; `candidate_eligibility_blocked=true`; 11 non-row aggregation blockers remain.
- **Static control-flow result:** in CP-0026 `main()`, `load_candidate_gate` at line 497 precedes flagged-date input read at line 499, candidate output-directory creation at line 514 and interval build loop at line 521. The inline exact key filter in `audit_and_write_interval` uses `(interval, str(open_time_ms))`; matching rows are added to quarantine evidence and `continue` executes before the output writer at line 415.
- **Existing builder self-test:** ran the builder's `run_gate_self_test` function against the actual frozen manifest, blocker CSV and summary. Result 5/5 PASS, including explicit failure-closed assertion with `G0_BLOCKED_NONROW_BLOCKERS_REMAIN: 11 unresolved non-row cases`, exact-key match, one-millisecond neighbor retention, raw timestamp preservation and other-interval non-match.
- **Synthetic exact-key probe:** all 35/35 target-key dictionaries were excluded by `partition_candidate_rows`; 0 were kept. One-millisecond neighbor and other-interval fixtures remained kept. Source timestamp tokens were not changed. The probe CSV is preserved in the linked run artifact, SHA-256 `7bef46faaffcb37c165cde9cbf6a628f1d55aefe9afa21de5cc1833a53d06a6f`.
- **Report:** `evidence/source_adjudication/CP0116_Candidate_Filter_Static_Audit_Report_HI.md`, Git blob SHA-1 `3f2a11cb5abd31bb62e0324c40c0ceb027c6b1b4`.
- **Current pointer:** `evidence/source_adjudication/CP0116_Candidate_Filter_Static_Audit_Current.json`; report Git blob linkage is recorded there.
- **Run-generated report artifact hash:** 2,331 bytes, SHA-256 `81549aca95eb826b75c04740e0a4ebbbef3d7627bb21df3cbe8ba3cdc8e543c4`. This is the report generated inside the Actions artifact; it is not the separately persisted repository report blob.
- **Critical boundary:** this confirms the exact-key filter implementation and its behavior with synthetic rows. It does **not** prove that real candidate output files have had the 35 target keys removed because production `main()` was not invoked and no candidate dataset/output rows were built. The production build remains intentionally blocked before source-data processing while 11 non-row blockers remain.
- **Decision and gates:** canonical source `NONE`; source cases closed 0; 11 aggregation blockers unresolved; G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`. No source case, strategy or candidate eligibility was promoted by CP-0116.
- **Non-actions:** no network requests/archive downloads, raw source edits, timestamp shifts/rounding, synthetic research candles, production candidate build, output rows, backtest, strategy promotion, live signing, public broadcast or Binance orders.
- **Next bounded action:** continue the frozen CP-0040 rulebook-bound disposition of the 11 non-row cross-interval aggregation blockers. Do not bypass the builder guard or invent daily-over-monthly source precedence.


## CP-0117 frozen-rulebook disposition of 11 non-row aggregation blockers — 2026-10-16

- **Checkpoint:** `CP-0117`; status `PASS_RULEBOOK_BOUND_NONROW_DISPOSITION_G0_STILL_BLOCKED`. Runner `PASS`, 11/11; audit checks `PASS`, 34/34.
- **Workflow:** [GitHub Actions run 38943714749](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38943714749), executed commit `6f6e46b76e0e95db29ee9ccef28cd617e5fed604`; conclusion `success`; child-summary SHA-256 `915647f94aff3977a6c05a172dd7eb60622aac6728d90db9643b9cadeaa620cf`.
- **Artifact:** [12063164661](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38943714749/artifacts/12063164661), 13,199 bytes; ZIP SHA-256 `110c2001850a047c0e35553aec65aefed1623c074ef98dbf9b8c9827f6357fe0`; retention 7 days.
- **Report:** `evidence/source_adjudication/CP0117_Rulebook_Bound_Blocker_Disposition_Report_HI.md`, Git blob SHA-1 `cee4dd57a8a7a42b99cd0934177a3540f26834cb`, 4,251 bytes; generated report SHA-256 `20f954f737cb6e4466b3fe0f5dd82318105e407d3c5920a4759e79c7cde0f7f4`.
- **Per-blocker matrix:** `evidence/source_adjudication/CP0117_NonRow_Blocker_Disposition_Matrix.csv`, 11 cases / 21 columns / 4,059 bytes; repository Git blob SHA-1 `0b34a1393dff60887ed384175025e1f02eacc1c7`. The Actions artifact's raw generated CSV SHA-256 is `b031e22afce350ff6acab7f69f266276a4989f29f5d9b4bb9f9109480e4ed8a3`; repository line-ending normalization means the artifact digest and Git blob identity are recorded separately.
- **Current pointer:** `evidence/source_adjudication/CP0117_Rulebook_Bound_Blocker_Disposition_Current.json`; links the report, matrix, input identities, run/artifact, counts and decision.
- **Frozen rulebook and manifest:** CP-0040 rulebook SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`; manifest 1,427 rows / 1,427 unique keys; 11 non-row blockers remain, and candidate eligibility stays blocked.
- **All eleven case joins:** the 11 blockers join 1:1 with the CP-0112 reconstructed bucket results. Per-case manifest key sets equal row-evidence key sets for `11/11`; all 35 exact row keys are represented/tagged; each case remains open and has no canonical source. Trade-derived parent-child rollups pass `11/11`.
- **Cross-source totals:** current checksum-verified Spot trades corroborate daily rows for `35/35` bars and `315/315` fields. Monthly rows match `21/35` bars and `218/315` fields; `14` unique keys / `97` fields remain divergent.
- **Quarantine/build boundary:** CP-0114 found `0/14` divergent keys in the previously applied CP-0040 sensitivity key list. CP-0116 verified the exact-key filter function on `35/35` synthetic rows, but did not run production candidate building. Actual candidate-specific quarantined metrics are not established because the builder remains fail-closed on the 11 blockers.
- **Candidate relevance and sensitivity:** CP-0115 identifies 9 low-timeframe candidate configurations with direct interval overlap; G2 still fails all 23 candidates. CP-0040's frozen sensitivity run changed TRAIN net return by `-15.89174082849894` percentage points, keeping G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- **Historical provenance:** dated snapshot `evidence/source_adjudication/CP0117_External_Provenance_Issue_Status_Snapshot_20261016.json`, Git blob SHA-1 `75010522badfb8b762b4fc25b804234e6e02585e`. Binance public-data issue #504 was open with zero comments at snapshot time; no maintainer answer to the previous-version/timestamp question was observed. That absence does not prove historical versions do not exist; it means the guarantee remains unestablished. Issue #475 concerns other dates and is context only.
- **Disposition:** all 11 relationship blockers remain `KEEP_OPEN_EXACT_ROWS_QUARANTINED_RELATIONSHIP_UNRESOLVED`. Root cause and historical archive-version provenance remain `OPEN_NOT_ESTABLISHED`; no daily-over-monthly precedence is introduced; canonical source `NONE`; source cases closed `0`.
- **Gates unchanged:** G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G7 `LIVE_BLOCKED`.
- **Non-actions:** no archive download/network inside CP-0117, no source-byte mutation, no timestamp shifts/rounding, no synthetic candles, production candidate build, backtest, strategy promotion, signing, public broadcast or Binance orders.
- **Next bounded action:** pursue independently evidenced historical-version/source adjudication for these 11 relationships, or a formally frozen conservative quarantine policy and real candidate-specific final metrics. Do not bypass the G0 builder guard.


## CP-0118 daily/monthly internal parent-child rollup audit — 2026-10-16

- **Checkpoint:** `CP-0118`; status `PASS_MONTHLY_PARENT_CHILD_INTERNAL_ROLLUP_AUDIT_SOURCE_AUTHORITY_OPEN`. This is a deterministic arithmetic comparison over frozen CP-0107 RowEvidence, not a source-selection decision.
- **Workflow:** [GitHub Actions run 38944519562](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38944519562), commit `693ccaaa226c8f81f3fe0e0dfeab9003f895d9a1`; conclusion `success`; child task result PASS. Child-summary SHA-256 `c82eba758b1a3b347af83d6bd8db1750780c94c72b3f86c0d85a4addf8ba5f94`.
- **Artifact:** [12064312282](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38944519562/artifacts/12064312282), 13,088 bytes, retention 7 days.
- **Frozen inputs:** CP-0107 RowEvidence CSV blob `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9` (78 records); bucket snapshot blob `6e32188472ab45b43e1b90fe138399818c937277` (11 bucket rows); CP-0117 pointer blob `1515a6f07dbb5a8b84e8de05ce3794558feb0bbf`; CP-0117 report blob `cee4dd57a8a7a42b99cd0934177a3540f26834cb`; frozen CP-0040 rulebook SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
- **Method:** each blocker’s frozen parent row was compared with its source’s own child-row rollup for open, high, low, close, base volume, quote volume, trade count and both taker-buy volume fields. Decimal arithmetic was used for economic numeric values and integer arithmetic for trade count. No source data was changed.
- **Primary result:** daily parent-child rollups match exactly in `11/11` buckets across all 9 fields. Monthly parent-child rollups fully match in `0/11`; every monthly bucket has at least one internal parent-vs-children mismatch.
- **Mismatch membership counts across buckets:** `58` monthly per-case field-mismatch memberships. This is a bucket-membership count with keys/fields that overlap across relationships; it is not the CP-0113 globally deduplicated 97-field figure. Field frequency by cases: open 2/11, high 3/11, low 3/11, close 1/11, volume 11/11, quote volume 11/11, trade count 11/11, taker-buy base volume 8/11, taker-buy quote volume 8/11.
- **Magnitude examples:** for AGG-01 monthly child base-volume sum is `5.55522600` while stored parent volume is `13.00336300`, and child trade counts sum to `46` while stored parent count is `106`. AGG-05 monthly child volume sum is `40.85844400` versus parent `140.41819800`, with child trades `423` versus parent `1512`. Exact per-case values are in the matrix/details CSV.
- **Interpretation:** this proves arithmetic inconsistency between the current monthly parent row and the rollup of that same monthly source’s child rows in all 11 exact windows. Together with CP-0112, daily rows match checksum-verified trade reconstruction (35/35 bars, 315/315 fields), while monthly source matches 21/35 bars and 218/315 fields. This localizes the inconsistency to the current monthly archive’s own parent-child relationship for these windows, but does not establish whether the cause is a historical revision, publication/version skew, processing difference or another root cause.
- **Report:** `evidence/source_adjudication/CP0118_Monthly_ParentChild_Internal_Rollup_Report_HI.md`, repository Git blob SHA-1 `336762296a9ac0bad06b6cc620722e16e1404c05`; 5,136 bytes; artifact SHA-256 `1cd91d2ca6a57828a515191446d57c2dcd5d1e9e21f6a8f09359f8d5f0fe76f7`.
- **Bucket matrix:** `evidence/source_adjudication/CP0118_ParentChild_Internal_Rollup_Matrix.csv`, 11 cases / 3,952 bytes; repository blob SHA-1 `d4680d70eb0cd71d3f6d14df1ba5ebcd1bf9c8b3`. Run-generated artifact SHA-256 `1f783b86dc021d9c7d305cc4dc9f9c4de93c846fb903fd3aec2fc69d35f35121`.
- **Detail matrix:** `evidence/source_adjudication/CP0118_ParentChild_Internal_Rollup_Details.csv`, 22 source-case rows / 9,630 repository bytes; repository blob SHA-1 `935edba0dee13450ef43ee67254b615cb329e728`. The raw run artifact records 9,618 bytes and SHA-256 `65c6a4a2ff431db172a5d48f469cdfeed2dd778f2c861d3025fb43b71e12f801`; use the linked Actions artifact for the exact runner-generated bytes.
- **Current pointer:** `evidence/source_adjudication/CP0118_Monthly_ParentChild_Internal_Rollup_Current.json`; binds run, frozen inputs, current report/matrix/detail repository blob IDs, raw artifact hashes and unchanged gate state.
- **Disposition/gates:** canonical source `NONE`; source cases closed `0`; all 11 cross-interval relationship blockers remain open; history provenance and root cause `OPEN_NOT_ESTABLISHED`. G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G7 `LIVE_BLOCKED`.
- **Non-actions:** no network/archive downloads, raw source mutation, timestamp shifts/rounding, synthetic candles, production candidate build, backtest, strategy promotion, signing, public broadcast or Binance orders.
- **Next bounded action:** seek dated correction/version evidence tied to the exact current daily/monthly ZIP hashes and these parent-child keys. If no acceptable version provenance can be obtained, only consider a formally frozen conservative quarantine policy with real candidate-specific final metrics; never bypass G0 or invent daily-over-monthly precedence.
