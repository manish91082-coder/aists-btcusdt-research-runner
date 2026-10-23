# मास्टर शोध लॉग: 1,000 USDT से ₹10 करोड़-समतुल्य लक्ष्य

**Version:** 2.2  
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


## 14. Final-document consistency run — 22 अक्टूबर 2026
- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817044689 — conclusion `success`.
- Tested commit: `038bf51cff07d1396f6a7a5d0baef25422c4c274`.
- Required current documents and target/status consistency: PASS; stale expanded-CI pending marker in README/Project Details/Project Status: absent.
- Committed allowlist dry-run: **20 tracked, 20 protected, 0 deletion candidates**.
- Deterministic unit tests: **5/5 PASS**.
- Run log: `execution_logs/2026-10-22-final-docs-ci-success.md`.
- This is a documentation/repository-integrity validation, not a market-data backtest or proof of trading profitability.


## 15. Latest end-to-end repository smoke run — 22 अक्टूबर 2026
- GitHub Actions: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39817387843 — conclusion `success`.
- Tested commit: `67c08f8d9c370e8d1f3171f5f7175ce6db41c016`.
- Current summary documents: required target and truth-state checks PASS; no stale pending label; valid Actions run links found.
- Keep-list dry-run: **21 tracked files, 21 protected, 0 deletion candidates**.
- Python compilation: PASS; helper unit tests: **5/5 PASS**.
- Detailed execution log: `execution_logs/2026-10-22-final-current-thread-ci-success.md`.
- Latest `main` tree now includes 22 current-thread files because the successful run record was added afterward; all tracked paths remain covered by `CURRENT_PROJECT_KEEP_PATHS.txt`, and no legacy/unexpected files remain.
- Research truth remains unchanged: no validated market data or strategy backtest yet; profitability not established and target time unknown.


## 16. Fully AI-driven autonomous trading ecosystem और primary target — 22 अक्टूबर 2026
- उपयोगकर्ता ने स्पष्ट किया कि लक्ष्य केवल strategy research नहीं, बल्कि पूरा **AI-driven autonomous trading ecosystem** है: current market state के अनुसार AI trade/no-trade, direction, market/strategy/timeframe, entry, exit, initial/trailing stop-loss, take-profit/trailing-profit, sizing, portfolio risk और regime adaptation तय करे।
- प्राथमिक लक्ष्य अब स्पष्ट रूप से **1,000 USDT → 10,000,000 USDT (10M USDT)** है, यानी 10,000× equity multiple। यह लक्ष्य है, guaranteed return या timeline नहीं।
- पहले दर्ज **1,061,120.54 USDT** ₹10 करोड़ का dated USDT-equivalent था; इसे अलग historical/secondary milestone के रूप में रखा गया है, 10M USDT से conflation नहीं करना है।
- नई architecture: `AI_AUTONOMOUS_TRADING_ARCHITECTURE.md`. इसमें data provenance, AI ensemble, dynamic entry/exit, SL/trailing SL, TP/trailing profit, net-cost economics, deterministic risk engine, execution reconciliation, model registry, kill switches, evaluation gates और implementation roadmap परिभाषित हैं।
- `CURRENT_PROJECT_KEEP_PATHS.txt` में architecture file को protect किया गया।
- अभी यह design/plan है, fully implemented bot नहीं। Market data acquisition, realistic backtester, AI model evaluation और execution simulator अभी बाकी हैं। Live orders/API credentials/funds movement अधिकृत नहीं हैं।
- अगला implementation gate: reproducible BTCUSDT data acquisition/integrity manifest; फिर cost-aware simulator और baselines; उसके बाद AI components को एक-एक करके out-of-sample evaluate करना। Hard risk controls AI से अलग और non-bypassable रहने चाहिए।


## 17. AI architecture और 10M target की automated verification — 22 अक्टूबर 2026
- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39819921442 — conclusion `success`.
- Tested commit: `98df0429d12ce9457fcc4ba7dded621c7e55bc95`.
- Architecture file मौजूद और required-doc check में शामिल: PASS.
- Primary target `10,000,000 USDT` पाँचों core/design documents में consistent: PASS; ₹10 करोड़ का पुराना `1,061,120.54 USDT` reference अलग रखा गया।
- Python compilation, allowlist dry-run और 5/5 unit tests: PASS.
- Execution record: `execution_logs/2026-10-22-ai-architecture-ci-success.md`.
- ये repository/design checks हैं; AI trading system end-to-end अभी implemented नहीं, और कोई market-data backtest या profitability evidence उपलब्ध नहीं।


## 18. लक्ष्य की गलती का सुधार — 22 अक्टूबर 2026
- उपयोगकर्ता ने स्पष्ट किया कि सही और अंतिम लक्ष्य **₹10 करोड़ के बराबर लगभग 1,061,120.54 USDT** ही है।
- `10,000,000 USDT` को primary target बनाना गलती थी। इसे current goal, status, architecture और planning से हटाया गया है।
- ₹10 करोड़ का USDT equivalent **22 अक्टूबर 2026 के दर्ज ₹94.24/USDT snapshot** पर आधारित है; conversion rate बदल सकता है। जब तक उपयोगकर्ता अलग निर्देश न दें, project target 1,061,120.54 USDT ही रहेगा।
- AI autonomy की बाकी requirement अपरिवर्तित है: dynamic AI decisions, entry/exit, SL/trailing SL, TP/trailing profit, cost-aware sizing, risk controls और staged validation।
- इस सुधार के बाद documentation और CI target checks को फिर से सत्यापित करना अनिवार्य है। पिछली section 16–17 में 10M USDT लिखे जाने का रिकॉर्ड ऐतिहासिक change-log है, current goal नहीं।


## 19. End-to-end योजना और zero-drift gate lock — 22 अक्टूबर 2026
- उपयोगकर्ता के निर्देशानुसार पूरा evidence-gated execution plan `END_TO_END_EXECUTION_PLAN_HI.md` बनाया गया।
- सही लक्ष्य: **1,000 USDT → 1,061,120.54 USDT**, दर्ज 22-Oct-2026 ₹94.24/USDT snapshot पर लगभग ₹10 करोड़। 10M USDT accidental target नहीं है। लक्ष्य तक पहुँचने का समय और profitability अभी अज्ञात हैं।
- योजना में governance, HD-03 data integrity, HD-04 universe coverage, leak-proof dataset building, cost-aware simulator, baselines, preregistered walk-forward experiments, AI components, independent risk engine, execution simulator, paper/forward tests और अलग live authorization gate शामिल हैं।
- **Current single next gate: HD-03** — September 2026 BTCUSDT Spot और USDⓈ-M Futures 5-minute data के वास्तविक source, files, SHA-256, UTC coverage, missing/duplicate/schema/OHLC checks और reproducible report का प्रमाण। इसके पास होने से पहले strategy/AI backtest नहीं।
- README, Project Details, Project Status और keep-list को plan से जोड़ा गया। कोई live trading/API credential/fund movement अधिकृत नहीं है।
- CI run और उसके final result को execution log में अलग से दर्ज किया जाएगा; green CI केवल repository checks का प्रमाण है, trading edge का नहीं।


## 20. योजना की CI जाँच — 22 अक्टूबर 2026
- GitHub Actions: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39822482423 — `success`.
- Tested commit: `a2450df4c76fb2e88b92a14432f50d81c7bb24a1`.
- End-to-end plan required-doc/target/HD-03 checks: PASS; keep-list dry-run: PASS; Python compilation: PASS; deterministic tests: 5/5 PASS.
- Execution log: `execution_logs/2026-10-22-end-to-end-plan-baseline.md`.
- यह केवल repository/plan checks हैं। HD-03 data acquisition/integrity अभी भी अगला gate है और इसका data evidence इस run में उत्पन्न नहीं हुआ।


## 21. HD-03 data gate का वास्तविक परिणाम — 22 अक्टूबर 2026
- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39823937420 — acquisition/validation step और job `success`.
- Tested commit: `95bdf820f783e0423911243c2a466b71af410966`.
- Binance Spot और USDⓈ-M Futures, दोनों के सितंबर 2026 BTCUSDT 5m archives डाउनलोड हुए। प्रत्येक में अपेक्षित 8,640/8,640 candles; पहली candle 2026-09-01 00:00 UTC, अंतिम 2026-09-30 23:55 UTC.
- दोनों Binance `.CHECKSUM` sidecars उपलब्ध और SHA-256 match: Spot `4106fc73698fd1851b1821cd0293adc6304f86f0c2e72244e15c41f63c2bde08`; USDⓈ-M Futures `3a2d163a2bd28ca614fa0840a92ecbcde0d9c4962b278dd619d5bf81a9918e26`.
- दोनों में missing intervals, duplicates, off-grid/out-of-month timestamps, numeric/trade-count, OHLC और close-time issues: सभी 0. Synthetic validator tests: 2/2 PASS (valid month accepted, injected duplicate/gap rejected).
- Artifact (original ZIPs + JSON report, 30-day retention): https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39823937420/artifacts/12445537564. विस्तृत log: `execution_logs/2026-10-22-hd03-data-integrity-pass.md`.
- सीमा: यह केवल एक महीने, एक symbol, एक interval और दो product archives की validation है; strategy edge या व्यापक universe की पुष्टि नहीं।
- निर्णय: **HD-03 PASS (scope-limited)**. अगला एकमात्र gate **HD-04**: source-verifiable universe snapshot, Spot/Futures eligibility, volume universe, product metadata, historical funding availability, fee assumptions और survivorship-bias controls.


## 22. HD-04 universe snapshot: पहला वास्तविक प्रयास — 22 अक्टूबर 2026
- `scripts/build_hd04_universe_snapshot.py`, workflow `.github/workflows/hd04-universe-snapshot.yml` और tests `tests_crypto_target/test_hd04_universe.py` जोड़े गए। Scope: Spot USDT trading pairs और USDⓈ-M USDT perpetuals की अलग-अलग 24h quote-volume rankings, exchange filters/metadata, top-10 Futures funding endpoint checks और account-specific fee uncertainty का स्पष्ट रिकॉर्ड।
- Run #39824506960 में GitHub Actions runner को official public Spot endpoint `https://api.binance.com/api/v3/exchangeInfo` से HTTP 451 मिला; कोई valid snapshot नहीं बना। Run #39824521991 भी completeness gate पर fail हुआ।
- Logs: `execution_logs/2026-10-22-hd04-initial-attempt.md`. इसे listing universe खाली होने का प्रमाण न समझें; यह source-access blocker है।
- निर्णय: **HD-04 BLOCKED**. अगला कार्य official alternate API edge या स्वतंत्र रूप से सत्यापित official public source से snapshot पुनः लेना, और पूर्ण timestamped report, hashes, Top-10 lists तथा funding coverage status सत्यापित करना है।
- Drift check: ₹10 करोड़ का लक्ष्य अपरिवर्तित; strategy/backtest पर आगे नहीं बढ़े; कोई profitability claim नहीं।


## 23. HD-04 fallback-source verification — 23 अक्टूबर 2026
- आधिकारिक Binance Spot market-data-only documentation पुष्टि करती है कि `data-api.binance.vision` पर `/api/v3/exchangeInfo` और `/api/v3/ticker/24hr` जैसे सार्वजनिक endpoints बिना API key उपलब्ध हैं: https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md
- Binance Public Data repository पुष्टि करती है कि `data.binance.vision` पर Spot और USDⓈ-M Futures की daily/monthly archives उपलब्ध हैं, और ZIP के साथ `.CHECKSUM` दिया जाता है: https://github.com/binance/binance-public-data/blob/master/README.md
- `scripts/build_hd04_universe_snapshot.py` को आधिकारिक Spot market-data-only host, GCP endpoint और API alternate hosts पर fallback की कोशिश करने के लिए अपडेट किया गया। Commit: `392e3a6e24c1babcabb5a2181fcd3bc398a3b69e`.
- इसी commit पर smoke tests सफल: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39885872012
- HD-04 source capture में Spot access path आगे बढ़ा, लेकिन USDⓈ-M Futures `/fapi/v1/exchangeInfo` response JSON parse नहीं हो सका (खाली/अमान्य response)। Snapshot और artifact नहीं बने; HD-04 अभी भी BLOCKED: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39885872160
- अगला कार्य: Futures metadata के लिए आधिकारिक Futures API host/response troubleshooting और Binance Public Data के उपलब्ध fundingRate/kline archives का bounded coverage probe; फिर स्वतंत्र प्रदाता का cross-check केवल उन metrics के लिए जोड़ना जिनकी परिभाषा/market scope वास्तव में तुलनीय हो। कोई काल्पनिक Top-10 सूची नहीं, कोई रणनीति/backtest शुरू नहीं।


## 24. HD-04 archive-first acquisition — 23 अक्टूबर 2026
- आधिकारिक Binance Public Data README में Spot और USD-M Futures klines के downloadable monthly/daily archives तथा ZIP `.CHECKSUM` सत्यापन documented हैं: https://github.com/binance/binance-public-data/blob/master/README.md. USDⓈ-M Futures funding-rate monthly archive path pattern को अलग से जाँचना आवश्यक है; इसे public REST funding endpoint से अलग dataset मानें।
- नया `scripts/probe_hd04_archive_sources.py` BTCUSDT सितंबर 2026 Spot 5m, USD-M Futures 5m और USD-M funding-rate monthly archives डाउनलोड/जाँचने, SHA-256 sidecar match और CSV row coverage दर्ज करने के लिए जोड़ा। Workflow `.github/workflows/hd04-universe-snapshot.yml` में यह probe API-based universe snapshot से पहले चलेगा।
- Commit path: `scripts/probe_hd04_archive_sources.py`, workflow और keep-list/smoke test updates. अभी इस probe का सफल runtime परिणाम सत्यापित नहीं है; अगला action उसके GitHub Actions run का report/artifact देखना है।
- Universe API snapshot अब भी अलग requirement है: historical archive probe pass होने से वर्तमान Spot/Futures listings या volume ranking अपने-आप प्रमाणित नहीं होंगे। HD-04 तब तक BLOCKED रहेगा जब तक listing/volume snapshot पूरा न हो।
- Drift check: लक्ष्य 1,000 USDT → 1,061,120.54 USDT अपरिवर्तित; कोई strategy/backtest या profitability claim नहीं।


## 25. HD-04 official archive probe का वास्तविक परिणाम — 23 अक्टूबर 2026
- Workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39886385373 (tested commit `018a840f9e18ff6948e99f1cf2af98fd9abde266`). Archive-probe step सफल; 3/3 archives download हुए, तीनों Binance `.CHECKSUM` SHA-256 matches सही।
- Spot BTCUSDT 5m सितंबर 2026: 8,640 CSV rows, SHA-256 `4106fc73698fd1851b1821cd0293adc6304f86f0c2e72244e15c41f63c2bde08`.
- USD-M Futures BTCUSDT 5m सितंबर 2026: 8,641 CSV rows, जिसमें पहली row header है; अर्थात 8,640 data candles. SHA-256 `3a2d163a2bd28ca614fa0840a92ecbcde0d9c4962b278dd619d5bf81a9918e26`.
- USD-M Futures BTCUSDT funding-rate सितंबर 2026: 91 CSV rows, जिसमें पहली row header है; अर्थात 90 data rows. SHA-256 `913cd31b8f924a06717a2fac17f3df6132c24ccded209eb3e4ae7d83e1b247f2`.
- Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39886385373/artifacts/12473175759 (30-day retention).
- उसी workflow का overall result फिर भी FAIL रहा, क्योंकि current USDⓈ-M Futures `/fapi/v1/exchangeInfo` API response JSON नहीं था। इसलिए यह ऐतिहासिक archive/funding access का PASS है, पूरे HD-04 universe का नहीं। HD-04 अभी BLOCKED है।
- Smoke tests archive-probe implementation के compile check सहित PASS: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39886398942 (commit `b8e94318ac7844907ec52e0dbbe3b2c1b34581cb`).


## 26. HD-04 archive probe में row-count assertions मजबूत किए — 23 अक्टूबर 2026
- Script commit: `1197e7592c79b0f4cf8440af5bf8f59a74690bdc`.
- अब probe केवल ZIP checksum और non-empty CSV पर निर्भर नहीं है। यह header की अपेक्षित मौजूदगी/पहचान और data rows की संख्या भी जाँचता है: Spot 5m = 8,640 data rows (header नहीं), USD-M Futures 5m = 8,640 data rows (एक header), fundingRate = 90 data rows (एक header)।
- Smoke CI उसी script commit पर PASS: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39887371687.
- यह अभी code-level/smoke verification है; नया HD-04 archive workflow result अभी प्राप्त नहीं हुआ। पिछला archive result तीन checksum matches दिखाता है, जबकि current USD-M Futures exchangeInfo API failure के कारण पूरा HD-04 BLOCKED है।
- अगला सीमित कदम: updated archive assertions को HD-04 workflow में वास्तविक रूप से चलाना, फिर current Spot/Futures listings और अलग-अलग volume universes के लिए प्रमाणित data source स्थापित करना। जब तक वह gate पास नहीं होता, backtest/strategy conclusions नहीं निकालने हैं।


## 27. Updated HD-04 workflow rerun — 23 अक्टूबर 2026
- Workflow: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39887437784; tested commit `986479a2bea5f5ae645b17cfb5feda3ceebcec07`.
- Archive probe: PASS. तीनों files में checksum match, अपेक्षित header और data-row count पास हुए: Spot candles 8,640; USD-M Futures candles 8,640; funding rows 90।
- Compile और deterministic eligibility tests: PASS।
- Universe snapshot: FAIL। `https://fapi.binance.com/fapi/v1/exchangeInfo` सहित configured official hosts से response JSON parse नहीं हुआ। Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39887437784/artifacts/12473615465.
- निर्णय: HD-04 BLOCKED रहेगा। अगला शोध कार्य CoinGecko के exchange/derivatives pair listings को independent corroboration के रूप में जाँचना है; यह aggregated listing Binance के अपने current tradability status, contract metadata या volume ranking का स्वतः विकल्प नहीं है। इन स्रोतों के अर्थ और coverage अलग रखनी है।
- कोई backtest, strategy edge, profitability, live execution या लक्ष्य तक पहुँचने का समय प्रमाणित नहीं हुआ। Live trading और credentials का gate बंद है।


## 28. Independent exchange-source probe को workflow में जोड़ा — 23 अक्टूबर 2026
- नई script: `scripts/probe_hd04_coingecko_source.py` (commits `7b8e7a116c95d5afa4e5c21d41bca2b6db9d7331` और newline fix `585b2d22d6e6ab6a9e39754265fcfbfd3780fc5c`).
- यह CoinGecko के Binance Spot `/exchanges/binance` और Binance Futures `/derivatives/exchanges/binance_futures` endpoints को जाँचती है; सफलता/विफलता, response SHA-256, उपलब्ध tickers और सीमित sample को JSON artifact में दर्ज करती है।
- Workflow में compile और probe step जोड़े; keep-list में script सुरक्षित की। Workflow commit `2665814b9eb56fc0ffe1462f3e5def377922997f`; keep-list commit `e79e5f9118f73874f580a4ea4734955cd84c0509`.
- CoinGecko data केवल independent corroboration है। यह Binance `exchangeInfo`, complete current symbols, exact tradability/contract metadata या official per-symbol USDT quoteVolume का विकल्प नहीं है। API key source में नहीं रखी; जरूरत होने पर केवल GitHub Actions secret `COINGECKO_DEMO_API_KEY` से दी जा सकती है।
- Workflow verification अभी pending है। HD-04 BLOCKED रहेगा; कोई strategy/backtest निष्कर्ष नहीं।


## 29. CoinGecko API reachability verified; derivatives pair coverage needs another endpoint — 23 अक्टूबर 2026
- Run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39888051398; workflow commit `2665814b9eb56fc0ffe1462f3e5def377922997f`.
- CoinGecko public API बिना configured key के दोनों endpoints पर सफल रहा: `/exchanges/binance` और `/derivatives/exchanges/binance_futures`। Spot exchange endpoint ने 100 tickers दिए; Futures exchange-detail endpoint ने 0 tickers लौटाए, केवल exchange-level volume उपलब्ध था।
- Spot reported volume BTC में है और ticker sample में USDC/USDT सहित अलग-अलग quote pairs आते हैं। इसे Binance per-symbol USDT quoteVolume ranking समझना गलत होगा।
- अगला छोटा सुधार: script commit `385d3dd7437ce9516f9e1a2168bac9e20db8a117` में global `/derivatives` endpoint से सभी returned derivative tickers लेकर Binance Futures label से filter करना जोड़ा है। इसका परिणाम नए workflow run के बाद ही माना जाएगा।
- उसी run में official Binance Futures `exchangeInfo` snapshot फिर विफल हुआ। HD-04 BLOCKED; कोई strategy/backtest या profitability claim नहीं।


## 30. CoinGecko global derivatives list से 823 Binance Futures candidate records — 23 अक्टूबर 2026
- Workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39888143324; tested commit `385d3dd7437ce9516f9e1a2168bac9e20db8a117`.
- CoinGecko probe के 3/3 endpoints सफल हुए। Spot exchange endpoint ने 100 tickers दिए; Binance Futures exchange-detail endpoint ने 0 pair tickers दिए; global `/derivatives` endpoint ने 27,951 records दिए, जिनमें market label में Binance और Futures दोनों आने वाले 823 records मिले।
- 823 को अभी **candidate records** ही माना जाएगा, verified full Binance contract universe नहीं। Aggregator coverage incomplete हो सकती है; contract status और official listing के लिए Binance authority अलग से चाहिए।
- इसी workflow में primary official Binance USD-M Futures `exchangeInfo` snapshot फिर विफल रहा, इसलिए HD-04 BLOCKED है।
- अगला कदम: CoinGecko candidate records को timestamp/hash के साथ अलग slice के रूप में संरक्षित करना, symbol mapping को conservative रखना, historical archive symbol coverage से overlap निकालना और primary exchange-status source को अलग resolve करना। कोई strategy/backtest निष्कर्ष नहीं।


## 31. CoinGecko candidate-symbol reconciliation और tests — 23 अक्टूबर 2026
- Script commit: `fd0e1e75d2d33269eeac4e85796a59ffd1b1ed5f`. अब हर external raw symbol ज्यों का त्यों सुरक्षित रहता है; केवल स्पष्ट alphanumeric symbol और recognized quote suffix (USDT/USDC/BUSD/USD) मिलने पर conservative candidate बनाया जाता है। बाकी unmapped रहते हैं, अनुमान नहीं लगाया जाता।
- Report में unique candidate count, duplicate candidate symbols, unmapped records और verified archive slice में BTCUSDT overlap शामिल किया।
- Unit-test commit: `bae405f87b0148bf5e7bbdf658d6f1d3558dd4ed`, ambiguous/invalid symbols के लिए test जोड़े।
- Workflow run अभी pending है। यह Binance के current contract status का प्रमाण नहीं है; HD-04 BLOCKED रहेगा।


## 32. Candidate mapping tests passed; current-source gate still blocked — 23 अक्टूबर 2026
- HD-04 run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39889218198; smoke run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39889218167. दोनों tested commit `bae405f87b0148bf5e7bbdf658d6f1d3558dd4ed` पर।
- Script output: global derivatives 27,978 records; Binance (Futures) label वाले 824 records; 779 unique conservative symbol candidates; 45 unmapped; normalized duplicate candidates 0; verified archive slice से overlap केवल BTCUSDT।
- Unit tests और smoke CI पास हैं। HD-04 workflow फिर भी primary Binance Futures `exchangeInfo` non-JSON response के कारण FAIL हुआ। इसलिए पूरा gate BLOCKED है।
- अगला सीमित कदम: CoinGecko के स्पष्ट USDT-quoted candidates के छोटे चुने हुए sample पर official historical archive existence/checksum matrix बनाना। सभी 779 candidates पर अंधाधुंध requests नहीं करनी हैं; missing archive को coverage debt दर्ज करना है और candidate को active Binance listing नहीं मानना है।


## 23 अक्टूबर 2026: सीमित candidate archive coverage जाँच

- निर्णय: CoinGecko के Binance-Futures-labelled records से अधिकतम 10 अद्वितीय, conservative USDT symbol candidates चुने जाएँ; चयन source के `volume_24h` के आधार पर descending हो और बराबरी में symbol क्रम deterministic रहे। यह aggregator ranking है, Binance की आधिकारिक listing/volume ranking नहीं।
- नया script: `scripts/probe_hd04_candidate_archive_coverage.py`. यह सितंबर 2026 के 5-minute Spot तथा USDⓈ-M Futures monthly kline ZIP URLs अलग-अलग जाँचता है, उपलब्ध ZIP का SHA-256 निकालता है और official `.CHECKSUM` sidecar से मिलान करता है। रिपोर्ट: `artifacts/hd04/hd04-candidate-archive-coverage.json`.
- HTTP 404 को केवल `NOT_AVAILABLE_OR_NOT_LISTED` दर्ज किया जाता है। इससे यह निष्कर्ष नहीं निकलेगा कि symbol कभी listed नहीं था या वर्तमान में inactive है। Checksum match archive-object integrity बताता है, candle schema/continuity नहीं।
- Unit tests में unique USDT filtering, volume ranking और deterministic tie-break जोड़े; script को keep-list और HD-04 Actions workflow में जोड़ा।
- अगली कार्रवाई: workflow artifact में परिणाम और logs देखना। HD-04 तब तक BLOCKED है जब तक आधिकारिक Binance Futures `exchangeInfo` snapshot सफल व पर्याप्त न हो। कोई strategy backtest, profitability claim या live trade इस probe से अधिकृत नहीं होता।


## 33. Candidate archive probe सफल; आधिकारिक current-universe gate अब भी BLOCKED — 23 अक्टूबर 2026
- HD-04 workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39890523651; tested commit `c14041b7398b40e9406c8857493d1c3e59067c69`.
- Compile, deterministic eligibility tests, official monthly archive probe, CoinGecko corroboration और bounded candidate archive coverage probe सभी सफल हुए। Coverage report artifact `hd04-market-universe-39890523651` में सुरक्षित है: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39890523651/artifacts/12474726467 (SHA-256: `d1898d7fe5530346380dff22497118fc0623a7339a520f0c36b1c131efb00f28`).
- 10 candidates × Spot/Futures = 20 archive checks: 14 ZIP और official `.CHECKSUM` matches; 6 HTTP 404 को `NOT_AVAILABLE_OR_NOT_LISTED` दर्ज किया गया; network/other errors 0। Candidates: BTCUSDT, ETHUSDT, SOXLUSDT, XAUUSDT, SNDKUSDT, ZECUSDT, SKHYNIXUSDT, KORUUSDT, SPCXUSDT, SOLUSDT। ये CoinGecko-derived candidates हैं, आधिकारिक active Binance listing का प्रमाण नहीं।
- पूरा workflow फिर भी FAILURE है, क्योंकि `https://fapi.binance.com/fapi/v1/exchangeInfo` से valid JSON नहीं मिला। विफलता `scripts/build_hd04_universe_snapshot.py` में primary metadata fetch पर हुई। इसे candidate archive probe की विफलता न समझें; primary current-universe source अभी unresolved है।
- अगला कदम: official current-contract metadata source/access को अलग से diagnose करना। Completeness gate ढीला नहीं करना, CoinGecko candidates को official listings नहीं मानना, और HD-04 पास घोषित नहीं करना। Strategy/backtest, profitability claim तथा live trading gate बंद हैं।


## 34. Binance के अलावा Tardis.dev को वैकल्पिक ऐतिहासिक डेटा स्रोत के रूप में चुना — 23 अक्टूबर 2026
- आधिकारिक documentation देखी: https://docs.tardis.dev/downloadable-csv-files ; https://docs.tardis.dev/faq/data ; https://docs.tardis.dev/downloadable-csv-files/api
- Tardis multi-exchange historical data provider है। Documentation में trades, order book, quotes और derivatives tick data जैसे funding rate, mark/index price, open interest तथा liquidations के data types हैं। CSV datasets दैनिक और tick-level हैं; ready-made monthly 5-minute OHLCV मानकर नहीं चलना है। Trade data से candle aggregation करनी पड़ सकती है।
- कुछ महीने की पहली तारीख के historical datasets बिना API key उपलब्ध हैं, लेकिन इससे पूरे इतिहास, हर symbol या free full access की पुष्टि नहीं होती। लागत और retention/coverage अलग से जाँचनी है।
- अगला bounded test: Tardis documentation में alternate exchange के Spot और perpetual Futures की symbol/data-type/date coverage जाँचना; फिर एक समान छोटे time window पर timestamps, OHLCV aggregation, gaps, symbol/contract mapping और funding fields validate करना। Tardis provider evidence है, Binance के official current contract status का विकल्प नहीं। HD-04 BLOCKED रहेगा जब तक primary universe metadata और coverage gate पूरे न हों।


## 35. Binance और Tardis के अलावा 3 zero-cost source candidates — 23 अक्टूबर 2026
- **Bybit official public market API**: Spot तथा linear/inverse contract candles के लिए `/v5/market/kline`; public market endpoints, API key की आवश्यकता नहीं। अधिकतम 1,000 bars प्रति request और response reverse chronological है। Instrument metadata तथा funding history के अलग endpoints हैं। Docs: https://bybit-exchange.github.io/docs/v5/market/kline ; https://bybit-exchange.github.io/docs/v5/market/instruments-info ; https://bybit-exchange.github.io/docs/v5/market/funding/history . प्राथमिक probe यही होगा।
- **OKX official historical downloads + public API**: official historical page पर trade history (Sep 2021 से), candles (Jul 2023 से), funding rates (Mar 2022 से) और L2 order book (Mar 2023 से) सूचीबद्ध हैं। Public REST docs में historical candles, instruments और funding endpoints भी हैं। Docs: https://www.okx.com/historical-data ; https://app.okx.com/docs-v5/en/ . Region availability, instrument naming और download limits अलग से verify होंगे।
- **CryptoDataDownload free CSV**: documented no-login Spot OHLCV CSVs daily/hourly/1-minute granularity में कई exchanges के लिए हैं। इसे केवल independent Spot cross-check मानेंगे, पूर्ण Futures/funding source नहीं। https://www.cryptodatadownload.com/ .
- Zero-cost का अर्थ public endpoints/downloads बिना paid plan/API key जहाँ समर्थित हो; unlimited requests, complete history या हर symbol की guarantee नहीं।
- अगला चरण: Bybit और OKX पर एक ही UTC window के BTCUSDT Spot तथा perpetual candles, instrument metadata और funding history का छोटा read-only probe। HTTP/JSON, symbol mapping, timestamp grid/continuity, OHLCV numeric rules और funding schema validate होंगे। CryptoDataDownload केवल exact comparable Spot file मिलने पर cross-check में शामिल होगा। कोई credentials या trading endpoints नहीं।


## 36. Bybit और OKX के वैकल्पिक public API probe को repository में जोड़ा — 23 अक्टूबर 2026

- कामचलाऊ बदलाव अलग branch `research/hd04-alternate-source-probe` पर किया गया है; अभी `main` में merge नहीं किया गया।
- नई script `scripts/probe_hd04_alternate_sources.py` निश्चित UTC window 2026-09-01 00:00–01:00 पर Bybit V5 और OKX V5 के public Spot/perpetual candle, instrument metadata और funding-history endpoints जाँचती है। Credentials और trading endpoints उपयोग नहीं होते।
- रिपोर्ट path: `artifacts/hd04/hd04-alternate-sources.json`; HTTP/API errors को report में दर्ज किया जाता है, ताकि स्रोत की अनुपलब्धता code exception से छिपे नहीं।
- HD-04 workflow में compile तथा probe step जोड़ा गया और script को `CURRENT_PROJECT_KEEP_PATHS.txt` में सुरक्षित किया गया।
- अभी Actions execution नहीं हुआ है। इसलिए Bybit/OKX availability, schema या historical candle correctness पर कोई PASS claim नहीं है। Binance authoritative current-universe gate BLOCKED है; strategy/backtest और live-trading gate बंद हैं।
- अगला कदम: branch diff review और CI execution। परिणाम artifact देखने के बाद ही तय होगा कि probe validation को और मजबूत करना है या CryptoDataDownload का Spot-only cross-check जोड़ना है।


## 37. वैकल्पिक स्रोतों का पहला live probe और OKX time-boundary सुधार — 23 अक्टूबर 2026

- पहला वास्तविक run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39901520198 ; artifact id `12479136008`। Bybit के पाँचों public endpoint checks पर इस runner से `HTTP 403 Forbidden` मिला। इसे Bybit पर डेटा न होने का प्रमाण नहीं मानना है; यह अभी access/reachability failure है।
- OKX Spot तथा Swap instrument metadata सफल रहे। दोनों candle endpoints में 11 candles आईं, क्योंकि query की lower boundary पर ठीक 00:00 वाली candle शामिल नहीं हुई। Funding history query भी खाली लौटी।
- OKX history query की lower boundary को `before=START-1ms` करने का सुधार commit `e8998d20d761bf8fc6c4a1fbe088a9744afebdff` में किया।
- सुधार के बाद run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39902158479 ; artifact id `12479226388`। कुल 10 checks में 5 PASS, 5 FAIL। OKX Spot और Swap दोनों में निश्चित एक घंटे के भीतर 12 unique, continuous 5-minute candles मिलीं। दोनों instrument metadata checks PASS हुए और Swap funding endpoint से एक row मिली। Bybit के पाँच checks पर HTTP 403 अब भी है।
- यह केवल एक सीमित OKX BTC sample का प्रमाण है, पूरे exchange universe या पूरे historical coverage का नहीं। Bybit access issue अलग से unresolved है। Binance का authoritative HD-04 universe gate BLOCKED रहेगा। PR #13 अभी merge नहीं करना; strategy/backtest तथा live trading शुरू नहीं करना।
- अगला कदम: OKX candle/funding fields की schema-level checks जोड़ना और Bybit 403 के लिए आधिकारिक alternate host/region/network behavior का सीमित diagnosis करना। कोई credentials या trading endpoint उपयोग नहीं होगा।


## 38. Critical-path सुधार: broad-universe HD-04 को BTCUSDT research से अलग किया — 23 अक्टूबर 2026

तुम्हारी चिंता सही थी: BTCUSDT-केंद्रित लक्ष्य में सभी Binance symbols की universe discovery पर अटकना scope drift बन सकता था। इसे स्पष्ट रूप से अलग किया गया है।

- Binance `exchangeInfo` access failure वास्तविक है; इसे PASS नहीं कहेंगे। Full universe, top-N ranking और दूसरे symbols की current eligibility अभी सिद्ध नहीं हैं।
- लेकिन इस failure को BTCUSDT historical research रोकने नहीं देंगे। `HD-04-BROAD-UNIVERSE` को DEFERRED/BLOCKED रखा जाएगा, और critical path को fixed BTCUSDT पर वापस लाया जाएगा।
- नया अगला काम: कई महीनों/वर्षों का Binance official Spot तथा USD-M Futures monthly archive + checksum + funding history इकट्ठा करना; हर file की provenance, checksum, schema, timestamp grid, missing/duplicate bars, OHLCV integrity और coverage manifest सत्यापित करना।
- Sep-2026 का 8,640-candle slice केवल एक महीने का है; robust strategy/backtest के लिए यह पर्याप्त नहीं। इसलिए अभी strategy ranking शुरू नहीं होगी, लेकिन data acquisition आगे बढ़ेगा।
- OKX sample को केवल cross-check evidence मानेंगे, Binance universe का विकल्प नहीं। Bybit HTTP 403 को access failure माना जाएगा, data absence नहीं।
- Live trading/keys/funds movement बंद हैं; profitability और target तक समय अज्ञात हैं। यह scope correction project को रोकने के बजाय measurable data coverage की ओर ले जाती है।


## 2026-10-23: GitHub execution-log rule reinforced

**निर्णय:** हर code execution, workflow step, data acquisition/validation और database upload के लिए GitHub में traceable log अनिवार्य है। कोई result केवल अनुमान या बिना log के घोषित नहीं किया जाएगा।

**लॉग में अनिवार्य फ़ील्ड:** UTC start/end, repository, commit SHA, Actions run ID/attempt, exact inputs, step-wise status, exit code, archive/file counts, bytes, SHA-256/checksum result, PASS/FAIL/UNAVAILABLE/SKIPPED का कारण, manifest/output paths और cloud upload/catalog result. Secrets या API keys कभी log नहीं होंगे। हर run के बाद पहले log और machine-readable manifest पढ़कर ही रिपोर्ट दी जाएगी।

**इस बार किया गया काम:** [commit bbabd2c1e1e1302c389d8e75ee95205341724b7c](https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/bbabd2c1e1e1302c389d8e75ee95205341724b7c) में .github/workflows/btcusdt-full-history-collection.yml को बदला गया है। यह collection console output को execution.log में tee करता है, UTC/run/commit/input metadata जोड़ता है, collector/uploader exit codes रिकॉर्ड करता है, manifest से counts और bytes निकालता है, और GitHub Step Summary बनाता है। Artifact में detailed execution.log और btc-usdt-archive-collection-manifest.json सहित outputs 30 दिनों तक रहेंगे।

**स्थिति की ईमानदार सीमा:** यह workflow change GitHub branch पर commit है, पर अभी इसका वास्तविक execution नहीं हुआ है। इसलिए runtime logging, Supabase upload, bucket या database catalog को PASS नहीं माना जाएगा। अगला सुरक्षित कदम केवल एक महीने का canary है; पहले GitHub run logs और artifact जाँचेंगे। Supabase secrets/bucket/table की उपलब्धता सिद्ध न होने पर cloud upload को साफ़ तौर पर SKIPPED/FAIL लिखना है, successful backup नहीं कहना है।

**Binance connector का उपयोग:** live/near-live snapshots, klines, order book, funding और independent cross-checks में सहायक; multi-year historical research के लिए official Binance archive ZIP + official .CHECKSUM sidecar प्राथमिक evidence रहेगा। Connector जुड़ना अपने-आप historical coverage प्रमाणित नहीं करता।


## GitHub execution logging change: CI evidence (23 October 2026)

- Workflow logging change: [commit bbabd2c1e1e1302c389d8e75ee95205341724b7c](https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/bbabd2c1e1e1302c389d8e75ee95205341724b7c).
- CI run [39920640004](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39920640004) completed SUCCESS. I fetched and read job log `120304743836`: Python 3.12.15; all listed Python scripts compiled; 34 deterministic unit tests passed in 0.576 seconds; cleanup was dry-run only and changed no files.
- Detailed audit note: `execution_logs/2026-10-23-github-execution-logging-change.md`.
- Scope boundary: this smoke test does not execute the full-history workflow, fetch Binance archives, or validate Supabase. Those remain UNVERIFIED, not PASS. No data collection or database write is claimed.


## One-month archive canary workflow and allow-list CI (23 October 2026)

- Added `.github/workflows/btcusdt-archive-canary.yml`, a bounded single-month (2026-09) read-only archive canary. It requests Spot 1m, USDⓈ-M Futures 1m and funding archives, records `execution.log` plus a JSON manifest, and does not write to Supabase.
- First CI run [39920771237](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39920771237) failed at the protected-path check because the new workflow was not yet in `CURRENT_PROJECT_KEEP_PATHS.txt`. The fetched log confirmed dry-run only and no files changed.
- Corrected the keep-list in commit [159f593a6052e31b06042e7217437e9637a03752](https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/159f593a6052e31b06042e7217437e9637a03752). Rerun [39920787299](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39920787299) passed: 59 tracked files, 59 protected, zero deletion candidates, 34 tests passed in 0.360 seconds.
- The run records and inspected logs are preserved in `execution_logs/2026-10-23-archive-canary-workflow-allowlist-ci.md`.
- Important: the commit-associated successful run was smoke CI, not the archive canary. Actual archive acquisition remains UNVERIFIED. Workflow dispatch availability is not confirmed because this workflow is only on the feature branch; do not merge PR #13 or write to Supabase to bypass the gate.


## BTCUSDT one-month archive canary: first end-to-end source validation (23 October 2026)

- Successful GitHub Actions run: [39921734599](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921734599), job archive-canary completed SUCCESS on commit e99f9a5ca905fc146a3a14e31f47c553461b068c.
- UTC runtime observed in job log: 08:01:34–08:01:40. Python 3.12.15. Requested only 2026-09.
- Actual outcome: 3 archives PASS, 0 UNAVAILABLE, 0 FAIL; total archive bytes 3,852,025. Spot 1m: 2,054,117 bytes, SHA-256 7a021fb5981cfdb1a56457d68fa81360ab27350c981ddfe63112b2322df44b56. USDⓈ-M Futures 1m: 1,796,984 bytes, SHA-256 e1a821b5bf6b48d57da01c3e390b8a467a698155def5c18c2c63c0eb044a3247. UM funding: 924 bytes, SHA-256 913cd31b8f924a06717a2fac17f3df6132c24ccded209eb3e4ae7d83e1b247f2.
- The first canary run [39921614983](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921614983) failed because the Futures CSV contains an open_time header. The log exposed the exact issue. Collector fix at e99f9a5ca905fc146a3a14e31f47c553461b068c now handles a valid 12-column header; a regression test was added in 5a6441b7c45e287bba891f0f4172fc76023f775f. Smoke CI [39921757171](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921757171) passed.
- Artifact: [canary logs, manifest and raw archives](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921734599/artifacts/12487337672), artifact ID 12487337672, 3,855,719 bytes, retention 30 days.
- Detailed execution record: execution_logs/2026-10-23-btcusdt-one-month-archive-canary.md.
- Scope boundary: this is a real PASS for the three requested September 2026 archives only. Supabase writes were explicitly NOT ATTEMPTED. Long-history coverage, permanent storage and trading strategy performance remain unverified.


## Historical coverage probe: September 2019 (23 October 2026)

- GitHub Actions [run 39921927263](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921927263) completed; collector exit code 0; Python 3.12.15.
- Summary for requested month 2019-09: PASS=1, UNAVAILABLE=2, FAIL=0. Spot 1m archive PASS, 2,140,033 bytes, SHA-256 `6bed8bcf250caedf243cd890cdffd93b6266e7f3007a8bb7e6d13b95a15645f1`. USDⓈ-M Futures 1m and UM funding exact monthly archive URLs returned HTTP 404 and were recorded UNAVAILABLE.
- Artifact [12486414849](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39921927263/artifacts/12486414849), 2,142,723 bytes, 30-day retention. It contains the execution log and machine-readable manifest.
- Detailed record: `execution_logs/2026-10-23-btcusdt-2019-history-canary.md`.
- Interpretation: 404 is archive-path availability evidence only, not proof that the contract did not exist. Spot and Futures coverage start dates must be measured independently. Next bounded probe is 2020-01 for UM Futures and funding availability. No Supabase writes were attempted.


## Historical coverage probe: January 2020 (23 October 2026)

- GitHub Actions [run 39922039878](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922039878) completed successfully. Requested 2020-01 only; collector exit code 0; PASS=3, UNAVAILABLE=0, FAIL=0.
- Spot 1m: PASS, 2,224,194 bytes, SHA-256 `02df6da44ed8145fbb9ed819858185d9e2f15eb025c5bec8a4ea2d8738cd0d19`. UM Futures 1m: PASS, 1,829,116 bytes, SHA-256 `b4e13ea185ba96c413ac9167cfbb6e238eb5eae119a7a77f41f4c61c5e099d03`. UM funding: PASS, 825 bytes, SHA-256 `7f81b2f3694d13779e7e896b69d60cd61e9444d7b9f9e90df761935e1c1b76e2`.
- Artifact [12486769727](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922039878/artifacts/12486769727), 4,057,887 bytes, retained for 30 days. Detailed record: `execution_logs/2026-10-23-btcusdt-2020-history-canary.md`.
- Compared with the September 2019 probe, this shows Spot archive availability at both tested points; UM Futures and funding returned HTTP 404 in 2019-09 but passed in 2020-01. This brackets availability between the tested months only, not exact start date. A month-by-month coverage manifest is required before stating a complete history range.
- No Supabase write attempted. Temporary GitHub artifact only; durable storage remains unverified.


## Full official archive URL coverage inventory (23 October 2026)

- GitHub Actions [run 39922532383](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922532383) completed SUCCESS for 2017-08 through 2026-09, 110 months. It made 330 monthly archive checks and checked each archive plus its .CHECKSUM sidecar via HTTP HEAD. Summary: AVAILABLE=272, UNAVAILABLE=58, FAIL=0. Archive bodies were not downloaded by this inventory.
- Spot 1m: 110/110 monthly URLs available, 2017-08 through 2026-09; reported Content-Length sum 234,954,793 bytes.
- UM Futures 1m: 81/110 URLs available, 2020-01 through 2026-09; earlier 29 months returned 404; reported Content-Length sum 151,823,703 bytes.
- UM funding: 81/110 URLs available, 2020-01 through 2026-09; earlier 29 months returned 404; reported Content-Length sum 71,993 bytes.
- Combined reported ZIP size estimate: 386,850,489 bytes, about 386.9 MB decimal / 0.36 GiB. This excludes normalized outputs and does not establish storage/egress pricing.
- Artifact [12488291064](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922532383/artifacts/12488291064) contains the URL-level JSON inventory and execution.log. Smoke CI [39922538810](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922538810) passed: 40 tests, 68/68 files protected, zero deletion candidates.
- Detailed record: `execution_logs/2026-10-23-btcusdt-archive-coverage-inventory.md`.
- Limitation: this is URL reachability via HEAD, not full archive checksum/content validation. Actual monthly content validation remains limited to the canary months already recorded. No Supabase write attempted.
- Next gate: confirm intended Supabase project before bulk storage. Do not upload to the previously listed project named `supabase ai content creation claude antigravity` without confirmation. After confirming project/bucket/schema/secrets, do a one-month upload canary and verify object bytes/hash plus catalog row.

## BTCUSDT candidate baselines: पहला वास्तविक बहु-महीना run (23 अक्टूबर 2026)

- Draft PR #16: https://github.com/manish91082-coder/aists-btcusdt-research-runner/pull/16
- Candidate run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947542681
- Smoke CI: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947549808
- Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39947542681/artifacts/12498179453

**Data gate:** जुलाई-सितंबर 2026 के official monthly archives validate हुए; normalized Spot/Futures aligned BTCUSDT 5-minute dataset में 26,496 candles और 276 funding events हैं। Candidate verifier PASS; दोनों equity curves में 26,496 rows। यह funding count सिर्फ normalized dataset में मौजूद है, Spot candidates funding cash flow इस्तेमाल नहीं करते।

**Illustrative cost assumptions:** 1,000 USDT initial equity; fee 10 bps/fill; full spread 2 bps; slippage 5 bps/fill। Long/flat Spot; completed candle signal अगले candle open पर execute; अंतिम position last close पर cost सहित liquidate।

| Candidate | Net return | Max marked-to-market drawdown | Fills |
|---|---:|---:|---:|
| SMA trend 12/48 | -68.0308% | -68.5169% | 742 |
| Mean reversion, trailing z-score 48, entry <= -1.5, exit >= 0 | -58.9397% | -59.4759% | 652 |

**व्याख्या:** दोनों शुरुआती candidates ने इस sample और cost assumptions पर बड़ी हानि दिखाई। यह negative initial evidence है; profitable edge नहीं। यह sample untouched holdout नहीं था, इसलिए out-of-sample performance का दावा नहीं किया जा सकता। Parameter tuning को इन परिणामों को बेहतर दिखाने के लिए hindsight में नहीं करना है।

**Implementation correction:** CI में पहले candidate test ने runner के return shape को गलत assert किया था; test को actual return structure के अनुसार ठीक किया गया। Final equity curve की आखिरी row को costed liquidation के बाद report की realized final equity से match कराने का fix जोड़ा गया। Final smoke CI PASS: run 39947549808.

**सीमाएँ:** Spot-only; Futures funding, leverage, liquidation, partial fills, exchange filters और fixed assumptions से आगे dynamic market impact शामिल नहीं। कोई AI decision layer, live order या funds movement नहीं। Target तक profitability/time अभी भी unknown है।

**अगला gate:** candidate rules/cost assumptions freeze करें; आगे tuning से पहले chronological train/validation/holdout windows लिखित रूप से तय करें। फिर cost sensitivity, turnover, benchmark comparison और walk-forward evaluation चलाएँ। हर parameter change का अलग experiment log रखें।
