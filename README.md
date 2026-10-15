# AISTS BTCUSDT Research Runner

A standalone GitHub Actions runner for reproducible, evidence-first BTCUSDT historical research.

## Current safety posture

- Public repository, using standard GitHub-hosted runners.
- No Binance REST market-data API, exchange API key, signing, live order placement, or transaction broadcast.
- Research data, when requested, must come from official downloadable archives on data.binance.vision with checksum and content validation.
- The workflow has contents: read permissions. It does not accept arbitrary inline Python or execute custom code from workflow inputs.
- The initial allowlisted task is smoke; additional research tasks must be implemented, tested and added to the explicit allowlist before use.
- Each run records its request ID, commit SHA, run ID, checks, and SHA-256 hashes in a compact JSON/CSV artifact.

## Execution

### Automatic trigger
A commit that changes requests/current.json on main triggers the workflow. Only a declared task in scripts/aists_runner.py can execute. Arbitrary code is not accepted from the request file.

### Manual trigger
Open Actions → AISTS Research Runner → Run workflow and select an allowlisted task.

### Verifying an execution
Each run should be checked by:
1. Exact commit SHA and Actions run ID.
2. Job/step conclusion, not only the workflow badge.
3. run_summary.json from the artifact.
4. Artifact ID, size and SHA-256 digest where provided by GitHub.
5. The report's check totals, request ID, and source/network policy fields.

A workflow showing success is necessary but not sufficient for a research gate to pass.

## Cost model

GitHub documents standard GitHub-hosted runner usage as free and unlimited for public repositories. This statement does not imply that every artifact, cache, larger runner, or other GitHub service is unlimited/free. Keep artifacts small and short-lived; commit verified compact evidence separately when durable retention is needed.

## Roadmap
1. Verify the runner, request-to-run chain, and artifact round trip.
2. Add official archive acquisition with SHA-256/ZIP CRC/content QA.
3. Rebuild only the frozen 4h, 1d, and 1mo candidate tests needed to investigate historical drawdown.
4. Separate data defects, accounting/simulator defects, and strategy failures.
5. Do not promote a strategy without out-of-sample evidence and frozen acceptance rules.

## License
MIT.
