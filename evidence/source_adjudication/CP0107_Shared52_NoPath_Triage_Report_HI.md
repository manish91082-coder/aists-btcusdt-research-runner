# CP-0107: 19 unmatched official-bundle paths triage (read-only)

**Status:** `PASS_EXISTING_CROSSWALK_TRIAGED_SOURCE_AUTHORITY_OPEN`  
**Purpose:** Reconcile the 19 cases where the already inspected official correction bundle had no exact daily archive path. This is a read-only classification of committed evidence, not a new archive fetch or source adjudication.

## Frozen inputs

- Source: `evidence/source_adjudication/CP0107_Shared52_RowValue_VersionCrosswalk.csv`
- Source Git blob SHA-1: `acbdf6fc6e161cbf18abde221a050701e88a9c01`
- Source rows: 52 data rows; selected rows: 19 where `exact_official_daily_path_found != True`.
- Source values retain monthly/daily raw row JSON, recorded archive SHA-256 values, field-level differences and existing disposition.

## Date-group triage

| UTC date | Cases | Intervals | Exact path in this bundle | Interpretation |
|---|---:|---|---|---|
| 2018-02-11 | 1 | 1h | 0/1 | No exact path in this one bundle; not proof that daily archive is unavailable or invalid. |
| 2020-12-21 | 13 | 15m, 1h, 30m, 5m | 0/13 | No exact path in this one bundle; not proof that daily archive is unavailable or invalid. |
| 2021-01-21 | 2 | 1d, 4h | 0/2 | No exact path in this one bundle; not proof that daily archive is unavailable or invalid. |
| 2021-09-23 | 1 | 5m | 0/1 | No exact path in this one bundle; not proof that daily archive is unavailable or invalid. |
| 2021-12-24 | 2 | 1d, 4h | 0/2 | No exact path in this one bundle; not proof that daily archive is unavailable or invalid. |

## Observations

- All 19 selected rows already carry `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION` in the source crosswalk. This triage does not alter dispositions.
- Group sizes: 2018-02-11: 1; 2020-12-21: 13; 2021-01-21: 2; 2021-09-23: 1; 2021-12-24: 2.
- “No exact path in bundle” means only that this specific correction bundle did not contain that exact member path. It does not mean the daily archive does not exist, and it does not establish which archive version is authoritative.
- For every selected case: canonical source `NONE`, root cause `OPEN_NOT_ESTABLISHED`, case closed `false`. No source rows changed, no timestamp shift/rounding, no merge/replacement/deletion, no synthetic candles, no backtest or strategy promotion.

## Next decision

Do not close any of these 19 cases based on bundle absence. Next inspect source provenance/coverage only where existing verified archive bytes and exact-key evidence are already available; otherwise retain `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION` and identify the precise missing evidence needed. Fresh raw-byte verification of the standalone CP-0040 rulebook remains `NOT_VERIFIED`.
