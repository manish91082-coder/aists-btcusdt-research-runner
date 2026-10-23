#!/usr/bin/env python3
"""Batch official BTCUSDT monthly archives in <=6-month chunks and build one manifest.

This orchestrator preserves the validator's six-month per-run cap while enabling
long historical coverage. It fails closed on any missing/invalid month.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def month_list(start: str, end: str) -> list[str]:
    def parse(value: str) -> tuple[int, int]:
        parts = value.split("-")
        if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
            raise ValueError("Months must use YYYY-MM")
        year, month = int(parts[0]), int(parts[1])
        if year < 2017 or not 1 <= month <= 12:
            raise ValueError(f"Invalid month: {value}")
        return year, month

    sy, sm = parse(start)
    ey, em = parse(end)
    first, last = sy * 12 + sm - 1, ey * 12 + em - 1
    if last < first:
        raise ValueError("end-month must not precede start-month")
    if last - first + 1 > 120:
        raise ValueError("refusing a run longer than 120 months")
    return [f"{idx // 12:04d}-{idx % 12 + 1:02d}" for idx in range(first, last + 1)]


def chunks(months: list[str], size: int = 6) -> list[list[str]]:
    return [months[i:i + size] for i in range(0, len(months), size)]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def append_csv_rows(source: Path, target: Path, write_header: bool) -> tuple[int, list[str]]:
    count = 0
    with source.open(newline="", encoding="utf-8") as inp:
        reader = csv.DictReader(inp)
        fields = reader.fieldnames
        if not fields:
            raise ValueError(f"missing CSV header: {source}")
        mode = "w" if write_header else "a"
        with target.open(mode, newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=fields, extrasaction="raise")
            if write_header:
                writer.writeheader()
            for row in reader:
                writer.writerow(row)
                count += 1
    return count, list(fields)


def validate_combined_candles(path: Path, expected_rows: int, interval_ms: int = 300000) -> dict:
    previous = None
    count = 0
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            ts = int(row["open_time_ms"])
            if previous is not None and ts - previous != interval_ms:
                raise ValueError(f"combined candle grid gap/order issue at row {count+1}: delta={ts-previous}")
            previous = ts
            count += 1
    if count != expected_rows:
        raise ValueError(f"combined candle count mismatch: expected {expected_rows}, got {count}")
    return {"rows": count, "continuous_5m_grid": True, "sha256": sha256(path)}


def validate_combined_funding(path: Path) -> dict:
    previous = None
    count = 0
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            ts = int(row["funding_time_ms"])
            if previous is not None and ts <= previous:
                raise ValueError(f"funding timestamps duplicate or nonascending at row {count+1}")
            previous = ts
            count += 1
    return {"rows": count, "timestamps_unique_ascending": True, "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-month", default="2020-01")
    parser.add_argument("--end-month", default="2026-09")
    parser.add_argument("--output-dir", default="artifacts/btcusdt-long-history")
    args = parser.parse_args()

    months = month_list(args.start_month, args.end_month)
    batches = chunks(months)
    root = Path(args.output_dir)
    raw_dir = root / "raw"
    reports_dir = root / "reports"
    chunks_dir = root / "normalized-chunks"
    raw_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)

    acquisition_script = Path("scripts/acquire_validate_btcusdt_history.py")
    prepare_script = Path("scripts/prepare_btcusdt_research_dataset.py")
    batch_reports = []
    normalized_manifests = []

    for batch in batches:
        start, end = batch[0], batch[-1]
        batch_key = f"{start}_{end}"
        print(f"ACQUIRE_VALIDATE batch={batch_key} months={len(batch)}", flush=True)
        result = subprocess.run([
            sys.executable, str(acquisition_script),
            "--start-month", start, "--end-month", end,
            "--output-dir", str(raw_dir),
        ], check=False)
        report_source = raw_dir / "btc-usdt-multimonth-integrity-report.json"
        if report_source.exists():
            report_target = reports_dir / f"archive-integrity-{batch_key}.json"
            shutil.copy2(report_source, report_target)
            batch_reports.append({
                "batch": batch_key, "report": report_target.name,
                "report_sha256": sha256(report_target),
                "summary": json.loads(report_target.read_text(encoding="utf-8")).get("summary", {}),
            })
        if result.returncode != 0:
            raise RuntimeError(f"archive validation failed for batch {batch_key}; inspect reports/{batch_key}")
        if not report_source.exists():
            raise RuntimeError(f"archive validator did not produce a report for {batch_key}")

        chunk_dir = chunks_dir / batch_key
        print(f"NORMALIZE batch={batch_key}", flush=True)
        subprocess.run([
            sys.executable, str(prepare_script),
            "--start-month", start, "--end-month", end,
            "--input-dir", str(raw_dir), "--output-dir", str(chunk_dir),
        ], check=True)
        manifest_path = chunk_dir / "btc-usdt-normalized-dataset-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_copy = reports_dir / f"normalized-manifest-{batch_key}.json"
        shutil.copy2(manifest_path, manifest_copy)
        normalized_manifests.append(manifest)

    candles_path = root / "btc-usdt-5m-aligned.csv"
    funding_path = root / "btc-usdt-funding-events.csv"
    candle_count = 0
    funding_count = 0
    candle_header_written = False
    funding_header_written = False
    for batch in batches:
        batch_key = f"{batch[0]}_{batch[-1]}"
        chunk_dir = chunks_dir / batch_key
        count, _ = append_csv_rows(
            chunk_dir / "btc-usdt-5m-aligned.csv", candles_path, not candle_header_written
        )
        candle_count += count
        candle_header_written = True
        count, _ = append_csv_rows(
            chunk_dir / "btc-usdt-funding-events.csv", funding_path, not funding_header_written
        )
        funding_count += count
        funding_header_written = True

    expected_rows = sum(calendar.monthrange(int(m[:4]), int(m[5:]))[1] * 288 for m in months)
    candle_validation = validate_combined_candles(candles_path, expected_rows)
    funding_validation = validate_combined_funding(funding_path)
    if funding_validation["rows"] != funding_count:
        raise ValueError("funding row count mismatch after aggregation")
    if candle_count != expected_rows:
        raise ValueError("candle row count does not match requested calendar coverage")

    archive_checks = []
    for report_item in batch_reports:
        report = json.loads((reports_dir / report_item["report"]).read_text(encoding="utf-8"))
        archive_checks.extend(report.get("checks", []))
    if len(archive_checks) != len(months) * 3:
        raise ValueError(f"expected {len(months)*3} archive checks, found {len(archive_checks)}")
    if any(item.get("status") != "PASS" for item in archive_checks):
        raise ValueError("one or more archive checks did not PASS")

    manifest = {
        "gate": "BTCUSDT-LONG-HISTORY-VALIDATION",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": "BTCUSDT",
        "interval": "5m",
        "months": months,
        "source": "Official Binance monthly Spot/UM Futures kline archives and UM funding archives, each archive SHA-256 checked against adjacent .CHECKSUM sidecar.",
        "batch_size_months_max": 6,
        "batch_archive_reports": batch_reports,
        "archive_checks": archive_checks,
        "normalized_batch_manifests": normalized_manifests,
        "combined_outputs": {
            "candles": {"file": candles_path.name, **candle_validation},
            "funding": {"file": funding_path.name, **funding_validation},
        },
        "summary": {
            "months_requested": len(months),
            "files_expected": len(months) * 3,
            "files_passed": sum(item.get("status") == "PASS" for item in archive_checks),
            "files_failed": sum(item.get("status") != "PASS" for item in archive_checks),
            "aligned_candles": candle_count,
            "funding_events": funding_count,
            "all_months_exactly_aligned": all(
                item.get("exact_timestamp_alignment") for part in normalized_manifests
                for item in part.get("alignment", [])
            ),
            "status": "PASS",
        },
        "limitations": [
            "This is BTCUSDT historical coverage, not current-universe discovery.",
            "Archive validation does not establish strategy profitability.",
            "Funding event-time semantics remain source-schema dependent; no funding cash flows are simulated by the Spot candidates.",
        ],
    }
    manifest_path = root / "btc-usdt-long-history-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), **manifest["summary"]}, indent=2), flush=True)
    # Chunk CSVs are temporary; preserve their manifests and the combined outputs.
    shutil.rmtree(chunks_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
