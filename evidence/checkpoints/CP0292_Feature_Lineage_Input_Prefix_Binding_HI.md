# CP-0292 — Feature lineage input-prefix binding (2026-10-20)

## Goal-directed finding
The causal decision validator checked that every feature `source_sha256` looked like a lowercase SHA-256, but it did not bind that value to the same snapshot's declared `input_prefix_sha256`. An internally inconsistent feature/source lineage could therefore pass this portion of the contract after the snapshot was re-hashed.

## Change
- Updated `aists_brain/decision_lineage.py` to require a valid lowercase `input_prefix_sha256` on each decision snapshot.
- Each feature observation's `source_sha256` must now exactly match that declared input-prefix hash.
- Added regression tests for a mismatching feature source hash and a missing input-prefix hash in `tests/test_market_decision_lineage.py`.
- Implementation commit: `af0fd32d1b254634fd794566e1bc12ef357e5b14`.
- Regression-test commit: `b3ecf194a25e115739b8808f488d02bb4eed91b0`.

## Verification boundary
GitHub Actions terminal result for the final branch head is to be recorded only after the run is fetched and its job logs are inspected. No test result is inferred from the commits alone.

## Impact and limitations
This tightens internal causal-lineage consistency. It does not independently prove feature values were derived honestly from the claimed candle prefix, authenticate source provenance, resolve G0, clear G2/G3, validate a strategy, or establish profitability. No market data was read; no candidate build, backtest, paper session, exchange order, signing or broadcast was performed.

## Gate state
- G0: `BLOCKED_GLOBAL`; canonical historical source remains `NONE`.
- G2: current 23 candidates remain `FAIL / NOT PROMOTED`.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- G4: `INSUFFICIENT_EVIDENCE`; G6: `NOT_BUILT / NOT_VALIDATED`; G7: `LIVE_BLOCKED`.
- PR #2 must remain OPEN and unmerged.

## Verification correction
- Initial exact-head CI run [39390971344](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39390971344) failed: compile passed, but the legacy synthetic fixture in `tests/test_market_research_harness.py` lacked the now-required `input_prefix_sha256` and used an unrelated feature source hash. This was a test-fixture contract mismatch, not a market-data failure.
- Updated that fixture to declare the same synthetic test hash for the input prefix and feature source. New test commit: `97ce79ef6a7512e6839e340ff4818555808d77bc`. Final exact-head CI remains to be rechecked.

## Final exact-head verification
- Final status/documentation head at verification: `9a9d4df818a190723401134320403ac73445e246`; PR #2 head matched exactly and remained OPEN, unmerged, mergeable.
- GitHub Actions run [39391119850](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39391119850) completed `success` on that exact head. Compile passed; all 233 brain tests passed (`OK`); all 11 CP-0026 exact-key quarantine tests passed (`OK`). The two new lineage regression tests and the updated research-harness fixture passed.
- An earlier run failed because a legacy test fixture did not declare the newly required prefix hash; the fixture was corrected and the subsequent exact-head runs passed. The failure and fix are retained here rather than hidden.
- These results verify software behavior only, not market-data provenance, candidate eligibility, or profitability.


## Subsequent exact-head re-verification
- The later documentation head `86bc46b682d117b33591e604c9885883de5ee81a` was associated with GitHub Actions run [39391222478](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39391222478), terminal `success`. Its job log confirms Python compile passed, all 233 brain unit tests passed (`OK`), and all 11 CP-0026 quarantine tests passed (`OK`). The CP-0292 source-hash consistency tests are included in the 233 brain tests.
- PR #2 was re-fetched and remained OPEN, `merged=false`; its head matched `86bc46b682d117b33591e604c9885883de5ee81a` before this report update. Because this report update creates a newer head, final verification must be repeated for the resulting head.
- Gates unchanged: G0 blocked; G2 23 candidates fail/not promoted; G3 blocked; G4 insufficient; G6 not built/validated; G7 live blocked. No real-market research was run.


## Latest documentation-head verification — 2026-10-20
- Branch/PR head `14f5e4c8ecd30bdde066a2d837ff845bb3a16e64` was verified by Actions run [39391875141](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39391875141), terminal `success`. Job steps confirm compile PASS, 233 brain tests PASS, and 11 CP-0026 quarantine tests PASS; log summaries explicitly report `Ran 233 tests` and `Ran 11 tests`, both `OK`.
- PR #2 matched this SHA, OPEN, unmerged, and mergeable at verification. This checkpoint/status update is documentation-only; recheck exact-head CI after these writes.


## CP-0292 exact-HEAD re-verification — 2026-10-20 (branch head efa52287a3f7955b9fcf1cdeb0fde30dc9cc962a)
- Live branch and PR #2 head exactly matched `efa52287a3f7955b9fcf1cdeb0fde30dc9cc962a`; PR #2 remains OPEN, merged=false, mergeable=true. No merge performed.
- Exact-HEAD push Actions run [39391953169](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39391953169) and pull_request Actions run [39391960946](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39391960946) both completed terminal `success` on `efa52287a3f7955b9fcf1cdeb0fde30dc9cc962a`. Each job log confirms compile step passed, `Ran 233 tests` / `OK`, and `Ran 11 tests` / `OK` for CP-0026 exact-key quarantine enforcement; both new CP-0292 regression tests passed.
- Files verified on this head: `aists_brain/decision_lineage.py` blob `08426fa9dd157e220f04bbc552202030a183706d`; `tests/test_market_decision_lineage.py` blob `a88fa30af7ee7b9f2737ca5632f2d1180fc066ba`.
- Follow-on read-only review: selector input contract remains fail-closed for unknown actions, unsupported strategy families, invalid order flags, missing timeframe evaluations, directional disagreement and weak confirmations. Quarantine builder validates frozen CP-0040 manifest/blocker hashes and fails closed while 27 non-row blockers exist (11 aggregation, 16 daily-reference acquisition); however real candidate-path quarantine effect and candidate-specific final metrics remain unproven because no production candidate build has run.
- Hash semantic limit remains explicit: equality of `source_sha256` and `input_prefix_sha256` enforces artifact consistency, not proof that the named hash was computed from the actual causal candle prefix or that feature values were derived from it. No producer implementing that semantic was verified here. Do not overclaim lineage authenticity.
- Gate states unchanged: G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 current 23 candidates `FAIL / NOT PROMOTED`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT / NOT_VALIDATED`; G7 `LIVE_BLOCKED`; profitability `NOT ESTABLISHED`. No real market data, candidate build, backtest, paper session, exchange signing, public broadcast or order was performed.
- Recommended next bounded task: verify current producer / feature-artifact schema for real prefix-hash semantics. If no producer exists, document the missing causal derivation contract without inventing a producer. Continue G3 remains evidence-blocked; do not rerun exhausted G0 source searches.


## CP-0292 documentation-head exact verification — 2026-10-20
- Final documentation branch/PR HEAD: `64964969843d6f087695bd8bb51342fa71c2586d`; exact-HEAD push run [39393790994](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39393790994) completed terminal `success`. The job completed compile, brain unit tests, and CP-0026 exact-key quarantine tests successfully; logs confirm 233 brain tests and 11 quarantine tests passed, including both CP-0292 regression tests.
- Exact commit `64964969843d6f087695bd8bb51342fa71c2586d` is also live PR #2 head. PR remains OPEN, `merged=false`, mergeable=true. No merge occurred.
- This is a documentation-only exact-head re-verification. Software tests are PASS; empirical market-data provenance/profitability remain unvalidated. All frozen gate states unchanged; no candidate build/backtest/live operation performed.


## CP-0292 final documentation HEAD verification — 2026-10-20
- Current branch and PR #2 HEAD `1a1cdde251d6125b6e32bc63560ecca4b7c7d179` verified; Actions run [39393866585](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39393866585) is terminal `success` on the exact same HEAD. Compile step, brain unit tests, and CP-0026 exact-key quarantine tests all completed successfully. Run logs for the same test workflow on immediately preceding exact-head commits confirm 233 brain tests and 11 quarantine tests, including both CP-0292 regression tests, PASS; the current run's steps are all SUCCESS.
- PR #2 remains OPEN and unmerged. No merge performed.
- Software validation only. G0 remains BLOCKED_GLOBAL, G2 current 23 candidates FAIL / NOT PROMOTED, G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT, G4 INSUFFICIENT_EVIDENCE, G5 NOT_RUN, G6 NOT_BUILT / NOT_VALIDATED, G7 LIVE_BLOCKED, profitability NOT ESTABLISHED. No real-market research, candidate build, backtest, paper session, signing, broadcast or order performed.
- Next bounded review: establish whether a trusted feature producer computes `input_prefix_sha256` from the actual causal prefix bytes/records. Hash equality alone cannot establish derivation authenticity. Do not repeat exhausted G0 source searches.
