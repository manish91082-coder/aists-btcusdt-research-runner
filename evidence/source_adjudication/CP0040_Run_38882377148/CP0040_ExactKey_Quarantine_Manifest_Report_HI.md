# CP-0040 Exact-Key Quarantine Manifest

## परिणाम
**PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN** — 17/17 checks PASS.

- Row-level exact-key manifest: 969 rows; 969 unique interval/open_time_ms keys.
- Daily-only: 452; monthly-only: 457; shared economic conflicts: 52; close-time-only: 8.
- February 2018 off-grid 450 rows are a subset of the 909 unmatched rows and were not double-counted.
- Frozen index SHA-256: a3a961a3e3ff0783c1cfed6efafddef313f7c455148a9a5174e95feef80062bf; expanded index SHA-256: 072009025272fcba372b820a2ecbd1c65f5938138c5206f19e7cfcdf83ecc39b.
- Manifest SHA-256: d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819; non-row blockers SHA-256: d0126152a58baecd8f61bcdcc21286ecffacba6427e7b09696ca63db33c1f0d0.

## अभी भी blocking
27 non-row cases: 11 RESIDUAL_AGGREGATION_BUCKET and 16 MISSING_DAILY_REFERENCE_ACQUISITION. The frozen index has no exact interval plus millisecond open-time key for these records. They are kept in a separate blocker ledger rather than assigning guessed timestamps.

## निर्णय
- This validates the frozen published index and evidence matrices; it is not a fresh raw-byte rehash of the original CP-0041 package/rulebook.
- No canonical source selected; no cases closed.
- No candidate build or backtest run.
- Candidate eligibility remains BLOCKED until the 27 non-row blockers are adjudicated and fail-closed builder integration is tested.
