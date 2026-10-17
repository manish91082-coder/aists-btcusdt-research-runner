# AISTS Project Live Status for ChatGPT

Last updated: 2026-10-17
Status checkpoint: CP-0141 implementation verified; latest checked documentation head CI passed. Re-fetch live GitHub state on every new session.
Canonical repository: https://github.com/manish91082-coder/aists-btcusdt-research-runner
Implementation branch: cp-0120-ai-brain-foundation
Pull request: https://github.com/manish91082-coder/aists-btcusdt-research-runner/pull/2 (must remain OPEN; do not merge)

## Mission and non-negotiable constraints
- Build and rigorously evaluate a BTCUSDT-first, long-only Binance Spot research/decision engine for initial capital ₹10,000 converted to USDT.
- Primary evidence source: Binance public downloadable monthly archives; do not substitute live API data.
- No fabricated/synthetic market candles in performance research. Synthetic fixtures are permitted only for software tests.
- Do not add automatic stop-loss/take-profit against the user's stated preference.
- No live signing, public broadcast, or Binance order placement. Research/paper only.
- Evidence-first; do not claim profitability unless an independently verified, cost-aware historical evaluation supports it.
- Workflow: INSPECT → VERIFY → DECIDE → IMPLEMENT → TEST → PUSH → GITHUB STATE CHECK → CI TERMINAL RESULT → VERIFIER → NEXT.
- Never merge PR #2. Keep updates append-only except narrowly necessary corrections to status metadata.

## Latest verified GitHub state
- Latest verified implementation checkpoint: CP-0140, independent structural audit-report verifier.
- Last verified implementation-code SHA before continuity-doc correction: 29bf1f101d81b478b040a8ae3182779bbf81bd5c. Latest docs-only branch/PR head: 7d53d0fa8fd29985346115a2eac45fe9e4558351.
- CI run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39020923719
- CI run 39021336643 on docs-only head 7d53d0fa8fd29985346115a2eac45fe9e4558351: terminal success; exact output `Ran 132 tests in 0.067s` and `OK`. Run URL: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39021336643.
- PR #2 state at this checkpoint: OPEN, merged_at=null; branch head matched PR head. The live branch must be re-fetched after this status-file commit because the docs update itself creates a new head and triggers CI.
- Important metadata issue discovered 2026-10-17: before this file was created, PROJECT_LIVE_STATUS_CHATGPT.md did not exist on the implementation branch. The roadmap header still said CP-0130 even though CP-0140 was appended. This continuity gap is being corrected now; do not assume prior status metadata was continuously current.

## Research gates (must not be inferred from code/test progress)
- G0: BLOCKED_GLOBAL.
- G2: FAIL_CURRENT_23_CANDIDATES; all 23 candidates failed the recorded G2 screen, none promoted.
- G3: BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT.
- G4: INSUFFICIENT_EVIDENCE.
- G6: NOT_BUILT.
- G7: LIVE_BLOCKED.
- Historical archive provenance has not been independently resolved; no valid real-market profitability result is established.

## CP-0140 implementation summary
- Added a structural verifier for research audit reports: canonical report SHA-256, schema, repo-head/run-ID binding, gate/status consistency, safety controls, input hash shape and simulated accounting/ledger status.
- Structural integrity is not proof of external provenance, gate authenticity, archive truth or profitability.
- CI passed on the exact SHA above; this is software-test evidence only.

## Goal-direction control
The next action must address the actual blocker to useful strategy evaluation, not add infrastructure merely to increase module/test count. First inspect current evidence and repository artifacts for a concrete, independently verifiable path to resolve G0/source adjudication and historical archive-version provenance. If evidence is unavailable, document the precise blocker and the smallest actionable evidence request; do not relabel data PASS or run a real-market backtest. Then resume the frozen strategy evaluation path only when the applicable gate legitimately passes.

## Resume protocol for a new chat/session
1. Read this file first, then docs/AI_BRAIN_ROADMAP_HI.md and the frozen CP-0040 acceptance rulebook.
2. Fetch the live branch head, PR #2 state and latest GitHub Actions run; do not trust this file without re-verification.
3. Resume from the last verified checkpoint, not from a new plan or an assumed state.
4. Before every project response, explicitly check whether the proposed next action removes a goal blocker; state drift if it only adds infrastructure without unblocking evidence.
5. Update this file and the roadmap checkpoint on each material project response/checkpoint, then verify the resulting branch/PR head and CI terminal outcome. Do not claim a GitHub update or CI pass until verified.
6. Keep all gate statuses and safety controls unchanged unless new admissible evidence independently justifies a change.


## CP-0141 work performed in this session
- Goal-direction check first: inspected current CP-0117/CP-0118/CP-0119 evidence, the exact frozen CP-0040 rulebook and the CP-0040 candidate-specific decision. No new official historical-version evidence was found in repository evidence; CP-0119 records 0 version-timeline links for 11 cases, and the recorded Binance issue #504 snapshot remains open with 0 comments/no maintainer answer. Do not repeat this same provenance search absent new official evidence.
- Found existing evidence is decisive about current limits: monthly parent-child rollups mismatch in 11/11 cases; the MTF_BREAKOUT_4H_D1 comparator's candidate-specific quarantine branch does not clear global G0, G2 is FAIL/NOT PROMOTED, G3 is blocked, and full-manifest quarantine changes TRAIN net return by -15.891741 percentage points. Do not present this diagnostic as validated profitability.
- To advance the actual AI brain rather than add another evidence-index module, added `aists_brain/strategy_action_engine.py`. It maps existing candidate eligibility into offline BUY_CANDIDATE/SELL_CANDIDATE/NO_TRADE actions and explicit rule exits. No automatic SL/TP or exchange-order behavior is added.
- Added `tests/test_market_strategy_action_engine.py` with 8 tests; added the module to CI compile list; appended CP-0141 to the roadmap. This is a new unvalidated deterministic rules adapter, not trained AI and not profitability evidence.
- CP-0141 code/test checkpoint verified: commit `f73fd7e3246d648d85a54be19d2c6f41f6531cfc`; CI run [39021588923](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39021588923) terminal success; exact output `Ran 140 tests in 0.076s`, `OK`. The final docs head `4dc91cb9b12077fd9a3232c851b34491d4c2e240` also passed CI in run [39021620053](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39021620053); terminal output `Ran 140 tests in 0.084s`, `OK`. The status-file commit that records this note is documentation-only and triggers another CI run; resume protocol requires rechecking the actual latest head and run before claiming that newest head is verified.
- Next after a verified CI pass: connect the action engine to a provenance-gated causal decision artifact producer, ensuring G0 BLOCKED still rejects any real-market run. Do not create or use a fake PASS manifest.
