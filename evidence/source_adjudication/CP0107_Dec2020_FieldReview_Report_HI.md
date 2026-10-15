# CP-0107: December 2020 raw-field / provenance classification

Status: PASS_FIELD_REVIEW_HASH_RECOMPUTED; checks 9/9 PASS.

## Directly evidenced

- Shared 5m exact open-time keys: 16; complete raw-field matches: 9; divergent pairs: 7.
- First shared-key divergence is 2020-12-21 13:15 UTC. Six later shared keys from 13:20 through 13:45 UTC pair flat/zero monthly rows with non-flat daily rows.
- Repeated close-time fingerprint 1608558440521 appears on 8 rows across 5m, 15m, 30m and 1h. It does not prove root cause or source authority.
- Exact expected 5m keys absent in the two verified archives: monthly 10, daily 14; all nine affected parent roll-ups remain open.

## SHA-256 recomputed in GitHub Actions

| File | Rows | Bytes | SHA-256 | Git blob SHA-1 |
|---|---:|---:|---|---|
| CP0107_Dec2020_Shared_5m_RawField_Comparison.csv | 16 | 12019 | 530d120984e88d37a7993c80151482d8b75677bbec9d04fa31a927373a55aca0 | 92c9e97f5c4baea175f89e7b36493a18e0934829 |
| CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv | 8 | 5671 | b2aa529e3d1e6bd03717507be650b660e712826b1994f9c2619bc47064af509d | f16e44d15cdec9bf47d974acd85e54d2d8361e7c |
| CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv | 24 | 9222 | cd659b18d996a9ea4d86dba50e07c8c116fc57188f77d5cda07eb9b261ef4110 | 4ce746db8ae8f9e6f1622e4c0bae17bf975348c1 |
| CP0107_Dec2020_FieldReview_Summary.json | 1 | 12728 | e706de9164f28a413de3b8817c863bd5df2ad27e597f8aec5478ea6182dbc294 | committed with this run |

## Provenance and disposition limits

- Missing exact keys are absent from the inspected archive bytes; this does not explain why they are absent.
- Monthly archive official-manifest SHA and ZIP CRC were verified in the prior run, but its .CHECKSUM sidecar bytes were not rehashed in that run. Daily ZIP and cached sidecar were rehashed/content-matched.
- All affected cases remain OPEN_REVIEW_REQUIRED; root cause OPEN_NOT_ESTABLISHED; canonical source NONE; cases closed 0.
- No archive downloads, raw source edits, timestamp shifts, synthetic candles, backtest rerun or strategy promotion.
