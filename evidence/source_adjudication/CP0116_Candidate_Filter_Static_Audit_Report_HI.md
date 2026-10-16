# CP-0116: CP-0026 builder exact-key filter static audit

**Date:** 2026-10-16
**Status:** `PASS_STATIC_AND_SYNTHETIC_KEY_FILTER_AUDIT_G0_STILL_BLOCKED`
**Scope:** frozen source-code control-flow analysis and synthetic function-level probes only. No production candidate build or backtest.

## 1. Execution proof
- GitHub Actions: [run 38942395977](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38942395977), head commit `d4ed30d0f7cecd9480c17e24cc79ec2a22fc96ac`; workflow and primary runner job both `success`.
- Runner: `PASS`, 11/11 checks. Child task: `PASS_STATIC_AND_SYNTHETIC_KEY_FILTER_AUDIT_G0_STILL_BLOCKED`.
- Child summary SHA-256: `aa8c903ecdd5b876355b389d3846aace6444e5b8770721ae6d69ec496d287242`.
- Artifact: [12063652242](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38942395977/artifacts/12063652242), 9,113 bytes, archive SHA-256 `d257f101fb1af7d11ed64e831e62705a3c40315cc75a7591f317f16f13b58042`, seven-day retention.
- Run-generated report inside the artifact: 2,331 bytes, SHA-256 `81549aca95eb826b75c04740e0a4ebbbef3d7627bb21df3cbe8ba3cdc8e543c4`.
- Run-generated exact-key probe CSV inside the artifact: 5,322 bytes, SHA-256 `7bef46faaffcb37c165cde9cbf6a628f1d55aefe9afa21de5cc1833a53d06a6f`.

## 2. Immutable inputs verified
- CP-0026 builder, Git blob SHA-1 `06e9f292603b1f4755bea4c28ef027a01e2226d1`.
- CP-0040 exact-key quarantine helper, Git blob SHA-1 `ff756af2f27d307779cde92f41a842467ada2d77`.
- Exact-key manifest: 1,427 rows / 1,427 unique keys; manifest SHA-256 matches its frozen summary. Git blob SHA-1 `8d956499b8f5053335b738cc408ca8859d326a3d`.
- Manifest summary Git blob SHA-1 `964197632042dd3c761ab25cf32921601ed74e4f`.
- Non-row blocker CSV Git blob SHA-1 `d3fca23bac424fa8c8b187434e8c63e8d188a0e1`; 11 rows remain.
- CP-0113 pointer/report and CP-0040 frozen rulebook identities all matched their expected hashes.

## 3. Code-path finding
- In CP-0026 `main()`, `load_candidate_gate(...)` is called at line 497, before reading the flagged-date input at line 499, creating the candidate output directory at line 514, or entering the interval loop at line 521.
- The gate verifies the manifest SHA-256, row count, exact-key schema, unique keys, case-class counts, open cases and canonical-source constraints. It then deliberately fails closed because 11 non-row blockers remain and the summary says candidate eligibility is blocked. Expected message: `G0_BLOCKED_NONROW_BLOCKERS_REMAIN: 11 unresolved non-row cases`.
- Inside `audit_and_write_interval`, the exact key is `(interval, str(open_time_ms))`. A matching row is recorded in the quarantine list and control continues before `writer.writerow(r)`, so the branch is placed before candidate output writing.
- The standalone `partition_candidate_rows` helper uses the same interval plus exact timestamp-string equality. It does not round timestamps or apply a cross-interval match.

## 4. Runtime tests that did execute
| Test | Result |
|---|---:|
| Static audit assertions | 20/20 PASS |
| Existing builder gate self-test using actual frozen manifest, blocker CSV and summary | 5/5 PASS |
| CP-0113 unique target keys covered by manifest | 35/35 |
| Synthetic target rows excluded by production partition function | 35/35 excluded, 0 kept |
| One-millisecond neighbour behavior | Correct: neighbor retained |
| Same timestamp in a different interval | Correct: not excluded by the 5m key |

The 35-row probe contains constructed dictionaries only. These results prove the filtering function's exact-key behavior for the frozen key universe; they do not prove that a production candidate output was written with those rows removed.

## 5. Decision and limits
**Established:** the exact-key quarantine implementation is present; its inline writer branch is correctly ordered; the function-level filter behaves correctly on all 35 target keys; and the current builder gate remains fail-closed.

**Not established:** candidate-specific quarantine application to real candidate files. Production `main()` was not invoked, real candle rows were not read into the builder, and no candidate dataset was built. The CP-0040 sensitivity run's prior 0/14 key overlap is a diagnostic applied-key list, not a contradiction of the CP-0026 code path; the actual builder path is still blocked before execution of that path.

Current disposition remains: global G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`; canonical source `NONE`; source cases closed `0`; 11 non-row aggregation blockers unresolved.

## 6. Non-actions and next step
- No network requests, archive downloads, raw source edits, timestamp shifts, synthetic research candles, production candidate output, backtest, promotion, signing, broadcast or Binance orders.
- Next: continue the frozen CP-0040 rulebook-bound disposition of the 11 non-row aggregation blockers. Do not bypass the guard or invent daily-over-monthly precedence.
