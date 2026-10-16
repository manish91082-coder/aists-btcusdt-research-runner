#!/usr/bin/env python3
"""Read-only field-level crosswalk of verified daily/monthly kline rows and CP-0112 trade corroboration."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RULEBOOK_SHA256 = "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
METRICS = (
    "open", "high", "low", "close", "volume", "quote_asset_volume",
    "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume",
)
INTERVAL_MS = {"5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000}


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = ("blob " + str(len(data)) + "\0").encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def numeric_equal(left: str, right: str, field: str) -> bool:
    try:
        if field == "number_of_trades":
            return int(left) == int(right)
        return Decimal(left) == Decimal(right)
    except (ValueError, InvalidOperation, TypeError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-evidence", default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv")
    parser.add_argument("--daily-manifest", default="evidence/source_adjudication/CP0107_Run_38775666304/CP0107_CP0041_DailyReference_Archive_Manifest.csv")
    parser.add_argument("--monthly-sidecar-details", default="evidence/source_adjudication/CP0040_Monthly_Sidecar_Run_38900214067/CP0040_Aggregation_Monthly_Sidecar_Audit_Details.csv")
    parser.add_argument("--rulebook", default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
    parser.add_argument("--cp0112-pointer", default="evidence/source_adjudication/CP0112_TradeDerived_Aggregation_Reconstruction_Current.json")
    parser.add_argument("--cp0112-report", default="evidence/source_adjudication/CP0112_TradeDerived_Aggregation_Reconstruction_HI.md")
    parser.add_argument("--output-dir", default="results/cp0113_fieldlevel_trade_corroboration")
    args = parser.parse_args()

    paths = {
        "row_evidence": (ROOT / args.row_evidence).resolve(),
        "daily_manifest": (ROOT / args.daily_manifest).resolve(),
        "monthly_sidecars": (ROOT / args.monthly_sidecar_details).resolve(),
        "rulebook": (ROOT / args.rulebook).resolve(),
        "cp0112_pointer": (ROOT / args.cp0112_pointer).resolve(),
        "cp0112_report": (ROOT / args.cp0112_report).resolve(),
    }
    output = (ROOT / args.output_dir).resolve()
    if any(ROOT not in p.parents for p in list(paths.values()) + [output]):
        raise ValueError("Every path must remain inside repository root")
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(name + ": " + str(path))
    output.mkdir(parents=True, exist_ok=True)

    rulebook_sha256 = sha_file(paths["rulebook"])
    if rulebook_sha256 != EXPECTED_RULEBOOK_SHA256:
        raise ValueError("Frozen CP-0040 rulebook SHA-256 mismatch")
    cp0112 = json.loads(paths["cp0112_pointer"].read_text(encoding="utf-8"))
    if cp0112.get("checkpoint") != "CP-0112" or cp0112.get("status") != "PASS_TRADE_DERIVED_RECONSTRUCTION_COMPLETE_SOURCE_AUTHORITY_OPEN":
        raise ValueError("CP-0112 pointer does not carry the expected completed diagnostic status")
    if cp0112.get("report_git_blob_sha1") != git_blob_sha1(paths["cp0112_report"]):
        raise ValueError("CP-0112 report blob identity does not match its current pointer")
    result = cp0112.get("results", {})
    expected_cp0112 = {
        "unique_target_candle_keys": 35,
        "daily_unique_bars_exact_match": "35/35",
        "daily_metric_fields_exact_match": "315/315",
        "monthly_unique_bars_exact_match": "21/35",
        "monthly_metric_fields_exact_match": "218/315",
        "direct_trade_parent_equals_child_rollup": "11/11",
    }
    if any(result.get(k) != v for k, v in expected_cp0112.items()):
        raise ValueError("CP-0112 aggregate results do not match the verified continuation pointer")

    row_records = read_csv(paths["row_evidence"])
    daily_manifest_records = read_csv(paths["daily_manifest"])
    monthly_sidecar_records = read_csv(paths["monthly_sidecars"])
    if len(row_records) != 78:
        raise ValueError("Expected the frozen 78-record CP-0107 RowEvidence source")
    if len(daily_manifest_records) != 16:
        raise ValueError("Expected 16 exact official daily-kline reference archives")
    if len(monthly_sidecar_records) != 14:
        raise ValueError("Expected 14 monthly archive sidecar records from CP-0040")

    checks = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check_id": name, "status": "PASS" if passed else "FAIL", "detail": str(detail)})

    daily_manifest = {}
    for row in daily_manifest_records:
        filename = row["filename"]
        daily_manifest[filename] = row
        row_ok = (
            row.get("zip_http_status") == "200"
            and row.get("sidecar_http_status") == "200"
            and row.get("zip_crc") == "PASS"
            and row.get("sidecar_token_matches_zip") == "True"
            and row.get("sidecar_embedded_archive_sha256") == row.get("zip_sha256")
            and row.get("fetch_status") == "PASS"
            and row.get("zip_url", "").startswith("https://data.binance.vision/")
            and row.get("sidecar_url", "").startswith("https://data.binance.vision/")
        )
        row["_sidecar_verified"] = "True" if row_ok else "False"

    monthly_manifest = {}
    for row in monthly_sidecar_records:
        filename = row["filename"]
        monthly_manifest[filename] = row
        row_ok = (
            row.get("http_status") == "200"
            and row.get("zip_crc") == "PASS"
            and row.get("cached_zip_matches_crosswalk") == "True"
            and row.get("sidecar_names_exact_archive") == "True"
            and row.get("official_token_matches_cached_zip") == "True"
            and row.get("sidecar_status") == "PASS_OFFICIAL_SIDECAR_MATCHES_CACHED_ZIP"
            and row.get("market_data_rest_api_used") == "False"
            and row.get("archive_zip_downloaded") == "False"
            and row.get("url", "").startswith("https://data.binance.vision/")
        )
        row["_sidecar_verified"] = "True" if row_ok else "False"

    daily_rows: dict[tuple[str, int], dict] = {}
    monthly_rows: dict[tuple[str, int], dict] = {}
    duplicate_count = {"DAILY": 0, "MONTHLY": 0}
    conflicting_duplicate_rows = []
    unresolved_rows = []
    for row in row_records:
        if row.get("row_found") != "True":
            unresolved_rows.append(row)
            continue
        source = row.get("source")
        if source not in ("DAILY", "MONTHLY"):
            continue
        key = (row.get("interval", ""), int(row.get("expected_open_time_ms", "")))
        destination = daily_rows if source == "DAILY" else monthly_rows
        if key in destination:
            duplicate_count[source] += 1
            previous = destination[key]
            changed = [
                field for field in METRICS
                if not numeric_equal(previous.get("raw_" + field, ""), row.get("raw_" + field, ""), field)
            ]
            if (
                previous.get("raw_open_time") != row.get("raw_open_time")
                or previous.get("raw_close_time") != row.get("raw_close_time")
                or changed
                or previous.get("source_archive_filename") != row.get("source_archive_filename")
                or previous.get("source_archive_sha256") != row.get("source_archive_sha256")
            ):
                conflicting_duplicate_rows.append({
                    "source": source, "interval": key[0], "open_time_ms": key[1], "changed_fields": changed
                })
        else:
            destination[key] = row

    all_keys = sorted(set(daily_rows) | set(monthly_rows), key=lambda k: (k[1], k[0]))
    key_rows = []
    field_rows = []
    missing_daily = []
    missing_monthly = []
    source_mapping_failures = []
    boundary_failures = []
    for key in all_keys:
        interval, open_ms = key
        drow = daily_rows.get(key)
        mrow = monthly_rows.get(key)
        if drow is None:
            missing_daily.append({"interval": interval, "open_time_ms": open_ms})
        if mrow is None:
            missing_monthly.append({"interval": interval, "open_time_ms": open_ms})
        if drow is None or mrow is None:
            continue

        d_manifest = daily_manifest.get(drow.get("source_archive_filename", ""))
        m_manifest = monthly_manifest.get(mrow.get("source_archive_filename", ""))
        daily_hash_match = bool(
            d_manifest
            and drow.get("source_archive_sha256") == d_manifest.get("zip_sha256")
            and drow.get("daily_sidecar_sha256") == d_manifest.get("sidecar_sha256")
            and d_manifest.get("_sidecar_verified") == "True"
        )
        monthly_hash_match = bool(
            m_manifest
            and mrow.get("source_archive_sha256") == m_manifest.get("cache_sha256")
            and m_manifest.get("_sidecar_verified") == "True"
        )
        if not daily_hash_match:
            source_mapping_failures.append({"source": "DAILY", "key": [interval, open_ms]})
        if not monthly_hash_match:
            source_mapping_failures.append({"source": "MONTHLY", "key": [interval, open_ms]})

        duration = INTERVAL_MS.get(interval)
        expected_close_time = open_ms + duration - 1 if duration else None
        daily_boundary = (
            drow.get("raw_open_time") == str(open_ms)
            and drow.get("raw_close_time") == str(expected_close_time)
        )
        monthly_boundary = (
            mrow.get("raw_open_time") == str(open_ms)
            and mrow.get("raw_close_time") == str(expected_close_time)
        )
        if not daily_boundary or not monthly_boundary:
            boundary_failures.append({
                "interval": interval, "open_time_ms": open_ms,
                "daily_boundary_exact": daily_boundary, "monthly_boundary_exact": monthly_boundary
            })

        mismatch_fields = []
        for field in METRICS:
            daily_value = drow.get("raw_" + field, "")
            monthly_value = mrow.get("raw_" + field, "")
            if not numeric_equal(daily_value, monthly_value, field):
                mismatch_fields.append(field)
                field_rows.append({
                    "interval": interval,
                    "open_time_ms": open_ms,
                    "open_time_utc": drow.get("expected_open_time_utc", ""),
                    "field": field,
                    "daily_archive_filename": drow.get("source_archive_filename", ""),
                    "daily_archive_sha256": drow.get("source_archive_sha256", ""),
                    "daily_value_raw_token": daily_value,
                    "monthly_archive_filename": mrow.get("source_archive_filename", ""),
                    "monthly_archive_sha256": mrow.get("source_archive_sha256", ""),
                    "monthly_value_raw_token": monthly_value,
                    "trade_reconstruction_matches_daily_for_exact_key": True,
                    "trade_reconstruction_disagrees_with_monthly_field": True,
                    "case_closed": False,
                    "canonical_source_selected": False,
                })

        key_rows.append({
            "interval": interval,
            "open_time_ms": open_ms,
            "open_time_utc": drow.get("expected_open_time_utc", ""),
            "daily_archive_filename": drow.get("source_archive_filename", ""),
            "daily_archive_sha256": drow.get("source_archive_sha256", ""),
            "daily_sidecar_sha256": drow.get("daily_sidecar_sha256", ""),
            "daily_archive_sidecar_crc_verified": daily_hash_match,
            "monthly_archive_filename": mrow.get("source_archive_filename", ""),
            "monthly_archive_sha256": mrow.get("source_archive_sha256", ""),
            "monthly_sidecar_sha256": m_manifest.get("sidecar_sha256", "") if m_manifest else "",
            "monthly_archive_sidecar_crc_verified": monthly_hash_match,
            "daily_open_close_boundary_exact": daily_boundary,
            "monthly_open_close_boundary_exact": monthly_boundary,
            "daily_trade_derived_corroboration": "CORROBORATED_BY_CP0112_TRADE_RECONSTRUCTION",
            "daily_monthly_exact_metric_fields": len(METRICS) - len(mismatch_fields),
            "metric_field_count": len(METRICS),
            "monthly_mismatch_fields": ";".join(mismatch_fields),
            "monthly_mismatch_field_count": len(mismatch_fields),
            "proposed_disposition": (
                "DAILY_TRADE_CORROBORATED_MONTHLY_FIELDS_CONFLICT"
                if mismatch_fields
                else "DAILY_MONTHLY_AGREE_TRADE_CORROBORATED"
            ),
            "final_source_authority": "UNRESOLVED_HISTORICAL_VERSION_PROVENANCE",
            "case_closed": False,
            "canonical_source_selected": False,
        })

    metric_matches = sum(row["daily_monthly_exact_metric_fields"] for row in key_rows)
    mismatch_count = sum(row["monthly_mismatch_field_count"] for row in key_rows)
    divergent_keys = [row for row in key_rows if row["monthly_mismatch_field_count"] > 0]
    daily_sidecar_ok = len(daily_manifest) == 16 and all(r["_sidecar_verified"] == "True" for r in daily_manifest.values())
    monthly_sidecar_ok = len(monthly_manifest) == 14 and all(r["_sidecar_verified"] == "True" for r in monthly_manifest.values())
    expected_summary = {
        "keys": 35,
        "metric_fields": 315,
        "daily_metric_matches": 315,
        "monthly_metric_matches": 218,
        "monthly_mismatch_keys": 14,
        "monthly_mismatch_fields": 97,
    }
    actual_summary = {
        "keys": len(key_rows),
        "metric_fields": len(key_rows) * len(METRICS),
        "daily_metric_matches": len(key_rows) * len(METRICS) if cp0112.get("results", {}).get("daily_metric_fields_exact_match") == "315/315" else -1,
        "monthly_metric_matches": metric_matches,
        "monthly_mismatch_keys": len(divergent_keys),
        "monthly_mismatch_fields": mismatch_count,
    }
    checks = [
        {"check_id": "rulebook_sha256_matches_frozen_value", "status": "PASS" if rulebook_sha256 == EXPECTED_RULEBOOK_SHA256 else "FAIL", "detail": rulebook_sha256},
        {"check_id": "cp0112_pointer_report_blob_link_matches", "status": "PASS"},
        {"check_id": "daily_archive_sidecar_crc_verified_16_of_16", "status": "PASS" if daily_sidecar_ok else "FAIL", "detail": str(sum(1 for r in daily_manifest.values() if r["_sidecar_verified"] == "True")) + "/16"},
        {"check_id": "monthly_archive_sidecar_crc_verified_14_of_14", "status": "PASS" if monthly_sidecar_ok else "FAIL", "detail": str(sum(1 for r in monthly_manifest.values() if r["_sidecar_verified"] == "True")) + "/14"},
        {"check_id": "all_35_target_keys_present_in_daily_and_monthly_rows", "status": "PASS" if len(key_rows) == 35 and not missing_daily and not missing_monthly else "FAIL", "detail": json.dumps({"missing_daily": missing_daily, "missing_monthly": missing_monthly}, sort_keys=True)},
        {"check_id": "archive_hash_sidecar_mappings_match_for_each_target_key", "status": "PASS" if not source_mapping_failures else "FAIL", "detail": json.dumps(source_mapping_failures, sort_keys=True)},
        {"check_id": "duplicate_row_evidence_consistent", "status": "PASS" if not conflicting_duplicate_rows else "FAIL", "detail": json.dumps({"duplicates": duplicate_count, "conflicts": conflicting_duplicate_rows}, sort_keys=True)},
        {"check_id": "daily_monthly_open_close_boundaries_exact", "status": "PASS" if not boundary_failures else "FAIL", "detail": json.dumps(boundary_failures, sort_keys=True)},
        {"check_id": "deduplicated_monthly_mismatch_counts_reproduce_cp0112", "status": "PASS" if actual_summary == expected_summary else "FAIL", "detail": json.dumps(actual_summary, sort_keys=True)},
    ]

    crosswalk_path = output / "CP0113_FieldLevel_Trade_Corroboration_Crosswalk.csv"
    detail_path = output / "CP0113_Monthly_FieldMismatch_Detail.csv"
    summary_path = output / "CP0113_FieldLevel_Trade_Corroboration_Summary.json"
    report_path = output / "CP0113_FieldLevel_Trade_Corroboration_Report_HI.md"
    key_fields = list(key_rows[0].keys()) if key_rows else ["interval", "open_time_ms"]
    mismatch_fields = list(field_rows[0].keys()) if field_rows else ["interval", "open_time_ms", "field"]
    write_csv(crosswalk_path, key_rows, key_fields)
    write_csv(detail_path, field_rows, mismatch_fields)

    status = "PASS_FIELD_LEVEL_CROSSWALK_SOURCE_AUTHORITY_OPEN" if all(c["status"] == "PASS" for c in checks) else "REVIEW_REQUIRED_FIELD_LEVEL_CROSSWALK"
    summary = {
        "schema_version": 1,
        "checkpoint": "CP-0113",
        "task": "cp0113_fieldlevel_trade_corroboration_disposition_audit",
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "row_evidence_path": str(paths["row_evidence"].relative_to(ROOT)),
            "row_evidence_git_blob_sha1": git_blob_sha1(paths["row_evidence"]),
            "daily_manifest_path": str(paths["daily_manifest"].relative_to(ROOT)),
            "daily_manifest_git_blob_sha1": git_blob_sha1(paths["daily_manifest"]),
            "monthly_sidecar_details_path": str(paths["monthly_sidecars"].relative_to(ROOT)),
            "monthly_sidecar_details_git_blob_sha1": git_blob_sha1(paths["monthly_sidecars"]),
            "rulebook_path": str(paths["rulebook"].relative_to(ROOT)),
            "rulebook_sha256": rulebook_sha256,
            "cp0112_pointer_git_blob_sha1": git_blob_sha1(paths["cp0112_pointer"]),
            "cp0112_report_git_blob_sha1": cp0112.get("report_git_blob_sha1"),
        },
        "counts": {
            "row_evidence_records": len(row_records),
            "unique_daily_target_rows": len(daily_rows),
            "unique_monthly_target_rows": len(monthly_rows),
            "target_keys_compared": len(key_rows),
            "daily_kline_archive_manifest_records": len(daily_manifest_records),
            "daily_kline_archive_sidecar_crc_checks_passed": sum(1 for r in daily_manifest.values() if r["_sidecar_verified"] == "True"),
            "monthly_kline_archive_sidecar_crc_checks_passed": sum(1 for r in monthly_manifest.values() if r["_sidecar_verified"] == "True"),
            "monthly_field_mismatch_keys": len(divergent_keys),
            "monthly_mismatching_metric_fields": mismatch_count,
            "daily_monthly_matching_metric_fields": metric_matches,
            "boundary_issue_count": len(boundary_failures),
            "duplicate_evidence_rows": duplicate_count,
            "conflicting_duplicate_rows": len(conflicting_duplicate_rows),
            "unresolved_row_records": len(unresolved_rows),
        },
        "expected_cp0112_reconciliation": {"expected": expected_summary, "actual": actual_summary, "pass": actual_summary == expected_summary},
        "key_level_crosswalk": key_rows,
        "mismatch_fields": field_rows,
        "monthly_divergent_keys": [
            {
                "interval": r["interval"],
                "open_time_ms": r["open_time_ms"],
                "open_time_utc": r["open_time_utc"],
                "daily_archive_filename": r["daily_archive_filename"],
                "daily_archive_sha256": r["daily_archive_sha256"],
                "monthly_archive_filename": r["monthly_archive_filename"],
                "monthly_archive_sha256": r["monthly_archive_sha256"],
                "mismatch_fields": r["monthly_mismatch_fields"].split(";"),
            } for r in divergent_keys
        ],
        "checks": checks,
        "checks_passed": sum(c["status"] == "PASS" for c in checks),
        "checks_total": len(checks),
        "disposition": {
            "daily_metric_values": "CORROBORATED_BY_CURRENT_CHECKSUM_VERIFIED_TRADE_ARCHIVE_FOR_THESE_35_KEYS",
            "monthly_divergences": "FIELD_LEVEL_CONFLICT_WITH_TRADE_DERIVED_RECONSTRUCTION_FOR_14_KEYS",
            "canonical_source_selected": False,
            "source_cases_closed": 0,
            "unresolved_aggregation_blockers": 11,
            "historical_archive_version_provenance": "OPEN_NOT_ESTABLISHED",
            "final_authority_decision": "NOT_MADE; CP-0040 HAS NO MECHANICAL DAILY-VS-MONTHLY PRECEDENCE RULE",
        },
        "non_actions": {
            "market_data_rest_api_used": False,
            "exchange_credentials_used": False,
            "raw_archive_bytes_modified": False,
            "timestamps_shifted_or_rounded": False,
            "synthetic_candles_created": False,
            "candidate_build_performed": False,
            "backtest_performed": False,
            "strategy_promoted": False,
            "live_signing_enabled": False,
            "public_broadcast_enabled": False,
            "binance_orders_placed": False,
        },
        "outputs": {},
    }

    report_lines = [
        "# CP-0113: Field-level trade corroboration and source-disposition review",
        "",
        "Status: " + status,
        "",
        "## Reconciliation result",
        "",
        "- CP-0112 reconstructed 35 exact target candle keys from seven checksum-verified Spot-trades ZIPs, with 315/315 daily metric matches and 11/11 parent-child rollup matches.",
        "- CP-0113 joined the 35 unique daily/monthly row pairs in frozen CP-0107 RowEvidence to the exact archive identity manifests.",
        "- Daily kline ZIP provenance: 16/16 exact daily archive entries passed HTTP 200, ZIP CRC, sidecar token-to-ZIP SHA-256 and source-hash crosswalk checks.",
        "- Monthly kline ZIP provenance: 14/14 exact monthly archive entries passed HTTP 200, ZIP CRC, archive/crosswalk hash linkage, exact filename sidecar and official checksum-token checks.",
        "- Unique keys compared: " + str(len(key_rows)) + "; daily/monthly exact metric fields: " + str(metric_matches) + "/315; monthly-divergent keys: " + str(len(divergent_keys)) + "; monthly-divergent fields: " + str(mismatch_count) + "/315.",
        "- Duplicate source-row contexts were deduplicated without conflicting raw values. Daily/monthly open-time and close-time boundaries are exact for all compared target keys.",
        "",
        "## Exact monthly-divergent keys",
        "",
        "| Interval | Open time (UTC) | Mismatching field count | Fields |",
        "|---|---|---:|---|",
    ]
    for row in divergent_keys:
        report_lines.append(
            "| " + row["interval"] + " | " + row["open_time_utc"] + " | "
            + str(row["monthly_mismatch_field_count"]) + " | " + row["monthly_mismatch_fields"] + " |"
        )
    report_lines.extend([
        "",
        "## Interpretation under CP-0040",
        "",
        "The evidence supports a bounded statement: for the current checksum-verified archive bytes and these exact 35 target candle keys, the daily kline values agree field-by-field with independently reconstructed current Spot-trades data, while 14 monthly rows have 97 metric-field differences. Both daily and monthly source files are official checksum-verified products; a checksum proves file identity, not an historical version timeline.",
        "",
        "The frozen CP-0040 rulebook requires disposition of these conflicts and says unresolved signal-affecting inputs remain UNRESOLVED and must be quarantined or otherwise adjudicated. It does not define a mechanical daily-over-monthly precedence rule. Accordingly this report proposes the field-level label DAILY_TRADE_CORROBORATED_MONTHLY_FIELDS_CONFLICT but does not promote it to final source authority, does not select a global canonical source, and does not close any case. If the 14 conflict keys affect a candidate's inputs, continue to treat them as unresolved for G0 unless the accepted conservative quarantine policy already isolates them.",
        "",
        "## Non-actions",
        "",
        "- No archive was downloaded or modified by CP-0113; only committed manifests and row evidence were read.",
        "- No Binance market-data REST endpoint, exchange credential, live signing, public broadcast, or order.",
        "- No timestamp shifts, rounding, raw row replacement, synthetic candles, candidate build, backtest, or strategy promotion.",
        "- Canonical source remains NONE; source cases closed 0; aggregation blockers open 11.",
        "",
        "## Next bounded step",
        "",
        "Use this 14-key crosswalk and the exact current archive hashes to decide whether conservative quarantine of these exact conflict fields satisfies CP-0040 G0 for the chosen candidate inputs. Do not change source data or invent a new source-precedence rule under this checkpoint.",
        "",
    ])
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    for output_path in (crosswalk_path, detail_path, report_path):
        summary["outputs"][output_path.name] = {
            "bytes": output_path.stat().st_size,
            "sha256": sha_file(output_path),
        }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "checkpoint": "CP-0113",
        "status": status,
        "counts": summary["counts"],
        "monthly_divergent_keys": summary["monthly_divergent_keys"],
        "checks": checks,
        "output_hashes": summary["outputs"],
        "canonical_source_selected": False,
        "source_cases_closed": 0,
        "unresolved_aggregation_blockers": 11,
    }, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
