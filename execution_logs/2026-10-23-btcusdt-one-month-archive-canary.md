# Execution record: BTCUSDT one-month official archive canary

- Repository: manish91082-coder/aists-btcusdt-research-runner
- Branch: research/hd04-alternate-source-probe
- Successful workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921734599
- Run ID: 39921734599
- Job ID: 120308322878
- Workflow commit: e99f9a5ca905fc146a3a14e31f47c553461b068c
- Started UTC: 2026-10-23T08:01:34Z
- Finished UTC: 2026-10-23T08:01:40Z
- Runtime: Python 3.12.15
- Requested UTC month: 2026-09 only
- Datasets requested: Spot 1m klines, USDⓈ-M Futures 1m klines, USDⓈ-M funding
- Collector exit code: 0
- Summary: PASS=3, UNAVAILABLE=0, FAIL=0
- Total verified archive bytes: 3,852,025
- Supabase/database writes: NOT ATTEMPTED by design

## Per-archive evidence from the GitHub execution log

1. Spot 1m klines: PASS; 2,054,117 bytes; SHA-256 7a021fb5981cfdb1a56457d68fa81360ab27350c981ddfe63112b2322df44b56.
2. USDⓈ-M Futures 1m klines: PASS; 1,796,984 bytes; SHA-256 e1a821b5bf6b48d57da01c3e390b8a467a698155def5c18c2c63c0eb044a3247.
3. USDⓈ-M funding archive: PASS; 924 bytes; SHA-256 913cd31b8f924a06717a2fac17f3df6132c24ccded209eb3e4ae7d83e1b247f2.

The collector verifies each downloaded archive against the official adjacent .CHECKSUM sidecar, then checks ZIP CRC, data member shape, monthly row count, timestamps and grid, numeric OHLCV consistency, close-time fields, and funding schema/event rows.

## Failure caught and corrected during the same canary cycle

- Earlier workflow execution: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921614983; FAILURE because the USDⓈ-M Futures archive had a header row whose first field was open_time, which the collector attempted to parse as an integer timestamp.
- Corrective commit: e99f9a5ca905fc146a3a14e31f47c553461b068c. The collector now tolerates the expected 12-column kline header while retaining exact data-row/grid checks. Regression test added in commit 5a6441b7c45e287bba891f0f4172fc76023f775f.
- Smoke CI after regression test: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921757171; SUCCESS.
- Successful canary artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921734599/artifacts/12487337672; artifact ID 12487337672; 3,855,719 bytes; retained 30 days.

## Boundaries and next gate

- This proves the one requested month and three specific archives passed this collector's checks; it does not establish earliest available BTCUSDT history or strategy profitability.
- The artifact is temporary (30 days). No durable Supabase storage or database catalog write has been attempted or verified.
- Next: confirm the intended Supabase project, bucket/schema and GitHub Actions Secrets through a safe canary configuration process. Never print secret values. Do not upload to the project named supabase ai content creation claude antigravity unless the user confirms it is the intended project.
