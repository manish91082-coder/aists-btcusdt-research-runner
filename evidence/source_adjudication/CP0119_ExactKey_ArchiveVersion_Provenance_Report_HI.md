# CP-0119: Exact-key archive-version provenance adjudication

- **Status:** `BLOCKED_INPUTS_NOT_REPRODUCIBLE`
- **Review date:** 2026-10-17
- **Scope:** Only the 11 frozen CP-0118 aggregation cases and their exact current daily/monthly archive SHA-256 identities. No new market-data archive was downloaded.
- **Current repository baseline:** `main` HEAD `bbbed4bb0aba3ca0e1a1545103d20bc0d430fa31`; CP-0118 current-pointer blob `05bab9942c87aeb28fab4bbc2d1125db5f0de4d0`; CP-0118 matrix blob `d4680d70eb0cd71d3f6d14df1ba5ebcd1bf9c8b3`; CP-0118 details blob `935edba0dee13450ef43ee67254b615cb329e728`.
- **Frozen evidence:** CP-0107 RowEvidence blob `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9` (78 contextual source rows); bucket snapshot blob `6e32188472ab45b43e1b90fe138399818c937277`; official daily reference manifest blob `1a1a264923b12bd8d8f38c362a4fe7f32b871356`; monthly archive subset manifest blob `c9baaaa65bf6d4be45aab2effba9fc31a4383910`.

## Findings

1. All 11 exact bucket keys were rejoined against frozen row evidence. For each bucket, the current daily and monthly child/parent archive filenames and SHA-256 values are recorded in the accompanying matrix. Daily checksum-sidecar SHA-256 values are retained where the frozen manifest records them. Monthly archive identities come from the previously verified monthly manifest subset.
2. These SHA-256 values identify the current bytes used by the prior audit. They do **not** provide an old-version hash, first-publication time, replacement time, or dated event linking a prior version to any of these exact keys.
3. The current official Binance Public Data README lists the 2022-08-08 Spot kline correction package and the 2022-04-21 aggregate-trade update. It does not provide a dated version history for the 11 exact current archive hashes. CP-0095/CP-0096/CP-0097 already exhausted the previously frozen official correction route for their frozen target set, with no exact path/basename or archive-hash link; this audit does not repeat that bundle/hash search.
4. Binance Public Data issue [#504](https://github.com/binance/binance-public-data/issues/504), checked on 2026-10-17, remains open with zero comments and no maintainer answer observed on previous-version retention, publication/replacement timestamps, or point-in-time reconstruction. Issue [#475](https://github.com/binance/binance-public-data/issues/475) remains open and discusses different dates, so it is context only, not a case-specific resolution.
5. Therefore, the reviewed public evidence does not establish historical version provenance for any of the 11 exact bucket relationships. This is an evidence gap, not proof that prior versions do not exist and not proof of which source is globally authoritative.

## Decision

- **Disposition:** all 11 blockers remain open; `BLOCKED_INPUTS_NOT_REPRODUCIBLE` for historical archive-version attribution.
- Canonical source: `NONE`. Source cases closed: `0`. Unresolved aggregation blockers: `11`.
- Gates unchanged: G0 `BLOCKED_GLOBAL`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G7 `LIVE_BLOCKED`.
- No daily-over-monthly precedence; no source bytes changed; no timestamp shift/rounding; no synthetic candles; no candidate build/backtest/strategy promotion; no live signing, public broadcast, or Binance orders.
- No GitHub Actions run was triggered for this read-only connector-side review. This checkpoint is a persisted evidence disposition, **not** a claimed CI PASS.

## Next step

Keep the 11 relationship blockers quarantined. Do not rerun the exhausted correction bundle without new official evidence. The next decision path is a formally frozen, rulebook-compatible conservative quarantine policy, followed by actual candidate-specific final metrics through the existing G0 fail-closed path. Do not weaken the production gate or promote candidates.
