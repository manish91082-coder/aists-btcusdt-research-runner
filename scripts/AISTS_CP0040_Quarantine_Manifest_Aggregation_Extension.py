#!/usr/bin/env python3
"""Add exact row keys implicated by the 11 frozen aggregation buckets to CP-0040 quarantine.

This is quarantine-only. It does not repair parent/child values, infer source authority,
close aggregation cases, or run a candidate build/backtest.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AGG_RUN="CP0107_Run_38776970911"
RULEBOOK_SHA="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
WORKLIST_SHA="f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f"
EXTRA_FIELDS=[
 "aggregation_bucket_case_ids","aggregation_bucket_roles","aggregation_source_row_relations",
 "aggregation_row_evidence_sha256","aggregation_bucket_comparison_sha256","aggregation_bucket_summary_sha256",
 "aggregation_bucket_disposition",
]

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def read_csv(p: Path) -> list[dict]:
    with p.open("r",newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def write_csv(p: Path,rows: list[dict],fields: list[str]):
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output-dir",default="results/cp0040_quarantine_manifest");args=ap.parse_args()
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    pointer_path=ROOT/"evidence/source_adjudication/CP0040_Current_Manifest.json"
    pointer=json.loads(pointer_path.read_text(encoding="utf-8"))
    base_manifest=ROOT/pointer["manifest_path"];base_blockers=ROOT/pointer["blockers_path"];base_summary_path=ROOT/pointer["summary_path"]
    base_summary=json.loads(base_summary_path.read_text(encoding="utf-8"))
    base_bytes=base_manifest.read_bytes();base_sha=sha(base_bytes)
    checks=[]
    def check(name,ok,detail):
        checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
        if not ok:raise RuntimeError(f"{name}: {detail}")
    check("current_pointer_matches_manifest",pointer.get("manifest_sha256")==base_sha==base_summary["row_level_manifest"]["sha256"],base_sha)
    base_rows=read_csv(base_manifest);base_keys={(r["interval"],r["open_time_ms"]) for r in base_rows}
    check("current_manifest_row_key_integrity",len(base_rows)==base_summary["row_level_manifest"]["rows"] and len(base_keys)==len(base_rows),f"rows={len(base_rows)} keys={len(base_keys)}")
    blockers=read_csv(base_blockers)
    check("eleven_aggregation_blockers_remain",len(blockers)==11 and Counter(r["record_type"] for r in blockers)=={"RESIDUAL_AGGREGATION_BUCKET":11},len(blockers))

    agdir=ROOT/"evidence/source_adjudication"/AGG_RUN
    comp_path=agdir/"CP0107_CP0041_AggregationBucket_Comparison.csv"
    evidence_path=agdir/"CP0107_CP0041_AggregationBucket_RowEvidence.csv"
    agg_summary_path=agdir/"CP0107_CP0041_AggregationBucket_Summary.json"
    agg_summary=json.loads(agg_summary_path.read_text(encoding="utf-8"))
    comp_bytes=comp_path.read_bytes();ev_bytes=evidence_path.read_bytes()
    comp_sha=sha(comp_bytes);ev_sha=sha(ev_bytes);agg_sum_sha=sha(agg_summary_path.read_bytes())
    check("aggregation_summary_status",agg_summary.get("status")=="PASS_AGGREGATION_BUCKET_DAILY_SOURCE_REVIEW",agg_summary.get("status"))
    check("aggregation_summary_checks",agg_summary.get("checks_passed")==agg_summary.get("checks_total")==12,
          f"{agg_summary.get('checks_passed')}/{agg_summary.get('checks_total')}")
    check("aggregation_source_file_hashes",
          comp_sha==agg_summary["outputs"][comp_path.name]["sha256"] and ev_sha==agg_summary["outputs"][evidence_path.name]["sha256"],
          f"comparison={comp_sha}; row_evidence={ev_sha}")
    buckets=read_csv(comp_path);evidence=read_csv(evidence_path)
    check("exactly_11_buckets_and_78_evidence_rows",len(buckets)==11 and len(evidence)==78 and agg_summary.get("row_evidence_count")==78,
          f"buckets={len(buckets)} evidence={len(evidence)}")
    check("all_evidence_rows_found_and_no_source_duplicates",
          all(str(r["row_found"]).lower()=="true" and str(r["duplicate_exact_key"]).lower()=="false" for r in evidence),
          "all 78 source rows exist and duplicate_exact_key=False")
    check("all_buckets_open_no_authority",
          all(r["current_disposition"]=="UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT" and r["source_authority"]=="NONE" and r["canonical_source_selected"].lower()=="false" and r["cases_closed"]=="0" for r in buckets),
          "11 buckets remain open; no source authority")

    # Build exact key -> all bucket roles and source-side row relations.
    evidence_by_key={}
    for r in evidence:
        iv=str(r["interval"]).strip();ts=str(r["expected_open_time_ms"]).strip()
        if not ts.isdigit() or not iv:raise RuntimeError(f"invalid exact key in aggregation evidence: {r}")
        key=(iv,ts)
        evidence_by_key.setdefault(key,[]).append(r)
    check("unique_bucket_exact_keys",len(evidence_by_key)==35,f"unique_keys={len(evidence_by_key)}")
    for key,items in evidence_by_key.items():
        sources={r["source"] for r in items}
        if sources!={"MONTHLY","DAILY"}:raise RuntimeError(f"exact key lacks both monthly/daily evidence: {key} {sources}")
    missing_keys=set(evidence_by_key)-base_keys
    existing_keys=set(evidence_by_key)&base_keys
    check("bucket_key_coverage_partition",len(missing_keys)==16 and len(existing_keys)==19 and len(missing_keys)+len(existing_keys)==35,
          f"missing={len(missing_keys)} existing={len(existing_keys)}")

    by_key={(r["interval"],r["open_time_ms"]):dict(r) for r in base_rows}
    for r in by_key.values():
        for f in EXTRA_FIELDS:r.setdefault(f,"")
    added=0
    for key,items in evidence_by_key.items():
        cases=sorted({x["bucket_case_id"] for x in items})
        roles=sorted({x["source"]+":"+x["role"] for x in items})
        relations=sorted({x["source"]+":"+x["source_row_relation"] for x in items})
        detail={
          "aggregation_bucket_case_ids":";".join(cases),
          "aggregation_bucket_roles":";".join(roles),
          "aggregation_source_row_relations":";".join(relations),
          "aggregation_row_evidence_sha256":ev_sha,
          "aggregation_bucket_comparison_sha256":comp_sha,
          "aggregation_bucket_summary_sha256":agg_sum_sha,
          "aggregation_bucket_disposition":"OPEN_REVIEW_REQUIRED; exact row quarantined; cross-interval relation remains unresolved",
        }
        if key in by_key:
            for f,v in detail.items():
                old=by_key[key].get(f,"")
                if old and old!=v:raise RuntimeError(f"conflicting aggregation provenance at {key}/{f}")
                by_key[key][f]=v
        else:
            iv,ts=key
            case_id=f"AGGBUCKET-{iv}-{ts}"
            row={
              "case_id":case_id,"case_class":"AGGREGATION_BUCKET_ROW_QUARANTINE","interval":iv,"open_time_ms":ts,
              "disposition":"OPEN_REVIEW_REQUIRED","canonical_source":"NONE","case_closed":"false",
              "source_record_type":"AGGREGATION_BUCKET_ROW_EVIDENCE",
              "source_disposition_original":"UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT",
              "source_index_sha256":"a3a961a3e3ff0783c1cfed6efafddef313f7c455148a9a5174e95feef80062bf",
              "source_index_expanded_sha256":"072009025272fcba372b820a2ecbd1c65f5938138c5206f19e7cfcdf83ecc39b",
              "source_worklist_sha256":WORKLIST_SHA,"cp0040_rulebook_sha256":RULEBOOK_SHA,
            }
            row.update({f:"" for f in EXTRA_FIELDS});row.update(detail)
            by_key[key]=row;added+=1
    final_rows=list(by_key.values());final_rows.sort(key=lambda r:(r["interval"],int(r["open_time_ms"])))
    final_keys={(r["interval"],r["open_time_ms"]) for r in final_rows}
    check("final_manifest_unique",len(final_rows)==len(final_keys)==len(base_rows)+added,
          f"rows={len(final_rows)} unique={len(final_keys)} added={added}")
    check("all_35_bucket_keys_in_manifest",set(evidence_by_key).issubset(final_keys),len(evidence_by_key))
    check("source_authority_unchanged",all(r["canonical_source"]=="NONE" and str(r["case_closed"]).lower()=="false" for r in final_rows),"all cases open/no canonical source")

    manifest_path=out/"CP0040_ExactKey_Quarantine_Manifest.csv";blockers_path=out/"CP0040_NonRow_Blockers.csv"
    fields=list(base_rows[0].keys())+[f for f in EXTRA_FIELDS if f not in base_rows[0]]
    write_csv(manifest_path,final_rows,fields)
    blocker_fields=list(blockers[0].keys());write_csv(blockers_path,blockers,blocker_fields)
    manifest_sha=sha(manifest_path.read_bytes());blockers_sha=sha(blockers_path.read_bytes())
    classes=Counter(r["case_class"] for r in final_rows)
    summary={
      "checkpoint":"CP0040_EXACT_KEY_QUARANTINE_MANIFEST_AGGREGATION_EXTENSION",
      "status":"PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN",
      "checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),"checks":checks,
      "inputs":{
        "base_manifest_run_id":pointer["run_id"],"base_manifest_sha256":base_sha,"base_manifest_rows":len(base_rows),
        "aggregation_comparison_sha256":comp_sha,"aggregation_row_evidence_sha256":ev_sha,"aggregation_summary_sha256":agg_sum_sha,
        "source_package_sha256":"23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc",
        "cp0040_rulebook_sha256":RULEBOOK_SHA,"original_worklist_sha256":WORKLIST_SHA
      },
      "row_level_manifest":{
        "rows":len(final_rows),"unique_exact_keys":len(final_keys),"sha256":manifest_sha,"case_class_counts":dict(classes),
        "aggregation_bucket_unique_keys_covered":len(evidence_by_key),"new_unique_keys_added_from_aggregation":added,
        "existing_keys_enriched_with_aggregation_evidence":len(existing_keys),"aggregation_bucket_count":len(buckets),
        "all_bucket_parent_and_child_keys_in_manifest":True,"canonical_source":"NONE","all_cases_open":True
      },
      "nonrow_blockers":{
        "rows":len(blockers),"sha256":blockers_sha,"record_type_counts":dict(Counter(r["record_type"] for r in blockers)),
        "candidate_eligibility_blocked":True,
        "reason":"11 cross-interval aggregation relationships remain unresolved. All exact row keys evidenced by those buckets are now quarantined, but the acceptance gate remains closed pending explicit rulebook-aligned disposition."
      },
      "aggregation_bucket_quarantine":{
        "buckets":11,"row_evidence_records":78,"unique_exact_keys":35,"keys_already_quarantined":len(existing_keys),
        "new_exact_keys_quarantined":added,"daily_child_rollups_match_daily_parents":11,
        "monthly_frozen_mismatch_signature_matches":11,"source_cases_closed":0,"canonical_source_selected":False,
        "interpretation":"All implicated exact rows are quarantined from any future candidate, but the cross-interval root cause is still OPEN_NOT_ESTABLISHED."
      },
      "outputs":{
        manifest_path.name:{"bytes":manifest_path.stat().st_size,"sha256":manifest_sha,"rows":len(final_rows)},
        blockers_path.name:{"bytes":blockers_path.stat().st_size,"sha256":blockers_sha,"rows":len(blockers)}
      },
      "decisions":{
        "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
        "timestamp_shifted_or_rounded":False,"raw_rows_merged_replaced_or_deleted":False,
        "synthetic_candles_created":False,"candidate_built":False,"backtest_rerun":False,"strategy_promoted":False,
        "candidate_eligibility":"BLOCKED_11_CROSS_INTERVAL_AGGREGATION_CASES_REMAIN"
      }
    }
    summary_path=out/"CP0040_ExactKey_Quarantine_Manifest_Summary.json"
    summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    report_path=out/"CP0040_ExactKey_Quarantine_Manifest_Report_HI.md"
    report=(
      "# CP-0040 Exact-Key Quarantine Manifest: Aggregation Extension\n\n"
      f"**{summary['status']}** — {summary['checks_passed']}/{summary['checks_total']} checks PASS.\n\n"
      f"- Prior manifest: {len(base_rows)} rows; aggregation evidence contains 78 source-row records across 35 unique exact keys.\n"
      f"- Existing keys enriched: {len(existing_keys)}; new unique keys added: {added}; final manifest: {len(final_rows)} rows / {len(final_keys)} unique keys.\n"
      f"- Manifest SHA-256: {manifest_sha}; blocker ledger SHA-256: {blockers_sha}.\n"
      "- All 11 aggregation buckets have their parent/child exact row keys represented in the quarantine manifest. No timestamps were inferred; keys came from the committed row-level evidence file.\n"
      "- The 11 aggregation relationships remain open: daily child rollups match daily parents, while the monthly frozen mismatch signature persists. This is not proof of canonical-source authority.\n"
      "- Candidate eligibility remains BLOCKED until a rulebook-aligned disposition of these 11 relationships is recorded. No candidate build/backtest; no source cases closed.\n"
    )
    report_path.write_text(report,encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":raise SystemExit(main())
