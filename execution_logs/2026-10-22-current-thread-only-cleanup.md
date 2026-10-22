# Current-thread-only repository cleanup — 2026-10-22

## Request
Keep only the files created for the crypto-target research work during this ChatGPT thread today; remove every other tracked file from the current `main` branch.

## Actions
- Rechecked the live `main` branch through GitHub API rather than relying on the screenshot's potentially stale rendered directory listing.
- The prior cleanup had removed the legacy audit files; the recursive tree at that point contained 15 files, including the pre-existing `README.md`.
- Removed `README.md` because it predated this research thread, even though its text had been updated during recent work.
- Removed `README.md` from both `scripts/cleanup_current_project.py` and `CURRENT_PROJECT_KEEP_PATHS.txt` so the allowlist matches the requested scope.
- GitHub commits:
  - Script strict-scope adjustment: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/c4057b62968216e239d9cc160b458d2ab5b757c2
  - Keep-list adjustment: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/582befc3e429a51aa70b67818197f50da0423703
  - Remove pre-existing README: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/1a673787c62b41305a92f3c3df5be89b552902af

## Verification
Latest `main` head checked: `1a673787c62b41305a92f3c3df5be89b552902af`.

Recursive tree contains exactly 14 tracked files:
- `.github/workflows/crypto-target-smoke.yml`
- `.github/workflows/repository-cleanup-preview.yml`
- `CRYPTO_10CR_PROJECT_STATUS.md`
- `CRYPTO_10CR_RESEARCH_LOG_HI.md`
- `CURRENT_PROJECT_KEEP_PATHS.txt`
- `crypto_target/__init__.py`
- `crypto_target/research_math.py`
- `execution_logs/2026-10-22-cleanup-final-verification.md`
- `execution_logs/2026-10-22-cleanup-script-push.md`
- `execution_logs/2026-10-22-repo-discovery.md`
- `execution_logs/2026-10-22-research-harness-bootstrap.md`
- `execution_logs/crypto-target/cleanup-20261022T153658Z.md`
- `scripts/cleanup_current_project.py`
- `tests_crypto_target/test_research_math.py`

- Missing expected files: none.
- Unexpected files: none.
- Old docs such as `CONTINUITY.md`, `DATA_AUDIT_LOG.md`, `PROJECT_STATUS.md`, old `tools/` scripts/tests and the pre-existing README are absent from current `main`.
- Git history and the repository's other branches were intentionally not erased.
- No market data was fetched and no trading strategy/backtest was run in this cleanup step.
