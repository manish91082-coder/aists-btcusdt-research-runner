# AISTS Execution Discipline: No Drift, No Circular Work

Status: ACTIVE PROJECT WORKING CONTRACT  
Scope: BTCUSDT Spot research and decision-engine project only.  
Canonical execution repository: https://github.com/manish91082-coder/aists-btcusdt-research-runner

## Mission
Build an evidence-backed, cost-aware BTCUSDT Spot research/paper-trading decision engine based on the user's actual starting capital of INR 10,000, and establish whether net profitability exists. Profitability is NOT ESTABLISHED until independently reproducible evidence passes the frozen acceptance criteria.

## Every `next` means
Continue the single highest-value admissible task on the critical path. It is not strategy approval, not permission to backtest while a gate is blocked, and not permission to merge or take exchange actions.

## Required decision loop
1. Read the last verified checkpoint and current live GitHub state.
2. Name the single blocker that most directly prevents the mission goal.
3. Choose exactly one bounded action that can change a gate, resolve a concrete defect, or produce a required decision artifact.
4. Execute it, test it, and verify the result against the exact commit SHA and terminal workflow/job result.
5. Read back the changed GitHub state and report what materially changed.
6. End with the next single action and the mission navigation table.

## Anti-loop rules
- Do not repeat an audit, directory inventory, checksum scan, or issue-status check already marked exhausted unless there is a specific, new trigger (new official response, new artifact/version, changed code, or user-provided evidence).
- Do not create a checkpoint/report/commit merely to show activity or trigger CI. Create one only when it records a new decision, material evidence, a verified defect/fix, or a gate-changing result.
- If a blocker has been checked twice with no new evidence path, stop repeating the same check. Record the route as exhausted and move to a different admissible path, or state precisely which external evidence/authorization is required.
- Never present static CI PASS, documentation growth, or repository activity as strategy validation, data provenance clearance, or profitability.
- Do not invent progress percentages. Report completed gates, blocked gates, and the specific evidence remaining.
- No generic research expansion or new infrastructure work unless it directly unblocks the critical path.

## Evidence and execution safety
- Never fabricate market data, fills, costs, capital conversions, results, or source responses.
- Checksums and ZIP CRC prove byte integrity, not semantic correctness or point-in-time provenance.
- Do not silently substitute current API data for historical point-in-time evidence.
- Preserve unresolved data keys and gaps; do not synthesize/fill candles.
- Do not build/run candidates, backtests, or paper trading while G0 is blocked or before the required explicit strategy approval.
- `next` is not explicit approval of CP-0152.
- No live signing, public broadcast, Binance order placement, merge, or external issue/comment without explicit user authorization.
- Actual capital basis remains INR 10,000. INR-to-USDT basis and allocation remain unfrozen until admissible evidence is recorded. Do not reuse the old 10,000 USDT diagnostic basis.

## Required response format
Every response must include:
- **Goal-direction verdict:** direct progress / necessary blocker decision / no material progress.
- **This turn's material change:** exact artifact, defect, decision, or evidence; if none, say none.
- **Verification:** exact commit SHA, workflow/run and terminal result when applicable. Never infer success from an earlier revision.
- **What remains blocked:** only material blockers.
- **Next action:** one concrete action, no menu of speculative options.
- **Mission Navigation:** G0, G2, G3, G4, G6, G7, profitability status, and distance-to-goal expressed as remaining gates/evidence, not a made-up percentage.

## Frozen known state at adoption
- Canonical historical source: NONE.
- G0: BLOCKED_GLOBAL.
- G2: FAIL_CURRENT_23_CANDIDATES (23/23 historical screen failures).
- G3: BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT.
- G4: INSUFFICIENT_EVIDENCE.
- G6: NOT_BUILT for validated adaptive AI.
- G7: LIVE_BLOCKED.
- Profitability: NOT ESTABLISHED.
- CP-0152: PENDING_EXPLICIT_APPROVAL.
- The latest known exact-head static audit CI passed on commit `60c98ab200538df56bd3a23cc4b32b3efe79c77` (run `39157592063`). Re-verify live state before relying on this as current.

## Immediate critical-path rule
The repeated public correction-directory and CP-0245 manifest scans are exhausted. Do not repeat them. Seek genuinely new official point-in-time/version evidence or follow a separately authorized independent-review path. If neither is available, identify the precise external dependency and do not disguise the blockage as progress.
