"""Fail-closed exact-key gate for scoped NOT_VERIFIED exclusions."""
import csv
import hashlib
from pathlib import Path

VERIFIED = {"VERIFIED_PRIMARY_CURRENT_SNAPSHOT", "VERIFIED_ALTERNATE_EXACT_KEY"}

class NotVerifiedGateError(RuntimeError):
    pass

def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def load_manifest(path, expected_sha256):
    path = Path(path)
    if sha256_file(path) != expected_sha256:
        raise NotVerifiedGateError("MANIFEST_SHA_MISMATCH")
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    required = {"symbol", "market", "interval", "open_time_ms", "status", "reason"}
    if not rows or not required.issubset(rows[0]):
        raise NotVerifiedGateError("MANIFEST_SCHEMA_OR_EMPTY")
    result = {}
    for row in rows:
        key = tuple(row[k].strip() for k in ("symbol", "market", "interval", "open_time_ms"))
        if not all(key) or key in result:
            raise NotVerifiedGateError("KEY_MISSING_OR_DUPLICATE")
        if not row["status"].strip() or not row["reason"].strip():
            raise NotVerifiedGateError("STATUS_OR_REASON_MISSING")
        result[key] = row["status"].strip()
    return result

def partition_rows(rows, manifest):
    kept, excluded = [], []
    for row in rows:
        key = tuple(str(row.get(k, "")).strip() for k in ("symbol", "market", "interval", "open_time_ms"))
        if not all(key) or key not in manifest:
            raise NotVerifiedGateError(f"KEY_NOT_IN_MANIFEST:{key}")
        if manifest[key] in VERIFIED:
            kept.append(row)
        else:
            excluded.append({**row, "exclusion_status": manifest[key]})
    return kept, excluded

def require_scored_rows(rows, manifest):
    for row in rows:
        key = tuple(str(row.get(k, "")).strip() for k in ("symbol", "market", "interval", "open_time_ms"))
        if manifest.get(key) not in VERIFIED:
            raise NotVerifiedGateError(f"UNVERIFIED_KEY_REACHED_SCORING:{key}")
    return True
