# CP-0293 — Source-feature verification boundary and G0 unblock contract (2026-10-20)

## Goal-directed decision
The latest code increment closed a concrete software-integrity gap: stored/decision features are now recomputed from the supplied causal candle prefix and compared against the claimed feature values and lineage hashes before the research harness proceeds. This reduces internal tampering risk, but it cannot establish that the supplied historical candles are an admissible canonical source. G0 therefore remains the controlling blocker; do not use more code work as a substitute for independent source adjudication.

## Live GitHub state verified
- Repository: https://github.com/manish91082-coder/aists-btcusdt-research-runner
- Branch: `cp-0120-ai-brain-foundation`
- HEAD: `473ef1e950d892801782aec71b89e4ae06bde9e9`
- PR #2: OPEN, unmerged; head matches the branch. Keep it open; do not merge without explicit user approval.
- Push Actions run [39402003605](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39402003605): terminal success on exact HEAD.
- PR Actions run [39402010103](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39402010103): terminal success on exact HEAD.
- Inspected job steps for both runs: Python compile passed; brain unit-test step passed (236 tests); CP-0026 exact-key quarantine enforcement passed (11 tests).

## Change represented by the current HEAD
- `aists_brain/source_feature_verifier.py` recomputes prefix hash and market context from supplied source candle rows and validates feature values, cutoff/timeframe and source binding.
- `aists_brain/research_harness.py` invokes this check before offline simulation and in the stored-artifact path, bound to the provenance-cleared interval.
- Regression tests reject tampered feature values and altered hashes even when snapshot/payload hashes are recomputed.
- Boundary: this validates derivation from the supplied rows; it does not authenticate archive origin, archive version history, source completeness, strategy quality, profitability or live readiness.

## G0 evidence contract and smallest actionable request
G0 can be reconsidered only when an independent, trusted reviewer supplies a dated and verifiable adjudication for each frozen CP-0040 clause G0-A through G0-E, bound to:
1. the exact frozen acceptance-rulebook SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`;
2. the evidence-population/manifest identity and its applicable quarantine state;
3. a named canonical historical source and direct evidence for archive/version/correction history for the disputed cases;
4. reviewer identity/independence, timestamp, and detached signature validated against a trust root configured independently of the submitted receipt; and
5. freshness/revocation and fail-closed validation.

A maintainer response or official source evidence may resolve particular clauses, but it must be captured and reconciled clause-by-clause. Do not treat an issue being open, a checksum pass, or an internally signed-by-owner note as independent adjudication. No external issue/comment was posted by this checkpoint.

## Frozen evidence and gate state
- Frozen CP-0040 rulebook remains unchanged. Baseline exact-key quarantine manifest SHA-256: `d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819`; baseline non-row blocker SHA-256: `d0126152a58baecd8f61bcdcc21286ecffacba6427e7b096ca63db33c1f0d0`.
- Prior CP-0106/CP-0151 evidence remains diagnostic only: disputed timestamp/value rows remain quarantined; no canonical source selected; no case is closed by this code change.
- G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL / NOT PROMOTED`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT / NOT_VALIDATED`; G7 `LIVE_BLOCKED`; profitability `NOT ESTABLISHED`.

## Next decision
Wait for new independent G0 adjudication or official archive-version evidence. On receipt, validate its trust and exact scope, reconcile G0-A..G0-E against the frozen rulebook, and update only the clauses the evidence actually resolves. Until then, no real-market backtest, candidate promotion, paper session, signing, broadcast or exchange order. Avoid further infrastructure-only changes that do not remove a demonstrated blocker.
