# Cleanup execution outcome and verification — 2026-10-22

## Result
- Repository: `manish91082-coder/aists-btcusdt-research-runner`
- Branch: `main`
- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39806484233
- Actions run conclusion: `success` (verified from GitHub API)
- Cleanup commit: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/0042c045702efa91a2a50d2672c6079c67edbb62
- Follow-up removal of generated root transcript: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/f06eb8bb296d3e4e934bb9e40b395fac93bf352a

## Cleanup scope
The cleanup runner reported 43 tracked files, 13 protected current-project files, and 30 tracked deletion candidates. GitHub's post-commit recursive tree was inspected and confirmed that the legacy docs, tests, scripts, and old workflows were removed. The exact list of 30 candidates is preserved in `execution_logs/crypto-target/cleanup-20261022T153658Z.md`.

Protected paths verified in the post-cleanup tree:
- `.github/workflows/crypto-target-smoke.yml`
- `.github/workflows/repository-cleanup-preview.yml`
- `CRYPTO_10CR_PROJECT_STATUS.md`
- `CRYPTO_10CR_RESEARCH_LOG_HI.md`
- `CURRENT_PROJECT_KEEP_PATHS.txt`
- `README.md`
- `crypto_target/__init__.py`
- `crypto_target/research_math.py`
- `execution_logs/2026-10-22-cleanup-script-push.md`
- `execution_logs/2026-10-22-repo-discovery.md`
- `execution_logs/2026-10-22-research-harness-bootstrap.md`
- `scripts/cleanup_current_project.py`
- `tests_crypto_target/test_research_math.py`

The cleanup script stages deletions and writes its own per-run log; the Actions workflow performed the subsequent commit and push. The first attempt's push was rejected because the job also tried to modify a workflow YAML. The workflow was corrected so the successful retry did not modify that YAML in the cleanup commit. The generated `cleanup-apply.txt` transcript was removed from the repository root afterward; the Actions report artifact remains available at the run link above.

## Boundaries
- Git history and other branches were not erased.
- The current crypto-target research files remain present in the verified tree.
- This was repository housekeeping only. No market data was downloaded and no strategy backtest or profitability claim was produced.
