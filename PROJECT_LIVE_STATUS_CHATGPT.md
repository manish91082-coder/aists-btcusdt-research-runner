# AISTS Project Live Status for ChatGPT

Last updated: 2026-10-17
Status checkpoint: CP-0143 official-source provenance recheck recorded; exact-head CI verified. Re-fetch live GitHub state on every new session.
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
- Latest verified checkpoint: CP-0143, official Binance Spot archive-provenance recheck (evidence documentation; no G0 clearance).
- CP-0143 evidence/docs head: `6eb292e88c0b5d7bb8d8430674ad9f937291b607`; exact-head CI passed in run [39022076178](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39022076178).
- CP-0142 implementation CI remains recorded below; CP-0143 exact-head CI is the latest verified workflow run.
- CP-0143 exact-head CI terminal success on `6eb292e88c0b5d7bb8d8430674ad9f937291b607`: compile step and test step success; exact output `Ran 148 tests in 0.352s` and `OK`; run [39022076178](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39022076178), job ID `117365720597`.
- PR #2 remains OPEN and unmerged; the live branch must be re-fetched after this metadata correction because it creates a new head and triggers CI.
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


## CP-0142 — Causal strategy decision artifact producer (2026-10-17)
- Live-state inspection before changes: branch head `d32993b33d07fefb48b2a90d504f72b0348ac580`; PR #2 OPEN, merged=false, head matched; latest run on that head was Actions run 39021648643, terminal success. Compile and test steps succeeded. Exact test count is being verified on the new checkpoint before this entry is treated as complete.
- Added `aists_brain/causal_decision_producer.py`. For each completed contiguous candle it computes context from the prefix ending at that candle, classifies the regime, calls the existing strategy action engine, and emits a versioned artifact with decision IDs, close-time cutoffs, source CSV hash, per-snapshot SHA-256, per-feature prefix hashes, selected strategy, action and reason.
- The artifact contract is offline-only and explicitly marks actions as not exchange orders. Live signing, public broadcast, order placement, automatic SL and automatic TP remain false. State transitions between decisions are research assumptions for a hypothetical next-contiguous-open fill, not actual fills; the downstream simulator remains authoritative.
- Added `tests/test_market_causal_decision_producer.py` for causal lineage, BUY candidate generation, NO_TRADE abstention, invariance of earlier snapshots when later candles change, future timestamp rejection, duplicate IDs, gap rejection and invalid metadata. Synthetic candles are unit-test fixtures only.
- The CSV entry point loads through the existing provenance gate; this does not authenticate an external adjudicator. Current G0 remains BLOCKED_GLOBAL, so no real BTCUSDT decision artifact or performance run is permitted.
- Goal-direction assessment: this joins the strategy action layer to the causal research artifact path and removes a real software integration gap. It does not resolve source provenance or G2; do not count it as profitability progress or candidate promotion.
- Gates unchanged: G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED.
- PR #2 must remain OPEN and must not be merged. Next: verify this exact head's CI terminal output and test count; if green, prioritize an admissible new official evidence path for G0 rather than continuing infrastructure-only increments.


## CP-0142 exact-head verification result
- Implementation commit: `9eb6fd94a210bc7976dd1dbafb0952e129c99f4a`.
- Exact-head GitHub Actions run [39021877488](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39021877488): terminal `success`; job `brain-unit-tests` ID `117365150499`; compile step and test step both completed successfully; log says `Ran 148 tests in 0.180s` and `OK`.
- Branch head and PR #2 head matched this implementation SHA at verification; PR state OPEN, merged=false, merged_at=null. The following status/roadmap documentation commit triggers its own CI run and must be rechecked.
- Next decision: no further infrastructure-only module is justified without an admissible new G0 evidence path. Continue only if a distinct, authoritative source artifact/version record or maintainer response is available; otherwise state the exact evidence request and do not repeat the same search.


## CP-0143 — Fresh official-source provenance recheck (2026-10-17)
- Inspected the current official Binance Public Data README and current API metadata/comments for issues #504, #475 and #505. The README says archived files can be updated later and lists two dated update bundles (2022-08-08 klines, 2022-04-21 aggregate trades), but does not provide prior-version retrieval or exact publication/replacement timestamps in the inspected text.
- At recheck: #504 OPEN, 0 comments; #475 OPEN, 1 contributor comment; #505 OPEN, 0 comments. #475/#505 contain user-submitted reports of monthly/daily/API disagreement and a malformed BTCUSDT 5m close_time despite matching checksum. These reports were not independently reproduced here and are not maintainer-confirmed canonical-source rulings.
- Detailed append-only evidence note: `evidence/source_adjudication/CP0143_Official_Binance_Spot_Archive_Provenance_Recheck_HI.md`.
- Gate impact: G0 remains BLOCKED_GLOBAL; no archive precedence, source repair, PASS manifest, real-market run, or candidate promotion is authorized. Smallest actionable request remains a maintainer response in #504 with official answers and explicit handling/correction guidance for #475/#505.
- Goal-direction: this adds concrete source-tracker evidence and narrows the unresolved request; it does not clear G0. Do not repeat the same search absent a new official response/artifact. At the time of this checkpoint commit, its own exact-head CI is pending and must be re-fetched before claiming verification.


## CP-0143 exact-head verification and issue recheck
- Branch/PR head at evidence checkpoint: `6eb292e88c0b5d7bb8d8430674ad9f937291b607`; PR #2 OPEN, merged=false, merged_at=null.
- Exact-head CI run [39022076178](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39022076178): terminal success; compile and test steps succeeded; log says `Ran 148 tests in 0.352s` and `OK`.
- Rechecked official tracker metadata/comments after the CP-0143 report: #504 OPEN, updated 2026-09-27, 0 comments; #475 OPEN, updated 2026-07-10, 1 contributor comment; #505 OPEN, updated 2026-09-27, 0 comments. No new maintainer response or official version/correction record observed.
- The status header above was corrected to reflect CP-0143; this documentation-only commit triggers its own CI and must be verified on the resulting exact head.
- Goal-direction decision: there is no newly arrived official evidence to justify another provenance search or a gate change. Do not add infrastructure-only modules. Wait for a new official response/artifact or a separately admissible evidence path. G0/G2/G3/G4/G6/G7 remain unchanged.


## CP-0145 — Continuity and next-action decision (2026-10-17)
- Re-fetched the current branch, PR #2, and latest Actions runs. Branch and PR head match `db835227eda2b631426885a0e80ce476f7f59244`; PR #2 is OPEN and unmerged. Latest run `39022396465` is completed/success on that exact SHA; compile and unit-test steps succeeded. No code was changed in this checkpoint.
- Rechecked Binance Public Data issue metadata: #504 OPEN/0 comments, #475 OPEN/1 contributor comment, #505 OPEN/0 comments. No new maintainer answer or issue resolution was present.
- Reviewed latest official repository activity: merge PR #441 (2026-10-16) changes utility URL encoding for Chinese-character instrument names. It is unrelated to historical Spot archive provenance and does not change any gate.
- Existing CP-0117/CP-0119 evidence already establishes 11 exact aggregation relationship blockers, daily-value corroboration for only 35 exact target bars, 14 monthly divergences across 97 fields, and no historical version timeline. Do not repeat checksum/correction-bundle work or treat current daily/trade agreement as global canonical-source authority.
- Decision: no infrastructure-only module, no real-market run, no source mutation, no fake PASS manifest, and no candidate promotion. A formally frozen conservative quarantine policy remains a possible future research path only if candidate-specific final metrics can be obtained through an authorized path; it must not bypass the current G0 fail-closed guard or imply global provenance PASS.
- Gates unchanged: G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. ₹10,000 INR converted to USDT; BTCUSDT Spot long-only research; live signing/broadcast/orders and automatic SL/TP remain disabled.
- Goal-direction assessment: this checkpoint removes no market-data blocker. It prevents a misleading detour by explicitly ruling out unrelated repository activity and redundant evidence searches. Next action requires a genuinely new official source response/artifact or a rulebook-compatible path that produces valid candidate-specific evidence without weakening G0.
