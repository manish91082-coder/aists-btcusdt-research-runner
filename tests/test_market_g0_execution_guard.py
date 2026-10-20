"""Regression tests for the G0 fail-closed historical execution policy."""
from __future__ import annotations

import ast
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
            "cp0026_candidate_builder",
        }
        self.assertEqual(G0_PROTECTED_TASKS, frozenset(expected))
        for task in expected:
            with self.subTest(task=task):
                self.assertTrue(is_g0_protected_task(task))
                with self.assertRaisesRegex(G0ExecutionBlocked, "G0_EVIDENCE_NOT_AUTHENTICATED"):
                    require_authenticated_g0(task)

    def test_direct_cli_entrypoints_call_guard_before_work(self):
        guarded = {
            "historical_reference_replay.py": "historical_reference_replay",
            "monthly_derived_replay.py": "monthly_derived_replay",
            "aists_legacy_pipeline.py": "legacy_pipeline",
            "AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py": "cp0027_baseline_backtest",
            "AISTS_CP0040_Quarantine_Sensitivity_Audit.py": "cp0040_quarantine_sensitivity_run",
        }
        for filename, task in guarded.items():
            with self.subTest(filename=filename):
                source = (SCRIPTS / filename).read_text(encoding="utf-8")
                tree = ast.parse(source, filename=filename)
                main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
                self.assertGreaterEqual(len(main.body), 2)
                call = main.body[1]
                self.assertIsInstance(call, ast.Expr)
                self.assertIsInstance(call.value, ast.Call)
                self.assertIsInstance(call.value.func, ast.Name)
                self.assertEqual(call.value.func.id, "require_authenticated_g0")
                self.assertEqual(ast.literal_eval(call.value.args[0]), task)

        builder_source = (SCRIPTS / "AISTS_CP0026_Research_Candidate_Builder.py").read_text(encoding="utf-8")
        builder_tree = ast.parse(builder_source, filename="AISTS_CP0026_Research_Candidate_Builder.py")
        builder_main = next(
            node for node in builder_tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        gate_self_test_index = next(
            i for i, node in enumerate(builder_main.body)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Attribute)
            and node.test.attr == "gate_self_test"
        )
        guard_index = next(
            i for i, node in enumerate(builder_main.body)
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "require_authenticated_g0"
        )
        self.assertGreater(guard_index, gate_self_test_index)
        guard_call = builder_main.body[guard_index].value
        self.assertEqual(ast.literal_eval(guard_call.args[0]), "cp0026_candidate_builder")

        for helper_name in ("audit_and_write_interval", "create_monthly_from_daily"):
            with self.subTest(helper_name=helper_name):
                helper = next(
                    node for node in builder_tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == helper_name
                )
                self.assertGreaterEqual(len(helper.body), 2)
                self.assertIsInstance(helper.body[0], ast.ImportFrom)
                self.assertEqual(helper.body[0].module, "g0_execution_guard")
                guard_stmt = helper.body[1]
                self.assertIsInstance(guard_stmt, ast.Expr)
                self.assertIsInstance(guard_stmt.value, ast.Call)
                self.assertIsInstance(guard_stmt.value.func, ast.Name)
                self.assertEqual(guard_stmt.value.func.id, "require_authenticated_g0")
                self.assertEqual(
                    ast.literal_eval(guard_stmt.value.args[0]),
                    "cp0026_candidate_builder",
                )

        runner_source = (SCRIPTS / "aists_runner.py").read_text(encoding="utf-8")
        self.assertIn("elif is_g0_protected_task(task):", runner_source)
        self.assertIn('child_status="BLOCKED_G0_AUTHORIZATION"', runner_source)

    def test_non_simulation_task_is_not_blocked_by_this_policy(self):
        self.assertFalse(is_g0_protected_task("smoke"))
        require_authenticated_g0("smoke")


if __name__ == "__main__":
    unittest.main()
