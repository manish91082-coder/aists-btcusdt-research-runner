import unittest

from aists_brain.causal_volatility import (
    causal_atr_percentile,
    causal_atr_percentile_series,
)


class CausalVolatilityTests(unittest.TestCase):
    def test_rejects_boolean_current_value(self):
        with self.assertRaisesRegex(ValueError, "not boolean"):
            causal_atr_percentile(True, [1.0, 2.0], min_observations=2, lookback=2)

    def test_rejects_boolean_in_history(self):
        with self.assertRaisesRegex(ValueError, "not boolean"):
            causal_atr_percentile(1.5, [1.0, False], min_observations=2, lookback=2)

    def test_rejects_numeric_string_current_value(self):
        with self.assertRaisesRegex(ValueError, "must be numeric"):
            causal_atr_percentile("1.5", [1.0, 2.0], min_observations=2, lookback=2)

    def test_rejects_numeric_string_in_history(self):
        with self.assertRaisesRegex(ValueError, "must be numeric"):
            causal_atr_percentile(1.5, [1.0, "2.0"], min_observations=2, lookback=2)

    def test_current_value_is_not_in_its_own_reference_history(self):
        result = causal_atr_percentile_series(
            [1.0, 2.0, 3.0], min_observations=2, lookback=2
        )
        self.assertEqual(result, [None, None, 100.0])

    def test_uses_only_configured_prior_lookback(self):
        result = causal_atr_percentile(
            2.0, [100.0, 1.0, 3.0], min_observations=2, lookback=2
        )
        self.assertEqual(result, 50.0)

    def test_rejects_invalid_lookback_contract(self):
        with self.assertRaisesRegex(ValueError, "lookback must be"):
            causal_atr_percentile(1.0, [1.0], min_observations=3, lookback=2)


if __name__ == "__main__":
    unittest.main()
