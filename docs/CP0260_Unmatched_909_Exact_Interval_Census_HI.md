# CP-0260: 909 unmatched-row exact interval census and G0 impact boundary (Hindi)

**स्थिति:** INTERVAL CENSUS VERIFIED; G0 STILL `BLOCKED_GLOBAL`.  
**Scope:** use the already-existing CP-0107 909-row provenance audit export to close the repository's missing interval-distribution fact. No archive rescan, no raw market-data change, no candidate build/backtest.  
**Frozen CP-0040 rulebook SHA-256:** `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.  
**Audit export SHA-256:** `b8ffd2a98f9296fdb04a2296f2190caca5387bbb286185a564717aadcb40d980`; matches CP-0107 provenance summary's recorded output SHA-256 and 909-row count.

## 1. Source and deterministic checks

- Source artifact: `CP0107_CP0041_Unmatched_909_Provenance_Audit.csv`, the existing CP-0107 Library export referenced by `CP0107_Unmatched_909_Provenance_Audit_Summary.json`.
- Parsed shape: 909 rows × 32 columns.
- Exact-key uniqueness: 909/909 unique `(interval, open_time_ms)` pairs.
- All 909 rows: monthly manifest match = true; daily manifest match = true; source JSON matches side-row JSON = true; worklist key/raw JSON match = true; worklist disposition match = true; no shift/round/merge/replace/delete = true.
- Existing disposition remains unchanged: 909/909 `UNMATCHED_ROW_QUARANTINE_PENDING_SOURCE_ATTRIBUTION`; exact counterpart absent 909/909; canonical source `NONE` 909/909; `case_closed=False` 909/909.

These checks establish row/manifest/worklist consistency, not historical publication/version authority.

## 2. Exact interval census

| Interval | Daily-only | Monthly-only | Total |
|---|---:|---:|---:|
| 5m | 241 | 245 | 486 |
| 15m | 81 | 82 | 163 |
| 30m | 86 | 86 | 172 |
| 1h | 43 | 44 | 87 |
| 4h | 1 | 0 | 1 |
| **Total** | **452** | **457** | **909** |

The interval totals reconcile exactly to 909. There are 908 unmatched rows across 5m/15m/30m/1h and exactly one unmatched 4h row. No 1d row occurs in this 909-row worklist.

## 3. The one 4h row and non-double-counting

The sole 4h row is `UNMATCHED-D-4h-1504713600000` at `2017-09-06T16:00:00Z`. It is the already-known daily-only flat-OHLC/zero-trade placeholder with invalid 4h close-time span. It is already linked by CP-0201 to the existing row-level case and the 17-slot gap disposition. **Do not count it as a new/additional gap case.** The remaining 16 CP-0200/0201 entries are gap-window-only items, not synthetic row cases.

## 4. Candidate-input impact boundary

- This census improves the prior unknown: the 909-row population's exact interval distribution is now available and hash-linked to the existing CP-0107 audit.
- The lone 4h row is a direct 4h input blocker and remains unresolved.
- The other 908 rows sit in lower-timeframe archives (5m/15m/30m/1h); they remain relevant to their matching lower-timeframe candidate inputs and do not become 4h rows by inference.
- The frozen CP-0115 exposure crosswalk still says exact row consumption in the new builder is `NOT_VERIFIED_NO_NEW_CANDIDATE_BUILD`. This census does **not** prove whether/how each exact key reaches a candidate's signal, position, or valuation path.
- CP-0203's hash-pinned gap-policy gate remains fail-closed; Policy B is not authorized/applied. No candidate build or acceptance-grade backtest is permitted.

## 5. Decision

This is a bounded evidence improvement, not source adjudication. No source selected, no case closed, no policy applied, no raw row altered, no candidate promoted.

- Canonical historical source: `NONE`
- G0: `BLOCKED_GLOBAL`
- G2: 23 candidates `FAIL`
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- Profitability: `NOT ESTABLISHED`
- Candidate build / acceptance-grade backtest: `BLOCKED`
- Live signing / public broadcast / exchange orders: `BLOCKED`

**Next single action:** update the live roadmap with this exact census and then verify CI's terminal result on the new exact HEAD. The remaining G0 decision-changing prerequisite is still qualifying official key-specific historical-version provenance or an actually authorized independent written adjudication. Do not infer either from hashes, this census, or CI.
