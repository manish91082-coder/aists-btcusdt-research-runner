# Execution record: multi-month BTCUSDT cost-aware Spot baseline

- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39946109683
- Workflow commit: `a9e55fd5afd47878bde9cddd8db8732e856b6c1f`
- Branch: `research/hd04-alternate-source-probe`
- Final job status: SUCCESS
- Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39946109683/artifacts/12497742805
- Artifact ID: `12497742805`; size: 5,331,690 bytes; artifact SHA-256: `5e9a6a77d4b1541be57ed526e18055fcc607a9d6dbd729edc214ebf07b8283a0`

## Verified input

- Window: July through September 2026 inclusive.
- Normalized aligned BTCUSDT 5-minute rows: 26,496.
- Funding events retained in normalized dataset: 276.
- Dataset builder: `all_months_exactly_aligned=true`, status PASS.
- Baseline input: `btc-usdt-5m-aligned.csv`.

## Baseline run

- Initial quote-currency equity: 1,000 (illustrative USDT).
- Fee assumption: 10 bps per fill.
- Full spread assumption: 2 bps.
- Slippage assumption: 5 bps per fill.
- Flat/no-trade benchmark: 0.0% net return, 0 trades.
- Spot buy-and-hold benchmark: **42.18651505299809% net return** over this sample under the specified assumptions.
- Output equity curve: 26,496 rows.
- Report status: PASS; explicit verification step passed and artifact uploaded.

## Interpretation and limitations

This is a reproducible accounting benchmark for one three-month BTCUSDT Spot sample, not an AI strategy, not a validated trading edge, and not a forecast. The fee/spread/slippage values are illustrative assumptions, not verified user-specific or account-specific exchange rates. Buy-and-hold uses idealized full fills at impacted reference prices; partial fills, exchange filters, Futures margin/liquidation, and Futures funding cash flows are not simulated by this baseline. A positive historical sample does not establish future profitability or time to the ₹10 crore-equivalent target.

## Next gate

Keep the baseline as a comparator. Next implement and test transparent candidate strategy baselines (no-trade, trend/momentum and mean-reversion) with preregistered rules, chronological out-of-sample evaluation, cost sensitivity and full accounting checks before introducing AI model selection. Do not promote or deploy any strategy based on this benchmark alone.
