# मास्टर शोध लॉग: 1,000 USDT से ₹10 करोड़-समतुल्य लक्ष्य

**Version:** 1.7  
**Last updated:** 22 October 2026  
**Repository:** [aists-btcusdt-research-runner](https://github.com/manish91082-coder/aists-btcusdt-research-runner)  
**अभी का चरण:** Data integrity pipeline से पहले research harness और project governance को व्यवस्थित करना।

## 1. लक्ष्य और इसकी सीमाएँ

- प्रारंभिक equity की धारणा: **1,000 USDT**.
- कार्यशील लक्ष्य: **1,061,120.54 USDT**, जो 22 अक्टूबर 2026 के दर्ज ₹94.24/USDT snapshot पर लगभग ₹10 करोड़ के बराबर है।
- आवश्यक वृद्धि: लगभग **1,061.12×**.
- यह FX conversion एक dated reference है। INR/USDT दर बदलने पर लक्ष्य राशि को स्पष्ट रूप से पुनः निर्धारित करना होगा।
- “Compounding” का अर्थ realized **net profit** को equity में जोड़ना और बाद की position sizing में शामिल करना है। इससे यह निष्कर्ष नहीं निकलता कि हर घंटे trade करना है या केवल 1-hour candles उपयोग करनी हैं।
- कोई अतिरिक्त deposit नहीं माना गया है। Live exchange access, live orders और funds movement इस research setup में अधिकृत नहीं हैं।

## 2. गणितीय hurdle, return forecast नहीं

यदि equity काल्पनिक रूप से समान दैनिक geometric rate से बढ़े, तो लक्ष्य तक पहुँचने के लिए आवश्यक दरें लगभग होंगी:

| काल्पनिक अवधि | आवश्यक औसत net geometric daily growth |
|---:|---:|
| 30 दिन | 26.14% |
| 90 दिन | 8.05% |
| 180 दिन | 3.95% |
| 365 दिन | 1.93% |
| 730 दिन | 0.96% |
| 1,095 दिन | 0.64% |

ये केवल गणितीय आवश्यकताएँ हैं, रणनीति की उपलब्धि या संभावना का अनुमान नहीं। वास्तविक return path असमान हो सकता है; losses, drawdown, costs और ruin risk लक्ष्य को बहुत दूर या असंभव बना सकते हैं। इन rates को expected return मानना गलत होगा।

## 3. अभी क्या वास्तव में बना है

- `crypto_target/research_math.py`: target multiple, geometric period-return hurdle, realized-return compounding path और maximum drawdown के deterministic helpers.
- `tests_crypto_target/test_research_math.py`: इन helpers के पाँच unit tests.
- `.github/workflows/crypto-target-smoke.yml`: Python compilation, required-document consistency, allowlist dry-run और unit-test workflow.
- `README.md`, `CRYPTO_10CR_PROJECT_DETAILS.md`, यह master log और `CRYPTO_10CR_PROJECT_STATUS.md`: scope, governance और current state.
- `scripts/cleanup_current_project.py` तथा `CURRENT_PROJECT_KEEP_PATHS.txt`: fail-closed, dry-run-by-default repository-cleanup utility और उसकी protected-path सूची.
- `execution_logs/`: execution और verification records.

**सीमा:** math helpers कोई entry/exit signal, execution simulator या trading strategy लागू नहीं करते।

## 4. Research hypotheses, अभी निष्कर्ष नहीं

इन परिवारों को केवल data और executable assumptions उपलब्ध होने पर परखा जा सकता है:

1. Multi-timeframe trend/momentum और breakout.
2. Regime-filtered mean reversion.
3. Volatility compression/expansion तथा event-driven methods.
4. Cost-aware no-trade filters.
5. Spot/perpetual funding, basis या carry, यदि hedge और execution costs ठीक से model किए जा सकें.
6. Cross-venue price differences, केवल simultaneous executable bid/ask और fees, latency, inventory constraints सहित.
7. Machine learning, केवल तब जब simple baselines के ऊपर robust out-of-sample improvement दिखे.

किसी भी hypothesis को केवल आकर्षक equity curve या in-sample result के कारण स्वीकार नहीं किया जाएगा।

## 5. Data integrity नियम

हर dataset के लिए source, product type, symbol, interval, start/end timestamps, timezone assumptions, retrieved object/URL, retrieval time, file size, checksum, schema और row count दर्ज किए जाएँ। Duplicate/out-of-order timestamps, missing intervals, invalid OHLCV, suspicious volume और unexplained gaps की जाँच होनी चाहिए।

Missing prices को fabricated data से भरना या synthetic fill मान लेना निषिद्ध है। किसी correction, exclusion, resampling या adjustment को अलग से document और test करना होगा।

Official starting points:
- Binance public historical data repository: https://github.com/binance/binance-public-data
- Binance public archive host: https://data.binance.vision/

इन links का मौजूद होना data acquisition का प्रमाण नहीं है। जब तक वास्तविक file/object, checksum और validation report run log में न हों, dataset को acquired/validated नहीं माना जाएगा।

## 6. Strategy/backtest नियम

- Decision समय पर अनुपलब्ध information का प्रयोग न हो।
- Candle close से बना signal सामान्यतः अगले defensible executable event पर लागू हो; उसी close पर fill तभी मानें जब execution mechanism उसका समर्थन करे।
- Fees, spread, slippage, funding, borrowing, partial fills, latency और liquidation constraints जहाँ लागू हों, शामिल हों।
- Train/validation/test को chronologically अलग रखें; walk-forward testing और experiment-selection history लिखें।
- No-trade तथा simple baseline से तुलना करें; held-out test को parameter tuning के लिए reuse न करें।
- Net return के साथ drawdown, turnover, exposure, trade count, tail loss, losing streak, cost sensitivity और risk-of-ruin भी report करें।
- Backtest के बाद भी forward/paper validation अलग gate है।

## 7. Evidence gates

| Gate | पास होने का प्रमाण | वर्तमान स्थिति |
|---|---|---|
| G0: Research harness | Versioned helpers, rules और deterministic tests | Implemented; earlier CI run passed |
| G1: Data provenance/integrity | Real source objects, hashes, schema, gaps और validity report | इस workstream में बाकी |
| G2: Baselines | No-look-ahead signals, executable assumptions, costs | शुरू नहीं |
| G3: Out-of-sample edge | Walk-forward net result बनाम baselines | स्थापित नहीं |
| G4: Risk/robustness | Drawdown, tail risk, cost/parameter sensitivity, ruin analysis | शुरू नहीं |
| G5: Forward validation | Paper/forward evidence | शुरू नहीं |
| G6: Live stage | अलग explicit approval और safety review | अधिकृत नहीं |

## 8. Repository cleanup और continuity checkpoint

- इस चैट के दौरान current crypto-target work के लिए नया README और project-details दस्तावेज़ बनाया गया; project status, master log, allowlist, cleanup utility और workflows भी align किए जा रहे हैं।
- GitHub Actions cleanup run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39806484233.
- Legacy tracked files को current `main` से हटाया गया। बाद में repository tree को strict current-thread scope पर verify किया गया; पुराने commits/history और दूसरी branches मिटाई नहीं गईं।
- Cleanup execution और scope verification:
  - `execution_logs/2026-10-22-cleanup-final-verification.md`
  - `execution_logs/2026-10-22-current-thread-only-cleanup.md`
- Cleanup repository-housekeeping था; इसने कोई market data download, backtest या profitability test नहीं किया।

## 9. वर्तमान निर्णय

- Target arithmetic: निर्धारित reference के आधार पर गणना योग्य.
- Real market data integrity for this target workstream: **NOT VERIFIED**.
- Strategy edge: **NOT ESTABLISHED**.
- Target-hit timeline: **UNKNOWN**.
- Live trading: **NOT AUTHORIZED**.
- Tax/TDS: **DEFERRED**.

## 10. अगला चरण

1. स्पष्ट BTCUSDT product type और interval चुनकर reproducible data-acquisition/integrity manifest बनाना।
2. Download/object URL, checksum, schema, timestamp continuity, duplicate और invalid-bar checks लागू करना।
3. Integrity gates पास होने पर multi-horizon simple baselines चलाना, realistic costs के साथ।
4. Walk-forward out-of-sample और risk robustness के बिना strategy को सफल घोषित न करना।
5. हर substantive run के लिए नया append-only execution log बनाना और status को उसी evidence के अनुसार update करना।

## Change control

Research status और claims केवल verified evidence के आधार पर बदलें। Repo cleanup या unit-test pass को market-data validation, profitable edge, या ₹10 करोड़ तक पहुँचने का प्रमाण न मानें।


## 11. दस्तावेज़ एवं सुरक्षा-जाँच refresh — 22 अक्टूबर 2026
- README पुनः बनाया गया और detailed project charter `CRYPTO_10CR_PROJECT_DETAILS.md` जोड़ा गया।
- Project Status को current evidence के अनुसार संक्षिप्त और अद्यतन किया गया; इस master log का version 1.5 है।
- `CURRENT_PROJECT_KEEP_PATHS.txt` अब cleanup utility की वास्तविक allowlist है। Utility required paths जाँचती है और invalid/missing allowlist पर fail-closed होती है।
- Cleanup workflow को manual, read-only preview में सीमित किया गया; सामान्य pushes अब auto-delete/auto-commit नहीं करते।
- Smoke workflow अब Python compilation, required docs/target consistency, allowlist-based cleanup preview में zero deletion candidates और deterministic unit tests जाँचता है।
- Expanded smoke run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873. Log update के समय status queued था; final pass/fail को GitHub के final conclusion के बिना घोषित नहीं किया जाएगा।
- यह documentation/governance update है; market data download या trading backtest नहीं।


## 12. अंतिम tree और document-map audit — 22 अक्टूबर 2026
- पुराने pre-existing README को cleanup checkpoint पर हटाया गया था; इस वर्तमान documentation request पर उसे नए current-thread project README के रूप में फिर बनाया और allowlist में फिर शामिल किया गया। Section 11 उस पहले cleanup checkpoint का ऐतिहासिक रिकॉर्ड है।
- README में Project Status, Project Details, Master Research Log और final verification log के links दिए गए।
- Project Details में current verification log और अगला evidence gate link किया गया; Project Status में final tree audit व pending CI की स्थिति दर्ज है।
- Final audit record: `execution_logs/2026-10-22-docs-final-verification.md`.
- Latest tree audit में 19 tracked files थीं; हर path `CURRENT_PROJECT_KEEP_PATHS.txt` में exact path या protected directory prefix से covered था। Unexpected files: 0.
- इस tree audit के समय run queued था; बाद में final conclusion `success` और सभी steps के pass होने की पुष्टि हुई। अंतिम परिणाम section 13 में दर्ज है।
- Next gate remains real market-data provenance/integrity checks. No market data acquisition, trading backtest, or profitability conclusion was produced by this documentation refresh.


## 13. Expanded smoke checks का अंतिम परिणाम — 22 अक्टूबर 2026
- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39815232873 — final conclusion `success`.
- Python compilation: PASS.
- Required documents exist, target amount consistent across README, Project Details, Project Status और Master Research Log, तथा truth-state markers present: PASS.
- Allowlist dry-run: PASS; **17 tracked files, 17 protected, 0 deletion candidates**. Dry-run ने कोई file नहीं बदली।
- Unit tests: **5/5 PASS**.
- Detailed execution record: `execution_logs/2026-10-22-expanded-smoke-ci-success.md`.
- Earlier sections 11–12 ने run को queue में दर्ज किया था क्योंकि उस समय final conclusion उपलब्ध नहीं था; section 13 वह historical status स्पष्ट रूप से close करता है।
- ये checks helper code, documents और repository protections को validate करते हैं; market-data acquisition या strategy edge को नहीं।
