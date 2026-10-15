# CP-0107: समेकित evidence reconciliation

**स्थिति:** `EVIDENCE_RECONCILED_ADJUDICATION_OPEN_NOT_STRATEGY_ACCEPTANCE`

पुराने draft में `0/16` official daily ZIP/checksum pairs लिखा था। वह ऐतिहासिक स्थिति थी। बाद के acquisition attempt ने 16 pairs capture किए, पर CSV output defect पर रुका; उसी artifact को reuse करके सफल run 38775666304 ने 98/98 checks पास किए। ZIP दोबारा download नहीं हुए।

## Verified results

- **February 2018:** 450 monthly off-grid rows; exact daily open-time counterparts 0; disposition `QUARANTINE_REVIEW_REQUIRED`.
- **December 21, 2020:** 59 raw-row records, 34 roll-up comparisons, 9 review-required roll-ups. 16 common 5m keys में 9 exact pairs और 7 divergent pairs। आठ rows पर close-time token `1608558440521` (13:47:20.521 UTC) साझा है। Missing 5m children: monthly 10, daily 14; incomplete aggregates unavailable रहते हैं।
- **Close-time-only:** 8/8 economic fields exact; monthly boundary mismatch 5 और daily mismatch 3। सिर्फ `close_time` metadata-field proposal; कोई canonical archive नहीं।
- **11 aggregation buckets:** daily child roll-ups अपने daily parent से 11/11 match; monthly mismatch signature 11/11 reproduce। एक bucket की exact numeric volume representation अलग है, इसलिए review खुला है।
- **7 residual December monthly-only rows:** daily exact-key counterpart 0/7; flat OHLC `22646.53000000`, volume/trades zero; सभी OPEN।
- **996-row CP-0041 worklist:** crosswalk 450/450 rows और सभी 12 raw fields match करता है। Append-only delta 450 rows quarantine प्रस्तावित करता है; अन्य 546 rows और original worklist unchanged हैं।

## Verified GitHub Actions

- [38771142900: February extraction, 9/9 PASS](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38771142900)
- [38771593935: December field/sidecar review](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38771593935)
- [38775666304: daily-reference audit, 98/98 PASS](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38775666304)
- [38776970911: bucket overlay, 12/12 PASS](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38776970911)
- [38777979719: 450-row delta, 11/11 PASS](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38777979719)
- [38779041545: seven residual rows, 30/30 PASS](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38779041545)

## Decision limits

Canonical source selected: **0**. Cases closed: **0**. Root cause: `OPEN_NOT_ESTABLISHED`. No raw archive edits, timestamp changes, merges/replacements/deletions, synthetic candles, backtest rerun or strategy promotion.

Gates unchanged: G0 `BLOCKED_GLOBAL`; G1 `PARTIAL_SYSTEM_LEVEL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL`; G4 `INSUFFICIENT_EVIDENCE`; G5 `NOT_RUN`; G6 `NOT_BUILT`; G7 `LIVE_BLOCKED`.

## अगला bounded action

Verified CP-0041 pack से exact 996-row worklist materialize करके **derived, not replacement** 996-row view बनाना है। उसमें सिर्फ 450 quarantine dispositions apply हों और case ID/raw-row hash से 450 changed + 546 unchanged prove हों। Original pack immutable रहेगा; फिर unresolved daily-only और shared economic conflicts जारी होंगे।
