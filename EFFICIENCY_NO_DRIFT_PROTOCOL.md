# Efficiency, No-Drift and Anti-Loop Protocol

Date: 2026-10-21
Status: ACTIVE PROCESS LOCK
Project: Full AI Crypto Trading Bot 21 OCT

## Purpose
Maximise verified progress per response while preventing repeated audits, unnecessary processing, scope drift, speculative work and false claims. This protocol governs research workflow only; it does not waive any data, safety, eligibility or authorisation gate.

## 1. Required pre-action checkpoint
At the start of each substantive response/action:
1. Confirm the user's mission and current request.
2. Read the live GitHub main SHA and compare it with the last verified checkpoint.
3. Identify the active phase, exact exit gate, last decisive evidence, blocker, and next allowed action from project status/continuity records.
4. Inspect only the relevant current workflow run, report, code, test, or document needed to decide the next action.
5. Use the latest verified full plan as the governing reference. Re-fetch/re-read the full plan when the main SHA changes unexpectedly, the plan itself changes, the phase/scope changes, a gate is ambiguous, or a new conversation lacks a reliable checkpoint. Do not repeatedly re-read every unchanged long file merely to simulate diligence.

## 2. One-question, one-pass rule
- Define the single decision the next action must resolve before using tools.
- Prefer one targeted query or one bounded run over broad repeated polling.
- Reuse already retrieved evidence if it answers the same question and has not been invalidated by a code, input, environment or scope change.
- Stop checking a completed workflow after its final conclusion and required evidence are retrieved. Do not repeatedly poll completed runs.
- Never rerun an audit solely to create activity or to obtain a more convenient result.

## 3. Rerun eligibility
A CI/data audit may be rerun only when at least one is true:
1. Relevant code, tests, configuration, input data, or documented protocol changed materially;
2. The previous run failed for a clearly identified correctable defect and the correction is committed;
3. The run was interrupted/incomplete and the missing result is required;
4. A documented environment/source condition has changed and the result is decision-relevant.
Before rerun, record the expected information gain and the exact pass/fail condition. If the same blocker repeats with no material change, stop retries and document the blocker.

## 4. Bounded blocker investigation
- First establish the precise failure and source from primary evidence.
- Consult official documentation for a finite, relevant list of supported options.
- Test only options that are documented, permitted, safe, and materially likely to resolve the blocker.
- For HTTP 451 or other jurisdiction/access restrictions, do not use VPNs, proxies, alternate identities, or technical workarounds to bypass restrictions.
- If the documented options are exhausted or blocked, stop endpoint cycling. Record the exact result, classify BLOCKED, and state the narrow user/environment decision or protocol change required next.
- Same-publisher archive agreement is not independent verification and cannot silently replace a locked API requirement.

## 5. Progress and scope discipline
- Work only on the current phase's next allowed action. No backtest, training, paper trading, live order, deployment or bulk data pull before the corresponding gates.
- Do not repeat successful tests unless a relevant change invalidates them.
- Avoid cosmetic commits, repeated trigger-marker commits, duplicated documentation, speculative code, unnecessary tool calls and repeated full-file reads.
- A material change should resolve a defined blocker, improve a required control, or create an explicitly required deliverable. Otherwise defer it.
- Keep code/test CI evidence, real market-data evidence, research/backtest results and trading/execution evidence strictly separate.

## 6. Evidence and reporting
For every material action, report only:
- What changed (or state no repository change);
- The exact source/commit/run/report used;
- What was verified and what remains unverified;
- Current gate status and the single next action.
Never describe a queued run as passed, a workflow success as data PASS, or same-publisher consistency as independent confirmation. Do not promise zero errors; describe the bounded checks actually performed.

## 7. Durable record and verification budget
- Update status/log/continuity only for material changes, new evidence, a changed blocker, or a new next action. Do not append repetitive entries that add no information.
- After a write, read back the changed file and verify the resulting main SHA. If another commit moves main, reconcile before writing again.
- Default per-response tool budget: one live-head check, one targeted evidence retrieval pass, one bounded research pass if needed, and only the minimum sequential repository writes required. Exceed this budget only when the task genuinely requires it; explain why in the durable log.
- Do not run periodic polls or create automation for this protocol unless explicitly requested.

## 8. Current application at adoption
- Active gate: Phase 2 representative official BTCUSDT Spot 5m and matching USDⓈ-M Futures audit.
- Latest decisive run: 39496937998. Spot API check PASS via https://data-api.binance.vision/api/v3/klines; Futures API check BLOCKED because fapi.binance.com returned HTTP 451 and fapi1–fapi4 returned HTTP 202. Archive integrity/quality and daily-monthly diagnostics passed, but do not substitute them for the Futures API gate.
- Do not rerun the same audit with unchanged code/environment. The next action is a bounded check of official USDⓈ-M Futures documentation for any explicitly documented, permitted public market-data endpoint. If none exists, stop endpoint cycling and preserve Phase 2 as BLOCKED pending a protocol decision or a compliant execution environment. No regional restriction bypass.
- No backtest, model training, paper trading, live order or deployment has occurred.
