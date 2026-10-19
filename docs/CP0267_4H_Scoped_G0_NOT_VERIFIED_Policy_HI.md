# CP-0267: 4h Scoped G0 NOT_VERIFIED Policy

Date: 2026-10-19
Scope: BTCUSDT Binance Spot, 4h candidate eligibility only
Frozen CP-0040 rulebook SHA-256: 5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0
Frozen CP-0040 exact-key manifest SHA-256: d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819
Frozen CP-0040 non-row blocker SHA-256: d0126152a58baecd8f61bcdcc21286ecffacba6427e7b09696ca63db33c1f0d0

## Decision

Use a separate versioned 4h scope. Do not edit the frozen CP-0040 acceptance contract. Every disputed or absent exact 4h key is NOT_VERIFIED and excluded from the 4h candidate. No disputed source is selected by convenience, no candle is synthesized, and no timestamp is shifted. Historical publication/version provenance remains NOT_VERIFIED even when current archive bytes pass their recorded checksum.

## Frozen 4h exclusion manifest

Artifact: evidence/source_adjudication/CP0267_4H_NOT_VERIFIED_Exclusion_Manifest.csv
SHA-256: c4daf0be851d9a4ae5dfca62e40f719ef8b6c3c8de7294d98f42c31fa4667241
Rows: 22 unique exact keys:
- 3 NOT_VERIFIED_CLOSE_TIME_CONFLICT
- 2 NOT_VERIFIED_MISMATCH
- 1 NOT_VERIFIED_INVALID_ROW
- 16 NOT_VERIFIED_GAP
The frozen gap population has 17 expected slots, one of which overlaps the invalid daily-only placeholder row. That overlap is represented once, not double-counted. The other 16 slots are gap-only. No gap bar is synthesized.

## Runtime policy

The opt-in `--scope-not-verified` mode:
1. Validates the frozen 969-row exact-key manifest and 27 non-row blocker file by SHA-256.
2. Expands unresolved exact keys, the 11 cross-interval aggregation buckets, 16 date-level FETCHREF cases, and 17 expected 4h gap slots into conservative exclusions.
3. Builds only the 4h candidate in this scoped mode. It verifies each output row has a checksum-backed current-snapshot identity and no unresolved exact-key/date/bucket/gap exclusion applies.
4. Labels historical-version provenance NOT_VERIFIED and the artifact as not acceptance-grade.
5. Leaves the default CP-0203/CP-0040 acceptance-grade gate unchanged. CP-0027 backtest and all live signing/broadcast/orders remain blocked by their existing gates.

## Closure criterion

G0 may be recorded as `G0_SCOPED_PASS_4H_CANDIDATE_ELIGIBILITY_ONLY` only after the runtime builder completes against the user's checksum-verified local archives and writes a report proving the exclusions and final candidate SHA. This repository change and static tests alone do not prove that runtime result. If any unresolved key leaks into output, any checksum differs, or the structural audit fails, G0 stays blocked.

## Current status

`IMPLEMENTED_PENDING_CI_AND_RUNTIME_EXECUTION`. No profitability claim, candidate promotion, historical point-in-time claim, backtest approval, or live permission is granted.
