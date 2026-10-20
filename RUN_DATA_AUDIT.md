# Run the representative Binance archive audit

Status: prepared, not executed against a downloaded market-data artifact.

## Purpose

Use a network-enabled, zero-cost Python runtime such as Google Colab to retrieve one real official archive, verify its publisher checksum, inspect its kline rows, and compare bounded samples with the official API. This tool is a research validator only. It does not contain trading logic or exchange credentials and cannot place orders.

## 1. Start a fresh Colab notebook

Run the following in a notebook cell:

```bash
!python --version
!curl -fL --retry 2 --connect-timeout 15 \
  https://raw.githubusercontent.com/manish91082-coder/aists-btcusdt-research-runner/main/tools/audit_binance_archive.py \
  -o audit_binance_archive.py
!python audit_binance_archive.py --help
```

If retrieval fails, do not copy a different script or mark the audit as passed. Save the error and report it.

## 2. Run Spot and USDⓈ-M Futures as separate audits

Choose a completed UTC date several days in the past so a daily archive has had time to publish. Example date below is only a candidate, not a verified available archive.

```bash
!python audit_binance_archive.py --market spot --symbol BTCUSDT --interval 5m --date 2026-10-15 --api-samples 3 --out audit_output
!python audit_binance_archive.py --market usdm --symbol BTCUSDT --interval 5m --date 2026-10-15 --api-samples 3 --out audit_output
```

Each run attempts to download the official ZIP and its `.CHECKSUM`, checks local SHA-256 against the official value, checks ZIP/CSV structure, inspects numeric fields and OHLC invariants, counts duplicates/out-of-order rows/gaps, and compares up to three selected candles against the relevant official public API. The script records its chosen timestamp convention in the report.

A missing archive, missing checksum, DNS failure, API error, or timeout is a blocker, not a data-quality PASS. A real data-quality FAIL must preserve the report and artifact.

## 3. Preserve outputs

The output directory should contain the original downloaded ZIP, the publisher checksum file, the extracted CSV, and a JSON report for each market. Keep the original artifacts unchanged. Do not commit large raw archives to GitHub unless a later documented decision explicitly permits it.

Review the JSON reports before interpreting the result. The script's PASS is only a bounded first-artifact gate; it is not evidence that all symbols/timeframes/history are complete or that any strategy is profitable.

## 4. Return the evidence for independent review

Upload both JSON reports here, plus the exact error output if either run is BLOCKED/FAIL. Do not upload API keys, secrets, account details, or private files. The next review will verify the report fields and determine whether the representative archive gate passes. Only then will S-01 to S-04 experiment protocols be frozen before any backtest.

## Current truth

- Script and run instructions are committed to the project.
- No archive was downloaded or audited by authoring these files.
- No checksum PASS, dataset PASS, strategy result, backtest, model training, paper run, or live order is claimed.

## Coverage checks added
The runner additionally checks expected UTC-day candle opens for intervals that divide a day, so missing leading or trailing candles cannot pass merely because there are no gaps between the rows that remain. The report records expected candle count and examples of missing opens. This check has been added to the script but has not yet been executed against a downloaded archive.

## Additional timestamp checks
The runner also checks that parsed candle opens belong to the requested UTC archive date, that open timestamps align to the selected interval, and that inclusive close timestamps equal open + interval − 1 ms after the documented timestamp normalization. Alignment and close-time checks are marked not applicable for intervals that do not divide a UTC day. These checks are code-added; confirm the associated GitHub Actions run before treating the edited runner as smoke-tested, and still require real archive reports.

## Preferred execution path: GitHub Actions (no Colab setup)
A manual workflow runs both representative markets in a network-enabled GitHub-hosted runner and uploads the JSON reports plus downloaded audit evidence as a 14-day artifact:
- Workflow: [Phase 2 Binance archive audit](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/workflows/phase2-binance-data-audit.yml)
- Workflow file: [phase2-binance-data-audit.yml](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/.github/workflows/phase2-binance-data-audit.yml)

Steps:
1. Open the workflow link and select **Run workflow**.
2. Keep the default representative inputs unless there is a documented reason to change them: date `2026-10-15` UTC, symbol `BTCUSDT`, interval `5m`. The chosen date is a candidate, not a claim that the archive exists.
3. Start the workflow and wait for both market steps to finish.
4. Open that run, download the artifact named `phase2-binance-audit-...`, and provide the two `.report.json` files here.
5. If a market is BLOCKED or FAIL, share its JSON report and workflow logs. Do not treat the overall workflow as a data-quality PASS unless both reports say `PASS` and the reports are reviewed.

The workflow is manual-only, uses no exchange credentials and submits no orders. It now validates the date, symbol, and interval before starting either market audit. An invalid input stops at preflight and does not produce audit artifacts. GitHub Actions smoke tests do not substitute for this real archive audit. Phase 2 stays BLOCKED until the two reports are reviewed.
