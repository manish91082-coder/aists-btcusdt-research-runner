# CP-0107 Unmatched-909 Distribution and Gate Triage (Hindi)

**तारीख:** 16 अक्टूबर 2026  
**स्थिति:** FROZEN LEDGER HASH VERIFIED; 909/909 ROWS CONSISTENT  
**निर्णय:** Same 909-row provenance loop बंद; source attribution अभी खुला है।

## 1. Input byte verification

Library file `/AISTS/CP0107/unmatched_provenance/CP0107_CP0041_Unmatched_909_Provenance_Audit.csv` को materialize कर वास्तविक bytes पर SHA-256 निकाला:

- Bytes: **963,228**
- SHA-256: `b8ffd2a98f9296fdb04a2296f2190caca5387bbb286185a564717aadcb40d980`
- Stored audit summary से hash match: **PASS**
- Rows: **909**, unique case IDs: **909**

यह GitHub repository में मौजूद file होने का दावा नहीं है; यह verified Library artifact है।

## 2. Row-level invariant checks

वास्तविक 909-row CSV पर जाँच:

- Record type: **452 DAILY_ONLY_ROW**, **457 MONTHLY_ONLY_ROW**
- Monthly manifest hash reference match: **909/909**
- Daily manifest + sidecar reference match: **909/909**
- Source-specific raw JSON hash/reference equality: **909/909**
- Frozen worklist key/raw JSON exact match: **909/909**
- Existing disposition equals frozen worklist disposition: **909/909**
- Exact counterpart status: **909/909 `ABSENT_BY_FROZEN_EXACT_OPEN_KEY_JOIN`**
- Canonical source `NONE`: **909/909**
- Root cause `OPEN_NOT_ESTABLISHED`: **909/909**
- Case closed `FALSE`: **909/909**
- No shift/round/merge/replace/delete flag true: **909/909**

## 3. Distribution by UTC date

| UTC date | Daily-only | Monthly-only | Total |
|---|---:|---:|---:|
| 2017-09-06 | 5 | 0 | 5 |
| 2018-02-09 | 266 | 270 | 536 |
| 2018-02-10 | 168 | 168 | 336 |
| 2018-02-11 | 13 | 12 | 25 |
| 2020-12-21 | 0 | 7 | 7 |
| **Total** | **452** | **457** | **909** |

**897/909 unmatched rows (98.68%)** are concentrated on 2018-02-09 through 2018-02-11. This is a concentration summary of frozen exact-key joins, not evidence that timestamps should be shifted. The 450 off-grid February monthly rows already have their own cache-only extraction/coverage evidence and must not be rounded or merged into daily rows. The remaining seven monthly-only 2020-12-21 rows already have a separate exact-key audit and stay unresolved.

## 4. Interpretation: stop repeating the same audit

The ledger/manifest provenance audit is complete for its defined scope. It proves the frozen references are internally consistent, but it does **not** independently re-download/re-parse all monthly and daily ZIPs and does not identify which upstream series is canonical.

Decision:
- Disposition remains `UNMATCHED_ROW_QUARANTINE_PENDING_SOURCE_ATTRIBUTION` for all 909.
- Canonical source selected: **0**
- Cases closed: **0**
- Root cause: `OPEN_NOT_ESTABLISHED`
- No raw data mutation, timestamp normalization, synthetic candles, backtest rerun, or strategy promotion.

## 5. Next gate decision

Do not rerun this 909-row audit or the already inspected 2022-08-08 correction bundle. The available evidence has reached its limit for source attribution. Unless another distinct, official source/version record is already present in the frozen artifacts, treat the unmatched keys as a **documented data limitation** and keep G0 blocked. The next research work must not use quarantined rows or claim an accepted canonical dataset; proceed only with a separate candidate-data eligibility review under the frozen CP-0040 acceptance rulebook.

Gates unchanged: G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.
