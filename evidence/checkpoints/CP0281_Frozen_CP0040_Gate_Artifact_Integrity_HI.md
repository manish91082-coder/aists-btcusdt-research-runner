# CP-0281: Frozen CP-0040 Gate Artifact Integrity (Hindi)

**तारीख:** 2026-10-20  
**Branch:** `cp-0120-ai-brain-foundation`  
**Code/test HEAD:** `b693de4d0c0943249f32df1d46ac6d049a700b9b`  
**CI run:** [39373532513](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39373532513)  
**Scope:** Production candidate-builder के CP-0040 gate inputs की frozen-hash integrity. No market-data access, candidate build, backtest, paper session, or exchange action.

## Finding

CP-0280 ने production CLI path overrides बंद किए थे, लेकिन gate loader manifest hash को supplied summary से compare करता था। इससे self-consistent mutable summary, manifest और blocker artifacts की authenticity को frozen CP-0040 reference के विरुद्ध साबित नहीं करता था। Production gate को independently pinned artifact hashes चाहिए थे।

## Change

Production gate invocation अब `require_frozen_hashes=True` देता है और निम्न frozen CP-0040 SHA-256 values enforce करता है:

- Exact-key manifest: `d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819`
- Non-row blockers: `d0126152a58baecd8f61bcdcc21286ecffacba6427e7b09696ca63db33c1f0d0`

Production mode अब:
1. Actual manifest bytes को frozen manifest hash से bind करता है।
2. Actual blocker bytes को frozen blocker hash से bind करता है।
3. Summary में मौजूद दोनों hashes को भी frozen values से match कराता है।
4. Existing row count, schema, exact-key uniqueness, class counts, source authority, and unresolved-blocker checks जारी रखता है।

Synthetic self-test fixtures frozen production hashes से अलग रह सकते हैं, लेकिन केवल default test mode में; production callsite frozen-hash enforcement explicitly मांगता है। किसी नए adjudicated evidence set को अपनाने के लिए reviewed code/evidence update आवश्यक होगा, summary-only edit पर्याप्त नहीं है।

## Regression / CI verification

- Added tests for a non-frozen manifest, non-frozen blocker artifact, and mutated summary hash.
- Exact latest branch HEAD: `b693de4d0c0943249f32df1d46ac6d049a700b9b`.
- GitHub Actions run [39373532513](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39373532513): **SUCCESS**.
- Compile step: PASS.
- Brain suite: **219 tests passed**.
- CP-0026 quarantine suite: **11 tests passed**, including all three new frozen-artifact regression tests.

## Limits / G0 status

- This closes a code-level integrity gap for the frozen CP-0040 manifest and blocker artifacts; it does not authenticate the historical market source or close any source-adjudication case.
- The frozen blocker set still contains 27 unresolved non-row blockers. Candidate eligibility remains blocked.
- G0 remains `BLOCKED_GLOBAL`; canonical historical source remains `NONE`.
- No candidate build, historical backtest, paper session, live signing, public broadcast, or Binance order was performed.
- PR #2 remains open and unmerged.

## Next action

Continue a bounded source-level audit of other production entry paths for gate-state or artifact substitution bypasses. Do not run the production builder or any historical simulation while G0 is blocked.
