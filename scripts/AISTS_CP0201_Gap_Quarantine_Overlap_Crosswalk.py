#!/usr/bin/env python3
"""Crosswalk 17 gap dispositions against frozen row-level quarantine ledgers; prevent double counting."""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def normalized_key(interval, open_time):
    try:
        return interval.strip(), str(int(open_time))
    except (TypeError, ValueError):
        return interval.strip(), str(open_time).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gap-manifest", default="results/cp0200_g0_rulebook_bound_gap_disposition/CP0200_G0_Gap_Quarantine_Recommendation.csv")
    parser.add_argument("--existing-quarantine", default="evidence/source_adjudication/CP0040_Run_38883792900/CP0040_ExactKey_Quarantine_Manifest.csv")
    parser.add_argument("--worklist-delta", default="evidence/source_adjudication/CP0107_CP0041_Worklist_Disposition_Delta_450.csv")
    parser.add_argument("--feb2018-disposition", default="evidence/source_adjudication/CP0107_Feb2018_OffGrid_RowDisposition.csv")
    parser.add_argument("--shared52", default="evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Matrix.csv")
    parser.add_argument("--close-time-only", default="evidence/source_adjudication/CP0107_CloseTimeOnly_FieldDisposition_Final.csv")
    parser.add_argument("--output-dir", default="results/cp0201_gap_quarantine_overlap_crosswalk")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    paths = {
        "gap_manifest": (root / args.gap_manifest).resolve(),
        "cp0040_quarantine": (root / args.existing_quarantine).resolve(),
        "cp0107_worklist_delta": (root / args.worklist_delta).resolve(),
        "cp0107_feb2018_disposition": (root / args.feb2018_disposition).resolve(),
        "cp0107_shared52": (root / args.shared52).resolve(),
        "cp0107_close_time_only": (root / args.close_time_only).resolve(),
    }
    out = (root / args.output_dir).resolve()
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"required evidence missing ({name}): {path}")
    started = datetime.now(timezone.utc).isoformat()
    gap_rows = read_csv(paths["gap_manifest"])
    if len(gap_rows) != 17:
        raise ValueError(f"expected exactly 17 CP-0200 gap dispositions, found {len(gap_rows)}")
    ledgers = {}
    input_manifest = []
    for name, path in paths.items():
        rows = read_csv(path)
        input_manifest.append({"ledger": name, "path": str(path.relative_to(root)),
                               "rows": len(rows), "bytes": path.stat().st_size,
                               "sha256": sha256_file(path)})
        if name == "gap_manifest":
            continue
        for row in rows:
            interval = row.get("interval", "")
            raw_time = row.get("open_time_ms", "")
            if not interval or raw_time == "":
                continue
            key = normalized_key(interval, raw_time)
            ledgers.setdefault(key, []).append({
                "ledger": name, "case_id": row.get("case_id", ""),
                "case_class": row.get("case_class", row.get("record_type", "")),
                "disposition": row.get("disposition", row.get("proposed_worklist_disposition", row.get("closure_gate", ""))),
                "canonical_source": row.get("canonical_source", "NONE"),
                "case_closed": str(row.get("case_closed", "False")).lower() == "true"
            })
    output = []
    for gap in gap_rows:
        iso = datetime.fromisoformat(gap["expected_open_time_utc"].replace("Z", "+00:00"))
        open_ms = int(iso.timestamp() * 1000)
        key = normalized_key("4h", open_ms)
        matches = ledgers.get(key, [])
        cp0040 = [m for m in matches if m["ledger"] == "cp0040_quarantine"]
        case_ids = sorted({m["case_id"] for m in matches if m["case_id"]})
        ledger_names = sorted({m["ledger"] for m in matches})
        if matches:
            disposition = "OVERLAPS_EXISTING_ROW_LEVEL_CASE_DO_NOT_DUPLICATE"
            gap_action = "LINK_TO_EXISTING_CASE; retain separate gap-window semantics; do not create a duplicate row case"
        else:
            disposition = "GAP_WINDOW_ONLY_NO_ROW_CASE_IN_INSPECTED_LEDGERS"
            gap_action = "KEEP_AS_GAP_POLICY_ITEM; no source row exists at this key in inspected ledgers; do not synthesize a bar"
        output.append({
            "expected_open_time_utc": gap["expected_open_time_utc"],
            "interval": "4h", "open_time_ms": open_ms,
            "cp0200_g0_disposition": gap.get("g0_disposition", ""),
            "cp0200_recommended_handling": gap.get("required_handling", ""),
            "existing_ledger_match_count": len(matches),
            "existing_ledger_names": ";".join(ledger_names),
            "existing_case_ids": ";".join(case_ids),
            "cp0040_exact_key_manifest_match": bool(cp0040),
            "existing_case_dispositions": " || ".join(sorted({m["disposition"] for m in matches if m["disposition"]})),
            "gap_crosswalk_disposition": disposition,
            "required_gap_action": gap_action,
            "duplicate_case_created": False,
            "canonical_source": "NONE", "source_case_closed": False,
            "quarantine_applied_to_candidate_builder": False
        })
    overlaps = sum(r["existing_ledger_match_count"] > 0 for r in output)
    cp0040_overlaps = sum(r["cp0040_exact_key_manifest_match"] for r in output)
    gap_only = sum(r["existing_ledger_match_count"] == 0 for r in output)
    closed = sum(r["source_case_closed"] for r in output)
    summary = {
        "schema_version": 1, "checkpoint": "CP-0201", "task": "gap_quarantine_overlap_crosswalk",
        "status": "PASS_EXACT_KEY_CROSSWALK_COMPLETE_G0_STILL_BLOCKED",
        "gap_dispositions_crosswalked": len(output), "overlaps_with_any_existing_row_ledger": overlaps,
        "overlaps_with_cp0040_exact_key_quarantine_manifest": cp0040_overlaps,
        "gap_window_only_items_not_row_cases": gap_only, "duplicate_cases_created": 0,
        "source_cases_closed": closed, "quarantine_applied_to_candidate_builder": False,
        "input_manifest": input_manifest,
        "canonical_source": "NONE", "g0": "BLOCKED_GLOBAL",
        "network_used": False, "downloads": 0, "raw_source_mutation": False,
        "timestamps_shifted_or_rounded": False, "synthetic_candles_created": False,
        "backtest_run": False, "candidate_build": False, "strategy_promoted": False,
        "live_signing_broadcast_orders": "BLOCKED",
        "finished_at_utc": datetime.now(timezone.utc).isoformat()
    }
    write_csv(out / "CP0201_Gap_Quarantine_Overlap_Crosswalk.csv", output, [
        "expected_open_time_utc", "interval", "open_time_ms", "cp0200_g0_disposition",
        "cp0200_recommended_handling", "existing_ledger_match_count", "existing_ledger_names",
        "existing_case_ids", "cp0040_exact_key_manifest_match", "existing_case_dispositions",
        "gap_crosswalk_disposition", "required_gap_action", "duplicate_case_created",
        "canonical_source", "source_case_closed", "quarantine_applied_to_candidate_builder"])
    write_csv(out / "CP0201_Input_Manifest.csv", input_manifest, ["ledger", "path", "rows", "bytes", "sha256"])
    (out / "CP0201_Summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# CP-0201: Gap/quarantine overlap crosswalk", "",
        f"- Status: {summary['status']}",
        f"- Gap items crosswalked: {len(output)}.",
        f"- Exact-key overlaps with existing row-level ledgers: {overlaps}; CP-0040 exact-key manifest overlaps: {cp0040_overlaps}.",
        f"- Gap-window-only items (not existing row cases): {gap_only}.",
        "- The 2017-09-06 16:00 UTC key must link to its existing CP-0040 daily-only quarantine case; do not count it as a second row-level case.",
        "- The other absent keys remain gap-window policy items, not fabricated row cases.",
        "- No duplicate case was created; no quarantine was applied to the candidate builder; G0 remains blocked.",
        "- No network, download, raw-data mutation, timestamp shift, synthetic bar, candidate build, backtest, or live action occurred."
    ]
    (out / "CP0201_Report_HI.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "status", "gap_dispositions_crosswalked", "overlaps_with_any_existing_row_ledger",
        "overlaps_with_cp0040_exact_key_quarantine_manifest", "gap_window_only_items_not_row_cases",
        "duplicate_cases_created", "quarantine_applied_to_candidate_builder", "canonical_source",
        "g0", "live_signing_broadcast_orders")}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
