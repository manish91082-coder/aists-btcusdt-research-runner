# Execution record: GitHub logging change and CI verification

- Record created UTC: 2026-10-23
- Repository: manish91082-coder/aists-btcusdt-research-runner
- Branch: research/hd04-alternate-source-probe
- Workflow logging change commit: bbabd2c1e1e1302c389d8e75ee95205341724b7c
- Research-log update commit: 77ebdc391ba7d0ea1c80333d2beb132e7629d882
- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39920640004
- Run ID: 39920640004
- Workflow: Crypto target research smoke tests
- Verified outcome: SUCCESS
- Job: unit-tests, job ID 120304743836, conclusion SUCCESS
- Runtime: Python 3.12.15
- Verification performed from downloaded GitHub Actions job log: py_compile passed for all listed research/collector/uploader Python scripts; deterministic unittest discovery ran 34 tests in 0.576 seconds; result OK.
- Cleanup safety check in the same job: dry run only, no files changed.
- Important limitation: this smoke run validates Python compilation and unit tests, not the YAML execution behavior of the full-history workflow, live Binance archive acquisition, Supabase upload, bucket existence, table existence, or database catalog contents.
- Full-history workflow change is committed, but no full-history collection/canary run has been started. No archive counts or cloud persistence are claimed from this record.
- Logging implementation: full-history workflow tees collector/uploader console output to artifacts/btcusdt-full-history/execution.log, records UTC/run/commit/input metadata and exit codes, writes a GitHub Step Summary, and retains the output directory as a 30-day GitHub artifact.
- Security: no secret values are written to logs. Service-role key must be stored only in GitHub Actions Secrets.
- Next controlled action: once the full-history workflow is dispatchable on the default branch under the repository's approved change process, run only 2026-09 to 2026-09 as a canary; inspect the complete Actions log and artifact. Treat Supabase as SKIPPED unless secrets, private bucket, schema, upload success, and catalog rows are all evidenced.
