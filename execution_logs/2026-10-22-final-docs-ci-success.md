# Final-document CI and allowlist verification — 2026-10-22

## Run identity
- Workflow: `Crypto target research smoke tests`
- Run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817044689
- Tested commit: `038bf51cff07d1396f6a7a5d0baef25422c4c274`
- Final conclusion: `success`
- Job `unit-tests`: all substantive steps completed successfully.

## Verified results
1. Python compilation of `crypto_target/research_math.py` and `scripts/cleanup_current_project.py`: **PASS**.
2. Required docs exist and are non-empty; target amount is consistent in README, project details, status and master research log; truth-state markers are present; no stale expanded-CI pending marker appears in the three current summary documents: **PASS**.
3. Committed allowlist dry-run: **PASS**. Output reported **20 tracked files, 20 protected files, 0 deletion candidates**. No files were changed by the dry-run.
4. Deterministic unit tests: **5/5 PASS** — invalid inputs, max drawdown, realized-profit reinvestment, geometric required-return math, and target multiple.

## Interpretation
This run validates the repository snapshot at the tested commit, the cleanup protection rules, required document consistency, helper compilation and five unit tests. It does not validate market data, test a trading strategy, establish profitability or estimate time to target. No market data was downloaded and no live exchange action occurred.
