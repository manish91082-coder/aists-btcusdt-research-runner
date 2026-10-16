#!/usr/bin/env python3
"""CP-0040 exact-key quarantine gate primitives and deterministic self-tests.

This module does not select a canonical source. It only excludes keys listed in
an externally verified quarantine manifest, using exact (interval, open_time_ms)
identity. It never shifts, rounds, merges, replaces, or edits source rows.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
from pathlib import Path

INTERVALS = {"1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"}
REQUIRED_MANIFEST_FIELDS = {"case_id", "case_class", "interval", "open_time_ms", "disposition", "canonical_source", "case_closed"}

class QuarantineManifestError(ValueError):
    pass

def exact_key(interval: object, open_time_ms: object) -> tuple[str, str]:
    """Validate and preserve an exact interval + integer-ms key; no rounding/coercion."""
    iv = str(interval)
    ts = str(open_time_ms)
    if iv not in INTERVALS:
        raise QuarantineManifestError(f"unsupported interval token: {iv!r}")
    if not re.fullmatch(r"[0-9]+", ts):
        raise QuarantineManifestError(f"open_time_ms must be an exact unsigned integer token: {ts!r}")
    return iv, ts

def load_quarantine_manifest(path: str | Path, *, expected_case_counts: dict[str, int] | None = None,
                             expected_sha256: str | None = None) -> tuple[set[tuple[str, str]], dict]:
    """Load only a complete, externally frozen manifest; optional hashes/counts are fail-closed gates."""
    import hashlib
    p = Path(path)
    if not p.is_file():
        raise QuarantineManifestError(f"quarantine manifest missing: {p}")
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    if expected_sha256 and digest.lower() != expected_sha256.lower():
        raise QuarantineManifestError("quarantine manifest SHA-256 mismatch")
    with p.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_MANIFEST_FIELDS - fields)
        if missing:
            raise QuarantineManifestError(f"manifest missing required fields: {missing}")
        rows = list(reader)
    if not rows:
        raise QuarantineManifestError("quarantine manifest is empty")
    case_ids = set()
    keys: set[tuple[str, str]] = set()
    counts: dict[str, int] = {}
    for line_no, row in enumerate(rows, 2):
        cid = (row.get("case_id") or "").strip()
        cls = (row.get("case_class") or "").strip()
        disposition = (row.get("disposition") or "").strip()
        canonical = (row.get("canonical_source") or "").strip()
        closed = (row.get("case_closed") or "").strip().lower()
        if not cid or not cls or not disposition:
            raise QuarantineManifestError(f"blank case identity/class/disposition at CSV line {line_no}")
        if cid in case_ids:
            raise QuarantineManifestError(f"duplicate case_id at CSV line {line_no}: {cid}")
        if closed not in {"true", "false"}:
            raise QuarantineManifestError(f"invalid case_closed at CSV line {line_no}: {closed!r}")
        if closed == "true" or canonical.upper() not in {"", "NONE", "UNRESOLVED"}:
            raise QuarantineManifestError(f"non-quarantine disposition in manifest at line {line_no}: {cid}")
        key = exact_key(row.get("interval", ""), row.get("open_time_ms", ""))
        case_ids.add(cid); keys.add(key); counts[cls] = counts.get(cls, 0) + 1
    if expected_case_counts is not None and counts != expected_case_counts:
        raise QuarantineManifestError(f"case-class counts mismatch: observed={counts}; expected={expected_case_counts}")
    return keys, {"status": "PASS_MANIFEST_VALIDATED", "sha256": digest, "manifest_rows": len(rows),
                  "unique_case_ids": len(case_ids), "unique_quarantine_keys": len(keys), "case_class_counts": counts}

def quarantine_rows(rows: list[dict], interval: str, keys: set[tuple[str, str]]) -> tuple[list[dict], list[dict]]:
    """Partition rows without modifying any field or changing key tokens."""
    kept, excluded = [], []
    for row in rows:
        key = exact_key(interval, row.get("open_time_ms", ""))
        (excluded if key in keys else kept).append(row)
    return kept, excluded

def _self_test() -> dict:
    tests = []
    def check(name, condition):
        tests.append({"test": name, "status": "PASS" if condition else "FAIL"})
        if not condition:
            raise AssertionError(name)
    ts = "1518170294789"
    keys = {exact_key("5m", ts)}
    fixture = [
        {"open_time_ms": ts, "open": "100", "raw_open_time_token": ts},
        {"open_time_ms": "1518170594789", "open": "101", "raw_open_time_token": "1518170594789"},
    ]
    kept, excluded = quarantine_rows(fixture, "5m", keys)
    check("exact_interval_timestamp_excluded", len(excluded) == 1 and excluded[0] is fixture[0])
    check("unlisted_timestamp_retained", len(kept) == 1 and kept[0] is fixture[1])
    other_interval, other_excluded = quarantine_rows([fixture[0]], "15m", keys)
    check("same_timestamp_other_interval_retained", len(other_interval) == 1 and not other_excluded)
    shifted, shifted_excluded = quarantine_rows([{"open_time_ms": "1518170294790"}], "5m", keys)
    check("one_ms_difference_not_rounded_or_matched", len(shifted) == 1 and not shifted_excluded)
    check("raw_tokens_untouched", fixture[0]["raw_open_time_token"] == ts and fixture[0]["open"] == "100")
    rejected = False
    try: exact_key("5m", "1518170294789.0")
    except QuarantineManifestError: rejected = True
    check("fractional_timestamp_token_rejected", rejected)
    rejected = False
    try: exact_key("5m", "1518170294789.5")
    except QuarantineManifestError: rejected = True
    check("no_rounding_on_fractional_token", rejected)
    return {"status": "PASS", "tests_passed": len(tests), "tests_total": len(tests), "tests": tests,
            "scope": "synthetic deterministic fixtures only; no market data read; no candidate build; no backtest"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--expected-sha256")
    ap.add_argument("--output", default="results/cp0040_quarantine_gate/CP0040_Quarantine_Gate_Summary.json")
    args = ap.parse_args()
    if not args.self_test and not args.manifest:
        ap.error("choose --self-test or provide --manifest")
    if args.self_test:
        summary = _self_test()
    else:
        _, summary = load_quarantine_manifest(args.manifest, expected_sha256=args.expected_sha256)
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if summary.get("status", "").startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
