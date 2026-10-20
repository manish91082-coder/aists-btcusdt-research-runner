# CP-0282: Unauthenticated G0 Entry-Path Fail-Closed (Hindi)

**तारीख:** 2026-10-20  
**Branch:** `cp-0120-ai-brain-foundation`  
**Verified code/test HEAD:** `844012fd2e32d26fc999bfe55870357b345cfcf3`  
**Exact-HEAD CI:** [39374294235](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39374294235)  
**Scope:** `aists_brain/research_run_entrypoint.py` में caller-supplied G0 PASS को execution authority समझने से रोकना। केवल source/tests/CI; कोई data execution नहीं।

## Finding

Source review में `run_research_entrypoint()` के पास G0 सहित gate states caller-supplied mapping से आते थे। यदि caller ने `G0="PASS"` दिया और inputs भी दे दिए, तो entrypoint stored-feature simulation harness invoke कर सकता था। उसी codebase के provenance loader, harness और report verifier स्पष्ट करते हैं कि PASS claims/hash bindings अपने-आप external adjudication authority authenticate नहीं करते।

यह production orchestration trust-boundary gap था: report में unauthenticated claim label होने के बावजूद simulation attempt संभव था।

## Implemented fix

- G0 के लिए supplied `PASS` अब entrypoint से execution authorization नहीं देता।
- जब तक trusted, independently verified gate receipt का integration मौजूद नहीं है, entrypoint `G0_EVIDENCE_NOT_AUTHENTICATED` कारण से `BLOCKED_INPUT` report देता है।
- Input CSV/manifest/feature artifact paths inspect नहीं होते; simulation harness call नहीं होता; input hashes या simulation payload नहीं जुड़ते।
- Report interpretation अब स्पष्ट करता है कि gate evidence unauthenticated है और simulation attempt नहीं हुआ।
- Structural report verifier अब इस no-execution reason को validate करता है, लेकिन इसे G0 PASS authentication नहीं मानता।
- Regression test synthetic caller-supplied G0 PASS, पूरी input arguments और nonexistent paths के साथ harness non-invocation व no-inspection assert करता है।

## Verification

- Final code/test HEAD: `844012fd2e32d26fc999bfe55870357b345cfcf3`
- Exact-HEAD GitHub Actions [run 39374294235](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39374294235): **SUCCESS**
- Brain suite: **220 tests passed**
- CP-0026 quarantine suite: **11 tests passed**
- Earlier intermediate runs failed while the new regression test was being wired; missing test import was corrected, and the exact final HEAD run above passed.

## Boundaries / current gate state

- This hardens the research orchestration entrypoint only. It does not make the lower-level harness an authority adjudicator, nor does it authenticate market source provenance.
- G0 remains `BLOCKED_GLOBAL`; canonical source remains `NONE`.
- The frozen CP-0040 manifest and unresolved non-row blocker authority state remain unchanged.
- No candidate build, historical backtest, paper session, live signing, public broadcast, or Binance order was run.
- PR #2 remains open and unmerged.

## Next action

Continue source-level inventory for alternate callable execution paths that could invoke the lower-level harness without this entrypoint guard. Confirm whether any are production-wired versus test-only; add focused regression coverage where an exposed production path exists. No execution while G0 remains blocked.
