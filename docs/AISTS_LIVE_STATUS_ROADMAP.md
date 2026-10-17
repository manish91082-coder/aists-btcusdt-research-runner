# AISTS Live Status & Mission Roadmap

Last verified checkpoint: **CP-0200**  
Branch: `cp-0165-4h-archive-audit`  
Research target: BTCUSDT historical-data provenance and risk-adjusted strategy validation  
Current global gate: **G0 = BLOCKED_GLOBAL**

## Latest verified GitHub runs

- Read-only execution pipeline (CP-0165 through CP-0200): [run 39062441786](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39062441786), completed successfully.
- Latest static CI including CP-0200 G0 disposition tests: [run 39062447823](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39062447823), completed successfully.
- Execution commit: `856361aa3603a1ef4b5402cf71b4c641c26b0152`.
- Static workflow commit: `b88f588eade414aa263bf5a442e88a64e6ff9071`.
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
- Result: `REVIEW_REQUIRED_CACHE_COVERAGE_INCOMPLETE`. This is an archive/data finding, not a profitability result.

### CP-0197: prior February 2018 evidence linkage

- The committed CP-0107 daily-coverage and off-grid CSV files were independently hash/byte checked against their CP-0107 extraction summary: 2/2 PASS.
- 5 missing slots on 2018-02-08 have no daily-reference evidence in CP-0107's scope.
- The 2018-02-09 00:00 and 04:00 UTC windows are not covered by the existing daily-reference rows; the first 5m and 1h rows in that evidence begin at 10:00 UTC.
- The prior CP-0107 package records 450 monthly off-grid rows across 5m/15m/30m/1h. Its monthly hashes were a recorded CP-0106 manifest reference, not a fresh official monthly sidecar validation.

### CP-0198/0199: frozen daily-reference exact-key comparison

- 10/10 daily 4h reference archives were present and passed frozen-inventory SHA/bytes, ZIP CRC, timestamp-unit and grid checks.
- Of the 17 missing 4h keys, **1 exact key is present** in a verified daily-reference archive and **16 are absent** from both the monthly and daily cached archives.
- The sole exact-key discrepancy is `2017-09-06T16:00:00Z`: monthly 4h archive is missing that key; daily reference contains a row with OHLC all equal to 4619.43, zero base/quote volume, zero trades, and close time equal to open time. The row is classified `ZERO_TRADE_PLACEHOLDER` with an invalid 4h close-time span.
- Monthly 4h neighbors are 12:00 and 20:00 UTC. The daily placeholder is evidence of a source-key discrepancy, **not** an accepted market candle or a canonical-source decision.
- CP-0199 result: `REVIEW_REQUIRED_EXACT_KEY_SOURCE_CONFLICTS`.

### CP-0200: frozen G0 rulebook disposition

- The CP-0040 rulebook hash and byte count matched its frozen verification receipt: SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`, 10,630 bytes.
- 17 missing slots dispositioned: 16 `UNRESOLVED_MISSING_KEY_BOTH_SOURCES`; 1 `UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT`.
- A gap-quarantine recommendation manifest was generated, but it has **not** been applied to the existing candidate builder.
- CP-0200 result: `BLOCKED_G0_UNRESOLVED_GAP_AND_SOURCE_ITEMS`.

## Next bounded action: CP-0201

1. Crosswalk the 17 gap dispositions against the frozen CP-0041 worklist and CP-0107 row-level disposition ledger using exact interval + raw open-time key.
2. Detect overlaps before counting exclusions; the existing 450 February-2018 off-grid rows are already a subset of the 909 unmatched-key rows and must not be double-counted.
3. Preserve the 16 absent keys as missing-bar/gap-window dispositions and the 2017-09-06 16:00 daily placeholder as a distinct unresolved source conflict.
4. Produce an append-only unified quarantine crosswalk and verify that every recommendation is linked to frozen evidence. Do not patch/build the candidate dataset until the crosswalk is reviewed and the builder can fail closed on every unresolved signal-influencing item.
5. No downloads, no new sidecar requests, no raw-data mutation, no timestamp shift, no synthetic candles, no backtest, no strategy promotion, and no live action.

## Goal distance / gate status

- G0: `BLOCKED_GLOBAL`; canonical source: `NONE`; source cases closed: 0.
- G2: all 23 current strategy candidates remain historical-screen FAIL; no strategy approved.
- G3: quarantine sensitivity/source adjudication unresolved.
- G4: insufficient forward/out-of-sample evidence.
- G6: adaptive AI validation not built.
- G7: live signing, broadcast, and orders remain `BLOCKED`.
- Profitability: **NOT ESTABLISHED**.

A green GitHub Actions run confirms bounded tooling/tests executed successfully. It does not establish source authority, clear G0, or prove profitability.
