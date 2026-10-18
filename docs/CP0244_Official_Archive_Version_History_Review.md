# CP-0244 — Official archive-version and point-in-time provenance boundary review

Recorded: 2026-10-19  
Workstream: historical source provenance  
Status: READ-ONLY OFFICIAL DOCUMENTATION/GIT-HISTORY REVIEW

## Decision

Decision: `CP0244_OFFICIAL_VERSION_HISTORY_INSUFFICIENT_G0_UNCHANGED`.

The official Binance Public Data README states that archived files may be updated later and lists archive update packages with old/new checksums. The visible update table contains entries dated 2022-08-08 (kline data, “Fixed inconsistent data”) and 2022-04-21 (aggregate-trade data alignment). This is useful correction evidence, but it does not establish exact UTC first-publication times for each archive version, exact replacement-effective timestamps, complete retained historical ZIP versions, or point-in-time reconstruction.

## Evidence reviewed

1. Official README: https://github.com/binance/binance-public-data/blob/master/README.md
   - States Spot kline files are obtained from `/api/v3/klines`.
   - States each ZIP has a `.CHECKSUM` file for integrity verification.
   - Says archived files may be updated later and presents an update table with old/replacement checksum packages.
   - The displayed update table does not document a per-version first-publication timestamp or a complete per-file version ledger.
2. README Git history:
   - Current README path history includes a commit on 2026-09-30 (`bd110bb04caad6ad964a0098809f18343b1e104b`) that added `TERMS_AND_CONDITIONS.md`; this is a repository documentation change, not a market archive publication record.
   - Earlier README history includes the 2025-01-09 “Microsecond update” commit (`de6bdec7520bcae888d66c362257f120dfc9d65b`) and 2024-08-02 README update (`9c1bbe657df8e8721cbd5670bac1d777767ca07f`). These are README commit times, not timestamps for individual data ZIP publication/replacement.
3. Official Terms file history:
   - Added 2026-09-30 in commit `bd110bb04caad6ad964a0098809f18343b1e104b`.
   - Syntax updated 2026-10-16 in commit `d3357a5c33bac92b60f2afb7f28a63991f099bcd`.
   - These commits document the terms file's Git history only and do not prove which terms applied to every older archive at its original download time.
4. Official repository issue #504: https://github.com/binance/binance-public-data/issues/504
   - At review time it remained OPEN with zero comments. It asks about previous ZIP versions, first-publication/replacement timestamps, correction-list completeness, REST/archive differences, and point-in-time reconstruction.
   - No official maintainer answer was present in the issue/comments response reviewed in this checkpoint.

## Findings and limits

- ZIP SHA-256/checksum validation establishes byte integrity relative to the supplied checksum, not that the file is the version available at a particular historical time.
- README correction packages establish that at least some archive updates/corrections are documented; they do not, by themselves, establish a complete immutable version history or guarantee that all corrections have a public changelog entry.
- A Git commit timestamp for README/terms is not an archive's first-publication or replacement timestamp.
- The documentation identifies Spot klines with the REST `/api/v3/klines` endpoint, but does not provide an officially supported point-in-time reconstruction procedure in the reviewed text.
- These findings are an evidence-boundary assessment, not proof that version history does not exist internally or through an unreviewed channel. Any undocumented capability remains UNKNOWN, not NO.

## Gate disposition

- Canonical historical source: `NONE`; G0: `BLOCKED_GLOBAL`.
- G2: all 23 current candidates remain historical-screen FAIL.
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`.
- G4: `INSUFFICIENT_EVIDENCE`; G6: `NOT_BUILT`; G7: `LIVE_BLOCKED`.
- Profitability: `NOT ESTABLISHED`.
- CP-0152 remains `PENDING_EXPLICIT_APPROVAL`.
- No market archive downloaded, no source case closed, no candidate build/backtest/paper run, and no exchange order, signing, or broadcast occurred.

## Next admissible action

Do not repeat checksum/cache-only scans. Seek a documented official per-file version/provenance mechanism or a written maintainer response to the already-open issue #504. If no official answer is available, preserve the result as UNKNOWN and use only an authorized independent review with explicit scope and a separate policy-application record; do not infer G0 clearance.

## Validation boundary

This checkpoint records official documentation and public Git/issue state. It does not validate profitability, establish canonical market data, provide legal advice, or authorize strategy execution.
