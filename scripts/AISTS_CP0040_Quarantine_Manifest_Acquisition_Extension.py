#!/usr/bin/env python3
"""Extend the CP-0040 quarantine manifest with the previously acquired 16-period row audit.

The official daily ZIPs are not downloaded here. The script reuses the committed,
hash-verified CP-0041 comparison and only adds unresolved exact row keys to a new
append-only manifest version. No source authority is selected.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_RUN="CP0040_Run_38882377148"
ACQ_RUN="CP0107_Run_38776970911"
EXPECTED_COMPARISON_SHA="ac08f6839e172919634d2823ae1f6df4d74613e473419b8c00881527e40906ba"
EXPECTED_COMPARISON_BYTES=1509065
EXPECTED_COMPARISON_ROWS=1992
EXPECTED_INDEX_SHA="a3a961a3e3ff0783c1cfed6efafddef313f7c455148a9a5174e95feef80062bf"
RULEBOOK_SHA="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
WORKLIST_SHA="f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f"
OPEN_RELATIONS={"SHARED_RAW_DIVERGENT","MONTHLY_ONLY_KEY","DAILY_ONLY_KEY","DUPLICATE_KEY_REVIEW"}
EXTENSION_FIELDS=[
 "acquisition_extension_relation","acquisition_source_case_id","acquisition_differing_raw_fields",
 "acquisition_economic_differing_fields","acquisition_monthly_archive","acquisition_monthly_sha256",
 "acquisition_daily_archive","acquisition_daily_sha256","acquisition_comparison_sha256",
 "acquisition_disposition",
]

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_csv(path: Path) -> list[dict]:
    with path.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n")
        w.writeheader();w.writerows(rows)

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",default="results/cp0040_quarantine_manifest")
    args=ap.parse_args()
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    base=ROOT/"evidence/source_adjudication"/BASE_RUN
    acq=ROOT/"evidence/source_adjudication"/ACQ_RUN
    base_manifest=base/"CP0040_ExactKey_Quarantine_Manifest.csv"
    base_blockers=base/"CP0040_NonRow_Blockers.csv"
    base_summary_path=base/"CP0040_ExactKey_Quarantine_Manifest_Summary.json"
    comparison_path=acq/"CP0107_CP0041_DailyReference_RawRow_Comparison.csv"
    missing_path=acq/"CP0107_CP0041_DailyReference_MissingExpectedKeys.csv"
    acquisition_summary_path=acq/"CP0107_CP0041_DailyReference_Acquisition_Summary.json"
    checks=[]
    def check(name,ok,detail):
        checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
        if not ok: raise RuntimeError(f"{name}: {detail}")

    base_summary=json.loads(base_summary_path.read_text(encoding="utf-8"))
    base_manifest_bytes=base_manifest.read_bytes()
    base_manifest_sha=sha(base_manifest_bytes)
    check("base_manifest_sha256",base_manifest_sha==base_summary["row_level_manifest"]["sha256"],base_manifest_sha)
    base_rows=read_csv(base_manifest)
    base_keys={(r["interval"],r["open_time_ms"]) for r in base_rows}
    check("base_manifest_unique_keys",len(base_rows)==969 and len(base_keys)==969,f"rows={len(base_rows)} keys={len(base_keys)}")
    blockers=read_csv(base_blockers)
    check("base_blockers_27",len(blockers)==27 and Counter(r["record_type"] for r in blockers)=={"RESIDUAL_AGGREGATION_BUCKET":11,"MISSING_DAILY_REFERENCE_ACQUISITION":16},f"rows={len(blockers)}")

    acquisition_summary=json.loads(acquisition_summary_path.read_text(encoding="utf-8"))
    check("acquisition_summary_pass",acquisition_summary.get("status")=="PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED",acquisition_summary.get("status"))
    check("acquisition_checks_all_pass",acquisition_summary.get("checks_passed")==acquisition_summary.get("checks_total")==98,
          f"{acquisition_summary.get('checks_passed')}/{acquisition_summary.get('checks_total')}")
    check("all_16_archives_and_sidecars_verified",acquisition_summary.get("queue_count")==16 and acquisition_summary.get("daily_archive_count")==16 and acquisition_summary.get("daily_sidecar_count")==16,
          f"queue={acquisition_summary.get('queue_count')} ZIPs={acquisition_summary.get('daily_archive_count')} sidecars={acquisition_summary.get('daily_sidecar_count')}")
    check("14_monthly_archives_reused",acquisition_summary.get("monthly_archive_count")==14 and acquisition_summary.get("monthly_zip_redownloads")==0,
          f"monthly={acquisition_summary.get('monthly_archive_count')} redownloads={acquisition_summary.get('monthly_zip_redownloads')}")
    comparison_bytes=comparison_path.read_bytes()
    comparison_sha=sha(comparison_bytes)
    recorded=acquisition_summary.get("outputs",{}).get(comparison_path.name,{})
    check("comparison_sha_and_size",comparison_sha==EXPECTED_COMPARISON_SHA==recorded.get("sha256") and len(comparison_bytes)==EXPECTED_COMPARISON_BYTES==recorded.get("bytes"),
          f"sha={comparison_sha}; bytes={len(comparison_bytes)}")
    comparison=read_csv(comparison_path)
    check("comparison_row_count",len(comparison)==EXPECTED_COMPARISON_ROWS==recorded.get("rows"),f"rows={len(comparison)}")
    metric=acquisition_summary["comparison"]
    relation_counts=Counter(r["row_relation"] for r in comparison)
    check("comparison_relation_counts",
          relation_counts=={"SHARED_RAW_EXACT":1550,"SHARED_RAW_DIVERGENT":432,"MONTHLY_ONLY_KEY":10},
          dict(relation_counts))
    check("comparison_summary_metrics",
          metric.get("union_open_key_rows")==1992 and metric.get("shared_open_keys")==1982 and
          metric.get("exact_raw_row_pairs")==1550 and metric.get("divergent_raw_row_pairs")==432 and
          metric.get("monthly_only_keys")==10 and metric.get("daily_only_keys")==0 and
          metric.get("economic_field_divergent_pairs")==14 and metric.get("missing_expected_keys_rows")==10,
          json.dumps(metric,sort_keys=True))
    open_rows=[r for r in comparison if r["row_relation"] in OPEN_RELATIONS]
    check("open_comparison_rows",len(open_rows)==442 and all(r.get("disposition")=="OPEN_REVIEW_REQUIRED" for r in open_rows),
          f"open_rows={len(open_rows)}")
    economic_rows=[r for r in open_rows if int(r.get("economic_differing_field_count") or 0)>0]
    monthly_only=[r for r in open_rows if r["row_relation"]=="MONTHLY_ONLY_KEY"]
    check("economic_and_monthly_only_counts",len(economic_rows)==14 and len(monthly_only)==10,
          f"economic={len(economic_rows)} monthly_only={len(monthly_only)}")
    missing_rows=read_csv(missing_path)
    missing_keys={(r["interval"],r["expected_open_time_ms"]) for r in missing_rows}
    monthly_only_keys={(r["interval"],str(r["open_time_ms"])) for r in monthly_only}
    check("missing_expected_grid_keys_equal_monthly_only",len(missing_rows)==10 and missing_keys==monthly_only_keys,
          f"missing={len(missing_keys)} monthly_only={len(monthly_only_keys)} exact_set_match={missing_keys==monthly_only_keys}")
    queue_ids={r["case_id"] for r in comparison}
    old_fetch_ids={r["case_id"] for r in blockers if r["record_type"]=="MISSING_DAILY_REFERENCE_ACQUISITION"}
    check("all_16_acquisition_blockers_have_verified_comparison",len(old_fetch_ids)==16 and old_fetch_ids==queue_ids,
          f"blockers={len(old_fetch_ids)} queue_cases={len(queue_ids)}")

    by_key={ (r["interval"],r["open_time_ms"]):dict(r) for r in base_rows}
    if len(by_key)!=len(base_rows): raise RuntimeError("base manifest duplicate exact keys")
    enriched=0;added=0;new_class_counts=Counter();seen_acq_keys=set()
    for row in open_rows:
        iv=str(row["interval"]);ts=str(row["open_time_ms"])
        if not ts.isdigit(): raise RuntimeError(f"non-integer exact open key: {row.get('case_id')}")
        key=(iv,ts)
        if key in seen_acq_keys: raise RuntimeError(f"duplicate open-review key in acquisition comparison: {key}")
        seen_acq_keys.add(key)
        relation=row["row_relation"]
        econ=int(row.get("economic_differing_field_count") or 0)>0
        if relation=="MONTHLY_ONLY_KEY": case_class="ACQUISITION_MONTHLY_ONLY_ROW"
        elif econ: case_class="ACQUISITION_ECONOMIC_CONFLICT"
        else: case_class="ACQUISITION_RAW_FIELD_CONFLICT"
        evidence={
          "acquisition_extension_relation":relation,
          "acquisition_source_case_id":row["case_id"],
          "acquisition_differing_raw_fields":row.get("differing_raw_fields",""),
          "acquisition_economic_differing_fields":row.get("economic_differing_fields",""),
          "acquisition_monthly_archive":row.get("monthly_archive_filename",""),
          "acquisition_monthly_sha256":row.get("monthly_archive_sha256",""),
          "acquisition_daily_archive":row.get("daily_archive_filename",""),
          "acquisition_daily_sha256":row.get("daily_archive_sha256",""),
          "acquisition_comparison_sha256":comparison_sha,
          "acquisition_disposition":row.get("disposition","OPEN_REVIEW_REQUIRED"),
        }
        if key in by_key:
            existing=by_key[key]
            for field,value in evidence.items():
                if existing.get(field) and existing[field]!=value:
                    raise RuntimeError(f"conflicting acquisition extension metadata for existing key {key} field {field}")
                existing[field]=value
            enriched+=1
        else:
            cid=f"ACQ-{iv}-{ts}"
            if any(x["case_id"]==cid for x in by_key.values()):
                raise RuntimeError(f"generated case ID collision: {cid}")
            item={
              "case_id":cid,"case_class":case_class,"interval":iv,"open_time_ms":ts,
              "disposition":"OPEN_REVIEW_REQUIRED","canonical_source":"NONE","case_closed":"false",
              "source_record_type":relation,"source_disposition_original":"OPEN_REVIEW_REQUIRED",
              "source_index_sha256":EXPECTED_INDEX_SHA,"source_index_expanded_sha256":base_summary["inputs"]["expanded_index_sha256"] if "expanded_index_sha256" in base_summary.get("inputs",{}) else "",
              "source_worklist_sha256":WORKLIST_SHA,"cp0040_rulebook_sha256":RULEBOOK_SHA,
            }
            item.update({field:"" for field in EXTENSION_FIELDS});item.update(evidence)
            by_key[key]=item;added+=1;new_class_counts[case_class]+=1

    final_rows=list(by_key.values())
    final_rows.sort(key=lambda r:(r["interval"],int(r["open_time_ms"])))
    final_keys={(r["interval"],r["open_time_ms"]) for r in final_rows}
    check("final_manifest_unique_keys",len(final_rows)==len(final_keys),f"rows={len(final_rows)} keys={len(final_keys)}")
    check("extension_key_accounting",added+enriched==len(open_rows),f"open_rows={len(open_rows)} added={added} enriched={enriched}")
    check("final_cases_open_no_source_authority",all(r["canonical_source"]=="NONE" and str(r["case_closed"]).lower()=="false" for r in final_rows),"all open and canonical source NONE")
    class_counts=Counter(r["case_class"] for r in final_rows)
    final_blockers=[dict(r) for r in blockers if r["record_type"]!="MISSING_DAILY_REFERENCE_ACQUISITION"]
    check("acquisition_blockers_resolved_by_row_audit",len(final_blockers)==11 and Counter(r["record_type"] for r in final_blockers)=={"RESIDUAL_AGGREGATION_BUCKET":11},
          f"remaining={len(final_blockers)} types={dict(Counter(r['record_type'] for r in final_blockers))}")

    manifest_fields=list(base_rows[0].keys())+[f for f in EXTENSION_FIELDS if f not in base_rows[0]]
    manifest_path=out/"CP0040_ExactKey_Quarantine_Manifest.csv"
    blockers_path=out/"CP0040_NonRow_Blockers.csv"
    write_csv(manifest_path,final_rows,manifest_fields)
    blocker_fields=list(blockers[0].keys())
    write_csv(blockers_path,final_blockers,blocker_fields)
    manifest_sha=sha(manifest_path.read_bytes());blockers_sha=sha(blockers_path.read_bytes())
    output_info={
      manifest_path.name:{"bytes":manifest_path.stat().st_size,"sha256":manifest_sha,"rows":len(final_rows)},
      blockers_path.name:{"bytes":blockers_path.stat().st_size,"sha256":blockers_sha,"rows":len(final_blockers)}
    }
    summary={
      "checkpoint":"CP0040_EXACT_KEY_QUARANTINE_MANIFEST_ACQUISITION_EXTENSION",
      "status":"PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN",
      "checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),"checks":checks,
      "inputs":{
        "base_manifest_run_id":38882377148,"base_manifest_sha256":base_manifest_sha,"base_manifest_rows":len(base_rows),
        "comparison_path":str(comparison_path.relative_to(ROOT)),"comparison_bytes":len(comparison_bytes),"comparison_sha256":comparison_sha,
        "comparison_rows":len(comparison),"acquisition_summary_sha256":sha(acquisition_summary_path.read_bytes()),
        "missing_expected_keys_sha256":sha(missing_path.read_bytes()),"source_package_sha256":acquisition_summary["provenance"]["source_package_sha256"],
        "cp0040_rulebook_sha256":RULEBOOK_SHA,"original_worklist_sha256":WORKLIST_SHA
      },
      "row_level_manifest":{
        "rows":len(final_rows),"unique_exact_keys":len(final_keys),"sha256":manifest_sha,"case_class_counts":dict(class_counts),
        "new_unique_keys_added_from_acquisition":added,"existing_keys_enriched_with_acquisition_evidence":enriched,
        "acquisition_open_rows_reviewed":len(open_rows),"acquisition_row_relation_counts":dict(relation_counts),
        "acquisition_economic_field_divergent_pairs":len(economic_rows),"acquisition_monthly_only_keys":len(monthly_only),
        "acquisition_missing_expected_keys_exactly_represented_as_monthly_only":True,
        "offgrid450_subset_of_original_unmatched909":True,"canonical_source":"NONE","all_cases_open":True
      },
      "nonrow_blockers":{
        "rows":len(final_blockers),"sha256":blockers_sha,"record_type_counts":dict(Counter(r["record_type"] for r in final_blockers)),
        "candidate_eligibility_blocked":True,
        "reason":"11 residual aggregation buckets remain unresolved; no guessed timestamp or synthetic row was added."
      },
      "acquisition_extension":{
        "daily_archives_verified":16,"daily_sidecars_verified":16,"monthly_archives_reused_and_verified":14,
        "raw_comparison_rows":len(comparison),"raw_divergent_pairs":relation_counts["SHARED_RAW_DIVERGENT"],
        "economic_field_divergent_pairs":len(economic_rows),"non_economic_raw_field_divergent_pairs":relation_counts["SHARED_RAW_DIVERGENT"]-len(economic_rows),
        "monthly_only_keys":len(monthly_only),"daily_only_keys":relation_counts["DAILY_ONLY_KEY"],
        "source_cases_closed":0,"canonical_source_selected":False
      },
      "outputs":output_info,
      "decisions":{
        "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
        "timestamp_shifted_or_rounded":False,"raw_rows_merged_replaced_or_deleted":False,
        "synthetic_candles_created":False,"candidate_built":False,"backtest_rerun":False,"strategy_promoted":False,
        "candidate_eligibility":"BLOCKED_RESIDUAL_AGGREGATION_BUCKETS_REMAIN"
      }
    }
    summary_path=out/"CP0040_ExactKey_Quarantine_Manifest_Summary.json"
    summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    report_path=out/"CP0040_ExactKey_Quarantine_Manifest_Report_HI.md"
    report=(
      "# CP-0040 Exact-Key Quarantine Manifest: Acquisition Extension\n\n"
      f"**{summary['status']}** — {summary['checks_passed']}/{summary['checks_total']} checks PASS.\n\n"
      f"- Prior manifest: {len(base_rows)} rows; acquisition evidence reviewed: {len(open_rows)} open row keys.\n"
      f"- New unique exact keys added: {added}; existing keys enriched with acquisition provenance: {enriched}.\n"
      f"- Final manifest: {len(final_rows)} rows / {len(final_keys)} unique (interval, open_time_ms) keys; SHA-256 {manifest_sha}.\n"
      f"- Acquisition comparison: 1,550 exact raw pairs, 432 divergent raw pairs (14 economic-field divergent; {432-14} non-economic raw-field divergent), 10 monthly-only keys, 0 daily-only keys.\n"
      "- The 10 absent expected-grid keys match the 10 monthly-only keys exactly; they are represented as open row-level quarantine cases, not synthetic candles.\n"
      "- All 16 official daily ZIP/.CHECKSUM pairs were already acquired and hash-verified in the prior audit; no downloads were performed by this extension task.\n"
      f"- The 16 archive-acquisition blockers were replaced by row-level evidence. Remaining non-row blockers: {len(final_blockers)} residual aggregation buckets. No canonical source chosen; no source cases closed.\n\n"
      "## Gate decision\n"
      "Candidate eligibility remains BLOCKED by the 11 unresolved cross-interval aggregation buckets. No candidate dataset or backtest was run. No timestamps were shifted or rounded, no rows were merged/replaced/deleted, and no synthetic candles were created.\n"
    )
    report_path.write_text(report,encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
