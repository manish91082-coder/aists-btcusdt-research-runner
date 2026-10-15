# CP-0107: Derived 996-row worklist integrity result

**Status: PASS_DERIVED_996_ROW_VIEW_VALIDATED, 22/22 checks PASS.**

- Original CP-0041 source pack SHA-256: `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`.
- Original worklist: 996 rows, 2,113,342 bytes, SHA-256 `f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f`.
- Crosswalk: 450/450 case IDs, monthly archive hashes, and all 12 raw fields matched.
- Derived view: 996 rows; exactly 450 target dispositions changed to `QUARANTINE_REVIEW_REQUIRED`; remaining 546 dispositions unchanged.
- All 996 non-disposition field sets and all 996 embedded raw-source JSON hashes remain identical. Original pack, worklist, crosswalk and delta were not modified.

## Persistent outputs

Full derived CSV (2,099,092 bytes; SHA-256 `137ad77bfafa7f7cd788db6f744e5567ad7dba889048b58feb743a34b863d9cb`) and 996-row audit (792,477 bytes; SHA-256 `717125e5abd83f987139d76df7ba245b972ad52438d4c64bb2e8bf06901012aa`) are saved under `/AISTS/CP0107/derived_worklist/` in Library. Compact index, summary and Hindi report are saved there as well.

The attempted binary index transfer to GitHub did not match the expected blob hash, so **no unverified compressed bytes were committed**. GitHub's CP-0107 summary records the exact local/Library hashes and paths instead.

## Research decision

This creates only a reproducible derived disposition view. It does not assign source authority or close cases. No timestamp shifts, raw-row edits, merges, replacements, synthetic candles, backtest reruns or strategy promotion. All G0-G7 gate states remain unchanged.
