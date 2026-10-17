# AISTS AI Brain Roadmap (Hindi)

Updated: 2026-10-17
Status: CP-0120 implementation started on branch `cp-0120-ai-brain-foundation`.
Canonical repository: https://github.com/manish91082-coder/aists-btcusdt-research-runner

## Goal
Build a BTCUSDT-first, long-only Binance Spot decision system for planning capital of INR 10,000 converted to USDT. It should combine multi-timeframe market context, technical/volume analysis, a strategy library, strategy selection, risk/capital controls, and a controlled learning loop. This roadmap does not promise profitability. Live signing, order placement, and public broadcast remain disabled.

## Execution order
1. **Brain contract and architecture** — define stable inputs/outputs, completed-candle semantics, abstention, versioning, and no-order boundary.
2. **Market context engine** — trend, momentum, volatility, volume, support/resistance references, and data-quality flags for 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mo.
3. **Strategy library** — implement established strategy families with explicit entry/exit rules, market-regime suitability, cost assumptions, and failure conditions.
4. **Strategy selector / meta-brain** — compare eligible strategies for current regime and timeframe; allow NO_TRADE when evidence is weak or signals conflict.
5. **Learning and discovery** — causal feature pipeline, versioned model training, search-trial ledger, benchmark comparison, calibration, and drift monitoring. No self-promotion without independent gates.
6. **Risk and capital engine** — INR 10,000 planning capital converted to USDT, position sizing, exposure limits, fees/slippage, BNB discount economics. Do not silently change the user's no-automatic-SL/TP preference.
7. **Historical validation** — only after brain modules are testable; preserve source lineage, split train/validation/OOS chronologically, prohibit leakage, report regime-wise net results.
8. **Paper evaluation** — frozen version, append-only decisions and virtual portfolio ledger, observation coverage and acceptance gates.
9. **Exchange readiness** — separate future review only. Live trading is not authorized by this roadmap.

## Completion ledger
- DONE (code exists; not an AI brain): CP-0026 provenance-aware candidate builder; CP-0027 fixed deterministic baseline with EMA/RSI/Donchian, buy-and-hold and cash benchmarks.
- DONE (audit infrastructure): source manifests, checksum verification, source-conflict evidence and append-only checkpoints.
- NOT DONE: adaptive AI, strategy discovery, market regime classifier, support/resistance knowledge store, multi-timeframe decision brain, 1w integration, verified account fee tier, paper acceptance, live readiness.
- Current known gates from last verified research ledger: G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. These gates must not be overwritten by a design/code milestone.
- Historical source-provenance blockers remain open. Do not falsify or silently bypass them. Independent brain modules can be developed and unit-tested, but historical performance claims remain blocked until the applicable data gates pass.

## Current implementation milestone: CP-0120
- Add a pure Python, no-network market-context module.
- Compute EMA20/EMA50, RSI14, ATR14, 10-bar momentum, relative volume, and prior lookback support/resistance references.
- Enforce OHLC validity and strictly increasing timestamps when supplied.
- No strategy signal, no market-data download, no exchange API, no signing, no orders.
- Verify with standard-library unit tests; then inspect GitHub state and CI results before marking tests accepted.
