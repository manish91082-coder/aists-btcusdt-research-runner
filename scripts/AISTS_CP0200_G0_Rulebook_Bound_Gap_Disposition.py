#!/usr/bin/env python3
"""Apply the frozen CP-0040 G0 rulebook to CP-0199 exact-key and missing-gap evidence."""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_RULEBOOK_SHA256 = "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
EXPECTED_RULEBOOK_BYTES = 10630

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conflict-matrix", default="results/cp0199_exact_key_source_conflict_probe/CP0199_ExactKey_SourceConflict_Matrix.csv")
    parser.add_argument("--rulebook", default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
    parser.add_argument("--rulebook-receipt", default="evidence/source_adjudication/CP0040_Original_Rulebook_Verification_Receipt.json")
    parser.add_argument("--output-dir", default="results/cp0200_g0_rulebook_bound_gap_disposition")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    matrix_path = (root / args.conflict_matrix).resolve()
    rulebook_path = (root / args.rulebook).resolve()
    receipt_path = (root / args.rulebook_receipt).resolve()
    out = (root / args.output_dir).resolve()
    for path in (matrix_path, rulebook_path, receipt_path):
        if not path.is_file():
            raise FileNotFoundError(f"required frozen input missing: {path}")
    rulebook_sha = sha256_file(rulebook_path)
    rulebook_bytes = rulebook_path.stat().st_size
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt_rulebook = receipt.get("rulebook", {})
    if not (rulebook_sha == EXPECTED_RULEBOOK_SHA256 == receipt_rulebook.get("sha256")
            and rulebook_bytes == EXPECTED_RULEBOOK_BYTES == receipt_rulebook.get("bytes")):
        raise ValueError("frozen CP-0040 rulebook hash/byte verification failed")
    rows = read_csv(matrix_path)
    dispositions = []
    for source in rows:
        monthly = source.get("monthly_exact_open_key_present", "UNKNOWN")
        daily = source.get("daily_exact_open_key_present", "UNKNOWN")
        disposition = source.get("disposition", "")
        if monthly == "UNKNOWN" or daily == "UNKNOWN" or "UNRESOLVED" in disposition:
            status = "UNRESOLVED_ARCHIVE_EVIDENCE_UNAVAILABLE"
            handling = "HOLD_FROM_SIGNAL_POSITION_VALUATION; resolve archive evidence or quarantine the affected window"
        elif "ZERO_TRADE_PLACEHOLDER" in disposition or "CLOSE_TIME_ANOMALY" in disposition:
            status = "UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT"
            handling = "DO_NOT_TREAT_AS_VALID_CANDLE; preserve raw tokens; quarantine exact key until source adjudication"
        elif "SOURCE_CONFLICT" in disposition or monthly != daily:
            status = "UNRESOLVED_CROSS_SOURCE_EXACT_KEY_CONFLICT"
            handling = "DO_NOT_SELECT_MONTHLY_OR_DAILY; exact-key quarantine required before candidate input"
        elif monthly == "NO" and daily == "NO":
            status = "UNRESOLVED_MISSING_KEY_BOTH_SOURCES"
            handling = "DO_NOT_SYNTHESIZE_BAR; record gap and apply frozen gap-window quarantine policy"
        else:
            status = "UNRESOLVED_REQUIRES_RULEBOOK_REVIEW"
            handling = "KEEP OUT OF PROMOTION; retain raw evidence and require explicit source disposition"
        dispositions.append({
            "expected_open_time_utc": source.get("expected_open_time_utc", ""),
            "date_utc": source.get("date_utc", ""),
            "monthly_exact_open_key_present": monthly,
            "daily_exact_open_key_present": daily,
            "source_probe_disposition": disposition,
            "g0_disposition": status,
            "required_handling": handling,
            "quarantine_status": "RECOMMENDED_NOT_APPLIED_TO_CANDIDATE_BUILDER",
            "canonical_source": "NONE",
            "source_case_closed": False,
            "g0_eligible": False
        })
    source_conflicts = sum("CROSS_SOURCE" in r["g0_disposition"] or "PLACEHOLDER" in r["g0_disposition"] for r in dispositions)
    missing_both = sum(r["g0_disposition"] == "UNRESOLVED_MISSING_KEY_BOTH_SOURCES" for r in dispositions)
    unavailable = sum(r["g0_disposition"] == "UNRESOLVED_ARCHIVE_EVIDENCE_UNAVAILABLE" for r in dispositions)
    summary = {
        "schema_version": 1, "checkpoint": "CP-0200", "task": "frozen_rulebook_bound_gap_disposition",
        "status": "BLOCKED_G0_UNRESOLVED_GAP_AND_SOURCE_ITEMS",
        "rulebook_sha256": rulebook_sha, "rulebook_bytes": rulebook_bytes,
        "rulebook_receipt_sha256": sha256_file(receipt_path),
        "conflict_matrix_sha256": sha256_file(matrix_path),
        "expected_missing_4h_slots_dispositioned": len(dispositions),
        "unresolved_source_or_placeholder_conflicts": source_conflicts,
        "missing_keys_absent_from_both_verified_archives": missing_both,
        "archive_evidence_unavailable": unavailable,
        "quarantine_manifest_created": True, "quarantine_applied_to_candidate_builder": False,
        "canonical_source": "NONE", "source_cases_closed": 0, "g0": "BLOCKED_GLOBAL",
        "backtest_run": False, "candidate_build": False, "strategy_promoted": False,
        "network_used": False, "downloads": 0, "raw_source_mutation": False,
        "timestamps_shifted_or_rounded": False, "synthetic_candles_created": False,
        "live_signing_broadcast_orders": "BLOCKED",
        "finished_at_utc": datetime.now(timezone.utc).isoformat()
    }
    write_csv(out / "CP0200_G0_Gap_Quarantine_Recommendation.csv", dispositions, [
        "expected_open_time_utc", "date_utc", "monthly_exact_open_key_present",
        "daily_exact_open_key_present", "source_probe_disposition", "g0_disposition",
        "required_handling", "quarantine_status", "canonical_source", "source_case_closed", "g0_eligible"])
    (out / "CP0200_Summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# CP-0200: Frozen-rulebook-bound G0 gap disposition", "",
        f"- Status: {summary['status']}",
        f"- Frozen rulebook SHA-256/bytes: {rulebook_sha} / {rulebook_bytes}; exact receipt match PASS.",
        f"- 4h missing slots dispositioned: {len(dispositions)}.",
        f"- Source/placeholder conflicts: {source_conflicts}; keys absent from both verified archives: {missing_both}; unavailable archive evidence: {unavailable}.",
        "- The row-level gap/quarantine recommendation is evidence only; it has not been applied to the existing candidate builder.",
        "- No canonical source selected and no source case closed. G0 remains globally blocked.",
        "- No network/download, raw-source mutation, timestamp shift, synthetic candle, candidate build, backtest, or live action occurred."
    ]
    (out / "CP0200_Report_HI.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "status", "expected_missing_4h_slots_dispositioned", "unresolved_source_or_placeholder_conflicts",
        "missing_keys_absent_from_both_verified_archives", "archive_evidence_unavailable",
        "quarantine_manifest_created", "quarantine_applied_to_candidate_builder",
        "canonical_source", "g0", "live_signing_broadcast_orders")}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
