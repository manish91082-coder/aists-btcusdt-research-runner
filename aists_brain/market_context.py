"""Deterministic, causal BTCUSDT market-context features.

This module is an initial AI-brain building block, not a trading strategy.
Input candles must be completed, chronologically ordered OHLCV records. It
never fetches data, places orders, or infers missing candles.
"""
from __future__ import annotations

from math import isfinite
from statistics import median
from typing import Any, Iterable, Mapping, Sequence

TIMEFRAMES = ("5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mo")


def _number(candle: Mapping[str, Any], field: str) -> float:
    try:
        value = float(candle[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"candle field {field!r} must be numeric") from exc
    if not isfinite(value):
        raise ValueError(f"candle field {field!r} must be finite")
    return value


def _validate(candles: Sequence[Mapping[str, Any]]) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    previous_time: int | None = None
    for index, candle in enumerate(candles):
        row = {key: _number(candle, key) for key in ("open", "high", "low", "close", "volume")}
        if row["low"] > min(row["open"], row["close"]) or row["high"] < max(row["open"], row["close"]):
            raise ValueError(f"invalid OHLC range at candle index {index}")
        if row["low"] > row["high"] or row["volume"] < 0:
            raise ValueError(f"invalid low/high/volume at candle index {index}")
        if "open_time_ms" in candle:
            timestamp = int(_number(candle, "open_time_ms"))
            if previous_time is not None and timestamp <= previous_time:
                raise ValueError("open_time_ms must be strictly increasing")
            previous_time = timestamp
        rows.append(row)
    return rows


def _ema(values: Sequence[float], period: int) -> float | None:
    if len(values) < period:
        return None
    alpha = 2.0 / (period + 1.0)
    value = sum(values[:period]) / period
    for item in values[period:]:
        value = alpha * item + (1.0 - alpha) * value
    return value


def _rsi(values: Sequence[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None
    changes = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(change, 0.0) for change in changes]
    losses = [max(-change, 0.0) for change in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = ((period - 1) * avg_gain + gain) / period
        avg_loss = ((period - 1) * avg_loss + loss) / period
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    return 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))


def _atr(rows: Sequence[Mapping[str, float]], period: int = 14) -> float | None:
    if len(rows) <= period:
        return None
    true_ranges: list[float] = []
    for index in range(1, len(rows)):
        current = rows[index]
        previous_close = rows[index - 1]["close"]
        true_ranges.append(max(
            current["high"] - current["low"],
            abs(current["high"] - previous_close),
            abs(current["low"] - previous_close),
        ))
    value = sum(true_ranges[:period]) / period
    for true_range in true_ranges[period:]:
        value = ((period - 1) * value + true_range) / period
    return value


def analyze_market_context(
    candles: Iterable[Mapping[str, Any]],
    timeframe: str,
    *,
    zone_lookback: int = 20,
    volume_lookback: int = 20,
) -> dict[str, Any]:
    """Summarize one timeframe using only supplied candles up to the latest close.

    The caller is responsible for passing completed candles and handling gaps.
    Historical zones use candles before the latest candle, so the current bar
    cannot define its own prior resistance/support.
    """
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    if zone_lookback < 2 or volume_lookback < 2:
        raise ValueError("lookback values must be >= 2")
    rows = _validate(list(candles))
    if not rows:
        raise ValueError("at least one candle is required")

    closes = [row["close"] for row in rows]
    latest = rows[-1]
    ema20 = _ema(closes, 20)
    ema50 = _ema(closes, 50)
    rsi14 = _rsi(closes, 14)
    atr14 = _atr(rows, 14)
    prior = rows[:-1]
    zone_rows = prior[-zone_lookback:]
    volume_rows = rows[:-1][-volume_lookback:]
    prior_high = max((row["high"] for row in zone_rows), default=None)
    prior_low = min((row["low"] for row in zone_rows), default=None)
    baseline_volume = median(row["volume"] for row in volume_rows) if volume_rows else None
    volume_ratio = (
        latest["volume"] / baseline_volume
        if baseline_volume is not None and baseline_volume > 0 else None
    )
    momentum_n = 10
    momentum_pct = (
        (closes[-1] / closes[-1 - momentum_n] - 1.0) * 100.0
        if len(closes) > momentum_n and closes[-1 - momentum_n] != 0 else None
    )
    atr_pct = atr14 / latest["close"] * 100.0 if atr14 is not None and latest["close"] != 0 else None

    if ema20 is None or ema50 is None:
        trend = "INSUFFICIENT_HISTORY"
    elif latest["close"] > ema20 > ema50:
        trend = "BULLISH"
    elif latest["close"] < ema20 < ema50:
        trend = "BEARISH"
    else:
        trend = "MIXED"

    if rsi14 is None:
        momentum_state = "INSUFFICIENT_HISTORY"
    elif rsi14 >= 70:
        momentum_state = "OVERBOUGHT_ZONE"
    elif rsi14 <= 30:
        momentum_state = "OVERSOLD_ZONE"
    else:
        momentum_state = "NEUTRAL"

    return {
        "schema_version": "aists.market_context.v1",
        "timeframe": timeframe,
        "candle_count": len(rows),
        "latest_close": latest["close"],
        "latest_volume": latest["volume"],
        "trend_state": trend,
        "ema20": ema20,
        "ema50": ema50,
        "rsi14": rsi14,
        "momentum_state": momentum_state,
        "momentum_10_bar_pct": momentum_pct,
        "atr14": atr14,
        "atr14_pct": atr_pct,
        "volume_median_prior": baseline_volume,
        "volume_ratio_vs_prior_median": volume_ratio,
        "prior_resistance": prior_high,
        "prior_support": prior_low,
        "zone_lookback_bars": min(zone_lookback, len(zone_rows)),
        "data_status": "READY" if len(rows) >= 50 else "LIMITED_HISTORY",
        "limitations": [
            "OHLCV-only context; no order-book or liquidation data",
            "support/resistance are lookback extrema, not guaranteed levels",
            "features are descriptive and do not constitute a trade signal",
            "caller must validate candle completion, gaps, and source provenance",
        ],
    }
