#!/usr/bin/env python3
"""Build a deterministic normalized BTCUSDT Spot/UM research dataset from validated archives."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import acquire_validate_btcusdt_history as validator

KLINE_COLUMNS = [
    "open_time_ms", "open", "high", "low", "close", "volume",
    "close_time_ms", "quote_volume", "trade_count",
    "taker_buy_base_volume", "taker_buy_quote_volume", "ignore",
]


def normalize_timestamp(raw: str) -> int:
    value = int(raw)
    return value // 1000 if value >= 100_000_000_000_000 else value


def archive_rows(path: Path) -> tuple[list[list[str]], str, str]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with zipfile.ZipFile(path) as archive:
        members = [name for name in archive.namelist() if not name.endswith("/")]
        if len(members) != 1:
            raise ValueError(f"{path}: expected one CSV member, got {len(members)}")
        member = members[0]
        payload = archive.read(member)
    return list(csv.reader(io.StringIO(payload.decode("utf-8-sig")))), member, digest


def load_klines(path: Path, period: str, header: bool, venue: str) -> tuple[list[dict], dict]:
    rows, member, digest = archive_rows(path)
    stats = validator.validate_klines(rows, period, header, venue)
    if stats.get("header_present"):
        rows = rows[1:]
    normalized = []
    for row in rows:
        record = dict(zip(KLINE_COLUMNS, row))
        record["open_time_ms"] = str(normalize_timestamp(row[0]))
        record["close_time_ms"] = str(normalize_timestamp(row[6]))
        record["venue"] = venue
        normalized.append(record)
    return normalized, {
        "archive": path.name, "archive_sha256": digest, "csv_member": member,
        "validated_rows": stats["rows"], "first_open_time_ms": stats["first_open_time_ms"],
        "last_open_time_ms": stats["last_open_time_ms"],
    }


def load_funding(path: Path, period: str) -> tuple[list[dict], dict]:
    rows, member, digest = archive_rows(path)
    stats = validator.validate_funding(rows, period)
    header = [item.strip().lower() for item in rows[0]]
    data = rows[1:]
    events = []
    legacy = header[:3] == ["calc_time", "funding_rate", "funding_rate_timestamp"]
    for row in data:
        if legacy:
            event_time = normalize_timestamp(row[2])
            rate = float(row[1])
            interval_hours = ""
            time_semantics = "funding_rate_timestamp"
        else:
            event_time = normalize_timestamp(row[0])
            rate = float(row[2])
            interval_hours = row[1]
            time_semantics = "calc_time"
        events.append({
            "funding_time_ms": str(event_time),
            "funding_rate": format(rate, ".16g"),
            "funding_interval_hours": interval_hours,
            "source_schema": "legacy" if legacy else "current",
            "source_time_field": time_semantics,
            "source_archive": path.name,
        })
    events.sort(key=lambda item: int(item["funding_time_ms"]))
    times = [int(item["funding_time_ms"]) for item in events]
    if len(times) != len(set(times)):
        raise ValueError(f"{path}: duplicate normalized funding event time")
    return events, {
        "archive": path.name, "archive_sha256": digest, "csv_member": member,
        "validated_rows": stats["rows"], "funding_time_semantics": "funding_rate_timestamp" if legacy else "calc_time",
        "first_funding_time_ms": min(times), "last_funding_time_ms": max(times),
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build(input_dir: Path, output_dir: Path, periods: list[str]) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    aligned_rows, funding_rows, provenance = [], [], []
    alignment_by_month = []
    for period in periods:
        spot_path = input_dir / f"{period}_spot_klines.zip"
        um_path = input_dir / f"{period}_um_klines.zip"
        funding_path = input_dir / f"{period}_um_funding.zip"
        for path in (spot_path, um_path, funding_path):
            if not path.is_file():
                raise FileNotFoundError(f"required source archive missing: {path}")
        spot, spot_meta = load_klines(spot_path, period, False, "spot")
        um, um_meta = load_klines(um_path, period, True, "um_futures")
        funding, funding_meta = load_funding(funding_path, period)
        spot_by_time = {int(row["open_time_ms"]): row for row in spot}
        um_by_time = {int(row["open_time_ms"]): row for row in um}
        spot_times, um_times = set(spot_by_time), set(um_by_time)
        matched = sorted(spot_times & um_times)
        spot_only = sorted(spot_times - um_times)
        um_only = sorted(um_times - spot_times)
        alignment_by_month.append({
            "period": period, "spot_rows": len(spot), "um_futures_rows": len(um),
            "matched_timestamps": len(matched), "spot_only_timestamps": len(spot_only),
            "um_futures_only_timestamps": len(um_only),
            "first_mismatch_examples_ms": {
                "spot_only": spot_only[:5], "um_futures_only": um_only[:5]},
            "exact_timestamp_alignment": not spot_only and not um_only and len(matched) == len(spot) == len(um),
        })
        if spot_only or um_only or len(matched) != len(spot) or len(matched) != len(um):
            raise ValueError(f"{period}: Spot/UM candle timestamp alignment failed")
        for timestamp in matched:
            s, f = spot_by_time[timestamp], um_by_time[timestamp]
            combined = {"open_time_ms": str(timestamp)}
            for field in KLINE_COLUMNS[1:]:
                combined[f"spot_{field}"] = s[field]
                combined[f"um_{field}"] = f[field]
            aligned_rows.append(combined)
        funding_rows.extend(funding)
        provenance.extend([
            {"period": period, "dataset": "spot_klines", **spot_meta},
            {"period": period, "dataset": "um_klines", **um_meta},
            {"period": period, "dataset": "um_funding", **funding_meta},
        ])
    aligned_rows.sort(key=lambda row: int(row["open_time_ms"]))
    funding_rows.sort(key=lambda row: int(row["funding_time_ms"]))
    candle_fields = ["open_time_ms"] + [
        f"{venue}_{field}" for field in KLINE_COLUMNS[1:] for venue in ("spot", "um")
    ]
    funding_fields = ["funding_time_ms", "funding_rate", "funding_interval_hours",
                      "source_schema", "source_time_field", "source_archive"]
    candles_path = output_dir / "btc-usdt-5m-aligned.csv"
    funding_path = output_dir / "btc-usdt-funding-events.csv"
    write_csv(candles_path, candle_fields, aligned_rows)
    write_csv(funding_path, funding_fields, funding_rows)
    manifest = {
        "dataset": "BTCUSDT normalized historical research inputs",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "periods": periods, "symbol": "BTCUSDT", "candle_interval": "5m",
        "source": "Official Binance monthly archives previously checked against official .CHECKSUM sidecars by acquire_validate_btcusdt_history.py",
        "source_archive_provenance": provenance,
        "alignment": alignment_by_month,
        "outputs": [
            {"file": candles_path.name, "rows": len(aligned_rows),
             "sha256": hashlib.sha256(candles_path.read_bytes()).hexdigest()},
            {"file": funding_path.name, "rows": len(funding_rows),
             "sha256": hashlib.sha256(funding_path.read_bytes()).hexdigest()},
        ],
        "safety_notes": [
            "This preparation step does not execute or rank a trading strategy.",
            "Funding events remain a separate event-time series; do not join a future funding rate to earlier candles.",
            "Legacy funding uses funding_rate_timestamp; current schema uses calc_time. Confirm event semantics before strategy evaluation.",
            "Aligned candles are timestamp-aligned only; they do not assert that Spot and Futures prices are interchangeable.",
            "Archive checksums and data integrity are not evidence of profitability."
        ],
        "summary": {"months": len(periods), "aligned_candles": len(aligned_rows),
                    "funding_events": len(funding_rows),
                    "all_months_exactly_aligned": all(item["exact_timestamp_alignment"] for item in alignment_by_month),
                    "status": "PASS"},
    }
    manifest_path = output_dir / "btc-usdt-normalized-dataset-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="artifacts/hd04-history")
    parser.add_argument("--output-dir", default="artifacts/hd04-normalized")
    parser.add_argument("--start-month", default="2026-07")
    parser.add_argument("--end-month", default="2026-09")
    args = parser.parse_args()
    periods = validator.month_range(args.start_month, args.end_month)
    manifest = build(Path(args.input_dir), Path(args.output_dir), periods)
    print(json.dumps({"manifest": str(Path(args.output_dir) / "btc-usdt-normalized-dataset-manifest.json"),
                      **manifest["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
