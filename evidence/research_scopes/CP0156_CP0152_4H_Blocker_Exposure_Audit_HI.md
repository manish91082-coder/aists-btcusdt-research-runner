# CP-0156 — CP-0152 4h Candidate-Specific Blocker Exposure Audit (Hindi)

Date: 2026-10-17
Status: **READ-ONLY EXPOSURE AUDIT — NO ELIGIBILITY PASS, NO BUILD**
Branch: `cp-0120-ai-brain-foundation`
Candidate under review: `CP0152_4H_EMA20_50_ATR_CAUSAL_LONG`

## 1. Decision

The reviewed evidence shows **no direct interval overlap** between the 11 frozen cross-interval aggregation blockers and the proposed candidate's declared 4h-only signal inputs. This is a bounded exposure finding, not a G0 PASS, not a source-authority decision, and not permission to build/backtest. The global G0 gate remains blocked, and the candidate-specific scope remains pending explicit user approval.

## 2. Evidence reviewed on current branch

- CP-0152 scope proposal: only completed Binance Spot BTCUSDT 4h candles are declared as signal inputs; EMA20, EMA50 and ATR14 are causal functions of those 4h candles.
- CP-0117 blocker matrix: all 11 unresolved cases concern 5m→15m, 15m→30m or 30m→1h relationships. All 11 remain `KEEP_OPEN_EXACT_ROWS_QUARANTINED_RELATIONSHIP_UNRESOLVED`; no canonical source is selected and production candidate metrics were not produced.
- CP-0115 interval exposure crosswalk/current summary: the 14 monthly-divergent keys are in 5m (9), 15m (4), and 30m (1); 4h has zero of these monthly-divergent keys. Existing 4h EMA12/26, RSI and Donchian rows had no direct CP-0113 monthly-divergence interval overlap and historical candidate-scoped G0 `PASS`, but their G2 screens failed. That historic result does not automatically approve the new EMA20/50+ATR candidate.
- CP-0113 field-level corroboration: current checksum-verified trade data corroborated 35/35 daily target bars and 315/315 daily metric fields; monthly values differed for 14 keys / 97 fields. Historical archive-version provenance remains open, canonical source remains `NONE`, and CP-0040 defines no automatic daily-over-monthly precedence.
- CP-0119: historical archive-version provenance `BLOCKED_INPUTS_NOT_REPRODUCIBLE`; 0/11 historical version timelines established; all 11 blockers remain open.
- Current production builder remains fail-closed while unresolved non-row blockers remain and eligibility summary is not `PASS_CANDIDATE_ELIGIBILITY_READY`.

## 3. Candidate-specific exposure matrix

| Check | Observed evidence | Result |
|---|---|---|
| Proposed candidate signal timeframe | 4h only | Declared in scope; actual production input not yet built |
| Intervals named by the 11 unresolved aggregation relationships | 5m, 15m, 30m, 1h | No direct interval match to 4h |
| CP-0115 monthly-divergent keys on 4h | 0 | No direct CP-0113 monthly-divergence key overlap identified |
| Exact candidate input rows and hashes | No CP-0152 candidate build exists | NOT VERIFIED |
| Production-path quarantine behavior on real CP-0152 rows | No candidate build; builder gate blocks before data processing | NOT VERIFIED |
| Historical archive-version authority for the 11 relationships | 0/11 timeline links | OPEN |
| Explicit approval of CP-0152 | Pending | NOT AUTHORIZED |
| Global G0 | `BLOCKED_GLOBAL` | UNCHANGED |

## 4. Interpretation and boundary

A 4h-only design appears less directly exposed to the frozen 5m–1h aggregation cases than lower-timeframe candidates. But interval non-overlap alone does not establish all G0 requirements: the candidate's exact data lineage, actual consumed rows, archive checksums, missing/gap coverage, valuation inputs, capital basis and cost assumptions still require verification. No inferred precedence between daily and monthly archives is allowed.

Do not remove or close any of the 11 blocker cases based on this audit. Do not modify the global builder gate or mark global G0 as PASS. A candidate-specific route, if later justified under the exact frozen CP-0040 rulebook, must explicitly record its scope and evidence and preserve fail-closed behavior for every other candidate.

## 5. Next admissible action

1. Wait for explicit approval of the exact CP-0152 candidate rules.
2. If approved, perform a separate evidence-only readiness check of 4h archive checksums, candidate input range/coverage/gaps, ₹10,000 INR→USDT basis, applicable fees/slippage, lot-size/minimum notional, allocation and cash reserve.
3. Resolve the candidate-specific G0 decision against the frozen rulebook and existing builder controls before any build. If unresolved evidence can influence candidate inputs, keep blocked.
4. Only after an authorized build becomes admissible, prove actual input-row hashes, exact exclusions, output hashes and coverage; then consider a backtest under the frozen acceptance rulebook.

## 6. Non-actions and gates

- No archive downloaded; no raw market data read or modified; no candidate built; no backtest run.
- No source case closed; no canonical source selected; no rulebook threshold changed.
- No strategy promoted; no signing, public broadcast, exchange orders, automatic SL/TP, or live execution.
- G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.
- Profitability `NOT_ESTABLISHED`.
