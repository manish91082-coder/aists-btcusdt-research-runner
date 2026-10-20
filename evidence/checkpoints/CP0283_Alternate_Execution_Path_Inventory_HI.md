# CP-0283: Alternate Research Execution-Path Inventory (Hindi)

तिथि: 2026-10-20  
Audited branch: `cp-0120-ai-brain-foundation`  
Audit base HEAD: `600b01cbe5dbd1b2f459dbc7fbef8e005b2f73e3`  
Scope: read-only source inventory; कोई candidate build, historical backtest, paper session या market-data execution नहीं चलाया गया।

## 1. Exact-head preflight

- Branch ref `cp-0120-ai-brain-foundation` audit शुरू होने पर `600b01cbe5dbd1b2f459dbc7fbef8e005b2f73e3` पर था।
- PR #2 खुला है, merged नहीं; PR head उसी SHA पर था।
- CP-0282 exact-head GitHub Actions run `39374357717` terminal `success` था।
- यह रिपोर्ट उसी audit base HEAD पर किए गए source inspection का record है; report commit के लिए अलग exact-head CI verification आवश्यक है।

## 2. Inspected execution surfaces

| File | Audit result |
|---|---|
| `aists_brain/research_run_entrypoint.py` | Caller-supplied `G0=PASS` पर `BLOCKED_INPUT / G0_EVIDENCE_NOT_AUTHENTICATED`; input paths inspect नहीं होते और harness invoke नहीं होता। |
| `aists_brain/research_harness.py` | दो public callable functions मौजूद हैं: `run_manifest_driven_simulation` और `run_manifest_driven_simulation_from_stored_features`. ये caller-provided external PASS claim को authenticated authority नहीं मानते, लेकिन module-level functions स्वयं G0 receipt verify नहीं करते। |
| `scripts/aists_runner.py` | Source inspection में research harness/entrypoint के direct import या call का match नहीं मिला। |
| `scripts/aists_legacy_pipeline.py` | Source inspection में research harness/entrypoint के direct import या call का match नहीं मिला। |
| `scripts/AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py` | Source inspection में इन harness functions का direct call नहीं मिला; यह अलग legacy baseline-backtest surface है और G0-blocked रहते हुए execute नहीं किया गया। |
| `.github/workflows/python-runner.yml` | Workflow source में research harness/entrypoint direct call का match नहीं मिला। Workflow को dispatch/run नहीं किया गया। |
| `tests/test_market_research_run_entrypoint.py` | Entry-point guard के regression tests हैं। |
| `tests/test_market_research_harness.py`, `tests/test_market_stored_feature_harness.py` | Test suites harness functions को सीधे call करती हैं; ये test-only callers हैं, production CLI wiring का प्रमाण नहीं। |

## 3. Decision

**Finding: production launch-surface bypass not demonstrated in the inspected runner/workflow files; lower-level callable boundary remains an unresolved defense-in-depth risk.**

CP-0282 केवल orchestration entrypoint को fail-closed करता है। कोई trusted, independently verified G0 receipt अभी integrate नहीं है। इसलिए इस inventory को यह दावा नहीं समझा जाए कि direct library callers पर G0 authorization लागू हो चुकी है। Harness functions को test fixtures के साथ चलने देना भी source authority सिद्ध नहीं करता।

इस चरण पर broad refactor या tests को हटाना उचित नहीं था। कोई source code, rulebook, manifest, blocker file या candidate data बदला नहीं गया। कोई strategy candidate promote/close नहीं हुआ।

## 4. Gate status (unchanged)

- G0: `BLOCKED_GLOBAL`; canonical historical source: `NONE`.
- G1: `PARTIAL_SYSTEM_LEVEL`.
- G2: current 23 candidates `FAIL`; none promoted.
- G3: blocked; material quarantine effects unresolved.
- G4: `INSUFFICIENT_EVIDENCE`.
- G5: `NOT_RUN`.
- G6: adaptive AI `NOT_BUILT / NOT_VALIDATED`.
- G7: `LIVE_BLOCKED`; live signing and public broadcast remain blocked.
- Profitability: `NOT ESTABLISHED`.

## 5. Next bounded action

Audit and harden the lower-level harness authorization boundary without allowing caller-supplied PASS to authorize production execution. Preserve a clearly isolated test-only path for synthetic fixtures, add regression coverage proving unauthenticated direct calls cannot start simulation, and verify the exact resulting GitHub Actions HEAD. Until then, do not run candidate builder, backtest, paper session, or exchange actions.
