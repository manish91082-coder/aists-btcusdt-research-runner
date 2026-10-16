# CP-0114: Exact-key quarantine overlap and G0 impact audit

**Date:** 2026-10-16
**Status:** `PASS_MANIFEST_OVERLAP_AUDIT_G0_STILL_BLOCKED`

## 1. Execution evidence

- Workflow: [GitHub Actions run 38940457832](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38940457832), executed commit `95d01d16e36505a4b207775b16394d3bddcdcbac`; conclusion `success`.
- Runner status: `PASS`, 11/11 checks passed.
- Child summary SHA-256: `1f33e12681a4be4f0280ac27a25f112714dd1e5555ca253fcb6ad58e39e3d1f0`.
- Workflow artifact: [12062208828](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38940457832/artifacts/12062208828), 9,906 bytes, ZIP SHA-256 `45fe350b7770f69276f2eb18ba2f70d6497ec2df19e2143872964f7046467434`, retention 7 days.

## 2. Exact-key overlap result

| Check | Result |
|---|---:|
| CP-0040 frozen exact-key manifest | 1,427 unique keys |
| CP-0113 daily/monthly target keys | 35 |
| Target keys present in exact-key manifest | 35/35 |
| Target keys with class ACQUISITION_ECONOMIC_CONFLICT | 14/14 monthly-divergent keys |
| Other target classes | 5 ACQUISITION_RAW_FIELD_CONFLICT; 16 AGGREGATION_BUCKET_ROW_QUARANTINE |
| Target keys with disposition OPEN_REVIEW_REQUIRED | 35/35 |
| Monthly-conflict keys already closed | 0/14 |
| Target keys included in CP-0040 sensitivity applied-key list | 0/35 |
| Monthly-conflict keys included in CP-0040 sensitivity applied-key list | 0/14 |

The frozen CP-0040 sensitivity application contains nine exact keys: six 4h keys and three 1d keys. CP-0040 Input Impact reports removal of 6/19,975 4h rows, 3/3,332 1d rows and 0/110 1mo rows, with zero replacement rows. None of the 35 5m/15m/30m/1h target candle keys occurs in that applied-key list.

## 3. Candidate-input relevance boundary

The existing CP-0040 candidate-input relevance matrix contains 11 rows, one for each unresolved cross-interval bucket, and records `direct_interval_overlap=False` for all 11 with the single frozen `MTF_BREAKOUT_4H_D1` comparator. The target intervals are 5m, 15m, 30m and 1h, so none of the 35 target keys is a direct 4h or 1d interval input to that comparator.

This is a narrow statement about the named comparator only. It does not prove that these source conflicts are irrelevant to all 23 candidates currently failing G2, nor does it prove that these keys are actually excluded by every candidate-specific builder input. The manifest entry alone must not be confused with execution of a quarantine filter.

## 4. Decision under CP-0040

**The accepted quarantine coverage for the 14 monthly-conflict keys is not proven.** The keys exist in the frozen manifest, but the verified CP-0040 sensitivity applied-key set does not include them. The 14 remain `ACQUISITION_ECONOMIC_CONFLICT`, `OPEN_REVIEW_REQUIRED`, canonical source `NONE`, and not closed.

The next valid step is candidate-specific exact-key coverage reconciliation against the frozen builder inputs for all currently considered candidates. For any candidate whose signals can consume these intervals, verify exact-key exclusion or other adjudication under CP-0040. Do not infer a daily-over-monthly precedence rule, modify source bytes, or claim G0 passes.

## 5. Outputs

| Output | Bytes | SHA-256 |
|---|---:|---|
| `CP0114_Quarantine_Overlap_G0_Impact_Crosswalk.csv` | 12,212 | `3028e71be4dedebbdae8c1ce475936b5475bacc32689ff6e70569454d468bed3` |
| `CP0114_MonthlyConflict_Quarantine_Overlap.csv` | 5,913 | `ed1ea276992c40cd2826ec67c328c4be52d85295cc47bfc8d7815900164a21c7` |
| `CP0114_Quarantine_Overlap_G0_Impact_Report_HI.md` | 2,041 | `5d4e1d42b24a3d15a561768e2228e67eb5861a8ccd9f4497b08b26f81a09f82b` |

The crosswalk and divergent-key CSVs are retained in the linked workflow artifact.

## 6. Non-actions and gates

- No archive download or network request; no source archive bytes modified.
- No timestamp shifting/rounding, synthetic candles, candidate build, backtest, strategy promotion, live signing, public broadcast or Binance orders.
- G0 remains `BLOCKED_GLOBAL`; G2 remains `FAIL_CURRENT_23_CANDIDATES`; G7 remains `LIVE_BLOCKED`.
- Canonical source `NONE`; source cases closed `0`; all 11 aggregation blockers remain unresolved.
