# CP-0107: दिसंबर 2020 full-archive child-key audit

- GitHub Actions run: https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38756665405
- Runner 11/11 PASS; task 5/5 PASS; evidence publisher PASS.
- Verified source files: monthly 5m ZIP SHA-256 `c169b2a72cc188c8089abc9f3c6f9699e4759a5e7d0d7a7c69d9117b0da68049`, CRC PASS; daily 5m ZIP SHA-256 `b21d0cdd4d29b8a8cfbfbaafd9f926e12989233290daeb0f4977eefb6489525b`, CRC PASS; daily `.CHECKSUM` rehashed and content-matched.
- Expected 5m grid keys in 12:30–14:55 UTC: 30 per source. Monthly archive: 20 present/10 absent. Daily archive: 16 present/14 absent.
- All 9 previously flagged roll-ups still have exact 5m child keys absent from the full verified archives. Detailed mappings and raw rows are in `evidence/source_adjudication/CP0107_Run_38756665405/`.
- This confirms exact-key absence in these archive bytes, not the reason. Root cause OPEN, canonical source NONE, no cases closed. No synthetic candles, download, archive mutation or backtest.
