#!/usr/bin/env python3
"""Upload validated BTCUSDT history files to a private Supabase Storage bucket and catalog."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def request(url: str, method: str, headers: dict[str, str], data: bytes | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read(2000).decode("utf-8", "replace")
        raise RuntimeError(f"{method} {url} failed HTTP {exc.code}: {body}") from exc

def classify(path: Path) -> tuple[str, str | None]:
    name = path.name
    match = re.search(r"(20\d{2}-\d{2})", str(path))
    month = match.group(1) if match else None
    if "funding" in name.lower():
        dataset = "um_funding_rate"
    elif "spot" in str(path).lower():
        dataset = "spot_klines_1m"
    elif "um" in str(path).lower() or "future" in str(path).lower():
        dataset = "um_klines_1m"
    elif name.lower().endswith(".json"):
        dataset = "manifest_or_report"
    else:
        dataset = "archive_or_report"
    return dataset, month

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--prefix", default="btc-usdt-history")
    args = parser.parse_args()
    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    bucket = os.environ.get("SUPABASE_BUCKET", "btc-usdt-history")
    if not base or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required", file=sys.stderr)
        return 2
    root = Path(args.input_dir).resolve()
    if not root.is_dir():
        print(f"ERROR: input directory not found: {root}", file=sys.stderr)
        return 2
    files = sorted(p for p in root.rglob("*") if p.is_file())
    if not files:
        print("ERROR: no files found to upload", file=sys.stderr)
        return 2
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    completed = 0
    errors = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        object_path = f"{args.prefix}/{rel}"
        encoded_bucket = urllib.parse.quote(bucket, safe="")
        encoded_path = urllib.parse.quote(object_path, safe="/")
        digest = sha256_file(path)
        size = path.stat().st_size
        dataset, month = classify(path)
        content_type = "application/json" if path.suffix.lower() == ".json" else (
            "application/zip" if path.suffix.lower() == ".zip" else "application/octet-stream"
        )
        try:
            request(
                f"{base}/storage/v1/object/{encoded_bucket}/{encoded_path}",
                "PUT",
                {**headers, "Content-Type": content_type, "x-upsert": "true"},
                path.read_bytes(),
            )
            record = {
                "object_path": object_path,
                "file_name": path.name,
                "dataset": dataset,
                "month": month,
                "size_bytes": size,
                "sha256": digest,
                "validation_status": "COLLECTED",
                "source_url": None,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            }
            request(
                f"{base}/rest/v1/btcusdt_history_objects?on_conflict=object_path",
                "POST",
                {**headers, "Content-Type": "application/json",
                 "Prefer": "resolution=merge-duplicates,return=minimal"},
                json.dumps(record).encode(),
            )
            completed += 1
            print(f"UPLOADED {object_path} bytes={size} sha256={digest}")
        except Exception as exc:
            errors.append({"path": object_path, "error": str(exc)})
            print(f"FAILED {object_path}: {exc}", file=sys.stderr)
            break
    report = {"status": "PASS" if not errors else "FAIL", "uploaded_files": completed,
              "total_files": len(files), "errors": errors}
    print(json.dumps(report, indent=2))
    return 0 if not errors and completed == len(files) else 1

if __name__ == "__main__":
    raise SystemExit(main())
