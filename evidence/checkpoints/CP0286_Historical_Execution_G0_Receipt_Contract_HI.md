# CP-0286: Historical Execution Bypass Guard and G0 Receipt Contract (Hindi)

**Checkpoint:** CP-0286  
**Branch:** `cp-0120-ai-brain-foundation`  
**Scope:** Source-level audit and fail-closed execution-entrypoint hardening. No market-data execution, candidate build, historical backtest, or paper session was run.

## 1. निर्णायक निष्कर्ष

CP-0285 ने public direct simulator API को बंद किया था। CP-0286 में उससे अलग runner/script execution paths मिले जो G0 receipt verifier के बिना historical simulation/backtest work शुरू कर सकते थे:

1. `historical_reference_replay`: official monthly archive ZIP/checksum acquisition के बाद `reference_backtest_grid.csv` और `candidate_reference_summary.csv` बनाता है।
2. `monthly_derived_replay`: official daily bars से derived monthly bars बनाकर `monthly_reference_backtest_grid.csv` और candidate reference summary बनाता है।
3. `legacy_pipeline`: CP-0026 candidate builder और CP-0027 baseline backtest invoke करता है।
4. Direct `AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py` CLI: अलग से चलाया जा सकता था।
5. `cp0040_quarantine_sensitivity_run`: baseline replay और gate पास होने पर quarantine sensitivity simulation चलाने वाला task है।

इन scripts में promotion रोकने वाले diagnostics मौजूद थे, लेकिन promotion रोकना और historical simulation को G0 से पहले रोकना दो अलग controls हैं। User/project की current boundary के अनुसार, G0 authorization receipt verifier उपलब्ध न होने तक इन execution paths को शुरू नहीं होना चाहिए।

## 2. Implemented guard

New helper: `scripts/g0_execution_guard.py`

Protected tasks:
- `historical_reference_replay`
- `monthly_derived_replay`
- `legacy_pipeline`
- `cp0027_baseline_backtest`
- `cp0040_quarantine_sensitivity_run`

Changes:
- `scripts/aists_runner.py` protected task को child process शुरू करने से पहले `G0_EVIDENCE_NOT_AUTHENTICATED` के साथ block करता है और runner summary में `BLOCKED_G0_AUTHORIZATION` दर्ज करता है।
- सभी पाँच direct CLI entrypoints में `main()` के पहले काम से पहले वही fail-closed guard call होता है।
- `tests/test_market_g0_execution_guard.py` protected task inventory, guard rejection और direct-entrypoint placement verify करता है।
- यह guard जानबूझकर कोई caller-supplied `PASS` स्वीकार नहीं करता। इसे हटाना या bypass करना तब तक अनुमत नहीं, जब तक trusted independent G0 receipt verifier integrate और test न हो।

## 3. Historical replay API inventory

`aists_brain.historical_replay.replay_decisions()` inspected tree में केवल module और its unit-test usage में मिला; reviewed runner/entrypoint scripts में इसका production caller नहीं मिला। यह bounded source inventory है, पूरे repository के हर संभावित external caller का proof नहीं।

यह API caller-supplied `provenance_gate="PASS"` स्वीकार करती है, और module की limitations स्वयं कहती हैं कि provenance gate independently adjudicated नहीं है। इसे G0 authorization या historical source acceptance के रूप में इस्तेमाल नहीं किया जा सकता।

## 4. Frozen CP-0040 evidence bindings

The original frozen CP-0040 baseline must remain identifiable and must not be overwritten by a mutable “current” pointer:

- Frozen rulebook SHA-256: `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`
- Baseline exact-key quarantine manifest: 969 rows; SHA-256 `d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819`
- Baseline non-row blocker inventory: 27 rows; SHA-256 `d0126152a58baecd8f61bcdcc21286ecffacba6427e7b096ca63db33c1f0d0`

Later additive evidence is not equivalent to closure of the original cases:
- CP-0040 aggregation-extension snapshot `CP0040_Run_38883792900` records 1,427 unique exact keys, manifest SHA-256 `e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a`.
- That snapshot records 11 non-row aggregation blockers, SHA-256 `f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36`.
- Its summary states canonical source selected = false and source cases closed = 0.

Therefore, a future G0 receipt must bind both the immutable baseline population and the complete append-only evidence lineage/current population. It must not silently substitute one population for another or interpret “all implicated keys quarantined” as source adjudication.

## 5. Proposed trusted G0 receipt contract (design only)

No executable verifier or G0 PASS receipt was created in CP-0286 because an independently trusted signing identity/public-key root has not been established in this checkpoint. Creating a local key and trusting its own receipt would not constitute independent adjudication.

A valid future receipt must require, at minimum:

1. **Identity and scope:** unique receipt ID, issued-at UTC, issuing reviewer identity/role, repository and exact commit SHA, and receipt schema version.
2. **Frozen policy binding:** exact CP-0040 rulebook path + SHA-256 and the existing provenance-only rulebook receipt. That provenance receipt alone is not authorization.
3. **Population binding:** path, byte count, SHA-256, row count and lineage for the 969-row/27-blocker baseline plus all subsequent append-only manifest/blocker extensions, including the latest 1,427-row/11-blocker snapshot.
4. **Clause-level adjudication:** G0-A through G0-E each must have an explicit PASS/FAIL/UNKNOWN, evidence references and hashes, reviewer rationale, and independent reviewer attestation. Any UNKNOWN, missing evidence, hash mismatch, unresolved signal-relevant conflict, or missing source authority means global G0 remains blocked.
5. **Source authority:** explicit named canonical historical source and evidence supporting authority, not merely checksum correctness or third-party overlap.
6. **Cryptographic authenticity:** detached signature over canonicalized receipt payload, verified using a public key/trust root configured independently of the receipt itself. A public key supplied only inside the same receipt is not trusted.
7. **Freshness and revocation:** issued-at/expiry or review-validity policy, revocation check, exact repository-head binding, and rejection of stale receipts or superseded evidence.
8. **Fail-closed semantics:** no user/caller-provided `PASS` string or boolean may authorize a run. Only the trusted verifier may return an authenticated, exact-scope authorization result.

The receipt contract is not complete until the independent trust root, reviewer authority, revocation mechanism and evidence location are established. Do not implement a pretend verifier around a hard-coded PASS.

## 6. Verification

Protected-entrypoint code/test HEAD:
`9ccb9a4919129e2c3d75afb7c7b967c5224ae80a`

- [GitHub Actions run 39381382642](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39381382642): terminal **success** for that exact HEAD.
- Brain unit suite: **226 tests passed**, including the new G0 execution guard tests.
- CP-0026 exact-key quarantine suite: **11 tests passed**.
- Compile step: success.

This CI run verifies the code/test HEAD above, not this report's eventual commit. A new exact-HEAD CI run is required after the report is committed.

## 7. Gate status and safety

- G0: **BLOCKED_GLOBAL**; canonical historical source remains **NONE**.
- G1: **PARTIAL_SYSTEM_LEVEL**.
- G2: current candidates remain **FAIL / NOT PROMOTED**.
- G3: blocked while source/quarantine effects remain unresolved.
- G4: **INSUFFICIENT_EVIDENCE**.
- G5: **NOT_RUN**.
- G6: **NOT_BUILT / NOT_VALIDATED**.
- G7: **LIVE_BLOCKED**.
- Profitability: **NOT ESTABLISHED**.
- No candidate builder, historical backtest, paper session, live signing, public broadcast or exchange order was executed in this checkpoint.
- PR #2 remains open and unmerged.

## 8. Next autonomous decision

CP-0287 should establish the missing trust-root decision without inventing one: inspect existing GitHub repository protections/maintainer-controlled evidence locations and the independent adjudication issue, then record exactly who or what can authoritatively sign the G0-A..G0-E receipt. If no independent trust root is available, leave verifier implementation blocked and focus on obtaining clause-level independent adjudication and canonical-source authority. Do not weaken the receipt requirements to force a PASS.

**Mission navigation:** CP-0286 blocks five historical simulation entrypoints; global G0 remains BLOCKED. This is execution-safety progress, not source acceptance or profitability evidence.
