# Execution record: official BTCUSDT archive URL coverage inventory

- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922532383
- Run ID: 39922532383
- Job ID: 120310939241
- Inventory commit: 79adf2e6fa20141d9c5a55d35c7dc174531d5f5c
- Requested UTC month range: 2017-08 through 2026-09 inclusive (110 months)
- Method: HTTP HEAD checks for each monthly archive URL and its adjacent .CHECKSUM URL. No archive bodies were downloaded in this inventory.
- Requested checks: 330 archive-month records, each checking archive and checksum sidecar URL.
- Overall: AVAILABLE=272, UNAVAILABLE=58, FAIL=0; exit code 0.

## Per-dataset inventory from the downloaded machine-readable artifact
1. Spot 1m klines: 110/110 monthly archive URLs available; first 2017-08; last 2026-09; no missing month in this range. Sum of reported archive Content-Length values: 234,954,793 bytes.
2. USDⓈ-M Futures 1m klines: 81/110 monthly archive URLs available; first 2020-01; last 2026-09; 29 months before 2020-01 returned HTTP 404. Sum of reported archive Content-Length values for available months: 151,823,703 bytes.
3. USDⓈ-M funding: 81/110 monthly archive URLs available; first 2020-01; last 2026-09; 29 months before 2020-01 returned HTTP 404. Sum of reported archive Content-Length values for available months: 71,993 bytes.

Estimated combined compressed archive size by HTTP Content-Length: 386,850,489 bytes (about 386.9 MB decimal, approximately 0.36 GiB). This is an estimate for the listed ZIPs, not the size of normalized datasets or a storage/egress quote.

## Evidence and limitations
- Inventory artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922532383/artifacts/12488291064; artifact ID 12488291064; 6,345 bytes; 30-day retention. It contains the 153,013-byte URL-level JSON inventory and execution.log.
- Smoke CI: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922538810; SUCCESS; 40 tests passed, 68 tracked files protected, zero deletion candidates.
- The coverage inventory confirms URL and sidecar availability by HEAD only. It does not download, checksum-compare, open ZIPs, count rows or validate every month's content. Full content validation is only proven for the September 2026 and January 2020 canary months (plus Spot September 2019 as a separate successful archive).
- A 404 means the exact monthly archive URL is unavailable; it is not evidence that the contract did not exist.
- No Supabase/database write was attempted. GitHub artifact retention remains temporary.

## Next gate
Before bulk collection, confirm the intended Supabase project. The only connected project previously listed was named `supabase ai content creation claude antigravity`, which does not clearly identify this BTCUSDT research project. Do not upload private research data or create tables in that project without confirmation. Once project identity, private bucket, schema, and GitHub Actions secrets are confirmed, run a one-month upload canary and verify both object bytes/SHA-256 and the Postgres catalog row before bounded batch ingestion.
