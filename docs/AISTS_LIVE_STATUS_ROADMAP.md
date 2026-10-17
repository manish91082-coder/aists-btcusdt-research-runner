# AISTS Live Status & Mission Roadmap

Last verified checkpoint: **CP-0203 (pinned fail-closed gap-policy gate; static CI PASS)**  
Branch: `cp-0165-4h-archive-audit`  
Research target: BTCUSDT historical-data provenance and risk-adjusted strategy validation  
Current global gate: **G0 = BLOCKED_GLOBAL**

## Latest verified GitHub runs

- Read-only execution pipeline through CP-0201: [run 39062577687](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39062577687), completed successfully.
- CP-0203 static CI including the new gap-policy gate tests: [run 39063641701](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39063641701), terminal `success` on tested SHA `c996807b8bffc247b991d9d82b45d20d02d425be`.
- Latest execution evidence through CP-0201: [run 39062577687](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39062577687), completed successfully; execution commit `b6b16ab2da9111e4a44a67c5c6d091b46729b8d3`.
- CP-0203 CI compiles CP-0026 and CP-0203 and runs seven CP-0203 gate tests; the separate CP-0040 gate test suite is still not wired into this workflow.
- The PR remains open and unmerged; `main` remains at `f2fcc6f2e74dcd08e59cdcb811cd680d35fb1733`.

## Verified findings

### CP-0165: 4h monthly archive integrity

- 110/110 monthly 4h archives matched recorded official SHA-256 checksum sidecars; ZIP CRC validation: 110/110.
- 19,974 raw 4h candle rows inspected.
- 9 gap events contain 17 missing 4h open-time slots.
- Duplicate 4h open timestamps: 0; off-grid 4h open timestamps: 0.

### CP-0192/0194/0196: cache-only 5m/1h triage

- Inspected 18 existing child archives: 5m and 1h monthly archives across 9 months. No archive was missing; ZIP CRC and timestamp-unit checks passed.
- 10 slots had both child archives grid-valid, but neither interval had an open timestamp inside the missing 4h window.
- The other 7 slots fall in February 2018. The cached `BTCUSDT-5m-2018-02.zip` has 241 off-grid open timestamps and `BTCUSDT-1h-2018-02.zip` has 43; duplicates: 0. Both archives are excluded from coverage claims.
- Result: `REVIEW_REQUIRED_CACHE_COVERAGE_INCOMPLETE`.

### CP-0197: prior February 2018 evidence linkage

- The committed CP-0107 daily-coverage and off-grid CSV files were hash/byte checked against their extraction summary: 2/2 PASS.
- 5 missing slots on 2018-02-08 have no daily-reference evidence in CP-0107's scope.
- The 2018-02-09 00:00 and 04:00 UTC windows are not covered by the existing daily-reference rows; the first 5m and 1h rows in that evidence begin at 10:00 UTC.
- CP-0107 records 450 monthly off-grid rows across 5m/15m/30m/1h. Its monthly hashes were recorded CP-0106 manifest references, not fresh official monthly sidecar validation.

### CP-0198/0199: frozen daily-reference exact-key comparison

- 10/10 daily 4h reference archives passed frozen-inventory SHA/bytes, ZIP CRC, timestamp-unit and grid checks.
- Of the 17 missing 4h keys, 1 exact key is present in a verified daily-reference archive and 16 are absent from both monthly and daily cached archives.
- The sole discrepancy is `2017-09-06T16:00:00Z`: monthly 4h archive lacks the key; daily reference contains OHLC all equal to 4619.43, zero base/quote volume, zero trades, and close time equal to open time. It is classified `ZERO_TRADE_PLACEHOLDER` with an invalid 4h close-time span.
- Monthly 4h neighbors are 12:00 and 20:00 UTC. The daily placeholder is a source-key discrepancy, not an accepted market candle or a canonical-source decision.

### CP-0200: frozen G0 rulebook disposition

- The CP-0040 rulebook hash/bytes matched its frozen receipt: SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`, 10,630 bytes.
- 17 missing slots dispositioned: 16 `UNRESOLVED_MISSING_KEY_BOTH_SOURCES`; 1 `UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT`.
- A gap-quarantine recommendation was generated but has not been applied to the candidate builder.
- Result: `BLOCKED_G0_UNRESOLVED_GAP_AND_SOURCE_ITEMS`.

### CP-0201: overlap crosswalk against existing row-level ledgers

- All 17 gap dispositions were crosswalked by exact interval + raw open-time key against the frozen CP-0040 quarantine manifest and CP-0107 worklist, February-2018, shared-52 and close-time-only ledgers.
- **1 exact-key overlap** found: `2017-09-06T16:00:00Z` already exists as `UNMATCHED-D-4h-1504713600000` in the CP-0040 quarantine manifest. No duplicate row-level case was created.
- **16 gap-window-only items** do not have a row-level key in the inspected ledgers. They must remain gap-policy entries, not fabricated row cases.
- No source case was closed; no quarantine was applied to the candidate builder. Crosswalk status: `PASS_EXACT_KEY_CROSSWALK_COMPLETE_G0_STILL_BLOCKED`.

## Historical checkpoint: CP-0202

The source-code-only eligibility matrix is preserved in [docs/CP0202_Candidate_Builder_Eligibility_Matrix.md](CP0202_Candidate_Builder_Eligibility_Matrix.md). Its findings directly motivated CP-0203. No candidate build or backtest was run.

## Goal distance / gate status

- G0: `BLOCKED_GLOBAL`; canonical source: `NONE`; source cases closed: 0.
- G2: all 23 current strategy candidates remain historical-screen FAIL; no strategy approved.
- G3: quarantine sensitivity/source adjudication unresolved.
- G4: insufficient forward/out-of-sample evidence.
- G6: adaptive AI validation not built.
- G7: live signing, broadcast, and orders remain `BLOCKED`.
- Profitability: **NOT ESTABLISHED**.

A green GitHub Actions run confirms the bounded audit program and tests executed successfully. It does not establish source authority, clear G0, or prove profitability.


## CP-0202: Candidate Builder Eligibility Matrix (source-code-only)

- Matrix: [docs/CP0202_Candidate_Builder_Eligibility_Matrix.md](CP0202_Candidate_Builder_Eligibility_Matrix.md).
- CP-0199 artifact downloaded and inspected: 17 keys; 20/20 scoped archives validate against the frozen inventory and prior integrity evidence. One daily-only zero-trade placeholder conflict; 16 keys absent from both inspected cached sources.
- CP-0200/0201 reconciliation: 16 unresolved missing-key gap windows and one unresolved placeholder conflict; one exact-key overlap links to existing case `UNMATCHED-D-4h-1504713600000`; no duplicate case created.
- Code inspection: CP-0026 exact-key row quarantine exists, but its gate only checks the manifest SHA against the accompanying mutable summary and does not consume CP-0200/0201 gap-policy evidence. Gap events are recorded, not independently enforced as a candidate-eligibility policy. CP-0026/CP-0040 gate tests are not wired into current static CI.
- Decision: no candidate build or backtest. Preserve the current fail-closed behavior and all 11 non-row blockers. The 17-item gap policy must be integrated into a pinned, tested eligibility gate before any future candidate build.
- Files changed in CP-0202: `docs/CP0202_Candidate_Builder_Eligibility_Matrix.md` (file commit `fae7dfc8538182def93eae0396a71076848e47a0`); roadmap checkpoint entry first recorded in commit `0ecbe8524b43cf852c71eb4bc4eb26c5d00d5627`.
- CP-0202 documentation-check CI: [run 39063150692](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39063150692), terminal `success` (all 1 job and all 11 steps completed), run head SHA `0ecbe8524b43cf852c71eb4bc4eb26c5d00d5627`. This validates the existing static test suite and roadmap trigger, not CP-0026/CP-0040 gate integration, which is not wired into CI. A subsequent metadata-only roadmap correction is on the current branch head; do not imply the run tested that later SHA.
- Checkpoint code changes: none. Source authority: `NONE`; G0: `BLOCKED_GLOBAL`; source cases closed: 0; strategy promotion: false; profitability: **NOT ESTABLISHED**.
- Review boundary: matrix review precedes any CP-0026 gate implementation. Next bounded action after review: implement the minimal fail-closed gap-policy gate and regression tests; keep candidate build/backtest disabled.
- Safety: live signing, broadcast, and exchange orders remain `BLOCKED`.


## CP-0203: Pinned fail-closed gap-policy gate

- Added `scripts/AISTS_CP0203_GapPolicy_Gate.py`; frozen CP-0200 recommendation SHA-256 is pinned to `e59c95764d4db76a8a707d07526d44b2b7e3487c534687584bd9936a5742b3bf`; CP-0201 crosswalk SHA-256 is pinned to `de8d829f405aa60f83e43744d4c281469fec6acb9bb99cfe6aa8823c8509be56`.
- Gate checks required files, both exact CSV hashes, CP-0200/0201 summary identity/status/counts, all 17 exact 4h keys, one existing overlap (`UNMATCHED-D-4h-1504713600000`), and 16 gap-window-only items. It rejects source selection, case closure, duplicate rows, and any evidence claiming the recommendation was applied.
- Integrated the gate into `scripts/AISTS_CP0026_Research_Candidate_Builder.py` before the existing row-level gate and before candidate output directory creation. Missing evidence, changed hashes, or still-unresolved gap policy block the candidate build.
- Added `tests/test_cp0203_gap_policy_gate.py` and wired the module/builder compilation plus CP-0203 tests into the static workflow.
- CI: [run 39063641701](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39063641701) terminal `success`; compile step, all prior test steps, and CP-0203 fail-closed gate tests passed on tested SHA `c996807b8bffc247b991d9d82b45d20d02d425be`.
- Scope boundary: gate tests use synthetic deterministic fixtures plus pinned constants; no candidate build/backtest was run and no source was promoted. The gate intentionally remains blocking even after evidence validation because the current frozen policy is only recommended, not applied.
- Current branch commit for CP-0203 gate integration: `c996807b8bffc247b991d9d82b45d20d02d425be`; this roadmap update is a separate documentation commit and will receive its own CI run.
- Next bounded action: inspect terminal CI for the roadmap update, then perform a source-only audit of whether an explicit, reviewable gap-window quarantine policy can be defined without inventing bars or choosing a canonical source. Keep G0 blocked until that policy is evidence-backed.
- Safety: canonical source `NONE`; source cases closed: 0; strategy promotion false; live signing/broadcast/orders `BLOCKED`; profitability **NOT ESTABLISHED**.
