# CP-0117: Frozen-rulebook disposition of the 11 non-row aggregation blockers

Status: PASS_RULEBOOK_BOUND_NONROW_DISPOSITION_G0_STILL_BLOCKED

## Evidence result

- The 11 non-row blockers join one-to-one with CP-0112 bucket results. All 35 unique row keys evidenced by CP-0107 are tagged to their associated blocker case or cases in the 1,427-row CP-0040 manifest. The case-specific manifest key sets equal the frozen row-evidence key sets.
- Trade-derived parent candles reconcile to reconstructed child-candle rollups for 11/11 buckets. For the 35 exact target bars, current checksum-verified Spot trades reproduce 35/35 daily bars and 315/315 daily metric fields. The monthly source matches 21/35 bars and 218/315 fields; 14 keys / 97 fields remain divergent.
- This improves diagnostic corroboration of the current daily values, but it does not establish a historical version timeline or prove which bytes were publicly available at a historical decision time.
- The dated public issue snapshot records issue #504 as open with zero comments; no maintainer answer to the historical-version/timestamp question was observed. Issue #475 remains open but concerns different dates and is only contextual evidence.
- CP-0116 verified the exact-key filter implementation and excluded 35/35 synthetic probe rows, but production CP-0026 main was not invoked. Production candidate inputs and policy-based final metrics were not generated.
- Frozen CP-0040 sensitivity shows TRAIN net return changed by -15.891741 percentage points; the rulebook-bound G3 status therefore remains blocked.

## Per-case disposition

| Case | Keys | Child -> parent | Daily exact | Monthly exact | Divergent keys / field memberships | Disposition |
|---|---:|---|---:|---:|---:|---|
| AGG-01-5m-15m-2017-12-04T09:00:00Z | 4 | 5m -> 15m | 4/4 | 1/4 | 3 / 22 | KEEP OPEN |
| AGG-02-5m-15m-2017-12-04T09:15:00Z | 4 | 5m -> 15m | 4/4 | 3/4 | 1 / 9 | KEEP OPEN |
| AGG-03-5m-15m-2018-02-05T10:00:00Z | 4 | 5m -> 15m | 4/4 | 3/4 | 1 / 4 | KEEP OPEN |
| AGG-04-5m-15m-2018-03-04T14:30:00Z | 4 | 5m -> 15m | 4/4 | 1/4 | 3 / 23 | KEEP OPEN |
| AGG-05-5m-15m-2018-03-04T14:45:00Z | 4 | 5m -> 15m | 4/4 | 2/4 | 2 / 18 | KEEP OPEN |
| AGG-06-5m-15m-2018-09-05T09:45:00Z | 4 | 5m -> 15m | 4/4 | 3/4 | 1 / 6 | KEEP OPEN |
| AGG-07-15m-30m-2017-12-04T09:00:00Z | 3 | 15m -> 30m | 3/3 | 2/3 | 1 / 7 | KEEP OPEN |
| AGG-08-15m-30m-2018-02-07T06:30:00Z | 3 | 15m -> 30m | 3/3 | 2/3 | 1 / 4 | KEEP OPEN |
| AGG-09-15m-30m-2018-03-04T14:30:00Z | 3 | 15m -> 30m | 3/3 | 2/3 | 1 / 7 | KEEP OPEN |
| AGG-10-15m-30m-2018-06-20T03:30:00Z | 3 | 15m -> 30m | 3/3 | 2/3 | 1 / 5 | KEEP OPEN |
| AGG-11-30m-1h-2018-03-20T03:00:00Z | 3 | 30m -> 1h | 3/3 | 2/3 | 1 / 6 | KEEP OPEN |

## Frozen-rulebook conclusion

All eleven relationship blockers remain open. Their implicated exact rows are represented in the frozen quarantine manifest, but row-level coverage alone does not resolve the cross-interval relationship or historical version provenance. CP-0040 requires material source-policy effects to be included in candidate metrics, and the real candidate build is fail-closed before data read while these blockers remain. A prior candidate-specific diagnostic PASS for MTF_BREAKOUT_4H_D1 is not global G0 approval.

No daily-over-monthly precedence rule is introduced. The current evidence supports a bounded daily-data corroboration statement for the 35 exact keys, not global canonical-source authority. The 11 root causes remain OPEN_NOT_ESTABLISHED.

## Gates and non-actions

- G0 BLOCKED_GLOBAL; G2 FAIL_CURRENT_23_CANDIDATES; G3 BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT; G7 LIVE_BLOCKED.
- Canonical source NONE; source cases closed 0; 11 non-row blockers remain open.
- No archive downloads/network inside this audit; no source edits, timestamp rounding, synthetic candles, production build, backtest, promotion, signing, broadcast or Binance orders.

## Next bounded step

Do not repeat checksum acquisition or bypass the fail-closed builder. Continue only with an independently evidenced historical-version/source adjudication for the 11 relationships, or a formally frozen conservative quarantine policy with actual candidate-specific final metrics. Until then, preserve all blockers open.
