# CP-0263: resolve the 16 daily-reference acquisition blockers using existing CP-0107 evidence (Hindi)

**स्थिति:** DAILY-REFERENCE ACQUISITION SUBTASK RESOLVED FOR ALL 16 QUEUED ITEMS; ROW/SOURCE ADJUDICATION STILL OPEN; G0 STILL `BLOCKED_GLOBAL`.
**Branch:** `cp-0165-4h-archive-audit`
**Frozen CP-0040 rulebook SHA-256:** `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`

## 1. निर्णय क्यों लिया गया

CP-0262 ने सही किया कि 16 `FETCHREF-*` items date-level acquisition blockers for 5m/15m/30m/1h हैं, 16 missing 4h gap slots नहीं। अगला कदम उन्हीं committed artifacts को जाँचना था कि acquisition बाद में पूरी हुई या नहीं। यह bounded check मौजूदा CP-0107 package पर हुआ; कोई नया archive scan/download नहीं किया गया।

## 2. Exact evidence और verification

- Daily-reference acquisition summary: `evidence/source_adjudication/CP0107_Run_38909366995/CP0107_CP0041_DailyReference_Acquisition_Summary.json`, blob `3d689b99913383c57868de170cdd7e757e46f140`.
- Exact 16-row archive manifest: `evidence/source_adjudication/CP0107_Run_38909366995/CP0107_CP0041_DailyReference_Archive_Manifest.csv`, blob `1a1a264923b12bd8d8f38c362a4fe7f32b871356`.
- Frozen queue snapshot: `evidence/source_adjudication/CP0107_Run_38909366995/CP0107_CP0041_DailyReference_Queue_Snapshot.csv`, blob `7e3b3231351a6afc946befa81d78113e6b41002f`.
- Per-period exact-row summary: `evidence/source_adjudication/CP0107_Run_38909366995/CP0107_CP0041_DailyReference_Period_Summary.csv`, blob `34b1dfa89b3618f455aaa655a54e797ecea1388e`.
- Source manifest's daily-reference raw row comparison is recorded as blob `1fa303ba60a6fdbee009435db2bba0f3fc788406`; the large CSV did not return through the text file endpoint in this check, so row-level claims here are limited to the readable per-period summary and acquisition summary.

Verified from the committed manifest and summary:
- 16/16 unique `FETCHREF` case IDs present.
- 16/16 daily ZIP retrieval status HTTP 200; 16/16 ZIP CRC `PASS`; 16/16 SHA-256 matches recorded sidecar; 16/16 sidecar token matches ZIP SHA.
- CP-0107 acquisition summary reports 98/98 checks `PASS` and `PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED`.
- The old queue snapshot records `NOT_ACQUIRED_BEFORE_THIS_RUN; OPEN_PENDING_EXACT_ROW_COMPARISON`. That is a historical pre-run status, superseded for acquisition only by the later verified manifest. It is not a source-case closure.

## 3. Row-comparison outcomes across the 16 periods

The committed period summary contains 16 unique FETCHREF periods. Recomputed totals from its 16 rows:

| Measure | Verified total |
|---|---:|
| Periods with complete expected grid | 14 / 16 |
| Periods still open for coverage review | 2 / 16 |
| Shared open-time keys | 1,982 |
| Exact raw row pairs | 1,550 |
| Divergent raw row pairs | 432 |
| Economic-field divergent pairs | 14 |
| Daily-only open keys | 0 |
| Monthly-only open keys | 10 |
| Expected daily grid keys absent | 10 |
| Close-time-only pairs | 0 |

The two periods still open for coverage review are:
- `FETCHREF-15m-2017-12-04`: daily 94 rows vs monthly 96; 2 monthly-only keys; 2 expected daily grid keys absent.
- `FETCHREF-5m-2017-12-04`: daily 280 rows vs monthly 288; 8 monthly-only keys; 8 expected daily grid keys absent.

The other 14 periods have complete expected-grid coverage, but complete coverage is not the same as row equality: 432 raw row pairs diverge, including 14 economic-field divergent pairs. All 16 per-period dispositions remain `OPEN_REVIEW_REQUIRED; archive hash verified but row equality and source authority are not presumed`.

## 4. What is now solved, and what is not

Solved:
- The 16 date-level acquisition tasks are no longer missing acquisition evidence; official URL/sidecar references, archive SHA, CRC, schema/date checks and exact period-level diagnostics are persisted.
- The old queue status is reconciled as historical pre-acquisition status, not current acquisition truth.
- The 16 acquisition records are kept separate from the 16 gap-only 4h slots.

Not solved:
- Historical authority between monthly and daily bytes.
- The 432 divergent raw row pairs, 14 economic-field divergent pairs, and 10 monthly-only keys / missing daily expected keys.
- Whether these period-level findings overlap other frozen source-case populations; do not add or merge counts without an exact-key join.
- Any candidate's full builder signal/position/valuation impact.
- G0-A through G0-E.

## 5. Final gate decision

No canonical source selected; no source case closed; no Policy B authorization/application; no raw archive or row modified; no candidate build or market backtest; no strategy promotion or profitability claim.

- G0: `BLOCKED_GLOBAL`
- G2: 23 candidates `FAIL`
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- Profitability: `NOT ESTABLISHED`
- Candidate build / acceptance-grade backtest: `BLOCKED`
- Live signing / broadcast / exchange orders: `BLOCKED`

**Next atomic action:** exact-key reconcile the 10 monthly-only keys and 14 economic-field divergent pairs in this 16-period package against the frozen CP-0041/CP-0107 case ledger and candidate-input relevance matrix. Record only exact intersections; preserve all unresolved source cases as open. This improves population attribution but cannot create historical authority. Do not repeat acquisition or full archive scans.
