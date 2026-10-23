# Execution record: canary workflow allow-list correction

Date: 2026-10-23
Repository: manish91082-coder/aists-btcusdt-research-runner
Branch: research/hd04-alternate-source-probe

## Event 1: first CI attempt failed safely
- Commit: 5e7501790fa14b436a05e7fdfb5649f00fc657df
- Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39920771237
- Job: unit-tests, job ID 120305171666
- Outcome: FAILURE at repository keep-list validation.
- Exact cause from fetched GitHub log: the newly added .github/workflows/btcusdt-archive-canary.yml was not yet listed in CURRENT_PROJECT_KEEP_PATHS.txt, so the cleanup preview flagged it as the one unprotected tracked file.
- Safety result: dry-run only. Log explicitly says no files changed. No deletion was applied.

## Corrective action
- Added .github/workflows/btcusdt-archive-canary.yml to CURRENT_PROJECT_KEEP_PATHS.txt.
- Correction commit: 159f593a6052e31b06042e7217437e9637a03752

## Event 2: verification after correction
- Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39920787299
- Job: unit-tests, job ID 120305222458
- Outcome: SUCCESS.
- Fetched and inspected job log: 59 tracked files, 59 protected current-project files, 0 deletion candidates, 34 tests passed in 0.360 seconds.
- This validates the keep-list and Python smoke suite. It does NOT prove the new archive-canary workflow executed; the commit-associated run available through the connector was the smoke-test workflow.
- No Binance archive acquisition and no Supabase write are claimed from these two CI events.

## Next gate
The one-month canary workflow requests only 2026-09 and uses official Binance Spot 1m, USDⓈ-M Futures 1m and funding archives, with checksum/schema/grid checks and an artifact containing execution.log plus the machine-readable manifest. It explicitly does not attempt Supabase writes. Actual canary execution remains unverified because the workflow is not confirmed dispatchable on the default branch. Do not merge PR #13 or write to a Supabase project merely to bypass this gate.
