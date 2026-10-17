#!/usr/bin/env python3
"""Cache-only exact-open-key comparison against frozen daily-reference 4h archives."""
from __future__ import annotations
import argparse, csv, hashlib, json, zipfile
from datetime import datetime, timezone
from pathlib import Path

INTERVAL_US = 4 * 60 * 60 * 1_000_000

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def normalize_timestamp_to_us(value):
    value = int(value)
    if 1_000_000_000_000 <= value < 100_000_000_000_000:
        return value * 1000, "milliseconds"
    if 1_000_000_000_000_000 <= value < 100_000_000_000_000_000:
        return value, "microseconds"
    raise ValueError(f"unsupported epoch timestamp magnitude: {value}")

def timestamp_to_iso(value_us):
    seconds, micros = divmod(value_us, 1_000_000)
    return datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=micros).isoformat()

def read_gap_slots(path):
    slots = []
    for row in read_csv(path):
        prev = datetime.fromisoformat(row["previous_open_time_utc"].replace("Z", "+00:00"))
        nxt = datetime.fromisoformat(row["next_open_time_utc"].replace("Z", "+00:00"))
        prev_us, next_us = int(prev.timestamp() * 1_000_000), int(nxt.timestamp() * 1_000_000)
        if next_us <= prev_us or (next_us - prev_us) % INTERVAL_US:
            raise ValueError(f"non-grid 4h gap in input: {row}")
        expected = (next_us - prev_us) // INTERVAL_US - 1
        if int(row["missing_intervals_estimate"]) != expected:
            raise ValueError(f"gap estimate mismatch: {row}")
        cursor = prev_us + INTERVAL_US
        while cursor < next_us:
            slots.append({"expected_open_time_us": cursor,
                          "expected_open_time_utc": timestamp_to_iso(cursor),
                          "period": datetime.fromtimestamp(cursor / 1_000_000, timezone.utc).strftime("%Y-%m"),
                          "date_utc": datetime.fromtimestamp(cursor / 1_000_000, timezone.utc).strftime("%Y-%m-%d"),
                          "source_gap_previous_open_time_utc": row["previous_open_time_utc"],
                          "source_gap_next_open_time_utc": row["next_open_time_utc"]})
            cursor += INTERVAL_US
    slots.sort(key=lambda r: r["expected_open_time_us"])
    if len({r["expected_open_time_us"] for r in slots}) != len(slots):
        raise ValueError("duplicate missing 4h open time")
    return slots

def inspect_daily_archive(path, inventory_row):
    rec = {
        "date_utc": inventory_row.get("date", ""), "filename": path.name, "cache_path": str(path),
        "cache_status": "MISSING", "bytes": "", "local_sha256": "",
        "inventory_sha256": inventory_row.get("sha256_local", ""),
        "official_sha256_recorded": inventory_row.get("official_sha256", ""),
        "sidecar_sha256_recorded": inventory_row.get("sidecar_sha256", ""),
        "inventory_bytes": inventory_row.get("bytes", ""), "inventory_sha_status": "NOT_CHECKED",
        "inventory_bytes_status": "NOT_CHECKED", "zip_crc": "NOT_CHECKED",
        "csv_member": "", "rows": 0, "timestamp_unit": "", "timestamp_unit_status": "NOT_CHECKED",
        "open_grid_status": "NOT_CHECKED", "duplicate_open_times": 0, "error": ""
    }
    if not path.is_file():
        return rec, set()
    rec["cache_status"] = "PRESENT"
    rec["bytes"] = path.stat().st_size
    rec["local_sha256"] = sha256_file(path)
    rec["inventory_sha_status"] = "MATCH" if rec["local_sha256"] == rec["inventory_sha256"] and rec["local_sha256"] == rec["official_sha256_recorded"] else "MISMATCH"
    rec["inventory_bytes_status"] = "MATCH" if str(rec["bytes"]) == str(rec["inventory_bytes"]) else "MISMATCH"
    opens, raw_opens, units = set(), [], {}
    try:
        with zipfile.ZipFile(path, "r") as archive:
            bad = archive.testzip()
            if bad is not None:
                raise ValueError(f"ZIP CRC failure at {bad}")
            members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(members) != 1:
                raise ValueError(f"expected one CSV member, found {len(members)}")
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
                        raise ValueError(f"invalid open_time at line {line_no}")
                    normalized, unit = normalize_timestamp_to_us(value)
                    raw_opens.append(normalized)
                    opens.add(normalized)
                    units[unit] = units.get(unit, 0) + 1
        rec["zip_crc"] = "PASS"
        rec["rows"] = len(raw_opens)
        observed = sorted(units)
        rec["timestamp_unit"] = "EMPTY" if not observed else observed[0] if len(observed) == 1 else "MIXED"
        expected_unit = "microseconds" if rec["date_utc"] >= "2025-01-01" else "milliseconds"
        rec["timestamp_unit_status"] = "PASS" if observed == [expected_unit] else "FAIL"
        rec["open_grid_status"] = "PASS" if all(value % INTERVAL_US == 0 for value in raw_opens) else "FAIL"
        rec["duplicate_open_times"] = len(raw_opens) - len(opens)
        if rec["inventory_sha_status"] != "MATCH" or rec["inventory_bytes_status"] != "MATCH":
            rec["error"] = "cached ZIP does not match frozen inventory SHA/bytes"
        elif rec["timestamp_unit_status"] != "PASS":
            rec["error"] = f"timestamp unit mismatch: {rec['timestamp_unit']}"
        elif rec["open_grid_status"] != "PASS" or rec["duplicate_open_times"]:
            rec["error"] = "duplicate or off-grid daily 4h open timestamp"
    except Exception as exc:
        rec["zip_crc"] = "FAIL"
        rec["error"] = f"{type(exc).__name__}: {exc}"
        opens = set()
    valid = (rec["cache_status"] == "PRESENT" and rec["inventory_sha_status"] == "MATCH"
             and rec["inventory_bytes_status"] == "MATCH" and rec["zip_crc"] == "PASS"
             and rec["timestamp_unit_status"] == "PASS" and rec["open_grid_status"] == "PASS"
             and rec["duplicate_open_times"] == 0)
    return rec, opens if valid else None

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gaps-csv", default="results/cp0165_4h_archive_audit/CP0165_4H_Monthly_Checksum_Gap_Audit_Gaps.csv")
    parser.add_argument("--archive-inventory", default="evidence/source_adjudication/CP0040_Reconstruction_Run_38895499283/CP0040_Baseline_Reconstruction_Archive_Inventory.csv")
    parser.add_argument("--daily-cache", default=".cache/aists/binance-daily-references")
    parser.add_argument("--output-dir", default="results/cp0198_daily_reference_4h_exact_key_audit")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    gaps_path = (root / args.gaps_csv).resolve()
    inventory_path = (root / args.archive_inventory).resolve()
    cache_root = (root / args.daily_cache).resolve()
    out = (root / args.output_dir).resolve()
    for path in (gaps_path, inventory_path):
        if not path.is_file():
            raise FileNotFoundError(f"required frozen input missing: {path}")
    started = datetime.now(timezone.utc).isoformat()
    slots = read_gap_slots(gaps_path)
    all_inventory = read_csv(inventory_path)
    inventory = {
        (row.get("source"), row.get("interval"), row.get("filename")): row
        for row in all_inventory
    }
    dates = sorted({slot["date_utc"] for slot in slots})
    archive_rows, open_index = [], {}
    for date in dates:
        filename = f"BTCUSDT-4h-{date}.zip"
        inv = inventory.get(("daily_reference_cache", "4h", filename))
        if inv is None:
            archive_rows.append({"date_utc": date, "filename": filename, "cache_path": str(cache_root / "4h" / filename),
                                 "cache_status": "NO_FROZEN_INVENTORY_ROW", "inventory_sha_status": "UNAVAILABLE",
                                 "inventory_bytes_status": "UNAVAILABLE", "zip_crc": "NOT_CHECKED",
                                 "timestamp_unit_status": "NOT_CHECKED", "open_grid_status": "NOT_CHECKED",
                                 "error": "daily reference archive absent from frozen inventory"})
            open_index[date] = None
            continue
        path = cache_root / "4h" / filename
        record, opens = inspect_daily_archive(path, inv)
        archive_rows.append(record)
        open_index[date] = opens

    detail = []
    for slot in slots:
        date, timestamp = slot["date_utc"], slot["expected_open_time_us"]
        opens = open_index.get(date)
        row = {key: value for key, value in slot.items() if key != "expected_open_time_us"}
        row["daily_reference_archive_status"] = "UNAVAILABLE_OR_INVALID" if opens is None else "VALID"
        row["daily_reference_exact_open_key_present"] = "UNKNOWN" if opens is None else "YES" if timestamp in opens else "NO"
        row["daily_reference_open_times_for_date"] = "" if opens is None else len(opens)
        row["disposition"] = ("UNRESOLVED_DAILY_REFERENCE_UNAVAILABLE" if opens is None else
                              "DAILY_REFERENCE_EXACT_KEY_PRESENT_REQUIRES_ADJUDICATION" if timestamp in opens else
                              "ABSENT_FROM_VERIFIED_DAILY_REFERENCE_ARCHIVE")
        row["canonical_source"] = "NONE"
        row["source_case_closed"] = False
        detail.append(row)
    missing = sum(r["cache_status"] != "PRESENT" for r in archive_rows)
    invalid = sum(r["cache_status"] == "PRESENT" and (
        r.get("inventory_sha_status") != "MATCH" or r.get("inventory_bytes_status") != "MATCH"
        or r.get("zip_crc") != "PASS" or r.get("timestamp_unit_status") != "PASS"
        or r.get("open_grid_status") != "PASS" or int(r.get("duplicate_open_times") or 0) != 0)
        for r in archive_rows)
    exact = sum(r["daily_reference_exact_open_key_present"] == "YES" for r in detail)
    absent = sum(r["daily_reference_exact_open_key_present"] == "NO" for r in detail)
    unknown = sum(r["daily_reference_exact_open_key_present"] == "UNKNOWN" for r in detail)
    status = "REVIEW_REQUIRED_DAILY_REFERENCE_ARCHIVES_UNAVAILABLE_OR_INVALID" if missing or invalid or unknown else "PASS_DAILY_REFERENCE_EXACT_KEY_SCAN_COMPLETE_SOURCE_AUTHORITY_OPEN"
    summary = {
        "schema_version": 1, "checkpoint": "CP-0198", "task": "daily_reference_4h_exact_open_key_audit",
        "status": status, "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "gaps_csv_sha256": sha256_file(gaps_path), "inventory_sha256": sha256_file(inventory_path),
        "missing_4h_slots": len(detail), "unique_target_dates": len(dates),
        "daily_reference_archives_expected": len(dates), "daily_reference_archives_missing": missing,
        "daily_reference_archives_invalid": invalid, "exact_open_keys_present": exact,
        "exact_open_keys_absent_from_verified_daily_archive": absent, "exact_open_keys_unknown": unknown,
        "network_used": False, "archive_downloads": 0, "sidecar_requests": 0, "market_data_rest_api_used": False,
        "cached_source_archives_modified": False, "candles_created_or_repaired": False,
        "canonical_source": "NONE", "source_cases_closed": 0, "g0": "BLOCKED_GLOBAL",
        "backtest_run": False, "candidate_build": False, "strategy_promoted": False,
        "live_signing_broadcast_orders": "BLOCKED"
    }
    write_csv(out / "CP0198_DailyReference_4H_ExactKey_Matrix.csv", detail, [
        "expected_open_time_utc", "period", "date_utc", "source_gap_previous_open_time_utc",
        "source_gap_next_open_time_utc", "daily_reference_archive_status",
        "daily_reference_exact_open_key_present", "daily_reference_open_times_for_date",
        "disposition", "canonical_source", "source_case_closed"])
    write_csv(out / "CP0198_DailyReference_Archive_Manifest.csv", archive_rows, [
        "date_utc", "filename", "cache_path", "cache_status", "bytes", "local_sha256",
        "inventory_sha256", "official_sha256_recorded", "sidecar_sha256_recorded", "inventory_bytes",
        "inventory_sha_status", "inventory_bytes_status", "zip_crc", "csv_member", "rows",
        "timestamp_unit", "timestamp_unit_status", "open_grid_status", "duplicate_open_times", "error"])
    (out / "CP0198_Summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# CP-0198: Daily-reference 4h exact-open-key audit", "",
        f"- Status: {status}",
        f"- Missing 4h open-time slots checked: {len(detail)} across {len(dates)} dates.",
        f"- Frozen-inventory daily-reference archives missing: {missing}; invalid: {invalid}.",
        f"- Exact keys present in verified daily archives: {exact}; absent: {absent}; unknown: {unknown}.",
        "- This is exact-key evidence only. A daily-reference match does not by itself establish canonical-source authority.",
        "- No network, downloads, sidecar requests, cache mutation, candle reconstruction, backtest, candidate build, or live action occurred."
    ]
    (out / "CP0198_Report_HI.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "status", "missing_4h_slots", "unique_target_dates", "daily_reference_archives_expected",
        "daily_reference_archives_missing", "daily_reference_archives_invalid", "exact_open_keys_present",
        "exact_open_keys_absent_from_verified_daily_archive", "exact_open_keys_unknown", "network_used",
        "archive_downloads", "canonical_source", "g0", "live_signing_broadcast_orders")}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
