# AISTS AI Brain Roadmap (Hindi)

Updated: 2026-10-17
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
- **Implemented in CP-0121 branch:** `aists_brain/market_regime.py` classifies descriptive trend/breakout/breakdown/mixed regimes and volume state. It explicitly abstains on limited history; high volatility is assessed only when a causal historical ATR percentile is supplied.
- **Unit tests added:** seven market-context tests and seven market-regime tests. CI is configured to compile both modules and discover both test files. Do not call CI PASS until a successful Actions run is actually verified.
- **NOT DONE:** trained/adaptive AI, strategy library beyond existing baseline, strategy selector, causal ATR percentile history, full support/resistance knowledge store, all-eight-timeframe pipeline integration, 1w aggregation verification, verified account fee tier, paper acceptance, live readiness.
- **Last known research gates:** G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G4 INSUFFICIENT_EVIDENCE; G6 NOT_BUILT; G7 LIVE_BLOCKED. Code milestones do not override these gates.
- Historical source-provenance blockers remain open. Independent brain modules can be developed and unit-tested, but historical performance claims remain blocked until applicable data gates pass.

## Current next step
Verify Actions execution and test results for the market-context and regime modules. Then implement the strategy contract/library and a deterministic selector with explicit NO_TRADE behavior. Do not repeat exhausted source correction searches unless new evidence appears.
