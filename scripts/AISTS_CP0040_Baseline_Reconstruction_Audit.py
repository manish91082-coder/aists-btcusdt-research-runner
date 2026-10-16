#!/usr/bin/env python3
"""CP-0040 cache-only reconstruction audit for frozen CP-0031 candidate contents.

This deliberately does NOT call the CP-0026 production builder entry point and
does not select/approve a canonical source. It uses the builder's pure parsing/
serialization helpers in a temporary directory, then verifies decompressed
CSV bytes against committed anchors from the already verified local snapshot.
No network requests, cache writes, candidate promotion, or backtest.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERVALS = ("4h", "1d")
FIRST = (2017, 8)
LAST = (2026, 9)
SYMBOL = "BTCUSDT"
BUILDER_PATH = ROOT / "scripts" / "AISTS_CP0026_Research_Candidate_Builder.py"


class BlockedReconstruction(Exception):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def month_pairs():
    y, m = FIRST
    while (y, m) <= LAST:
        yield y, m
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1


def load_builder():
    spec = importlib.util.spec_from_file_location("aists_cp0026_reconstruction_helpers", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the reviewed CP-0026 helper module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def find_unique(root: Path, basename: str) -> Path:
    matches = [p for p in root.rglob(basename) if p.is_file()]
    if len(matches) != 1:
        raise BlockedReconstruction(
            f"Expected exactly one cached file named {basename}; found {len(matches)}"
        )
    return matches[0]


def validate_zip(path: Path) -> str:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            broken = zf.testzip()
            if broken is not None:
                raise BlockedReconstruction(f"ZIP CRC failure: {path.name}:{broken}")
            members = [x.filename for x in zf.infolist() if not x.is_dir()]
            csv_members = [name for name in members if name.lower().endswith(".csv")]
            if len(members) != 1 or len(csv_members) != 1:
                raise BlockedReconstruction(
                    f"Expected one regular CSV member in {path.name}; members={members}"
                )
            return csv_members[0]
    except zipfile.BadZipFile as exc:
        raise BlockedReconstruction(f"Invalid ZIP: {path.name}: {exc}") from exc


def official_sidecar_hash(path: Path, archive_name: str) -> str:
    text = path.read_text(encoding="utf-8-sig", errors="strict").strip()
    tokens = sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b", text)))
    if len(tokens) != 1 or archive_name not in text:
        raise BlockedReconstruction(
            f"Cached official checksum sidecar is ambiguous or not filename-bound: {path.name}"
        )
    return tokens[0]


def inspect_csv_gzip(path: Path, anchor: dict) -> dict:
    try:
        raw = gzip.decompress(path.read_bytes())
    except Exception as exc:
        raise BlockedReconstruction(f"Candidate GZIP cannot be decompressed: {path.name}: {exc}") from exc
    raw_sha = sha256_bytes(raw)
    try:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    except Exception as exc:
        raise BlockedReconstruction(f"Candidate CSV parse failed: {path.name}: {exc}") from exc
    header = list(rows[0].keys()) if rows else []
    matches = (
        raw_sha == anchor["decompressed_sha256"]
        and len(raw) == anchor["decompressed_bytes"]
        and len(rows) == anchor["rows"]
        and header == anchor["header"]
    )
    return {
        "file_name": path.name,
        "compressed_bytes": path.stat().st_size,
        "compressed_sha256_reconstructed": sha256_file(path),
        "compressed_sha256_original_anchor": anchor["compressed_sha256"],
        "compressed_bytes_hash_identical": sha256_file(path) == anchor["compressed_sha256"],
        "decompressed_bytes": len(raw),
        "decompressed_sha256": raw_sha,
        "decompressed_sha256_anchor": anchor["decompressed_sha256"],
        "rows": len(rows),
        "expected_rows": anchor["rows"],
        "header": header,
        "matches_frozen_content_anchor": matches,
        "interpretation": (
            "Decompressed CSV content must match exactly. The GZIP wrapper hash may differ "
            "because it can include a generation timestamp; this is recorded separately."
        ),
    }


def write_blocked(output: Path, anchors: dict, started: str, reason: str, checks: list[dict]):
    output.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema_version": 1,
        "checkpoint": "CP-0040",
        "task": "cp0040_baseline_reconstruction_audit",
        "status": "BLOCKED_INPUTS_NOT_REPRODUCIBLE",
        "started_at_utc": started,
        "finished_at_utc": utc_now(),
        "scope": "CACHE_ONLY_TEMPORARY_BASELINE_CONTENT_RECONSTRUCTION",
        "network_used": False,
        "market_data_downloads": 0,
        "cache_source_roots": [
            ".cache/aists/binance-monthly-archives",
            ".cache/aists/binance-daily-references",
        ],
        "production_candidate_build": False,
        "backtest_run": False,
        "signal_or_position_comparison": False,
        "strategy_promoted": False,
        "anchor_file": "evidence/source_adjudication/CP0040_Baseline_Reconstruction_Anchors.json",
        "snapshot_sha256": anchors.get("created_from", {}).get("package_sha256"),
        "blocking_reason": reason,
        "checks": checks,
        "limitations": [
            "This task never downloads archives or repairs missing cache bytes.",
            "Monthly cache archive hashes are measured locally only; the exact final candidate-content anchor is the acceptance test for this reconstruction.",
            "A block means the later quarantine-sensitivity comparison must not run.",
        ],
        "gate": {
            "g0": "BLOCKED_GLOBAL",
            "unresolved_nonrow_aggregation_blockers": 11,
            "canonical_source": "NONE",
            "candidate_promotion": "BLOCKED",
            "live_signing_broadcast_orders": "BLOCKED",
        },
    }
    (output / "CP0040_Baseline_Reconstruction_Audit_Summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    report = [
        "# CP-0040 Baseline Reconstruction Audit",
        "",
        f"- Status: `{summary['status']}`",
        "- Scope: temporary, cache-only reconstruction of the frozen CP-0031 candidate input contents.",
        "- Network/downloads: none.",
        f"- Blocking reason: {reason}",
        "- No production candidate build, backtest, signal comparison, or promotion was run.",
        "",
        "## Checks",
    ]
    report.extend(f"- {x['status']}: {x['check_id']} | {x['detail']}" for x in checks)
    report += [
        "",
        "## Gate",
        "- G0 remains `BLOCKED_GLOBAL`; 11 non-row aggregation blockers remain open.",
        "- Canonical source remains `NONE`; promotion and all live exchange actions remain blocked.",
    ]
    (output / "CP0040_Baseline_Reconstruction_Audit_Report_HI.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--monthly-cache", default=".cache/aists/binance-monthly-archives")
    ap.add_argument("--daily-cache", default=".cache/aists/binance-daily-references")
    ap.add_argument("--anchors", default="evidence/source_adjudication/CP0040_Baseline_Reconstruction_Anchors.json")
    ap.add_argument("--flagged-dates", default="evidence/runs/38725478106_flagged_dates.csv")
    ap.add_argument("--output-dir", default="results/cp0040_baseline_reconstruction_audit")
    args = ap.parse_args()
    started = utc_now()
    output = (ROOT / args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(check_id, ok, detail):
        record = {"check_id": check_id, "status": "PASS" if ok else "FAIL", "detail": str(detail)}
        checks.append(record)
        if not ok:
            raise BlockedReconstruction(f"{check_id}: {detail}")

    anchors_path = ROOT / args.anchors
    anchors = json.loads(anchors_path.read_text(encoding="utf-8"))
    anchor_ok = anchors.get("checkpoint") == "CP-0040" and anchors.get("anchor_id") == "CP0040-BASELINE-RECONSTRUCTION-ANCHORS-20261016-01"
    checks.append({"check_id": "anchor_schema", "status": "PASS" if anchor_ok else "FAIL", "detail": anchors_path.as_posix()})
    if not anchor_ok:
        write_blocked(output, anchors, started, "Anchor schema or ID did not match the frozen CP-0040 reconstruction record.", checks)
        print(json.dumps({"status": "BLOCKED_INPUTS_NOT_REPRODUCIBLE", "reason": "anchor schema mismatch"}, ensure_ascii=False))
        return 0
    monthly_cache = (ROOT / args.monthly_cache).resolve()
    daily_cache = (ROOT / args.daily_cache).resolve()
    monthly_ok = monthly_cache.is_dir()
    checks.append({"check_id": "monthly_cache_present", "status": "PASS" if monthly_ok else "FAIL", "detail": str(monthly_cache)})
    if not monthly_ok:
        write_blocked(output, anchors, started, "Monthly source cache directory is missing; no network fallback is permitted.", checks)
        print(json.dumps({"status": "BLOCKED_INPUTS_NOT_REPRODUCIBLE", "reason": "monthly cache absent"}, ensure_ascii=False))
        return 0
    daily_ok = daily_cache.is_dir()
    checks.append({"check_id": "daily_cache_present", "status": "PASS" if daily_ok else "FAIL", "detail": str(daily_cache)})
    if not daily_ok:
        write_blocked(output, anchors, started, "Daily-reference cache directory is missing; no network fallback is permitted.", checks)
        print(json.dumps({"status": "BLOCKED_INPUTS_NOT_REPRODUCIBLE", "reason": "daily cache absent"}, ensure_ascii=False))
        return 0

    flagged_path = ROOT / args.flagged_dates
    try:
        with flagged_path.open("r", encoding="utf-8-sig", newline="") as f:
            flagged_rows = list(csv.DictReader(f))
    except OSError as exc:
        write_blocked(output, anchors, started, f"Frozen flagged-date evidence unavailable: {exc}", checks)
        print(json.dumps({"status": "BLOCKED_INPUTS_NOT_REPRODUCIBLE", "reason": str(exc)}, ensure_ascii=False))
        return 0
    flagged_dates = [str(r.get("date", "")).strip() for r in flagged_rows]
    flagged_ok = len(flagged_dates) == 40 and len(set(flagged_dates)) == 40 and all(re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", x) for x in flagged_dates)
    checks.append({"check_id": "flagged_dates_exactly_40_unique", "status": "PASS" if flagged_ok else "FAIL", "detail": f"rows={len(flagged_dates)} unique={len(set(flagged_dates))}"})
    if not flagged_ok:
        write_blocked(output, anchors, started, "Frozen flagged-date evidence is not exactly 40 unique ISO dates.", checks)
        print(json.dumps({"status": "BLOCKED_INPUTS_NOT_REPRODUCIBLE", "reason": "flagged-date anchor mismatch"}, ensure_ascii=False))
        return 0

    builder = load_builder()
    monthly_used = 0
    daily_used = 0
    sidecars_verified = 0
    archive_records = []
    candidate_results = {}

    try:
        with tempfile.TemporaryDirectory(prefix="cp0040-baseline-reconstruction-") as tmp:
            tmp_root = Path(tmp)
            monthly_checksums = {}
            daily_manifest = {}

            # Stage only the source ZIPs needed for 4h + 1d, in an isolated temporary tree.
            for interval in INTERVALS:
                for year, month in month_pairs():
                    filename = f"{SYMBOL}-{interval}-{year:04d}-{month:02d}.zip"
                    cached = find_unique(monthly_cache, filename)
                    member = validate_zip(cached)
                    digest = sha256_file(cached)
                    destination = tmp_root / "klines" / interval / filename
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(cached, destination)
                    copied_digest = sha256_file(destination)
                    check(f"monthly_cache_copy:{interval}:{year:04d}-{month:02d}", digest == copied_digest, f"sha256={digest}; member={member}")
                    monthly_checksums[(interval, filename)] = {
                        "status": "MATCH",
                        "local_sha256": digest,
                        "official_sha256": digest,
                        "validation_note": "Local cache-byte identity only; final frozen candidate-content hash is the acceptance anchor.",
                    }
                    archive_records.append({
                        "source": "monthly_cache",
                        "interval": interval,
                        "filename": filename,
                        "bytes": cached.stat().st_size,
                        "sha256_local": digest,
                        "zip_crc": "PASS",
                        "csv_member": member,
                    })
                    monthly_used += 1

            for interval in INTERVALS:
                for day in sorted(flagged_dates):
                    filename = f"{SYMBOL}-{interval}-{day}.zip"
                    cached = find_unique(daily_cache, filename)
                    sidecar = find_unique(daily_cache, filename + ".CHECKSUM")
                    official_sha = official_sidecar_hash(sidecar, filename)
                    actual_sha = sha256_file(cached)
                    check(f"daily_official_sidecar_hash:{interval}:{day}", actual_sha == official_sha, f"zip_sha256={actual_sha}; sidecar_sha256={sha256_file(sidecar)}")
                    member = validate_zip(cached)
                    destination = tmp_root / "reference_daily" / interval / filename
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(cached, destination)
                    sidecars_verified += 1
                    daily_used += 1
                    daily_manifest[(interval, day)] = {
                        "interval": interval,
                        "date": day,
                        "filename": filename,
                        "checksum_status": "MATCH",
                        "zip_sha256": actual_sha,
                        "official_sha256": official_sha,
                    }
                    archive_records.append({
                        "source": "daily_reference_cache",
                        "interval": interval,
                        "date": day,
                        "filename": filename,
                        "bytes": cached.stat().st_size,
                        "sha256_local": actual_sha,
                        "official_sha256": official_sha,
                        "sidecar_sha256": sha256_file(sidecar),
                        "zip_crc": "PASS",
                        "csv_member": member,
                    })

            # This is reconstruction-only. It never calls the production builder main()
            # and passes an empty quarantine set so the frozen pre-CP-0040 baseline can
            # be reconstituted in temp storage for a hash-anchor check.
            summaries = []
            candidate_dir = tmp_root / "derived" / "research_candidate_v1" / SYMBOL / "intervals"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            for interval in INTERVALS:
                path = candidate_dir / f"{SYMBOL}-{interval}-research-candidate.csv.gz"
                result, _, _, _ = builder.audit_and_write_interval(
                    tmp_root, interval, set(flagged_dates), daily_manifest,
                    monthly_checksums, path, set(), {}
                )
                summaries.append(result)
                candidate_results[interval] = inspect_csv_gzip(path, anchors["input_content_anchors"][interval])
            monthly_path = candidate_dir / f"{SYMBOL}-1mo-research-candidate.csv.gz"
            month_summary = builder.create_monthly_from_daily(
                tmp_root, candidate_dir / f"{SYMBOL}-1d-research-candidate.csv.gz", monthly_path
            )
            candidate_results["1mo"] = inspect_csv_gzip(monthly_path, anchors["input_content_anchors"]["1mo"])

            expected_counts = {"4h": 19975, "1d": 3332}
            for interval, expected_rows in expected_counts.items():
                actual_rows = summaries[INTERVALS.index(interval)].get("candidate_rows")
                check(f"{interval}_builder_row_count", actual_rows == expected_rows, f"actual={actual_rows}; expected={expected_rows}")
            check("monthly_archive_count", monthly_used == 220, f"used={monthly_used}; expected=220")
            check("daily_reference_archive_count", daily_used == 80, f"used={daily_used}; expected=80")
            check("daily_sidecar_count", sidecars_verified == 80, f"verified={sidecars_verified}; expected=80")

            for interval in ("4h", "1d", "1mo"):
                res = candidate_results[interval]
                check(
                    f"{interval}_frozen_decompressed_content_anchor",
                    res["matches_frozen_content_anchor"],
                    f"actual_raw_sha={res['decompressed_sha256']}; expected_raw_sha={res['decompressed_sha256_anchor']}; rows={res['rows']}"
                )

            summary = {
                "schema_version": 1,
                "checkpoint": "CP-0040",
                "task": "cp0040_baseline_reconstruction_audit",
                "status": "PASS_BASELINE_INPUTS_RECONSTRUCTED",
                "started_at_utc": started,
                "finished_at_utc": utc_now(),
                "scope": "CACHE_ONLY_TEMPORARY_BASELINE_CONTENT_RECONSTRUCTION",
                "network_used": False,
                "market_data_downloads": 0,
                "raw_source_archives_modified": False,
                "monthly_archives_used": monthly_used,
                "daily_reference_archives_used": daily_used,
                "official_daily_sidecars_verified": sidecars_verified,
                "official_monthly_sidecar_requests": 0,
                "baseline_candidate_rows": {k: v["rows"] for k, v in candidate_results.items()},
                "candidate_content_results": candidate_results,
                "candidate_summaries": summaries,
                "derived_monthly_summary": month_summary,
                "archive_record_count": len(archive_records),
                "archive_records_sha256": sha256_bytes(json.dumps(archive_records, sort_keys=True, separators=(",", ":")).encode()),
                "archive_records": archive_records,
                "anchor_file": str(anchors_path.relative_to(ROOT)),
                "snapshot_sha256": anchors["created_from"]["package_sha256"],
                "engine_sha256_anchor": anchors["frozen_engine"]["sha256"],
                "production_candidate_build": False,
                "backtest_run": False,
                "signal_or_position_comparison": False,
                "strategy_promoted": False,
                "checks": checks,
                "limitations": [
                    "This confirms decompressed candidate CSV content, schema, and row counts match the frozen verified snapshot anchors. A GZIP wrapper may have a different timestamp and therefore a different compressed SHA-256.",
                    "Monthly source ZIP byte hashes are measured from the cache; this task does not fetch monthly .CHECKSUM sidecars. The final candidate-content anchors must match exactly, including embedded source SHA-256 fields.",
                    "This task does not run CP-0031 or calculate any strategy/performance metrics; those belong to the next separately scoped diagnostic step.",
                ],
                "gate": {
                    "g0": "BLOCKED_GLOBAL",
                    "unresolved_nonrow_aggregation_blockers": 11,
                    "canonical_source": "NONE",
                    "candidate_promotion": "BLOCKED",
                    "live_signing_broadcast_orders": "BLOCKED",
                },
            }
            (output / "CP0040_Baseline_Reconstruction_Audit_Summary.json").write_text(
                json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
            )
            report = [
                "# CP-0040 Baseline Reconstruction Audit",
                "",
                f"- Status: `{summary['status']}`",
                "- The 4h and 1d inputs were reconstructed in an isolated temporary directory using cached monthly archives and cached daily references.",
                "- The 1mo series was re-derived from the reconstructed daily candidate using the same reviewed CP-0026 serialization helper.",
                f"- Monthly ZIPs used: {monthly_used}; daily reference ZIPs used: {daily_used}; daily .CHECKSUM sidecars verified: {sidecars_verified}.",
                "- Network/archive acquisition: none. Raw cache archives were read-only.",
                "",
                "## Exact decompressed-content checks",
            ]
            for interval, res in candidate_results.items():
                report.append(
                    f"- {interval}: `{res['rows']}` rows; reconstructed CSV SHA-256 `{res['decompressed_sha256']}`; "
                    f"frozen anchor `{res['decompressed_sha256_anchor']}`; match={res['matches_frozen_content_anchor']}."
                )
            report += [
                "",
                "## Gate",
                "- This is an input reproducibility audit only, not a backtest or candidate-promotion event.",
                "- G0 remains `BLOCKED_GLOBAL`; the 11 non-row aggregation blockers remain open.",
                "- Canonical source remains `NONE`; promotion and live exchange actions remain blocked.",
            ]
            (output / "CP0040_Baseline_Reconstruction_Audit_Report_HI.md").write_text(
                "\n".join(report) + "\n", encoding="utf-8"
            )
            with (output / "CP0040_Baseline_Reconstruction_Archive_Inventory.csv").open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for row in archive_records for k in row)))
                writer.writeheader()
                writer.writerows(archive_records)
            print(json.dumps({"status": summary["status"], "monthly_archives": monthly_used, "daily_archives": daily_used, "sidecars_verified": sidecars_verified, "matches": {k: v["matches_frozen_content_anchor"] for k, v in candidate_results.items()}, "checks_passed": sum(c["status"] == "PASS" for c in checks), "checks_total": len(checks)}, ensure_ascii=False, sort_keys=True))
            return 0
    except BlockedReconstruction as exc:
        write_blocked(output, anchors, started, str(exc), checks)
        print(json.dumps({"status": "BLOCKED_INPUTS_NOT_REPRODUCIBLE", "reason": str(exc), "checks_passed": sum(c["status"] == "PASS" for c in checks), "checks_total": len(checks)}, ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        output.mkdir(parents=True, exist_ok=True)
        summary = {
            "schema_version": 1,
            "checkpoint": "CP-0040",
            "task": "cp0040_baseline_reconstruction_audit",
            "status": "FAIL_CLOSED_UNEXPECTED_ERROR",
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
            "network_used": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "checks": checks,
            "production_candidate_build": False,
            "backtest_run": False,
            "strategy_promoted": False,
            "live_signing_broadcast_orders": "BLOCKED",
        }
        (output / "CP0040_Baseline_Reconstruction_Audit_Summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output / "CP0040_Baseline_Reconstruction_Audit_Report_HI.md").write_text(
            f"# CP-0040 Baseline Reconstruction Audit\n\n- Status: `FAIL_CLOSED_UNEXPECTED_ERROR`\n- Error: {type(exc).__name__}: {exc}\n- No backtest or candidate promotion was performed.\n",
            encoding="utf-8",
        )
        print(json.dumps({"status": "FAIL_CLOSED_UNEXPECTED_ERROR", "error_type": type(exc).__name__, "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
