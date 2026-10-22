# 1,000 USDT → ₹10 करोड़-समतुल्य USDT: मास्टर शोध लॉग
**Version:** 1.0  
**Updated:** 2026-10-22  
**Repository:** https://github.com/manish91082-coder/aists-btcusdt-research-runner  
**Scope:** शोध, market data, backtesting, reproducibility. Tax/TDS अभी स्थगित।

## 1. लक्ष्य का निश्चित अर्थ
- Starting equity: **1,000 USDT**
- Target: **1,061,120.54 USDT** (22 Oct 2026 reference snapshot ₹94.24/USDT पर ₹10 करोड़ का अनुमानित समतुल्य; यह conversion rate स्थायी नहीं है)।
- Required multiple: **1,061.12×**.
- “Hourly compounding” का अर्थ: जब भी net profit वास्तव में realize/settle हो, उसे equity में जोड़कर आगे की sizing में शामिल करना। इसका अर्थ 1-hour chart या हर घंटे trade करना नहीं है।
- Trade timeframe खुला है: 15m/1h/4h/daily/multi-day, event-driven, carry/basis, market-neutral approaches, provided they can be tested with valid data.
- कोई अतिरिक्त deposit नहीं माना गया। Live orders और credentials अधिकृत नहीं हैं।

## 2. गणितीय hurdle, forecast नहीं
स्थिर geometric growth मानने पर:
| काल्पनिक अवधि | आवश्यक निरंतर net daily growth |
|---:|---:|
| 30 दिन | 26.1417% |
| 90 दिन | 8.0487% |
| 180 दिन | 3.9465% |
| 365 दिन | 1.9271% |
| 730 दिन | 0.9590% |
| 1,095 दिन | 0.6383% |

ये केवल लक्ष्य की गणितीय आवश्यकताएँ हैं। ये returns प्राप्त किए जा सकते हैं, ऐसा कोई दावा नहीं है। वास्तविक P&L असमान होगा और drawdowns समय बढ़ा सकते हैं या पूँजी समाप्त कर सकते हैं।

## 3. रणनीति शोध के खुले ट्रैक
1. Multi-timeframe trend/momentum और breakout.
2. Regime-filtered mean reversion.
3. Volatility compression/expansion और event-driven setups.
4. Cost-aware trade/no-trade filters.
5. Spot-perpetual funding/basis/carry, केवल verified funding, hedge और execution assumptions के साथ.
6. Cross-venue price differences, केवल simultaneous executable bid/ask, fees, latency और inventory constraints के साथ.
7. Machine learning केवल तब जब simple baselines के ऊपर walk-forward out-of-sample सुधार दिखे.

## 4. अनिवार्य परीक्षण नियम
- केवल वास्तविक, स्रोत-सत्यापित market data; कोई synthetic price/fill नहीं।
- Signal में केवल decision time पर उपलब्ध जानकारी; close-based signal अगले executable event पर लागू हो।
- Fees, spread, slippage, funding और partial fills जहाँ लागू हों, शामिल करें।
- Chronological train/validation/test और walk-forward testing; repeated experiments/selection bias दर्ज करें।
- Report: net return, benchmark, maximum drawdown, turnover, exposure, tail losses, losing streak, cost sensitivity और ruin-risk simulation.
- Backtest success live readiness नहीं है; पहले paper/forward validation।
- कोई strategy profitable घोषित नहीं होगी जब तक reproducible out-of-sample evidence उपलब्ध न हो।

## 5. प्रारंभिक स्रोत-आधारित चेतावनी
- Binance public historical data/checksum docs: https://github.com/binance/binance-public-data
- Binance archive host: https://data.binance.vision/
- Crypto strategy research must model execution costs; historical predictive accuracy alone does not prove net profitability. A 2026 preprint on hourly BTC/USDT reports naive direction signals failing after assumed transaction costs and improvements only for selected cost-aware configurations; treat it as preliminary evidence, not a universal edge: https://arxiv.org/abs/2606.00060
- A 2026 Frontiers study similarly emphasizes that transaction costs materially reduce short-horizon strategy profitability: https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1888767/full

## 6. Current truth status
- Target arithmetic: calculated.
- Data pipeline for this specific target project: not yet validated.
- Strategy edge: **NOT ESTABLISHED**.
- Target-hit time: **UNKNOWN** until return distributions are supported by valid out-of-sample evidence.
- Live trading: **NOT AUTHORIZED**.
- Tax/TDS: deferred.

## 7. Next steps
1. Establish a clean, reproducible research harness with unit tests.
2. Confirm code execution via GitHub Actions and save the run/result log as a new file.
3. Fetch real official market data and record URL, checksum, timestamps, gaps and schema.
4. Run simple baselines across multiple holding horizons with realistic costs.
5. Advance only when the evidence gates pass.

## Change log
- **v1.0 — 2026-10-22:** Added explicit USDT-denominated target, clarified realized-profit compounding versus chart timeframe, and froze evidence-first research rules.
