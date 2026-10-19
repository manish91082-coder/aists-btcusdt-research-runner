#!/usr/bin/env python3
"""CP-0268: GitHub-hosted, fail-closed CP-0267 scoped G0 runtime.

Uses only the pre-existing monthly archive cache. It may fetch official .CHECKSUM
sidecars via CP-0165, but never downloads ZIPs or calls Binance REST APIs.
Historical point-in-time provenance remains NOT_VERIFIED.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / ".cache" / "aists" / "binance-monthly-archives"
DATA_ROOT = REPO / ".runtime" / "aists_data" / "market_data" / "binance_spot" / "BTCUSDT"
AUDIT_DIR = REPO / "results" / "cp0165_4h_archive_audit"
OUT_DIR = REPO / "results" / "cp0268_g0_runtime"
FROZEN = REPO / "evidence" / "source_adjudication" / "CP0040_Run_38882377148"
FLAGGED_DATES_FILE = REPO / "evidence" / "runs" / "38725478106_flagged_dates.csv"
FLAGGED_DATES_SHA256 = "9692ebcfc5a73e96fc9e78b0ac9eb56086a6bd7b7bf05596b837170ded607ce9"
EXPECTED = {
    "CP0040_ExactKey_Quarantine_Manifest.csv": "d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819",
    "CP0040_NonRow_Blockers.csv": "d0126152a58baecd8f61bcdcc21286ecffacba6427e7b09696ca63db33c1f0d0",
}
GATE_SCRIPT = REPO / "scripts" / "AISTS_CP0267_NotVerified_Gate.py"
BUILDER = REPO / "scripts" / "AISTS_CP0026_Research_Candidate_Builder.py"
AUDITOR = REPO / "scripts" / "AISTS_CP0165_4H_Monthly_Checksum_Gap_Audit.py"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fail(message: str):
    raise RuntimeError(message)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not CACHE.is_dir():
        fail(f"CP0268_BLOCKED_CACHE_MISSING:{CACHE}")
    if not FROZEN.is_dir():
        fail(f"CP0268_BLOCKED_FROZEN_CP0040_EVIDENCE_MISSING:{FROZEN}")

    # Verify frozen source evidence before any runtime preparation.
    frozen_hashes = {}
    for name, expected_sha in EXPECTED.items():
        path = FROZEN / name
        if not path.is_file():
            fail(f"CP0268_BLOCKED_FROZEN_FILE_MISSING:{path}")
        actual = sha256(path)
        frozen_hashes[name] = actual
        if actual != expected_sha:
            fail(f"CP0268_BLOCKED_FROZEN_SHA256_MISMATCH:{name}:{actual}")

    # Pin the pre-existing 40-date CP-0025 flagged-date evidence. Scoped mode
    # excludes these dates rather than selecting daily data or falling back to monthly.
    if not FLAGGED_DATES_FILE.is_file() or sha256(FLAGGED_DATES_FILE) != FLAGGED_DATES_SHA256:
        fail("CP0268_BLOCKED_FLAGGED_DATES_EVIDENCE_MISSING_OR_HASH_MISMATCH")
    with FLAGGED_DATES_FILE.open(newline="", encoding="utf-8-sig") as stream:
        flagged_rows = list(csv.DictReader(stream))
    flagged_dates = [str(row.get("date", "")).strip() for row in flagged_rows]
    if len(flagged_dates) != 40 or len(set(flagged_dates)) != 40 or any(len(day) != 10 for day in flagged_dates):
        fail(f"CP0268_BLOCKED_FLAGGED_DATES_SCHEMA_OR_COUNT:{len(flagged_dates)}")

    # Official checksum sidecars only; CP-0165 refuses to download monthly ZIPs.
    audit_cmd = [
        sys.executable, str(AUDITOR),
        "--archive-inventory",
        "evidence/source_adjudication/CP0040_Reconstruction_Run_38895499283/CP0040_Baseline_Reconstruction_Archive_Inventory.csv",
        "--monthly-cache", str(CACHE.relative_to(REPO)),
        "--output-dir", str(AUDIT_DIR.relative_to(REPO)),
    ]
    audit_proc = subprocess.run(audit_cmd, cwd=REPO, text=True, capture_output=True)
    (OUT_DIR / "cp0165_stdout.log").write_text(audit_proc.stdout, encoding="utf-8")
    (OUT_DIR / "cp0165_stderr.log").write_text(audit_proc.stderr, encoding="utf-8")
    audit_summary_path = AUDIT_DIR / "CP0165_4H_Monthly_Checksum_Gap_Audit_Summary.json"
    if not audit_summary_path.is_file():
        fail(f"CP0268_BLOCKED_CP0165_SUMMARY_MISSING:exit={audit_proc.returncode}")
    audit = load_json(audit_summary_path)
    if audit.get("status") != "PASS_ALL_110_OFFICIAL_CHECKSUMS_MATCH":
        write_json(OUT_DIR / "CP0268_G0_Runtime_Receipt.json", {
            "checkpoint": "CP-0268", "status": "BLOCKED_SOURCE_AUDIT",
            "cp0165_status": audit.get("status"), "cp0165_exit_code": audit_proc.returncode,
            "cp0165_summary_sha256": sha256(audit_summary_path),
            "frozen_evidence_sha256": frozen_hashes,
            "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "github_sha": os.environ.get("GITHUB_SHA", ""),
            "candidate_build_run": False, "historical_version_provenance": "NOT_VERIFIED",
            "live_signing_broadcast_orders": "BLOCKED",
        })
        fail(f"CP0268_BLOCKED_CP0165_NOT_PASS:{audit.get('status')}")

    details_path = AUDIT_DIR / "CP0165_4H_Monthly_Checksum_Gap_Audit_Details.csv"
    with details_path.open(newline="", encoding="utf-8-sig") as stream:
        details = list(csv.DictReader(stream))
    if len(details) != 110 or any(r.get("checksum_status") != "MATCH" or r.get("zip_crc") != "PASS" for r in details):
        fail(f"CP0268_BLOCKED_DETAIL_POPULATION_OR_CHECKSUM_FAILURE:rows={len(details)}")

    # Prepare a temporary runtime tree; raw cache ZIPs are only symlinked, never edited.
    if DATA_ROOT.exists():
        shutil.rmtree(DATA_ROOT)
    reports = DATA_ROOT / "reports"
    klines = DATA_ROOT / "klines" / "4h"
    reports.mkdir(parents=True, exist_ok=True)
    klines.mkdir(parents=True, exist_ok=True)
    official_rows = []
    archive_hashes = {}
    for row in details:
        filename = row["filename"]
        cache_rel = row.get("cache_path", "")
        source = REPO / cache_rel
        if not cache_rel or not source.is_file():
            fail(f"CP0268_BLOCKED_ARCHIVE_PATH_MISSING:{filename}:{cache_rel}")
        actual = sha256(source)
        official_sha = (row.get("sidecar_hashes", "").split(";") or [""])[0].strip().lower()
        if actual != row.get("local_sha256", "").lower() or actual != official_sha:
            fail(f"CP0268_BLOCKED_ARCHIVE_SHA_CHANGED:{filename}")
        destination = klines / filename
        destination.symlink_to(source.resolve())
        archive_hashes[filename] = actual
        official_rows.append({
            "interval": "4h", "filename": filename, "status": "MATCH",
            "local_sha256": actual, "official_sha256": official_sha,
        })

    with (reports / "official_checksum_verification.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["interval", "filename", "status", "local_sha256", "official_sha256"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(official_rows)

    # Explicitly use monthly 4h archives only. No daily overrides or fabricated bars.
    write_json(reports / "cp0025_reference_dates.json", {"dates": sorted(flagged_dates)})
    with (reports / "cp0025_daily_reference_manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        csv.writer(stream, lineterminator="\n").writerow(
            ["interval", "date", "filename", "checksum_status", "zip_sha256", "official_sha256"]
        )

    for name in EXPECTED:
        shutil.copyfile(FROZEN / name, reports / name)

    env = os.environ.copy()
    env["AISTS_DATA_ROOT"] = str(DATA_ROOT)
    build_cmd = [sys.executable, str(BUILDER), "--scope-not-verified"]
    build_proc = subprocess.run(build_cmd, cwd=REPO, env=env, text=True, capture_output=True)
    (OUT_DIR / "cp0026_stdout.log").write_text(build_proc.stdout, encoding="utf-8")
    (OUT_DIR / "cp0026_stderr.log").write_text(build_proc.stderr, encoding="utf-8")

    manifest_path = reports / "cp0026_research_candidate_manifest.json"
    candidate_path = DATA_ROOT / "derived" / "research_candidate_v1" / "BTCUSDT" / "intervals" / "BTCUSDT-4h-research-candidate.csv.gz"
    receipt = {
        "checkpoint": "CP-0268",
        "status": "BLOCKED_RUNTIME_BUILD",
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "github_sha": os.environ.get("GITHUB_SHA", ""),
        "cp0165_status": audit.get("status"),
        "cp0165_summary_sha256": sha256(audit_summary_path),
        "cp0165_details_sha256": sha256(details_path),
        "frozen_evidence_sha256": frozen_hashes,
        "flagged_dates_evidence_sha256": sha256(FLAGGED_DATES_FILE),
        "flagged_dates_excluded_count": len(flagged_dates),
        "official_4h_archive_count": len(archive_hashes),
        "official_4h_archive_manifest_sha256": hashlib.sha256(
            json.dumps(archive_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "candidate_build_exit_code": build_proc.returncode,
        "candidate_manifest_sha256": sha256(manifest_path) if manifest_path.is_file() else None,
        "candidate_file_sha256": sha256(candidate_path) if candidate_path.is_file() else None,
        "candidate_build_run": False,
        "g0_scope_status": "PENDING_VERIFICATION",
        "historical_version_provenance": "NOT_VERIFIED",
        "acceptance_grade": False,
        "backtest_approved": False,
        "profitability_established": False,
        "live_signing_broadcast_orders": "BLOCKED",
    }

    if build_proc.returncode == 0 and manifest_path.is_file() and candidate_path.is_file():
        report = load_json(manifest_path)
        candidate_meta = report.get("results", {}).get("4h", {})
        expected_candidate_sha = candidate_meta.get("sha256")
        if expected_candidate_sha != sha256(candidate_path):
            receipt["failure_reason"] = "CANDIDATE_SHA256_RECEIPT_MISMATCH"
        else:
            from AISTS_CP0267_NotVerified_Gate import load_scoped_policy, exclusion_reasons
            policy = load_scoped_policy(reports / "CP0040_ExactKey_Quarantine_Manifest.csv",
                                        reports / "CP0040_NonRow_Blockers.csv")
            row_count = 0
            with gzip.open(candidate_path, "rt", newline="", encoding="utf-8") as stream:
                for row in csv.DictReader(stream):
                    row_count += 1
                    if row.get("interval", "4h") != "4h":
                        fail("CP0268_CANDIDATE_INTERVAL_LEAK")
                    if exclusion_reasons(policy, "4h", row.get("open_time_ms", ""), row.get("open_time_utc", "")):
                        fail("CP0268_NOT_VERIFIED_KEY_LEAKED")
                    if row.get("source_status") != "VERIFIED_PRIMARY_CURRENT_SNAPSHOT" or not row.get("source_sha256"):
                        fail("CP0268_SOURCE_IDENTITY_MISSING")
                    if str(row.get("open_time_utc", ""))[:10] in set(flagged_dates):
                        fail("CP0268_FLAGGED_DATE_LEAKED_INTO_MONTHLY_ONLY_CANDIDATE")
            if row_count != candidate_meta.get("candidate_rows"):
                fail("CP0268_CANDIDATE_ROW_COUNT_MISMATCH")
            if report.get("g0_scope", {}).get("status") == "G0_SCOPED_PASS_4H_CANDIDATE_ELIGIBILITY_ONLY":
                receipt["status"] = "PASS_G0_SCOPED_4H_CANDIDATE_ELIGIBILITY_ONLY"
                receipt["candidate_build_run"] = True
                receipt["g0_scope_status"] = "G0_SCOPED_PASS_4H_CANDIDATE_ELIGIBILITY_ONLY"
                receipt["candidate_rows"] = row_count
                receipt["candidate_file_sha256"] = sha256(candidate_path)
                receipt["candidate_manifest_sha256"] = sha256(manifest_path)
            else:
                receipt["failure_reason"] = "BUILDER_DID_NOT_REPORT_SCOPED_PASS"
    else:
        receipt["failure_reason"] = f"BUILDER_EXIT_OR_OUTPUT_MISSING:{build_proc.returncode}"

    write_json(OUT_DIR / "CP0268_G0_Runtime_Receipt.json", receipt)
    # Copy compact evidence, not a substitute for the immutable raw ZIP cache.
    for src in [
        audit_summary_path, details_path,
        manifest_path,
        reports / "cp0026_day_source_disposition.csv",
        reports / "cp0026_candidate_quality_issues.csv",
        reports / "cp0026_quarantined_candidate_rows.csv",
    ]:
        if src.is_file():
            shutil.copy2(src, OUT_DIR / src.name)
    if candidate_path.is_file():
        shutil.copy2(candidate_path, OUT_DIR / candidate_path.name)
    if receipt["status"] != "PASS_G0_SCOPED_4H_CANDIDATE_ELIGIBILITY_ONLY":
        raise SystemExit(f"CP0268_RUNTIME_NOT_PASS:{receipt.get('failure_reason', receipt['status'])}")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        out = OUT_DIR / "CP0268_G0_Runtime_Receipt.json"
        error_text = f"{type(exc).__name__}: {exc}"
        if not out.exists():
            write_json(out, {
                "checkpoint": "CP-0268", "status": "BLOCKED_RUNTIME_EXCEPTION",
                "error": error_text,
                "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
                "github_sha": os.environ.get("GITHUB_SHA", ""),
                "historical_version_provenance": "NOT_VERIFIED",
                "live_signing_broadcast_orders": "BLOCKED",
            })
        else:
            existing = load_json(out)
            if existing.get("status") != "PASS_G0_SCOPED_4H_CANDIDATE_ELIGIBILITY_ONLY":
                existing["runtime_exception"] = error_text
                if existing.get("status") == "BLOCKED_RUNTIME_BUILD":
                    existing["status"] = "BLOCKED_RUNTIME_EXCEPTION"
                write_json(out, existing)
        print(f"CP0268_BLOCKED:{error_text}", file=sys.stderr)
        raise
