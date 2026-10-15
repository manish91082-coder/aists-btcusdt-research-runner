# CP-0107: official .CHECKSUM provenance audit

Status: PASS_OFFICIAL_SIDECAR_PROVENANCE; checks 10/10.

Only two official text .CHECKSUM URLs were requested from HTTPS host data.binance.vision. No ZIP archive was downloaded and no Binance market-data REST endpoint was called.

| Source | Sidecar SHA-256 | Matches frozen sidecar hash | Embedded archive SHA matches manifest |
|---|---|---|---|
| MONTHLY | 0db24ee3bb2a29cfd9971949837eab439c3226666bb2b00c458aaa16eb249667 | True | True |
| DAILY | a4aabf08bf9c231daf643071dd531f1f814a7fbdea86b4e8c38a7ce795f13962 | True | True |

## Interpretation

A PASS confirms the fetched .CHECKSUM content exactly matches the recorded CP-0106 sidecar digest and its embedded archive hash matches the frozen official archive SHA. This authenticates this sidecar/archive hash linkage only; it does not adjudicate disputed kline rows or establish a canonical data source.
Affected row dispositions remain OPEN; root cause OPEN; canonical source NONE; no backtest rerun or strategy promotion.
