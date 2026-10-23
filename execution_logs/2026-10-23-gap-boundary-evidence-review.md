# Gap-boundary evidence review

**Date:** 23 October 2026  
**Branch:** `research/full-history-validation`  
**Workflow run:** [39968448783](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions/runs/39968448783)

## Actions performed
- Polled the workflow run, jobs, and artifacts after completion.
- Confirmed `spot-1m-gap-audit` completed successfully and `long-history-validation` failed.
- Retrieved the diagnostic job log and parsed boundary context for all 12 affected months.

## Verified observations
- The diagnostic artifact was uploaded as `btcusdt-spot-1m-gap-audit` (artifact ID `12507817926`).
- The long-history job still fails 12 Spot 5m monthly checks; the diagnostic did not clear the fail-closed archive gate.
- Across affected months, Spot 1m and Spot 5m show matching discontinuity windows/counts.
- Boundary rows are heterogeneous: some preceding candles are flat with zero volume, while other gap boundaries have nonzero volume and normal price movement. This does not support a blanket assumption that every missing interval is simply a no-trade interval.
- Raw close-time anomalies are present. For example, the 2020-12 row at open time `1608559500000` has raw close time `1608558440521`, which is earlier than its open time; other affected boundaries also have close-time values ending before the expected interval end. These rows need source-level resolution.
- Matching checksums confirm archive bytes against the published sidecar; they do not prove timestamp continuity or semantic correctness.

## Decision and next step
Do not change validator rules yet. Do not synthesize candles, forward-fill prices, or silently exclude gaps. Next, compare each exact UTC gap window and anomalous close-time row against an independent official Spot trade/aggregate-trade source where available. Keep raw data and record any source unavailability explicitly. Only after that review should we decide whether the validator expectation is wrong or the archives are incomplete/anomalous.

## Gate status
- Full-history validation: **BLOCKED / FAIL-CLOSED**.
- Walk-forward research: **NOT STARTED**, pending data gate.
- PR #17: **UNMERGED**.
- Live trading/orders/funds movement: **NOT AUTHORIZED**.
- Tax analysis: **DEFERRED**.
