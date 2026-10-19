# CP-0269: Independent Verification of CP-0268 Scoped G0 Artifact

Date: 2026-10-19
Scope: BTCUSDT Binance Spot, 4h candidate eligibility only.
Purpose: Independently inspect the CP-0268 GitHub Actions artifact without changing source archives, selecting a canonical historical source, running a backtest, or enabling trading.

## Source artifact identity

- GitHub run ID: 39285070782
- Head SHA: `2f8e549d39aec9b2435b66be491d3daa30aab112`
- Artifact: `cp0268-g0-runtime-39285070782-attempt-1`
- Artifact ID: 12202328549
- Artifact ZIP SHA-256 reported by GitHub: `4ce353d324a954442cf30aa91283026b58c3b3f31b8af59a6a47b445cbc364ad`
- Runtime receipt: `CP0268_G0_Runtime_Receipt.json`
- Candidate SHA-256: `60da1fdf1e188daf7c2cbeed508368042c92e5736c4a52c0eabad8019068b434`
- Candidate manifest SHA-256: `c91386d3a42c07ce7da7093029e32773a1eeff78eec287a73661cf9622213bac`

## Independent checks

| Check | Result |
|---|---|
| Receipt status equals `PASS_G0_SCOPED_4H_CANDIDATE_ELIGIBILITY_ONLY` | PASS |
| Receipt, candidate manifest, and candidate row count agree | PASS |
| Candidate compressed-file SHA-256 matches receipt and manifest | PASS |
| Candidate has 19,751 rows and 19,751 unique open-time keys | PASS |
| Every candidate row has `VERIFIED_PRIMARY_CURRENT_SNAPSHOT` source status | PASS |
| Every candidate row has a non-empty source SHA-256 | PASS |
| No candle falls on any of the 40 frozen CP-0025 flagged UTC dates | PASS |
| 110 monthly 4h archives pass the CP-0165 checksum/CRC audit | PASS |
| Candidate structural audit reports zero parse errors, off-grid opens, OHLC anomalies, duplicate opens, or out-of-order opens | PASS |

Independent verifier result: `PASS_SCOPED_CANDIDATE_INTEGRITY` (9/9 checks).

## Interpretation and limits

The 4h scoped candidate contains 19,751 rows. The build recorded 35 gap events and 240 estimated missing intervals; these include deliberate full-day exclusions for the 40 flagged dates and are not silently filled. The candidate is **not acceptance-grade**.

Historical-version provenance remains `NOT_VERIFIED`. CP-0040's frozen manifest has 969 unresolved exact-key cases and its frozen non-row blocker file has 27 unresolved blockers, including aggregation and date-reference cases. The runtime receipt explicitly states `g0_scope_status=G0_SCOPED_PASS_4H_CANDIDATE_ELIGIBILITY_ONLY`, `profitability_established=false`, and `live_signing_broadcast_orders=BLOCKED`.

**Decision:** accept only the bounded CP-0268 scoped candidate-eligibility result, pending workflow terminal-state reconciliation and CI terminal verification. Do not mark global G0 closed. Global closure requires source-authority/provenance adjudication of the frozen unresolved populations under the unchanged CP-0040 acceptance contract. Do not merge the PR or promote the candidate based on this scoped result.

## Workflow state caveat

At the time of this independent check, GitHub's run/job API still returned run 39285070782 and its static test run 39285076379 as `queued`, despite the downloadable artifact containing a completed runtime receipt and candidate. This API/artifact state discrepancy is unresolved; no terminal CI success is claimed.
