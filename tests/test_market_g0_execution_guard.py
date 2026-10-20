"""Regression tests for the G0 fail-closed historical execution policy."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from g0_execution_guard import (  # noqa: E402
    G0ExecutionBlocked,
    G0_PROTECTED_TASKS,
    is_g0_protected_task,
    require_authenticated_g0,
)


class G0ExecutionGuardTests(unittest.TestCase):
    def test_all_historical_simulation_entrypoints_are_protected(self):
        expected = {
            "historical_reference_replay",
            "monthly_derived_replay",
            "legacy_pipeline",
            "cp0027_baseline_backtest",
            "cp0040_quarantine_sensitivity_run",
        }
        self.assertEqual(G0_PROTECTED_TASKS, frozenset(expected))
        for task in expected:
            with self.subTest(task=task):
                self.assertTrue(is_g0_protected_task(task))
                with self.assertRaisesRegex(G0ExecutionBlocked, "G0_EVIDENCE_NOT_AUTHENTICATED"):
                    require_authenticated_g0(task)

    def test_non_simulation_task_is_not_blocked_by_this_policy(self):
        self.assertFalse(is_g0_protected_task("smoke"))
        require_authenticated_g0("smoke")


if __name__ == "__main__":
    unittest.main()
