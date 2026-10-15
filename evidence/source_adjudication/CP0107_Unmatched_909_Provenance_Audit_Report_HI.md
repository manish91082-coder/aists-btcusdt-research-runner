# CP-0107: 909 unmatched rows provenance audit

**Status: PASS_UNMATCHED_909_MANIFEST_PROVENANCE_AUDIT, 13/13 checks PASS.**

- CP-0041 unmatched records checked: 909, comprising 452 daily-only and 457 monthly-only rows.
- Every case ID, open-time key and source-side raw JSON matches its exact record in the frozen 996-row worklist: 909/909.
- Monthly archive manifest/hash references match for 909/909 rows. Daily archive SHA, recorded sidecar SHA and daily manifest SHA references match for 909/909 rows.
- Existing dispositions match the original worklist for 909/909 records. No case status changed.
- Audit CSV: 909 rows, 963,228 bytes, SHA-256 `b8ffd2a98f9296fdb04a2296f2190caca5387bbb286185a564717aadcb40d980`; preserved at `/AISTS/CP0107/unmatched_provenance/CP0107_CP0041_Unmatched_909_Provenance_Audit.csv`.

**Scope qualification:** this audit verifies the frozen ledger and hash-manifest references. It did not redownload/reopen every monthly and daily ZIP in this turn, does not establish upstream root cause, and does not select a canonical source.

Canonical source selected: 0. Cases closed: 0. Root cause `OPEN_NOT_ESTABLISHED`. No timestamps shifted/rounded, no raw row edits/merges/replacements/deletions, no synthetic candles, no backtest rerun and no strategy promotion. G0 remains `BLOCKED_GLOBAL`; G2 remains `FAIL_CURRENT_23_CANDIDATES`; G7 remains `LIVE_BLOCKED`.
