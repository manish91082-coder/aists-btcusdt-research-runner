# CP-0107 February 2018 cache-only row extraction

Status: PASS_CACHE_ONLY_EXTRACTION
Expected/extracted off-grid rows: 450/450
Target source objects verified: 16/16
Daily raw coverage rows exported: 1167
Off-grid segments verified: 10; date/interval coverage rows: 12
Checks: 9/9

Monthly ZIP SHA-256 values were compared with the official hash stored in the frozen CP-0106 manifest. Monthly checksum sidecar bytes were not reacquired; the corresponding hashes are parent-manifest references only. Daily ZIPs and cached same-directory checksum sidecars were rehashed and content-matched.
Raw fields are preserved as exact text tokens. Floor/ceiling keys are diagnostic only. No network, repair, timestamp shift, merge, replacement, deletion, synthetic candle, canonical-source selection or backtest was used.
