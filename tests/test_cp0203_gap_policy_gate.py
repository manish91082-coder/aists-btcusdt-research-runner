import csv
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0203_GapPolicy_Gate.py"
SPEC = importlib.util.spec_from_file_location("cp0203_gap_gate", SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(GATE)


def fixture_rows():
    gap_rows = []
    cross_rows = []
    for i, token in enumerate(GATE.EXPECTED_GAP_KEYS):
        dt = datetime.fromtimestamp(int(token) / 1000, tz=timezone.utc).isoformat()
        placeholder = token == GATE.EXPECTED_OVERLAP_KEY[1]
        disposition = "UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT" if placeholder else "UNRESOLVED_MISSING_KEY_BOTH_SOURCES"
        gap_rows.append({
            "expected_open_time_utc": dt,
            "g0_disposition": disposition,
            "canonical_source": "NONE",
            "source_case_closed": "False",
            "g0_eligible": "False",
            "quarantine_status": "RECOMMENDED_NOT_APPLIED_TO_CANDIDATE_BUILDER",
        })
        cross_rows.append({
            "interval": "4h",
            "open_time_ms": token,
            "cp0200_g0_disposition": disposition,
            "canonical_source": "NONE",
            "source_case_closed": "False",
            "duplicate_case_created": "False",
            "quarantine_applied_to_candidate_builder": "False",
            "existing_case_ids": GATE.EXPECTED_OVERLAP_CASE if placeholder else "",
            "existing_ledger_match_count": "1" if placeholder else "0",
            "gap_crosswalk_disposition": (
                "OVERLAPS_EXISTING_ROW_LEVEL_CASE_DO_NOT_DUPLICATE" if placeholder
                else "GAP_WINDOW_ONLY_NO_ROW_CASE_IN_INSPECTED_LEDGERS"
            ),
        })
    gap_summary = {
        "checkpoint": "CP-0200",
        "task": "frozen_rulebook_bound_gap_disposition",
        "status": "BLOCKED_G0_UNRESOLVED_GAP_AND_SOURCE_ITEMS",
        "rulebook_sha256": GATE.EXPECTED_RULEBOOK_SHA256,
        "expected_missing_4h_slots_dispositioned": 17,
        "missing_keys_absent_from_both_verified_archives": 16,
        "unresolved_source_or_placeholder_conflicts": 1,
        "canonical_source": "NONE",
        "g0": "BLOCKED_GLOBAL",
        "candidate_build": False,
        "backtest_run": False,
        "quarantine_applied_to_candidate_builder": False,
        "source_cases_closed": 0,
        "live_signing_broadcast_orders": "BLOCKED",
    }
    cross_summary = {
        "checkpoint": "CP-0201",
        "task": "gap_quarantine_overlap_crosswalk",
        "status": "PASS_EXACT_KEY_CROSSWALK_COMPLETE_G0_STILL_BLOCKED",
        "gap_dispositions_crosswalked": 17,
        "overlaps_with_any_existing_row_ledger": 1,
        "overlaps_with_cp0040_exact_key_quarantine_manifest": 1,
        "gap_window_only_items_not_row_cases": 16,
        "duplicate_cases_created": 0,
        "quarantine_applied_to_candidate_builder": False,
        "canonical_source": "NONE",
        "g0": "BLOCKED_GLOBAL",
        "source_cases_closed": 0,
        "live_signing_broadcast_orders": "BLOCKED",
    }
    return gap_rows, gap_summary, cross_rows, cross_summary


class TestCP0203GapPolicyGate(unittest.TestCase):
    def test_frozen_17_key_matrix_preserves_single_overlap_and_16_gap_only(self):
        gap, gs, cross, cs = fixture_rows()
        result = GATE.validate_gap_evidence(gap, gs, cross, cs)
        self.assertEqual(result["status"], "BLOCKED_G0_UNRESOLVED_GAP_AND_SOURCE_ITEMS")
        self.assertEqual(result["gap_items"], 17)
        self.assertEqual(result["gap_window_only_items"], 16)
        self.assertEqual(result["existing_row_case_overlap"], 1)
        self.assertEqual(result["canonical_source"], "NONE")

    def test_missing_gap_key_fails_closed(self):
        gap, gs, cross, cs = fixture_rows()
        with self.assertRaisesRegex(GATE.GapPolicyGateError, "G0_BLOCKED_GAP_ROW_COUNT"):
            GATE.validate_gap_evidence(gap[:-1], gs, cross, cs)

    def test_overlap_must_link_existing_case_without_duplicate(self):
        gap, gs, cross, cs = fixture_rows()
        cross[0]["existing_case_ids"] = "NEW_DUPLICATE_CASE"
        with self.assertRaisesRegex(GATE.GapPolicyGateError, "G0_BLOCKED_EXPECTED_EXISTING_CASE_LINK_MISMATCH"):
            GATE.validate_gap_evidence(gap, gs, cross, cs)

    def test_gap_only_item_cannot_be_misclassified_as_row_case(self):
        gap, gs, cross, cs = fixture_rows()
        cross[1]["existing_ledger_match_count"] = "1"
        with self.assertRaisesRegex(GATE.GapPolicyGateError, "G0_BLOCKED_GAP_ONLY_ITEM_MISCLASSIFIED"):
            GATE.validate_gap_evidence(gap, gs, cross, cs)

    def test_closed_case_or_selected_source_is_rejected(self):
        gap, gs, cross, cs = fixture_rows()
        gap[0]["canonical_source"] = "DAILY"
        with self.assertRaisesRegex(GATE.GapPolicyGateError, "G0_BLOCKED_GAP_SOURCE_CLOSED_OR_SELECTED"):
            GATE.validate_gap_evidence(gap, gs, cross, cs)

    def test_missing_evidence_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(GATE.GapPolicyGateError, "G0_BLOCKED_GAP_POLICY_FILE_MISSING"):
                GATE.load_gap_policy_gate(root / "gap.csv", root / "gap.json", root / "cross.csv", root / "cross.json")

    def test_tampered_manifest_hash_fails_closed_before_parsing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [root / name for name in ("gap.csv", "gap.json", "cross.csv", "cross.json")]
            paths[0].write_text("not,the,frozen,evidence\n", encoding="utf-8")
            for path in paths[1:]:
                path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(GATE.GapPolicyGateError, "G0_BLOCKED_GAP_MANIFEST_SHA256_MISMATCH"):
                GATE.load_gap_policy_gate(*paths)

    def test_candidate_builder_invokes_gate_before_candidate_output(self):
        builder = (Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0026_Research_Candidate_Builder.py").read_text(encoding="utf-8")
        self.assertIn("load_gap_policy_gate", builder)
        call = builder.index("load_gap_policy_gate(")
        old_gate = builder.index("load_candidate_gate(", call)
        output = builder.index('outdir=CANDIDATE_ROOT/"intervals"', call)
        self.assertLess(call, old_gate)
        self.assertLess(call, output)


if __name__ == "__main__":
    unittest.main()
