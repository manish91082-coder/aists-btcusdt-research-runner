# Market Data Manifest Specification v0.1

Status: SPECIFICATION ONLY; no dataset acquired or validated.
Purpose: make every market-data input traceable and auditable before strategy testing.

## 1. One manifest row per dataset artifact

Required fields:
- manifest_id: stable unique identifier.
- venue: Binance.
- market_type: SPOT or USD_M_FUTURES (use a distinct value for any other product).
- symbol: exact exchange symbol.
- interval: exact API/archive interval token (monthly archive token is 1mo).
- data_kind: klines, aggTrades, trades, fundingRate, markPriceKlines, indexPriceKlines, depth_observation, exchangeInfo_snapshot or another explicitly named dataset.
- source_type: public_archive or public_api.
- source_url: exact canonical URL/path used.
- retrieved_at_utc: UTC retrieval timestamp.
- source_file_name, source_file_bytes, source_sha256.
- official_checksum_path, official_checksum_result (PASS/FAIL/NOT_AVAILABLE).
- schema_version, timestamp_unit (ms/us/ns/other), timestamp_timezone.
- first_event_time_utc, last_event_time_utc, row_count.
- duplicate_rows, out_of_order_rows, missing_interval_count, malformed_rows.
- validation_status: NOT_STARTED/PASS/FAIL/BLOCKED.
- validator_version, validator_output_path.
- notes: documented limitations, archive updates, transformations and known gaps.

Never populate a field by guessing. Use NOT_AVAILABLE or UNKNOWN and explain why.

## 2. Companion validation report

For each artifact, record:
1. Source URL and retrieval date/time.
2. Exact original filename and byte size.
3. Official checksum result, when a checksum is provided; independent local SHA-256.
4. File format, header/schema, numeric precision and timestamp unit.
5. Earliest/latest event and expected interval alignment.
6. Row count, duplicate/out-of-order/malformed rows and gaps.
7. OHLC invariants: low <= open/close <= high, low <= high; volume/price non-negativity where the product semantics require it.
8. Candle open/close-time semantics and whether the final candle is partial.
9. A sample comparison with the relevant official API endpoint.
10. Explicit PASS/FAIL/BLOCKED decision and reviewer note.

A checksum PASS proves byte integrity relative to that checksum, not that the source data is economically correct or complete. Data quality checks are separate.

## 3. Timestamp handling lock

Binance public-data documentation notes that Spot archive timestamps from 2025-01-01 onward use microseconds for the documented fields. Older files may use milliseconds. Do not decide by magnitude alone without corroborating source, file period and schema. Record the raw integer and the normalised UTC value. Unit conversion must be tested around known dates and compared with API responses. Preserve the original raw file unchanged.

## 4. Required dataset matrix

For each candidate symbol, keep Spot and Futures rows separate:
- Klines: 5m, 15m, 1h, 4h, 8h, 1d, 1w, 1mo.
- Futures funding history where the candidate is used for Futures.
- Futures mark/index/contract price series where needed for trigger, basis or funding modelling.
- Trade/aggregate-trade data or finer bars where intrabar stop/target order matters.
- Live best bid/ask/depth observations for scanner/execution research, stored with capture timestamps. Do not claim historical order-book coverage unless verified source artifacts exist.
- Timestamped exchangeInfo/symbol-filter snapshots and 24h ticker snapshots for universe research. Current snapshots must not be mistaken for historical membership.

## 5. First audit target and acceptance
Recommended first representative audit: BTCUSDT Spot 5m archive for a clearly bounded month, plus the corresponding USDⓈ-M Futures dataset as a separate artifact. This is a test target, not a claim that the files have been downloaded or that either market has complete coverage.

Acceptance requires source path, archive existence, byte size, checksum, schema, timestamp unit, row count, first/last candle, gap/duplicate audit and sample API comparison. If any step cannot be reproduced, status stays BLOCKED/NOT_STARTED. Do not bulk-download all assets/timeframes until this representative path works.

## 6. Strategy test readiness
A strategy experiment may not begin until all input datasets have a validated manifest row and the experiment specification records:
- exact market/symbol/interval/date range;
- source manifest IDs and revisions;
- feature availability timestamp and lookback warm-up;
- point-in-time universe membership;
- execution and cost assumptions;
- split boundaries and holdout lock.

The manifest records provenance and quality, not trading performance.