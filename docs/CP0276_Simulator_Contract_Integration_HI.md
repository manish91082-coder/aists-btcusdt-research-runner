# CP-0276 — Capital/Cost Contract से Simulator Integration (Hindi)

तिथि: 2026-10-20  
स्थिति: Software integration checkpoint; market research gate clearance नहीं।

## उद्देश्य
CP-0275 के evidence-gated INR-to-USDT capital/cost contract को offline next-open simulator से जोड़ना, ताकि simulator को contract से पूँजी, allocation, fee, slippage और BTCUSDT symbol filters मिलें और unverified assumptions चुपचाप contract-bound path में उपयोग न हों।

## लागू बदलाव
- `aists_brain/cost_aware_simulator.py` में `simulate_next_open_with_capital_cost_contract(...)` wrapper जोड़ा/सत्यापित किया।
- Wrapper schema version, modeling-only status, G0 boundary, safety flags, जरूरी numeric inputs और प्रत्येक required input का non-empty source reference जाँचता है।
- `research_input_scope` को स्पष्ट रूप से `SYNTHETIC_SOFTWARE_FIXTURE_ONLY` होना जरूरी है। G0 blocked रहते historical market input वाला scope अस्वीकार होता है।
- Simulator को `capital_usdt`, `allocation_fraction`, `fee_bps_per_side`, `slippage_bps_per_side` और `symbol_filters` सीधे validated contract से मिलते हैं।
- Result में contract schema/status, fixture-only execution mode, source references और explicit safety boundary शामिल हैं।
- `tests/test_market_simulator_contract_integration.py` में synthetic fixtures से contract wiring, 2 simulated events, blocked contract, missing source reference, wrong schema, historical scope rejection और forged gate-boundary rejection के tests हैं।

## सत्यापन और सीमाएँ
- Test commit `1c052b2b415a075d15fc25f821ec4586c4d1e4b4` पर GitHub Actions run [39362322504](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39362322504) terminal SUCCESS: compile और test steps सफल; कुल 219 tests, `OK`।
- Logs में `test_non_finite_contract_capital_is_rejected_by_simulator` नाम से नया test स्पष्ट रूप से चला और पास हुआ। PR #2 HEAD भी इस test commit से मेल खाता है और PR OPEN/unmerged है।
- Fixture FX 100 INR/USDT, fee/slippage और filters केवल test values हैं, वास्तविक FX rate, Binance fee terms या verified exchange snapshot नहीं।
- कोई historical BTCUSDT data, candidate build, performance backtest या paper session नहीं चलाया गया। कोई profitability claim नहीं।
- Roadmap/report के बाद आने वाले documentation-only commit के exact HEAD पर CI को फिर से verify करना आवश्यक है।

## Gate और सुरक्षा स्थिति
- G0: `BLOCKED_GLOBAL`; canonical historical source: `NONE`.
- G2: मौजूदा 23 candidates FAIL; कोई promotion नहीं।
- G3: blocked; G4: insufficient evidence; G6: adaptive AI NOT BUILT/validated; G7: LIVE BLOCKED.
- CP-0040 frozen rulebook अपरिवर्तित।
- Live signing, public broadcast, Binance orders और automatic SL/TP disabled।
- PR #2 open और unmerged रहना चाहिए।

## अगला सीमित कदम
CP-0276 code/test commit पर CI सत्यापित है। अब documentation-final HEAD का CI terminal result और test count फिर से verify करना है। उसके बाद अगला कदम G0 के वास्तविक external dependency (authorized independent adjudication / authoritative Binance historical-version evidence) पर ही केंद्रित होगा, न कि और infrastructure जोड़ने पर। G0 के लिए नया admissible evidence न मिलने तक real-market run नहीं।
