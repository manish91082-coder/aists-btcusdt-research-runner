# CP-0109: Link CP-0097 correction-route evidence to the 11 residual aggregation buckets
**Checkpoint date:** 2026-10-16  
**Status:** `BLOCKED_OFFICIAL_CORRECTION_ROUTE_EXHAUSTED_FOR_11_AGGREGATION_BUCKETS_SOURCE_AUTHORITY_OPEN`  
**Checkpoint type:** Read-only evidence join and scope reconciliation; no new market-data run

## 1. Purpose
CP-0108 correctly retained all 11 residual cross-interval aggregation cases as unresolved. This follow-up checks whether CP-0095/CP-0096/CP-0097's frozen correction-target archives are actually the same archive set referenced by the 11 CP-0107 aggregation buckets. This is a link/identity audit over existing committed evidence, not a rerun of the correction search or a new archive acquisition.

## 2. Read-only inputs and their current Git blob SHA-1 values

| File | Git blob SHA-1 |
|---|---|
| `evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv` | `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9` |
| `evidence/source_adjudication/CP0095_Official_Correction_Target_Mapping_Run_38912641513/CP0095_Correction_Target_Mapping_Matrix.csv` | `53f98b0c68abcd6bb62d31ddd73415fa62d5d3ba` |
| `evidence/source_adjudication/CP0095_Official_Correction_Target_Mapping_Current.json` | `ac317a58197f0ccc72981cb015a0493db318905d` |
| `evidence/source_adjudication/CP0096_Correction_Checksum_Crosswalk_Run_38913040361/CP0096_Correction_Checksum_Crosswalk.csv` | `7e7b00dc9f38897349682dce0807b0e599ee180f` |
| `evidence/source_adjudication/CP0096_Correction_Checksum_Crosswalk_Current.json` | `c2e276b691600d4fa5155c2cad02ba5ca8e82097` |
| `evidence/source_adjudication/CP0096_Correction_Checksum_Crosswalk_Run_38913040361/CP0096_Correction_Checksum_Crosswalk_Report_HI.md` | `3a30f215daea16217ec9b9daa15d6e47ece29167` |
| `evidence/source_adjudication/CP0097_Official_Correction_Route_Closure_HI.md` | `e0d19fcbdfd288148a3a45e8a4e4feb0da06dddd` |
| `evidence/source_adjudication/CP0097_Official_Correction_Route_Closure_Current.json` | `084a401073c573fb80d005d6982cb955c737b841` |
| `evidence/source_adjudication/CP0097_Official_Binance_Public_Data_README_master.md` | `e01e34a0b0cd91d62386a5a237190a3167138bae` |
| `evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Comparison.csv` | `5dae35e8d420b3997be90cabc263825e98b8b918` |
| `evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Summary.json` | `08221ec6baab7257b61f803fe78064cc26717ef5` |

All files were fetched through GitHub at `main` for this comparison. SHA-1 above is Git blob identity, not archive SHA-256.

## 3. Exact target-set linkage checks

### Daily archives: CP-0095 target set versus CP-0107 bucket evidence
- CP-0107 RowEvidence has 78 data rows across 11 frozen buckets and 16 unique daily archive filenames.
- CP-0095 mapping matrix has 16 daily target rows.
- The unique daily archive filename sets are exactly equal: **16/16 names match**.
- For every shared filename, CP-0107's `source_archive_sha256` equals CP-0095's `verified_daily_zip_sha256`: **16/16 filename-to-SHA-256 pairs match**.
- No target filename is missing, extra, or mapped to a different SHA-256 in this linkage check.

### Monthly archives: CP-0096 target set versus CP-0107 bucket evidence
- CP-0107 RowEvidence has 14 unique monthly archive filenames across the same 11 buckets.
- CP-0096's checksum crosswalk contains 14 monthly archive targets.
- The unique monthly archive filename sets are exactly equal: **14/14 names match**.
- For every shared filename, CP-0107's `source_archive_sha256` equals CP-0096's crosswalk `sha256`: **14/14 filename-to-SHA-256 pairs match**.
- The CP-0096 daily target names and SHA-256 mappings also independently match CP-0107's 16 daily source archive entries exactly.

**Linkage decision:** The 16 daily and 14 monthly files previously examined in CP-0095/CP-0096 are the exact archive-file set referenced by the 11 frozen CP-0107 aggregation buckets. CP-0097's correction-route decision is therefore directly applicable to these 11 buckets; this was verified through name-set and per-filename archive-hash equality, not inferred from the checkpoint labels.

## 4. Correction-route results applied to this exact archive set
- CP-0095 reports exact official correction paths: 0/16; correction basename matches: 0/16.
- CP-0096 parsed 73,234 correction CSV records and compared both Original File Checksum and New File Checksum SHA-256 tokens with every one of the 16 daily and 14 monthly archive SHA-256 values.
- Result: daily checksum hits 0/16; monthly checksum hits 0/14. There are no exact correction-file path or basename hits for the 16 daily archive target names, and no correction Original/New checksum token matches any of the 30 verified archive byte hashes.
- The preserved official Binance Public Data README has blob SHA-1 `e01e34a0b0cd91d62386a5a237190a3167138bae`, matching the official blob identity recorded in CP-0097. Its Updates inventory documents one kline correction archive, `2022-08-08_kline_updates.zip`; the other listed update is for aggregate trades.
- Therefore the already-inspected public kline-correction bundle is exhausted for the **exact archive set underlying these 11 aggregation buckets**. Do not download, reparse, or re-run the same correction lookup against this unchanged target set absent genuinely new official evidence.

## 5. What this does and does not establish
**Established**
1. Daily and monthly archive identities in CP-0107 exactly match the already inspected correction-route target manifests by filename and SHA-256.
2. The correction CSV provides no exact path/basename match for the 16 daily targets and no Original/New checksum hit for any of the 30 archive files.
3. The CP-0097 closure is not unrelated to these blockers; its frozen archive set is the exact set now cross-joined to the 11 blockers.

**Not established**
1. No conclusion that daily or monthly candles are universally correct.
2. No source-authority attribution for any conflicting field.
3. No root cause for the cross-interval mismatch.
4. No case closure and no canonical-source selection.
5. No strategy eligibility, G0/G2/G7 promotion, or quantitative-performance result.

The daily archive child-parent rollup matches in CP-0107 provide internal consistency evidence only. The monthly rollup mismatches remain in all 11 buckets; the recorded AGG-10 volume-sum representation difference remains unchanged and is not normalized.

## 6. Decision and next bounded action
**Decision:** correction-route lookup is exhausted for the 11 aggregation buckets as well as for the specific CP-0097 target set. Keep all 11 buckets unresolved because official correction-route non-applicability is not itself source authority.

The next valid action is to inspect only a *distinct* source-of-authority or archive-version provenance source that can independently adjudicate the exact child/parent archive bytes and frozen UTC keys and is permitted by the frozen rulebook. The next action must record exact URL/path, version or checksum linkage, applicability to each bucket, and reproducible evidence. Do not re-run the same correction package, repeat the daily rollup arithmetic, or mutate sources. If no distinct applicable evidence exists, remain blocked and document the missing source authority.

## 7. Gates and safety state
- `G0 = BLOCKED_GLOBAL`
- `G2 = FAIL_CURRENT_23_CANDIDATES`
- `G7 = LIVE_BLOCKED`
- Canonical source: `NONE`
- Non-row aggregation blockers: 11 unresolved
- Shared conflicts: 60 unresolved
- Unmatched rows quarantined: 909
- Source cases closed by this checkpoint: 0
- Archive downloads in this checkpoint: 0
- Raw source bytes modified: false
- Timestamps shifted/rounded or synthetic candles created: false
- Candidate build/backtest/strategy promotion: not performed
- Signing/public broadcast/Binance orders: not performed
- GitHub Actions workflow dispatch: not performed; this is an evidence-only linkage check.

This checkpoint reconciles the scope boundary. It is not a successful source-adjudication gate.
