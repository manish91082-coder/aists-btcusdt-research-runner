# CP-0254 — G0 Rapid Closure Review Packet (Independent Adjudication Required)

**Created:** 2026-10-19  
**Parent execution HEAD:** `2e25eec0f0ca3f930fc958ac35499bece8adf295`  
**Branch:** `cp-0165-4h-archive-audit`  
**Status:** `PACKET_PREPARED_NOT_REVIEWED_G0_BLOCKED_GLOBAL`

## Purpose and fastest valid route

This packet compresses the existing evidence into one decision request so an authorized independent reviewer can adjudicate the unresolved source-authority and quarantine questions without repeating completed checksum/cache scans. It does not itself constitute an independent review, source selection, quarantine authorization, or G0 PASS.

**Fastest valid route:** (1) independent reviewer evaluates the frozen CP-0040 rulebook and linked evidence below; (2) reviewer records a signed, case-specific disposition for each material unresolved population, distinguishing evidence-backed closure from unresolved; (3) if quarantine is recommended, the authorized reviewer approves the exact scope/policy and a separate scoped application record is created; (4) run the existing fail-closed gate and candidate-input dependency checks against the exact reviewed hashes; (5) declare only the gate scope that all frozen CP-0040 clauses actually satisfy. Do not wait on another generic checksum scan.

## Frozen decision contract

- Frozen acceptance rulebook: `evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md`
- Frozen rulebook Git blob: `f0d0e81ea6708a0abeb34676f3ff12859080a3c7`
- Frozen package-member SHA-256: `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`
- Do not edit or reinterpret CP-0040 silently. Any change to acceptance criteria requires a separately versioned change, rationale, prior-vs-new comparison and required independent approval.
- A checksum match proves byte integrity against the matched sidecar; it does not prove historical publication/version authority.
- Do not shift timestamps, fill gaps, synthesize bars, silently replace sources, infer fills, or infer reviewer approval.
- Policy B is frozen for sensitivity only, not G0 clearance: `evidence/source_adjudication/CP0206_Gap_Window_Quarantine_Policy.json`, policy SHA-256 `f8bdc5b034a65e6a9e906c3b80443e9cc149e3d922f6f6f763692cb38cfa8641`.

## Current evidence bundle

1. **Unified unresolved populations:** `docs/CP0251_G0_Unified_Unresolved_Population_Crosswalk_HI.md`. It records non-double-counting rules and links the existing populations.
2. **Clause-level 11 aggregation cases:** `docs/CP0252_Frozen_G0_Aggregation_Clause_Crosswalk_HI.md`. The 11 exact relationship IDs remain open; daily arithmetic agreement does not prove historical version authority.
3. **Second-source feasibility:** `docs/CP0253_Secondary_BTCUSDT_Source_Feasibility_HI.md`. No second dataset has been downloaded and cross-compared; do not treat source discovery as corroboration.
4. **Gap window contract:** `evidence/source_adjudication/CP0206_Gap_Window_Quarantine_Policy.json`. 17 missing 4h slots comprise one overlap with an existing row case and 16 gap-window-only keys; Policy B remains sensitivity-only.
5. **Existing archive audit:** PR #3 / CP-0165 documents 110/110 monthly 4h ZIP checksum-sidecar matches and ZIP CRC passes, 19,974 raw rows, zero duplicate/off-grid 4h opens, 9 gap events / 17 missing slots, and unresolved cross-source aggregation conflicts.
6. **Official-provenance probe:** PR #5 / CP-0248 documents no new key-specific official point-in-time version evidence found in that bounded review. Binance Public Data issue #504 was recorded open with zero comments on 2026-10-19; no external comment was posted.
7. **Current source decision:** canonical historical source `NONE`; G0 `BLOCKED_GLOBAL`; source cases closed `0`; G2 `FAIL_CURRENT_23_CANDIDATES`; G3 `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`; G4 `INSUFFICIENT_EVIDENCE`; profitability `NOT_ESTABLISHED`.

## Exact questions for the independent reviewer

For each population below, return one of: `CLOSED_WITH_EVIDENCE`, `AUTHORIZED_SCOPED_QUARANTINE`, or `REMAINS_UNRESOLVED`. Attach exact source references, hashes, keys, reasoning, scope, and the rulebook clause. A general statement such as “Binance data is trusted” is insufficient.

- [ ] 909 unmatched exact-open-key rows (452 daily-only + 457 monthly-only); 450 February-2018 off-grid rows are a subset of this population, not additive.
- [ ] 52 shared economic/trade-metric conflicts.
- [ ] 8 close-time-only conflicts.
- [ ] 14/35 daily-vs-monthly aggregate divergences across 97 metric fields, cross-linked to their underlying keys rather than double-counted.
- [ ] 11 non-row cross-interval aggregation relationships: AGG-01 through AGG-11, each with its own parent/child identity.
- [ ] 17 missing 4h slots: 1 existing-row overlap plus 16 gap-window-only keys. No synthetic bars or inferred intragap path.
- [ ] December-2020 residuals and other remaining exact-key/roll-up cases as listed in CP-0251.
- [ ] Historical archive/version authority: whether the supplied exact hashes establish the required authority for the proposed research scope; if not, identify the precise missing primary evidence.
- [ ] If quarantine is recommended: whether the reviewer is authorized to approve it; exact affected inputs, exclusions, episode/position accounting, metrics scope, and required separate application record.

## Reviewer decision record (must be completed by the reviewer, not prefilled by execution)

- Reviewer identity / role / authority:
- Review date (UTC):
- Exact commit SHA and evidence bundle hashes reviewed:
- Clause-by-clause findings (G0-A through G0-E):
- Per-population dispositions and evidence links:
- Approved quarantine policy and scope, if any:
- Explicit unresolved items and why they do/do not affect the declared scope:
- Decision: `G0 PASS FOR EXACT DECLARED SCOPE` / `G0 BLOCKED`
- Signature or independently verifiable approval reference:

**No decision is implied until this section is completed by an authorized reviewer and the result is independently verified.**

## Execution boundary

This packet prepares the shortest review handoff; it does not authorize production candidate building, acceptance-grade backtesting, strategy promotion, or live signing/broadcast/orders. Exploratory analysis, if run separately under the user's instruction, must remain provisional and must not be represented as G0 clearance.
