# AISTS Project Live Status for ChatGPT

Latest goal-directed checkpoint: CP-0292 feature-lineage input-prefix binding. Implementation commit `af0fd32d1b254634fd794566e1bc12ef357e5b14`; regression tests/fixture correction at `97ce79ef6a7512e6839e340ff4818555808d77bc`. Exact-head verification recorded in CP-0292 report: run 39391119850 succeeded on HEAD `9a9d4df818a190723401134320403ac73445e246` (233 brain tests + 11 CP-0026 quarantine tests; compile passed). Later documentation commits require fresh exact-head verification. Latest empirical admissibility audit remains CP-0151; no historical gate has cleared.
Latest goal-directed checkpoint: CP-0291 multi-timeframe candidate contract hardening. Implementation/test HEAD: def8a9208cf2ae1bae9b6a5f0980e24be43abbfb; exact-HEAD CI run 39390227679 terminal SUCCESS (231 brain tests + 11 CP-0026 quarantine tests; compile passed). Append-only checkpoint/status documentation commits may follow this code head, so re-fetch the current branch HEAD and exact-HEAD CI before relying on the terminal state. Latest empirical admissibility audit remains CP-0151; no historical gate has cleared.
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
- Canonical implementation branch: `cp-0120-ai-brain-foundation`; PR #2 remains OPEN and unmerged.
- Latest code/test HEAD: `def8a9208cf2ae1bae9b6a5f0980e24be43abbfb`; exact-HEAD Actions run [39390227679](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39390227679) terminal SUCCESS.
- Verified run: Python compile PASS; 231 brain unit tests PASS; 11 CP-0026 exact-key quarantine enforcement tests PASS.
- CP-0291 hardens `select_multi_timeframe_candidate`: malformed candidate records, unknown actions, unsupported strategy labels, inconsistent NO_TRADE records, and non-boolean order flags now fail closed.
- CP-0291 is software-contract progress only. It does not clear any historical gate or establish profitability. The report is `evidence/checkpoints/CP0291_MultiTimeframe_Candidate_Contract_Hardening_HI.md`.
- Re-fetch current branch HEAD, PR #2 HEAD, and exact-head CI each session. Never merge PR #2.
- Prior documentation-only or code commits are not empirical market research progress. No market-performance claim may be inferred from a green CI run.
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



## CP-0146 — Existing quarantine evidence and capital-basis guard (2026-10-17)
- Re-fetched live branch, PR #2 and Actions before this decision: branch/PR head `d0b4ab3cc352a4584b1b48686d2795cc6a17d83e`; PR #2 OPEN, merged=false; latest exact-head run [39023546490](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39023546490) completed/success. Compile and unit-test job succeeded; no test count is claimed because this run's log count was not read.
- Re-read the frozen CP-0040 quarantine scope, completed sensitivity report, metric anchors and rulebook-bound eligibility decision. The diagnostic already exists: 4h rows removed=6, 1d rows removed=3, no replacements; TRAIN net-return delta=-15.891740828 percentage points; DEVELOPMENT_CHECK and CONSUMED_OOS_DIAGNOSTIC deltas=0. This is an old, consumed diagnostic, not new performance evidence; the consumed OOS diagnostic remains negative.
- Critical capital-basis correction: the frozen CP-0040 metric anchors specify `initial_capital_usdt: 10000`. That is not the user's ₹10,000 INR converted to USDT. Do not scale, relabel, or present these anchor returns/equity/P&L as user-capital results. No valid user-capital profitability result is established by this artifact.
- Decision: do not rerun or duplicate the existing quarantine sensitivity; do not tune or promote `MTF_BREAKOUT_4H_D1`; do not bypass CP-0026's production fail-closed gate. A future candidate-specific run must use the actual INR-to-USDT capital basis with explicitly evidenced FX/cost/lot-size assumptions, frozen rules, exact quarantined inputs, and the existing acceptance gates. If those assumptions/data are not verifiable, mark the affected metric `NOT_COMPUTABLE`.
- Gates remain unchanged: G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. No code/backtest was run in CP-0146; this is an append-only decision checkpoint, not a gate pass.


### CP-0146 — Existing quarantine evidence and capital-basis guard (2026-10-17; continuity reconciliation)
- Continuity check found the roadmap contains CP-0146 but this live-status ledger ended at CP-0145. This append reconciles the missing checkpoint reference; it does not create new research evidence.
- CP-0146's final branch head is `9892bc6d59f12f7d7216dae95cdfd7deaeb7733d`; PR #2 remains OPEN and unmerged. Exact-head Actions run [39024175207](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39024175207) completed with conclusion SUCCESS on that SHA. Do not infer a test count from this run without reading its logs.
- The existing CP-0040 quarantine sensitivity is reused, not rerun: 4h removed 6 rows, 1d removed 3 rows, no replacements; TRAIN net-return delta `-15.891740828` percentage points; DEVELOPMENT_CHECK and CONSUMED_OOS_DIAGNOSTIC deltas zero. The consumed OOS diagnostic remains negative and is not fresh/pristine OOS evidence.
- Frozen metric anchors use `initial_capital_usdt: 10000`, which is not the user's ₹10,000 INR converted to USDT. Do not scale or relabel those results as user-capital performance.
- Next action remains blocked pending admissible source/version provenance or another rulebook-compatible evidence path that does not bypass G0. Do not repeat the same provenance searches, rerun the old diagnostic, tune/promote candidates, or add infrastructure-only modules.
- Gates unchanged: G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`. No profitability claim, live signing, public broadcast, Binance orders, automatic stop-loss or take-profit.


### CP-0147 — Mission navigation / verified goal-distance baseline (2026-10-17)
- User requirement: every assistant response should end with a mission-navigation indicator; keep this goal ledger and roadmap updated in GitHub. The indicator must report verified state, not an invented completion percentage.
- Pre-change verification: branch head and PR #2 head both `c2fa0adfdbecab65902a600c7dcb224077720f68`; PR #2 OPEN, merged=false; exact-head Actions run [39024464747](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39024464747) completed SUCCESS on that SHA.
- Mission target: independently validated, cost-aware BTCUSDT Spot long-only research/paper decision engine for ₹10,000 INR converted to USDT; no live orders, no automatic SL/TP; no profitability claim without admissible evidence.
- Verified distance baseline: six release gates remain unresolved (G0 blocked; G2 all 23 current candidates failed; G3 quarantine effect blocks; G4 insufficient evidence; G6 adaptive AI not built; G7 live blocked). This is a gate count, not a percentage-complete score. First critical-path blocker is G0 archive provenance.
- Paper acceptance horizon remains at least 180 calendar days AND at least 30 closed round trips, whichever is longer; if not met by 365 days, classify as insufficient evidence. These are future acceptance requirements, not elapsed-progress claims.
- Direction verdict: this checkpoint improves continuity and prevents goal drift, but it does not clear a market-data gate or establish profitability. Do not claim the core trading goal is closer in empirical-evidence terms. Next action remains to wait for genuinely new admissible official archive-version evidence or establish a rulebook-compatible candidate-specific path without bypassing G0; no repeated search, no old diagnostic rerun, no infrastructure-only module.
- Standard response footer from now on: `MISSION NAV: TOWARD GOAL / NO EMPIRICAL GATE CLEARED THIS TURN | VERIFIED OPEN GATES: 6/6 | CRITICAL BLOCKER: G0 archive provenance | PROFITABILITY: NOT ESTABLISHED | LIVE: BLOCKED`. Update counts only after verified gate changes.


### CP-0148 — Rulebook-bound candidate debt disposition (2026-10-17)
- Re-verified pre-change branch/PR state: branch and PR #2 head `fe4286c7e7f8aa35356bf9ac37e9f43482beaded`; PR #2 OPEN/unmerged; exact-head CI run [39025449289](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39025449289) terminal SUCCESS.
- Re-read the frozen CP-0040 rulebook, candidate-specific eligibility decision, quarantine sensitivity CSV/summary, metric anchors and input-relevance audit. The rulebook permits a candidate-specific quarantine branch only for the frozen comparator; it does not authorize global G0 PASS or production-builder bypass.
- Candidate `MTF_BREAKOUT_4H_D1` remains FAIL / NOT PROMOTED: frozen consumed-OOS diagnostic net return `-1.384621431%`, PF `0.846407`, 24 closed round trips (below the rulebook's 100-round-trip G2 screen); these are old consumed diagnostics, not pristine OOS.
- The existing quarantine sensitivity is not repeated: it removed 6 4h rows and 3 daily rows with no replacements; TRAIN return changed by `-15.891740828` percentage points. This is a material G3 source-policy effect.
- Capital-basis defect remains decisive: historical metric anchors use `initial_capital_usdt: 10000`, not ₹10,000 INR converted to USDT. Therefore the historical P&L/equity/returns cannot answer the user's capital-specific goal. No re-scaling or relabelling permitted.
- Decision: retire this already-failed comparator from further tuning/replay; do not spend another run on it. Do not use it as proof of profitability or as a fresh strategy candidate. The only admissible continuation is (a) genuinely new official archive-version evidence that changes the G0 decision, or (b) a separately approved rulebook-compatible candidate-specific run with exact frozen inputs, quarantine lineage, evidenced INR/USDT conversion and cost/lot-size assumptions, while the production builder remains fail-closed. No such fresh run is started in this checkpoint because current artifacts do not provide a verified user-capital basis or fresh OOS.
- No code, candidate build, backtest, market-data download or source mutation in this checkpoint. Gates remain G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. Live signing/broadcast/orders and automatic SL/TP remain disabled.
- Mission navigation update: candidate-specific next action is now narrowed; this is a decision-quality improvement, not an empirical gate clearance. Do not report a completion percentage.


## CP-0149 — Continuity metadata reconciliation and next admissible action (2026-10-17)
- Start-of-checkpoint live verification: branch head and PR #2 head matched at `0e70898dc53132459c4ac606c579955d897fca33`; PR #2 OPEN/unmerged. Exact-head CI run [39027219413](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39027219413) completed SUCCESS. A second exact-head run [39027216920](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39027216920) also completed SUCCESS.
- Found a continuity defect: this status file's top checkpoint label remained CP-0143 even though CP-0148 was present in the body and the roadmap. Corrected the top label and recorded this reconciliation; this is metadata hygiene, not research progress.
- Goal-directed decision: do not repeat the already-exhausted official provenance search, rerun the consumed quarantine sensitivity, tune the failed `MTF_BREAKOUT_4H_D1` comparator, or add infrastructure-only code. Current repository evidence does not authorize a new real-market evaluation: G0 is still globally blocked, and no fresh official archive-version record has been established.
- Next admissible work is event-driven: act only on genuinely new official archive-version/publication evidence that can adjudicate the 11 unresolved aggregation relationships, or obtain explicit authorization for a frozen candidate-specific quarantine evaluation with exact lineage and evidenced INR→USDT, fee, slippage and lot-size assumptions. Keep production builder fail-closed. No synthetic market candles, no fake G0 PASS, no candidate promotion, no live signing/broadcast/orders, and no automatic SL/TP.
- Gates remain unchanged: G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. Profitability is NOT ESTABLISHED. This checkpoint clears no empirical gate.


## CP-0150 — Binance issue-state recheck (2026-10-17)
- Verified pre-change branch/PR head `839c3124b115a0066f4b8fcac379fdc78d33ccf7`; PR #2 OPEN/unmerged; exact-head CI runs [39027548596](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39027548596) and [39027545713](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39027545713) both terminal SUCCESS.
- Rechecked official Binance Public Data issue metadata and comments: [#504](https://github.com/binance/binance-public-data/issues/504) OPEN/0 comments (last updated 2026-09-27); [#475](https://github.com/binance/binance-public-data/issues/475) OPEN/1 contributor comment (last updated 2026-07-10); [#505](https://github.com/binance/binance-public-data/issues/505) OPEN/0 comments (last updated 2026-09-27). No new maintainer resolution or official archive-version record was found. The single #475 comment is contributor evidence, not a maintainer-confirmed adjudication.
- Decision: this check does not justify another duplicate provenance search, replay of the consumed quarantine sensitivity, tuning of failed `MTF_BREAKOUT_4H_D1`, or an infrastructure-only module. No new real-market run is authorized by current evidence. Wait for genuinely new official archive-version/publication evidence or explicit authorization of a frozen candidate-specific quarantine evaluation with exact lineage and evidenced INR→USDT, fees, slippage and lot-size assumptions; production builder remains fail-closed.
- Gates unchanged: G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. No profitability established; no candidate promotion; no live signing, public broadcast, exchange orders or automatic SL/TP. This checkpoint clears no empirical gate.


## CP-0151 — Candidate-run admissibility audit (2026-10-17)
- Verified pre-change branch/PR head `630823edb136b360de9677f450eae716bc4c4cbf`; PR #2 OPEN/unmerged; exact-head CI runs [39027977112](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39027977112) and [39027980805](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39027980805) terminal SUCCESS.
- Inspected committed CP-0040 artifacts directly: frozen metric anchors, rulebook-bound decision, quarantine sensitivity summary, G0 eligibility review and frozen acceptance rulebook. The only recorded candidate-specific G0 quarantine branch is for `MTF_BREAKOUT_4H_D1`, explicitly diagnostic-only; global G0 is BLOCKED_GLOBAL, canonical source NONE, and 11 non-row aggregation blockers remain unresolved.
- Existing anchor assumes `initial_capital_usdt: 10000`, fee 10 bps/side, extra slippage 5 bps/side and 25% allocation. This is not the user's ₹10,000 INR converted to USDT. The consumed OOS diagnostic is negative (-1.384621431% net, PF 0.846407, 24 closed round trips), and quarantine sensitivity materially changes TRAIN net return (-15.891740828 percentage points). These old windows are consumed diagnostics, not pristine OOS.
- Admissibility decision: do not repeat the failed comparator or relabel/scale its metrics. A new candidate-specific run is not currently actionable because it would repeat a failed comparator and lacks a verified user-capital/cost basis; production builder also lacks the necessary row-level quarantine integration and must remain fail-closed. No code, candidate build, data mutation or backtest authorized by this audit.
- Smallest genuine unblock: (1) a new official archive-version/publication record adjudicating affected exact-key aggregation relationships, OR (2) separately approved frozen evaluation scope for a genuinely new candidate with exact quarantine lineage, verified INR→USDT conversion, fees, slippage and lot-size assumptions, while not bypassing G0 or builder safeguards. Do not repeat old provenance searches without a new official signal.
- Gates unchanged: G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. No profitability claim, candidate promotion, live signing/broadcast/orders or automatic SL/TP. This audit clears no empirical gate.


## CP-0152 — New 4h candidate scope proposal (2026-10-17)
- Pre-change live state verified: branch and PR #2 head matched `9883051893f0b6675a060bee21eede299bf80f21`; PR #2 OPEN/unmerged; exact-head Actions run [39035163301](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39035163301) completed SUCCESS.
- Added proposal `evidence/research_scopes/CP0152_4H_EMA20_50_CAUSAL_ATR_SCOPE_PROPOSAL_HI.md`. Candidate proposal: 4h EMA20/EMA50 crossover plus causal ATR% percentile filter over the prior 252 completed 4h observations, eligible percentile band 20–90, long-only and next-contiguous-open hypothetical fills. No automatic SL/TP, signing, broadcast or exchange orders.
- This is explicitly `PROPOSAL ONLY`; approval is `PENDING_EXPLICIT_APPROVAL`; execution is `NOT_AUTHORIZED`; candidate build/backtest `NOT_RUN`. No real-market data was built or evaluated.
- Scope does not relax frozen CP-0040 thresholds or G0. Before any run, require exact-key quarantine lineage and actual row-exclusion proof, verified INR→USDT basis, fees/slippage, BTCUSDT lot-size/min-notional constraints, and frozen allocation/cash reserve. Unverifiable capital/quantity results are `NOT_COMPUTABLE`.
- Gate status unchanged: G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`. Eleven non-row aggregation blockers remain open; no profitability is established.
- Goal-direction decision: this prepares a concrete reviewable scope rather than repeating failed work or adding a code-only module. It clears no empirical gate. Do not execute the proposed candidate until the scope is explicitly approved and all applicable frozen rulebook prerequisites are satisfied.


## CP-0153 — CP-0152 exact-HEAD CI terminal verification (2026-10-17)
- Branch and PR #2 head before this status update: `4e1cf587122f831b916f5733500b6f99da2fcb6d`; PR #2 OPEN/unmerged.
- Exact-head Actions run [39035650619](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39035650619) terminal SUCCESS; `brain-unit-tests`, compile brain modules and unit tests all SUCCESS.
- G0 summary re-read: `BLOCKED_EXISTING_CP0026_BUILDER_LACKS_ROW_LEVEL_CP0107_QUARANTINE`; 909 unmatched exact-open key rows, 52 shared economic conflicts and 11 non-row blockers remain unresolved. Production builder lacks the needed row-level CP0107 exclusion lookup and fails closed.
- This CI result is not market-data or strategy evidence. CP-0152 remains `PENDING_EXPLICIT_APPROVAL`; execution `NOT_AUTHORIZED`; candidate build/backtest `NOT_RUN`.
- Gates unchanged: G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`. Profitability is not established.


## CP-0154 — CP-0152 preflight readiness review (2026-10-17)
- Read-only inspection verified the CP-0040 G0 review summary remains `BLOCKED_EXISTING_CP0026_BUILDER_LACKS_ROW_LEVEL_CP0107_QUARANTINE`; CP-0119 provenance remains `BLOCKED_INPUTS_NOT_REPRODUCIBLE`; CP-0117 disposition explicitly says G0 remains blocked.
- Existing frozen manifest is not proof of current production-path exclusion. Builder review records the required row-level CP0107 exclusion lookup is absent. Eleven non-row aggregation blockers remain unresolved.
- Created `evidence/research_scopes/CP0154_CP0152_Preflight_Readiness_HI.md` with prerequisite matrix. CP-0152 explicit approval remains pending; user message “next” is not treated as approval of exact candidate rules.
- ₹10,000 INR→USDT basis, fee evidence, BTCUSDT lot-size/minimum notional and frozen allocation/cash reserve remain unverified/unfrozen. No candidate build or backtest run.
- Gates unchanged: G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`. Profitability `NOT_ESTABLISHED`.


## CP-0155 — Correction to CP-0154 builder finding (2026-10-17)
- **Correction:** CP-0154 incorrectly stated that current builder lacked row-level CP0107 exclusion. Direct source inspection shows generic exact-key manifest validation/exclusion is already integrated: `load_candidate_gate()` lines 135–180; `partition_candidate_rows()` 182–190; production gate load at 497; row exclusion in interval audit at 368; quarantined-row output at 536. CP-0040 integration report documents the same.
- True blocker: the fail-closed gate stops while 11 non-row aggregation blockers remain and eligibility status is not `PASS_CANDIDATE_ELIGIBILITY_READY`. Thus no production candidate build has processed real market rows, and application of the current manifest to real input rows remains unproven.
- Corrected preflight report includes CP-0155 addendum. No market-data candidate build/backtest was run; CP-0152 explicit approval remains pending.
- Prior HEAD `af1da38f0aec95946211690940aed8d9c28002a4` exact-head CI run 39036029613 was SUCCESS. This documentation correction has a new SHA and must be checked at exact HEAD before claiming CI success.
- Gates unchanged: G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.


## CP-0156 — CP-0152 candidate-specific 4h exposure audit (2026-10-17)
- CP-0155 exact-head CI run `39036179330` completed SUCCESS on `4de3fa6d8bdf03045bdd6a059c959cc69fc6230c`; PR #2 was OPEN/unmerged at that head before CP-0156.
- Created `evidence/research_scopes/CP0156_CP0152_4H_Blocker_Exposure_Audit_HI.md`. Read-only crosswalk: the 11 unresolved relationship blockers involve 5m→15m, 15m→30m and 30m→1h; CP-0115 records 0 monthly-divergent keys on 4h. No direct interval overlap with the proposed 4h-only EMA20/EMA50/ATR signal inputs was identified.
- This bounded result does NOT clear G0. Candidate-specific exact rows/hashes, production-path row application, archive coverage/gaps and INR→USDT, fees, lot-size/min-notional and capital allocation assumptions remain unverified. CP-0119 provenance remains blocked and 11 relationship cases remain open.
- CP-0152 explicit approval remains pending. No market data read, no candidate build/backtest, no source case closed, no strategy promoted. Global G0 remains BLOCKED; G2 FAIL_CURRENT_23_CANDIDATES; G3 blocked; G4 insufficient; G6 not built; G7 live blocked.


## CP-0292 — Feature lineage input-prefix binding (2026-10-20)
- Tightened `aists_brain/decision_lineage.py`: every snapshot must declare a valid lowercase `input_prefix_sha256`, and every feature observation's `source_sha256` must exactly equal it.
- Added mismatch/missing-prefix regression tests in `tests/test_market_decision_lineage.py`; updated the existing synthetic harness fixture so its feature-source hash is internally consistent with its declared prefix hash.
- Implementation commit: `af0fd32d1b254634fd794566e1bc12ef357e5b14`; test/fixture correction commit: `97ce79ef6a7512e6839e340ff4818555808d77bc`; checkpoint/report commit: `ff5c12ca649b9b672f153ed8625fb335ada2db62`.
- Initial CI on prior docs head failed because the legacy synthetic harness fixture did not satisfy the strengthened contract. The exact failure and correction are recorded in the CP-0292 report. The current documentation head's Actions result is pending terminal verification; do not infer PASS.
- This is a lineage-consistency safeguard only. It does not prove feature derivation truth or external provenance and does not clear G0/G2/G3 or establish profitability.
- No real market data, candidate build, backtest, paper session, signing, broadcast, or exchange order was performed. PR #2 remains OPEN/unmerged; never merge.
- Report: [CP-0292 Feature Lineage Input-Prefix Binding](evidence/checkpoints/CP0292_Feature_Lineage_Input_Prefix_Binding_HI.md).

- CP-0292 verification addendum: report updated in commit `fa9466a27c917e01d9324d78b67277b98966070b` with the exact-head success for run 39391119850. Current status-file update commit is now being re-verified; do not assume its CI terminal result until fetched.


## CP-0292 subsequent exact-head verification note — 2026-10-20
- GitHub Actions run [39391222478](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39391222478) on then-current head `86bc46b682d117b33591e604c9885883de5ee81a` completed terminal `success`; log confirms compile passed, 233 brain tests passed, and 11 CP-0026 quarantine tests passed.
- The source-hash/input-prefix regression checks are included in the 233 brain tests. This proves internal software-contract behavior only, not honest feature derivation or external market-source provenance.
- PR #2 remained OPEN and unmerged. G0 blocked; G2 current 23 candidates FAIL/not promoted; G3 blocked; G4 insufficient; G6 not built/validated; G7 live blocked. No real-market run, candidate build, backtest, paper session, signing, broadcast, or exchange order was performed.
- This status commit itself requires exact-head CI re-verification.


## Latest documentation-head verification — 2026-10-20
- Branch/PR head `14f5e4c8ecd30bdde066a2d837ff845bb3a16e64` was verified by Actions run [39391875141](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39391875141), terminal `success`. Job steps confirm compile PASS, 233 brain tests PASS, and 11 CP-0026 quarantine tests PASS; log summaries explicitly report `Ran 233 tests` and `Ran 11 tests`, both `OK`.
- PR #2 matched this SHA, OPEN, unmerged, and mergeable at verification. This checkpoint/status update is documentation-only; recheck exact-head CI after these writes.
