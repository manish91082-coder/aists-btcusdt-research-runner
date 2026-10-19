# CP-0170: Uploaded AISTS ZIP Deep Audit and Data-Retention Decision

**Audit date:** 2026-10-19  
**Input archive:** `AISTS-20261019T072605Z-1-001.zip`  
**Audit scope:** Read-only analysis of the user-provided ZIP snapshot plus read-only inspection of the canonical GitHub repository/PR state. No Colab, no exchange API, no trading, no source-data rewrite, and no backtest was run in this audit.

## 1. Executive decision

The uploaded ZIP is structurally intact and its source archives/candidate files are internally reproducible. It is **not** a complete snapshot of the current project implementation or current GitHub evidence: it contains historical data and reports through CP-0098, no Python/notebook source, and no CP-0100+ evidence. The most important unresolved issue is not byte corruption. It is **source adjudication**: CP-0026 promoted a checksum-valid daily-reference row that is a zero-trade, flat-price placeholder with a nonstandard 4h close-time token.

**Decision:** Keep the uploaded ZIP as a source snapshot; do not push the 200 MB archive into Git. Commit this compact audit record and its hashes to the existing research PR branch. Preserve the original ZIP in user-controlled Drive if durable retention is wanted. Do not build a new candidate or backtest until the frozen source gate and strategy approval are resolved.

## 2. Outer ZIP integrity and scope

- File size: approximately 191 MiB (199.7 MB decimal).
- SHA-256: `e39f08a53377b5568e05e2c97b3757e052f9103d4c42ae0865b58fe3c2bb1778`
- ZIP entries: 1,394; duplicate member names: 0; outer ZIP CRC check: PASS.
- Expanded member bytes: approximately 201,975,328.
- Member types: 1,026 nested `.zip`, 246 `.checksum`, 61 `.json`, 49 `.csv`, 11 `.gz`, 1 extensionless.
- Main contents: 1,338 market-data files, 37 source-reconciliation files, 19 diagnostics files.
- Highest checkpoint represented in ZIP paths: CP-0098. The ZIP includes older checkpoints CP-0021 through CP-0031, CP-0062/0065 and CP-0093 through CP-0098.
- No `.py` or `.ipynb` source files; no CP-0100+ evidence; no futures-data path found.
- Therefore, the ZIP is a substantial data/evidence snapshot, but **not** the full current code/repository state.

## 3. Raw archive integrity

- Download manifest: 770 records, 765 `DOWNLOADED_VALID` and 5 `NOT_AVAILABLE_404`.
- All 765 downloaded monthly archive SHA-256 values matched their recorded official checksum sidecars; ZIP CRC passed.
- The five 404s are all native `1mo` monthly archives. This is an availability observation, not evidence of a bad archive.
- Nested CRC validation passed for all 1,005 monthly + daily raw ZIPs examined.
- Daily reference manifest: 240 interval/date records across 5m, 15m, 30m, 1h, 4h and 1d; all have checksum/CRC evidence in the snapshot.
- Candidate row lineage: 1,539,950 rows across 5m/15m/30m/1h/4h/1d had zero source-hash mismatches when each row's recorded source archive hash was checked against the raw ZIP SHA-256.
- Seven candidate hashes exactly match the CP-0026 candidate manifest.

**Interpretation boundary:** checksum and source-hash matches prove byte integrity and internal lineage, not that a daily or monthly version is the canonical historical market bar.

## 4. Candidate inventory

| Interval | Candidate rows | Candidate SHA-256 |
|---|---:|---|
| 5m | 957,861 | `d142c0e07500e1c3c96db5758b3d8430bf4d8f6c40739c5a7f34f8950d7fc588` |
| 15m | 319,293 | `c4ddcf3ade3fe2f66f91d965df4e5025ba1fff6b5f2a76c7126e83e0f659880f` |
| 30m | 159,653 | `27cdac02bbd112cd31fe0789e66b35ee32b43343a9e2230a4e141dc9677786c9` |
| 1h | 79,836 | `a70bd58711ba89278a429dbc7c412fe9b71a900a47aaa22fe32b26ee5caac1c8` |
| 4h | 19,975 | `989a4c2023a28b991455b9bb4149dd0a0a56e6435b34f805f56de5e888d907e1` |
| 1d | 3,332 | `dc9a4cb53818ed6ffed10825989cb621c0ec4306c316b15fa8136010601fb76b` |
| 1mo derived from 1d | 110 | `2fb1005954d2dab96fe1c848a06bd7c5044547a531f208f81c630bea5866f1a0` |

The raw native `1mo` archive inventory is 105 ZIPs; the derived 1mo candidate is a separate 110-row monthly aggregation from the daily candidate and must not be confused with native 1mo archives.

## 5. Critical unresolved candidate defect

CP-0026 selected daily-reference bars for 40 flagged dates when the daily archive hash matched the CP-0025 checksum evidence; monthly bars were retained on unflagged dates when their recorded checksum matched. The rule is provisional and does not establish global source authority.

For 4h:
- Candidate total: 19,975 rows = 19,751 monthly-retained rows + 224 daily-reference override rows.
- Raw monthly 4h archive row count in prior evidence: 19,974.
- A daily-reference override row exists at `2017-09-06T16:00:00Z`: OHLC all `4619.43`, volume `0E-8`, trade count `0`, source archive `BTCUSDT-4h-2017-09-06.zip`, raw close-time token `1504713600000`, normalized close time flagged true.
- This is a zero-trade, flat-price placeholder and its raw close-time token is not a normal 4h close boundary.
- The candidate therefore contains at least one row that must not be accepted as a valid market candle without a separately authorized disposition.

The raw ZIP and sidecar can both be authentic while the data-selection decision is still wrong or unresolved. Do not modify raw files, infer a replacement candle, or close the source case based on checksum success alone.

## 6. Existing source investigations in the ZIP

- CP-0025: 240 daily archives examined; 60 checksum-verified daily/monthly value-mismatch rows; zero read errors; no automatic corrections; gate `INVESTIGATE_BEFORE_BACKTEST`.
- CP-0093: six official daily ZIP/checksum pairs; 3/6 content QA pass, 3/6 aggregation buckets exact match, 3 incomplete/not computed; no source selection or case closure.
- CP-0095: three archives for 2017-12-04 share a bad close-time row across 5m/15m/30m; exact aggregation matched in scoped checks, but archives remain `REVIEW_REQUIRED`; zero cases closed and raw rows unchanged.
- CP-0098: official `updates/2022-08-08_kline_updates.zip`, SHA-256 `1404dbfb3d62534b2576a6c0c046826fe652f895b9bebfe4c13df58bc8cf6240`, CRC pass; zero target matches for the known 2017-12 daily keys; no source selected and no case closed.
- Strict monthly audit reports 82 close-time anomalies and 450 off-grid opens (concentrated mainly in Feb 2018), zero OHLC/parse anomalies, and no bad ZIP archives. These are investigation flags, not permission to rewrite source data.

The evidence in this ZIP is historical and ends at CP-0098. It does not supersede later GitHub evidence or current branch state.

## 7. Old backtests are not accepted performance evidence

All historical diagnostics below used the provisional CP-0026 candidate and are **not** strategy approval or established profitability:

- 4h EMA12/26 OOS (2025–Sep 2026): -46.33%; intrabar DD proxy -58.89%.
- 4h Donchian20/10 OOS: -24.85%; intrabar DD proxy -39.88%.
- 4h RSI14_30_55 OOS: +0.63%; intrabar DD proxy -39.80%.
- CP-0031 4h breakout + daily regime at 25% allocation: TRAIN +81.993%, DEVELOPMENT_CHECK +24.344%, consumed OOS -1.385%, PF 0.846 on consumed OOS. `pristine_oos=False`.
- CP-0030 paper session: about 62 minutes, 6 loops, zero closed trades and zero realized P&L. It is not 180-day forward-paper evidence.
- Legacy diagnostics used 10,000 USDT as starting capital. The actual user capital baseline is ₹10,000 INR, so those absolute amounts do not represent the user's capital.

These results reinforce the need to repair the evidence decision first, not to tune a strategy against a disputed candidate.

## 8. Canonical GitHub state checked during this audit

Canonical repository: `manish91082-coder/aists-btcusdt-research-runner`, public, default branch `main`, reported repository size 14,613 KB.

- PR #3, CP-0165 read-only 4h archive audit: OPEN, unmerged, mergeable; head `cec9840c32c80e19f9bc96a5e3655696d303c240`; base `f2fcc6f2e74dcd08e59cdcb811cd680d35fb1733`.
- Latest checked PR #3 static CI run: run `39159871510`, completed/success on that head. It validates configured static tests and fail-closed controls only.
- PR #2, CP-0120 AI-brain foundation: OPEN, unmerged; head `e0f8a6f6e8a5ebf02e171c8a1a85bf853f8b72ec`.
- No submitted reviews on PR #2 or PR #3 at the time of this check.
- Repository README says raw archives and full candidate datasets are excluded from workflow artifacts; artifacts retain for 7 days.
- No new backtest, candidate build, source-policy application, PR merge, or live exchange action was performed.

## 9. Locked gates and next actions

- G0: `BLOCKED_GLOBAL`; canonical historical source remains `NONE`.
- G2: `FAIL_CURRENT_23_CANDIDATES`.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- G4: `INSUFFICIENT_EVIDENCE`; no adequate forward-paper validation.
- G6: `NOT_BUILT`; no adaptive learning/strategy selector validated end-to-end.
- G7: live signing, public broadcast and exchange orders remain `BLOCKED`.
- CP-0152 strategy proposal remains pending explicit approval; no new strategy backtest until source gate clearance and explicit scope approval.

### Three-step execution plan

**STEP 1 — ZIP audit, compact record, Git persistence (this report):** complete the read-only archive inventory, hash/lineage checks, defect isolation, current GitHub-state reconciliation, and save this compact record to the existing PR branch. Do not upload the 200 MB archive to GitHub.

**STEP 2 — Fresh-data eligibility and acquisition through GitHub only:** first inspect the existing allowlisted GitHub Actions workflow inputs and source/retention rules. Then acquire only the genuinely missing official archive data needed for the next evidence question, via the existing GitHub workflow and official downloadable archive/checksum objects. No Colab, no Binance REST API, no credentials, no live prices. Before dispatch, identify exact interval/date coverage and avoid re-downloading already verified archives. Do not run candidate build/backtest as a side effect.

**STEP 3 — Source disposition and research readiness:** build a read-only, exact-key disposition matrix for the unresolved source conflicts using only genuinely new official evidence or an authorized independent review. Do not apply Policy B, close cases, promote candidates, or declare G0 passed without the required independent authorization. Only after G0 and explicit strategy-scope approval can a frozen-input research run be considered.

### Retention decision

- GitHub: store compact reports, manifests, hashes, decision records and small reproducible code/tests only.
- User Drive: retain the original uploaded ZIP and, if needed, larger raw archives/candidate datasets. The original archive hash above is the identity check.
- ChatGPT: this report and the verified summary are available in this conversation, but do not treat the chat as durable binary storage.

**Final status:** ZIP integrity PASS; internal source lineage PASS; canonical source authority NOT ESTABLISHED; candidate eligibility FAIL/BLOCKED; profitability NOT ESTABLISHED. No gate was promoted by this audit.
