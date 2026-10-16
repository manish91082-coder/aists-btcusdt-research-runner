# CP-0115: Candidate-universe interval exposure audit for the 14 monthly conflicts

**तारीख:** 2026-10-16
**स्थिति:** `PASS_CANDIDATE_INTERVAL_OVERLAP_AUDIT_G0_STILL_BLOCKED`
**सीमा:** frozen CP-0043 candidate eligibility matrix और CP-0113/CP-0114 evidence का read-only join। कोई नया candidate build या backtest नहीं।

## 1. इस्तेमाल किए गए प्रमाण

- CP-0043 candidate matrix: `AISTS_CP0043_Candidate_G0_G1_Eligibility_Matrix.csv`, 33,602 bytes, SHA-256 `e18d0a2bbf6e724eb11507b35b3c0c4dfebbc5bfeda3c310c3f9e1b9f15b01c9`. यह hash CP-0045 package integrity record में दर्ज है; उसी exact named file को Library से पढ़ा गया।
- Candidate matrix में 23 candidates हैं। प्रत्येक candidate का `local_interval`, `higher_interval`, candidate-scoped G0 result और G2 historical-screen status crosswalk में सुरक्षित है।
- CP-0113 report blob SHA-1: `50973223cbb94eb1889f946d51369f7e7c5c63a5`; CP-0113 current pointer blob SHA-1: `6d3476ed2770d1629596ea8e94e8508dabac776d`.
- CP-0114 report blob SHA-1: `1546408f8b6c77b21a62fbd92fa9aceebdfcbe25`; CP-0114 current pointer blob SHA-1: `ab6997b1d8dabcbaaccbba0f8f9915a8f11280cb`.

## 2. Candidate-overlap परिणाम

| माप | सत्यापित परिणाम |
|---|---:|
| Frozen candidate universe | 23 |
| G2 historical screen FAIL | 23/23 |
| Candidate-scoped G0 BLOCKED in CP-0043 matrix | 12 |
| Candidate-scoped G0 PASS in CP-0043 matrix | 11 |
| CP-0113 monthly-divergent keys | 14 keys / 97 fields |
| Conflict keys by interval | 5m: 9; 15m: 4; 30m: 1 |
| Candidates whose local interval directly overlaps those conflict intervals | 9 |
| Exact CP-0113 monthly-conflict keys on the 1h interval | 0 |
| Exact CP-0113 monthly-conflict keys on 4h, 1d, 1mo | 0 |

### नौ candidate configurations जिनके local interval पर direct overlap है

**5m: 9 conflict keys, तीन candidate configurations**
- `CP0027_5m_EMA_12_26`
- `CP0027_5m_RSI14_30_55`
- `CP0027_5m_DONCHIAN20_10`

**15m: 4 conflict keys, तीन candidate configurations**
- `CP0027_15m_EMA_12_26`
- `CP0027_15m_RSI14_30_55`
- `CP0027_15m_DONCHIAN20_10`

**30m: 1 conflict key, तीन candidate configurations**
- `CP0027_30m_EMA_12_26`
- `CP0027_30m_RSI14_30_55`
- `CP0027_30m_DONCHIAN20_10`

इन नौ candidates में historical data interval और conflict interval का direct overlap है। यह **candidate-specific exact key का current builder input में वास्तव में consume होना या quarantine से exclude होना साबित नहीं करता**। CP-0040 G0 gates के कारण कोई नया production candidate build नहीं चलाया गया। इसलिए crosswalk `exact_row_consumption_in_new_builder=NOT_VERIFIED_NO_NEW_CANDIDATE_BUILD` दर्ज करता है।

### बाकी candidate groups

- तीन `1h` candidates CP-0043 में candidate-scoped G0 BLOCKED हैं क्योंकि low-timeframe source policy unresolved है, हालाँकि CP-0113 के 14 *monthly-divergent* keys में कोई 1h key नहीं है। यह उन्हें स्वतः eligible नहीं बनाता; 11 cross-interval relationship blockers अभी भी खुले हैं।
- तीन `4h`, तीन `1d`, तीन `1mo` और दो multi-timeframe candidates के local/higher intervals में CP-0113 के 14 exact monthly-divergent keys का direct interval overlap नहीं है। CP-0043 का candidate-scoped G0 PASS historical matrix outcome है, वर्तमान global G0 PASS नहीं। G2 इन सभी 23 candidates पर FAIL है।

## 3. CP-0114 quarantine-application gap के साथ मिलाकर निष्कर्ष

CP-0114 ने दिखाया कि सभी 14 monthly-conflict keys frozen 1,427-row exact-key manifest में हैं, लेकिन इनमें से `0/14` CP-0040 sensitivity run की actual applied-key list में हैं। वह executed sensitivity set केवल छह 4h और तीन 1d keys का था। अतः manifest में key होना quarantine filter का candidate input पर लागू होना नहीं है।

CP-0115 अब बताता है कि interval स्तर पर नौ low-timeframe candidate configurations सीधे conflict intervals के संपर्क में हैं। लेकिन exact key consumption/exclusion का प्रमाण अभी नहीं है, क्योंकि new builder run G0 के कारण नहीं चला। तीन 1h candidate configurations का candidate-scoped G0 भी broader unresolved low-timeframe policy के कारण blocked है, भले ही इन 14 monthly field divergences में उनका local interval न हो।

## 4. निर्णय

**G0 को upgrade नहीं किया जाएगा।** यह audit 9 direct interval-overlap candidate configurations पहचानता है, लेकिन exact row-level consumption/exclusion की पुष्टि नहीं करता। Frozen CP-0040 source authority rule में daily-over-monthly automatic precedence नहीं है।

अगला सीमित कदम frozen builder/input dependency definitions के आधार पर उन नौ candidates के लिए प्रत्येक exact `(interval, open_time_ms)` conflict key का inclusion/exclusion प्रमाण निकालना है। अगर builder की G0 guard यह static result उत्पन्न होने से भी रोकती है, तो उस सीमा को दर्ज करके सभी प्रभावित keys unresolved/quarantined ही रहेंगी। Raw source files, rulebook, candidate universe या acceptance thresholds नहीं बदलेंगे।

## 5. गैर-कार्रवाइयाँ और gates

- Source bytes में कोई बदलाव नहीं; कोई network call या archive download नहीं।
- कोई candidate build/backtest, strategy promotion, timestamp shift, synthetic candle, signing, public broadcast या Binance order नहीं।
- G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G7 `LIVE_BLOCKED`।
- Canonical source `NONE`; source cases closed `0`; 11 aggregation blockers unresolved।

## Artifact

[23-candidate interval exposure crosswalk CSV](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/evidence/source_adjudication/CP0115_Candidate_Universe_Interval_Exposure_Crosswalk.csv)
