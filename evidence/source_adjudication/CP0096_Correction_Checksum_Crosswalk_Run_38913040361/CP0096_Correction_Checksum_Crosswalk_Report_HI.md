# CP-0096: Official correction checksum crosswalk

Status: PASS_CHECKSUM_CROSSWALK_NO_ARCHIVE_HASH_HITS_SOURCE_AUTHORITY_OPEN

## Provenance and integrity
- Reused the prior CP-0092 correction ZIP; no download or source mutation.
- ZIP 6,653,240 bytes; SHA-256 1404dbfb3d62534b2576a6c0c046826fe652f895b9bebfe4c13df58bc8cf6240; Git blob SHA-1 90631298cf50ac2e1ee8372a087767b010d78a21; CRC PASS.
- Official CSV SHA-256 94fea6dfad2903b5a1b0ed0193c9694318655e00f7d164224be72e82d7599046; 73,234 rows. Previous exact path/basename audit CP-0095: 0/16 matches.
- 16 daily archive ZIPs have verified official checksum tokens and ZIP CRC; 14 monthly archives match frozen source-manifest hashes and CRC.

## Hash-field crosswalk
- Compared exact SHA-256 values of all 16 daily ZIPs and 14 monthly ZIPs against every parsed Original File Checksum and New File Checksum token in the official correction CSV.
- Daily archive checksum hits: 0/16; monthly archive checksum hits: 0/14.
- This audit is broader than filename matching: it can detect same archive bytes listed under an alternate path/name.

## Decision boundary
- A checksum hit would be evidence of byte identity for that archive, not by itself a canonical-source decision for individual conflicting raw rows.
- No source selected; source authority remains UNDETERMINED; cases closed=0. Global G0 BLOCKED_GLOBAL, G2 current 23 candidates FAIL, G7 LIVE_BLOCKED.
- No downloads, row changes, timestamp edits, synthetic candles, candidate builds, backtests or exchange actions.

## Next action
- If there are no checksum hits, stop rechecking this correction bundle for this frozen source set and continue only with new exact-row official evidence.
