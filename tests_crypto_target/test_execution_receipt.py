import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "write_execution_receipt.py"
SPEC = importlib.util.spec_from_file_location("write_execution_receipt", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExecutionReceiptTests(unittest.TestCase):
    def test_receipt_only_reads_allowlisted_metadata_and_never_serializes_environment(self):
        env = {
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_WORKFLOW": "smoke",
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_RUN_ID": "123",
            "GITHUB_RUN_ATTEMPT": "2",
            "GITHUB_JOB": "unit-tests",
            "GITHUB_SHA": "abc123",
            "INPUT_MONTH": "2026-09",
            "RECEIPT_STATUS": "PASS",
            "SUPABASE_SERVICE_ROLE_KEY": "NEVER_LOG_THIS_SECRET",
            "GITHUB_TOKEN": "NEVER_LOG_THIS_TOKEN",
        }
        with patch.dict(os.environ, env, clear=True):
            receipt = MODULE.build_receipt()
        serialized = json.dumps(receipt)
        self.assertEqual(receipt["repository"], "owner/repo")
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["inputs"]["month"], "2026-09")
        self.assertFalse(receipt["secret_values_recorded"])
        self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY", serialized)
        self.assertNotIn("NEVER_LOG_THIS_SECRET", serialized)
        self.assertNotIn("NEVER_LOG_THIS_TOKEN", serialized)

    def test_main_writes_json_and_markdown_receipts(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"RECEIPT_STATUS": "FAIL", "GITHUB_RUN_ID": "456"}, clear=True
        ):
            with patch("sys.argv", ["write_execution_receipt.py", "--output-dir", tmp]):
                self.assertEqual(MODULE.main(), 0)
            data = json.loads((Path(tmp) / "execution-receipt.json").read_text())
            markdown = (Path(tmp) / "execution-receipt.md").read_text()
            self.assertEqual(data["status"], "FAIL")
            self.assertEqual(data["run_id"], "456")
            self.assertIn("Secret values recorded: **no**", markdown)


if __name__ == "__main__":
    unittest.main()
