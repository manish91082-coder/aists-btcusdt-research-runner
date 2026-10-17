# AISTS Project Live Status for ChatGPT

Last updated: 2026-10-17
Status checkpoint: CP-0140 verified; next action is goal-direction reset before CP-0141.
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
- Exact branch/PR head SHA: 29bf1f101d81b478b040a8ae3182779bbf81bd5c.
- CI run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39020923719
- CI terminal conclusion: success; recorded terminal output: 132 tests passed (Ran 132 tests ... OK).
- PR #2 state: OPEN, merged_at=null; branch head matches PR head at this checkpoint.
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
