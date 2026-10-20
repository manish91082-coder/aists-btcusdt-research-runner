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
