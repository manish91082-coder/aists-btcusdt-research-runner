# CP-0294: Candle Gap Accounting Must Match Observed Timestamps

Date: 2026-10-20  
Branch: `cp-0120-ai-brain-foundation`  
Implementation commit: `24ba93dbd92001dbed557a7da389e45133b09a8f`  
Adversarial-test commit / code HEAD: `29af0007fc403dcb5b2dd473b9b00feafdd9bf92`

## Goal-directed finding

A targeted audit of `aists_brain/provenance_input.py` found that the loader previously checked only the manifest booleans `all_missing_intervals_accounted` and `all_gap_events_accounted`, plus monotonic timestamps. It did not derive actual gaps from the CSV or compare them with explicit manifest gap records. A hash-bound CSV could therefore contain missing intervals while the manifest asserted that all gaps were accounted for.

## Change implemented

- The loader now detects timestamp gaps from consecutive candle open times.
- Off-grid timestamp gaps fail closed.
- When gaps exist, a `gap_events` manifest list is required and must exactly equal the gap events derived from the CSV. Each event binds previous/next observed opens, first/last missing open, and missing count.
- If no gaps exist, a non-empty claimed gap list is rejected.
- The loader returns the observed `gap_events` list for downstream visibility.
- Added adversarial tests for an observed gap with no explicit record, an exact matching gap record, and an off-grid gap.

This is a narrow structural-integrity improvement. It does not authenticate a manifest's authority or prove Binance archive provenance.

## Verification

- Push CI: [39404393997](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39404393997), exact code HEAD `29af0007fc403dcb5b2dd473b9b00feafdd9bf92`, terminal SUCCESS.
- PR CI: [39404398830](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39404398830), exact code HEAD `29af0007fc403dcb5b2dd473b9b00feafdd9bf92`, terminal SUCCESS.
- In both runs, Python compilation, brain unit tests, and CP-0026 exact-key quarantine enforcement steps succeeded.
- PR #2 remains OPEN and unmerged.

## Gates and exclusions

- G0: `BLOCKED_GLOBAL`; this code change does not authenticate independent G0-A..G0-E adjudication.
- G2: current 23 candidates remain FAIL / NOT PROMOTED.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- G4: `INSUFFICIENT_EVIDENCE`.
- G5: `NOT_RUN`.
- G6: `NOT_BUILT / NOT_VALIDATED`.
- G7: `LIVE_BLOCKED`.
- Profitability: `NOT ESTABLISHED`.

No real-market backtest, candidate promotion, paper session, external reviewer request, external issue comment, signing, public broadcast, or exchange order was performed. Synthetic data remains test-only. Frozen CP-0040 rulebook is unchanged.
