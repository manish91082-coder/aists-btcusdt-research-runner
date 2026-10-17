# AISTS Live Status & Mission Roadmap

Last verified checkpoint: **CP-0201**  
Branch: `cp-0165-4h-archive-audit`  
Research target: BTCUSDT historical-data provenance and risk-adjusted strategy validation  
Current global gate: **G0 = BLOCKED_GLOBAL**

## Latest verified GitHub runs

- Read-only execution pipeline through CP-0201: [run 39062577687](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39062577687), completed successfully.
- Latest static CI including CP-0201 overlap-crosswalk tests: [run 39062614659](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39062614659), completed successfully.
- Execution commit: `b6b16ab2da9111e4a44a67c5c6d091b46729b8d3`.
- Static-test commit: `12e932a5dff9570640bfc32dd77159c54dd4a372`.
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

## Next bounded action: CP-0202

1. Inspect the existing CP-0026 candidate builder and its deterministic tests for exact-key exclusion, missing-bar/gap-window handling, and fail-closed behavior.
2. Compare builder behavior against the frozen CP-0040 G0 rulebook and the existing 909 unmatched rows, 52 shared economic conflicts, 8 close-time-only cases, 450 February-2018 off-grid subset, and this 17-slot gap crosswalk. Do not double-count overlapping cases.
3. Produce a source-code-only eligibility matrix: implemented / missing / not tested, with exact file and line references. No candidate build or backtest.
4. Only after the matrix is reviewed should the next implementation step patch a fail-closed gate. The current quarantine recommendation remains unapplied.

## Goal distance / gate status

- G0: `BLOCKED_GLOBAL`; canonical source: `NONE`; source cases closed: 0.
- G2: all 23 current strategy candidates remain historical-screen FAIL; no strategy approved.
- G3: quarantine sensitivity/source adjudication unresolved.
- G4: insufficient forward/out-of-sample evidence.
- G6: adaptive AI validation not built.
- G7: live signing, broadcast, and orders remain `BLOCKED`.
- Profitability: **NOT ESTABLISHED**.

A green GitHub Actions run confirms the bounded audit program and tests executed successfully. It does not establish source authority, clear G0, or prove profitability.
