"""
AISTS BTCUSDT Research Runner - Sample Research Script
Run this locally or via GitHub Actions Python Runner workflow.
"""

import json
import datetime
import requests
import pandas as pd
import numpy as np


def fetch_btcusdt_data(interval="1h", limit=200):
    """Fetch BTCUSDT OHLCV data from Binance public API."""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": interval, "limit": limit}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()

    cols = ["open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "num_trades", "tbbav", "tbqav", "ignore"]
    df = pd.DataFrame(resp.json(), columns=cols)

    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df.set_index("open_time", inplace=True)
    return df


def compute_indicators(df):
    """Compute technical indicators."""
    df["sma_20"] = df["close"].rolling(20).mean()
    df["sma_50"] = df["close"].rolling(50).mean()
    df["ema_12"] = df["close"].ewm(span=12).mean()
    df["ema_26"] = df["close"].ewm(span=26).mean()
    df["macd"]   = df["ema_12"] - df["ema_26"]
    df["signal"] = df["macd"].ewm(span=9).mean()
    df["hist"]   = df["macd"] - df["signal"]

    delta  = df["close"].diff()
    gain   = delta.clip(lower=0).rolling(14).mean()
    loss   = delta.clip(upper=0).abs().rolling(14).mean()
    rs     = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    df["bb_mid"]   = df["close"].rolling(20).mean()
    df["bb_upper"] = df["bb_mid"] + 2 * df["close"].rolling(20).std()
    df["bb_lower"] = df["bb_mid"] - 2 * df["close"].rolling(20).std()
    return df


def generate_report(df):
    """Generate research report."""
    latest = df.iloc[-1]
    report = {
        "generated_at":  str(datetime.datetime.utcnow()),
        "current_price": float(latest["close"]),
        "rsi":           float(latest["rsi"]),
        "macd":          float(latest["macd"]),
        "signal":        float(latest["signal"]),
        "sma_20":        float(latest["sma_20"]),
        "sma_50":        float(latest["sma_50"]),
        "bb_upper":      float(latest["bb_upper"]),
        "bb_lower":      float(latest["bb_lower"]),
        "trend":         "UPTREND" if latest["sma_20"] > latest["sma_50"] else "DOWNTREND",
        "rsi_signal":    ("OVERSOLD" if latest["rsi"] < 30 else
                          "OVERBOUGHT" if latest["rsi"] > 70 else "NEUTRAL"),
        "macd_signal":   "BULLISH" if latest["macd"] > latest["signal"] else "BEARISH",
    }
    return report


if __name__ == "__main__":
    print("🔬 AISTS BTCUSDT Sample Research Script")
    print("=" * 50)

    df = fetch_btcusdt_data(interval="1h", limit=200)
    print(f"✅ Fetched {len(df)} candles")

    df = compute_indicators(df)
    print("✅ Indicators computed")

    report = generate_report(df)
    print("\n📊 Research Report:")
    print(json.dumps(report, indent=2))

    # Save results
    import os
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/ohlcv.csv")
    with open("results/report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n✅ Results saved to results/")
