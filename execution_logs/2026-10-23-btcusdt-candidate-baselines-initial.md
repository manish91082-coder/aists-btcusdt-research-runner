# BTCUSDT candidate-baseline initial run

- Date: 2026-10-23
- Branch: `research/candidate-baselines-clean`
- Pull request: https://github.com/manish91082-coder/aists-btcusdt-research-runner/pull/16
- Multi-month run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947263184
- Smoke/unit test run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947277912
- Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947263184/artifacts/12498676912
- Artifact ID: `12498676912`; size 5,839,681 bytes; artifact ZIP SHA-256 `cd4dd3b560fe70a95aa273b2ffb7bdbeaf7d8af1d638c6cb2d70082f65b93da5`.

## Verified inputs and checks

- July-September 2026 inclusive, official monthly archives with integrity validation.
- Normalized aligned BTCUSDT 5-minute dataset: 26,496 rows; 276 funding events retained in normalized data.
- Cost-aware Spot baseline and candidate baseline runner completed.
- Candidate output verifier: PASS; both candidate reports present and PASS; each equity curve has 26,496 rows.
- Smoke CI: SUCCESS; deterministic unit tests passed after correcting one test assertion to match the runner's report structure.
- Equity curve final point is explicitly recorded after final costed liquidation and tested against realized final equity.

## Initial candidate results

Assumptions: initial equity 1,000 USDT; fee 10 bps per fill; full spread 2 bps; slippage 5 bps per fill. Spot, long/flat, all available equity allocated while long. Signals from a completed candle execute at the next candle open; remaining position is liquidated at the last close with modeled costs.

| Candidate | Net return | Maximum marked-to-market drawdown | Fills |
|---|---:|---:|---:|
| SMA trend, 12/48 | -68.0308% | -68.5169% | 742 |
| Mean reversion, trailing z-score 48, entry <= -1.5, exit >= 0 | -58.9397% | -59.4759% | 652 |

## Interpretation

Both initial candidates lost substantially on this sample under the fixed cost assumptions. This is a negative initial result, not a profitable edge. It does not prove the rules cannot work in another preregistered configuration or period; equally, it gives no justification for tuning until a favorable result appears. The same July-September sample was used for implementation validation and initial candidate inspection, so it is not an untouched holdout. Do not promote these numbers as out-of-sample performance.

The benchmark runner excludes Futures positions/funding cash flows, leverage, liquidation, partial fills, exchange filters, and dynamic market impact beyond fixed costs. No AI strategy, live trading, or target timeline is established. No exchange credentials or orders were used.

## Next gate

Freeze these baseline rules and assumptions. Define chronological train/validation/holdout periods before further tuning, include turnover/cost sensitivity and benchmark comparisons, then run walk-forward evaluation. Any parameter change must be logged and evaluated on data not used to select it.
