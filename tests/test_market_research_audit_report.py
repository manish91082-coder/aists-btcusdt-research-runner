"""Tests for hash-addressed end-to-end research audit reports."""
import copy
import json
import unittest

from aists_brain.research_audit_report import (
    AuditReportError, build_research_audit_report, serialize_research_audit_report,
)


GATES_BLOCKED = {
    "G0": "BLOCKED_GLOBAL",
    "G2": "FAIL_CURRENT_23_CANDIDATES",
    "G3": "BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT",
    "G4": "INSUFFICIENT_EVIDENCE",
    "G6": "NOT_BUILT",
    "G7": "LIVE_BLOCKED",
}
GATES_READY = {**GATES_BLOCKED, "G0": "PASS"}
HEAD = "b10505566fab1c76951a4c1886d9372a2336510c"


def sample_run():
    return {
        "schema_version": "aists.manifest_research_harness.v1",
        "status": "SIMULATED_NOT_VALIDATED",
        "mode": "OFFLINE_RESEARCH_ONLY",
        "data_input": {
            "symbol": "BTCUSDT", "market": "spot", "interval": "5m",
            "csv_sha256": "a" * 64, "manifest_sha256": "b" * 64, "row_count": 3,
        },
        "decision_input": {
            "artifact_sha256": "c" * 64, "brain_version": "test-fixture-v1", "decision_count": 2,
        },
        "simulation": {
            "status": "SIMULATED_NOT_VALIDATED", "event_count": 0,
            "closed_round_trip_count": 0, "closed_round_trips": [],
            "events": [], "skipped_decisions": [
                {"decision_id": "d-gap", "reason": "NO_NEXT_CONTIGUOUS_BAR", "is_order_instruction": False}
            ],
        },
        "accounting_reconciliation": {"status": "PASS_ACCOUNTING_RECONCILIATION"},
        "paper_ledger_integrity": {"status": "PASS_HASH_CHAIN"},
        "limitations": ["Synthetic test fixture only; no market-performance evidence."],
    }


class ResearchAuditReportTests(unittest.TestCase):
    def test_blocked_gate_report_has_no_run_or_input_hashes(self):
        report = build_research_audit_report(
            gate_snapshot=GATES_BLOCKED, run_id="cp0134-blocked-test", repository_head_sha=HEAD,
        )
        self.assertEqual(report["status"], "BLOCKED_GATE")
        self.assertIsNone(report["run"])
        self.assertEqual(report["input_hashes"], {})
        self.assertEqual(report["controls"]["live_signing"], "BLOCKED")
        self.assertEqual(report["controls"]["exchange_orders"], "BLOCKED")
        self.assertEqual(report["report_sha256"].__len__(), 64)
        self.assertEqual(json.loads(serialize_research_audit_report(report))["status"], "BLOCKED_GATE")

    def test_run_report_preserves_hashes_events_and_skipped_decisions(self):
        report = build_research_audit_report(
            gate_snapshot=GATES_READY, run_result=sample_run(),
            run_id="cp0134-synthetic-fixture", repository_head_sha=HEAD,
        )
        self.assertEqual(report["status"], "SIMULATED_NOT_VALIDATED")
        self.assertEqual(report["input_hashes"]["candle_csv_sha256"], "a" * 64)
        self.assertEqual(report["run"]["brain_version"], "test-fixture-v1")
        self.assertEqual(report["skipped_decisions"][0]["reason"], "NO_NEXT_CONTIGUOUS_BAR")
        self.assertIn("not a profitability claim", report["interpretation"])
        self.assertIn("report_sha256", json.loads(serialize_research_audit_report(report)))

    def test_blocked_g0_cannot_attach_simulation(self):
        with self.assertRaisesRegex(AuditReportError, "G0 is not PASS"):
            build_research_audit_report(
                gate_snapshot=GATES_BLOCKED, run_result=sample_run(),
                run_id="blocked-with-run", repository_head_sha=HEAD,
            )

    def test_acceptance_or_live_status_cannot_be_smuggled_into_report(self):
        altered = sample_run()
        altered["status"] = "ACCEPTED_PROFITABLE"
        with self.assertRaisesRegex(AuditReportError, "SIMULATED_NOT_VALIDATED"):
            build_research_audit_report(
                gate_snapshot=GATES_READY, run_result=altered,
                run_id="bad-status", repository_head_sha=HEAD,
            )

    def test_reconciliation_and_ledger_must_pass(self):
        altered = sample_run()
        altered["accounting_reconciliation"]["status"] = "FAIL"
        with self.assertRaisesRegex(AuditReportError, "reconciliation"):
            build_research_audit_report(
                gate_snapshot=GATES_READY, run_result=altered,
                run_id="bad-accounting", repository_head_sha=HEAD,
            )

    def test_report_tampering_is_detected(self):
        report = build_research_audit_report(
            gate_snapshot=GATES_BLOCKED, run_id="tamper-test", repository_head_sha=HEAD,
        )
        report["interpretation"] = "profitable"
        with self.assertRaisesRegex(AuditReportError, "hash mismatch"):
            serialize_research_audit_report(report)

    def test_missing_gate_and_invalid_sha_are_rejected(self):
        with self.assertRaisesRegex(AuditReportError, "missing gate states"):
            build_research_audit_report(
                gate_snapshot={"G0": "BLOCKED_GLOBAL"}, run_id="missing", repository_head_sha=HEAD,
            )
        with self.assertRaisesRegex(AuditReportError, "40-character git SHA"):
            build_research_audit_report(
                gate_snapshot=GATES_BLOCKED, run_id="bad-sha", repository_head_sha="123",
            )


    def test_simulation_event_count_mismatch_is_rejected(self):
        altered = sample_run()
        altered["simulation"]["event_count"] = 1
        with self.assertRaisesRegex(AuditReportError, "event_count does not match"):
            build_research_audit_report(
                gate_snapshot=GATES_READY, run_result=altered,
                run_id="bad-event-count", repository_head_sha=HEAD,
            )

    def test_simulation_round_trip_count_mismatch_is_rejected(self):
        altered = sample_run()
        altered["simulation"]["closed_round_trip_count"] = 1
        with self.assertRaisesRegex(AuditReportError, "closed_round_trip_count does not match"):
            build_research_audit_report(
                gate_snapshot=GATES_READY, run_result=altered,
                run_id="bad-round-trip-count", repository_head_sha=HEAD,
            )

    def test_skipped_decision_cannot_be_order_instruction(self):
        altered = sample_run()
        altered["simulation"]["skipped_decisions"][0]["is_order_instruction"] = True
        with self.assertRaisesRegex(AuditReportError, "non-order-instruction"):
            build_research_audit_report(
                gate_snapshot=GATES_READY, run_result=altered,
                run_id="bad-skipped-decision", repository_head_sha=HEAD,
            )



if __name__ == "__main__":
    unittest.main()
