#!/usr/bin/env python3
"""CP-0203 fail-closed gate for the frozen CP-0200/0201 4h gap evidence.

This is an eligibility blocker, not a source adjudicator. The frozen evidence
still says G0=BLOCKED_GLOBAL; therefore this module must raise rather than
allow CP-0026 to build a candidate. It never selects a source or synthesizes bars.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_CP0200_GAP_CSV_SHA256 = "e59c95764d4db76a8a707d07526d44b2b7e3487c534687584bd9936a5742b3bf"
EXPECTED_CP0201_CROSSWALK_CSV_SHA256 = "de8d829f405aa60f83e43744d4c281469fec6acb9bb99cfe6aa8823c8509be56"
EXPECTED_RULEBOOK_SHA256 = "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
EXPECTED_OVERLAP_KEY = ("4h", "1504713600000")
EXPECTED_OVERLAP_CASE = "UNMATCHED-D-4h-1504713600000"
EXPECTED_GAP_KEYS = (
    "1504713600000", "1518062400000", "1518076800000", "1518091200000",
    "1518105600000", "1518120000000", "1518134400000", "1518148800000",
    "1529985600000", "1530000000000", "1530676800000", "1542168000000",
    "1552363200000", "1557892800000", "1557907200000", "1565841600000",
    "1582113600000",
)


class GapPolicyGateError(RuntimeError):
    """Raised whenever frozen gap evidence is absent, inconsistent, or unresolved."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GapPolicyGateError(message)


def validate_gap_evidence(gap_rows: list[dict[str, str]], gap_summary: dict,
                          crosswalk_rows: list[dict[str, str]], crosswalk_summary: dict) -> dict:
    """Validate exact identity/counts and preserve unresolved state; never grants eligibility."""
    _require(len(gap_rows) == 17, "G0_BLOCKED_GAP_ROW_COUNT: expected 17")
    _require(len(crosswalk_rows) == 17, "G0_BLOCKED_CROSSWALK_ROW_COUNT: expected 17")
    _require(gap_summary.get("checkpoint") == "CP-0200", "G0_BLOCKED_GAP_SUMMARY_IDENTITY")
    _require(gap_summary.get("task") == "frozen_rulebook_bound_gap_disposition", "G0_BLOCKED_GAP_SUMMARY_TASK")
    _require(gap_summary.get("status") == "BLOCKED_G0_UNRESOLVED_GAP_AND_SOURCE_ITEMS", "G0_BLOCKED_GAP_SUMMARY_STATUS")
    _require(gap_summary.get("rulebook_sha256") == EXPECTED_RULEBOOK_SHA256, "G0_BLOCKED_RULEBOOK_SHA256")
    _require(gap_summary.get("expected_missing_4h_slots_dispositioned") == 17, "G0_BLOCKED_GAP_SUMMARY_COUNT")
    _require(gap_summary.get("missing_keys_absent_from_both_verified_archives") == 16, "G0_BLOCKED_GAP_MISSING_BOTH_COUNT")
    _require(gap_summary.get("unresolved_source_or_placeholder_conflicts") == 1, "G0_BLOCKED_GAP_CONFLICT_COUNT")
    _require(gap_summary.get("canonical_source") == "NONE" and gap_summary.get("g0") == "BLOCKED_GLOBAL",
             "G0_BLOCKED_GAP_SOURCE_OR_GATE_STATE")
    _require(gap_summary.get("candidate_build") is False and gap_summary.get("backtest_run") is False,
             "G0_BLOCKED_GAP_UNSAFE_EXECUTION_FLAG")
    _require(gap_summary.get("quarantine_applied_to_candidate_builder") is False,
             "G0_BLOCKED_GAP_QUARANTINE_ALREADY_APPLIED_FLAG_MISMATCH")
    _require(gap_summary.get("source_cases_closed") == 0 and gap_summary.get("live_signing_broadcast_orders") == "BLOCKED",
             "G0_BLOCKED_GAP_SAFETY_FLAG_MISMATCH")

    gap_by_key = {}
    for row in gap_rows:
        iso = row.get("expected_open_time_utc", "")
        try:
            parsed = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            _require(parsed.tzinfo is not None, "G0_BLOCKED_GAP_TIMEZONE_MISSING")
            open_ms = str(int(parsed.timestamp() * 1000))
        except (TypeError, ValueError, OverflowError) as exc:
            raise GapPolicyGateError(f"G0_BLOCKED_GAP_TIMESTAMP_INVALID: {iso!r}") from exc
        _require(open_ms not in gap_by_key, "G0_BLOCKED_GAP_DUPLICATE_KEY")
        _require(row.get("g0_disposition") in {
            "UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT",
            "UNRESOLVED_MISSING_KEY_BOTH_SOURCES",
        }, "G0_BLOCKED_GAP_DISPOSITION_UNKNOWN")
        _require(row.get("canonical_source") == "NONE" and row.get("source_case_closed") == "False",
                 "G0_BLOCKED_GAP_SOURCE_CLOSED_OR_SELECTED")
        _require(row.get("g0_eligible") == "False", "G0_BLOCKED_GAP_ITEM_MARKED_ELIGIBLE")
        _require(row.get("quarantine_status") == "RECOMMENDED_NOT_APPLIED_TO_CANDIDATE_BUILDER",
                 "G0_BLOCKED_GAP_QUARANTINE_STATUS_MISMATCH")
        gap_by_key[open_ms] = row

    _require(tuple(sorted(gap_by_key)) == tuple(sorted(EXPECTED_GAP_KEYS)), "G0_BLOCKED_GAP_EXACT_KEY_SET_MISMATCH")
    _require(sum(r["g0_disposition"] == "UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT" for r in gap_by_key.values()) == 1,
             "G0_BLOCKED_GAP_PLACEHOLDER_CLASS_COUNT")
    _require(sum(r["g0_disposition"] == "UNRESOLVED_MISSING_KEY_BOTH_SOURCES" for r in gap_by_key.values()) == 16,
             "G0_BLOCKED_GAP_MISSING_CLASS_COUNT")

    _require(crosswalk_summary.get("checkpoint") == "CP-0201", "G0_BLOCKED_CROSSWALK_SUMMARY_IDENTITY")
    _require(crosswalk_summary.get("task") == "gap_quarantine_overlap_crosswalk", "G0_BLOCKED_CROSSWALK_SUMMARY_TASK")
    _require(crosswalk_summary.get("status") == "PASS_EXACT_KEY_CROSSWALK_COMPLETE_G0_STILL_BLOCKED",
             "G0_BLOCKED_CROSSWALK_SUMMARY_STATUS")
    _require(crosswalk_summary.get("gap_dispositions_crosswalked") == 17, "G0_BLOCKED_CROSSWALK_SUMMARY_COUNT")
    _require(crosswalk_summary.get("overlaps_with_any_existing_row_ledger") == 1
             and crosswalk_summary.get("overlaps_with_cp0040_exact_key_quarantine_manifest") == 1,
             "G0_BLOCKED_CROSSWALK_OVERLAP_COUNT")
    _require(crosswalk_summary.get("gap_window_only_items_not_row_cases") == 16, "G0_BLOCKED_CROSSWALK_GAP_ONLY_COUNT")
    _require(crosswalk_summary.get("duplicate_cases_created") == 0
             and crosswalk_summary.get("quarantine_applied_to_candidate_builder") is False,
             "G0_BLOCKED_CROSSWALK_MUTATION_FLAG")
    _require(crosswalk_summary.get("canonical_source") == "NONE" and crosswalk_summary.get("g0") == "BLOCKED_GLOBAL",
             "G0_BLOCKED_CROSSWALK_SOURCE_OR_GATE_STATE")
    _require(crosswalk_summary.get("source_cases_closed") == 0 and crosswalk_summary.get("live_signing_broadcast_orders") == "BLOCKED",
             "G0_BLOCKED_CROSSWALK_SAFETY_FLAG")

    cross_by_key = {}
    for row in crosswalk_rows:
        _require(row.get("interval") == "4h", "G0_BLOCKED_CROSSWALK_INTERVAL")
        key = row.get("open_time_ms", "")
        _require(key in EXPECTED_GAP_KEYS and key not in cross_by_key, "G0_BLOCKED_CROSSWALK_KEY_SET_OR_DUPLICATE")
        _require(row.get("canonical_source") == "NONE" and row.get("source_case_closed") == "False",
                 "G0_BLOCKED_CROSSWALK_SOURCE_CLOSED_OR_SELECTED")
        _require(row.get("duplicate_case_created") == "False"
                 and row.get("quarantine_applied_to_candidate_builder") == "False",
                 "G0_BLOCKED_CROSSWALK_QUARANTINE_OR_DUPLICATE_FLAG")
        _require(row.get("cp0200_g0_disposition") == gap_by_key[key]["g0_disposition"],
                 "G0_BLOCKED_CROSSWALK_DISPOSITION_MISMATCH")
        if key == EXPECTED_OVERLAP_KEY[1]:
            _require(row.get("existing_case_ids") == EXPECTED_OVERLAP_CASE,
                     "G0_BLOCKED_EXPECTED_EXISTING_CASE_LINK_MISMATCH")
            _require(row.get("gap_crosswalk_disposition") == "OVERLAPS_EXISTING_ROW_LEVEL_CASE_DO_NOT_DUPLICATE",
                     "G0_BLOCKED_EXPECTED_OVERLAP_DISPOSITION_MISMATCH")
        else:
            _require(row.get("existing_ledger_match_count") == "0"
                     and row.get("gap_crosswalk_disposition") == "GAP_WINDOW_ONLY_NO_ROW_CASE_IN_INSPECTED_LEDGERS",
                     "G0_BLOCKED_GAP_ONLY_ITEM_MISCLASSIFIED")
        cross_by_key[key] = row
    _require(set(cross_by_key) == set(gap_by_key), "G0_BLOCKED_CROSSWALK_GAP_KEY_SET_MISMATCH")

    return {
        "status": "BLOCKED_G0_UNRESOLVED_GAP_AND_SOURCE_ITEMS",
        "gap_items": 17,
        "gap_window_only_items": 16,
        "existing_row_case_overlap": 1,
        "canonical_source": "NONE",
        "candidate_eligibility": "BLOCKED",
    }


def load_gap_policy_gate(gap_manifest_path: str | Path, gap_summary_path: str | Path,
                         crosswalk_path: str | Path, crosswalk_summary_path: str | Path) -> dict:
    paths = {
        "gap manifest": Path(gap_manifest_path),
        "gap summary": Path(gap_summary_path),
        "crosswalk": Path(crosswalk_path),
        "crosswalk summary": Path(crosswalk_summary_path),
    }
    for label, path in paths.items():
        if not path.is_file():
            raise GapPolicyGateError(f"G0_BLOCKED_GAP_POLICY_FILE_MISSING: {label}: {path}")
    actual_gap_sha = sha256_file(paths["gap manifest"])
    actual_cross_sha = sha256_file(paths["crosswalk"])
    _require(actual_gap_sha == EXPECTED_CP0200_GAP_CSV_SHA256,
             f"G0_BLOCKED_GAP_MANIFEST_SHA256_MISMATCH: {actual_gap_sha}")
    _require(actual_cross_sha == EXPECTED_CP0201_CROSSWALK_CSV_SHA256,
             f"G0_BLOCKED_GAP_CROSSWALK_SHA256_MISMATCH: {actual_cross_sha}")
    try:
        gap_summary = json.loads(paths["gap summary"].read_text(encoding="utf-8"))
        cross_summary = json.loads(paths["crosswalk summary"].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GapPolicyGateError(f"G0_BLOCKED_GAP_SUMMARY_INVALID: {exc}") from exc
    result = validate_gap_evidence(
        read_csv(paths["gap manifest"]), gap_summary,
        read_csv(paths["crosswalk"]), cross_summary,
    )
    # This frozen evidence explicitly says the recommended policy has not been applied.
    # Never return eligibility PASS until a new reviewed policy artifact supersedes it.
    raise GapPolicyGateError(
        "G0_BLOCKED_GAP_POLICY_UNRESOLVED: validated CP-0200/0201 evidence "
        f"({result['gap_items']} items; {result['gap_window_only_items']} gap-only; "
        f"{result['existing_row_case_overlap']} existing row-case overlap); "
        "no candidate build/backtest permitted"
    )
