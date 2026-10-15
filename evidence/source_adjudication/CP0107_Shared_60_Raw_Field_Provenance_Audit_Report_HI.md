# CP-0107: 60 shared-open conflicts raw-field provenance audit

**Status: PASS_SHARED_60_RAW_FIELD_PROVENANCE_AUDIT, 13/13 checks PASS.**

- The 60 frozen CP-0041 shared-open conflict keys match the original 996-row worklist. Both source raw-row JSON objects match the worklist record: 60/60.
- Monthly archive hashes match the frozen monthly manifest for 60/60; daily archive SHA-256, .CHECKSUM sidecar and manifest values match for 60/60.
- 52 rows have economic/trade-metric differences; 8 rows have exact economic fields and a close-time boundary metadata difference. Any ignore-field metadata differences remain explicit.
- No original disposition or source-choice field changed. Full audit CSV: 60 rows, 179,989 bytes, SHA-256 7647e5f72f4ee212e2d67aff0dd9851e2556b32e1f882da1dd290b3df1076187, in /AISTS/CP0107/shared_conflicts/.

This checks frozen ledger and manifest reference consistency; it is not a fresh download/reparse of every archive. It does not select a canonical source or explain upstream cause. Cases closed: 0; canonical source selected: 0; root cause OPEN_NOT_ESTABLISHED. No source mutation, timestamp correction, row replacement, synthetic data, backtest rerun or strategy promotion.
