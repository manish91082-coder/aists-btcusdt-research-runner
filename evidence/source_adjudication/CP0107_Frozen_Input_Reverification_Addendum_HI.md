# CP-0107 Frozen-Input Reverification Addendum (Hindi)

**तारीख:** 16 अक्टूबर 2026  
**स्थिति:** Fresh raw-byte re-verification PASS; 23/23 targeted checks PASS  
**Scope:** CP-0107 derived 996-row worklist के frozen CP-0041 inputs, CP-0040 rulebook, crosswalk और derived outputs की वास्तविक bytes पर पुनः जाँच।

## 1. Frozen source package: fresh verification

Library में उपलब्ध exact source package `/AISTS_CP0041_Row_Level_Evidence_Disposition_Pack.zip` को materialize करके वास्तविक bytes पर जाँचा गया:

- ZIP size: **317,677 bytes**
- ZIP SHA-256: `23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc`
- ZIP CRC: **PASS**
- ZIP members: **19**
- Embedded payload manifest: **18/18 member byte-count checks PASS और 18/18 SHA-256 checks PASS**
- Original CP-0041 worklist: 2,111,342 bytes; SHA-256 `f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f`
- Embedded CP-0040 rulebook: 10,630 bytes; SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`
- Embedded CP-0041 unmatched ledger: 1,850,523 bytes; SHA-256 `11eb82994d5a17469eefee9f14d360537d5871c19d303ed0466c5df4f6c34021`

यह नया raw-byte verification पहले की continuity report में लिखे `fresh raw-byte rehash NOT_VERIFIED` status को **इस addendum के scope में supersede** करता है। पुरानी रिपोर्ट को overwrite नहीं किया गया।

## 2. Crosswalk और derived worklist की स्वतंत्र तुलना

- CP-0107 crosswalk (materialized Library file; no GitHub repository path is asserted): 450 rows, 452,986 bytes; SHA-256 `5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b`
- Derived worklist (materialized Library file): 996 rows, 2,099,092 bytes; SHA-256 `137ad77bfafa7f7cd788db6f744e5567ad7dba889048b58feb743a34b863d9cb`
- Per-row audit (materialized Library file): 996 rows, 792,477 bytes; SHA-256 `717125e5abd83f987139d76df7ba245b972ad52438d4c64bb2e8bf06901012aa`
- Derived summary (materialized Library file): 7,294 bytes; SHA-256 `31bf7846d3429e6590724250459bf2fc1317dcabccf71cca8c21b5ed575fee96`

ताज़ा reproducible comparison का परिणाम:

1. Original और derived worklist में **996/996 unique case IDs** हैं; ID set में कोई missing या extra case नहीं।
2. Exactly **450 rows** बदलीं, और ये IDs crosswalk की **450/450 unique IDs** से exact match करती हैं।
3. इन 450 rows में केवल `current_disposition` field बदली; किसी अन्य field में बदलाव **0**।
4. बाकी **546/996 rows पूरी तरह unchanged** हैं।
5. Crosswalk के 450/450 rows में monthly archive hash match और सभी 12 raw fields की CP-0041 equality flag PASS है।
6. सभी 450 crosswalk proposals `RETAIN_QUARANTINE_REVIEW_REQUIRED` हैं; `canonical_source=NONE`।
7. Row audit में 996/996 non-disposition unchanged flags और 996/996 original-source-row-JSON unchanged flags true हैं। Audit में दर्ज source/worklist/crosswalk/package/rulebook hashes verified frozen hashes से match करते हैं।

## 3. Check register

**23/23 PASS, 0 FAIL**:

- Source ZIP SHA-256, ZIP CRC और 18 embedded member byte-count/SHA-256 pairs।
- CP-0040 rulebook, CP-0041 original worklist और CP-0107 crosswalk के fresh SHA-256।
- 996-row count, unique IDs और original/derived exact ID-set equality।
- 450-row change set equals crosswalk targets; 546 rows unchanged।
- Disposition-only changes; zero non-disposition changes।
- 450/450 crosswalk archive-hash and 12-field equality flags।
- 996/996 audit invariants and frozen-input hash references.

## 4. Decision boundaries

यह integrity/disposition validation है, market-source authority का निर्णय नहीं।

- Canonical source: **NONE**
- Source cases formally closed: **0**
- Root cause: `OPEN_NOT_ESTABLISHED`
- 450 February off-grid rows: `QUARANTINE_REVIEW_REQUIRED`
- 52 shared economic conflicts और अन्य unresolved rows: अपने existing open dispositions में बने रहेंगे।
- कोई timestamp shift/rounding, raw-row merge/replacement/deletion, synthetic candle, backtest rerun या strategy promotion नहीं।
- Frozen gates unchanged: G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.
- Live signing, public broadcast और exchange orders blocked रहेंगे।

## 5. Execution evidence / limitation

यह addendum Library से materialize किए गए source/output bytes पर local hash/row-level checks और GitHub पर इस addendum के fetch-back पर आधारित है। इस addendum को publish करने के लिए कोई GitHub Actions run execute नहीं किया गया; इसलिए इस addendum के लिए CI success का दावा नहीं है। GitHub पर report, JSON और state note publish होने के बाद exact fetch-back verification अलग से दर्ज किया जाना है।

## अगला checkpoint

इसी verified crosswalk का उपयोग करके 52 shared economic/trade-metric conflicts के source-version evidence को final disposition matrix में बाँधें। Official correction bundle के 33 exact path matches provenance-only evidence हैं; 19 no-path cases unresolved हैं। कोई source authority decision केवल frozen rules और पर्याप्त evidence से ही होगा।
