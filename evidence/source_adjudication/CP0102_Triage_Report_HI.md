# CP-0102 Source Conflict Triage — Run 38725478106

This checkpoint classifies existing CP-0025 mismatch/unmatched evidence only. It does not repair rows, choose canonical source, close cases, or rerun strategies.

## 60 value mismatches
- 8 rows change only `close_time`: 5 on 2017-09-06, 2 on 2018-02-08, 1 on 2019-11-25. These remain open because timestamp metadata must be formally dispositioned under the exact close-boundary rule.
- 52 rows differ in economic/trade metrics.
- Main economic clusters: 2020-12-21 (13 rows), 2021-04-22 (5), 2021-04-23 (16), 2021-12-24 (10), 2022-04-13 (4). Smaller clusters: 2018-02-11 (1), 2021-01-21 (2), 2021-09-23 (1).

## 909 unmatched rows
- Daily-only 452; monthly-only 457.
- 897/909 are on 2018-02-09, 2018-02-10, 2018-02-11. Monthly records include fractional/off-grid UTC timestamps while daily records often have grid-aligned opens. Treat this as a timestamp-alignment divergence candidate, not a proven root cause or source-authority decision.
- 7 on 2020-12-21 coincide with the malformed flat/zero-volume monthly row and roll-up mismatches.
- 5 on 2017-09-06 coincide with close_time-only differences and a daily-only 16:00 UTC key.

## Next investigation order
1. Reconstruct exact monthly/daily timestamp neighborhoods on 2018-02-09..11, preserving raw open-time keys and showing nearest-grid offsets. Do not round or drop unmatched rows.
2. Trace the 2020-12-21 row through 5m→15m→30m→1h roll-ups.
3. Review the 8 close_time-only conflicts against the frozen expected-boundary rule.
4. Keep every decision OPEN until evidence supports a formal disposition. No candidate backtest rerun until a reviewed candidate input hash changes.

## Gate
`INVESTIGATE_BEFORE_BACKTEST`. 60 mismatch rows OPEN; 909 unmatched rows OPEN/quarantined; 0 source cases closed; 0 canonical sources selected; 0 automatic corrections. No strategy promotion. Live trading remains blocked.

The full row-level triage is attached in the CP-0102 evidence ZIP shared in the ChatGPT conversation.
