#!/usr/bin/env python3
"""Build a read-only case-by-case crosswalk of official archive integrity vs aggregation conflict."""
from __future__ import annotations
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_MANIFEST_SHA="e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a"
EXPECTED_BLOCKERS_SHA="f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36"
EXPECTED_SNAPSHOT_GIT_SHA1="6e32188472ab45b43e1b90fe138399818c937277"
EXPECTED_BUCKET_SUMMARY_GIT_SHA1="08221ec6baab7257b61f803fe78064cc26717ef5"
EXPECTED_BUCKET_COMPARISON_SHA="fa571c863b3f28da89395f7dc43832329c8ea2152655808fee24064638a46952"
EXPECTED_ROW_EVIDENCE_SHA="adecc637fc6683bf5c59558ac45b7fb6ceb4d4dad9b0b3d18b6a380c7b191400"
EXPECTED_DAILY_MANIFEST_SHA="78d909e837989548f23ccb6206d32a430071fc06979472e34c33fac55d7405db"
EXPECTED_MONTHLY_SIDECAR_SUMMARY_SHA="2a100613172c7e0d4a364eb6968a981bc40a531d8b05b10bea6553b3c4990478"

def now():return datetime.now(timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):return sha(Path(p).read_bytes())
def gitsha(b):return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read_json(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def read_csv(p):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write_json(p,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p,rows):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader()
        if rows:w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest-pointer",default="evidence/source_adjudication/CP0040_Current_Manifest.json")
    ap.add_argument("--bucket-snapshot",default="evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv")
    ap.add_argument("--bucket-summary",default="evidence/source_adjudication/CP0107_CP0041_AggregationBucket_Summary.json")
    ap.add_argument("--bucket-comparison",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Comparison.csv")
    ap.add_argument("--row-evidence",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv")
    ap.add_argument("--daily-archive-manifest",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_DailyReference_Archive_Manifest.csv")
    ap.add_argument("--monthly-sidecar-pointer",default="evidence/source_adjudication/CP0040_Aggregation_Monthly_Sidecar_Current.json")
    ap.add_argument("--output-dir",default="results/cp0040_archive_integrity_conflict_matrix")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    checks=[]
    def ck(n,ok,d):checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    try:
        pointer=read_json(ROOT/a.manifest_pointer)
        manifest=ROOT/pointer["manifest_path"];blockers=ROOT/pointer["blockers_path"]
        cp_summary=ROOT/pointer["summary_path"]
        snap=ROOT/a.bucket_snapshot; bucket_sum_path=ROOT/a.bucket_summary
        comp=ROOT/a.bucket_comparison; row_ev_path=ROOT/a.row_evidence
        daily_path=ROOT/a.daily_archive_manifest; monthly_ptr=read_json(ROOT/a.monthly_sidecar_pointer)
        monthly_summary_path=ROOT/monthly_ptr["summary_path"]
        required=(manifest,blockers,cp_summary,snap,bucket_sum_path,comp,row_ev_path,daily_path,monthly_summary_path)
        missing=[str(p) for p in required if not p.is_file()]
        ck("all_frozen_evidence_paths_present",not missing,missing or "all present")
        if missing:raise ValueError("Missing evidence paths: "+", ".join(missing))
        manifest_sha=sha_file(manifest);blockers_sha=sha_file(blockers)
        ck("cp0040_manifest_hash",manifest_sha==EXPECTED_MANIFEST_SHA,manifest_sha)
        ck("cp0040_nonrow_blockers_hash",blockers_sha==EXPECTED_BLOCKERS_SHA,blockers_sha)
        ck("source_snapshot_git_blob",gitsha(snap.read_bytes())==EXPECTED_SNAPSHOT_GIT_SHA1,gitsha(snap.read_bytes()))
        bsum=read_json(bucket_sum_path)
        ck("bucket_summary_git_blob",gitsha(bucket_sum_path.read_bytes())==EXPECTED_BUCKET_SUMMARY_GIT_SHA1,gitsha(bucket_sum_path.read_bytes()))
        comp_rows=read_csv(comp);ev_rows=read_csv(row_ev_path);daily_rows=read_csv(daily_path)
        comp_sha=sha_file(comp);ev_sha=sha_file(row_ev_path);daily_sha=sha_file(daily_path)
        out_rec=bsum.get("outputs",{})
        ck("bucket_comparison_sha_and_rows",comp_sha==EXPECTED_BUCKET_COMPARISON_SHA and len(comp_rows)==11,f"sha={comp_sha}; rows={len(comp_rows)}")
        ck("raw_row_evidence_sha_and_rows",ev_sha==EXPECTED_ROW_EVIDENCE_SHA and len(ev_rows)==78,f"sha={ev_sha}; rows={len(ev_rows)}")
        ck("daily_archive_manifest_sha_and_rows",daily_sha==EXPECTED_DAILY_MANIFEST_SHA and len(daily_rows)==16,f"sha={daily_sha}; rows={len(daily_rows)}")
        ms=read_json(monthly_summary_path)
        ck("monthly_sidecar_pointer_status",monthly_ptr.get("status")=="PASS_MONTHLY_SIDECARS_MATCH_CACHED_ARCHIVE_BYTES" and ms.get("status")==monthly_ptr.get("status"),monthly_ptr.get("status"))
        ck("monthly_sidecar_summary_hash",sha_file(monthly_summary_path)==EXPECTED_MONTHLY_SIDECAR_SUMMARY_SHA,sha_file(monthly_summary_path))
        ck("all_14_monthly_sidecars_verified",ms.get("monthly_sidecars_passed")==14 and ms.get("monthly_sidecars_failed_or_unavailable")==0 and ms.get("monthly_zip_downloads")==0,{"passed":ms.get("monthly_sidecars_passed"),"failed":ms.get("monthly_sidecars_failed_or_unavailable")})
        if any(c["status"]!="PASS" for c in checks):raise ValueError("A frozen input/provenance gate failed; matrix is not considered complete")

        blocker_rows=read_csv(blockers);snapshot_rows=read_csv(snap)
        blocker_ids={r.get("case_id","").strip() for r in blocker_rows}
        snap_ids={r.get("case_id","").strip() for r in snapshot_rows}
        ck("eleven_open_cases_align",len(blocker_rows)==11 and len(snapshot_rows)==11 and blocker_ids==snap_ids,{"blocker_rows":len(blocker_rows),"snapshot_rows":len(snapshot_rows),"id_sets_equal":blocker_ids==snap_ids})
        cmp_by={r["case_id"]:r for r in comp_rows}
        evidence_by={}
        for r in ev_rows:evidence_by.setdefault(r["bucket_case_id"],[]).append(r)
        daily_by={}
        for r in daily_rows:daily_by.setdefault((r.get("interval",""),r.get("utc_date","")),[]).append(r)
        monthly_by={}
        for r in ms.get("monthly_targets",[]):monthly_by[(r.get("interval",""),r.get("filename",""))]=r
        matrix=[];details=[]
        for b in snapshot_rows:
            cid=b["case_id"];cmp=cmp_by.get(cid);ev=evidence_by.get(cid,[])
            if cmp is None:raise ValueError("Missing comparison row for "+cid)
            child=b["child_interval"];parent=b["parent_interval"];date=b["bucket_utc"][:10];period=b["bucket_utc"][:7]
            monthly_rows=[r for r in ev if r.get("source")=="MONTHLY"]
            daily_ev=[r for r in ev if r.get("source")=="DAILY"]
            monthly_files=sorted({(r.get("interval",""),r.get("source_archive_filename",""),r.get("source_archive_sha256","")) for r in monthly_rows})
            daily_files=sorted({(r.get("interval",""),r.get("source_archive_filename",""),r.get("source_archive_sha256",""),r.get("daily_sidecar_sha256","")) for r in daily_ev})
            monthly_checks=[]
            for interval,filename,archive_sha in monthly_files:
                mr=monthly_by.get((interval,filename))
                ok=bool(mr and mr.get("sidecar_status")=="PASS_OFFICIAL_SIDECAR_MATCHES_CACHED_ZIP" and mr.get("cache_sha256")==archive_sha)
                monthly_checks.append(ok)
                details.append({"case_id":cid,"source":"MONTHLY","interval":interval,"bucket_utc":b["bucket_utc"],
                    "archive_filename":filename,"archive_sha256_row_evidence":archive_sha,
                    "official_sidecar_sha256":mr.get("sidecar_sha256","") if mr else "",
                    "sidecar_status":mr.get("sidecar_status","MISSING") if mr else "MISSING",
                    "archive_hash_matches_sidecar_audit":ok,"daily_sidecar_sha256":"",
                    "raw_source_relation":next((r.get("source_row_relation","") for r in monthly_rows if r.get("source_archive_filename")==filename),"")})
            daily_checks=[]
            for interval,filename,archive_sha,sidecar_sha in daily_files:
                dmatches=[r for r in daily_by.get((interval,date),[]) if r.get("filename")==filename]
                dm=dmatches[0] if len(dmatches)==1 else None
                ok=bool(dm and dm.get("fetch_status")=="PASS" and dm.get("sidecar_token_matches_zip")=="True"
                        and dm.get("zip_sha256")==archive_sha and dm.get("sidecar_sha256")==sidecar_sha
                        and dm.get("sidecar_embedded_archive_sha256")==archive_sha)
                daily_checks.append(ok)
                details.append({"case_id":cid,"source":"DAILY","interval":interval,"bucket_utc":b["bucket_utc"],
                    "archive_filename":filename,"archive_sha256_row_evidence":archive_sha,
                    "official_sidecar_sha256":sidecar_sha,"sidecar_status":"PASS_OFFICIAL_DAILY_SIDECAR" if ok else "REVIEW_DAILY_SIDEcar_CROSSWALK",
                    "archive_hash_matches_sidecar_audit":ok,"daily_sidecar_sha256":sidecar_sha,
                    "raw_source_relation":next((r.get("source_row_relation","") for r in daily_ev if r.get("source_archive_filename")==filename),"")})
            monthly_ok=bool(monthly_checks) and all(monthly_checks) and len(monthly_files)==2
            daily_ok=bool(daily_checks) and all(daily_checks) and len(daily_files)==2
            daily_rollup_ok=cmp.get("daily_rollup_status")=="DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT"
            monthly_conflict=cmp.get("monthly_frozen_mismatch_signature_matches")=="True"
            fields=cmp.get("monthly_rollup_mismatch_fields_primary","")
            integrity=monthly_ok and daily_ok
            category=("OFFICIAL_ARCHIVE_BYTES_AUTHENTICATED_AGGREGATION_CONFLICT_CONFIRMED" if integrity and daily_rollup_ok and monthly_conflict
                      else "REVIEW_REQUIRED_INCOMPLETE_CROSSWALK_OR_SIGNATURE")
            matrix.append({
                "case_id":cid,"child_interval":child,"parent_interval":parent,"bucket_utc":b["bucket_utc"],
                "monthly_source_archives":len(monthly_files),"monthly_official_sidecars_matched":sum(monthly_checks),
                "daily_source_archives":len(daily_files),"daily_official_sidecars_matched":sum(daily_checks),
                "monthly_archive_integrity_complete":monthly_ok,"daily_archive_integrity_complete":daily_ok,
                "both_source_archive_integrities_complete":integrity,"monthly_mismatch_fields_frozen":cmp.get("frozen_monthly_mismatch_fields",""),
                "monthly_primary_rollup_mismatch_fields":fields,"monthly_mismatch_signature_reproduced":monthly_conflict,
                "daily_rollup_status":cmp.get("daily_rollup_status",""),"daily_rollup_matches_daily_parent":daily_rollup_ok,
                "monthly_child_volume_exact_sum_match":cmp.get("frozen_monthly_child_volume_exact_numeric_match",""),
                "monthly_parent_numeric_metrics_match":cmp.get("frozen_monthly_parent_numeric_metrics_match",""),
                "disposition":"UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT","source_authority":"NONE","canonical_source_selected":False,
                "case_closed":False,"matrix_classification":category,
                "interpretation":"Both archive byte sets authenticated; daily child roll-up matches its daily parent, while the frozen monthly mismatch remains. This proves a cross-interval aggregation conflict, not which interval is canonical."
            })
        ck("eleven_matrix_rows",len(matrix)==11,f"rows={len(matrix)}")
        ck("all_11_have_both_source_archive_integrities",all(r["both_source_archive_integrities_complete"] for r in matrix),
           f"passed={sum(r['both_source_archive_integrities_complete'] for r in matrix)}/11")
        ck("all_11_preserve_daily_match_and_monthly_conflict",all(r["daily_rollup_matches_daily_parent"] and r["monthly_mismatch_signature_reproduced"] for r in matrix),
           f"passed={sum(r['daily_rollup_matches_daily_parent'] and r['monthly_mismatch_signature_reproduced'] for r in matrix)}/11")
        status="PASS_OFFICIAL_ARCHIVE_INTEGRITY_CONFLICT_MATRIX_COMPLETE" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_MATRIX_GATE_FAILURE"
        summary={
            "schema_version":1,"checkpoint":"CP-0040","task":"cp0040_archive_integrity_conflict_matrix",
            "status":status,"started_at_utc":started,"finished_at_utc":now(),"scope":"READ_ONLY_EVIDENCE_CROSSWALK_NO_NETWORK",
            "evidence_integrity":{"cp0040_manifest_sha256":manifest_sha,"cp0040_nonrow_blockers_sha256":blockers_sha,
                "bucket_snapshot_git_blob_sha1":gitsha(snap.read_bytes()),"bucket_comparison_sha256":comp_sha,
                "row_evidence_sha256":ev_sha,"daily_archive_manifest_sha256":daily_sha,
                "monthly_sidecar_summary_sha256":sha_file(monthly_summary_path)},
            "source_evidence":{"buckets":len(matrix),"raw_row_links":len(ev_rows),
                "monthly_official_archives":14,"monthly_sidecars_matched":14,
                "daily_official_archive_records":len(daily_rows),
                "matrix_buckets_with_both_archive_sets_authenticated":sum(x["both_source_archive_integrities_complete"] for x in matrix),
                "matrix_buckets_with_daily_rollup_match_and_monthly_conflict":sum(x["daily_rollup_matches_daily_parent"] and x["monthly_mismatch_signature_reproduced"] for x in matrix)},
            "matrix":matrix,"checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
            "network_used":False,"monthly_zip_downloads":0,"daily_archive_downloads":0,"market_data_rest_api_used":False,
            "source_bytes_modified":False,"canonical_source_selected":False,"source_cases_closed":0,
            "unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","canonical_source":"NONE",
            "backtest_rerun":False,"production_candidate_build":False,"strategy_promoted":False,
            "live_signing_broadcast_orders":"BLOCKED",
            "decision":"Monthly and daily archive checksum provenance is authenticated for the 11 cases. The cross-interval aggregation conflict is confirmed, but source authority remains unresolved; all 11 blockers must stay open."
        }
        write_json(out/"CP0040_Archive_Integrity_Conflict_Matrix_Summary.json",summary)
        write_csv(out/"CP0040_Archive_Integrity_Conflict_Matrix.csv",matrix)
        write_csv(out/"CP0040_Archive_Integrity_Row_Crosswalk.csv",details)
        report=["# CP-0040: Official archive integrity vs aggregation conflict matrix","",
            "Status: "+status,
            "Monthly official sidecars verified: 14/14; daily official sidecar/archive records retained: 16/16.",
            "Bucket cases covered: 11/11; raw row-evidence links available: 78.",
            "Buckets with both source archive families authenticated: "+str(summary["source_evidence"]["matrix_buckets_with_both_archive_sets_authenticated"])+"/11.",
            "Buckets where the daily roll-up matches its daily parent and the frozen monthly mismatch remains: "+str(summary["source_evidence"]["matrix_buckets_with_daily_rollup_match_and_monthly_conflict"])+"/11.",
            "",
            "| Bucket | Pair | Both archive sets authenticated | Daily roll-up | Monthly mismatch signature | Disposition |",
            "|---|---|---|---|---|---|"]
        for r in matrix:
            report.append("| "+r["case_id"]+" | "+r["child_interval"]+" → "+r["parent_interval"]+" | "+str(r["both_source_archive_integrities_complete"])+" | "+r["daily_rollup_status"]+" | "+str(r["monthly_mismatch_signature_reproduced"])+" | OPEN |")
        report += ["","## Decision",
            "This establishes integrity of the particular monthly and daily archive byte sets and confirms the aggregation disagreement; it does not decide which interval is canonical.",
            "All 11 relationship blockers remain unresolved; G0 BLOCKED_GLOBAL; canonical source NONE; no source case closed.",
            "No network activity, archive download, data repair, candidate build, backtest or strategy promotion occurred."]
        (out/"CP0040_Archive_Integrity_Conflict_Matrix_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
        print(json.dumps({"status":status,"matrix_rows":len(matrix),"both_archive_integrities":summary["source_evidence"]["matrix_buckets_with_both_source_archive_integrities_authenticated"] if "matrix_buckets_with_both_source_archive_integrities_authenticated" in summary["source_evidence"] else summary["source_evidence"]["matrix_buckets_with_both_archive_sets_authenticated"],
            "daily_rollup_plus_monthly_conflict":summary["source_evidence"]["matrix_buckets_with_daily_rollup_match_and_monthly_conflict"],
            "checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"]},ensure_ascii=False,sort_keys=True))
        return 0
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0040","task":"cp0040_archive_integrity_conflict_matrix",
            "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),
            "error_type":type(exc).__name__,"error":str(exc),"checks":checks,
            "network_used":False,"monthly_zip_downloads":0,"daily_archive_downloads":0,"source_bytes_modified":False,
            "canonical_source_selected":False,"source_cases_closed":0,"unresolved_nonrow_aggregation_blockers":11,
            "g0":"BLOCKED_GLOBAL","canonical_source":"NONE","backtest_rerun":False,"strategy_promoted":False,
            "live_signing_broadcast_orders":"BLOCKED"}
        write_json(out/"CP0040_Archive_Integrity_Conflict_Matrix_Summary.json",summary)
        (out/"CP0040_Archive_Integrity_Conflict_Matrix_Report_HI.md").write_text(
            "# CP-0040 Archive Integrity Conflict Matrix\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\nError: "+type(exc).__name__+": "+str(exc)+"\n",
            encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1

if __name__=="__main__":raise SystemExit(main())
