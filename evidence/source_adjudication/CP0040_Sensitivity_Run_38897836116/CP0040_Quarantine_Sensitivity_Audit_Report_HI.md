# CP-0040 Exact-Key Quarantine Sensitivity Audit

- Status: `PASS_QUARANTINE_SENSITIVITY_DIAGNOSTIC_COMPLETE`
- Comparator: `MTF_BREAKOUT_4H_D1` (frozen; diagnostic-only)
- Strategy and cost parameters were not tuned.
- No network calls or market-data acquisition; production candidate builder not invoked.
- Baseline replay must match frozen CP-0031 metric anchors before quarantine results are allowed.

## Input impact (exact key only)

| Interval | Baseline rows | Exact-key rows removed | Rows retained |
|---|---:|---:|---:|
| 4h | 19975 | 6 | 19969 |
| 1d | 3332 | 3 | 3329 |
| 1mo | 110 | 0 | 110 |

## Metric deltas (quarantine minus baseline)

| Period | Baseline net return % | Quarantine net return % | Delta percentage points | Baseline DD proxy % | Quarantine DD proxy % |
|---|---:|---:|---:|---:|---:|
| TRAIN | 81.993135445 | 66.101394616 | -15.891740828 | -22.190809231 | -21.405331682 |
| DEVELOPMENT_CHECK | 24.343646291 | 24.343646291 | +0.000000000 | -8.480433308 | -8.480433308 |
| CONSUMED_OOS_DIAGNOSTIC | -1.384621431 | -1.384621431 | +0.000000000 | -5.297173132 | -5.297173132 |

## Signal/input effect (separate from PnL)

- **4h_common_timestamps**: changed/flipped=; common timestamps=19969. 4h timestamps retained in both input scenarios
- **4h_regime_up_flips_at_common_timestamps**: changed/flipped=353; common timestamps=19969. Changes to attached completed-1d regime state at common 4h bars
- **4h_entry_bar_flag_flips_pre_position**: changed/flipped=32; common timestamps=19969. Pre-position breakout entry-rule boolean flips; not actual filled entries
- **4h_exit_bar_flag_flips_pre_position**: changed/flipped=343; common timestamps=19969. Pre-position exit-rule boolean flips; not actual exits
- **4h_prior_high20_changed_at_common_timestamps**: changed/flipped=80; common timestamps=19969. Rolling breakout threshold value changed or became/ceased missing
- **4h_prior_low10_changed_at_common_timestamps**: changed/flipped=40; common timestamps=19969. Rolling exit threshold value changed or became/ceased missing
- **1d_daily_ema_regime_flips_at_common_timestamps**: changed/flipped=58; common timestamps=3329. Daily EMA20>EMA50 regime boolean flips, which is the higher-timeframe input to the 4h comparator
- **removed_4h_rows_with_baseline_entry_bar_flag**: changed/flipped=0; common timestamps=9. Removed bars that met the raw entry-rule boolean before position-state logic
- **removed_4h_rows_with_baseline_exit_bar_flag**: changed/flipped=6; common timestamps=9. Removed bars that met the raw exit-rule boolean before position-state logic
- **removed_4h_rows_with_regime_up**: changed/flipped=1; common timestamps=9. Removed bars where the attached daily regime was up

## Actual trade-event deltas

- **TRAIN**: baseline trades=69; quarantine trades=67; shared pairs=64; baseline-only=5; quarantine-only=3.
- **DEVELOPMENT_CHECK**: baseline trades=42; quarantine trades=42; shared pairs=42; baseline-only=0; quarantine-only=0.
- **CONSUMED_OOS_DIAGNOSTIC**: baseline trades=24; quarantine trades=24; shared pairs=24; baseline-only=0; quarantine-only=0.

## Interpretation and restrictions
- This is a temporary exact-key omission sensitivity diagnostic. It does not declare daily or monthly archives canonical and does not resolve any row-level or aggregation blocker.
- The TRAIN, DEVELOPMENT_CHECK and CONSUMED_OOS_DIAGNOSTIC windows are historic examined windows; none is pristine untouched OOS evidence.
- The 1mo input is part of the frozen engine input bundle but has no exact-key overlap with the scoped manifest and is unchanged.
- G0 remains `BLOCKED_GLOBAL`; all 11 non-row aggregation blockers remain open; candidate promotion and live signing/broadcast/orders remain blocked.
