# CP-0280: Candidate Builder Fail-Closed Entry-Path Audit (Hindi)

**तारीख:** 2026-10-20  
**Branch:** `cp-0120-ai-brain-foundation`  
**Verified code/test HEAD:** `a06b1691a9627535c02900431c325e2f912eda0d`  
**Scope:** Production entry-path gate bypass review. No market-data build, backtest, or paper session.

## Finding

CP-0026 candidate-builder के production CLI में `--manifest`, `--blockers`, और `--gate-summary` paths override किए जा सकते थे। Gate का hash check supplied manifest को supplied summary से मिलाता था, लेकिन इन user-supplied paths को canonical CP-0040 paths से bind नहीं करता था। इसलिए self-consistent alternate files pass कराकर canonical G0 gate को bypass करने का source-level रास्ता मौजूद था। यह production-path security gap था, भले normal/default invocation canonical files इस्तेमाल करता हो।

## Change

Production mode अब `--manifest`, `--blockers`, `--gate-summary`, या `--gate-test-output` override स्वीकार नहीं करता। ऐसे arguments पर argparse exit code 2 से fail-closed करता है। Explicit `--gate-self-test` mode अभी भी test fixtures के साथ चल सकता है। Normal production mode canonical CP-0040 gate paths ही इस्तेमाल करेगा।

## Regression and CI evidence

- Added test `test_production_entrypoint_rejects_gate_path_overrides`.
- Existing quarantine and derived-monthly tests retained.
- Exact code/test HEAD `a06b1691a9627535c02900431c325e2f912eda0d`:
  - GitHub Actions run [39373244566](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39373244566): **SUCCESS**.
  - Compile step: PASS.
  - Existing brain suite: PASS.
  - CP-0026 quarantine suite: PASS.

## Limits / G0 status

- This change closes the CLI override bypass only. It does not prove all canonical gate files are authentic or independently adjudicated.
- G0 remains `BLOCKED_GLOBAL`; source authority is not established.
- No candidate data was built, no backtest or paper session was run, and no live signing, public broadcast, or Binance order placement occurred.
- CP-0040 frozen rulebook and frozen evidence were not modified.
- PR #2 remains the review path; do not merge without required review/state reconciliation.

## Next action

Audit the canonical CP-0040 gate artifact integrity contract and the other production entry paths, without running the production builder. Keep all unresolved cases blocked. Do not claim G0 closure or profitability.
