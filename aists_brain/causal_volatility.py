"""Causal historical percentile utilities for ATR-percent observations."""
from __future__ import annotations

from math import isfinite
from typing import Sequence


def causal_atr_percentile(
    current_value: float,
    prior_values: Sequence[float],
    *,
    min_observations: int = 30,
    lookback: int = 100,
) -> float | None:
    """Rank current ATR% against prior observations only; current is excluded.

    Returns a percentile in [0, 100], or None when prior history is insufficient.
    Values must be chronological and finite. This function cannot establish
    whether upstream ATR values came from completed, gap-validated candles.
    """
    if min_observations < 1 or lookback < min_observations:
        raise ValueError("lookback must be >= min_observations >= 1")
    if isinstance(current_value, bool) or any(isinstance(value, bool) for value in prior_values):
        raise ValueError("ATR-percent values must be numeric, not boolean")
    if not isinstance(current_value, (int, float)) or any(
        not isinstance(value, (int, float)) for value in prior_values
    ):
        raise ValueError("ATR-percent values must be numeric")
    current = float(current_value)
    history = [float(value) for value in prior_values]
    if not isfinite(current) or current < 0:
        raise ValueError("current ATR-percent must be finite and non-negative")
    if any(not isfinite(value) or value < 0 for value in history):
        raise ValueError("historical ATR-percent values must be finite and non-negative")
    reference = history[-lookback:]
    if len(reference) < min_observations:
        return None
    return 100.0 * sum(value <= current for value in reference) / len(reference)


def causal_atr_percentile_series(
    values: Sequence[float],
    *,
    min_observations: int = 30,
    lookback: int = 100,
) -> list[float | None]:
    """Return one causal percentile per item, using only strictly earlier items."""
    result: list[float | None] = []
    for index, value in enumerate(values):
        result.append(causal_atr_percentile(
            value, values[:index],
            min_observations=min_observations,
            lookback=lookback,
        ))
    return result
