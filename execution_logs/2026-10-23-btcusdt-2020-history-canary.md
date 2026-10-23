# Execution record: BTCUSDT January 2020 historical coverage canary

- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922039878
- Run ID: 39922039878
- Job ID: 120309329993
- Workflow commit: 914309e0b134add033206be80183c9cad35b7e5d
- Requested UTC month: 2020-01
- Collector exit code: 0; summary PASS=3, UNAVAILABLE=0, FAIL=0.
- Total verified archive bytes: 4,054,135.

## Per-archive evidence from the GitHub execution log
1. Spot 1m klines: PASS; 2,224,194 bytes; SHA-256 02df6da44ed8145fbb9ed819858185d9e2f15eb025c5bec8a4ea2d8738cd0d19.
2. USDⓈ-M Futures 1m klines: PASS; 1,829,116 bytes; SHA-256 b4e13ea185ba96c413ac9167cfbb6e238eb5eae119a7a77f41f4c61c5e099d03.
3. USDⓈ-M funding archive: PASS; 825 bytes; SHA-256 7f81b2f3694d13779e7e896b69d60cd61e9444d7b9f9e90df761935e1c1b76e2.

Artifact: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39922039878/artifacts/12486769727 ; artifact ID 12486769727; size 4,057,887 bytes; retention 30 days. The artifact contains execution.log, the JSON manifest and source archives.

## Interpretation
- The exact September 2019 UM Futures and funding archive paths were HTTP 404, while January 2020 UM Futures and funding archives both passed. This narrows the archive availability boundary to somewhere between these tested months only; it does NOT establish the exact earliest available month.
- Spot passed in both September 2019 and January 2020. A proper month-by-month coverage manifest is still needed to determine exact contiguous coverage and any gaps.
- No Supabase/database write was attempted. No permanent storage is claimed.
