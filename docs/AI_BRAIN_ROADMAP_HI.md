# AISTS AI Brain Roadmap (Hindi)

Updated: 2026-10-17
Latest checkpoint: CP-0130
Implementation branch: `cp-0120-ai-brain-foundation`
Canonical repository: https://github.com/manish91082-coder/aists-btcusdt-research-runner
Pull request: https://github.com/manish91082-coder/aists-btcusdt-research-runner/pull/2

## Goal
Build a BTCUSDT-first, long-only Binance Spot decision system for planning capital of INR 10,000 converted to USDT. It should combine multi-timeframe market context, technical/volume analysis, a strategy library, strategy selection, risk/capital controls, and a controlled learning loop. This roadmap does not promise profitability. Live signing, order placement, and public broadcast remain disabled.

## Execution order
1. **Brain contract and architecture** — stable inputs/outputs, completed-candle semantics, abstention, versioning, and no-order boundary.
2. **Market context and regime** — trend, momentum, volatility, volume, support/resistance references, and data-quality flags for 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mo.
3. **Strategy library** — established strategy families with explicit entry/exit rules, regime suitability, cost assumptions, and failure conditions.
4. **Strategy selector / meta-brain** — compare eligible strategies for current regime/timeframe; allow NO_TRADE when evidence is weak or signals conflict.
5. **Learning and discovery** — causal feature pipeline, versioned model training, search-trial ledger, benchmark comparison, calibration, and drift monitoring. No self-promotion without independent gates.
6. **Risk and capital engine** — INR 10,000 planning capital converted to USDT, position sizing, exposure limits, fees/slippage, BNB discount economics. Do not silently change the user's no-automatic-SL/TP preference.
7. **Historical validation** — preserve source lineage, chronological train/validation/OOS splits, leakage prevention, regime-wise net results.
8. **Paper evaluation** — frozen version, append-only decisions and virtual portfolio ledger, observation coverage and acceptance gates.
9. **Exchange readiness** — separate future review only. Live trading is not authorized by this roadmap.

## Completion ledger
- **Existing baseline code:** CP-0026 provenance-aware candidate builder; CP-0027 deterministic EMA/RSI/Donchian baseline with buy-and-hold and cash benchmarks. These are not adaptive AI.
- **Existing audit infrastructure:** source manifests, checksum verification, source-conflict evidence and append-only checkpoints.
- **Implemented in CP-0120 branch:** `aists_brain/market_context.py` computes EMA20/EMA50, RSI14, ATR14, 10-bar momentum, relative volume and prior-lookback support/resistance references; validates OHLC and timestamp ordering.
- **Implemented in CP-0121 branch:** `aists_brain/market_regime.py` classifies descriptive trend/breakout/breakdown/mixed regimes and volume state. It abstains on limited history; high volatility requires a causal historical ATR percentile.
- **Implemented in CP-0122 branch:** `aists_brain/strategy_candidates.py` evaluates three transparent strategy families (trend-following, breakout, mean reversion) and abstains on insufficient data, low-volume breakout, or strategy conflict. Candidate output is not an order.
- **Unit tests added:** seven market-context tests, seven regime tests, and six strategy-candidate tests. CI compiles all three modules and discovers `test_market_*.py`. Do not call CI PASS until a successful Actions run is actually verified.
- **Implemented CP-0123/CP-0124 (CI verification pending):** `aists_brain/multi_timeframe.py` joins all eight supported timeframes without filling missing frames; any missing/limited frame forces a non-trade readiness state. `aists_brain/causal_volatility.py` ranks current ATR% only against prior observations and returns unavailable when history is insufficient. These modules require upstream completed-candle, gap and provenance validation.
- **Implemented CP-0125 (CI verification pending):** `aists_brain/multi_timeframe_selector.py` requires a ready eight-timeframe snapshot, bullish directional alignment, complete candidate evaluations, and at least three timeframes agreeing on one strategy family. It abstains on missing evidence, conflict or weak confirmation. Output remains a research candidate, not an order.
- **Implemented CP-0126 (CI verified on prior head):** `aists_brain/historical_replay.py` replays timestamped, precomputed snapshots only when the caller supplies an explicit provenance PASS and a source manifest containing SHA-256 values. It enforces increasing decision timestamps and rejects snapshots timestamped after the decision. It deliberately reports `REPLAYED_NO_PNL`; it is not a market-data loader or profitability backtest. The caller-supplied provenance gate is not independently adjudicated by this module.
- **Implemented CP-0127 (CI verified on prior head):** `aists_brain/capital_risk.py` calculates planning-only USDT conversion, allocation/position caps, and simple round-trip fee/slippage sensitivity. FX, fee, slippage, allocation and BNB-discount values are explicit assumptions, not live verified terms. It adds no automatic SL/TP and emits no order instruction.
- **Implemented CP-0128 (CI verified on commit `9989def`):** `aists_brain/paper_portfolio.py` tracks caller-supplied simulated Spot fills in a hash-chained in-memory journal. It accounts for cash, BTC inventory, average-cost realized P&L and recorded fees; it rejects overspending, shorting, duplicate decision IDs, bad timestamps and tampering. Prices and fills are hypothetical caller inputs.
- **NOT DONE:** source-gate adjudication, integration with verified historical candle files, fill-based fee/slippage portfolio backtest, trained/adaptive AI, verified account fee tier, paper acceptance, live readiness.
- **Last known research gates:** G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. Code milestones do not override these gates.
- Historical source-provenance blockers remain open. Independent brain modules can be developed and unit-tested, but historical performance claims remain blocked until applicable data gates pass.

## CP-0127 source-gate inspection and next step
- CP-0119 was inspected from the current repository tree: `BLOCKED_INPUTS_NOT_REPRODUCIBLE`; 11/11 aggregation blockers remain open, 0 source cases closed, no canonical source selected. Current daily/monthly archive identities are recorded, but historical version timeline links established = 0. Binance issue #504 remained open with zero comments in the recorded snapshot; no maintainer answer was observed.
- This is an evidence gap, not proof that historical versions do not exist. No production candidate build, backtest, strategy promotion or data repair was performed as part of this inspection.
- Keep G0 `BLOCKED_GLOBAL`, G2 `FAIL_CURRENT_23_CANDIDATES`, G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`, G4 `INSUFFICIENT_EVIDENCE`, G6 `NOT_BUILT`, and G7 `LIVE_BLOCKED` until their own evidence gates change.
- **Implemented CP-0129 (CI verified on commit `15858c5`; 61/61 tests passed):** `paper_portfolio.py` now binds eligible research-candidate fills to a brain version, causal snapshot SHA-256, decision timestamp, selected strategy and confirming timeframes. It adds append-only JSONL persistence, reconstruction on restart, hash-chain verification, prefix-only append, rollback refusal and tamper/truncation checks. The JSONL writer is single-writer only; this is not tamper-proof external storage, and all fills remain hypothetical.
- **CP-0129 verification and next step:** CI run [39017061105](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39017061105) completed successfully on exact commit `15858c57fbd67049b9b470288c5c039caee8a3aa`; Python compilation passed and 61/61 tests passed. The next goal-directed step is to resolve the historical data provenance gate before any performance run, then build a no-lookahead, cost-aware fill simulator using only provenance-cleared market data. Do not fabricate performance or bypass the blocked source gate.


## CP-0130 — Cost-aware next-open simulator (2026-10-17)
- Added `aists_brain/cost_aware_simulator.py`, a pure offline simulator that accepts caller-supplied candle bars and explicit research actions. It fills only at the immediately next contiguous bar open after the referenced candle close, applies configurable per-side fee and slippage assumptions, enforces one long position at a time, and logs gap-skipped decisions.
- Added seven deterministic unit tests for cost-adjusted fill prices, gap skip behavior, no-trade/no-automatic-SL/TP behavior, open-position marking, timestamp contract, duplicate decisions, invalid allocation, and candle ordering.
- The simulator does **not** generate signals, adjudicate source provenance, fetch data, or place orders. Test candles are synthetic fixtures solely for engine correctness. No historical performance was computed.
- Updated CI compilation to include the new simulator. CP-0130 is not complete until GitHub Actions passes on the exact final branch HEAD.
- Existing source gate remains unchanged: global G0 `BLOCKED_GLOBAL`; the frozen `MTF_BREAKOUT_4H_D1` diagnostic has candidate-specific quarantine eligibility only, but G2 remains FAIL/NOT PROMOTED and G3 remains blocked due material TRAIN sensitivity. No candidate or strategy is promoted.
- Next: verify CI, then integrate only provenance-cleared historical candle inputs and independent accounting reconciliation. If the current data gate remains blocked, do not run a performance backtest or invent results.


## CP-0131 — Provenance-bound historical candle input guard (2026-10-17)
- Added `aists_brain/provenance_input.py`: offline CSV loader bound to a JSON manifest via SHA-256. It fails closed unless the manifest explicitly claims both adjudication PASS and global G0 PASS, identifies BTCUSDT Spot and a supported interval, supplies valid source/archive/report hashes, reports at least 99.5% coverage, accounts for all missing intervals and gap events, and certifies completed candles only.
- The loader independently verifies the actual CSV hash, row count, first/last timestamps, timestamp order, candle interval duration, finite OHLCV, OHLC range and non-negative volume. It does not repair gaps or alter source data.
- Important boundary: this code validates manifest claims and file integrity, but does not authenticate the adjudicator or prove the historical archive-version provenance itself. A manifest cannot legitimately claim PASS until external evidence independently supports it.
- Added 10 unit tests for accepted contract, blocked global gate, tampering, interval mismatch, coverage, gap accounting, OHLC, row count and source hashes. CI compiles the new module and discovers the test file.
- **No historical performance run was performed.** Current global G0 remains `BLOCKED_GLOBAL`, so real project data must continue to fail closed until the existing evidence gap is independently resolved. No source data, frozen acceptance rulebook, strategy gate, or live-trading control was changed.
- Next: verify the complete test suite on the exact final branch HEAD and inspect CI logs; if green, move to a manifest-driven integration harness that refuses to run when G0 is blocked.


## CP-0132 — Manifest-driven research integration harness (2026-10-17)
- Added `aists_brain/research_harness.py` to join the provenance-bound candle loader with the offline next-open simulator. It requires the data manifest's explicit adjudication and global G0 PASS claims, and a separate decision artifact bound to the exact candle CSV SHA-256 with a non-empty brain version.
- The harness rejects blocked/mismatched data, wrong timeframe, non-PASS decision artifacts, missing brain version and decisions that do not reference a supplied candle close. It emits a combined result with data, manifest and decision artifact hashes plus the simulator result.
- Added seven integration tests covering successful wiring and fail-closed cases. CI compilation now includes the harness.
- **Trust boundary remains explicit:** PASS labels and source report hashes are not authenticated by this harness. It does not generate decisions, validate the decision producer's causal lineage, resolve historical archive-version provenance, or establish strategy profitability. Current project G0 remains BLOCKED_GLOBAL; therefore the real unresolved data must not be relabelled PASS merely to run this harness.
- No real-market performance run, source-data mutation, gate relaxation, SL/TP addition or live exchange action occurred.
- Next: verify the complete CI suite on exact final HEAD; then build independent accounting reconciliation for simulator events versus paper portfolio ledger before any accepted paper run.


## CP-0133 — Independent simulator / paper-ledger reconciliation (2026-10-17)
- Added `aists_brain/accounting_reconciliation.py` to recompute cash flows, BTC inventory, recorded fees and exit-cost-adjusted marked equity from the simulator's ordered fill events, then compare the independent arithmetic with both the simulator output and hash-verified paper ledger.
- Reconciler checks event counts, decision IDs, fill timestamps, sides, quantities, prices, fees, notionals, no-short inventory, ending cash, BTC quantity, cumulative fees and mark-to-market arithmetic. Any mismatch raises a reconciliation error rather than being silently tolerated.
- Added six tests for successful reconciliation and deliberate cash, event-ID/hash, fee, equity and event-count mismatches. CI compilation now includes the reconciler.
- This is accounting consistency only. It does not authenticate source provenance, verify Binance fee terms, validate decisions, establish profitability, or make hypothetical fills real.
- Integrated the reconciler into `aists_brain/research_harness.py`: every successful harness simulation now builds a hypothetical paper ledger from the simulator fills, runs independent accounting reconciliation, and verifies the ledger hash chain. The harness returns both results; its integration test asserts both PASS statuses. This is not a real exchange ledger or a profitability gate.
- Next: verify CI on the exact final HEAD. Preserve all current blocked research gates.

## CP-0134 — End-to-end research audit report (2026-10-17)
- Added `aists_brain/research_audit_report.py`: deterministic JSON audit report with report SHA-256, repository HEAD, explicit G0/G2/G3/G4/G6/G7 snapshot, input artifact hashes, run metadata, simulator events and skipped decisions, accounting reconciliation, paper-ledger integrity, limitations, and safety controls.
- The report fails closed: if G0 is not PASS, a simulation result cannot be attached. It refuses any run result labelled as accepted/validated and requires accounting reconciliation and paper-ledger hash-chain checks to PASS before embedding a simulated run.
- Added seven tests covering blocked reporting, input hash/event/skipped-decision retention, G0 enforcement, forbidden status promotion, accounting failures, report tampering, missing gates and invalid commit SHA.
- CI compilation list now includes the audit report module. Test fixtures are synthetic software fixtures only; they are not BTCUSDT historical data and do not produce performance evidence.
- **No real historical run was performed.** Current G0 remains `BLOCKED_GLOBAL`; the appropriate report today is a gate-blocked report with no simulation payload. The report hashes its own canonical content for tamper detection but does not authenticate gate claims, external adjudicators or historical archive provenance.
- Live signing, public broadcast, exchange orders, automatic stop-loss and automatic take-profit remain blocked/not implemented. PR remains open and must not be merged.
- Next: inspect exact final branch SHA and CI terminal result, correct any failures, then proceed to the next bounded research-engine component without weakening gates.

## CP-0135 — Causal decision snapshot lineage guard (2026-10-17)
- Added `aists_brain/decision_lineage.py` and integrated it into `research_harness.py`. The harness now requires schema `aists.causal_research_decisions.v1`, exact candle-CSV SHA binding, non-empty brain/strategy versions, unique ordered decision IDs, a known candle-close cutoff, snapshot SHA-256, feature source hashes, finite numeric feature values, and feature observation timestamps no later than the decision cutoff.
- This closes a concrete gap in CP-0132: decisions are no longer accepted merely because their `as_of_ms` points to a candle close. A snapshot hash binds its contents; a future-dated feature is rejected even if its snapshot hash is recomputed.
- Added seven direct lineage tests and updated integration fixtures to include causal snapshots. CI compilation includes the new module.
- **Trust boundary:** timestamp and hash checks do not prove feature values were genuinely calculated from the declared source, and a SHA-256 does not authenticate source truth. No model signal generation or historical performance claim is added.
- G0 remains `BLOCKED_GLOBAL`; no real historical run is permitted. All live signing, public broadcast, exchange orders and automatic SL/TP remain blocked/not implemented. PR #2 remains open and must not be merged.
- Next: verify compile, all tests and exact final HEAD CI. If green, continue with a reproducible feature/snapshot producer that computes features only from source candles at or before each decision cutoff, while keeping G0 closed.

## CP-0136 — Prefix-only causal feature/snapshot producer (2026-10-17)
- Added `aists_brain/causal_feature_producer.py`. For every supplied completed candle, it computes market-context features from only the prefix ending at that candle, hashes the canonical prefix, binds the snapshot to brain/strategy versions, and emits a snapshot SHA-256. Later candles cannot change an earlier snapshot.
- The producer emits `NO_TRADE` for every row by design: it is a feature producer, not a signal generator. It rejects malformed OHLCV, invalid timestamps, unsupported intervals and any gap; it never repairs or fills data.
- Added a second entry point that loads candles through `load_provenance_cleared_candles` first. A blocked G0 manifest is rejected before feature generation. This does not authenticate the external adjudicator; an external PASS claim still needs independent evidence.
- Added eight tests covering snapshot generation, no-trade-only output, earlier-snapshot invariance when later candles change, feature timestamp cutoffs, gaps, invalid OHLC, hash/version validation, interval duration and blocked-G0 refusal. CI compiles the new module.
- **No real historical feature run or performance backtest was performed.** Synthetic candles exist only inside software tests. Current G0 remains `BLOCKED_GLOBAL`; do not create a manifest claiming PASS to bypass it. No live signing, public broadcast, exchange orders, automatic SL/TP, or PR merge.
- Next: inspect exact final HEAD and CI terminal logs; fix any failures before proceeding. Following a green gate, the next step is to persist deterministic feature artifacts with exact source hashes and connect the producer to the offline research harness without relaxing G0.

## CP-0137 — Deterministic, create-only feature artifact persistence (2026-10-17)
- Added `aists_brain/feature_artifact_store.py` to validate causal decision lineage before storage, serialize deterministically, record the exact source CSV hash, brain/strategy versions, timeframe and decision count, and bind the payload to SHA-256 metadata.
- Persistence uses a same-directory temporary file, flush/fsync, and atomic create-only hard-link publication. Existing destination paths are rejected rather than overwritten. The store reloads the saved artifact and verifies its payload hash and causal lineage before reporting success.
- Added five tests for round-trip persistence and hashes, refusal to overwrite, payload tampering, mismatched candle-close evidence, and rejecting already wrapped artifacts. CI compile list includes the store.
- Hashes prove identity/integrity only, not source truth, independent archive provenance, or feature correctness. Synthetic candles are software test fixtures only.
- G0 remains `BLOCKED_GLOBAL`; no real historical run, strategy performance claim, candidate promotion, live signing, public broadcast, exchange orders, automatic SL/TP, or PR merge.
- Next: verify exact final branch SHA, CI terminal result and PR state; then integrate persisted artifacts into a reproducible offline harness entry point that still refuses to run unless the independent G0/provenance gate is genuinely cleared.
