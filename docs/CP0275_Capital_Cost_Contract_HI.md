# CP-0275 — Evidence-gated INR capital and cost contract

**Status:** Verified. Exact-head run [39311654371](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39311654371) completed successfully on `a604748a5d8bb9580febb36536e6636d0a2f81c1`; compile passed and all 212 tests passed (`OK`), including nine CP-0275 tests.  
**Branch:** `cp-0120-ai-brain-foundation`  
**Capital basis:** INR 10,000, preserved as the source amount.

## Implementation

- Added `aists_brain/capital_cost_contract.py`.
- Added `tests/test_market_capital_cost_contract.py` with nine tests.
- INR-to-USDT conversion, allocation, fee bps, slippage bps, and BTCUSDT symbol filters are only used in derived calculations when the caller supplies both a source reference and explicit verification.
- Missing or unverified assumptions remain unavailable; the contract does not fetch FX, Binance fee schedules, BNB discounts, or exchange filters.
- BNB fee savings and conversion overhead are modeled only as explicit, source-referenced scenario inputs. They are not represented as confirmed Binance terms.
- The simple round-trip cost estimate is a transparent notional approximation, not a backtest or fill simulation.

## Safety and gate boundary

- A fully populated contract can report `ASSUMPTIONS_VERIFIED_FOR_MODELING_ONLY`; it cannot authorize candidate building, market backtesting, paper trading, or live activity.
- G0 remains `BLOCKED_GLOBAL`; canonical historical source remains `NONE`.
- CP-0040 remains frozen. No real market data was read and no candidate/backtest/paper run was started.
- Live signing, public broadcast, exchange orders, and automatic stop-loss/take-profit remain blocked.
- PR #2 remains open and unmerged.

## Verification result

Exact-head run [39311654371](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39311654371) was terminal-success on `a604748a5d8bb9580febb36536e6636d0a2f81c1`. Compile step passed; test log reports `Ran 212 tests ... OK`, including all nine CP-0275 tests. The workflow compile list explicitly includes `aists_brain/capital_cost_contract.py`. This verifies the software contract only, not source truth or profitability.
