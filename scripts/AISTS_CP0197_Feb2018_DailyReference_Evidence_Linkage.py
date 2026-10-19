#!/usr/bin/env python3
"""Link CP-0192 gap slots to already-committed CP-0107 February 2018 evidence; no network."""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def normalize_ms_to_us(value):
    value = int(value)
    if 1_000_000_000_000 <= value < 100_000_000_000_000:
        return value * 1000
    if 1_000_000_000_000_000 <= value < 100_000_000_000_000_000:
        return value
    raise ValueError(f"unsupported epoch timestamp magnitude: {value}")

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage-csv", default="results/cp0192_cross_interval_gap_triage/CP0192_Cross_Interval_Gap_Triage.csv")
    parser.add_argument("--prior-evidence-dir", default="evidence/source_adjudication/CP0107_Run_38777979719")
    parser.add_argument("--output-dir", default="results/cp0197_feb2018_evidence_linkage")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    triage_path = (root / args.triage_csv).resolve()
    prior = (root / args.prior_evidence_dir).resolve()
    out = (root / args.output_dir).resolve()
    summary_path = prior / "CP0107_Feb2018_Extraction_Summary.json"
    daily_path = prior / "CP0107_Feb2018_DailyCoverage_RawRows.csv"
    offgrid_path = prior / "CP0107_Feb2018_OffGrid_RawRows.csv"
    verification_path = prior / "CP0107_Feb2018_SourceVerification.csv"
    for path in (triage_path, summary_path, daily_path, offgrid_path, verification_path):
        if not path.is_file():
            raise FileNotFoundError(f"required existing evidence missing: {path}")
    triage_hash = sha256_file(triage_path)
    prior_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expected_outputs = prior_summary.get("outputs", {})
    hash_checks = []
    for path, key in ((daily_path, "CP0107_Feb2018_DailyCoverage_RawRows.csv"),
                      (offgrid_path, "CP0107_Feb2018_OffGrid_RawRows.csv")):
        expected = expected_outputs.get(key, {})
        actual_sha = sha256_file(path)
        actual_bytes = path.stat().st_size
        hash_checks.append({
            "file": path.name,
            "expected_sha256": expected.get("sha256", ""),
            "actual_sha256": actual_sha,
            "expected_bytes": expected.get("bytes", ""),
            "actual_bytes": actual_bytes,
            "status": "PASS" if actual_sha == expected.get("sha256") and actual_bytes == expected.get("bytes") else "FAIL",
        })
    if any(item["status"] != "PASS" for item in hash_checks):
        raise ValueError("CP-0107 prior evidence hash/byte verification failed; refusing linkage")
    daily_rows = read_csv(daily_path)
    offgrid_rows = read_csv(offgrid_path)
    source_rows = read_csv(verification_path)
    by_date_interval = {}
    for row in daily_rows:
        interval = row.get("interval", "")
        if interval not in ("5m", "1h"):
            continue
        key = (row.get("date", ""), interval)
        by_date_interval.setdefault(key, []).append(normalize_ms_to_us(row["open_time_ms"]))
    offgrid_by_date_interval = {}
    for row in offgrid_rows:
        interval = row.get("interval", "")
        if interval not in ("5m", "1h"):
            continue
        key = (row.get("date", ""), interval)
        offgrid_by_date_interval.setdefault(key, []).append(normalize_ms_to_us(row["open_time_ms"]))

    slots = read_csv(triage_path)
    linkage = []
    for slot in slots:
        iso = datetime.fromisoformat(slot["expected_open_time_utc"].replace("Z", "+00:00"))
        start_us = int(iso.timestamp() * 1_000_000)
        end_us = start_us + 4 * 60 * 60 * 1_000_000
        date = iso.strftime("%Y-%m-%d")
        row = {
            "expected_open_time_utc": slot["expected_open_time_utc"],
            "period": slot.get("period", date[:7]),
            "date_utc": date,
            "prior_cp0107_daily_rows_for_date": "YES" if any(k[0] == date for k in by_date_interval) else "NO",
            "prior_cp0107_offgrid_rows_for_date": "YES" if any(k[0] == date for k in offgrid_by_date_interval) else "NO",
        }
        total_daily_in_window = 0
        total_offgrid_in_window = 0
        for interval in ("5m", "1h"):
            opens = by_date_interval.get((date, interval), [])
            offgrid = offgrid_by_date_interval.get((date, interval), [])
            in_window = [value for value in opens if start_us <= value < end_us]
            offgrid_in_window = [value for value in offgrid if start_us <= value < end_us]
            total_daily_in_window += len(in_window)
            total_offgrid_in_window += len(offgrid_in_window)
            row[f"cp0107_daily_{interval}_rows_on_date"] = len(opens)
            row[f"cp0107_daily_{interval}_rows_in_window"] = len(in_window)
            row[f"cp0107_daily_{interval}_first_open_utc"] = datetime.fromtimestamp(min(opens) / 1_000_000, timezone.utc).isoformat() if opens else ""
            row[f"cp0107_daily_{interval}_last_open_utc"] = datetime.fromtimestamp(max(opens) / 1_000_000, timezone.utc).isoformat() if opens else ""
            row[f"cp0107_monthly_offgrid_{interval}_rows_in_window"] = len(offgrid_in_window)
        row["cp0107_daily_rows_in_window_total"] = total_daily_in_window
        row["cp0107_monthly_offgrid_rows_in_window_total"] = total_offgrid_in_window
        if date == "2018-02-08":
            row["linkage_disposition"] = "UNRESOLVED_NO_PRIOR_DAILY_REFERENCE_FOR_DATE"
        elif date == "2018-02-09" and iso.hour in (0, 4):
            row["linkage_disposition"] = "DAILY_REFERENCE_DOES_NOT_COVER_TARGET_WINDOW"
        elif row["prior_cp0107_daily_rows_for_date"] == "NO":
            row["linkage_disposition"] = "OUTSIDE_CP0107_DAILY_EVIDENCE_SCOPE"
        elif total_daily_in_window == 0:
            row["linkage_disposition"] = "NO_CP0107_DAILY_ROWS_IN_TARGET_WINDOW"
        else:
            row["linkage_disposition"] = "DAILY_ROWS_PRESENT_EXACT_KEY_REVIEW_REQUIRED"
        row["canonical_source"] = "NONE"
        row["source_case_closed"] = False
        linkage.append(row)

    verification_counts = {}
    for item in source_rows:
        key = item.get("source", "") + ":" + item.get("checksum_validation", "")
        verification_counts[key] = verification_counts.get(key, 0) + 1
    feb8 = sum(r["date_utc"] == "2018-02-08" for r in linkage)
    feb9_early = sum(r["date_utc"] == "2018-02-09" and r["linkage_disposition"] == "DAILY_REFERENCE_DOES_NOT_COVER_TARGET_WINDOW" for r in linkage)
    outside_scope = sum(r["linkage_disposition"] == "OUTSIDE_CP0107_DAILY_EVIDENCE_SCOPE" for r in linkage)
    summary = {
        "schema_version": 1, "checkpoint": "CP-0197", "task": "existing_feb2018_daily_reference_evidence_linkage",
        "status": "PASS_PRIOR_EVIDENCE_HASHES_VERIFIED_LINKAGE_REVIEW_REQUIRED",
        "triage_csv_sha256": triage_hash, "prior_cp0107_summary_sha256": sha256_file(summary_path),
        "prior_evidence_hash_checks": hash_checks,
        "expected_missing_4h_slots_linked": len(linkage),
        "february_8_slots_without_daily_reference_evidence": feb8,
        "february_9_00_04_slots_daily_reference_does_not_cover": feb9_early,
        "slots_outside_cp0107_daily_evidence_scope": outside_scope,
        "daily_reference_rows": len(daily_rows), "offgrid_monthly_rows": len(offgrid_rows),
        "cp0107_source_verification_rows": len(source_rows), "cp0107_source_verification_counts": verification_counts,
        "network_used": False, "downloads": 0, "market_data_rest_api_used": False,
        "timestamps_shifted_or_rounded": False, "candles_created_or_repaired": False,
        "canonical_source": "NONE", "source_cases_closed": 0, "g0": "BLOCKED_GLOBAL",
        "backtest_run": False, "candidate_build": False, "strategy_promoted": False,
        "live_signing_broadcast_orders": "BLOCKED"
    }
    fields = [
        "expected_open_time_utc", "period", "date_utc", "prior_cp0107_daily_rows_for_date",
        "prior_cp0107_offgrid_rows_for_date", "cp0107_daily_5m_rows_on_date", "cp0107_daily_5m_rows_in_window",
        "cp0107_daily_5m_first_open_utc", "cp0107_daily_5m_last_open_utc",
        "cp0107_daily_1h_rows_on_date", "cp0107_daily_1h_rows_in_window",
        "cp0107_daily_1h_first_open_utc", "cp0107_daily_1h_last_open_utc",
        "cp0107_monthly_offgrid_5m_rows_in_window", "cp0107_monthly_offgrid_1h_rows_in_window",
        "cp0107_daily_rows_in_window_total", "cp0107_monthly_offgrid_rows_in_window_total",
        "linkage_disposition", "canonical_source", "source_case_closed"
    ]
    write_csv(out / "CP0197_Feb2018_DailyEvidence_Linkage.csv", linkage, fields)
    write_csv(out / "CP0197_PriorEvidence_HashChecks.csv", hash_checks,
              ["file", "expected_sha256", "actual_sha256", "expected_bytes", "actual_bytes", "status"])
    (out / "CP0197_Summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# CP-0197: Existing February 2018 evidence linkage", "",
        f"- Status: {summary['status']}",
        f"- Linked missing 4h slots: {len(linkage)}.",
        f"- Prior CP-0107 daily-coverage/off-grid CSV hash checks: {sum(x['status'] == 'PASS' for x in hash_checks)}/{len(hash_checks)} PASS.",
        f"- 2018-02-08 slots with no daily-reference evidence in CP-0107 scope: {feb8}.",
        f"- 2018-02-09 00:00/04:00 UTC slots outside the daily-reference rows' covered window: {feb9_early}.",
        f"- Other slots outside CP-0107 daily evidence scope: {outside_scope}.",
        f"- CP-0107 source verification rows: {len(source_rows)}; monthly archive status remains manifest-reference-only where recorded, not a fresh monthly sidecar verification.",
        "- This links existing evidence only. It does not assign canonical-source authority or close a source case.",
        "- No network, download, raw-data mutation, timestamp shift, interpolation, backtest, candidate build, or live action occurred."
    ]
    (out / "CP0197_Report_HI.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "status", "expected_missing_4h_slots_linked", "february_8_slots_without_daily_reference_evidence",
        "february_9_00_04_slots_daily_reference_does_not_cover", "slots_outside_cp0107_daily_evidence_scope",
        "network_used", "downloads", "canonical_source", "g0", "live_signing_broadcast_orders")}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
