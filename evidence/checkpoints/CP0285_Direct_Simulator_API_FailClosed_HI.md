# CP-0285: Direct Simulator API Fail-Closed Audit (Hindi)

**Checkpoint:** CP-0285  
**Branch:** `cp-0120-ai-brain-foundation`  
**Scope:** Source-level authorization hardening only. No historical candidate build, market-data run, backtest, or paper session.

## 1. निर्णय

CP-0284 के बाद एक दूसरा callable path मिला: `aists_brain.cost_aware_simulator.simulate_next_open` caller-provided candles और decisions लेकर modeled fees/slippage सहित simulated P&L/equity निकालता था। यह public function खुद trusted G0 receipt verify नहीं करता था। इसलिए CP-0284 के public harness wrappers बंद होने के बावजूद यह lower-level direct-call boundary अलग से खुली थी।

**CP-0285 action:** public direct simulator API अब fail-closed है और `G0_EVIDENCE_NOT_AUTHENTICATED` उठाती है। मौजूदा implementation को `_simulate_next_open_test_only` नाम के private helper में बदला गया। यह conventional Python privacy है, cryptographic security boundary नहीं।

## 2. किए गए बदलाव

- `aists_brain/cost_aware_simulator.py`
  - Original simulator implementation renamed to `_simulate_next_open_test_only`.
  - Public `simulate_next_open` now rejects immediately with `G0_EVIDENCE_NOT_AUTHENTICATED`.
  - Contract-bound simulator remains restricted to `SYNTHETIC_SOFTWARE_FIXTURE_ONLY` and calls the private test helper only after checking its fixture-only contract boundary.
- `aists_brain/research_harness.py`
  - Private fixture implementation now calls the explicitly test-only simulator helper. Public harness APIs remain fail-closed as in CP-0284.
- Tests updated:
  - `tests/test_market_cost_aware_simulator.py`: public API rejection regression; calculation tests use the fixture helper.
  - `tests/test_market_accounting_reconciliation.py`: synthetic accounting fixtures use the fixture helper.
  - `tests/test_market_synthetic_pipeline_integration.py`: synthetic pipeline uses the fixture helper.

## 3. Verification evidence

The first CI attempts failed because two existing synthetic test modules still called the newly disabled public API. The failure was inspected in GitHub Actions logs; those test call sites were corrected. Do not treat those failed attempts as passing evidence.

After correction, exact code/test HEAD `6346f7792c4e0b8cc9b2f50f8f3696d8094e4916` passed:

- [GitHub Actions run 39380285595](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39380285595): terminal **success**.
- Compile step: success.
- Brain unit suite: **223 tests passed**.
- CP-0026 exact-key quarantine suite: **11 tests passed**.

This run covers code/test HEAD `6346f7792c4e0b8cc9b2f50f8f3696d8094e4916`, not this report's eventual commit. A new exact-HEAD run is required after this report is committed.

## 4. Bounded path inventory and remaining limits

- Public direct simulator API: blocked.
- Public manifest-driven harness APIs: blocked pending trusted G0 receipt verifier (CP-0284).
- Contract-bound simulator: fixture-only scope, no authorization for historical data, candidate build, backtest, paper, live signing, broadcast, exchange orders, or automatic SL/TP.
- `historical_replay.replay_decisions` is a separate public decision-replay primitive that accepts a caller-supplied `provenance_gate="PASS"`; it does not calculate P&L, load files, or place orders, and its own limitations say that the gate is not independently adjudicated. This is not G0 authorization and must not be used as historical evidence while G0 is blocked. Consider a dedicated follow-up audit if the replay API is later wired into a production research path.
- Repository code-search results were incomplete, so this checkpoint is a bounded source-level audit of the simulator, harness, contract wrapper and known test callers, not a formal proof that no other callable primitive exists.
- A Python underscore helper is not a security sandbox. Real enforcement still requires the independently verifiable G0 authorization receipt and controlled entrypoint design.

## 5. Gate and safety status

- G0: **BLOCKED_GLOBAL**; canonical historical source authority remains unresolved.
- G1: **PARTIAL_SYSTEM_LEVEL**.
- G2: current 23 candidates remain **FAIL**, none promoted.
- G3: blocked; quarantine effects unresolved.
- G4: **INSUFFICIENT_EVIDENCE**.
- G5: **NOT_RUN**.
- G6: **NOT_BUILT / NOT_VALIDATED**.
- G7: **LIVE_BLOCKED**.
- Profitability: **NOT ESTABLISHED**.
- No production candidate builder, historical backtest, paper session, real market-data execution, exchange orders, live signing, or public broadcast was run.

## 6. Next decision

Proceed to CP-0286 with a narrow source-level audit of whether `historical_replay.replay_decisions` is wired into any production research entrypoint, and define the trusted G0 receipt contract bound to the frozen CP-0040 rulebook and unresolved populations. Do not claim G0 closure until independent adjudication and canonical historical source authority are actually evidenced.

**Mission navigation:** G0 closure remains the goal; CP-0285 reduces one code-level bypass risk but does not change the global gate status.
