# Expanded GitHub Actions smoke-test result — 2026-10-22

## Run identity
- Workflow: `Crypto target research smoke tests`
- Run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873
- Tested commit: `c1f7464f91816ebbffd614ba857b66aa5b69db24`
- Workflow conclusion: `success`
- Job: `unit-tests`; all seven substantive workflow steps completed successfully.

## Verified steps
1. Python compilation of `crypto_target/research_math.py` and `scripts/cleanup_current_project.py`: **PASS**.
2. Required project documents exist and are non-empty; target amount matches in README, project details, status and master research log; status includes NOT ESTABLISHED and UNKNOWN markers: **PASS**.
3. Cleanup script dry-run using committed `CURRENT_PROJECT_KEEP_PATHS.txt`: **PASS**. Log output reported 17 tracked files, 17 protected current-project files, and **0 tracked deletion candidates**. No files were changed by the dry-run.
4. Deterministic unit tests: **PASS**, 5 tests run, all passed:
   - invalid inputs rejected
   - maximum drawdown
   - realized profit reinvestment
   - required return reaches target
   - target multiple

## Interpretation and limits
- This is evidence that Python syntax, the current helper tests, the document checks and the cleanup allowlist passed on the tested commit.
- It is not market-data validation, a trading strategy backtest, evidence of a profitable edge, or a forecast of time-to-target.
- Main-branch documentation was subsequently edited only to record this result and provide navigation links; those later documentation-only changes do not alter the research helper code tested by this run.
- No data was downloaded and no live exchange action took place.
