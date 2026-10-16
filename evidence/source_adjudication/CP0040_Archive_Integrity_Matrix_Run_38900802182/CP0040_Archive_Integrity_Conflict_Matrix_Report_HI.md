# CP-0040: Official archive integrity vs aggregation conflict matrix

Status: PASS_OFFICIAL_ARCHIVE_INTEGRITY_CONFLICT_MATRIX_COMPLETE
Monthly official sidecars verified: 14/14; daily official sidecar/archive records retained: 16/16.
Bucket cases covered: 11/11; raw row-evidence links available: 78.
Buckets with both source archive families authenticated: 11/11.
Buckets where the daily roll-up matches its daily parent and the frozen monthly mismatch remains: 11/11.

| Bucket | Pair | Both archive sets authenticated | Daily roll-up | Monthly mismatch signature | Disposition |
|---|---|---|---|---|---|
| AGG-01-5m-15m-2017-12-04T09:00:00Z | 5m → 15m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-02-5m-15m-2017-12-04T09:15:00Z | 5m → 15m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-03-5m-15m-2018-02-05T10:00:00Z | 5m → 15m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-04-5m-15m-2018-03-04T14:30:00Z | 5m → 15m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-05-5m-15m-2018-03-04T14:45:00Z | 5m → 15m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-06-5m-15m-2018-09-05T09:45:00Z | 5m → 15m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-07-15m-30m-2017-12-04T09:00:00Z | 15m → 30m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-08-15m-30m-2018-02-07T06:30:00Z | 15m → 30m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-09-15m-30m-2018-03-04T14:30:00Z | 15m → 30m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-10-15m-30m-2018-06-20T03:30:00Z | 15m → 30m | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |
| AGG-11-30m-1h-2018-03-20T03:00:00Z | 30m → 1h | True | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | True | OPEN |

## Decision
This establishes integrity of the particular monthly and daily archive byte sets and confirms the aggregation disagreement; it does not decide which interval is canonical.
All 11 relationship blockers remain unresolved; G0 BLOCKED_GLOBAL; canonical source NONE; no source case closed.
No network activity, archive download, data repair, candidate build, backtest or strategy promotion occurred.
