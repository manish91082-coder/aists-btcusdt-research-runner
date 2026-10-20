"""Fail-closed loader for explicitly adjudicated historical candle inputs.

This module verifies file integrity and structural contracts. It does NOT
authenticate the authority or truth of the supplied adjudication report; that
must be independently established before a manifest may claim PASS.
No downloads, network calls, repairs, forward-fills, or trading actions.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "aists.provenance_cleared_candles.v1"
INTERVAL_MS = {
    "5m": 300_000,
    "15m": 900_000,
    "30m": 1_800_000,
    "1h": 3_600_000,
    "4h": 14_400_000,
    "1d": 86_400_000,
    "1w": 604_800_000,
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CSV_COLUMNS = ("open_time_ms", "close_time_ms", "open", "high", "low", "close", "volume")


class ProvenanceGateError(ValueError):
    """Raised when provenance evidence or candle structure fails closed."""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProvenanceGateError(message)


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def load_provenance_cleared_candles(
    csv_path: str | Path, manifest_path: str | Path, *,
    expected_symbol: str = "BTCUSDT", expected_market: str = "spot",
    expected_interval: str | None = None,
) -> dict[str, Any]:
    """Load OHLCV only if an explicit, hash-bound PASS manifest satisfies the contract.

    Manifest fields required:
      schema_version, adjudication_status='PASS', global_g0_status='PASS',
      symbol, market, interval, csv_sha256, source_manifest_sha256,
      adjudication_report_sha256, source_archive_sha256 (nonempty list),
      expected_row_count, first_open_time_ms, last_open_time_ms,
      coverage_pct (>=99.5), all_missing_intervals_accounted=true,
      all_gap_events_accounted=true, completed_candles_only=true.
    If timestamp gaps exist, gap_events must exactly enumerate each observed
    gap as {previous_open_time_ms, next_open_time_ms, first_missing_open_time_ms,
    last_missing_open_time_ms, missing_count}. This validates claims and hashes,
    not the external adjudicator's authority.
    """
    data_path, meta_path = Path(csv_path), Path(manifest_path)
    try:
        manifest = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProvenanceGateError(f"cannot read valid manifest: {exc}") from exc
    _require(isinstance(manifest, dict), "manifest must be a JSON object")

    required = (
        "schema_version", "adjudication_status", "global_g0_status", "symbol",
        "market", "interval", "csv_sha256", "source_manifest_sha256",
        "adjudication_report_sha256", "source_archive_sha256", "expected_row_count",
        "first_open_time_ms", "last_open_time_ms", "coverage_pct",
        "all_missing_intervals_accounted", "all_gap_events_accounted",
        "completed_candles_only",
    )
    missing = [key for key in required if key not in manifest]
    _require(not missing, f"manifest missing required fields: {','.join(missing)}")
    _require(manifest["schema_version"] == SCHEMA_VERSION, "unsupported manifest schema")
    _require(manifest["adjudication_status"] == "PASS", "adjudication status is not PASS")
    _require(manifest["global_g0_status"] == "PASS", "global G0 is not PASS")
    _require(manifest["symbol"] == expected_symbol, "symbol mismatch")
    _require(manifest["market"] == expected_market, "market mismatch")
    interval = manifest["interval"]
    _require(interval in INTERVAL_MS, "unsupported interval")
    if expected_interval is not None:
        _require(interval == expected_interval, "interval mismatch")
    for field in ("csv_sha256", "source_manifest_sha256", "adjudication_report_sha256"):
        _require(_valid_sha(manifest[field]), f"{field} must be lowercase SHA-256")
    archives = manifest["source_archive_sha256"]
    _require(isinstance(archives, list) and len(archives) > 0, "source archive hashes must be non-empty")
    _require(all(_valid_sha(item) for item in archives), "each source archive hash must be lowercase SHA-256")
    _require(manifest["all_missing_intervals_accounted"] is True, "missing intervals are not fully accounted")
    _require(manifest["all_gap_events_accounted"] is True, "gap events are not fully accounted")
    _require(manifest["completed_candles_only"] is True, "manifest does not certify completed candles only")
    coverage = manifest["coverage_pct"]
    _require(isinstance(coverage, (int, float)) and not isinstance(coverage, bool)
             and math.isfinite(coverage) and 99.5 <= coverage <= 100.0,
             "coverage_pct must be between 99.5 and 100")
    row_count = manifest["expected_row_count"]
    _require(isinstance(row_count, int) and not isinstance(row_count, bool) and row_count > 0,
             "expected_row_count must be a positive integer")
    for field in ("first_open_time_ms", "last_open_time_ms"):
        _require(isinstance(manifest[field], int) and not isinstance(manifest[field], bool)
                 and manifest[field] >= 0, f"{field} must be a non-negative integer")

    try:
        actual_hash = sha256_file(data_path)
    except OSError as exc:
        raise ProvenanceGateError(f"cannot read candle CSV: {exc}") from exc
    _require(actual_hash == manifest["csv_sha256"], "CSV SHA-256 does not match manifest")

    candles: list[dict[str, Any]] = []
    observed_gap_events: list[dict[str, int]] = []
    interval_ms = INTERVAL_MS[interval]
    try:
        with data_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            _require(reader.fieldnames is not None and set(CSV_COLUMNS).issubset(reader.fieldnames),
                     "CSV is missing required OHLCV columns")
            previous_open: int | None = None
            for line_no, row in enumerate(reader, start=2):
                try:
                    open_ms, close_ms = int(row["open_time_ms"]), int(row["close_time_ms"])
                    values = {key: float(row[key]) for key in ("open", "high", "low", "close", "volume")}
                except (TypeError, ValueError, KeyError) as exc:
                    raise ProvenanceGateError(f"invalid numeric field on CSV line {line_no}") from exc
                _require(open_ms >= 0 and close_ms == open_ms + interval_ms - 1,
                         f"invalid candle timestamps on CSV line {line_no}")
                _require(previous_open is None or open_ms > previous_open,
                         f"timestamps not strictly increasing on CSV line {line_no}")
                if previous_open is not None:
                    delta_ms = open_ms - previous_open
                    _require(delta_ms % interval_ms == 0,
                             f"timestamp gap is off-grid on CSV line {line_no}")
                    if delta_ms > interval_ms:
                        missing_count = delta_ms // interval_ms - 1
                        observed_gap_events.append({
                            "previous_open_time_ms": previous_open,
                            "next_open_time_ms": open_ms,
                            "first_missing_open_time_ms": previous_open + interval_ms,
                            "last_missing_open_time_ms": open_ms - interval_ms,
                            "missing_count": missing_count,
                        })
                _require(all(math.isfinite(value) for value in values.values()),
                         f"non-finite OHLCV value on CSV line {line_no}")
                o, h, low, c, volume = (values[k] for k in ("open", "high", "low", "close", "volume"))
                _require(min(o, h, low, c) > 0 and low <= min(o, c) <= max(o, c) <= h,
                         f"invalid OHLC range on CSV line {line_no}")
                _require(volume >= 0, f"negative volume on CSV line {line_no}")
                candles.append({"open_time_ms": open_ms, "close_time_ms": close_ms,
                                "open": o, "high": h, "low": low, "close": c, "volume": volume})
                previous_open = open_ms
    except OSError as exc:
        raise ProvenanceGateError(f"cannot read candle CSV: {exc}") from exc

    _require(len(candles) == row_count, "CSV row count does not match manifest")
    _require(candles, "CSV contains no candle rows")
    _require(candles[0]["open_time_ms"] == manifest["first_open_time_ms"],
             "first candle timestamp does not match manifest")
    _require(candles[-1]["open_time_ms"] == manifest["last_open_time_ms"],
             "last candle timestamp does not match manifest")

    claimed_gap_events = manifest.get("gap_events")
    if observed_gap_events:
        _require(isinstance(claimed_gap_events, list),
                 "observed candle gaps require an explicit gap_events manifest list")
    else:
        _require(claimed_gap_events is None or claimed_gap_events == [],
                 "manifest gap_events do not match the contiguous candle series")
    if claimed_gap_events is not None:
        _require(claimed_gap_events == observed_gap_events,
                 "manifest gap_events do not match observed candle timestamp gaps")

    return {
        "status": "LOADED_WITH_EXTERNAL_PASS_CLAIM",
        "symbol": expected_symbol,
        "market": expected_market,
        "interval": interval,
        "interval_ms": interval_ms,
        "csv_sha256": actual_hash,
        "row_count": len(candles),
        "first_open_time_ms": candles[0]["open_time_ms"],
        "last_open_time_ms": candles[-1]["open_time_ms"],
        "coverage_pct_claimed": float(coverage),
        "gap_events": observed_gap_events,
        "candles": candles,
        "limitations": [
            "manifest PASS claims and report hashes are not independently authenticated here",
            "this loader does not adjudicate Binance historical archive version provenance",
            "gaps are not repaired; caller must retain gap metadata and simulator skips non-contiguous fills",
            "passing this loader is not strategy acceptance or evidence of profitability",
        ],
    }
