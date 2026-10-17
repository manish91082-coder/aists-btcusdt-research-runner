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
