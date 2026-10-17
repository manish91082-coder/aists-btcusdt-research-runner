# CP-0143 — Official Binance Spot archive provenance recheck (2026-10-17)

## Decision summary

**Result: G0 remains BLOCKED_GLOBAL.** This is a targeted fresh check of official Binance Public Data documentation and three issue records, not an independent verification of the reported candle mismatches. It produces no permission to select daily over monthly data, rewrite candles, claim historical point-in-time reproducibility, run a real-market backtest, or promote a candidate.

## Sources inspected

1. Official repository README: https://github.com/binance/binance-public-data and raw README at https://raw.githubusercontent.com/binance/binance-public-data/master/README.md
2. Official repository issue #504, historical version/provenance questions: https://github.com/binance/binance-public-data/issues/504
3. Official repository issue #475, monthly Spot klines disagree with daily archives/API report: https://github.com/binance/binance-public-data/issues/475
4. Official repository issue #505, BTCUSDT 5m March 2023 close_time inconsistency report: https://github.com/binance/binance-public-data/issues/505

## Findings observed at recheck

### Official README

The current README states that archived files may be updated later when issues are discovered and calls its update list exhaustive. The listed entries are:
- 2022-08-08: `updates/2022-08-08_kline_updates.zip`, note "Fixed inconsistent data".
- 2022-04-21: `updates/2022-04-21_aggregate_trade_updates.zip`, aligned to the Spot aggregate-trade data change.

The README explains that companion `.CHECKSUM` files verify downloaded ZIP integrity and says the updates list includes replaced and replacement checksums. The README does **not**, in the inspected text, specify a public API for retrieving every prior ZIP version, exact first-publication timestamps, exact replacement timestamps, or point-in-time reconstruction of what was available at a past date. A checksum proves that a downloaded file matches its published checksum; by itself it does not prove historical immutability or publication-time provenance.

### Issue #504

GitHub issue API metadata at recheck: state OPEN; created 2026-09-27; last updated 2026-09-27; comments 0. The issue asks the maintainers to clarify prior-version retention/retrieval, first-publication and replacement timestamps, checksum/correction-list completeness, whether closed klines can change, REST/archive source equivalence, point-in-time reconstruction, retention policy and reproducible-backtest guidance. No maintainer answer was present in the observed issue metadata/comments.

### Issue #475

GitHub issue API metadata at recheck: state OPEN; created 2026-06-30; last updated 2026-07-10; comments 1. The issue author reports 398 rows across symbols/intervals where monthly Spot kline archives differed from daily archives and current API/chart endpoints, with the daily/API values matching in the reported sample. A subsequent comment reports additional BTCUSDT/ETHUSDT cross-timeframe aggregate mismatches. These are user-submitted reports and a contributor comment, **not a maintainer-confirmed canonical-source ruling**. This report does not reproduce those row comparisons independently.

### Issue #505

GitHub issue API metadata at recheck: state OPEN; created 2026-09-27; last updated 2026-09-27; comments 0. The author reports that row 6776 in `BTCUSDT-5m-2023-03.zip` has an early `close_time` for the 2023-03-24 12:35 UTC candle despite the ZIP matching the published checksum, and requests confirmation/correction guidance. This remains an issue report, not an independently verified market-data finding or maintainer confirmation.

## Evidence classification

- **Official documentation fact:** the README acknowledges later archive updates and lists two dated update bundles.
- **Official issue-tracker state:** #504 and #505 were OPEN with zero comments at this recheck; #475 was OPEN with one contributor comment.
- **Reported but not independently reproduced here:** the candle conflicts and malformed close-time examples in #475/#505.
- **Not established:** historical version retrieval, exact publication/replacement times, complete point-in-time history, a universal canonical precedence between monthly/daily/API sources, or whether the reported issues have a corrected archive.
- **Not inferred:** absence of a public version API in the inspected README does not prove no internal or undocumented retention exists.

## Gate impact and next action

G0 remains `BLOCKED_GLOBAL`; G2 remains `FAIL_CURRENT_23_CANDIDATES`; G3 remains `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 remains `INSUFFICIENT_EVIDENCE`; G6 remains `NOT_BUILT`; G7 remains `LIVE_BLOCKED`.

Smallest actionable evidence request is already expressed in issue #504: a maintainer must answer the version-retention/publication-time/immutability/REST-versus-archive questions with official references, and give an explicit canonical handling/correction answer for the reported #475 and #505 cases. Until that or equivalent admissible official evidence arrives:
- do not fabricate a PASS manifest;
- do not silently choose monthly or daily precedence;
- do not patch/shift/repair source candles;
- do not run real-market performance evaluation;
- do not promote a strategy or enable signing, public broadcast, exchange orders, automatic stop-loss or automatic take-profit.

## Goal-direction review

This check found new, concrete official-tracker evidence to add to the source-adjudication record, but it did **not** clear the actual provenance blocker. Repeating the same search without a new maintainer response or newly published official artifact is not useful. The next action should wait for or inspect a genuinely new official response/version record, rather than add more engine scaffolding.
