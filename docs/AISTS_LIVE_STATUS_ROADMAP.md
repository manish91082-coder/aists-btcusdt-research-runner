# AISTS Live Status & Mission Roadmap

Last verified checkpoint: **CP-0196**  
Branch: `cp-0165-4h-archive-audit`  
Research target: BTCUSDT historical-data provenance and risk-adjusted strategy validation  
Current global gate: **G0 = BLOCKED_GLOBAL**

## Latest verified execution

- CP-0165 read-only 4h archive audit: [GitHub Actions run 39061829550](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39061829550)
- CP-0192 cache-only cross-interval triage is included in the same run and uploaded artifact.
- Latest static CI before this status update: [run 39061840931](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39061840931), successful.
- Execution commit: `56413adb693d62f2a2bfca13fc7180f2ef12b4dc`.
- Static-test commit: `7813d8141cdda3eeb3a3853391fac4e62b4a23ce`.

## Verified findings

### 4h archive audit

- 110/110 monthly 4h archives matched the recorded official SHA-256 checksum sidecars in the CP-0165 execution.
- ZIP CRC validation: 110/110.
- 19,974 raw 4h candle rows inspected.
- 9 gap events contain 17 estimated missing 4h open-time slots.
- Duplicate 4h open timestamps: 0; off-grid 4h open timestamps: 0.

### Cache-only 5m/1h cross-interval triage

- Inspected 18 existing child archives: 5m and 1h monthly archives across 9 relevant months.
- No child archive was missing; ZIP CRC checks passed and observed timestamp units matched the expected archive-month unit.
- 10 of the 17 missing 4h slots had both child archives pass the open-time grid check, but neither the 5m nor 1h archive contained any open timestamp inside those windows.
- The other 7 slots fall in February 2018. The cached `BTCUSDT-5m-2018-02.zip` contains 241 off-grid open timestamps; `BTCUSDT-1h-2018-02.zip` contains 43. Neither has duplicate open timestamps. These two archives are excluded from child-coverage claims.
- Triage result: `REVIEW_REQUIRED_CACHE_COVERAGE_INCOMPLETE`.
- No ZIP downloads, no network calls in CP-0192, no Binance market-data REST API, no cache mutation, no candle interpolation/reconstruction, no candidate build or backtest.

### Link to prior February 2018 evidence

Existing CP-0107 evidence at `evidence/source_adjudication/CP0107_Run_38777979719/` independently records:
- 450 monthly off-grid rows across 5m/15m/30m/1h for 2018-02-09 through 2018-02-11.
- Zero exact open-key matches for those off-grid rows in the daily reference rows.
- Daily-reference raw rows were preserved without timestamp shifting or rounding.
- The monthly SHA-256 values in that evidence were a recorded CP-0106 manifest reference, not a fresh official monthly sidecar validation; canonical source remains `NONE`.
- The committed daily-coverage CSV has records beginning at 2018-02-09 10:00 UTC for the 5m rows, so it does not supply rows for the missing 2018-02-09 00:00 and 04:00 windows. No matching 2018-02-08 daily reference ZIP is present in the repository tree.

These findings overlap with known CP-0107 evidence and do **not** close source cases or establish which archive should be treated as canonical.

## Next bounded action: CP-0197

1. Reconcile the seven February 2018 slots against the existing CP-0107 daily-reference evidence by exact open-time key only.
2. Classify the two 2018-02-09 slots (00:00 and 04:00 UTC) as “no rows in the currently committed daily-reference evidence window”; do not generalize that absence to source-authority conclusions.
3. Keep the five 2018-02-08 slots unresolved because the repository contains no corresponding daily reference ZIP in the inspected evidence tree.
4. Carry forward the ten grid-valid slots with zero child opens as unresolved historical gaps.
5. Do not download archives, fetch new sidecars, modify raw source data, synthesize/shift candles, close source cases, change strategies, or run a backtest in this checkpoint.

## Goal distance / gate status

- G0: `BLOCKED_GLOBAL`; canonical source: `NONE`.
- G2: all 23 current strategy candidates remain historical-screen FAIL; no strategy approved.
- G3: quarantine sensitivity/source adjudication unresolved.
- G4: insufficient forward/out-of-sample evidence.
- G6: adaptive AI validation not built.
- G7: live signing, broadcast, and orders remain `BLOCKED`.
- Profitability: **NOT ESTABLISHED**.

A green GitHub Actions run means the bounded audit program executed successfully; it does not mean historical provenance is complete or a strategy is profitable.
