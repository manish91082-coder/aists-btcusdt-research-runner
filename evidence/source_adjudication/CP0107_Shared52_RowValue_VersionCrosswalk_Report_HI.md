# CP-0107: Shared-52 raw-value और official checksum crosswalk audit

**Status:** `PASS_ROW_VALUE_CROSSWALK_RECONCILIATION_SOURCE_AUTHORITY_OPEN`  
**Scope:** 52 economic/trade-metric conflicts; existing Shared-60 raw-field provenance audit के raw monthly/daily row values और official correction-bundle crosswalk का join।

## Verified results

- 52/52 unique economic case IDs और 52/52 exact case-ID joins।
- Official correction bundle में 33/52 rows के exact daily archive paths मिले, जो 14 unique daily archive objects से संबंधित हैं। 19/52 rows के लिए इस bundle में exact daily path नहीं मिला।
- Exact-path matched 33 rows में official **New File Checksum** frozen daily archive SHA-256 से 33/33 match हुआ; **Original File Checksum** 0/33 में match हुआ।
- Monthly तथा daily raw row JSON और field-level economic differences 52/52 मामलों के लिए output में संरक्षित हैं। Disposition 52/52 में `UNRESOLVED_SOURCE_CONFLICT_NO_AUTO_CORRECTION` रही।
- Output: `evidence/source_adjudication/CP0107_Shared52_RowValue_VersionCrosswalk.csv`; 116236 bytes; 52 rows / 30 columns; SHA-256 `6a4175567f2af0d0a7e6cf45b76485f496faa680a7248f30e118e55bb2ed0af9`।

## Raw-value signal

- Exact official-path matched subset में सभी 33 rows में volume, quote-volume और trade-count metrics अलग हैं; 30/33 में कम-से-कम एक OHLC field भी अलग है।
- Exact-path-unmatched subset में 19/19 rows के trade/volume metrics अलग हैं; 15/19 में कम-से-कम एक OHLC field भी अलग है।
- 2020-12-21 के 13 no-path cases विशेष review group हैं: monthly rows के कुछ raw values flat OHLC `22646.53000000` और zero volume/trade-count दिखाते हैं, जबकि उसी open-time की daily raw values active prices/volume/trade counts दिखाती हैं। यह observed raw-value conflict है, पर root cause या source authority का प्रमाण नहीं।
- शेष no-path cases: 2018-02-11 (1h, 1), 2021-01-21 (1d और 4h, 2), 2021-09-23 (5m, 1), 2021-12-24 (1d और 4h, 2)।

## Limits / decision

Official bundle का New-checksum match केवल archive-version provenance evidence है। इससे daily को canonical घोषित नहीं किया गया। यह bounded task stored CP0107 row tokens और crosswalk पर आधारित था; सभी source archives पुनः download/reparse नहीं किए गए।

CP-0040 rulebook का expected hash `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0` recorded reference है, लेकिन full standalone rulebook bytes का fresh re-verification अभी `NOT_VERIFIED` है। Source canonical नहीं, cases closed 0, root cause `OPEN_NOT_ESTABLISHED`, कोई backtest/promotion नहीं। Live signing, public broadcast और exchange orders blocked हैं।

## Frozen gates

G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.
