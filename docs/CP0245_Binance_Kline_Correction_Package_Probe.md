# CP-0245 — Official Binance kline correction-package content probe

Recorded: 2026-10-19  
Workstream: historical source provenance  
Status: READ-ONLY OFFICIAL CORRECTION MANIFEST INSPECTION

## Decision

Decision: `CP0245_CORRECTION_MANIFEST_DOES_NOT_COVER_KNOWN_2017_KEY_G0_UNCHANGED`.

The official `updates/2022-08-08_kline_updates.zip` package was downloaded by the isolated GitHub Actions probe and inspected as a ZIP. Its contents are a correction manifest CSV and a macOS metadata entry; it does not contain replacement market-data ZIPs. The manifest lists checksum replacements for daily archives. It does not establish a correction for the known BTCUSDT 4h key at `1504713600000` (`2017-09-06T16:00:00Z`).

## Reproducible package identity

- Official package URL: https://raw.githubusercontent.com/binance/binance-public-data/master/updates/2022-08-08_kline_updates.zip
- Download HTTP status: `200`
- Downloaded bytes: `6,653,240`
- SHA-256: `1404dbfb3d62534b2576a6c0c046826fe652f895b9bebfe4c13df58bc8cf6240`
- Outer ZIP CRC test: `PASS`
- Outer ZIP entries:
  - `2022-08-08_kline_updates.csv` (17,950,767 uncompressed bytes)
  - `__MACOSX/._2022-08-08_kline_updates.csv` (220 bytes, metadata)
- Manifest data rows: `73,234`
- Manifest columns: `File Path`, `Original File Checksum`, `New File Checksum`

## Project-specific relevance

The manifest has four rows whose path names contain both `BTCUSDT` and `4h`. All four are daily archives, not the project’s monthly 4h archive inventory:

| Manifest path | Original SHA-256 | Replacement SHA-256 |
|---|---|---|
| `data/spot/daily/klines/BTCUSDT/4h/BTCUSDT-4h-2021-08-02.zip` | `4da2ef979d4ed7588dc5b6e719018917c72889209f9fa51b2b03f69ef5ff47d4` | `c35a1097f131a35049d275efa3b42f28f8bde01429e4e4df35db310ff43193c2` |
| `data/spot/daily/klines/BTCUSDT/4h/BTCUSDT-4h-2022-03-10.zip` | `7b30d9db8759b2516cfec3ff6cbc7671f11579beacfbe87f9208453e670955c1` | `71060af247b5a10cbd7504a5257d047cc569ba43292e8ecb9c2ab98fe770ee77` |
| `data/spot/daily/klines/BTCUSDT/4h/BTCUSDT-4h-2022-03-22.zip` | `8441a6756bd9dfd76f2728ff5bc304b19c1ced3b85a224e69176e12410b28d7e` | `b3b64cc14844bfd8a45cc0d8502e5d294fbdead644d6a5f9c581b95eaa88418c` |
| `data/spot/daily/klines/BTCUSDT/4h/BTCUSDT-4h-2022-03-14.zip` | `be337cec630c853c94825c79ce170829072d3696471ddfa3855d4b077ccb1cdb` | `fd7e0f12c88aeca25ecfd780603b54aeffcc3417468073c72b5ea05a4e91a6ca` |

No manifest row matched the known 2017-09-06 key. Because this bundle is a checksum manifest, not a bundle of replacement market-data records, that absence means only that this manifest does not list a matching correction path. It does not prove that no correction exists elsewhere, nor does it adjudicate the daily/monthly conflict or reconstruct historical point-in-time availability.

## Verification

- Probe workflow run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39157359192
- Probe workflow completed successfully; its JSON artifact was uploaded by the run.
- Static audit CI on the prior code revision: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39157315873 (SUCCESS).
- The probe downloads only the public correction package, does not change source market data, and never selects a canonical source.

## Gate disposition

- Canonical historical source: `NONE`; G0: `BLOCKED_GLOBAL`.
- G2: all 23 current candidates remain historical-screen FAIL.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- G4: `INSUFFICIENT_EVIDENCE`; G6: `NOT_BUILT`; G7: `LIVE_BLOCKED`.
- Profitability: `NOT ESTABLISHED`.
- CP-0152 remains `PENDING_EXPLICIT_APPROVAL`.
- No market-data correction was applied; no source case was closed; no candidate build/backtest/paper run or exchange order/signing/broadcast occurred.

## Next admissible action

Do not re-run this package scan. It is now bounded and exhausted for the known key. Continue only with genuinely new official per-file version/provenance evidence or an authorized independent review and separately scoped policy-application record. Preserve unresolved cases and do not infer G0 clearance from this manifest or CI success.
