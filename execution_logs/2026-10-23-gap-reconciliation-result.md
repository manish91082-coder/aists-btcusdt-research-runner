# Execution Log: Spot 1m and 5m Gap Reconciliation

- Date: 2026-10-23
- Branch: research/full-history-validation
- Run: [39960237333](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39960237333)
- Diagnostic job: PASS; official 1m archive audit and 1m/5m reconciliation completed for 12 months; artifact uploaded.
- Long-history job: FAIL closed, 231/243 expected archive checks passed, 12 failures, no normalized aggregate.
- Finding: each of the 12 failed months reports discontinuities in both Spot 1m and Spot 5m archives, with equal gap counts per month. This is evidence of shared discontinuity windows, not proof of the cause. Do not infer no trades or source corruption without boundary evidence.
- December 2020: two timestamp gaps plus one 1m close-time anomaly; unresolved.
- Limitation: GitHub connector exposes decoded job logs but cannot decode the binary artifact ZIP. Updated diagnostic output to print boundary candle context directly in logs, commit f93b385225d9384c8060d727f0df9a5773788e82.
- Next gate: verify compile, inspect logged OHLCV boundary rows and close-time anomaly, then assess validator semantics. No synthetic bars, no silent exclusions, no walk-forward, no merge, no live trading. Tax/TDS deferred.
