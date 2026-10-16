# CP-0108: Residual aggregation blocker evidence-boundary decision
**Checkpoint date:** 2026-10-16  
**Status:** `BLOCKED_NO_NEW_AUTHORITY_EVIDENCE_FOR_11_RESIDUAL_AGGREGATION_BUCKETS`  
**Checkpoint type:** Evidence-only, read-only adjudication decision

## 1. Scope and inspection baseline
This checkpoint resumes the existing AISTS BTCUSDT research/audit project. It does not create a new audit universe or replace prior evidence.

- Repository: `manish91082-coder/aists-btcusdt-research-runner`
- Branch inspected: `main`
- Latest commit returned by the connector's descending recent-commit search before this checkpoint: `9cc1e532df745a5a04de91ea0d7a7d185e1d4490`
- Prior continuity checkpoint: CP-0097, official correction-route closure for its frozen target set.
- Current continuity file at inspection: `evidence/CURRENT_RESEARCH_STATE_HI.md`, Git blob SHA-1 `5770fcf0a2d96f4e03d7c745af75413cfcab0e48`.
- Combined commit status for the inspected commit returned no status entries. This is not treated as CI PASS or CI FAIL.

The inspection used committed GitHub evidence and a read-only check of the current official Binance Public Data README. No new market-data acquisition, trading research run, backtest, candidate build, data repair, workflow dispatch, or strategy evaluation was performed.

## 2. Evidence read and current Git blob identities

| Evidence | Current blob SHA-1 | Verified content |
|---|---|---|
| `evidence/CURRENT_RESEARCH_STATE_HI.md` | `5770fcf0a2d96f4e03d7c745af75413cfcab0e48` | 638 lines at inspection; tail ends at CP-0097 |
| `evidence/source_adjudication/CP0097_Official_Correction_Route_Closure_HI.md` | `e0d19fcbdfd288148a3a45e8a4e4feb0da06dddd` | CP-0097 scope and decision |
| `evidence/source_adjudication/CP0097_Official_Correction_Route_Closure_Current.json` | `084a401073c573fb80d005d6982cb955c737b841` | Pointer reports route exhausted only for its frozen set; no source selected and zero cases closed |
| `evidence/source_adjudication/CP0097_Official_Binance_Public_Data_README_master.md` | `e01e34a0b0cd91d62386a5a237190a3167138bae` | Preserved official README; exact hash is also recorded in CP-0097 |
| `evidence/source_adjudication/CP0040_Run_38883792900/CP0040_NonRow_Blockers.csv` | `d3fca23bac424fa8c8b187434e8c63e8d188a0e1` | 11 unresolved aggregation blockers |
| `evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv` | `6e32188472ab45b43e1b90fe138399818c937277` | 11 frozen buckets, monthly mismatch signature and closure requirement |
| `evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Comparison.csv` | `5dae35e8d420b3997be90cabc263825e98b8b918` | 11 per-bucket comparison rows |
| `evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv` | `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9` | 78 row-evidence records |
| `evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Summary.json` | `08221ec6baab7257b61f803fe78064cc26717ef5` | CP-0107 summary and 12 PASS diagnostic checks |
| `evidence/source_adjudication/CP0107_Official_Update_Package_Shared52_DailyCrosswalk.csv` | `718c2ac990d9fb5d9c731fdda4fc92657d375ad2` | 52 distinct shared economic-conflict rows |

These are Git blob SHA-1 identifiers, not archive SHA-256 values. The row-level archive SHA-256 values and the source package/member SHA-256 values remain those recorded in the respective CP-0107 evidence; this checkpoint does not recompute or replace them.

## 3. Aggregation evidence result
The frozen blocker ledger and CP-0107 artifacts agree on 11 unresolved cross-interval buckets. The row-evidence file has 78 records: 8 records for each of six 5m-to-15m buckets and 6 records for each of five remaining buckets.

- All 11 buckets have complete exact-key daily child/parent coverage.
- No daily child keys are reported missing or duplicated in the comparison.
- Daily child rollups match their respective daily parent rows for all 11 buckets.
- Monthly child/parent rollup mismatches remain for all 11 buckets and match the frozen mismatch signature.
- The CP-0107 summary records 12/12 diagnostic checks PASS, but explicitly says this overlay does not assign canonical-source authority and does not close a bucket.
- The monthly child-volume sum representation check reports 10 matches out of 11. AGG-10 retains the recorded values `279.26867100000004` and `279.26867100` as a representation difference. Do not normalize or overwrite them under this checkpoint.

The affected frozen bucket dates are 2017-12-04, 2018-02-05, 2018-02-07, 2018-03-04, 2018-03-20, 2018-06-20, and 2018-09-05. This is diagnostic evidence of an archive-to-archive discrepancy, not proof that either archive is universally canonical.

## 4. Official-correction evidence reconciliation
### CP-0097 scope
CP-0097 verified the preserved README blob identity, CP-0095's exact-path and basename results of 0/16, and CP-0096's daily and monthly archive-hash hits of 0/16 and 0/14. Its closure is strictly limited to the correction-search route for that frozen set. It cannot be generalized into closure of other cases.

### Current public README check
The current public page at `https://github.com/binance/binance-public-data/blob/master/README.md` still shows two update-table entries: the 2022-08-08 kline correction bundle and the 2022-04-21 aggregate-trade update. The only listed kline correction is `2022-08-08_kline_updates.zip`. No new kline-correction entry was visible in this inspection. This is a catalogue observation, not an assertion that every archive is correct.

### CP-0107 shared-52 crosswalk is a separate target set
The committed crosswalk contains 52 rows; 33 rows have exact official daily paths and 33 rows have a replacement checksum matching the frozen daily archive SHA-256. Nevertheless, its current disposition is `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION` for all 52 rows, canonical source is `NONE` for all 52, and `case_closed=false` for all 52.

The 52-row crosswalk has no exact UTC-date overlap with the 11 frozen aggregation bucket dates in this checkpoint. It therefore supplies no direct row-level correction mapping for these 11 aggregation cases. The 33/52 result must not be used either to close these buckets or to contradict CP-0097's narrower frozen-target result.

## 5. Decision
**Decision: remain BLOCKED; do not close or reclassify any of the 11 buckets.**

The missing evidence is not another arithmetic comparison. The missing evidence is authoritative version/provenance evidence that attributes the affected child and parent archive bytes for the exact frozen bucket keys, or another independently verifiable primary-source record permitted by the frozen rulebook that can adjudicate those specific values.

The following actions are explicitly not justified:
- Re-running the same 2022-08-08 correction-bundle lookup against the same already-audited files without genuinely new official evidence.
- Treating daily rollup consistency alone as canonical-source authority.
- Treating the shared-52 crosswalk as evidence about these 11 exact bucket keys.
- Closing cases, changing source dispositions, altering raw archives, shifting timestamps, rounding away mismatches, creating synthetic candles, rebuilding candidates, backtesting, or promoting a strategy.

## 6. Next bounded action
Proceed only if genuinely new official provenance/version evidence can be identified for the exact child/parent archive files and UTC bucket keys listed in the frozen CP-0107 source snapshot. The next inspection must skip the exhausted correction-bundle route and the already-reviewed CP-0107 artifacts, and must record exact source URL/path, archive identity, checksum/version linkage, UTC key coverage, and applicability to each bucket. If no distinct applicable evidence is available, preserve all 11 blockers as unresolved and do not run a research or strategy gate.

## 7. Gate and safety state
- `G0 = BLOCKED_GLOBAL`
- `G2 = FAIL_CURRENT_23_CANDIDATES`
- `G7 = LIVE_BLOCKED`
- Canonical source: `NONE`
- Unresolved non-row aggregation blockers: 11
- Shared conflicts: 60
- Unmatched rows quarantined: 909
- Source cases closed by this checkpoint: 0
- Raw source bytes changed: false
- Candidate build/backtest/strategy promotion performed: false
- Live signing/public broadcast/Binance orders performed: false

This checkpoint is a reasoned decision over previously committed evidence; it is not a new quantitative result, a workflow run, or a gate pass.
