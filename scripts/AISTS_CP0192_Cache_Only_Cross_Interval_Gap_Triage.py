#!/usr/bin/env python3
"""Cache-only triage of missing 4h open times against existing 5m and 1h monthly archives."""
from __future__ import annotations
import argparse, csv, hashlib, json, zipfile
from datetime import datetime, timezone
from pathlib import Path

INTERVAL_US = {"5m": 5 * 60 * 1_000_000, "1h": 60 * 60 * 1_000_000, "4h": 4 * 60 * 60 * 1_000_000}
EXPECTED_CHILD_INTERVALS = {"5m": 48, "1h": 4}

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def normalize_timestamp_to_us(value):
    if 1_000_000_000_000 <= value < 100_000_000_000_000:
        return value * 1000, "milliseconds"
    if 1_000_000_000_000_000 <= value < 100_000_000_000_000_000:
        return value, "microseconds"
    raise ValueError(f"unsupported epoch timestamp magnitude: {value}")

def timestamp_to_iso(timestamp_us):
    seconds, micros = divmod(timestamp_us, 1_000_000)
    return datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=micros).isoformat()

def month_from_timestamp_us(timestamp_us):
    dt = datetime.fromtimestamp(timestamp_us / 1_000_000, timezone.utc)
    return f"{dt.year:04d}-{dt.month:02d}"

def read_gap_slots(gap_csv):
    slots = []
    with gap_csv.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        previous = datetime.fromisoformat(row["previous_open_time_utc"].replace("Z", "+00:00"))
        following = datetime.fromisoformat(row["next_open_time_utc"].replace("Z", "+00:00"))
        previous_us = int(previous.timestamp() * 1_000_000)
        following_us = int(following.timestamp() * 1_000_000)
        delta = following_us - previous_us
        if delta <= INTERVAL_US["4h"] or delta % INTERVAL_US["4h"]:
            raise ValueError(f"non-grid 4h gap in input: {row}")
        expected_missing = delta // INTERVAL_US["4h"] - 1
        if int(row["missing_intervals_estimate"]) != expected_missing:
            raise ValueError(f"gap estimate does not match exact endpoints: {row}")
        cursor = previous_us + INTERVAL_US["4h"]
        while cursor < following_us:
            slots.append({"expected_open_time_us": cursor,
                          "expected_open_time_utc": timestamp_to_iso(cursor),
                          "source_gap_previous_open_time_utc": row["previous_open_time_utc"],
                          "source_gap_next_open_time_utc": row["next_open_time_utc"]})
            cursor += INTERVAL_US["4h"]
    slots.sort(key=lambda item: item["expected_open_time_us"])
    if len({item["expected_open_time_us"] for item in slots}) != len(slots):
        raise ValueError("duplicate expected missing 4h open time in source gap CSV")
    return slots

def expected_archive_path(cache_root, interval, period):
    filename = f"BTCUSDT-{interval}-{period}.zip"
    return cache_root / interval / period / filename

def inspect_cached_archive(path, interval, period):
    rec = {"interval": interval, "period": period, "filename": path.name,
           "cache_path": str(path), "cache_status": "MISSING",
           "sha256": "", "bytes": "", "zip_crc": "NOT_CHECKED",
           "csv_member": "", "rows": 0, "timestamp_unit": "",
           "timestamp_unit_status": "NOT_CHECKED", "error": ""}
    if not path.is_file():
        return rec, set()
    rec["cache_status"] = "PRESENT"
    rec["bytes"] = path.stat().st_size
    rec["sha256"] = sha256_file(path)
    opens = set()
    unit_counts = {"milliseconds": 0, "microseconds": 0}
    try:
        with zipfile.ZipFile(path, "r") as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                raise ValueError(f"ZIP CRC failure at member {bad_member}")
            members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(members) != 1:
                raise ValueError(f"expected exactly one CSV member, found {len(members)}")
            rec["csv_member"] = members[0]
            import io
            with archive.open(members[0], "r") as raw:
                reader = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline=""))
                for line_no, row in enumerate(reader, 1):
                    if not row:
                        continue
                    try:
                        value = int(row[0])
                    except (ValueError, IndexError):
                        if line_no == 1:
                            continue
                        raise ValueError(f"invalid open_time at CSV line {line_no}")
                    normalized, unit = normalize_timestamp_to_us(value)
                    opens.add(normalized)
                    unit_counts[unit] += 1
        rec["zip_crc"] = "PASS"
        rec["rows"] = sum(unit_counts.values())
        observed = sorted(unit for unit, count in unit_counts.items() if count)
        rec["timestamp_unit"] = "EMPTY" if not observed else observed[0] if len(observed) == 1 else "MIXED"
        expected = "microseconds" if period >= "2025-01" else "milliseconds"
        rec["timestamp_unit_status"] = "PASS" if observed == [expected] else "FAIL"
        if rec["timestamp_unit_status"] != "PASS":
            rec["error"] = f"expected {expected}, observed {rec['timestamp_unit']}"
    except Exception as exc:
        rec["zip_crc"] = "FAIL"
        rec["timestamp_unit_status"] = "FAIL"
        rec["error"] = f"{type(exc).__name__}: {exc}"
        opens = set()
    return rec, opens

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--monthly-cache", default=".cache/aists/binance-monthly-archives")
    parser.add_argument("--gaps-csv", default="results/cp0165_4h_archive_audit/CP0165_4H_Monthly_Checksum_Gap_Audit_Gaps.csv")
    parser.add_argument("--output-dir", default="results/cp0192_cross_interval_gap_triage")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    cache_root = (root / args.monthly_cache).resolve()
    gaps_path = (root / args.gaps_csv).resolve()
    out = (root / args.output_dir).resolve()
    started = datetime.now(timezone.utc).isoformat()
    if not gaps_path.is_file():
        raise FileNotFoundError(f"required CP-0165 gap evidence missing: {gaps_path}")
    source_hash = sha256_file(gaps_path)
    slots = read_gap_slots(gaps_path)
    if not slots:
        raise ValueError("CP-0165 gap CSV contains no missing slots; refusing to infer coverage")
    periods = sorted({month_from_timestamp_us(slot["expected_open_time_us"]) for slot in slots})
    archive_rows = []
    open_index = {}
    for period in periods:
        for interval in ("5m", "1h"):
            path = expected_archive_path(cache_root, interval, period)
            record, opens = inspect_cached_archive(path, interval, period)
            archive_rows.append(record)
            open_index[(interval, period)] = opens if record["cache_status"] == "PRESENT" and record["zip_crc"] == "PASS" and record["timestamp_unit_status"] == "PASS" else None

    detail_rows = []
    for slot in slots:
        t = slot["expected_open_time_us"]
        period = month_from_timestamp_us(t)
        row = dict(slot)
        row["period"] = period
        all_intervals_complete = True
        any_interval_available = False
        for interval in ("5m", "1h"):
            opens = open_index[(interval, period)]
            expected_count = EXPECTED_CHILD_INTERVALS[interval]
            expected_opens = set(range(t, t + INTERVAL_US["4h"], INTERVAL_US[interval]))
            found = len(expected_opens.intersection(opens)) if opens is not None else ""
            row[f"{interval}_archive_status"] = "UNAVAILABLE_OR_INVALID" if opens is None else "VALID"
            row[f"{interval}_expected_opens"] = expected_count
            row[f"{interval}_found_opens"] = found
            row[f"{interval}_coverage_status"] = "UNAVAILABLE_OR_INVALID" if opens is None else "COMPLETE" if found == expected_count else "PARTIAL" if found else "NONE"
            if opens is not None:
                any_interval_available = True
                if found != expected_count:
                    all_intervals_complete = False
            else:
                all_intervals_complete = False
        row["triage_status"] = "COMPLETE_FINER_INTERVAL_COVERAGE" if all_intervals_complete else "PARTIAL_FINER_INTERVAL_COVERAGE" if any_interval_available and any(row[f"{i}_found_opens"] not in ("", 0) for i in ("5m", "1h")) else "NO_COMPLETE_FINER_INTERVAL_EVIDENCE"
        row["interpretation"] = "coverage_only_not_reconstruction_or_canonical_source"
        detail_rows.append(row)

    missing = sum(r["cache_status"] != "PRESENT" for r in archive_rows)
    invalid = sum(r["cache_status"] == "PRESENT" and (r["zip_crc"] != "PASS" or r["timestamp_unit_status"] != "PASS") for r in archive_rows)
    complete_5m = sum(r["5m_coverage_status"] == "COMPLETE" for r in detail_rows)
    complete_1h = sum(r["1h_coverage_status"] == "COMPLETE" for r in detail_rows)
    complete_any = sum(r["triage_status"] == "COMPLETE_FINER_INTERVAL_COVERAGE" for r in detail_rows)
    summary = {
        "schema_version": 1, "checkpoint": "CP-0192", "task": "cache_only_cross_interval_gap_triage",
        "status": "PASS_CACHE_ONLY_TRIAGE_COMPLETED" if len(detail_rows) == len(slots) and missing == 0 and invalid == 0 else "REVIEW_REQUIRED_CACHE_COVERAGE_INCOMPLETE",
        "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_gap_csv": str(gaps_path.relative_to(root)), "source_gap_csv_sha256": source_hash,
        "expected_4h_missing_slots": len(slots), "source_gap_events": len({(r["source_gap_previous_open_time_utc"], r["source_gap_next_open_time_utc"]) for r in slots}),
        "months_inspected": periods, "intervals_checked": ["5m", "1h"],
        "expected_child_archives": len(periods) * 2, "cache_archives_missing": missing, "cache_archives_invalid_or_wrong_unit": invalid,
        "slots_with_complete_5m_coverage": complete_5m, "slots_with_complete_1h_coverage": complete_1h,
        "slots_with_complete_5m_and_1h_coverage": complete_any,
        "network_used": False, "archive_downloads": 0, "official_sidecar_requests": 0, "market_data_rest_api_used": False,
        "cached_source_archives_modified": False, "candles_created_or_repaired": False, "timestamp_shift_or_interpolation": False,
        "canonical_source": "NONE", "source_cases_closed": 0, "g0": "BLOCKED_GLOBAL",
        "backtest_run": False, "candidate_build": False, "strategy_promoted": False,
        "live_signing_broadcast_orders": "BLOCKED"
    }
    write_csv(out / "CP0192_Cross_Interval_Gap_Triage.csv", detail_rows, [
        "expected_open_time_utc", "period", "source_gap_previous_open_time_utc", "source_gap_next_open_time_utc",
        "5m_archive_status", "5m_expected_opens", "5m_found_opens", "5m_coverage_status",
        "1h_archive_status", "1h_expected_opens", "1h_found_opens", "1h_coverage_status",
        "triage_status", "interpretation"])
    write_csv(out / "CP0192_Cache_Archive_Manifest.csv", archive_rows, [
        "interval", "period", "filename", "cache_path", "cache_status", "sha256", "bytes",
        "zip_crc", "csv_member", "rows", "timestamp_unit", "timestamp_unit_status", "error"])
    (out / "CP0192_Summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# CP-0192: Cache-only cross-interval gap triage", "",
        f"- Status: {summary['status']}",
        f"- Source gap CSV SHA-256: {source_hash}",
        f"- Expected missing 4h slots inspected: {len(slots)} across {len(periods)} months.",
        f"- Existing child archives checked: {len(archive_rows)}; missing: {missing}; invalid or wrong-unit: {invalid}.",
        f"- Slots with complete 5m coverage: {complete_5m}/{len(slots)}.",
        f"- Slots with complete 1h coverage: {complete_1h}/{len(slots)}.",
        f"- Slots with complete 5m and 1h coverage: {complete_any}/{len(slots)}.",
        "- This is presence/coverage triage only. It does not reconstruct candles, establish source authority, or close any source case.",
        "- Network access, downloads, Binance REST, cache mutation, interpolation, backtests, candidate builds, and live actions are prohibited by this task."
    ]
    (out / "CP0192_Report_HI.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("status", "expected_4h_missing_slots", "expected_child_archives", "cache_archives_missing", "cache_archives_invalid_or_wrong_unit", "slots_with_complete_5m_coverage", "slots_with_complete_1h_coverage", "slots_with_complete_5m_and_1h_coverage", "network_used", "archive_downloads", "canonical_source", "g0", "live_signing_broadcast_orders")}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
