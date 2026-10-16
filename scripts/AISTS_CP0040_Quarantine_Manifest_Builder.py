#!/usr/bin/env python3
"""Build a row-level CP-0040 quarantine manifest from the frozen 996-row Git index.

This task never builds candidate market data or chooses a canonical source. The 27
non-row blockers remain explicit and make candidate eligibility false.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "evidence/source_adjudication/CP0107_CP0041_Derived_996_Row_GitIndex_Minimal.csv.gz"
INDEX_SHA256 = "a3a961a3e3ff0783c1cfed6efafddef313f7c455148a9a5174e95feef80062bf"
INDEX_EXPANDED_SHA256 = "072009025272fcba372b820a2ecbd1c65f5938138c5206f19e7cfcdf83ecc39b"
RULEBOOK_SHA256 = "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
EXPECTED_RECORD_COUNTS = {
    "MONTHLY_ONLY_ROW": 457,
    "DAILY_ONLY_ROW": 452,
    "SHARED_OPEN_VALUE_CONFLICT": 60,
    "RESIDUAL_AGGREGATION_BUCKET": 11,
    "MISSING_DAILY_REFERENCE_ACQUISITION": 16,
}
EXPECTED_ROW_CLASS_COUNTS = {
    "MONTHLY_ONLY_ROW": 457,
    "DAILY_ONLY_ROW": 452,
    "SHARED_ECONOMIC_CONFLICT": 52,
    "CLOSE_TIME_ONLY": 8,
}
REQUIRED_INDEX_FIELDS = {
    "case_id", "record_type", "interval", "utc_date", "open_time_utc",
    "effective_current_disposition", "original_current_disposition",
}
INTERVALS = {"1m","3m","5m","15m","30m","1h","2h","4h","6h","8h","12h","1d","3d","1w","1mo"}

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def timestamp_ms_from_iso(value: str) -> int:
    token = (value or "").strip()
    if not token:
        raise ValueError("blank open_time_utc")
    dt = datetime.fromisoformat(token.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"naive timestamp is forbidden: {token}")
    dt = dt.astimezone(timezone.utc)
    if dt.microsecond % 1000:
        raise ValueError(f"timestamp has sub-millisecond precision: {token}")
    return int(dt.timestamp()) * 1000 + dt.microsecond // 1000

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="results/cp0040_quarantine_manifest")
    args = ap.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    checks = []
    def check(name, ok, detail):
        checks.append({"check_id": name, "status": "PASS" if ok else "FAIL", "detail": str(detail)})
        if not ok:
            raise RuntimeError(f"{name}: {detail}")

    index_bytes = INDEX.read_bytes()
    index_sha = sha256_bytes(index_bytes)
    check("frozen_index_sha256", index_sha == INDEX_SHA256, f"observed={index_sha}; expected={INDEX_SHA256}")
    raw = gzip.decompress(index_bytes)
    expanded_sha = sha256_bytes(raw)
    check("expanded_index_sha256", expanded_sha == INDEX_EXPANDED_SHA256, f"observed={expanded_sha}; expected={INDEX_EXPANDED_SHA256}")
    import io
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    fields = set(reader.fieldnames or [])
    check("index_schema", REQUIRED_INDEX_FIELDS.issubset(fields), f"fields={sorted(fields)}")
    rows = list(reader)
    check("index_row_count", len(rows) == 996, f"rows={len(rows)}")
    ids = [r["case_id"].strip() for r in rows]
    check("case_id_unique", len(ids) == len(set(ids)) == 996, f"unique={len(set(ids))}")
    type_counts = Counter(r["record_type"].strip() for r in rows)
    check("record_type_counts", dict(type_counts) == EXPECTED_RECORD_COUNTS, dict(type_counts))

    shared52_path = ROOT / "evidence/source_adjudication/CP0107_Shared52_EvidenceLinked_Disposition_Matrix.csv"
    close8_path = ROOT / "evidence/source_adjudication/CP0107_CloseTimeOnly_FieldDisposition_Final.csv"
    delta450_path = ROOT / "evidence/source_adjudication/CP0107_CP0041_Worklist_Disposition_Delta_450.csv"
    shared52 = read_csv(shared52_path)
    close8 = read_csv(close8_path)
    delta450 = read_csv(delta450_path)
    shared_ids = {r["case_id"].strip() for r in shared52}
    close_ids = {r["case_id"].strip() for r in close8}
    shared_worklist_ids = {r["case_id"].strip() for r in rows if r["record_type"] == "SHARED_OPEN_VALUE_CONFLICT"}
    check("shared52_count_and_unique", len(shared52) == len(shared_ids) == 52, f"rows={len(shared52)} unique={len(shared_ids)}")
    check("close8_count_and_unique", len(close8) == len(close_ids) == 8, f"rows={len(close8)} unique={len(close_ids)}")
    check("shared52_close8_disjoint", not (shared_ids & close_ids), f"overlap={sorted(shared_ids & close_ids)}")
    check("shared52_close8_cover_all_shared60", shared_ids | close_ids == shared_worklist_ids, f"union={len(shared_ids | close_ids)}; shared_worklist={len(shared_worklist_ids)}")
    delta_ids = {r["case_id"].strip() for r in delta450}
    unmatched_ids = {r["case_id"].strip() for r in rows if r["record_type"] in {"MONTHLY_ONLY_ROW","DAILY_ONLY_ROW"}}
    check("offgrid450_subset_of_unmatched909", len(delta450) == len(delta_ids) == 450 and delta_ids <= unmatched_ids, f"delta={len(delta_ids)}; unmatched={len(unmatched_ids)}; outside={len(delta_ids-unmatched_ids)}")
    check("offgrid450_disposition", all(r.get("proposed_worklist_disposition") == "QUARANTINE_REVIEW_REQUIRED" and r.get("canonical_source") == "NONE" and str(r.get("case_closed","")).lower() == "false" for r in delta450), "all 450 remain quarantine-review-required and open")

    manifest = []
    blockers = []
    key_set = set()
    row_class_counts = Counter()
    key_errors = []
    for row in rows:
        cid = row["case_id"].strip()
        rtype = row["record_type"].strip()
        disposition = row["effective_current_disposition"].strip()
        if rtype in {"RESIDUAL_AGGREGATION_BUCKET","MISSING_DAILY_REFERENCE_ACQUISITION"}:
            blockers.append({
                "case_id": cid, "record_type": rtype, "interval": row["interval"].strip(),
                "utc_date": row["utc_date"].strip(), "disposition": disposition,
                "reason": "NO_EXACT_ROW_OPEN_KEY_IN_FROZEN_MINIMAL_INDEX; candidate eligibility remains blocked",
            })
            continue
        match = re.search(r"-(\d{13})$", cid)
        if not match:
            key_errors.append({"case_id":cid,"error":"case_id lacks exact 13-digit millisecond suffix"})
            continue
        ts = match.group(1)
        interval = row["interval"].strip()
        if interval not in INTERVALS:
            key_errors.append({"case_id":cid,"error":f"unsupported or blank interval: {interval!r}"})
            continue
        try:
            iso_ms = timestamp_ms_from_iso(row["open_time_utc"])
        except Exception as exc:
            key_errors.append({"case_id":cid,"error":str(exc)})
            continue
        if str(iso_ms) != ts:
            key_errors.append({"case_id":cid,"error":f"case_id timestamp {ts} != ISO exact-ms {iso_ms}"})
            continue
        if rtype == "SHARED_OPEN_VALUE_CONFLICT":
            if cid in shared_ids: case_class = "SHARED_ECONOMIC_CONFLICT"
            elif cid in close_ids: case_class = "CLOSE_TIME_ONLY"
            else:
                key_errors.append({"case_id":cid,"error":"shared conflict not classified by either frozen matrix"})
                continue
        elif rtype in {"MONTHLY_ONLY_ROW","DAILY_ONLY_ROW"}:
            case_class = rtype
        else:
            key_errors.append({"case_id":cid,"error":f"unexpected row-level record type: {rtype}"})
            continue
        key = (interval, ts)
        key_set.add(key)
        row_class_counts[case_class] += 1
        manifest.append({
            "case_id": cid, "case_class": case_class, "interval": interval, "open_time_ms": ts,
            "disposition": disposition, "canonical_source": "NONE", "case_closed": "false",
            "source_record_type": rtype, "source_disposition_original": row["original_current_disposition"].strip(),
            "source_index_sha256": index_sha, "source_index_expanded_sha256": expanded_sha,
            "source_worklist_sha256": "f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f",
            "cp0040_rulebook_sha256": RULEBOOK_SHA256,
        })
    check("row_key_validation", not key_errors, json.dumps(key_errors[:10], ensure_ascii=False))
    check("row_manifest_count", len(manifest) == 969, f"manifest_rows={len(manifest)}")
    check("row_class_counts", dict(row_class_counts) == EXPECTED_ROW_CLASS_COUNTS, dict(row_class_counts))
    check("unique_exact_keys", len(key_set) == len(manifest), f"unique_keys={len(key_set)} manifest_rows={len(manifest)}")
    check("nonrow_blocker_inventory", len(blockers) == 27 and Counter(x["record_type"] for x in blockers) == {"RESIDUAL_AGGREGATION_BUCKET":11,"MISSING_DAILY_REFERENCE_ACQUISITION":16}, f"count={len(blockers)} types={dict(Counter(x['record_type'] for x in blockers))}")

    manifest_path = out / "CP0040_ExactKey_Quarantine_Manifest.csv"
    blockers_path = out / "CP0040_NonRow_Blockers.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()), lineterminator="\n"); w.writeheader(); w.writerows(manifest)
    with blockers_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(blockers[0].keys()), lineterminator="\n"); w.writeheader(); w.writerows(blockers)
    manifest_sha = sha256_bytes(manifest_path.read_bytes())
    blockers_sha = sha256_bytes(blockers_path.read_bytes())
    summary = {
        "checkpoint":"CP0040_EXACT_KEY_QUARANTINE_MANIFEST",
        "status":"PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN",
        "checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),"checks":checks,
        "inputs":{
            "index_path":"evidence/source_adjudication/CP0107_CP0041_Derived_996_Row_GitIndex_Minimal.csv.gz",
            "index_bytes":len(index_bytes),"index_sha256":index_sha,"expanded_index_bytes":len(raw),"expanded_index_sha256":expanded_sha,
            "shared52_sha256":sha256_bytes(shared52_path.read_bytes()),"close8_sha256":sha256_bytes(close8_path.read_bytes()),
            "delta450_sha256":sha256_bytes(delta450_path.read_bytes()),"cp0040_rulebook_sha256":RULEBOOK_SHA256,
            "original_worklist_sha256":"f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f"
        },
        "row_level_manifest":{
            "rows":len(manifest),"unique_exact_keys":len(key_set),"sha256":manifest_sha,
            "case_class_counts":dict(row_class_counts),"source_record_type_counts":dict(type_counts),
            "offgrid450_are_subset_of_unmatched909":True,"shared52_plus_close8_cover_shared60":True,
            "all_cases_open":all(x["case_closed"]=="false" for x in manifest),"canonical_source":"NONE"
        },
        "nonrow_blockers":{
            "rows":len(blockers),"sha256":blockers_sha,
            "record_type_counts":dict(Counter(x["record_type"] for x in blockers)),
            "candidate_eligibility_blocked":True,
            "reason":"11 aggregation buckets and 16 missing daily-reference acquisition cases do not carry exact row keys in this frozen index and remain unresolved."
        },
        "outputs":{
            manifest_path.name:{"bytes":manifest_path.stat().st_size,"sha256":manifest_sha,"rows":len(manifest)},
            blockers_path.name:{"bytes":blockers_path.stat().st_size,"sha256":blockers_sha,"rows":len(blockers)}
        },
        "decisions":{
            "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
            "timestamp_shifted_or_rounded":False,"raw_rows_merged_replaced_or_deleted":False,
            "synthetic_candles_created":False,"candidate_built":False,"backtest_rerun":False,"strategy_promoted":False,
            "candidate_eligibility":"BLOCKED_NONROW_SOURCE_AND_COVERAGE_CASES_REMAIN"
        }
    }
    summary_path = out / "CP0040_ExactKey_Quarantine_Manifest_Summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True)+"\n", encoding="utf-8")
    report_path = out / "CP0040_ExactKey_Quarantine_Manifest_Report_HI.md"
    report = (
        "# CP-0040 Exact-Key Quarantine Manifest\n\n"
        "## परिणाम\n"
        f"**{summary['status']}** — {summary['checks_passed']}/{summary['checks_total']} checks PASS.\n\n"
        f"- Row-level exact-key manifest: {len(manifest)} rows; {len(key_set)} unique interval/open_time_ms keys.\n"
        f"- Daily-only: {row_class_counts['DAILY_ONLY_ROW']}; monthly-only: {row_class_counts['MONTHLY_ONLY_ROW']}; shared economic conflicts: {row_class_counts['SHARED_ECONOMIC_CONFLICT']}; close-time-only: {row_class_counts['CLOSE_TIME_ONLY']}.\n"
        "- February 2018 off-grid 450 rows are a subset of the 909 unmatched rows and were not double-counted.\n"
        f"- Frozen index SHA-256: {index_sha}; expanded index SHA-256: {expanded_sha}.\n"
        f"- Manifest SHA-256: {manifest_sha}; non-row blockers SHA-256: {blockers_sha}.\n\n"
        "## अभी भी blocking\n"
        "27 non-row cases: 11 RESIDUAL_AGGREGATION_BUCKET and 16 MISSING_DAILY_REFERENCE_ACQUISITION. The frozen index has no exact interval plus millisecond open-time key for these records. They are kept in a separate blocker ledger rather than assigning guessed timestamps.\n\n"
        "## निर्णय\n"
        "- This validates the frozen published index and evidence matrices; it is not a fresh raw-byte rehash of the original CP-0041 package/rulebook.\n"
        "- No canonical source selected; no cases closed.\n"
        "- No candidate build or backtest run.\n"
        "- Candidate eligibility remains BLOCKED until the 27 non-row blockers are adjudicated and fail-closed builder integration is tested.\n"
    )
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
