# AISTS Current Resume State (Hindi)

Updated: 2026-10-15 after CP-0103 signature diagnostics.

## Last verified execution
- Full source-lineage pipeline CP-0023 → CP-0024 → CP-0025 → CP-0026 → CP-0027 succeeded: run 38725478106.
- Latest focused source-adjudication run succeeded: run 38728831256.
- Focused run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38728831256
- Artifact ID 11969112194; 173,038 bytes; SHA-256 `e2d1de5ad50348ecb357c5e7a003dfa2fd3607f43877190c1aa2a3a728af5386`; seven-day Actions retention.
- Permanent report: `evidence/source_adjudication/CP0103_Run_38728831256_HI.md`
- Permanent CSVs: `CP0103_Economic_Signature_Summary.csv`, `CP0103_Partial_Signature_Summary.csv`, `CP0103_CloseTime_Only_Review.csv`, all under `evidence/source_adjudication/`.
- All source ZIP work ran in GitHub Actions. No Colab interaction required.

## Latest source evidence
- CP-0025 frozen reference set correctly restored: 40 flagged UTC dates, 240 daily archive references, all official-checksum matched.
- 60 daily/monthly shared-open value mismatches: 8 close_time-only; 52 economic/trade-metric.
- 909 unmatched keys: 452 daily-only, 457 monthly-only.
- CP-0103 focused target: 66/66 source archive objects verified, no source/archive errors, 5/5 self tests pass.
- Within the 909 unmatched rows, exact matching count is zero for full economic fields, OHLC-only fields, and OHLC + base volume. This does **not** prove no systematic timestamp alignment issue, but it does not support simply shifting timestamps to recover identical rows.
- 2018-02-09 through 2018-02-11 contains 897/909 unmatched rows (447 daily-only, 450 monthly-only); 450 monthly rows are off-grid with systematic fractional timestamp suffix. Do not round/shift/merge.
- CP-0103 checked 8 close_time-only shared-key cases. Expected-boundary differences are quantified; all 8 remain formally OPEN.
- 2020-12-21 roll-up checks: 34 rows, 25 exact, 9 review-required due missing exact 5m children in source variants. No child candles were filled.
- There are 0 canonical source selections, 0 source case closures, 0 auto-repairs, 0 strategy promotions, and no backtest rerun in CP-0103.

## Research gate state
- G0 BLOCKED_GLOBAL
- G1 PARTIAL_SYSTEM_LEVEL
- G2 FAIL_CURRENT_23_CANDIDATES
- G3 BLOCKED_PARTIAL
- G4 INSUFFICIENT_EVIDENCE
- G5 NOT_RUN
- G6 NOT_BUILT
- G7 LIVE_BLOCKED

## Resume instructions / no drift
1. Do not repeat 770 monthly archive acquisition or the CP-0027 baseline backtest.
2. Next investigate the source-row content/coverage around the 2020-12-21 missing-child window (roughly 13:45–14:55 UTC), using already verified archives. Then formalize disposition evidence for the 52 economic conflicts and 909 unmatched rows.
3. Keep original raw keys and values intact. No source is canonical until an explicit, evidence-backed disposition is recorded.
4. Only if an adjudicated candidate dataset changes bytes should CP-0026/CP-0027 be rerun; then compare with the frozen CP-0040 acceptance rules.
5. Trading strategy/live gate remains blocked. Legacy CP-0027 assumed 10,000 USDT, not the user's ₹10,000 INR planning capital; do not use its absolute currency results as INR projections.
