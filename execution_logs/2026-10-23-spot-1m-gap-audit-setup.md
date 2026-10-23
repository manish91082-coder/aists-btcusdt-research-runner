# Execution log — Spot 1m archive gap audit setup
**Date:** 2026-10-23  
**Branch:** `research/full-history-validation`  
**Status:** Implemented; runtime validation pending.

## Triggering evidence
- Full-history workflow run [39954840075](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39954840075): 81 months / 243 expected archive checks; 231 passed, 12 failed; aggregate dataset withheld.
- Smoke CI [39954846287](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39954846287): passed.
- Reporting fixes: valid JSON newline in failed manifest; preserved raw archive names are included in failure accounting.

## New audit
- Script: `scripts/audit_btcusdt_spot_1m_gap_months.py`
- Scope: official Spot 1m archives for the 12 months with failed Spot 5m archive checks.
- Validates official .CHECKSUM SHA-256 sidecars, CSV schema, expected row count, 1m timestamp grid, OHLC relations and close-time bounds.
- Saves raw checksum-matching 1m ZIPs and a JSON audit report as a GitHub Actions artifact.
- Does not reconstruct 5m candles, fill missing minute rows, or declare a strategy profitable.

## Next gate
Review the audit artifact. Only reconstruct a 5m candle if its five constituent 1m candles are all present, consecutive and valid, with deterministic OHLCV aggregation and tests. Otherwise preserve the gap and exclude/mark the affected period. Do not merge PR #17 or run walk-forward on an incomplete aggregate.
