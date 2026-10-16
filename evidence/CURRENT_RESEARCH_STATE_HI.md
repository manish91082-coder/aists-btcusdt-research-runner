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
