# CP-0040 Exact-Key Quarantine Gate Self-Test — 2026-10-16

## निर्णय
**PASS: 7/7 deterministic synthetic tests; candidate eligibility अभी भी BLOCKED.**

## Goal alignment
यह checkpoint CP-0040 के unresolved source rows को exact `(interval, open_time_ms)` key पर quarantine करने के लिए reusable gate primitives और deterministic regression tests जोड़ता है। इससे पहले builder को unresolved rows को गलती से स्वीकार करने से रोकने की दिशा में आधार तैयार होता है।

## सत्यापित GitHub evidence
- Repository: `manish91082-coder/aists-btcusdt-research-runner`
- Tested commit: `15a2f1826e27e7bbccde74ffafc035b645a594ea`
- Workflow run: [38874755147](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/38874755147)
- Run terminal result: `completed / success`
- Runner result: `PASS`, 11/11 runner checks passed.
- Quarantine gate self-tests: 7/7 passed.
- Workflow artifact: `aists-run-38874755147-attempt-1`, artifact ID `12033984922`, SHA-256 `a9220017bb4eb576213c50b5b9bd4390d88dfced9ba9ec59b0bdd24561102d53`.
- Embedded self-test summary SHA-256: `3c8007bc6f5e6beb8506ac07e8ee8c54da457582ee8d911804f0e4a253b6e8da`.
- Runner summary SHA-256: `c21a75ff5720a3c885d7995e76b327ab34560e7cb8dc1ede6d2deef00230856d`.
- Artifact ZIP CRC: PASS; embedded summary and runner summary parsed successfully from downloaded artifact.

## Test scope
1. Exact interval + timestamp key is excluded.
2. Unlisted timestamp is retained.
3. Same timestamp in another interval is retained.
4. One-millisecond difference is not rounded into a match.
5. Raw tokens and source row values remain unchanged.
6. Fractional timestamp token is rejected.
7. No rounding is applied to fractional tokens.

## सीमा / क्या नहीं हुआ
- Tests used synthetic fixtures only.
- No market-data archive was read by this task.
- No CP-0026 candidate build or backtest was run.
- The new quarantine primitive is not yet wired into the CP-0026 candidate builder.
- A complete frozen manifest still needs all unresolved exact keys and explicit scope/count/hash checks before candidate use.
- No source was declared canonical, no strategy was promoted, and live signing/public broadcast/exchange orders remain blocked.

## अगला goal-aligned कदम
Complete and verify the full exact-key quarantine manifest from the frozen CP-0041 evidence, then wire this gate into the candidate builder with fail-closed coverage checks. Only after those tests pass should a quarantined candidate build be considered. Re-run a historical backtest only if candidate bytes change.
