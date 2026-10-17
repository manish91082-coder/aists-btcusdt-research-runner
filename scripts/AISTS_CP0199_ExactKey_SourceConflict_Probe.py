#!/usr/bin/env python3
"""Read-only exact-key probe for 4h slots where monthly and daily reference archives disagree."""
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

def read_archive_rows(path):
    rows = []
    raw_opens = []
    unit_counts = {}
    with zipfile.ZipFile(path, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise ValueError(f"ZIP CRC failure at {bad}")
        members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(members) != 1:
            raise ValueError(f"expected one CSV member, found {len(members)}")
        member = members[0]
        import io
        with archive.open(member, "r") as raw:
            reader = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline=""))
            for line_no, row in enumerate(reader, 1):
                if not row:
                    continue
                try:
                    timestamp, unit = normalize_timestamp_to_us(row[0])
                except (ValueError, IndexError):
                    if line_no == 1:
                        continue
                    raise
                raw_opens.append(timestamp)
                unit_counts[unit] = unit_counts.get(unit, 0) + 1
                rows.append({"open_time_us": timestamp, "raw_tokens": row})
    counts = {}
    for row in rows:
        counts[row["open_time_us"]] = counts.get(row["open_time_us"], 0) + 1
    off_grid = sum(row["open_time_us"] % INTERVAL_US != 0 for row in rows)
    duplicates = sum(count - 1 for count in counts.values() if count > 1)
    return {
        "member": member, "rows": rows, "unit_counts": unit_counts,
        "timestamp_unit": next(iter(unit_counts)) if len(unit_counts) == 1 else "MIXED" if unit_counts else "EMPTY",
        "off_grid_rows": off_grid, "duplicate_open_times": duplicates,
        "zip_crc": "PASS", "unique_open_count": len(counts),
    }

def classify_presence(monthly_present, daily_present, monthly_tokens=None, daily_tokens=None):
    if monthly_present and daily_present:
        return "BOTH_PRESENT_ROW_TOKENS_MATCH" if monthly_tokens == daily_tokens else "BOTH_PRESENT_ROW_TOKEN_CONFLICT"
    if daily_present:
        return "DAILY_PRESENT_MONTHLY_MISSING_SOURCE_CONFLICT"
    if monthly_present:
        return "MONTHLY_PRESENT_DAILY_MISSING_SOURCE_CONFLICT"
    return "ABSENT_FROM_BOTH_CACHED_ARCHIVES"

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exact-key-matrix", default="results/cp0198_daily_reference_4h_exact_key_audit/CP0198_DailyReference_4H_ExactKey_Matrix.csv")
    parser.add_argument("--monthly-audit-details", default="results/cp0165_4h_archive_audit/CP0165_4H_Monthly_Checksum_Gap_Audit_Details.csv")
    parser.add_argument("--archive-inventory", default="evidence/source_adjudication/CP0040_Reconstruction_Run_38895499283/CP0040_Baseline_Reconstruction_Archive_Inventory.csv")
    parser.add_argument("--monthly-cache", default=".cache/aists/binance-monthly-archives")
    parser.add_argument("--daily-cache", default=".cache/aists/binance-daily-references")
    parser.add_argument("--output-dir", default="results/cp0199_exact_key_source_conflict_probe")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    matrix_path = (root / args.exact_key_matrix).resolve()
    details_path = (root / args.monthly_audit_details).resolve()
    inventory_path = (root / args.archive_inventory).resolve()
    monthly_root = (root / args.monthly_cache).resolve()
    daily_root = (root / args.daily_cache).resolve()
    out = (root / args.output_dir).resolve()
    for path in (matrix_path, details_path, inventory_path):
        if not path.is_file():
            raise FileNotFoundError(f"required frozen input missing: {path}")
    started = datetime.now(timezone.utc).isoformat()
    matrix = read_csv(matrix_path)
    monthly_details = {row["filename"]: row for row in read_csv(details_path)}
    inventory_rows = read_csv(inventory_path)
    inventory = {(r.get("source"), r.get("interval"), r.get("filename")): r for r in inventory_rows}
    monthly_data, daily_data, archive_manifest = {}, {}, []
    all_dates = sorted({r["date_utc"] for r in matrix})
    for date in all_dates:
        period = date[:7]
        monthly_name = f"BTCUSDT-4h-{period}.zip"
        daily_name = f"BTCUSDT-4h-{date}.zip"
        monthly_inv = inventory.get(("monthly_cache", "4h", monthly_name))
        daily_inv = inventory.get(("daily_reference_cache", "4h", daily_name))
        monthly_path = monthly_root / "4h" / period / monthly_name
        daily_path = daily_root / "4h" / daily_name
        monthly_record = {"archive_type": "monthly", "date_utc": date, "filename": monthly_name,
                          "cache_path": str(monthly_path), "status": "UNAVAILABLE"}
        daily_record = {"archive_type": "daily_reference", "date_utc": date, "filename": daily_name,
                        "cache_path": str(daily_path), "status": "UNAVAILABLE"}
        if monthly_inv and monthly_path.is_file():
            md = monthly_details.get(monthly_name, {})
            sha = sha256_file(monthly_path)
            size = monthly_path.stat().st_size
            try:
                data = read_archive_rows(monthly_path)
                ok = (sha == monthly_inv.get("sha256_local") == md.get("local_sha256")
                      and str(size) == str(monthly_inv.get("bytes"))
                      and md.get("checksum_status") == "MATCH" and md.get("zip_crc") == "PASS"
                      and data["zip_crc"] == "PASS" and data["off_grid_rows"] == 0
                      and data["duplicate_open_times"] == 0)
                monthly_record.update({"sha256": sha, "bytes": size, "inventory_sha_status": "MATCH" if sha == monthly_inv.get("sha256_local") else "MISMATCH",
                                       "official_sidecar_status_from_cp0165": md.get("checksum_status", "UNAVAILABLE"),
                                       "open_rows": len(data["rows"]), "off_grid_rows": data["off_grid_rows"],
                                       "duplicate_open_times": data["duplicate_open_times"], "status": "VALID" if ok else "INVALID",
                                       "error": "" if ok else "monthly archive failed checksum/grid/inventory gate"})
                monthly_data[date] = data if ok else None
            except Exception as exc:
                monthly_record.update({"sha256": sha, "bytes": size, "status": "INVALID", "error": f"{type(exc).__name__}: {exc}"})
                monthly_data[date] = None
        else:
            monthly_data[date] = None
            monthly_record["error"] = "monthly archive or frozen inventory row unavailable"
        if daily_inv and daily_path.is_file():
            sha = sha256_file(daily_path)
            size = daily_path.stat().st_size
            try:
                data = read_archive_rows(daily_path)
                ok = (sha == daily_inv.get("sha256_local") == daily_inv.get("official_sha256")
                      and str(size) == str(daily_inv.get("bytes"))
                      and daily_inv.get("zip_crc") == "PASS" and data["zip_crc"] == "PASS"
                      and data["off_grid_rows"] == 0 and data["duplicate_open_times"] == 0
                      and data["timestamp_unit"] == ("microseconds" if date >= "2025-01-01" else "milliseconds"))
                daily_record.update({"sha256": sha, "bytes": size, "inventory_sha_status": "MATCH" if sha == daily_inv.get("sha256_local") else "MISMATCH",
                                     "open_rows": len(data["rows"]), "off_grid_rows": data["off_grid_rows"],
                                     "duplicate_open_times": data["duplicate_open_times"], "status": "VALID" if ok else "INVALID",
                                     "error": "" if ok else "daily reference failed frozen inventory/grid gate"})
                daily_data[date] = data if ok else None
            except Exception as exc:
                daily_record.update({"sha256": sha, "bytes": size, "status": "INVALID", "error": f"{type(exc).__name__}: {exc}"})
                daily_data[date] = None
        else:
            daily_data[date] = None
            daily_record["error"] = "daily reference archive or frozen inventory row unavailable"
        archive_manifest.extend((monthly_record, daily_record))

    detail = []
    for slot in matrix:
        date = slot["date_utc"]
        target_us = int(datetime.fromisoformat(slot["expected_open_time_utc"].replace("Z", "+00:00")).timestamp() * 1_000_000)
        monthly, daily = monthly_data.get(date), daily_data.get(date)
        monthly_rows = monthly["rows"] if monthly else []
        daily_rows = daily["rows"] if daily else []
        monthly_by_key = {r["open_time_us"]: r["raw_tokens"] for r in monthly_rows}
        daily_by_key = {r["open_time_us"]: r["raw_tokens"] for r in daily_rows}
        exact_m = target_us in monthly_by_key
        exact_d = target_us in daily_by_key
        prev = max((k for k in monthly_by_key if k < target_us), default=None)
        nxt = min((k for k in monthly_by_key if k > target_us), default=None)
        disposition = "UNRESOLVED_ARCHIVE_UNAVAILABLE_OR_INVALID" if monthly is None or daily is None else classify_presence(exact_m, exact_d, monthly_by_key.get(target_us), daily_by_key.get(target_us))
        detail.append({
            "expected_open_time_utc": slot["expected_open_time_utc"], "date_utc": date,
            "monthly_archive_status": "VALID" if monthly else "UNAVAILABLE_OR_INVALID",
            "daily_reference_archive_status": "VALID" if daily else "UNAVAILABLE_OR_INVALID",
            "monthly_exact_open_key_present": "YES" if exact_m else "NO" if monthly else "UNKNOWN",
            "daily_exact_open_key_present": "YES" if exact_d else "NO" if daily else "UNKNOWN",
            "monthly_previous_open_time_utc": timestamp_to_iso(prev) if prev is not None else "",
            "monthly_next_open_time_utc": timestamp_to_iso(nxt) if nxt is not None else "",
            "daily_exact_row_raw_tokens_json": json.dumps(daily_by_key.get(target_us), separators=(",", ":")) if exact_d else "",
            "monthly_exact_row_raw_tokens_json": json.dumps(monthly_by_key.get(target_us), separators=(",", ":")) if exact_m else "",
            "monthly_previous_row_raw_tokens_json": json.dumps(monthly_by_key.get(prev), separators=(",", ":")) if prev is not None else "",
            "monthly_next_row_raw_tokens_json": json.dumps(monthly_by_key.get(nxt), separators=(",", ":")) if nxt is not None else "",
            "disposition": disposition, "canonical_source": "NONE", "source_case_closed": False
        })
    conflicts = sum("SOURCE_CONFLICT" in r["disposition"] or "ROW_TOKEN_CONFLICT" in r["disposition"] for r in detail)
    unknown = sum("UNRESOLVED" in r["disposition"] for r in detail)
    status = "REVIEW_REQUIRED_EXACT_KEY_SOURCE_CONFLICTS" if conflicts else "REVIEW_REQUIRED_ARCHIVE_EVIDENCE_UNAVAILABLE" if unknown else "PASS_EXACT_KEY_COMPARISON_COMPLETE_SOURCE_AUTHORITY_OPEN"
    summary = {
        "schema_version": 1, "checkpoint": "CP-0199", "task": "exact_key_source_conflict_probe",
        "status": status, "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "exact_key_rows_compared": len(detail), "source_conflict_rows": conflicts, "unresolved_rows": unknown,
        "daily_exact_keys_present": sum(r["daily_exact_open_key_present"] == "YES" for r in detail),
        "monthly_exact_keys_present": sum(r["monthly_exact_open_key_present"] == "YES" for r in detail),
        "monthly_archives_valid": sum(r["status"] == "VALID" for r in archive_manifest if r["archive_type"] == "monthly"),
        "daily_reference_archives_valid": sum(r["status"] == "VALID" for r in archive_manifest if r["archive_type"] == "daily_reference"),
        "network_used": False, "archive_downloads": 0, "sidecar_requests": 0, "market_data_rest_api_used": False,
        "cached_source_archives_modified": False, "candles_created_or_repaired": False,
        "canonical_source": "NONE", "source_cases_closed": 0, "g0": "BLOCKED_GLOBAL",
        "backtest_run": False, "candidate_build": False, "strategy_promoted": False,
        "live_signing_broadcast_orders": "BLOCKED"
    }
    write_csv(out / "CP0199_ExactKey_SourceConflict_Matrix.csv", detail, [
        "expected_open_time_utc", "date_utc", "monthly_archive_status", "daily_reference_archive_status",
        "monthly_exact_open_key_present", "daily_exact_open_key_present",
        "monthly_previous_open_time_utc", "monthly_next_open_time_utc",
        "daily_exact_row_raw_tokens_json", "monthly_exact_row_raw_tokens_json",
        "monthly_previous_row_raw_tokens_json", "monthly_next_row_raw_tokens_json",
        "disposition", "canonical_source", "source_case_closed"])
    write_csv(out / "CP0199_Archive_Integrity_Manifest.csv", archive_manifest, [
        "archive_type", "date_utc", "filename", "cache_path", "status", "sha256", "bytes",
        "inventory_sha_status", "official_sidecar_status_from_cp0165", "open_rows",
        "off_grid_rows", "duplicate_open_times", "error"])
    (out / "CP0199_Summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# CP-0199: Exact-key source conflict probe", "",
        f"- Status: {status}",
        f"- Exact 4h keys compared: {len(detail)}; source-conflict rows: {conflicts}; unresolved rows: {unknown}.",
        f"- Valid monthly archives: {summary['monthly_archives_valid']}; valid daily-reference archives: {summary['daily_reference_archives_valid']}.",
        "- Raw row tokens and immediate monthly neighbors are preserved for every target key.",
        "- A daily/monthly exact-key conflict is evidence for adjudication, not a decision that either source is canonical.",
        "- No network, downloads, sidecar requests, cache mutation, candle reconstruction, backtest, candidate build, or live action occurred."
    ]
    (out / "CP0199_Report_HI.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "status", "exact_key_rows_compared", "source_conflict_rows", "unresolved_rows",
        "daily_exact_keys_present", "monthly_exact_keys_present", "monthly_archives_valid",
        "daily_reference_archives_valid", "network_used", "archive_downloads",
        "canonical_source", "g0", "live_signing_broadcast_orders")}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
