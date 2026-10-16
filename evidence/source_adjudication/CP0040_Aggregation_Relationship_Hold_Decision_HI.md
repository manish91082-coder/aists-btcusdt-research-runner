# CP-0040 Aggregation Relationship Hold Decision — 2026-10-16

## Decision
**HOLD: all 11 cross-interval aggregation relationship cases remain OPEN. G0 remains BLOCKED_GLOBAL. Candidate eligibility remains BLOCKED.**

This is a conservative evidence disposition, not a root-cause finding and not a source-case closure.

## Evidence reviewed
- Current manifest pointer: `evidence/source_adjudication/CP0040_Current_Manifest.json`.
- Current manifest run: 38883792900.
- Manifest: 1,427 rows / 1,427 unique exact keys; SHA-256 `e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a`.
- Aggregation evidence: 78 records, 11 buckets, 35 unique exact keys. All 35 parent/child keys are represented in the manifest.
- In all 11 buckets, daily child rollups match the daily parent; the monthly mismatch signature persists.
- Current non-row blocker ledger has 11 unresolved `RESIDUAL_AGGREGATION_BUCKET` cases.
- Gate regression run 38883871540 completed successfully: runner 11/11 PASS; builder gate tests 5/5 PASS. The gate refuses candidate build while the 11 non-row blockers remain.

## Frozen-policy boundary
The previously verified CP-0040 rulebook hash is `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`. The available prior status records state that unexplained or signal-influencing source conflicts must remain unresolved or be explicitly quarantined. That does **not** by itself prove that exact-key row quarantine is sufficient to close a cross-interval relationship blocker or open G0.

The full rulebook bytes are not present as a standalone file in this repository tree, and this checkpoint does not claim a clause-by-clause revalidation of the original package. Therefore no policy authority is inferred beyond the evidence already recorded. A formal clearance requires the exact frozen rulebook text plus an explicit mapping from its G0 criteria to these relationship-level cases, or new source evidence that resolves the monthly mismatch.

## Disposition
- All 11 relationship cases: `OPEN_NOT_ESTABLISHED`.
- Root cause: `NOT_ESTABLISHED`.
- Source authority: `NONE`.
- Canonical source selections: 0.
- Source cases closed by this checkpoint: 0.
- Candidate build / backtest: NOT RUN.
- Strategy promotion: NOT performed.
- Live signing, public broadcast, and exchange orders: BLOCKED.

## Next bounded action
Retrieve the exact frozen CP-0040 rulebook from the verified CP-0041 authority package and record a clause-level G0 crosswalk for each of the 11 relationship cases. If the exact bytes cannot be retrieved, preserve this HOLD and do not infer clearance from row-level quarantine alone. Do not redownload archives, repair candles, shift timestamps, select a canonical source, build candidates, or run a backtest as part of this step.

## References
- Current manifest pointer: https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/evidence/source_adjudication/CP0040_Current_Manifest.json
- Aggregation quarantine report: https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/evidence/source_adjudication/CP0040_Aggregation_Bucket_ExactKey_Quarantine_Report_HI.md
- Gate regression run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38883871540


---

## Amendment 1 — exact frozen rulebook recovered and clause-level crosswalk (2026-10-16)

The verified CP-0041 authority package was materialized from the conversation file `AISTS_CP0041_Row_Level_Evidence_Disposition_Pack.zip`. Verification reproduced:
- Package SHA-256: `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`.
- ZIP CRC test: PASS.
- Embedded `AISTS_CP0040_Strategy_Acceptance_Rulebook_HI.md` SHA-256: `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`, exact match to the frozen hash already recorded.

### Direct rulebook mapping
- **G0 clause 18:** every cross-timeframe aggregation conflict needs a disposition; until source adjudication, mark the item `UNRESOLVED` and run quarantine sensitivity separately from signal-influence research.
- **G0 clause 19:** PASS is possible only if no unresolved item can affect the selected candidate's actual signal/position/valuation inputs, **or** each unresolved item is explicitly quarantined **and final metrics are based on that quarantine policy**.
- **G3 clause 38:** source-policy/quarantine sensitivities must be shown; material metric differences keep the data gate open unless the source is adjudicated or the conservative quarantine policy is frozen.

### Row-level crosswalk result
The actual `AISTS_CP0041_Residual_Aggregation_Bucket_Disposition.csv` has 11/11 cases still `UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT`. All 11 have verified monthly archive/raw rows and saved candidate values, but exact-date official daily reference availability is `False` for 11/11. Public evidence grades: 3 `SAME_DATE_CONTEXT_ONLY`, 2 `MONTH_CONTEXT_ONLY`, 6 `NO_MATCH`. Each closure requirement calls for exact-date official daily ZIP/checksum evidence for both child and parent intervals, then reconciliation of the UTC bucket and OHLCV/trade count, without correction before attribution.

### Final interpretation
The rulebook does **not** require every source conflict to be causally resolved before any diagnostic can occur. It does, however, require the quarantine policy to be explicit and final metrics to be based on that policy before using the G0 quarantine alternative as a PASS. Current evidence proves exact row-key quarantine coverage, but no candidate build/backtest or final metrics under the current 1,427-key quarantine manifest have been run. Therefore the 11 relationship blockers remain open, G0 remains `BLOCKED_GLOBAL`, and no candidate build/backtest is authorized by this checkpoint.

The earlier statement that the full rulebook bytes were not available as a standalone repository file remains true for the GitHub tree; the exact frozen bytes have now been independently recovered from the verified authority package and hash-checked. This amendment supersedes any implication that the rulebook itself is still unavailable.
