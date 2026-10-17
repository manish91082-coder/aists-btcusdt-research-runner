"""Tests for independent structural verification of AISTS audit reports."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aists_brain.research_audit_report import build_research_audit_report, serialize_research_audit_report
from aists_brain.research_report_verifier import (
    ResearchReportVerificationError,
    verify_research_audit_report,
    verify_serialized_research_audit_report,
)

HEAD = "2e0570e654541562e76148ae8af217a4adcad12c"
GATES_BLOCKED = {
    "G0": "BLOCKED_GLOBAL",
    "G2": "FAIL_CURRENT_23_CANDIDATES",
    "G3": "BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT",
    "G4": "INSUFFICIENT_EVIDENCE",
    "G6": "NOT_BUILT",
    "G7": "LIVE_BLOCKED",
}


class ResearchReportVerifierTests(unittest.TestCase):
    def blocked_report(self):
        return build_research_audit_report(
            gate_snapshot=GATES_BLOCKED,
            run_id="cp0140-test",
            repository_head_sha=HEAD,
        )

    def test_valid_blocked_report_passes_structural_verification(self):
        report = self.blocked_report()
        result = verify_research_audit_report(
            report, expected_repository_head_sha=HEAD, expected_run_id="cp0140-test"
        )
        self.assertEqual(result["status"], "PASS_STRUCTURAL_INTEGRITY")
        self.assertEqual(result["gate_g0"], "BLOCKED_GLOBAL")
        self.assertEqual(result["report_status"], "BLOCKED_GATE")

    def test_report_tampering_is_detected(self):
        report = self.blocked_report()
        report["interpretation"] = "Claim of profitability"
        with self.assertRaisesRegex(ResearchReportVerificationError, "SHA-256 mismatch"):
            verify_research_audit_report(report)

    def test_repository_head_or_run_id_mismatch_is_detected(self):
        report = self.blocked_report()
        with self.assertRaisesRegex(ResearchReportVerificationError, "head binding mismatch"):
            verify_research_audit_report(report, expected_repository_head_sha="a" * 40)
        with self.assertRaisesRegex(ResearchReportVerificationError, "run_id binding mismatch"):
            verify_research_audit_report(report, expected_run_id="another-run")

    def test_blocked_g0_cannot_claim_simulation(self):
        report = self.blocked_report()
        report["status"] = "SIMULATED_NOT_VALIDATED"
        unsigned = dict(report)
        unsigned.pop("report_sha256")
        report["report_sha256"] = hashlib.sha256(json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")).hexdigest()
        with self.assertRaisesRegex(ResearchReportVerificationError, "blocked G0"):
            verify_research_audit_report(report)

    def test_safety_controls_cannot_be_weakened(self):
        report = self.blocked_report()
        report["controls"]["exchange_orders"] = "ENABLED"
        unsigned = dict(report)
        unsigned.pop("report_sha256")
        report["report_sha256"] = hashlib.sha256(json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")).hexdigest()
        with self.assertRaisesRegex(ResearchReportVerificationError, "safety control"):
            verify_research_audit_report(report)

    def test_simulated_report_nested_event_count_is_reconciled(self):
        gates_ready = {**GATES_BLOCKED, "G0": "PASS"}
        run = {
            "status": "SIMULATED_NOT_VALIDATED",
            "mode": "OFFLINE_RESEARCH_ONLY",
            "data_input": {"symbol": "BTCUSDT", "market": "spot", "interval": "5m",
                           "csv_sha256": "a" * 64, "manifest_sha256": "b" * 64, "row_count": 3},
            "decision_input": {"artifact_sha256": "c" * 64, "brain_version": "fixture-v1", "decision_count": 0},
            "simulation": {"status": "SIMULATED_NOT_VALIDATED", "event_count": 0, "events": [],
                           "closed_round_trip_count": 0, "closed_round_trips": [], "skipped_decisions": []},
            "accounting_reconciliation": {"status": "PASS_ACCOUNTING_RECONCILIATION", "event_count": 0},
            "paper_ledger_integrity": {"status": "PASS_HASH_CHAIN"},
            "limitations": ["Synthetic fixture only"],
        }
        report = build_research_audit_report(
            gate_snapshot=gates_ready, run_result=run,
            run_id="cp0175-forged-nested-summary", repository_head_sha=HEAD,
        )
        report["run"]["simulation"]["event_count"] = 1
        unsigned = dict(report)
        unsigned.pop("report_sha256")
        report["report_sha256"] = hashlib.sha256(json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")).hexdigest()
        with self.assertRaisesRegex(ResearchReportVerificationError, "nested simulation event count mismatch"):
            verify_research_audit_report(report)

    def test_serialized_report_verifies_file_hash_and_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "audit.json"
            report = self.blocked_report()
            path.write_text(serialize_research_audit_report(report), encoding="utf-8")
            result = verify_serialized_research_audit_report(
                path, expected_repository_head_sha=HEAD
            )
            self.assertEqual(result["status"], "PASS_STRUCTURAL_INTEGRITY")
            self.assertEqual(result["serialized_file_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
