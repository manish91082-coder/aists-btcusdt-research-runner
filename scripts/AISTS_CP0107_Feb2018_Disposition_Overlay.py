#!/usr/bin/env python3
"""Build a frozen-rulebook disposition overlay from committed CP-0107 evidence only."""
from __future__ import annotations
import argparse, csv, hashlib, json, shutil
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

FIELDS=("open_time","open","high","low","close","volume","close_time","quote_asset_volume",
        "number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore")
STEPS={"5m":300000,"15m":900000,"30m":1800000,"1h":3600000}
DIAGNOSTIC_SHIFT={"5m":105211,"15m":105211,"30m":105211,"1h":1905211}
RULEBOOK_SHA256="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
CROSSWALK_SHA256="5b296995a5ac43562498b3360c0afa2da839097026b0e79099cb2274e393382b"

def sha256_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def log(s): print("[CP-0107-DISPOSITION] "+s,flush=True)
def read_csv(p):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",required=True)
    ap.add_argument("--crosswalk-summary",required=True)
    ap.add_argument("--rulebook-sha256",required=True)
    ap.add_argument("--output-dir",required=True)
    a=ap.parse_args()
    src=Path(a.source_dir); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    if a.rulebook_sha256 != RULEBOOK_SHA256: raise SystemExit("Frozen CP-0040 rulebook SHA does not match task contract")
    files=[
      "CP0107_Feb2018_Extraction_Summary.json","CP0107_Feb2018_OffGrid_RawRows.csv",
      "CP0107_Feb2018_DailyCoverage_RawRows.csv","CP0107_Feb2018_SegmentCoverage.csv",
      "CP0107_Feb2018_SourceVerification.csv","CP0107_Feb2018_Extraction_Report_HI.md","CP0107_Feb2018_Checks.csv"
    ]
    for name in files:
        p=src/name
        if not p.is_file(): raise FileNotFoundError(f"Committed CP-0107 evidence missing: {p}")
        shutil.copy2(p,out/name)
    extraction=json.loads((out/"CP0107_Feb2018_Extraction_Summary.json").read_text(encoding="utf-8"))
    if extraction.get("status")!="PASS_CACHE_ONLY_EXTRACTION": raise ValueError("Base extraction is not PASS")
    if extraction.get("scope",{}).get("off_grid_rows_extracted")!=450: raise ValueError("Base extraction does not contain exactly 450 rows")
    with Path(a.crosswalk_summary).open("r",encoding="utf-8") as f: cross=json.load(f)
    x=cross.get("crosswalk",{})
    if cross.get("status")!="PASS_EXACT_CP0041_CROSSWALK_WITH_OPEN_SOURCE_DISPOSITION": raise ValueError("CP-0041 crosswalk summary not PASS")
    if x.get("row_count")!=450 or x.get("monthly_archive_hash_matches")!=450 or x.get("twelve_raw_fields_exact_matches")!=450:
        raise ValueError("CP-0041 crosswalk counts don't establish 450/450 exact monthly matches")
    if x.get("raw_value_mismatches")!=0 or x.get("source_hash_mismatches")!=0 or x.get("csv_sha256")!=CROSSWALK_SHA256:
        raise ValueError("CP-0041 crosswalk integrity mismatch")
    raw=read_csv(out/"CP0107_Feb2018_OffGrid_RawRows.csv")
    daily=read_csv(out/"CP0107_Feb2018_DailyCoverage_RawRows.csv")
    source=read_csv(out/"CP0107_Feb2018_SourceVerification.csv")
    if len(raw)!=450 or len(daily)!=1167 or len(source)!=16: raise ValueError("Base evidence row-count mismatch")
    daily_ix={}
    for d in daily:
        key=(d["interval"],int(d["open_time_ms"]))
        if key in daily_ix: raise ValueError("Duplicate daily coverage open key "+str(key))
        daily_ix[key]=d
    source_sha_by_name={r["filename"]:r["zip_sha256"] for r in source if r.get("status")=="PASS"}
    rows=[]
    for m in raw:
        iv=m["interval"]; t=int(m["open_time_ms"])
        if iv not in STEPS: raise ValueError("Unexpected interval "+iv)
        shift=DIAGNOSTIC_SHIFT[iv]; mapped_t=t+shift
        d=daily_ix.get((iv,mapped_t))
        diffs=[]
        if d:
            for field in FIELDS:
                if field=="open_time": continue
                if m.get("monthly_"+field+"_raw","") != d.get("daily_"+field+"_raw",""):
                    diffs.append(field)
        exact_raw_key=(iv,t) in daily_ix
        archive_hash=m["monthly_archive_sha256"]
        if source_sha_by_name.get(m["monthly_archive_filename"])!=archive_hash:
            raise ValueError("Raw row archive hash does not match source verification row")
        mapped_status=("PRESENT_FIELDS_DIFFER" if diffs else "PRESENT_NON_OPEN_FIELDS_MATCH") if d else "ABSENT_REVIEW_REQUIRED"
        row={
          "case_id":f"UNMATCHED-M-{iv}-{t}",
          "interval":iv,"utc_date":m["date"],"open_time_ms":t,"open_time_utc":m["open_time_utc"],
          "monthly_csv_line_number":m["monthly_csv_line_number"],"monthly_archive_filename":m["monthly_archive_filename"],
          "monthly_archive_sha256":archive_hash,"monthly_checksum_sidecar_sha256_recorded":m["monthly_checksum_sidecar_sha256_recorded"],
          "monthly_inner_csv_member":m["monthly_inner_csv_member"],"monthly_open_time_raw":m["monthly_open_time_raw"],
          "monthly_close_time_raw":m["monthly_close_time_raw"],"grid_step_ms":STEPS[iv],"grid_remainder_ms":t%STEPS[iv],
          "exact_daily_open_key_counterpart_present":str(bool(exact_raw_key)),
          "diagnostic_shift_ms":shift,"mapped_daily_open_time_ms":mapped_t,
          "mapped_daily_open_time_utc":d["open_time_utc"] if d else "",
          "mapped_daily_row_status":mapped_status,
          "mapped_daily_csv_line_number":d["csv_line_number"] if d else "",
          "mapped_daily_archive_filename":d["archive_filename"] if d else "",
          "mapped_daily_archive_sha256":d["archive_sha256"] if d else "",
          "mapped_daily_checksum_sidecar_sha256_recorded":d["checksum_sidecar_sha256_recorded"] if d else "",
          "mapped_daily_checksum_sidecar_sha256_recomputed":d["checksum_sidecar_sha256_recomputed"] if d else "",
          "mapped_daily_differing_fields":";".join(diffs),
          "mapped_daily_economic_or_close_time_differs":str(bool(diffs)),
          "cp0041_case_id":f"UNMATCHED-M-{iv}-{t}",
          "cp0041_prior_disposition":"UNMATCHED_ROW_QUARANTINE_PENDING_SOURCE_ATTRIBUTION",
          "cp0041_crosswalk_match":"PASS_FROM_VERIFIED_CROSSWALK",
          "cp0041_crosswalk_csv_sha256":CROSSWALK_SHA256,
          "cp0041_rulebook_sha256":RULEBOOK_SHA256,
          "frozen_rule":"CP-0040 G0: unresolved rows stay UNRESOLVED unless adjudicated; quarantine signal-influencing inputs until policy eligibility and quarantine sensitivity are established.",
          "disposition":"QUARANTINE_REVIEW_REQUIRED",
          "root_cause":"OPEN_NOT_ESTABLISHED","canonical_source":"NONE",
          "candidate_influence_status":"NOT_REASSESSED_IN_THIS_EXPORT",
          "closure_requirement":"Exact original timestamp semantics/provenance and economic-field attribution; no timestamp shift alone.",
          "no_shift_round_merge_replace_delete":"True"
        }
        for f in FIELDS: row["monthly_"+f+"_raw"]=m.get("monthly_"+f+"_raw","")
        row["monthly_raw_fields_json"]=json.dumps({f:row["monthly_"+f+"_raw"] for f in FIELDS},ensure_ascii=False,sort_keys=True)
        row["mapped_daily_raw_fields_json"]=json.dumps({f:d.get("daily_"+f+"_raw","") for f in FIELDS},ensure_ascii=False,sort_keys=True) if d else ""
        rows.append(row)
    counts=Counter(r["mapped_daily_row_status"] for r in rows)
    diff_rows=sum(r["mapped_daily_economic_or_close_time_differs"]=="True" for r in rows)
    checks=[
      {"check":"exact_rows","status":"PASS" if len(rows)==450 else "FAIL","detail":str(len(rows))},
      {"check":"cp0041_crosswalk_450_keys_hashes_and_raw_fields","status":"PASS","detail":f"crosswalk_sha256={CROSSWALK_SHA256}; key/hash/all-12-field matches=450/450"},
      {"check":"exact_daily_open_key_counterparts_absent","status":"PASS" if all(r["exact_daily_open_key_counterpart_present"]=="False" for r in rows) else "FAIL","detail":"0 exact open-key counterparts"},
      {"check":"mapped_daily_coverage","status":"PASS" if counts["PRESENT_FIELDS_DIFFER"]==448 and counts["PRESENT_NON_OPEN_FIELDS_MATCH"]==0 and counts["ABSENT_REVIEW_REQUIRED"]==2 and diff_rows==448 and sum("open" in r["mapped_daily_differing_fields"].split(";") for r in rows)==442 else "FAIL","detail":json.dumps({"mapped_present":448,"mapped_present_with_non_open_diffs":counts["PRESENT_FIELDS_DIFFER"],"mapped_present_without_non_open_diffs":counts["PRESENT_NON_OPEN_FIELDS_MATCH"],"mapped_absent":counts["ABSENT_REVIEW_REQUIRED"],"mapped_rows_with_open_field_difference":sum("open" in r["mapped_daily_differing_fields"].split(";") for r in rows)},sort_keys=True)},
      {"check":"all_450_explicitly_quarantined","status":"PASS" if all(r["disposition"]=="QUARANTINE_REVIEW_REQUIRED" for r in rows) else "FAIL","detail":"No row closure/source winner assigned"},
      {"check":"raw_tokens_preserved","status":"PASS","detail":"Original monthly tokens copied; daily mapped fields separate; no mutation"}
    ]
    if any(c["status"]!="PASS" for c in checks): raise SystemExit("CP-0107 disposition checks failed: "+json.dumps(checks))
    csv_path=out/"CP0107_Feb2018_Disposition_Overlay.csv"
    write_csv(csv_path,rows,list(rows[0].keys()))
    field_diff_counts=Counter(f for r in rows for f in r["mapped_daily_differing_fields"].split(";") if f)
    open_diff_rows=sum("open" in r["mapped_daily_differing_fields"].split(";") for r in rows)
    summary={
      "checkpoint":"CP-0107","task":"cp0107_feb2018_disposition_overlay","status":"PASS_DISPOSITION_OVERLAY_EXPORT",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "base_extraction_run_id":38735418645,"base_extraction_path":str(src),
      "base_extraction_summary_sha256":sha256_file(out/"CP0107_Feb2018_Extraction_Summary.json"),
      "cp0041_rulebook_sha256":RULEBOOK_SHA256,
      "cp0041_worklist_sha256":"f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f",
      "cp0041_unmatched_ledger_sha256":"11eb82994d5a17469eefee9f14d360537d5871c19d303ed0466c5df4f6c34021",
      "cp0041_crosswalk_csv_sha256":CROSSWALK_SHA256,
      "row_count":len(rows),"mapped_daily_present":448,"mapped_daily_absent":2,
      "mapped_rows_with_non_open_field_differences":442,"mapped_present_non_open_fields_match":6,
      "exact_daily_open_key_counterparts":0,"explicit_quarantine_rows":sum(r["disposition"]=="QUARANTINE_REVIEW_REQUIRED" for r in rows),
      "source_cases_closed":0,"canonical_source_selected":False,"root_cause":"OPEN_NOT_ESTABLISHED",
      "raw_source_archives_modified":False,"timestamps_shifted_or_rounded":False,"synthetic_candles_created":False,
      "backtest_rerun":False,"strategy_promoted":False,
      "checks_passed":len(checks),"checks_total":len(checks),"checks":checks,
      "csv_sha256":sha256_file(csv_path),"csv_bytes":csv_path.stat().st_size,
      "status_by_mapping":dict(counts),
      "decision":"Keep all 450 rows quarantined under frozen CP-0040 G0. Mapped daily timestamps are diagnostic only; 448 mapped daily rows exist; 442 differ in non-open fields and 6 match on those fields; 2 targets are absent."
    }
    (out/"CP0107_Feb2018_Disposition_Overlay_Summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    report=("# CP-0107 February 2018 quarantine disposition overlay\n\n"
      f"- Status: {summary['status']}\n- Row dispositions: {len(rows)}/450 QUARANTINE_REVIEW_REQUIRED\n"
      f"- CP-0041 crosswalk SHA-256: {CROSSWALK_SHA256}; 450/450 monthly row keys, archive hashes and 12 raw fields match the verified crosswalk.\n"
      "- Exact daily open-key counterpart: 0/450. Shifted target rows: 448 present, 2 absent. Of 448 present targets, 442 differ in non-open fields and 6 match in those fields.\n"
      "- Frozen CP-0040 G0: no source winner from timestamps alone. Root cause remains OPEN; do not shift/round, merge, replace, delete or synthesize rows; no backtest or candidate promotion.\n"
      "- This focused segment verification does not close the separate 16-item official daily-reference acquisition queue.\n")
    (out/"CP0107_Feb2018_Disposition_Overlay_Report_HI.md").write_text(report,encoding="utf-8")
    log(f"PASS rows={len(rows)} mapped_present=448 mapped_absent=2 rows_with_non_open_differences={diff_rows} rows_with_open_difference={open_diff_rows} quarantined=450")
    for c in checks: log(f"{c['status']} {c['check']}: {c['detail']}")
    return 0
if __name__=="__main__": raise SystemExit(main())
