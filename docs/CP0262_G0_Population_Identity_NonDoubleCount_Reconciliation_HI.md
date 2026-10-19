# CP-0262: G0 population identity and non-double-counting reconciliation (Hindi)

**स्थिति:** COUNT PARTITION RECONCILED; KEY-LEVEL SUBSET LINKS PARTIALLY UNVERIFIED; G0 STILL `BLOCKED_GLOBAL`.
**Branch:** `cp-0165-4h-archive-audit`
**Frozen CP-0040 rulebook SHA-256:** `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`

## 1. उद्देश्य और स्रोत

यह bounded reconciliation पहले से committed evidence को जोड़ता है; कोई archive/source rescan नहीं किया गया। प्रमुख inputs:

- `evidence/source_adjudication/CP0107_Derived_996_Row_Worklist_Summary.json`, Git blob `9f5988febc993cb13f5feb31e6aa808f4b983607`
- `evidence/source_adjudication/CP0107_Unmatched_909_Provenance_Audit_Summary.json`, Git blob `fe51b63f1fb54c5077d844e635e73aceb96f16e1`
- `evidence/source_adjudication/CP0107_Unmatched_909_Distribution_Gate_Triage_Summary.json`, Git blob `018c59260e6d3a6fb69ddd9c6425cac92b464b4a`
- `evidence/source_adjudication/CP0107_CP0041_Worklist_Disposition_Delta_Summary.json`, Git blob `5296bfd9e6a0c341100893f001c85861234e264b`
- `evidence/source_adjudication/CP0107_CP0041_AggregationBucket_Summary.json`, Git blob `08221ec6baab7257b61f803fe78064cc26717ef5`
- `evidence/source_adjudication/CP0107_CloseTimeOnly_FieldDisposition_Final_Summary.json`, Git blob `5354cf3df24a747a8f098ca0f9d39e277a6b40e1`
- `docs/CP0259_G0_Unresolved_Population_Candidate_Impact_Reconciliation_HI.md`, Git blob `ce36368b7b61a32d6e6ce31b8a1bae2e620c231c`
- `docs/CP0260_Unmatched_909_Exact_Interval_Census_HI.md`, Git blob `cec2f53ba41983be0ce889be6b551947c7618719`
- `docs/CP0261_Unmatched_909_Candidate_Interval_Dependency_Crosswalk_HI.md`, Git blob `f4edbb5f69f9397bc593275fa4fdd801b05c2013`

## 2. 996-record worklist partition

CP-0107's validated derived worklist reports 996 source records and 996 derived records; its 22 checks passed, with 450 scoped disposition changes and 546 unchanged rows. The frozen member-type counts reconcile arithmetically:

| Worklist member type | Count | Reconciliation |
|---|---:|---|
| `DAILY_ONLY_ROW` | 452 | Part of unmatched population |
| `MONTHLY_ONLY_ROW` | 457 | Part of unmatched population |
| **Unmatched exact-open-key rows subtotal** | **909** | 452 + 457 |
| `SHARED_OPEN_VALUE_CONFLICT` | 60 | Count aligns with 52 economic conflicts + 8 close-time-only conflicts |
| `RESIDUAL_AGGREGATION_BUCKET` | 11 | Count aligns with 11 aggregation blockers |
| `MISSING_DAILY_REFERENCE_ACQUISITION` | 16 | Distinct date-level reference-acquisition records for 5m/15m/30m/1h; statuses say `NOT_ACQUIRED_BLOCKED_EXTERNAL_NETWORK`. They are not the 16 missing 4h gap-only slots. |
| **Total worklist records** | **996** | **909 + 60 + 11 + 16 = 996** |

This is a validated **count partition**, not proof that every cross-population relationship is adjudicated. The 996 derived worklist validation says all non-disposition fields and source JSON were preserved; it does not establish canonical historical source authority.

## 3. Subset and overlap register

| Population / relationship | Decision |
|---|---|
| 450 February-2018 off-grid rows | Explicitly a subset of the 909 unmatched rows; do not add as 450 new cases. |
| 7 December-2020 monthly-only residual keys | The 909 census records 7 monthly-only rows on 2020-12-21; treat them within the unmatched population, not as an extra 7, unless a future key-level ledger disproves identity. |
| 52 shared economic conflicts + 8 close-time-only conflicts | Counts reconcile to the 60 shared-conflict worklist category. All remain open; count reconciliation does not authorize source selection. |
| 11 aggregation blockers | Count reconciles to 11 residual aggregation buckets; all remain unresolved. |
| 17 missing 4h slots | Existing evidence says one overlaps the already-counted 4h placeholder row and 16 are gap-only. Do not count 17 as 17 additional unmatched rows. |
| 16 `MISSING_DAILY_REFERENCE_ACQUISITION` records vs 16 gap-only 4h slots | **Distinct scope, not a same-count join.** FETCHREF records are date-level acquisition blockers on 5m/15m/30m/1h; the 16 gap-only items are 4h open-time slots. Keep these ledgers separate. |
| 909 unmatched rows vs candidate builder | CP-0261 maps intervals to candidate families, but exact full-builder row consumption after an authorized gate transition remains unverified. |

## 4. What this action actually resolves

- The 996-record worklist's top-level count partition is reconciled without double-counting the 450 off-grid subset.
- The December seven are accounted for within the dated unmatched census population, not added on top of 909.
- The 60 shared-conflict count and 11 aggregation-bucket count reconcile to the separately reported blocker families.
- A cross-ledger scope distinction is now explicit: the 16 \`FETCHREF-*\` records are date-level acquisition blockers for 5m/15m/30m/1h (e.g. 2017-12-04, 2018-02-05, 2018-03-04); they are not the 16 4h gap-only slots. Equal count is coincidental and must not be treated as an identity join. The gap ledger remains its own population.
- This identifies the next useful internal verification task; it does not re-run exhausted archive scans or change any source row.

## 5. G0 decision boundary

No canonical source was selected. No source case was closed. No Policy B application was authorized or applied. No raw row, timestamp, archive, or rulebook was changed. No candidate build or market backtest was run.

- Canonical historical source: `NONE`
- G0: `BLOCKED_GLOBAL`
- G2: 23 candidates `FAIL`
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- Profitability: `NOT ESTABLISHED`
- Candidate build / acceptance-grade backtest: `BLOCKED`
- Live signing / broadcast / exchange orders: `BLOCKED`

**Next atomic action:** reconcile the 16 date-level FETCHREF acquisition blockers against their existing daily-reference acquisition queue and archive manifest to determine whether acquisition has since been completed. Keep the 16 gap-only 4h slots separate. If acquisition evidence is absent, preserve `NOT_ACQUIRED_BLOCKED_EXTERNAL_NETWORK` / `MISSING_EVIDENCE`; do not repeat exhausted full archive scans. The remaining G0 decision-changing dependency is admissible official key-specific historical-version evidence or an actually authorized independent written adjudication.
