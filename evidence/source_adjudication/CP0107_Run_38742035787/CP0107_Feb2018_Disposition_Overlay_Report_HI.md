# CP-0107 February 2018 quarantine disposition overlay

- Status: PASS_DISPOSITION_OVERLAY_EXPORT
- Row dispositions: 450/450 QUARANTINE_REVIEW_REQUIRED
- CP-0041 crosswalk SHA-256: 5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b; 450/450 monthly row keys, archive hashes and 12 raw fields match the verified crosswalk.
- Exact daily open-key counterpart: 0/450. Shifted target rows: 448 present, 2 absent. All 448 present targets differ in at least one non-open field; 442 differ in open price, 447 in close_time and 448 in volume.
- Frozen CP-0040 G0: no source winner from timestamps alone. Root cause remains OPEN; do not shift/round, merge, replace, delete or synthesize rows; no backtest or candidate promotion.
- This focused segment verification does not close the separate 16-item official daily-reference acquisition queue.
