# CP-0279: Derived Monthly Quarantine Enforcement Audit (Hindi)

**तारीख:** 2026-10-20  
**Branch:** `cp-0120-ai-brain-foundation`  
**Code HEAD verified before this report:** `9ba6a66b588bad20e1f1924c89a96b57656e01ca`  
**Scope:** CP-0026 candidate-builder production-path review only. No market-data build or strategy evaluation.

## निर्णय

Production candidate-builder में derived `1mo` aggregation के लिए exact-key quarantine enforcement अधूरी थी। `1d` candidate में quarantined day को हटाने के बाद भी उस महीने की बची हुई daily bars से monthly candle बन सकती थी; साथ ही `1mo` exact-key quarantine aggregation में लागू नहीं हो रही थी। इससे derived candle quarantine से बचकर candidate file में आ सकती थी।

## किए गए सीमित सुधार

1. `create_monthly_from_daily` अब quarantine keys और case IDs स्वीकार करता है।
2. जिस महीने में `1d` source quarantine key हो, उसकी derived `1mo` candle candidate output में नहीं लिखी जाती।
3. Exact `1mo` interval + monthly open-time quarantine key वाली candle भी output से बाहर रहती है।
4. दोनों स्थितियों को `cp0026_quarantined_candidate_rows.csv` ledger में दर्ज किया जाता है, जिसमें reason, source key(s), case IDs, source SHA-256, bar count और `derived_row_written=false` शामिल हैं।
5. Monthly summary में `quarantined_rows`, `quarantined_exact_key_rows`, और `quarantined_source_input_rows` counters जोड़े गए। Derived quarantine मिलने पर monthly status `BLOCKED_QUARANTINED_DERIVED_INPUTS` रहता है, जिससे overall report का blocking gate सक्रिय रहता है।
6. Report counters अब base source-row quarantines और derived monthly quarantine entries को अलग-अलग दर्शाते हैं।

## Regression और CI सत्यापन

- Added synthetic regression tests:
  - exact `1mo` key quarantined and audited;
  - `1d` source quarantine propagates to and blocks its derived month.
- Existing exact-key, interval isolation, malformed timestamp, manifest SHA-256 mismatch और unresolved non-row blocker tests retained.
- Final code HEAD `9ba6a66b588bad20e1f1924c89a96b57656e01ca`:
  - GitHub Actions run [39372037628](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39372037628): **SUCCESS**.
  - Existing brain suite: 219 tests passed.
  - CP-0026 quarantine suite: 7 tests passed.
- एक intermediate test run में केवल fixture का UTC timestamp अपेक्षित string से अलग था (`+00:00` बनाम `Z`); test expectation को वास्तविक canonical output से मिलाया गया और final run SUCCESS रहा।

## सुरक्षा सीमा और शेष स्थिति

- G0 अभी भी `BLOCKED_GLOBAL`; unresolved source-authority adjudication का समाधान इस code change से नहीं हुआ।
- कोई production candidate build, backtest, paper session, Binance order, signing या public broadcast नहीं चलाया गया।
- कोई market-data result या profitability claim नहीं बनाया गया।
- CP-0040 frozen rulebook या quarantine manifest को बदला नहीं गया।
- PR #2 को merge नहीं किया गया।

## अगला सीमित कदम

इस checkpoint commit के exact HEAD पर GitHub Actions की terminal result verify करें, PR #2 का head/state reconcile करें, और फिर candidate-builder के fail-closed gate को बिना production build चलाए source-level/CI evidence से आगे audit करें। G0 closure के लिए independent source adjudication अब भी अलग अनिवार्य gate है।
