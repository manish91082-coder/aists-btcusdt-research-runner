#!/usr/bin/env python3
"""Recompute committed CP-0107 field-review hashes in GitHub Actions."""
from __future__ import annotations
import argparse,csv,hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIELD_FILES=(
 ("CP0107_Dec2020_Shared_5m_RawField_Comparison.csv",16),
 ("CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv",8),
 ("CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv",24),
)
BASE_FILES=(
 "CP0107_Feb2018_Extraction_Summary.json","CP0107_Feb2018_OffGrid_RawRows.csv",
 "CP0107_Feb2018_DailyCoverage_RawRows.csv","CP0107_Feb2018_SegmentCoverage.csv",
 "CP0107_Feb2018_SourceVerification.csv","CP0107_Feb2018_Extraction_Report_HI.md",
 "CP0107_Feb2018_Checks.csv","CP0107_Dec2020_ChildWindow_Audit_Summary.json",
 "CP0107_Dec2020_5m_ActualRows_Window.csv","CP0107_Dec2020_5m_ChildCoverage.csv",
 "CP0107_Dec2020_ReviewRollup_ChildCoverage.csv","CP0107_Dec2020_5m_SourceVerification.csv",
)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csv_rows(path):
 with Path(path).open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def blob(path):
 return subprocess.check_output(["git","rev-parse","HEAD:"+str(path)],cwd=ROOT,text=True).strip()
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source-dir",required=True);ap.add_argument("--evidence-dir",required=True);ap.add_argument("--output-dir",required=True)
 a=ap.parse_args();src=ROOT/a.source_dir;ev=ROOT/a.evidence_dir;out=ROOT/a.output_dir
 out.mkdir(parents=True,exist_ok=True);checks=[]
 def check(name,ok,detail): checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
 for name in BASE_FILES:
  p=src/name
  if not p.is_file(): raise FileNotFoundError("Previously verified source evidence absent: "+str(p))
  shutil.copy2(p,out/name)
 base=json.loads((out/"CP0107_Feb2018_Extraction_Summary.json").read_text(encoding="utf-8"))
 check("preserved_feb2018_baseline",base.get("status")=="PASS_CACHE_ONLY_EXTRACTION" and base.get("scope",{}).get("off_grid_rows_extracted")==450,base.get("status"))
 child=json.loads((out/"CP0107_Dec2020_ChildWindow_Audit_Summary.json").read_text(encoding="utf-8"))
 check("preserved_dec2020_child_audit",child.get("status")=="PASS_CACHE_ONLY_DEC2020_CHILD_AUDIT" and child.get("review_rollups_checked")==9,child.get("status"))
 outputs={};inputs={}
 for name,nexpected in FIELD_FILES:
  path=ev/name
  if not path.is_file():raise FileNotFoundError("Committed field-review table absent: "+str(path))
  rows=csv_rows(path)
  if len(rows)!=nexpected:raise ValueError(name+" expected "+str(nexpected)+" rows; got "+str(len(rows)))
  shutil.copy2(path,out/name);copied=out/name
  digest=sha(copied)
  if digest!=sha(path) or copied.stat().st_size!=path.stat().st_size:raise ValueError("Copied field-review file mismatch: "+name)
  inputs[name]={"path":str(Path(a.evidence_dir)/name),"git_blob_sha1":blob(str(Path(a.evidence_dir)/name)),"sha256":sha(path),"bytes":path.stat().st_size,"rows":len(rows)}
  outputs[name]={"path":str(Path(a.evidence_dir)/name),"git_blob_sha1":blob(str(Path(a.evidence_dir)/name)),"sha256":digest,"bytes":copied.stat().st_size,"rows":len(rows)}
  check("hash_and_copy_"+name,digest==sha(path),digest)
 pairs=csv_rows(out/FIELD_FILES[0][0]);exact=sum(int(x["raw_field_difference_count"])==0 for x in pairs);divergent=sum(int(x["raw_field_difference_count"])>0 for x in pairs)
 fingerprints=csv_rows(out/FIELD_FILES[1][0]);missing=csv_rows(out/FIELD_FILES[2][0])
 monthly=sum(x["source"]=="MONTHLY" for x in missing);daily=sum(x["source"]=="DAILY" for x in missing)
 check("shared_open_key_pair_counts",len(pairs)==16 and exact==9 and divergent==7,"total=16 exact=9 divergent=7")
 check("close_time_fingerprint_rows",len(fingerprints)==8 and all(x["close_time_raw"]=="1608558440521" for x in fingerprints),"8 rows with exact token")
 check("missing_child_key_counts",len(missing)==24 and monthly==10 and daily==14,"monthly=10 daily=14")
 check("removed_misleading_boundary_label","monthly_close_boundary_expected" not in pairs[0],"column absent")
 current_inputs={}
 input_paths=[
 "evidence/source_adjudication/CP0107_Dec2020_Shared_5m_RawField_Comparison.csv",
 "evidence/source_adjudication/CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv",
 "evidence/source_adjudication/CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv",
 "evidence/source_adjudication/CP0107_Run_38756665405/CP0107_Dec2020_5m_ActualRows_Window.csv",
 "evidence/source_adjudication/CP0107_Run_38756665405/CP0107_Dec2020_5m_ChildCoverage.csv",
 "evidence/source_adjudication/CP0107_Run_38756665405/CP0107_Dec2020_ReviewRollup_ChildCoverage.csv",
 "evidence/source_adjudication/CP0107_Dec2020_RowDisposition.csv",
 "evidence/source_adjudication/CP0107_Dec2020_Rollup_Disposition.csv",
 "evidence/source_adjudication/CP0107_Run_38756665405/CP0107_Dec2020_5m_SourceVerification.csv",
 ]
 for rel in input_paths:
  p=ROOT/rel
  if not p.is_file():raise FileNotFoundError("Evidence input absent: "+rel)
  current_inputs[rel]={"git_blob_sha1":blob(rel),"sha256":sha(p),"bytes":p.stat().st_size,
                       "rows":len(csv_rows(p)) if p.suffix==".csv" else None}
 base_summary=json.loads((ev/"CP0107_Dec2020_FieldReview_Summary.json").read_text(encoding="utf-8"))
 base_summary["classification_status"]=base_summary.get("status","PASS_EVIDENCE_CLASSIFICATION_NOT_ROOT_CAUSE")
 base_summary["status"]="PASS_FIELD_REVIEW_HASH_RECOMPUTED"
 base_summary["generated_at_utc"]=datetime.now(timezone.utc).isoformat()
 base_summary["trusted_runner"]={"run_id":os.environ.get("AISTS_RUN_ID",""),"commit_sha":os.environ.get("AISTS_COMMIT_SHA",""),
  "method":"Python hashlib.sha256 over exact committed bytes in GitHub Actions checkout"}
 base_summary["outputs"]=outputs;base_summary["inputs_verified_now"]=current_inputs
 base_summary["integrity_note"]="Derived CSV SHA-256 values recomputed by Python hashlib inside GitHub Actions. Git blob SHA-1, byte count, row count and SHA-256 are recorded together."
 base_summary["checks"]=checks;base_summary["checks_passed"]=sum(x["status"]=="PASS" for x in checks);base_summary["checks_total"]=len(checks)
 base_summary["constraints"]={"external_network_used":False,"market_data_rest_api_used":False,"raw_archives_modified":False,
  "timestamp_shift_or_rounding":False,"synthetic_candles_created":False,"backtest_rerun":False,"strategy_promoted":False,
  "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED"}
 if base_summary["checks_passed"]!=base_summary["checks_total"]:base_summary["status"]="FAIL_FIELD_REVIEW_HASH_RECOMPUTED"
 summary_path=out/"CP0107_Dec2020_FieldReview_Summary.json"
 summary_path.write_text(json.dumps(base_summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 summary_sha=sha(summary_path);summary_bytes=summary_path.stat().st_size
 report=(ev/"CP0107_Dec2020_FieldReview_Report_HI.md").read_text(encoding="utf-8")
 start=report.find("| File | Rows | Bytes | SHA-256 |");end=report.find("\n\n## What remains unproven",start)
 if start<0 or end<0:raise ValueError("Report output table markers absent")
 table=["| File | Rows | Bytes | SHA-256 |","|---|---:|---:|---|"]
 for name,item in outputs.items():table.append("| "+name+" | "+str(item["rows"])+" | "+str(item["bytes"])+" | "+item["sha256"]+" |")
 table.append("| CP0107_Dec2020_FieldReview_Summary.json | 1 | "+str(summary_bytes)+" | "+summary_sha+" |")
 report=report[:start]+"\n".join(table)+report[end:]
 report=report.replace("no Actions job/backtest was run for the comparison outputs","SHA-256 was recomputed and checked in this GitHub Actions run; no archives were downloaded and no backtest was run")
 report=report.replace("This analysis uses committed, hash-identified CSV evidence only.","This analysis uses committed CSV evidence only; derived-table SHA-256 was recomputed inside the trusted GitHub Actions runner.")
 report_path=out/"CP0107_Dec2020_FieldReview_Report_HI.md";report_path.write_text(report,encoding="utf-8")
 all_ok=base_summary["status"]=="PASS_FIELD_REVIEW_HASH_RECOMPUTED" and all(x["status"]=="PASS" for x in checks)
 print(json.dumps({"status":base_summary["status"],"checks_passed":base_summary["checks_passed"],"checks_total":base_summary["checks_total"],
  "outputs":outputs,"summary_sha256":sha(summary_path),"summary_bytes":summary_path.stat().st_size,
  "report_sha256":sha(report_path),"report_bytes":report_path.stat().st_size},ensure_ascii=False,sort_keys=True),flush=True)
 return 0 if all_ok else 1
if __name__=="__main__":raise SystemExit(main())
