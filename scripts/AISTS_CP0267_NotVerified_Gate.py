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


# Frozen evidence identities from CP-0040 Run 38882377148.
EXPECTED_EXACT_MANIFEST_SHA256 = "d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819"
EXPECTED_NONROW_SHA256 = "d0126152a58baecd8f61bcdcc21286ecffacba6427e7b09696ca63db33c1f0d0"
INTERVAL_MS = {"5m":300_000, "15m":900_000, "30m":1_800_000, "1h":3_600_000, "4h":14_400_000, "1d":86_400_000}
EXPECTED_GAP_KEYS = (
    "1504713600000", "1518062400000", "1518076800000", "1518091200000",
    "1518105600000", "1518120000000", "1518134400000", "1518148800000",
    "1529985600000", "1530000000000", "1530676800000", "1542168000000",
    "1552363200000", "1557892800000", "1557907200000", "1565841600000",
    "1582113600000",
)

def load_scoped_policy(exact_manifest_path, nonrow_path):
    """Load frozen unresolved populations and expand them into conservative row exclusions."""
    exact_manifest_path, nonrow_path = Path(exact_manifest_path), Path(nonrow_path)
    exact_sha, nonrow_sha = sha256_file(exact_manifest_path), sha256_file(nonrow_path)
    if exact_sha != EXPECTED_EXACT_MANIFEST_SHA256:
        raise NotVerifiedGateError("CP0267_EXACT_MANIFEST_SHA_MISMATCH")
    if nonrow_sha != EXPECTED_NONROW_SHA256:
        raise NotVerifiedGateError("CP0267_NONROW_SHA_MISMATCH")
    with exact_manifest_path.open(encoding="utf-8-sig", newline="") as f:
        exact_rows = list(csv.DictReader(f))
    with nonrow_path.open(encoding="utf-8-sig", newline="") as f:
        nonrow_rows = list(csv.DictReader(f))
    if len(exact_rows) != 969 or len(nonrow_rows) != 27:
        raise NotVerifiedGateError("CP0267_FROZEN_POPULATION_COUNT_MISMATCH")
    exact_cases, date_blockers, agg_cases = {}, set(), {}
    for row in exact_rows:
        interval, token = row.get("interval", "").strip(), row.get("open_time_ms", "").strip()
        key = (interval, token)
        if interval not in INTERVAL_MS or not token.isdigit() or key in exact_cases:
            raise NotVerifiedGateError("CP0267_EXACT_KEY_INVALID_OR_DUPLICATE")
        if row.get("canonical_source", "").upper() != "NONE" or row.get("case_closed", "").lower() != "false":
            raise NotVerifiedGateError("CP0267_SOURCE_SELECTED_OR_CASE_CLOSED")
        exact_cases[key] = [row.get("case_id", "UNKNOWN_CASE")]
    for row in nonrow_rows:
        case_id, kind = row.get("case_id", ""), row.get("record_type", "")
        if kind == "MISSING_DAILY_REFERENCE_ACQUISITION":
            interval, day = row.get("interval", "").strip(), row.get("utc_date", "").strip()
            if interval not in INTERVAL_MS or len(day) != 10:
                raise NotVerifiedGateError("CP0267_FETCHREF_SCOPE_INVALID")
            date_blockers.add((interval, day, case_id))
        elif kind == "RESIDUAL_AGGREGATION_BUCKET":
            import re
            m = re.fullmatch(r"AGG-\d+-(5m|15m|30m|1h|4h|1d)-(5m|15m|30m|1h|4h|1d)-(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", case_id)
            if not m:
                raise NotVerifiedGateError(f"CP0267_AGG_KEY_UNPARSEABLE:{case_id}")
            child, parent, iso = m.groups()
            from datetime import datetime, timezone
            start = int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp() * 1000)
            if INTERVAL_MS[child] >= INTERVAL_MS[parent] or INTERVAL_MS[parent] % INTERVAL_MS[child]:
                raise NotVerifiedGateError(f"CP0267_AGG_INTERVAL_RELATION_INVALID:{case_id}")
            agg_cases.setdefault((parent, str(start)), []).append(case_id)
            for child_start in range(start, start + INTERVAL_MS[parent], INTERVAL_MS[child]):
                agg_cases.setdefault((child, str(child_start)), []).append(case_id)
        else:
            raise NotVerifiedGateError(f"CP0267_NONROW_TYPE_UNKNOWN:{kind}")
    gap_cases = {("4h", token): [f"GAP-4h-{token}"] for token in EXPECTED_GAP_KEYS}
    return {
        "exact_sha256": exact_sha, "nonrow_sha256": nonrow_sha,
        "exact_rows": len(exact_rows), "nonrow_rows": len(nonrow_rows),
        "exact_cases": exact_cases, "date_blockers": date_blockers,
        "agg_cases": agg_cases, "gap_cases": gap_cases,
        "gap_keys": len(gap_cases), "status": "NOT_VERIFIED_EXCLUSION_POLICY_LOADED",
    }

def exclusion_reasons(policy, interval, open_time_ms, open_time_utc=""):
    """Return every applicable exclusion reason for a candidate row."""
    token = str(open_time_ms).strip()
    key = (interval, token)
    reasons = []
    reasons.extend(policy["exact_cases"].get(key, []))
    reasons.extend(policy["agg_cases"].get(key, []))
    reasons.extend(policy["gap_cases"].get(key, []))
    if open_time_utc:
        day = str(open_time_utc)[:10]
    else:
        from datetime import datetime, timezone
        day = datetime.fromtimestamp(int(token) / 1000, tz=timezone.utc).date().isoformat()
    reasons.extend(case for iv, blocked_day, case in policy["date_blockers"] if iv == interval and blocked_day == day)
    return sorted(set(reasons))
