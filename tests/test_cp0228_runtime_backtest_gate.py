"""CP-0228 runtime fail-closed check for the CP-0027 entrypoint.

This test runs the actual CLI in an isolated temporary data root with no
frozen gate evidence. It must stop at the gap-policy gate before creating
report/output directories or loading market data. No network or market data.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BACKTEST = ROOT / "scripts" / "AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py"


class TestCP0228RuntimeBacktestGate(unittest.TestCase):
    def test_missing_frozen_gap_evidence_stops_before_any_outputs(self):
        with tempfile.TemporaryDirectory(prefix="aists-cp0228-") as tmp:
            data_root = Path(tmp)
            env = os.environ.copy()
            env["AISTS_DATA_ROOT"] = str(data_root)
            # Ensure this subprocess cannot accidentally inherit a Colab mount.
            env.pop("COLAB_RELEASE_TAG", None)

            proc = subprocess.run(
                [sys.executable, str(BACKTEST)],
                cwd=str(ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            output = proc.stdout + "\n" + proc.stderr
            self.assertNotEqual(proc.returncode, 0, output)
            self.assertIn("G0_BLOCKED_GAP_POLICY_FILE_MISSING", output)
            self.assertFalse((data_root / "reports").exists())
            self.assertFalse(
                (data_root / "derived" / "research_candidate_v1" / "BTCUSDT" / "backtest_cp0027").exists()
            )

    def test_runtime_test_does_not_use_network_or_market_archives(self):
        source = BACKTEST.read_text(encoding="utf-8")
        for forbidden in (
            "api.binance.com/api/",
            "create_order(",
            "new_order(",
            "signed_request(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
