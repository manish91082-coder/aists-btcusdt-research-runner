# CP-0259: G0 unresolved-population candidate-impact reconciliation (Hindi)

**स्थिति:** EXISTING-EVIDENCE RECONCILIATION COMPLETE FOR AVAILABLE REPOSITORY RECORDS; G0 STILL `BLOCKED_GLOBAL`.  
**Scope:** reconcile known unresolved populations against the frozen `MTF_BREAKOUT_4H_D1` candidate and all-candidate exposure, without rescanning archives or changing raw data.  
**Frozen rulebook SHA-256:** `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.  
**No source archive downloaded/modified. No candidate build/backtest run.**

## 1. Why this checkpoint was necessary

The CP-0257 result that AGG-01…AGG-11 have no direct 4h/D1 interval overlap applies only to those 11 lower-timeframe aggregation relationships. It must not be generalized to all unresolved populations. Existing records show **four shared economic conflicts directly overlap the frozen 4h/D1 comparator**, and **three close-time-only cases are on 4h bars**. Therefore the comparator's G0 cannot be cleared by the AGG crosswalk alone.

## 2. Existing evidence reconciled

| Population | Existing source / blob | Verified facts | Candidate impact and decision |
|---|---|---|---|
| 23-candidate interval exposure | `evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Crosswalk.csv`; blob `cdecff27f2472a59d91470cfd9ae774128ed0b37` | 23 rows; 9 candidates have direct local interval overlap with monthly divergences; 3 lower-timeframe candidates remain blocked by source policy; 11 candidates show no direct CP-0113 monthly-divergence interval overlap | All 23 remain G2 FAIL. “No direct CP-0113 overlap” is not proof that other G0 populations do not affect those inputs. Exact row consumption in new builder remains NOT VERIFIED. |
| 909 unmatched rows | `evidence/source_adjudication/CP0107_Unmatched_909_Provenance_Audit_Summary.json`; blob `fe51b63f1fb54c5077d844e635e73aceb96f16e1`; triage summary blob `018c59260e6d3a6fb69ddd9c6425cac92b464b4a` | 909 exact worklist/raw/source links and archive-manifest/sidecar hash matches; 452 daily-only + 457 monthly-only; 909/909 exact counterpart absent; 909/909 cases remain open; no shift/round/merge/replace/delete | Provenance integrity is verified, source authority and full per-candidate impact are not. The repository points to a Library CSV, not an exact-key impact output available in this branch; per-key active-input impact remains `MISSING_EVIDENCE` here. |
| 52 shared economic/trade conflicts | `evidence/source_adjudication/CP0107_Shared52_Candidate_Input_Dependency_Run_38902949514/CP0107_Shared52_Candidate_Input_Dependency_Matrix.csv`; blob `196bdb50546e184b755151fc4e14b5b7246267e4`; summary blob `a5d15c671682bfd7b7910c82289dbcbfe986bce7` | 52 cases; 4 direct frozen comparator input conflicts: 2 × 4h and 2 × 1d; 48 other intervals; all 52 remain open, canonical source NONE | **Direct G0 blocker for MTF_BREAKOUT_4H_D1.** Exact cases below. Inspected official update bundle did not contain exact target archive members; source authority remains open. |
| 8 close-time-only conflicts | `evidence/source_adjudication/CP0107_CloseTimeOnly_FieldDisposition_Final.csv`; blob `2c02c75b1d4c32f84d210d4981b0a5a1efd78faf`; summary blob `5354cf3df24a747a8f098ca0f9d39e277a6b40e1` | 8/8 economic fields match; 5 monthly boundary mismatches and 3 daily boundary mismatches; 3 cases are 4h, all 8 open, canonical source NONE | **Three direct 4h boundary-metadata cases remain unresolved.** Exact close-time policy disposition and source authority are not established. |
| 450 February-2018 off-grid rows | `evidence/source_adjudication/CP0107_Feb2018_OffGrid_RowDisposition.csv`; blob `8ac5bd8469217b0d9b8a914b5532d7e992d7f6b0` | 10 segment/source summary rows; all show `QUARANTINE_REVIEW_REQUIRED`, `OPEN_PROVENANCE_REQUIRED`, canonical source NONE; raw per-row values not all exported in the referenced CP-0106 artifact | These 450 are a subset of 909, not additional cases. Preserve raw timestamps; no shifting/rounding. Exact row-level disposition/impact remains unresolved. |
| 11 non-row aggregation blockers | `evidence/source_adjudication/CP0117_NonRow_Blocker_Disposition_Matrix.csv`; blob `0b34a1393dff60887ed384175025e1f02eacc1c7`; CP-0107 78-row evidence blob `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9` | 11 relationships; lineage evidence exists; source root cause and historical archive-version provenance unresolved; cases not closed | All 11 remain open. CP-0257's no-direct-4h/D1-overlap finding is narrow; it does not close the global source-authority gate. |
| 17 missing 4h slots | CP-0215 residual-gap matrix blob `b4b75841f9c15ce1336919614754bd54927a10d2`; CP-0206 frozen policy blob `224deb40b9acae340103ed1acc360a2d50d971c9` | 1 slot overlaps an existing row case; 16 are absent from both inspected sources. Production censor/scored-ledger path is not fully verified; Policy B not authorized | Direct 4h input gap blocker. No synthetic candle, inferred fill, or intragap path. |
| December-2020 residuals | `evidence/source_adjudication/CP0107_CP0041_Dec2020_Residual7_ExactKey_Audit.csv`; blob `879740918b86b7932bd7d89736d7516225408dde`; summary blob `6429a0761a932b866293d588a77a6342ded83985` | 7 exact monthly-only keys; exact raw tokens/archive integrity checked; daily exact counterpart absent; all remain open | Existing source audit did not establish authority. Preserve separately until identity links prove overlap/disjointness; no auto-closure. |
| Invalid daily-only 4h placeholder | Existing CP-0107 unmatched/gap records and frozen CP-0206 policy | At `2017-09-06T16:00:00Z`: flat OHLC, zero volume/trades, invalid 4h close-time span; not a valid accepted candle | Direct 4h input blocker. Presence in daily file is insufficient. Must be authoritatively adjudicated or covered by an actually authorized scope. |

## 3. Four direct shared conflicts that prevent declaring comparator input clean

| Case ID | Interval | UTC open | Conflicting fields | Current disposition |
|---|---|---|---|---|
| `SHARED-1d-1611187200000` | 1d | 2021-01-21T00:00:00Z | volume, quote volume, trade count, taker-buy base/quote volumes | `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION` |
| `SHARED-4h-1611216000000` | 4h | 2021-01-21T08:00:00Z | volume, quote volume, trade count, taker-buy base/quote volumes | `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION` |
| `SHARED-1d-1640304000000` | 1d | 2021-12-24T00:00:00Z | volume, quote volume, trade count, taker-buy base/quote volumes | `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION` |
| `SHARED-4h-1640304000000` | 4h | 2021-12-24T00:00:00Z | volume, quote volume, trade count, taker-buy base/quote volumes | `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION` |

All four remain open, and no canonical source is selected. The existence of a checksum or official daily update path is not sufficient to adjudicate monthly-versus-daily historical authority.

## 4. Batch decision

The following are now safe to treat as one reconciled internal evidence package:
- All existing population summaries, candidate exposure counts, and exact IDs/hashes above.
- The non-double-counting links: February off-grid ⊂ 909 unmatched; 17 gap slots include one existing row case; 52 shared conflicts and 11 non-row relationships remain separate views unless exact-key identity proves overlap.
- The four direct shared conflicts and three 4h close-time-only cases are explicitly called out as direct comparator dependencies.

The following cannot be completed internally by inference:
- Select a historical canonical source for conflicting bytes.
- Close the 909 unmatched cases, 52 economic conflicts, 8 boundary conflicts, 11 aggregation relationships, 17 gap slots or 7 December residuals without compliant evidence/disposition.
- Authorize Policy B or fill the independent review decision record.
- Claim all unresolved keys are excluded from active candidate signal/position/valuation inputs: exact-row consumption is still not verified for the new builder and the unmatched 909 per-key impact export is not available in this branch.

## 5. Final decision and next gate

**G0 remains `BLOCKED_GLOBAL`.** This is a substantive blocker map, not a source scan and not an approval.

Next action: obtain qualifying official key-specific historical-version evidence or an authorized independent written adjudication for the frozen populations. If neither is present, no amount of internal CI or repeated hash verification can truthfully change G0. Once the required authority record exists, process all affected cases in one bounded review/application/impact/accounting/CI package, then make the G0-A–G0-E decision.

Current safety state: canonical source `NONE`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; candidate build and acceptance-grade backtest blocked; profitability not established; live signing/broadcast/orders blocked.
