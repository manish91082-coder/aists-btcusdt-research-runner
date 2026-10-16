# CP-0107: Final Continuity Reconciliation and Verified Index Publication

**तारीख:** 16 अक्टूबर 2026  
**स्थिति:** 56/56 current-output integrity checks PASS; frozen raw-input rehash **NOT_VERIFIED**

## 1. Verified GitHub publication

- Repository: [aists-btcusdt-research-runner](https://github.com/manish91082-coder/aists-btcusdt-research-runner)
- Compact minimal index: [CP0107_CP0041_Derived_996_Row_GitIndex_Minimal.csv.gz](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/evidence/source_adjudication/CP0107_CP0041_Derived_996_Row_GitIndex_Minimal.csv.gz)
- Publication commit: `ecde99840fefa91027145720025f615680b963af`
- Git blob SHA-1: `95dec028cb6fc7787990950a55a21cb67c9ffdc8`
- Compressed bytes: 7,282; SHA-256: `a3a961a3e3ff0783c1cfed6efafddef313f7c455148a9a5174e95feef80062bf`
- Expanded index: 996 rows, 185,941 bytes; SHA-256: `072009025272fcba372b820a2ecbd1c65f5938138c5206f19e7cfcdf83ecc39b`.
- Fetch-back: `main` points to the publication commit; recursive Git tree confirms the exact path, blob SHA-1, file mode and 7,282-byte size. The binary payload itself was not returned by the text-only fetch endpoint, so no binary-content download is claimed.

## 2. Independent current-output integrity checks

**56/56 PASS** on the materialized Library outputs and available crosswalk:

| Output | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| Derived worklist | 996 | 2,099,092 | `137ad77bfafa7f7cd788db6f744e5567ad7dba889048b58feb743a34b863d9cb` |
| Per-row audit | 996 | 792,477 | `717125e5abd83f987139d76df7ba245b972ad52438d4c64bb2e8bf06901012aa` |
| Disposition view | 996 | 776,844 | `990ea275d5f5fece863d7655615bc8d29dd321107668fd3322f18bb7fc61567d` |
| Crosswalk | 450 | 452,986 | `5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b` |
| Expanded minimal index | 996 | 185,941 | `072009025272fcba372b820a2ecbd1c65f5938138c5206f19e7cfcdf83ecc39b` |

The 450 changed case IDs equal the 450 unique crosswalk case IDs exactly. All 450 are monthly-only rows. The effective derived disposition is `QUARANTINE_REVIEW_REQUIRED`; the crosswalk retains the more explicit proposed token `RETAIN_QUARANTINE_REVIEW_REQUIRED`. The remaining 546 rows preserve their dispositions. The audit records all 996 non-disposition hash comparisons and original raw-source JSON unchanged flags as true. Gzip decompression reproduces the exact expanded index bytes.

These checks validate the materialized outputs, crosswalk links and recorded row-audit fields. They do **not** replace a fresh end-to-end run against all original frozen inputs.

## 3. Important verification limit

The original CP-0041 source ZIP/worklist and CP-0040 rulebook raw bytes were not available in the checked repository paths and relevant current Library retrieval results during this recheck. Their documented hashes remain:

- CP-0041 source pack: `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`
- Original 996-row worklist: `f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f`
- CP-0040 rulebook: `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`

Fresh current-session raw-byte rehash of those original inputs: **NOT_VERIFIED**. Do not present their expected hashes as newly recomputed.

## 4. GitHub Actions run distinction

The latest known run was [#42 / 38779041545](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38779041545), conclusion `success`, artifact ID `11994173921` (172,937 bytes; not expired). It checked out `17bedc3151fff525c4d58f58a196ccca4fc2c2c6`, so it predates the later `main` commits and is **not** proof that the current HEAD or new index was tested. No new run is claimed for this evidence-only publication.

## 5. Decision limits and current gates

- Disposition changes: 450; unchanged rows: 546.
- Canonical source: `NONE`; source cases closed: 0; root cause: `OPEN_NOT_ESTABLISHED`.
- No timestamp shifts/rounding, raw-row merge/replacement/deletion, synthetic candles, backtest rerun or strategy promotion.
- G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.
- Live signing, public broadcast and exchange orders remain blocked.

## अगला सीमित checkpoint

मौजूदा CP-0107 snapshots तथा official checksum evidence का उपयोग करते हुए 52 shared economic/trade-metric conflicts की official archive-version/provenance adjudication करें। व्यापक archive refetch न करें; candidate promotion या backtest rerun तभी विचारें जब adjudication से dataset bytes/hash में प्रमाणित बदलाव हो और frozen rules rerun अनिवार्य करें।

Machine-readable companion: `evidence/source_adjudication/CP0107_Final_Continuity_Reconciliation_Summary.json`.
