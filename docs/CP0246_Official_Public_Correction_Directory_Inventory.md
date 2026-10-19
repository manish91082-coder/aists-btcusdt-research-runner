# CP-0246 — Official public correction-directory inventory

Recorded: 2026-10-19  
Workstream: historical source provenance  
Status: READ-ONLY OFFICIAL REPOSITORY INVENTORY

## Decision

Decision: `CP0246_PUBLIC_UPDATES_DIRECTORY_HAS_NO_LISTED_MONTHLY_SPOT_KLINE_CORRECTION_G0_UNCHANGED`.

The current official `binance/binance-public-data` repository `updates/` directory lists three files: one 2022-04-21 aggregate-trade package, the 2022-08-08 kline checksum manifest, and one 2022-10-04 aggregate-trade CSV. The only listed kline correction package is the one already inspected in CP-0245. Its four BTCUSDT 4h rows refer to daily archives in 2021/2022, not the project's monthly archive or the known 2017-09-06 key.

This is a bounded inventory of the currently listed public directory, not proof that no private, historical, external, or unlisted correction record exists.

## Evidence

Official directory: https://github.com/binance/binance-public-data/tree/master/updates

At inspection, the directory listed:
- `2022-04-21_aggregate_trade_updates.zip` (GitHub object SHA `876a78514c357a501ab27c31dd75ed565228a87c`)
- `2022-08-08_kline_updates.zip` (GitHub object SHA `90631298cf50ac2e1ee8372a087767b010d78a21`)
- `2022-10-04_aggregate_trade_updates.csv` (GitHub object SHA `1877919385993a77614941aea355a575e6177755`)

Official issue #504 was rechecked:
https://github.com/binance/binance-public-data/issues/504
It remains OPEN, last updated `2026-09-27T18:20:58Z`, with zero comments. This is a current API observation, not proof no response exists through another channel.

CP-0245 already inspected the kline package itself:
- 6,653,240 bytes; SHA-256 `1404dbfb3d62534b2576a6c0c046826fe652f895b9bebfe4c13df58bc8cf6240`
- ZIP CRC PASS; 73,234 manifest data rows
- Four BTCUSDT 4h manifest entries, all daily archive paths; no matching 2017-09-06T16:00:00Z correction path.

## Gate disposition

- Canonical historical source: `NONE`; G0: `BLOCKED_GLOBAL`.
- G2: all 23 current candidates remain historical-screen FAIL.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- G4: `INSUFFICIENT_EVIDENCE`; G6: `NOT_BUILT`; G7: `LIVE_BLOCKED`.
- Profitability: `NOT ESTABLISHED`.
- CP-0152 remains `PENDING_EXPLICIT_APPROVAL`.

No market-data archive was downloaded in this checkpoint; no source data was changed; no source case was closed; no backtest, paper run, or exchange action occurred.

## Next admissible action

The publicly indexed correction-directory route is exhausted for this known gap. Do not repeat its inventory or the CP-0245 package scan. Advance only when genuinely new official point-in-time/version evidence arrives, or an authorized independent review and separate scoped policy-application record are available. Until then preserve UNKNOWNs and keep G0 blocked.
