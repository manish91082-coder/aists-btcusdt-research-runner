import unittest

from crypto_target.research_math import (
    compound_returns,
    max_drawdown,
    required_period_return,
    target_multiple,
)


class ResearchMathTests(unittest.TestCase):
    def test_target_multiple(self):
        self.assertAlmostEqual(target_multiple(1000, 1_000_000), 1000.0)

    def test_required_return_reaches_target(self):
        r = required_period_return(1000, 1_000_000, 100)
        self.assertAlmostEqual(1000 * (1 + r) ** 100, 1_000_000, places=5)

    def test_realized_profit_is_reinvested(self):
        path = compound_returns(1000, [0.10, -0.05, 0.02])
        self.assertAlmostEqual(path[0], 1100.0)
        self.assertAlmostEqual(path[1], 1045.0)
        self.assertAlmostEqual(path[2], 1065.9)

    def test_max_drawdown(self):
        self.assertAlmostEqual(max_drawdown([100, 120, 90, 99, 130]), -0.25)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            required_period_return(1000, 1_000_000, 0)
        with self.assertRaises(ValueError):
            compound_returns(1000, [-1.01])


if __name__ == "__main__":
    unittest.main()
