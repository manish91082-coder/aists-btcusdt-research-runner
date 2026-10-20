# Project Status

Last updated: 2026-10-21
Status: RESEARCH-FIRST BLUEPRINT BASELINED; RESEARCH INCOMPLETE

## Current repository state
- Repository: manish91082-coder/aists-btcusdt-research-runner (rename deferred by user).
- Working/default branch: main.
- Pre-change main head verified before this blueprint update: db6fb812d911ded08f75923a57f22ea39f0611c0.
- Clean-slate commit: f52bac573c9509c71143158a7f609bd55a6a76bb.
- Previous snapshot branch: backup/pre-cleanup-2026-10-21-main-f2fcc6f, originally at f2fcc6f2e74dcd08e59cdcb811cd680d35fb1733.
- This checkpoint adds the blueprint, research workstreams, evidence source register, decision log and quality-audit checklist, and synchronises governance and continuity records.

## User requirements captured
Binance; Spot + Futures; long/short exposure; BNB fees wherever supported; AI-dynamic universe/strategy/indicator/entry/exit/stop/target/trailing choices; rolling high-volume top-ten universe; 5m/15m/1h/4h/8h/1d/1w/1M; longest verifiable historical data with ten-year target where possible; stated 10,000 USDT initial capital; zero-cost-first; evidence-based research before coding; no fake data, unsupported assertions or drift; GitHub is the project memory/continuity/log source.

## Work done in this update
- Drafted PROJECT_BLUEPRINT.md with system scope, ten proposed AI roles, deterministic Safety Kernel, multi-timeframe cadence, research methods, data controls, BNB/fee accounting, risk mathematics, dynamic exits and staged release gates.
- Added RESEARCH_REGISTER.md, EVIDENCE_REGISTER.md, DECISION_LOG.md and QUALITY_AUDIT.md.
- Recorded initial official-source findings: archive/checksum documentation, interval naming, BNB discount differences, Futures funding/commission categories, Spot Testnet reset limits, July 2017 venue launch constraint and India-specific product/tax verification gates.
- Updated README, status, memory, continuity, rules/locks, session log and changelog.

## Not done / not to imply completion
- No trading engine, strategy or model code written.
- No selected symbol's data has been downloaded or checksum-verified.
- No top-ten list chosen.
- No feature/strategy candidate empirically validated; no model trained.
- No backtest, walk-forward report, paper-trading report or exchange order test has run.
- No credentials created, funds moved, account settings changed, real order submitted or deployment enabled.
- User/account-specific Futures eligibility remains unresolved.
- No free always-on runtime has been proven to meet uptime and safety requirements.

## Next action
Work R02 and R03 first: current official Binance product/account/jurisdiction eligibility and applicable requirements; then exact per-symbol historic coverage, checksums, timestamp units and gap inventory. Do not start trading implementation until research and coverage gates pass.

## Verification rule
Use live main ref as authority. After the current write, re-fetch main, root listing and changed file contents. If a write/readback fails, record the failure rather than calling the update verified.

## 2026-10-21 strategy-focused checkpoint
- User reprioritised immediate work: defer tax/jurisdiction research for now and focus on strategies and Binance data needed to test them. Those topics remain later execution gates; no bypass is planned.
- Added STRATEGY_RESEARCH.md with 12 falsifiable strategy hypotheses, research order, minimum Binance data inventory, multi-timeframe causality rules, BNB commission accounting and test acceptance criteria.
- Official docs reviewed: Spot exchange information/current symbol rules and rate limits, Spot filters, USDⓈ-M Futures kline/market-data reference, and Binance public archives/checksums/timestamp notes.
- No strategy has been backtested, ranked by results, or approved. No data was downloaded or checksum-verified. Next task: data manifest and representative archive audit, then pre-register S-01 to S-04 experiments.
