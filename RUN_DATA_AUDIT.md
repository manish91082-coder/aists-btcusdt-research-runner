# Run the representative Binance archive audit in GitHub Actions

## Purpose
Run the locked Phase 2 representative archive audit entirely within GitHub. Do not use Google Colab or Google Drive for this project workflow. GitHub main remains the source of truth; GitHub Actions stores the execution logs and time-limited evidence artifact.

## 1. Open the existing workflow
- Workflow: [Phase 2 Binance archive audit](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/workflows/phase2-binance-data-audit.yml)
- Source: [.github/workflows/phase2-binance-data-audit.yml](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/.github/workflows/phase2-binance-data-audit.yml)

On GitHub, select **Run workflow**. Use:
- UTC archive date: `2026-10-15`
- Symbol: `BTCUSDT`
- Interval: `5m`

Then start the workflow once. Do not create marker commits or rerun the workflow merely to generate activity.

## 2. Retrieve the evidence from GitHub
When the run completes:
1. Open the new run in Actions.
2. Inspect the Spot and USDⓈ-M Futures audit steps and the final gate-enforcement step.
3. Download the artifact named `phase2-binance-audit-...` from that same run. The artifact retention is 14 days.
4. Preserve both `.report.json` files and any downloaded archive/checksum evidence in the GitHub Actions artifact. Do not commit large raw archives into Git.

## 3. Interpret the result correctly
- **PASS** is accepted only when both Spot and USDⓈ-M reports pass every required check and the reports are reviewed.
- **BLOCKED** means required evidence could not be verified, such as an unavailable API response or network restriction. Preserve the exact error.
- **FAIL** means a required check demonstrated a data or validation failure. Preserve the report; do not relabel it BLOCKED to hide a proven defect.
- Daily-versus-monthly archive agreement is same-publisher consistency evidence. It does not replace the required API candle comparison.
- A successful smoke-test workflow verifies code/tests only. It does not pass the real-data gate.

## 4. Current gate
The latest decisive run recorded Spot API verification as PASS and USDⓈ-M Futures API verification as BLOCKED (HTTP 451 on the primary host; HTTP 202 on numbered hosts). Phase 2 therefore remains BLOCKED. Do not start backtests, model training, paper trading, live orders, or deployment.

## 5. Tool boundary
This session's GitHub connector can inspect repository files, commits, runs, jobs, logs and artifacts, but does not expose a workflow-dispatch action. Therefore I cannot honestly claim to have clicked **Run workflow** from this chat. The only manual action required is starting the existing workflow in GitHub's Actions UI and sharing its artifact/run link. No Colab or Drive step is part of this route.
