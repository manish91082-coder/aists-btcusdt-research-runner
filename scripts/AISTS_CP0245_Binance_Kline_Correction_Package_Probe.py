#!/usr/bin/env python3
"""Bounded read-only inspection of Binance's official 2022-08-08 kline correction bundle.

Downloads only the public correction package (not market-data archives), verifies the
outer ZIP CRC, recursively inspects nested ZIPs, and reports BTCUSDT 4h entries plus
the known disputed open-time key. It never edits source data or selects a canonical source.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

URL = "https://raw.githubusercontent.com/binance/binance-public-data/master/updates/2022-08-08_kline_updates.zip"
KNOWN_OPEN_TIME_MS = 1504713600000
OUT = Path("results/cp0245_binance_kline_correction_probe")
MAX_DOWNLOAD_BYTES = 50_000_000


def read_csv_rows(data: bytes, label: str, result: dict) -> None:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return
    sample = text[:4096]
    if not sample or "\n" not in sample:
        return
    try:
        rows = csv.reader(io.StringIO(text))
        for row_number, row in enumerate(rows, start=1):
            if not row:
                continue
            # Binance kline CSV: open time is column 0; no header in normal archives.
            if row[0].strip().lstrip("-").isdigit() and len(row) >= 7:
                try:
                    open_time = int(row[0].strip())
                except ValueError:
                    continue
                result["numeric_rows_seen"] += 1
                if open_time == KNOWN_OPEN_TIME_MS:
                    result["known_key_matches"].append({
                        "member": label,
                        "row_number": row_number,
                        "row": row[:12],
                    })
    except (csv.Error, UnicodeError):
        return


def inspect_zip_bytes(payload: bytes, label: str, result: dict, depth: int = 0) -> None:
    if depth > 3:
        result["inspection_limits"].append({"member": label, "reason": "max_nested_zip_depth"})
        return
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            bad = zf.testzip()
            result["zip_files"].append({
                "member": label,
                "members": len(zf.infolist()),
                "crc_test": "PASS" if bad is None else "FAIL",
                "bad_member": bad,
                "member_inventory": [
                    {"name": item.filename, "bytes": item.file_size, "crc32": format(item.CRC, "08x")}
                    for item in zf.infolist() if not item.is_dir()
                ],
            })
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = f"{label}!/{info.filename}"
                if info.file_size > MAX_DOWNLOAD_BYTES:
                    result["inspection_limits"].append({"member": name, "reason": "member_too_large", "bytes": info.file_size})
                    continue
                try:
                    data = zf.read(info)
                except Exception as exc:
                    result["read_errors"].append({"member": name, "error": type(exc).__name__})
                    continue
                if info.filename.lower().endswith(".zip"):
                    inspect_zip_bytes(data, name, result, depth + 1)
                elif info.filename.lower().endswith(".csv") and "kline_updates" in info.filename.lower():
                    try:
                        manifest_rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
                        result["correction_manifest"] = {
                            "member": name,
                            "header": manifest_rows[0] if manifest_rows else [],
                            "data_row_count": max(0, len(manifest_rows) - 1),
                            "btc_usdt_4h_rows": [
                                {"row_number": idx + 1, "row": row}
                                for idx, row in enumerate(manifest_rows[1:], start=1)
                                if any("BTCUSDT" in cell.upper() for cell in row)
                                and any("4H" in cell.upper() for cell in row)
                            ],
                            "first_rows": manifest_rows[:3],
                        }
                    except (UnicodeDecodeError, csv.Error) as exc:
                        result["read_errors"].append({"member": name, "error": type(exc).__name__})
                elif ("BTCUSDT" in info.filename.upper() and "4H" in info.filename.upper()) or info.filename.lower().endswith(".csv"):
                    before = result["numeric_rows_seen"]
                    read_csv_rows(data, name, result)
                    if result["numeric_rows_seen"] > before and "BTCUSDT" in info.filename.upper() and "4H" in info.filename.upper():
                        result["btc_usdt_4h_csv_members"].append({
                            "member": name,
                            "numeric_rows": result["numeric_rows_seen"] - before,
                            "bytes": len(data),
                        })
    except zipfile.BadZipFile:
        result["read_errors"].append({"member": label, "error": "BadZipFile"})


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "AISTS-CP0245-read-only-audit/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = response.read(MAX_DOWNLOAD_BYTES + 1)
        final_url = response.geturl()
        status = getattr(response, "status", None)
    if len(payload) > MAX_DOWNLOAD_BYTES:
        raise RuntimeError(f"correction package exceeds {MAX_DOWNLOAD_BYTES} bytes; refused")
    result = {
        "checkpoint": "CP-0245",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "requested_url": URL,
        "final_url": final_url,
        "http_status": status,
        "package_bytes": len(payload),
        "package_sha256": hashlib.sha256(payload).hexdigest(),
        "known_open_time_ms": KNOWN_OPEN_TIME_MS,
        "known_open_time_utc": "2017-09-06T16:00:00Z",
        "zip_files": [],
        "btc_usdt_4h_csv_members": [],
        "correction_manifest": None,
        "numeric_rows_seen": 0,
        "known_key_matches": [],
        "read_errors": [],
        "inspection_limits": [],
        "decision": "EVIDENCE_ONLY_NO_SOURCE_SELECTION",
        "canonical_source": "NONE",
        "g0": "BLOCKED_GLOBAL",
    }
    inspect_zip_bytes(payload, "2022-08-08_kline_updates.zip", result)
    result["known_key_match_count"] = len(result["known_key_matches"])
    result["decision_note"] = (
        "A matching record in a correction bundle is only a lead; source authority, "
        "affected archive identity, old/new checksums, and complete row-level lineage "
        "must be verified before any source adjudication."
    )
    (OUT / "CP0245_Binance_Kline_Correction_Package_Probe.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
