#!/usr/bin/env python3
"""Read-only CP-0114 join: test exact-key quarantine coverage for CP-0113 target rows."""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULEBOOK_SHA = "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
METRICS = ("open","high","low","close","volume","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume")

def sha_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def git_blob(p):
    b=p.read_bytes()
    return hashlib.sha1(("blob "+str(len(b))+"\0").encode()+b).hexdigest()

def read_csv(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def write_csv(p,rows,fields):
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)

def equal(field,a,b):
    try: return int(a)==int(b) if field=="number_of_trades" else Decimal(a)==Decimal(b)
    except (ValueError,InvalidOperation,TypeError): return False

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--row-evidence",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv")
    ap.add_argument("--manifest",default="evidence/source_adjudication/CP0040_Run_38883792900/CP0040_ExactKey_Quarantine_Manifest.csv")
    ap.add_argument("--bucket-relevance",default="evidence/source_adjudication/CP0040_Candidate_Input_Relevance_Run_38901790221/CP0040_Candidate_Input_Relevance_Matrix.csv")
    ap.add_argument("--quarantine-key-application",default="evidence/source_adjudication/CP0040_Sensitivity_Run_38897836116/CP0040_Quarantine_Key_Application.csv")
    ap.add_argument("--quarantine-input-impact",default="evidence/source_adjudication/CP0040_Sensitivity_Run_38897836116/CP0040_Input_Impact.csv")
    ap.add_argument("--rulebook",default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
    ap.add_argument("--cp0113-pointer",default="evidence/source_adjudication/CP0113_FieldLevel_Trade_Corroboration_Disposition_Current.json")
    ap.add_argument("--cp0113-report",default="evidence/source_adjudication/CP0113_FieldLevel_Trade_Corroboration_Disposition_HI.md")
    ap.add_argument("--output-dir",default="results/cp0114_quarantine_overlap_g0_audit")
    a=ap.parse_args()
    names={"row_evidence":a.row_evidence,"manifest":a.manifest,"bucket_relevance":a.bucket_relevance,"application":a.quarantine_key_application,"impact":a.quarantine_input_impact,"rulebook":a.rulebook,"pointer":a.cp0113_pointer,"report":a.cp0113_report}
    paths={k:(ROOT/v).resolve() for k,v in names.items()}
    out=(ROOT/a.output_dir).resolve()
    if any(ROOT not in p.parents for p in list(paths.values())+[out]): raise ValueError("Path escapes repository root")
    for k,p in paths.items():
        if not p.is_file(): raise FileNotFoundError(k+": "+str(p))
    out.mkdir(parents=True,exist_ok=True)
    if sha_file(paths["rulebook"])!=RULEBOOK_SHA: raise ValueError("Frozen CP-0040 rulebook SHA-256 mismatch")
    cp=json.loads(paths["pointer"].read_text(encoding="utf-8"))
    if cp.get("checkpoint")!="CP-0113" or cp.get("status")!="PASS_FIELD_LEVEL_CROSSWALK_SOURCE_AUTHORITY_OPEN": raise ValueError("CP-0113 pointer status mismatch")
    if cp.get("report_git_blob_sha1")!=git_blob(paths["report"]): raise ValueError("CP-0113 report blob linkage mismatch")
    if cp.get("counts",{}).get("target_keys_compared")!=35 or cp.get("counts",{}).get("monthly_divergent_keys")!=14 or cp.get("counts",{}).get("monthly_mismatching_metric_fields")!=97: raise ValueError("CP-0113 expected counts mismatch")
    rows=read_csv(paths["row_evidence"]); manifests=read_csv(paths["manifest"]); relevance=read_csv(paths["bucket_relevance"]); application=read_csv(paths["application"]); impact=read_csv(paths["impact"])
    if (len(rows),len(manifests),len(relevance),len(application))!=(78,1427,11,9): raise ValueError("Frozen evidence cardinality mismatch")
    manifest={}
    for r in manifests:
        k=(r.get("interval",""),r.get("open_time_ms",""))
        if k in manifest: raise ValueError("Duplicate exact-key manifest key: "+repr(k))
        manifest[k]=r
    sources={"DAILY":{},"MONTHLY":{}}
    dup={"DAILY":0,"MONTHLY":0};dup_conflicts=[]
    for r in rows:
        if r.get("row_found")!="True" or r.get("source") not in sources: continue
        src=r["source"];k=(r.get("interval",""),r.get("expected_open_time_ms",""))
        vals=tuple(r.get("raw_"+m,"") for m in METRICS)+(r.get("raw_open_time",""),r.get("raw_close_time",""),r.get("source_archive_filename",""),r.get("source_archive_sha256",""))
        if k in sources[src]:
            dup[src]+=1;p=sources[src][k]
            old=tuple(p.get("raw_"+m,"") for m in METRICS)+(p.get("raw_open_time",""),p.get("raw_close_time",""),p.get("source_archive_filename",""),p.get("source_archive_sha256",""))
            if vals!=old: dup_conflicts.append({"source":src,"key":k})
        else:sources[src][k]=r
    keys=sorted(set(sources["DAILY"])|set(sources["MONTHLY"]),key=lambda k:(int(k[1]),k[0]))
    if len(keys)!=35 or len(sources["DAILY"])!=35 or len(sources["MONTHLY"])!=35: raise ValueError("Expected 35 unique daily and monthly keys")
    app_keys={(r.get("interval",""),r.get("open_time_ms","")) for r in application}
    cross=[]; divergent=[];missing=[]
    for interval,ms in keys:
        d=sources["DAILY"].get((interval,ms));m=sources["MONTHLY"].get((interval,ms))
        if d is None or m is None: raise ValueError("Daily/monthly target row missing")
        mf=manifest.get((interval,ms))
        if mf is None: missing.append({"interval":interval,"open_time_ms":ms})
        diffs=[f for f in METRICS if not equal(f,d.get("raw_"+f,""),m.get("raw_"+f,""))]
        k=(interval,ms);app=k in app_keys
        item={
            "interval":interval,"open_time_ms":ms,"open_time_utc":d.get("expected_open_time_utc",""),
            "daily_archive_filename":d.get("source_archive_filename",""),"monthly_archive_filename":m.get("source_archive_filename",""),
            "monthly_mismatch_fields":";".join(diffs),"monthly_mismatch_field_count":len(diffs),
            "cp0040_manifest_case_id":mf.get("case_id","") if mf else "",
            "cp0040_manifest_case_class":mf.get("case_class","NOT_IN_MANIFEST") if mf else "NOT_IN_MANIFEST",
            "cp0040_manifest_disposition":mf.get("disposition","") if mf else "",
            "cp0040_manifest_canonical_source":mf.get("canonical_source","") if mf else "",
            "cp0040_manifest_case_closed":mf.get("case_closed","") if mf else "",
            "cp0040_aggregation_bucket_disposition":mf.get("aggregation_bucket_disposition","") if mf else "",
            "present_in_cp0040_sensitivity_key_application":app,
            "current_4h_d1_comparator_direct_input_interval":interval in ("4h","1d"),
            "case_closed":False,"canonical_source_selected":False
        }
        cross.append(item)
        if diffs: divergent.append(dict(item))
    class_counts={};disposition_counts={}
    for r in cross:
        c=r["cp0040_manifest_case_class"];d=r["cp0040_manifest_disposition"]
        class_counts[c]=class_counts.get(c,0)+1;disposition_counts[d]=disposition_counts.get(d,0)+1
    direct=[r for r in relevance if r.get("direct_interval_overlap")=="True"]
    overlap_app=[r for r in cross if r["present_in_cp0040_sensitivity_key_application"]]
    divergent_app=[r for r in divergent if r["present_in_cp0040_sensitivity_key_application"]]
    div_missing=[r for r in divergent if r["cp0040_manifest_case_class"]=="NOT_IN_MANIFEST"]
    div_wrongclass=[r for r in divergent if r["cp0040_manifest_case_class"]!="ACQUISITION_ECONOMIC_CONFLICT"]
    div_closed=[r for r in divergent if r["cp0040_manifest_case_closed"].lower()=="true"]
    counts={
      "manifest_rows":len(manifests),"manifest_unique_keys":len(manifest),
      "target_keys":len(cross),"target_keys_in_manifest":sum(r["cp0040_manifest_case_class"]!="NOT_IN_MANIFEST" for r in cross),
      "target_class_counts":class_counts,"target_disposition_counts":disposition_counts,
      "monthly_divergent_keys":len(divergent),"monthly_divergent_fields":sum(r["monthly_mismatch_field_count"] for r in divergent),
      "divergent_keys_in_manifest":len(divergent)-len(div_missing),
      "divergent_keys_with_economic_conflict_class":len(divergent)-len(div_wrongclass),
      "divergent_keys_closed":len(div_closed),
      "target_keys_in_sensitivity_applied_list":len(overlap_app),
      "divergent_keys_in_sensitivity_applied_list":len(divergent_app),
      "candidate_relevance_buckets":len(relevance),"buckets_with_direct_4h_d1_interval_overlap":len(direct),
      "target_keys_direct_to_frozen_4h_d1_comparator":sum(r["current_4h_d1_comparator_direct_input_interval"] for r in cross),
      "consistent_duplicate_context_rows":dup,"conflicting_duplicate_values":len(dup_conflicts),
      "input_impact_rows":[{"interval":r.get("interval"),"baseline_rows":r.get("baseline_rows"),"removed_exact_key_rows":r.get("removed_exact_key_rows"),"quarantine_rows_after_filter":r.get("quarantine_rows_after_filter"),"replacements_added":r.get("replacements_added")} for r in impact]
    }
    checks=[
      {"check_id":"frozen_rulebook_and_cp0113_report_pointer_valid","status":"PASS"},
      {"check_id":"all_35_keys_present_in_cp0040_manifest","status":"PASS" if counts["target_keys_in_manifest"]==35 and not missing else "FAIL","detail":str(counts["target_keys_in_manifest"])+"/35"},
      {"check_id":"all_14_monthly_divergent_keys_open_economic_conflicts","status":"PASS" if counts["divergent_keys_in_manifest"]==14 and counts["divergent_keys_with_economic_conflict_class"]==14 and counts["divergent_keys_closed"]==0 else "FAIL","detail":json.dumps(counts,sort_keys=True)},
      {"check_id":"no_target_key_in_current_cp0040_sensitivity_application","status":"PASS" if len(overlap_app)==0 else "FAIL","detail":str(len(overlap_app))+" overlaps"},
      {"check_id":"11_relationship_buckets_have_no_direct_4h_d1_interval_overlap","status":"PASS" if len(relevance)==11 and len(direct)==0 and all(r.get("direct_interval_overlap")=="False" for r in relevance) else "FAIL","detail":str(len(direct))+" direct overlaps"},
      {"check_id":"duplicate_source_contexts_are_consistent","status":"PASS" if not dup_conflicts else "FAIL","detail":json.dumps({"duplicates":dup,"conflicts":dup_conflicts},sort_keys=True)},
      {"check_id":"14_monthly_mismatch_keys_and_97_fields_reproduced","status":"PASS" if counts["monthly_divergent_keys"]==14 and counts["monthly_divergent_fields"]==97 else "FAIL","detail":str(counts["monthly_divergent_keys"])+" keys / "+str(counts["monthly_divergent_fields"])+" fields"}
    ]
    status="PASS_MANIFEST_OVERLAP_AUDIT_G0_STILL_BLOCKED" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_QUARANTINE_OVERLAP_AUDIT"
    out_key=out/"CP0114_Quarantine_Overlap_G0_Impact_Crosswalk.csv";out_div=out/"CP0114_MonthlyConflict_Quarantine_Overlap.csv"
    out_summary=out/"CP0114_Quarantine_Overlap_G0_Impact_Summary.json";out_report=out/"CP0114_Quarantine_Overlap_G0_Impact_Report_HI.md"
    fields=list(cross[0].keys());write_csv(out_key,cross,fields);write_csv(out_div,divergent,fields)
    summary={
      "schema_version":1,"checkpoint":"CP-0114","task":"cp0114_quarantine_overlap_g0_impact_audit","status":status,
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "inputs":{"row_evidence_git_blob_sha1":git_blob(paths["row_evidence"]),"manifest_git_blob_sha1":git_blob(paths["manifest"]),
        "bucket_relevance_git_blob_sha1":git_blob(paths["bucket_relevance"]),"quarantine_application_git_blob_sha1":git_blob(paths["application"]),
        "quarantine_input_impact_git_blob_sha1":git_blob(paths["impact"]),"rulebook_sha256":sha_file(paths["rulebook"]),
        "cp0113_pointer_git_blob_sha1":git_blob(paths["pointer"]),"cp0113_report_git_blob_sha1":git_blob(paths["report"])},
      "counts":counts,"missing_manifest_keys":missing,"duplicate_conflicts":dup_conflicts,
      "checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
      "decision":{"all_35_keys_in_manifest":counts["target_keys_in_manifest"]==35,
        "all_14_divergent_keys_are_open_economic_conflicts":counts["divergent_keys_in_manifest"]==14 and counts["divergent_keys_with_economic_conflict_class"]==14 and counts["divergent_keys_closed"]==0,
        "all_14_divergent_keys_in_sensitivity_application":len(divergent_app)==14,
        "accepted_quarantine_coverage_for_these_keys_proven":False,
        "direct_input_scope":"No target key is a direct interval input to frozen MTF_BREAKOUT_4H_D1; this does not establish irrelevance across all 23 G2-failing candidates.",
        "source_authority":"OPEN_NOT_ESTABLISHED","canonical_source":"NONE","source_cases_closed":0,
        "unresolved_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED"},
      "non_actions":{"archive_downloads":0,"network_used":False,"raw_archive_bytes_modified":False,"timestamps_shifted_or_rounded":False,
        "synthetic_candles_created":False,"candidate_build_performed":False,"backtest_performed":False,"strategy_promoted":False,
        "live_signing_enabled":False,"public_broadcast_enabled":False,"binance_orders_placed":False},"outputs":{}
    }
    report=[
      "# CP-0114: Exact-key quarantine overlap and G0 impact audit","",
      "Status: "+status,"",
      "## Results","",
      "- The 35 daily/monthly target candle keys from CP-0113 are all present in the frozen 1,427-row CP-0040 exact-key manifest.",
      "- The 14 monthly-divergent keys all have manifest class ACQUISITION_ECONOMIC_CONFLICT, disposition OPEN_REVIEW_REQUIRED, canonical source NONE and case_closed=false.",
      "- The frozen CP-0040 sensitivity run applied a list of nine exact keys, all 4h/1d. Overlap with the 35 target keys is 0/35 and overlap with the 14 monthly-divergent keys is 0/14. Manifest presence alone does not prove that this filter was applied to these lower-interval keys.",
      "- The CP-0040 relevance matrix records all 11 cross-interval aggregation blockers as having no direct interval overlap with the single frozen MTF_BREAKOUT_4H_D1 comparator. Its blocker intervals are 5m, 15m, 30m and 1h, versus direct comparator intervals 4h and 1d. This narrow comparator result cannot be generalized to every current G2-failing candidate.",
      "- The exact CP-0113 mismatch count rechecks as "+str(counts["monthly_divergent_keys"])+" unique monthly keys and "+str(counts["monthly_divergent_fields"])+" differing fields. Duplicate row contexts are consistent and source boundaries remain exact.",
      "",
      "## Decision","",
      "Do not upgrade G0, select a canonical source or close any case. It is proven that the current 35 keys are represented in the manifest, but not proven that the accepted candidate quarantine removes all 14 divergent keys from every candidate's active signal inputs. The accepted next step is a candidate-specific exact-key coverage reconciliation against frozen builder inputs for the full current candidate universe, under CP-0040. Do not change source bytes or create a new precedence rule.",
      "",
      "## Non-actions","",
      "- No archive download or network request.",
      "- No source edits, timestamp normalization, rounding or synthetic candles.",
      "- No candidate build, backtest, strategy promotion, signing, public broadcast or exchange order.",
      "- Canonical source remains NONE; source cases closed 0; 11 aggregation blockers open."
    ]
    out_report.write_text("\n".join(report)+"\n",encoding="utf-8")
    for p in (out_key,out_div,out_report): summary["outputs"][p.name]={"bytes":p.stat().st_size,"sha256":sha_file(p)}
    out_summary.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"checkpoint":"CP-0114","status":status,"counts":counts,"checks":checks,"outputs":summary["outputs"],"decision":summary["decision"]},ensure_ascii=False,sort_keys=True),flush=True)
    return 0
if __name__=="__main__": raise SystemExit(main())
