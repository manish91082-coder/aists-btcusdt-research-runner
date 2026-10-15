# AISTS CP-0107: Row-by-row source disposition draft (Hindi)

## Execution and parent evidence
- Parent run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38730420808
- Parent commit: `b6ddcc9ed6c486570dc0c2da8857dd013cba18ae`; current `main` HEAD observed at resume: `a78b6e0dd531484a0d7f3e1345c420a76c115237`. The latter is a descendant that persists CP-0106 evidence; never equate the run's checkout SHA with current HEAD.
- CP-0106 artifact: ID `11969978987`, 579,598 bytes, SHA-256 `cdddab3be37f5c593d5cd42ac6c6f72b53f5b3a3fc4dae1218c3bd833850adb4`; ZIP CRC PASS.
- CP-0106 source objects: 66/66 verified, research status `PASS_DIAGNOSTICS_ONLY`. This is not strategy acceptance.

## Important limitation before interpreting this draft
The frozen CP-0040 rulebook and a current source-disposition ledger are **not present in the canonical repository tree searched at CP-0107 start**. Therefore this checkpoint records evidence-linked recommendations only, without pretending to apply inaccessible acceptance thresholds or formally close cases. The current project state is carried forward, not overwritten.

## A. February 2018 off-grid segment disposition
- CP-0106 reported 10 off-grid monthly segments, totaling 450 rows: 5m 241, 15m 81, 30m 85, 1h 43. Daily-reference records in the aligned segment evidence remain on-grid; CP-0104 exact numeric counterpart search returned zero for OHLC, OHLC+base volume and full economic fields for the 909 unmatched rows. CP-0105 nearest timestamps also found no exact economic equality.
- Proposed status for all 10 segments: `QUARANTINE_REVIEW_REQUIRED`; root cause/provenance `OPEN`. Keep exact source timestamp and bytes. No shift, rounding, merge, replacement or deletion.
- The prior committed segment inventory contains segment boundaries and row counts, not all individual raw records for the 450 monthly rows. This CP-0107 draft **does not falsely claim row-by-row economic review completed** for these rows. It records exactly which evidence and source ZIP/sidecar hashes should be used, and makes the missing all-row extract the next bounded diagnostic action.

## B. December 21, 2020 anomaly
- 59 raw records were exported (33 monthly, 26 daily) for the 12:30–14:15 UTC window across 5m/15m/30m/1h. Monthly source has 16 flat OHLC=`22646.53`, base volume=`0`, trade count=`0` records. All sixteen are retained as review flags, not automatically labelled corrupt.
- Eight rows share close-time fingerprint `1608558440521` (`2020-12-21 13:47:20.521 UTC`): four daily and four monthly. Their exact boundary deltas are preserved in `CP0107_Dec2020_RowDisposition.csv`, along with OHLC, volume, quote volume, trades, taker metrics, source archive filename/hash, CSV member and raw line.
- Parent-child evidence has 34 roll-up comparisons. The child sets marked `REVIEW_REQUIRED` remain unavailable where exact 5m children are missing; no synthetic rows or aggregate have been made. Exact available comparisons are evidence of numeric agreement for those particular rows only, not proof of source authority.
- Candidate interpretation: a shared row-content/close-time anomaly is supported by repeated field values across intervals; upstream cause is not proven. Case status stays `OPEN_REVIEW_REQUIRED`.

## C. Eight close-time-only conflicts
The frozen boundary arithmetic for each record is `expected_close_time = open_time + interval_ms - 1 ms`.
- 2017-09-06: 5m, 15m, 30m, 1h, 4h. For all five, daily close time exactly matches the expected boundary and monthly is +1 ms late. Proposal is limited to the **close_time metadata field**: monthly field fails the declared boundary comparison; daily field matches. The case and archive acceptance remain open.
- 2018-02-08: 4h and 1d. Monthly close-time matches the boundary; daily is early by 12,705,211 ms and 84,705,211 ms respectively. Proposal is metadata-field only.
- 2019-11-25: 4h. Monthly matches; daily is early by 7,200,000 ms. Proposal is metadata-field only.
- No archive is canonicalized, no economic field chosen, and no case is closed. Exact row keys and source archive hashes are indexed in `CP0107_SourceArchive_Manifest_66.csv`.

## What was changed in CP-0107 draft
- Created a machine-readable disposition set for the 10 February off-grid segments, 59 December raw rows, 34 roll-up comparisons, eight close-time-only cases, plus a 66-object source manifest.
- No raw data, candidate dataset, frozen evidence, or strategy file was modified. This is not yet a repository commit or a completed Actions run.

## Unresolved / next action
1. Locate or restore the frozen CP-0040 rulebook and current authoritative disposition ledger.
2. Run a focused cache-only CP-0107 extraction that writes every individual monthly off-grid February row (450 rows) alongside exact daily coverage, raw tokens, economic values, inner CSV row/member, source ZIP SHA-256 and sidecar SHA-256. No broad acquisition.
3. Reconcile those evidence rows against the frozen ledger and rulebook; until then retain OPEN/QUARANTINE statuses.

## Frozen gates and safety
G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`. No Binance market-data REST API, signing, public broadcast, exchange order, raw repair, canonical source selection, strategy promotion or backtest rerun was performed.