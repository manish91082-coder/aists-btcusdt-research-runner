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

## CP-0107 final extraction addendum — Run 38735418645

- Final run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38735418645. Runner PASS 11/11; child extraction PASS 9/9; evidence-publisher job PASS.
- Permanent output folder: `evidence/source_adjudication/CP0107_Run_38735418645/`; post-publish commit `b35953da0d12a84d52429a9dd064842900e0107e`.
- 450 raw off-grid monthly rows exported, 1,167 daily coverage rows exported, 10 off-grid segments verified across 12 date/interval cells, 16/16 scoped source objects verified, 0 exact daily open-key matches for the off-grid rows. No network, repair, timestamp shift/rounding, synthetic candle, backtest, canonical source selection or candidate promotion.
- Durable row export `CP0107_Feb2018_OffGrid_RawRows.csv` SHA-256 `379b1b9b258eed3fa55dfc95238e43e849300b14b85dd7643c0034befd841d64`; daily coverage SHA-256 `5dd5f5b314ff8518f06f6370db5502c79c3fd2a110653b05822921ff2b5dbcde`; segment coverage SHA-256 `652562ecd179896e0ecd48f2d434be3c5b81bf139d2ac4098062e43f38caf200`; source verification SHA-256 `3692b0dc2378e5115326834a2b09a625341aa245396a4cca8ac1670474ae19b5`.
- Hash rule: monthly ZIPs are checked against the official hash recorded in CP-0106’s frozen manifest; monthly sidecar bytes were not downloaded/re-hashed in this cache-only run. The daily ZIP + local .CHECKSUM bytes were re-hashed and content-matched. This distinction is in the extraction report and machine-readable summary.
- Supersession/correction: the earlier provisional `CP0107_Feb2018_OffGrid_RowDisposition.csv` has hash cells which were not fully validated and do not match all run-verified ZIP hashes. Do not use that draft’s hash columns for provenance decisions. Run-scoped source verification and raw-row outputs are the authoritative evidence for this extraction; the old file remains unchanged as historical draft.
- The frozen CP-0040 policy and authoritative CP-0041 disposition ledger have not yet been located as exact standalone repo files. Therefore CP-0107 closes no source-authority cases; all source decisions remain OPEN/REVIEW_REQUIRED pending the authoritative ledger and policy.


## CP-0107 / CP-0041 frozen-rulebook crosswalk addendum

- Authority source: CP-0041 package SHA-256 `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`, CRC PASS, 19 members, embedded payloads 18/18 PASS. Frozen CP-0040 rulebook SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.
- Exact crosswalk CSV: 450 rows, SHA-256 `5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b`; interval/open-time keys 450/450; monthly archive SHA match 450/450; all 12 raw fields match the CP-0041 monthly ledger 450/450; zero hash/value/key mismatches.
- Daily mapping diagnostic: 448 mapped daily keys present in CP-0107 official coverage, 2 still absent; 442 mapped rows have field differences. CP-0041's earlier candidate/override fixed-shift diagnostic listed 8 without exact counterparts; six now exist in CP-0107 direct daily coverage, two remain absent at the 2018-02-10 06:00 UTC targets for 5m and 15m. This does not establish why the economic fields differ.
- Frozen G0 interpretation: retain all 450 as `QUARANTINE_REVIEW_REQUIRED`; no rounding/shifting/merge/replacement/deletion, root cause OPEN, source NONE, zero cases closed, no backtest/promotion. Required source-time/provenance semantics evidence is still absent.


## Metric clarification from row-level CSV verification

- Corrected mapped daily counts: 448 rows have a mapped official daily target present; 2 targets are absent. Of the 448 present targets, 448 have at least one non-open-field difference, including volume/quote volume/trade metrics; 442 rows specifically differ in open price; 447 differ in close_time; all 448 differ in volume. The previous summary's `442` mapped-field aggregate was mislabeled/ambiguous and is superseded by these field-specific counts.
- This does not change disposition: all 450 monthly off-grid records remain QUARANTINE_REVIEW_REQUIRED, root cause OPEN, canonical source NONE.


## Superseding final overlay run and metric correction — CP-0107 run 38742035787

- Final Actions run and publisher: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38742035787; runner PASS 11/11, disposition checks PASS 6/6, publisher hash/row-count validation PASS.
- Durable row-level overlay: `evidence/source_adjudication/CP0107_Run_38742035787/CP0107_Feb2018_Disposition_Overlay.csv`, 450 rows, 1,036,405 bytes, SHA-256 `3fa8cd5e17718dfe3069aab0b1d55fbf990723f1865c77412a957dd63f898a0f`.
- Correct field-specific comparison: 448 mapped official daily targets exist, 2 are absent. All 448 present targets have non-open-field differences; `open` differs in 442 rows, `close_time` in 447, and `volume` in 448. Zero exact daily open-key counterparts exist for the 450 monthly off-grid rows.
- This supersedes the earlier CP-0107 generated-summary phrase that said 442 mapped rows had any non-open-field difference and 6 matched those fields. That earlier metric was incorrect; the row-level overlay and the corrected summary are authoritative.
- Frozen CP-0040 G0 disposition: all 450 rows stay `QUARANTINE_REVIEW_REQUIRED`; do not repair, shift, round, merge, replace or delete. Root cause OPEN, canonical source NONE, source cases closed 0.


## Joined evidence: eight close-time-only cases

CSV: `CP0107_CloseTimeOnly_FieldDisposition_Final.csv`, 8 rows; SHA-256 `473b149630edb6ee86b1720e2ffa4dd1afa7f022894bf5951ca398199319731c`. Monthly/daily ZIP and checksum-sidecar hashes are joined from the verified CP-0106 manifest for each CP-0041 shared-conflict key.
- Five monthly close_time values are +1 ms past boundary on 2017-09-06; three daily close_time values are early by 12,705,211 ms (4h), 84,705,211 ms (1d), and 7,200,000 ms (4h). Selected economic fields match on all 8 rows.
- Field-only proposal; no archive acceptance or canonical-source selection. All cases remain OPEN, root cause OPEN.
