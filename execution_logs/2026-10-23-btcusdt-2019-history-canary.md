# Execution record: BTCUSDT September 2019 historical coverage canary

- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921927263
- Run ID: 39921927263
- Job ID: 120308954232
- Workflow commit: 5a18ab3b088561a215d433c776926297d1f132d2
- Runtime: Python 3.12.15; run completed successfully at workflow level, collector exit code 0.
- Requested month: 2019-09; total archive bytes PASS: 2,140,033.
- Summary: PASS=1, UNAVAILABLE=2, FAIL=0.

## Per-source result
1. Spot 1m klines: PASS; 2,140,033 bytes; SHA-256 6bed8bcf250caedf243cd890cdffd93b6266e7f3007a8bb7e6d13b95a15645f1.
2. USDⓈ-M Futures 1m klines: UNAVAILABLE, HTTP 404.
3. USDⓈ-M funding archive: UNAVAILABLE, HTTP 404.

The workflow is designed to exit successfully when the collector records HTTP 404 as UNAVAILABLE rather than FAIL. This is not proof that the BTCUSDT contract did not exist at the time; it only records that these exact monthly archive URLs were unavailable at probe time.

Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921927263/artifacts/12486414849 ; artifact ID 12486414849; size 2,142,723 bytes; retention 30 days. Artifact includes execution.log and machine-readable manifest.

No Supabase/database write was attempted. Next bounded probe: test 2020-01 to see whether official UM Futures 1m and funding monthly archives are available there. Keep Spot and Futures start dates separate in coverage manifest; do not infer one venue's history from the other.
