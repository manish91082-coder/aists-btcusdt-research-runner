# CP-0243 — Binance Vision Dataset Terms: research-use and release-boundary review

Recorded: 2026-10-19  
Workstream: external source governance / data-use compliance  
Status: READ-ONLY OFFICIAL TERMS REVIEW; NO LEGAL DETERMINATION

## Decision

Decision: `CP0243_OFFICIAL_TERMS_FOUND_COMMERCIAL_LIVE_USE_REVIEW_REQUIRED_G0_UNCHANGED`.

The official Binance Public Data repository exposes `TERMS_AND_CONDITIONS.md`, labelled **BINANCE VISION DATASET TERMS, Version 1.0, Last Updated: August 26, 2026**. These terms create a separate data-use/release constraint for any future commercial or live-execution path. This is distinct from historical-data provenance (G0) and does not resolve it.

## Source and clauses inspected

Official source: https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md

- §1.4: terms state amendments apply prospectively to datasets made available after they take effect; the page does not itself establish which terms applied when every older archive was originally downloaded.
- §§3.1–3.4: datasets are stated to be under CC BY-NC-SA 4.0, supplemented by the Vision Dataset Terms; commercial licensing is excluded from this agreement and requires a separate written enterprise data license.
- §4.1: listed permitted non-commercial uses include algorithmic historical backtesting for purely personal, non-production research.
- §§4.2 and 4.4: the text prohibits live proprietary trading execution, automated commercial order generation, paid signal distribution, and integration into commercial trading-bot platforms.
- §§10.1–10.3: data is provided “as is”; Binance disclaims warranties of accuracy and completeness.

These are the published text's stated conditions, not a legal opinion about enforceability, jurisdiction, the user's exact activity, or any separately negotiated licence. Obtain qualified legal/licensing review before relying on these terms for a commercial product or live-execution plan.

## Impact on this project

1. Preserve personal/non-production historical research as a separate scope; it still remains blocked by G0 provenance and candidate prerequisites.
2. Do not treat this research permission as approval for commercial deployment, live proprietary execution, commercial order generation, signal distribution, or a paid trading-bot product.
3. Before any such release path, obtain written clarification/licensing appropriate to the intended use and record its scope, effective date, data coverage, and evidence hash.
4. Do not infer that repository MIT licensing covers the downloaded dataset; the official terms separately describe the dataset licence.
5. The terms do not establish point-in-time archive version history, immutable historical klines, or a canonical source for the project's conflicting/missing 4h bars.

## Gate disposition

- Historical canonical source: `NONE`; G0: `BLOCKED_GLOBAL`.
- G2: all 23 current historical candidates remain FAIL.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- G4: `INSUFFICIENT_EVIDENCE`; G6: `NOT_BUILT`; G7: `LIVE_BLOCKED`.
- Profitability: `NOT ESTABLISHED`.
- CP-0152 remains `PENDING_EXPLICIT_APPROVAL`; this review does not approve or implement the strategy.
- No archive downloaded; no candidate/backtest/paper run; no account access, order, signing, or broadcast.

## Validation boundary

This is a source-derived governance checkpoint, not a strategy or market-data validation result. No Binance issue/comment was created. No source case was closed and no gate was cleared.
