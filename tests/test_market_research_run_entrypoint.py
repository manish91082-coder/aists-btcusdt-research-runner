"""Tests for fail-closed orchestration and deterministic audit publication."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aists_brain.research_audit_report import serialize_research_audit_report
from aists_brain.research_run_entrypoint import (
    ResearchRunEntryPointError,
    run_research_entrypoint,
)


GATES_BLOCKED = {
    "G0": "BLOCKED_GLOBAL",
    "G2": "FAIL_CURRENT_23_CANDIDATES",
    "G3": "BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT",
    "G4": "INSUFFICIENT_EVIDENCE",
    "G6": "NOT_BUILT",
    "G7": "LIVE_BLOCKED",
}
HEAD = "d5f70ca65408b663c5c230ba794067479691353e"


class ResearchRunEntryPointTests(unittest.TestCase):
    def test_blocked_g0_does_not_inspect_paths_or_attempt_simulation(self):
        report = run_research_entrypoint(
            gate_snapshot=GATES_BLOCKED,
            run_id="cp0139-blocked-test",
            repository_head_sha=HEAD,
            csv_path="/path/that/must/not/be/opened.csv",
            manifest_path="/path/that/must/not/be/opened.json",
            stored_artifact_path="/path/that/must/not/be/opened-features.json",
            expected_interval="4h",
            initial_cash_usdt=100.0,
        )
        self.assertEqual(report["status"], "BLOCKED_GATE")
        self.assertEqual(report["entrypoint"]["blocked_reason"], "G0_NOT_PASS")
        self.assertFalse(report["entrypoint"]["input_artifacts_inspected"])
        self.assertFalse(report["entrypoint"]["simulation_attempted"])
        self.assertEqual(report["input_hashes"], {})
        self.assertIsNone(report["run"])
        self.assertEqual(report["gate_snapshot"]["G0"], "BLOCKED_GLOBAL")
        self.assertEqual(serialize_research_audit_report(report).count("report_sha256"), 1)

    def test_blocked_report_is_deterministic_for_same_inputs(self):
        kwargs = dict(
            gate_snapshot=GATES_BLOCKED,
            run_id="cp0139-deterministic",
            repository_head_sha=HEAD,
        )
        first = run_research_entrypoint(**kwargs)
        second = run_research_entrypoint(**kwargs)
        self.assertEqual(first["report_sha256"], second["report_sha256"])
        self.assertEqual(serialize_research_audit_report(first),
                         serialize_research_audit_report(second))

    def test_create_only_report_persistence_and_refusal_to_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "audit.json"
            report = run_research_entrypoint(
                gate_snapshot=GATES_BLOCKED,
                run_id="cp0139-persist",
                repository_head_sha=HEAD,
                report_path=path,
            )
            persisted = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["report_sha256"], report["report_sha256"])
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                report["report_file_sha256"],
            )
            with self.assertRaisesRegex(ResearchRunEntryPointError, "overwrite refused"):
                run_research_entrypoint(
                    gate_snapshot=GATES_BLOCKED,
                    run_id="cp0139-persist-again",
                    repository_head_sha=HEAD,
                    report_path=path,
                )

    def test_missing_gate_state_rejected(self):
        with self.assertRaisesRegex(ResearchRunEntryPointError, "missing gate states"):
            run_research_entrypoint(
                gate_snapshot={"G0": "BLOCKED_GLOBAL"},
                run_id="bad-gates",
                repository_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
