# CP-0239 Current BTCUSDT Spot Filter Evidence Capture

**Review date:** 2026-10-18  
**Decision:** `CP0239_CURRENT_SPOT_FILTER_SNAPSHOT_CAPTURED_HISTORICAL_G0_UNCHANGED`  
**Purpose:** Capture official public operational symbol filters for BTCUSDT without accessing account credentials, trading, or historical market candles.

## 1. Capture method and verification

- Official Binance public market-data endpoint: `https://data-api.binance.vision/api/v3/exchangeInfo?symbol=BTCUSDT`
- Official documentation identifies `GET /api/v3/exchangeInfo` as the endpoint for current exchange trading rules and symbol information. The market-data-only documentation explicitly lists this endpoint as public and unauthenticated.
- Capture implementation: [scripts/capture_binance_spot_filters.py](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/cp-0120-ai-brain-foundation/scripts/capture_binance_spot_filters.py)
- Workflow: [CP-0239 Capture Current BTCUSDT Spot Filters](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/cp-0120-ai-brain-foundation/.github/workflows/cp0239-capture-spot-filters.yml)
- Workflow run succeeded: [39152856418](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39152856418), head commit `e387b418df289fa5c815dde78f2536d567125d8a`. CP-0120 unit tests also succeeded at that exact head: [39152856412](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39152856412).
- The workflow validates the response contains exactly BTCUSDT and a non-empty filter list, preserves the exact raw response bytes, calculates SHA-256 over those bytes, and writes a timestamped manifest.
- Raw response and manifest were re-fetched from the repository. Two captures occurred 29 seconds apart, with identical reported filter values.

## 2. Captured evidence files

### Snapshot A

- Captured UTC: `2026-10-18T18:09:01.577309+00:00`
- Manifest: [BTCUSDT_Spot_exchangeInfo_20261018T180901Z.manifest.json](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/cp-0120-ai-brain-foundation/evidence/operational_filters/BTCUSDT_Spot_exchangeInfo_20261018T180901Z.manifest.json)
- Raw response: [BTCUSDT_Spot_exchangeInfo_20261018T180901Z.raw.json](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/cp-0120-ai-brain-foundation/evidence/operational_filters/BTCUSDT_Spot_exchangeInfo_20261018T180901Z.raw.json)
- SHA-256 of raw response bytes, as recorded by the capture script: `24f73a00a40402ad3b622fb55e87084d08bd0b0ec2fe5d3b7c80f1d04272a7b6`
- Git blob SHA of raw file: `408da72dd60b41d192921f9c630c6b874196864e`

### Snapshot B

- Captured UTC: `2026-10-18T18:09:30.811077+00:00`
- Manifest: [BTCUSDT_Spot_exchangeInfo_20261018T180930Z.manifest.json](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/cp-0120-ai-brain-foundation/evidence/operational_filters/BTCUSDT_Spot_exchangeInfo_20261018T180930Z.manifest.json)
- Raw response: [BTCUSDT_Spot_exchangeInfo_20261018T180930Z.raw.json](https://github.com/manish91082-coder/aists-btcusdt-research-runner/blob/cp-0120-ai-brain-foundation/evidence/operational_filters/BTCUSDT_Spot_exchangeInfo_20261018T180930Z.raw.json)
- SHA-256 of raw response bytes, as recorded by the capture script: `3f22b055b83ce3d837e5b90a54156573220f48900d736af782e812fe5f5ee1c6`
- Git blob SHA of raw file: `ce1f4cc3fef4c90d7b2afb323655e9253bf69e45`

The raw payloads have different hashes because response metadata (including server time) changes. The symbol filter fields reviewed in the two manifests were identical.

## 3. Key current filter values captured

These are current operational values from the captured payload, not values reconstructed for past dates.

| Filter | Captured value | Meaning / caution |
|---|---|---|
| Symbol status | `TRADING` | Status at capture time only |
| `PRICE_FILTER.tickSize` | `0.01000000` | Price increment |
| `PRICE_FILTER.minPrice` | `0.01000000` | Minimum permitted price |
| `LOT_SIZE.minQty` | `0.00001000` | Minimum limit-order quantity |
| `LOT_SIZE.stepSize` | `0.00001000` | Limit-order quantity increment |
| `LOT_SIZE.maxQty` | `9000.00000000` | Maximum quantity under this filter |
| `MARKET_LOT_SIZE.maxQty` | `144.13038045` | Captured market-order quantity cap |
| `NOTIONAL.minNotional` | `5.00000000` USDT | Minimum notional; payload says applies to market orders |
| `NOTIONAL.maxNotional` | `9000000.00000000` USDT | Maximum notional in this filter |

The market-lot-size `minQty` and `stepSize` were both reported as zero in this payload. Do not treat that as a universal quantity-rounding rule: candidate-side rounding and order-type-specific filter enforcement must be tested explicitly if a future evaluation is approved. These filters alone do not establish actual account eligibility or the full acceptance of any order.

## 4. What this does and does not resolve

**Resolved for current operational metadata:** the official public endpoint was queried by GitHub Actions; exact raw responses and timestamped manifests were committed and re-fetched; reported hashes and filter fields are recorded.

**Not resolved:**
- Historical BTCUSDT filter state for any earlier candle/date.
- G0 historical candle-source provenance, archive-version history, or the 4h monthly/daily discrepancies.
- Actual account fee tier or BNB fee-discount eligibility.
- ₹10,000 INR-to-USDT conversion source/time/cost, allocation fraction, or cash reserve.
- CP-0152 explicit user approval.
- Any strategy profitability or trade execution quality.

No klines or trade-history data were downloaded by this capture script. No candidate was built, no backtest/paper test was run, and no order, signature, or public broadcast was performed.

## 5. Gate status

- G0: `BLOCKED_GLOBAL`; canonical historical source: `NONE`
- G2: `FAIL_CURRENT_23_CANDIDATES`; CP-0152 remains an unapproved proposal
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- G4: `INSUFFICIENT_EVIDENCE`
- G6: `NOT_BUILT` for validated adaptive AI
- G7: `LIVE_BLOCKED`
- Profitability: `NOT ESTABLISHED`

**Next admissible step:** separately reconcile the two snapshot manifests and capture/verify account-independent capital-conversion inputs only if an authoritative source can be preserved. Do not backdate these operational filters, bypass G0, or run CP-0152 without explicit approval and G0 clearance.
