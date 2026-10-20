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
- GitHub Actions run [39311740842](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39311740842) exact HEAD `2f3557d7d4f490c4c442dd936d83230f648de9c1` पर terminal SUCCESS था; compile और test steps सफल; log में 212 tests, `OK` है।
- सावधानी: run log में CP-0276 integration test के नाम स्पष्ट रूप से सूचीबद्ध नहीं दिखे। इसलिए उस run को CP-0276 के नए test की executed verification नहीं माना जाएगा, भले कुल 212 tests पास हों। CP-0276 को complete/verified कहने से पहले नए test file वाले exact commit पर नया CI run चाहिए।
- Fixture FX 100 INR/USDT, fee/slippage और filters केवल test values हैं, वास्तविक FX rate, Binance fee terms या verified exchange snapshot नहीं।
- कोई historical BTCUSDT data, candidate build, performance backtest या paper session नहीं चलाया गया। कोई profitability claim नहीं।

## Gate और सुरक्षा स्थिति
- G0: `BLOCKED_GLOBAL`; canonical historical source: `NONE`.
- G2: मौजूदा 23 candidates FAIL; कोई promotion नहीं।
- G3: blocked; G4: insufficient evidence; G6: adaptive AI NOT BUILT/validated; G7: LIVE BLOCKED.
- CP-0040 frozen rulebook अपरिवर्तित।
- Live signing, public broadcast, Binance orders और automatic SL/TP disabled।
- PR #2 open और unmerged रहना चाहिए।

## अगला सीमित कदम
पहले CP-0276 test file और wrapper वाले वास्तविक current branch HEAD को reconcile करें, फिर उसी exact HEAD पर CI terminal success तथा test-name/count सत्यापित करें। यदि test discovery में शामिल न हो, CI/test pattern ठीक करें। G0 के लिए नया authoritative evidence न मिलने तक real-market run नहीं।
