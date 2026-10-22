# 1,000 USDT → ₹10 करोड़-समतुल्य USDT: मास्टर शोध लॉग
**Version:** 1.4  
**Updated:** 2026-10-22 (v1.4, strict current-thread-only cleanup verified)  
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


## 8. Repository execution checkpoint — 2026-10-22
- Added deterministic helper module `crypto_target/research_math.py`: target multiple, required geometric period return, realized-return compounding path and maximum drawdown.
- Added five unit tests in `tests_crypto_target/test_research_math.py` and GitHub Actions workflow `.github/workflows/crypto-target-smoke.yml`.
- Files were read back from GitHub after writes. The crypto-target smoke workflow succeeded: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39793473617. This validates helper/unit tests only, not market-data quality or strategy returns.
- These are math/helper unit tests only, not market-data validation or strategy backtests.
- At this checkpoint the repository still contained the older Binance archive audit pipeline and governance files. A later explicit tracked-tree review and allowlist-based cleanup removed 30 legacy tracked paths; details and post-cleanup verification are in section 10. Git history/other branches remain untouched.
- Next: verify the Actions run result; then add a real-data acquisition + checksum manifest and test strategy baselines with multi-timeframe execution and costs.


## 9. Cleanup script added — 2026-10-22
- Guarded cleanup script: [scripts/cleanup_current_project.py](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/main/scripts/cleanup_current_project.py)
- Commit: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/1bd521dfa8bb2739b78846c16985e103908d51e9
- Default is preview-only; explicit `--apply --confirm-repository manish91082-coder/aists-btcusdt-research-runner` is required to stage deletions.
- Script checks the repository remote, prints tracked paths to keep/delete, stages deletions only, and writes a separate cleanup log. It does not commit/push or erase history/branches.
- At the moment this script-addition checkpoint, cleanup had not yet run. The final cleanup execution was completed later and is documented in section 10.


## 10. Final legacy cleanup execution — 2026-10-22
- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39806484233 — conclusion verified as `success`.
- Cleanup commit: https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/0042c045702efa91a2a50d2672c6079c67edbb62.
- Removed 30 legacy tracked paths after a preview enumerated 43 tracked files, 13 protected active-project paths, and 30 deletion candidates. The exact candidate list and timestamp are retained in `execution_logs/crypto-target/cleanup-20261022T153658Z.md`.
- A post-cleanup recursive GitHub tree confirmed the target research dossier, project status, allowlist, Python math helpers, tests, cleanup script, research workflows and execution logs remained present.
- The first automated push was rejected because that attempt also modified the active workflow YAML. The workflow was corrected, then the explicit one-time trigger was rerun without changing the active YAML in the cleanup commit. The retry committed and pushed successfully.
- The root-level generated `cleanup-apply.txt` transcript was removed in follow-up commit https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/f06eb8bb296d3e4e934bb9e40b395fac93bf352a; the Actions artifact remains accessible from the run.
- Detailed outcome: `execution_logs/2026-10-22-cleanup-final-verification.md`.
- Scope guard: only tracked paths outside the explicit allowlist were removed. Git history and other branches were not erased. This was repo housekeeping, not a market-data/backtest run.
- Current research decision unchanged: strategy edge NOT ESTABLISHED; target-hit time UNKNOWN; live trading NOT AUTHORIZED; tax/TDS deferred.


## 11. Strict current-thread-only repository cleanup — 2026-10-22
- User clarified the repository should contain only files created for this current crypto-target thread today. Pre-existing repository files should not be retained merely because they were edited.
- Removed pre-existing `README.md`; removed it from `KEEP_EXACT` in `scripts/cleanup_current_project.py` and from `CURRENT_PROJECT_KEEP_PATHS.txt`.
- Latest branch-head recursive tree was verified from GitHub API and contained exactly 14 files, all created during this thread's crypto-target research/cleanup work. No expected files were missing and no unexpected files remained.
- Verification log: `execution_logs/2026-10-22-current-thread-only-cleanup.md`.
- Cleanup commits:
  - https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/c4057b62968216e239d9cc160b458d2ab5b757c2
  - https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/582befc3e429a51aa70b67818197f50da0423703
  - https://github.com/manish91082-coder/aists-btcusdt-research-runner/commit/1a673787c62b41305a92f3c3df5be89b552902af
- Git history and other branches have not been erased.
- Research status is unchanged: strategy edge NOT ESTABLISHED; target-hit time UNKNOWN; live trading NOT AUTHORIZED; tax/TDS deferred. This cleanup was not a market-data/backtest run.
