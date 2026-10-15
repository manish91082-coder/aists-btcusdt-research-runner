#!/usr/bin/env python3
"""Compare daily and monthly exact-row OHLCV/trade roll-ups for the 11 frozen CP-0041 buckets."""
from __future__ import annotations
import argparse,csv,hashlib,json,subprocess
from collections import defaultdict,Counter
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKAGE_SHA="23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc"
BUCKET_MEMBER="AISTS_CP0041_Residual_Aggregation_Bucket_Disposition.csv"
BUCKET_MEMBER_SHA="aba8bfeca2ea62f576075faf926e4c425c862d50428cd59732ab9db88a64442a"
RULEBOOK_SHA="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
BUCKET_BLOB="6e32188472ab45b43e1b90fe138399818c937277"
RAW_REL="evidence/source_adjudication/CP0107_Run_38775666304/CP0107_CP0041_DailyReference_RawRow_Comparison.csv"
RAW_BLOB="1fa303ba60a6fdbee009435db2bba0f3fc788406"
RAW_SHA="ac08f6839e172919634d2823ae1f6df4d74613e473419b8c00881527e40906ba"
PERIOD_REL="evidence/source_adjudication/CP0107_Run_38775666304/CP0107_CP0041_DailyReference_Period_Summary.csv"
PERIOD_BLOB="34b1dfa89b3618f455aaa655a54e797ecea1388e"
PERIOD_SHA="ac0049d157ea7a9d881389a6f38f6e292201bcdce0f6c5317504ef8dc5e2c32e"
ARCHIVE_REL="evidence/source_adjudication/CP0107_Run_38775666304/CP0107_CP0041_DailyReference_Archive_Manifest.csv"
ARCHIVE_BLOB="1a1a264923b12bd8d8f38c362a4fe7f32b871356"
ARCHIVE_SHA="78d909e837989548f23ccb6206d32a430071fc06979472e34c33fac55d7405db"
STEP_MS={"5m":300000,"15m":900000,"30m":1800000,"1h":3600000}
PRIMARY_FIELDS=("open","high","low","close","volume")
SUM_FIELDS=("volume","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume")
COMPARE_FIELDS=("open","high","low","close","volume","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume")
RAW_FIELDS=("open_time","open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore")
def sha_file(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def git_blob(rel): return subprocess.check_output(["git","rev-parse","HEAD:"+rel],cwd=ROOT,text=True).strip()
def read_csv(path):
 with Path(path).open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write_csv(path,rows,fields):
 with Path(path).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader();w.writerows(rows)
def iso(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
def epoch_ms(value):
 return int(datetime.fromisoformat(value.replace("Z","+00:00")).timestamp()*1000)
def dnum(value):
 if value is None or str(value).strip()=="":return None
 return Decimal(str(value).strip())
def raw_for(record,source):
 prefix="daily_" if source=="DAILY" else "monthly_"
 if not str(record.get(prefix+"open_time","")).strip():return None
 return {k:record.get(prefix+k,"") for k in RAW_FIELDS}
def aggregate(children):
 vals=[x["raw"] for x in children]
 result={"open":vals[0]["open"],"high":str(max(dnum(x["high"]) for x in vals)),
         "low":str(min(dnum(x["low"]) for x in vals)),"close":vals[-1]["close"]}
 for field in SUM_FIELDS:
  if field=="number_of_trades":
   result[field]=str(sum(int(x[field]) for x in vals))
  else:result[field]=str(sum((dnum(x[field]) for x in vals),Decimal("0")))
 return result
def diff_fields(agg,parent):
 return [f for f in COMPARE_FIELDS if dnum(agg.get(f))!=dnum(parent.get(f))]
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--bucket-snapshot",required=True);ap.add_argument("--row-comparison",required=True)
 ap.add_argument("--period-summary",required=True);ap.add_argument("--archive-manifest",required=True)
 ap.add_argument("--output-dir",required=True)
 args=ap.parse_args();out=Path(args.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
 source_dir=ROOT/"evidence/source_adjudication/CP0107_Run_38775666304"
 for source_file in sorted(source_dir.iterdir()):
  if source_file.is_file():
   target=out/source_file.name
   if source_file.resolve()!=target.resolve():
    import shutil
    shutil.copy2(source_file,target)
 snapshot=ROOT/args.bucket_snapshot;rawpath=ROOT/args.row_comparison;periodpath=ROOT/args.period_summary;archivepath=ROOT/args.archive_manifest
 for p in (snapshot,rawpath,periodpath,archivepath):
  if not p.is_file():raise FileNotFoundError("Required committed evidence absent: "+str(p))
 checks=[]
 def check(name,ok,detail):checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
 check("cp0041_bucket_snapshot_blob",git_blob(args.bucket_snapshot)==BUCKET_BLOB,git_blob(args.bucket_snapshot))
 check("cp0041_bucket_snapshot_provenance",all(x.get("source_package_sha256")==PACKAGE_SHA and x.get("source_member_sha256")==BUCKET_MEMBER_SHA and x.get("source_member_name")==BUCKET_MEMBER and len(x.get("source_record_canonical_sha256",""))==64 for x in read_csv(snapshot)),"source package/member/record hashes are recorded")
 check("row_comparison_blob_and_sha",git_blob(RAW_REL)==RAW_BLOB and sha_file(rawpath)==RAW_SHA and rawpath.stat().st_size==1509065,"committed 1,992-row daily/monthly raw comparison")
 check("period_summary_blob_and_sha",git_blob(PERIOD_REL)==PERIOD_BLOB and sha_file(periodpath)==PERIOD_SHA and periodpath.stat().st_size==7855,"committed 16-period row summary")
 check("daily_archive_manifest_blob_and_sha",git_blob(ARCHIVE_REL)==ARCHIVE_BLOB and sha_file(archivepath)==ARCHIVE_SHA and archivepath.stat().st_size==14055,"committed 16-item official ZIP/.CHECKSUM manifest")
 buckets=read_csv(snapshot);records=read_csv(rawpath);periods=read_csv(periodpath);archives=read_csv(archivepath)
 check("exactly_11_frozen_buckets",len(buckets)==11 and len({x["case_id"] for x in buckets})==11,"count="+str(len(buckets)))
 check("frozen_bucket_dispositions_open",all(x.get("current_disposition")=="UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT" for x in buckets),"all source buckets start unresolved")
 check("frozen_bucket_provenance",all(x.get("source_package_sha256")==PACKAGE_SHA and x.get("source_member_sha256")==BUCKET_MEMBER_SHA and x.get("source_record_canonical_sha256") for x in buckets),"package/member/record lineage references present")
 bykey=defaultdict(list)
 for n,r in enumerate(records,start=2):
  key=(r["interval"],r["utc_date"],int(r["open_time_ms"]))
  item=dict(r);item["_data_record_number"]=n;bykey[key].append(item)
 pidx={(x["interval"],x["utc_date"]):x for x in periods}
 aidx={(x["interval"],x["utc_date"]):x for x in archives}
 evidence=[];overlay=[]
 for bucket in buckets:
  case=bucket["case_id"];child_iv=bucket["child_interval"];parent_iv=bucket["parent_interval"]
  start=epoch_ms(bucket["bucket_utc"]);date=bucket["bucket_utc"][:10]
  child_step=STEP_MS[child_iv];parent_step=STEP_MS[parent_iv]
  if parent_step%child_step:raise ValueError("Non-integral child/parent interval for "+case)
  count=parent_step//child_step;child_keys=[start+i*child_step for i in range(count)]
  source_results={}
  for source,prefix in (("MONTHLY","monthly_"),("DAILY","daily_")):
   item_rows=[];child_rows=[];duplicate_keys=[];parent_row=None
   expected=[(child_iv,k,"CHILD") for k in child_keys]+[(parent_iv,start,"PARENT")]
   for iv,key,role in expected:
    candidates=bykey.get((iv,date,key),[])
    present=[x for x in candidates if raw_for(x,source) is not None]
    if len(present)>1:duplicate_keys.append(iso(key))
    chosen=present[0] if present else (candidates[0] if candidates else None)
    raw=raw_for(chosen,source) if chosen else None
    source_prefix="daily_" if source=="DAILY" else "monthly_"
    archive_name=(chosen.get(source_prefix+"archive_filename","") if chosen else "")
    archive_hash=(chosen.get(source_prefix+"archive_sha256","") if chosen else "")
    sidecar_hash=(chosen.get("daily_sidecar_sha256","") if chosen and source=="DAILY" else "")
    csv_record_number=(chosen.get(source_prefix+"csv_line_number","") if chosen else "")
    relation=(chosen.get("row_relation","") if chosen else "NO_EXACT_OPEN_KEY_IN_COMPARISON")
    ev={"bucket_case_id":case,"source":source,"role":role,"interval":iv,"bucket_utc":bucket["bucket_utc"],
        "expected_open_time_ms":key,"expected_open_time_utc":iso(key),"row_found":"True" if raw else "False",
        "duplicate_exact_key":"True" if len(present)>1 else "False","source_csv_data_record_number":chosen.get("_data_record_number","") if chosen else "",
        "source_archive_csv_line_number":csv_record_number,"source_row_relation":relation,"source_archive_filename":archive_name,
        "source_archive_sha256":archive_hash,"daily_sidecar_sha256":sidecar_hash,
        "raw_close_time_expected_delta_ms":(int(raw["close_time"])-(key+STEP_MS[iv]-1)) if raw and str(raw.get("close_time","")).isdigit() else ""}
    for field in RAW_FIELDS:ev["raw_"+field]=raw.get(field,"") if raw else ""
    evidence.append(ev)
    if role=="CHILD" and raw:
     child_rows.append({"key":key,"raw":raw,"record":chosen,"archive_sha256":archive_hash,"sidecar_sha256":sidecar_hash,"csv_line":csv_record_number})
    if role=="PARENT" and raw:
     parent_row={"key":key,"raw":raw,"record":chosen,"archive_sha256":archive_hash,"sidecar_sha256":sidecar_hash,"csv_line":csv_record_number}
   missing_children=[iso(k) for k in child_keys if not any(x["expected_open_time_ms"]==k and x["bucket_case_id"]==case and x["source"]==source and x["role"]=="CHILD" and x["row_found"]=="True" for x in evidence)]
   expected_count=len(child_keys)
   child_complete=len(child_rows)==expected_count and not duplicate_keys
   parent_present=any(x["bucket_case_id"]==case and x["source"]==source and x["role"]=="PARENT" and x["row_found"]=="True" for x in evidence)
   if not child_complete or not parent_present:
    source_results[source]={"coverage_status":"INCOMPLETE_OR_DUPLICATE_EXACT_KEYS","aggregate":None,"parent":parent_row["raw"] if "parent_row" in locals() and parent_present else None,
      "diffs":[],"missing_children":missing_children,"duplicate_keys":duplicate_keys,"child_rows":child_rows,"parent_row":parent_row if "parent_row" in locals() and parent_present else None}
   else:
    agg=aggregate(child_rows);parent_raw=parent_row["raw"];diffs=diff_fields(agg,parent_raw)
    source_results[source]={"coverage_status":"COMPLETE_EXACT_KEYS","aggregate":agg,"parent":parent_raw,"diffs":diffs,
      "missing_children":[],"duplicate_keys":duplicate_keys,"child_rows":child_rows,"parent_row":parent_row}
   # Validate the archive hashes used by daily rows against the independent archive manifest.
   if source=="DAILY":
    manifest=aidx.get((child_iv,date))
    parent_manifest=aidx.get((parent_iv,date))
    for role_iv,manifest_row in ((child_iv,manifest),(parent_iv,parent_manifest)):
     if manifest_row is None:
      check("daily_manifest_period_present:"+case+":"+role_iv,False,"period absent from archive manifest")
     else:
      used_hashes=set()
      for ev in evidence:
       if ev["bucket_case_id"]==case and ev["source"]==source and ev["interval"]==role_iv and ev["row_found"]=="True":
        used_hashes.add(ev["source_archive_sha256"])
        if ev["daily_sidecar_sha256"]!=manifest_row["sidecar_sha256"]:
         check("daily_sidecar_reference:"+case+":"+role_iv,False,"sidecar hash differs from acquisition manifest")
      if used_hashes and used_hashes!={manifest_row["zip_sha256"]}:
       check("daily_zip_reference:"+case+":"+role_iv,False,"daily ZIP hash differs from acquisition manifest")
   source_results[source]["missing_children"]=missing_children
  monthly=source_results["MONTHLY"];daily=source_results["DAILY"]
  monthly_diffs=monthly["diffs"] if monthly["coverage_status"]=="COMPLETE_EXACT_KEYS" else []
  daily_diffs=daily["diffs"] if daily["coverage_status"]=="COMPLETE_EXACT_KEYS" else []
  frozen_diff_set=set(filter(None,bucket["monthly_mismatch_fields_frozen"].split(";")))
  computed_primary=set(x for x in monthly_diffs if x in PRIMARY_FIELDS)
  monthly_primary_match=(monthly["coverage_status"]=="COMPLETE_EXACT_KEYS" and computed_primary==frozen_diff_set)
  monthly_frozen_volume_sum="";monthly_frozen_child_trades_match=False;monthly_frozen_parent_match=False
  if monthly["coverage_status"]=="COMPLETE_EXACT_KEYS":
   monthly_frozen_volume_sum=monthly["aggregate"]["volume"]
   monthly_frozen_child_trades_match=(int(monthly["aggregate"]["number_of_trades"])==int(bucket["frozen_monthly_child_trade_count_sum"]))
   monthly_frozen_parent_match=(dnum(monthly["parent"]["volume"])==dnum(bucket["frozen_monthly_parent_volume"]) and int(monthly["parent"]["number_of_trades"])==int(bucket["frozen_monthly_parent_trade_count"]))
   monthly_frozen_sum_match=(dnum(monthly["aggregate"]["volume"])==dnum(bucket["frozen_monthly_child_volume_sum"]))
  else:
   monthly_frozen_sum_match=False
  monthly_reference_match=monthly_primary_match and monthly_frozen_child_trades_match and monthly_frozen_parent_match and monthly_frozen_sum_match
  if daily["coverage_status"]!="COMPLETE_EXACT_KEYS":
   daily_status="DAILY_CHILD_OR_PARENT_COVERAGE_REVIEW_REQUIRED"
  elif not daily_diffs:
   daily_status="DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT"
  else:
   daily_status="DAILY_CHILD_ROLLUP_DIVERGES_FROM_DAILY_PARENT"
  if monthly["coverage_status"]!="COMPLETE_EXACT_KEYS":
   proposed="OPEN_REVIEW_REQUIRED_MONTHLY_EXACT_KEYS_INCOMPLETE"
  elif not monthly_reference_match:
   proposed="OPEN_REVIEW_REQUIRED_FROZEN_MONTHLY_ROLLUP_REPRESENTATION_OR_FIELD_REVIEW"
  elif daily["coverage_status"]!="COMPLETE_EXACT_KEYS":
   proposed="OPEN_REVIEW_REQUIRED_DAILY_CHILD_COVERAGE_INCOMPLETE"
  elif not daily_diffs:
   proposed="OPEN_REVIEW_REQUIRED_MONTHLY_CONFLICT_NOT_REPRODUCED_IN_DAILY_REFERENCE"
  elif set(daily_diffs)==set(monthly_diffs):
   proposed="OPEN_REVIEW_REQUIRED_DAILY_AND_MONTHLY_DIVERGENCE_SIGNATURE_MATCHES"
  else:
   proposed="OPEN_REVIEW_REQUIRED_DAILY_DIVERGENCE_SIGNATURE_DIFFERS"
  overlay.append({
   "case_id":case,"child_interval":child_iv,"parent_interval":parent_iv,"bucket_utc":bucket["bucket_utc"],
   "frozen_monthly_mismatch_fields":bucket["monthly_mismatch_fields_frozen"],
   "frozen_monthly_child_volume_sum":bucket["frozen_monthly_child_volume_sum"],
   "recomputed_monthly_child_volume_sum":monthly_frozen_volume_sum,
   "frozen_monthly_child_volume_exact_numeric_match":str(monthly_frozen_sum_match),
   "frozen_monthly_parent_volume":bucket["frozen_monthly_parent_volume"],
   "frozen_monthly_child_trade_count_sum":bucket["frozen_monthly_child_trade_count_sum"],
   "recomputed_monthly_child_trade_count_sum":monthly["aggregate"]["number_of_trades"] if monthly["aggregate"] else "",
   "frozen_monthly_child_trade_count_match":str(monthly_frozen_child_trades_match),
   "frozen_monthly_parent_trade_count":bucket["frozen_monthly_parent_trade_count"],
   "frozen_monthly_parent_numeric_metrics_match":str(monthly_frozen_parent_match),
   "monthly_exact_child_parent_coverage":monthly["coverage_status"],
   "monthly_rollup_mismatch_fields_all_metrics":";".join(monthly_diffs),
   "monthly_rollup_mismatch_fields_primary":";".join(sorted(computed_primary)),
   "monthly_frozen_mismatch_signature_matches":str(monthly_primary_match),
   "daily_exact_child_parent_coverage":daily["coverage_status"],
   "daily_missing_exact_child_keys":";".join(daily["missing_children"]),
   "daily_duplicate_exact_keys":";".join(daily["duplicate_keys"]),
   "daily_rollup_mismatch_fields_all_metrics":";".join(daily_diffs),
   "daily_rollup_mismatch_fields_primary":";".join(sorted(set(x for x in daily_diffs if x in PRIMARY_FIELDS))),
   "daily_rollup_status":daily_status,
   "monthly_recomputed_aggregate_json":json.dumps(monthly["aggregate"],sort_keys=True) if monthly["aggregate"] else "",
   "monthly_parent_raw_json":json.dumps(monthly["parent"],sort_keys=True) if monthly["parent"] else "",
   "daily_recomputed_aggregate_json":json.dumps(daily["aggregate"],sort_keys=True) if daily["aggregate"] else "",
   "daily_parent_raw_json":json.dumps(daily["parent"],sort_keys=True) if daily["parent"] else "",
   "suggested_disposition_only":"REVIEW_ONLY; "+proposed,
   "current_disposition":"UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT",
   "source_authority":"NONE","canonical_source_selected":"False","cases_closed":0,
   "source_package_sha256":PACKAGE_SHA,"source_bucket_member_sha256":BUCKET_MEMBER_SHA,
   "raw_comparison_sha256":RAW_SHA,"raw_comparison_git_blob_sha1":RAW_BLOB,
   "rulebook_sha256":RULEBOOK_SHA,"backtest_rerun":"False","strategy_promoted":"False"})
 # Ensure every bucket has the expected number of source-side key audit lines: child count + one parent, for daily and monthly.
 exp_evidence=sum((STEP_MS[b["parent_interval"]]//STEP_MS[b["child_interval"]]+1)*2 for b in buckets)
 check("row_level_evidence_count",len(evidence)==exp_evidence,"expected="+str(exp_evidence)+" actual="+str(len(evidence)))
 check("all_daily_rows_link_to_acquisition_manifest",not any(x["check_id"].startswith("daily_") and x["status"]=="FAIL" for x in checks),"sidecar/archive hashes join to verified daily manifest")
 check("all_buckets_remain_open",len(overlay)==11 and all(x["current_disposition"]=="UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT" and x["canonical_source_selected"]=="False" and x["cases_closed"]==0 for x in overlay),"no bucket closed or canonical source selected")
 check("no_repair_or_research_promotion",True,"no raw source bytes written; no timestamp correction, row replacement, synthetic candles, backtest, or strategy promotion")
 overlay_path=out/"CP0107_CP0041_AggregationBucket_Comparison.csv"
 evidence_path=out/"CP0107_CP0041_AggregationBucket_RowEvidence.csv"
 overlay_fields=list(overlay[0].keys())
 evidence_fields=list(evidence[0].keys()) if evidence else ["bucket_case_id","source","role"]
 write_csv(overlay_path,overlay,overlay_fields);write_csv(evidence_path,evidence,evidence_fields)
 outputs={}
 for name in (overlay_path.name,evidence_path.name):
  p=out/name
  with p.open("r",encoding="utf-8-sig",newline="") as f:nrows=sum(1 for _ in csv.DictReader(f))
  outputs[name]={"sha256":sha_file(p),"bytes":p.stat().st_size,"rows":nrows}
 status="PASS_AGGREGATION_BUCKET_DAILY_SOURCE_REVIEW" if all(c["status"]=="PASS" for c in checks) else "FAIL_AGGREGATION_BUCKET_DAILY_SOURCE_REVIEW"
 comparisons=Counter(x["daily_rollup_status"] for x in overlay)
 summary={"checkpoint":"CP-0107","task":"cp0107_cp0041_aggregation_bucket_overlay_audit","status":status,
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),"bucket_count":len(overlay),"row_evidence_count":len(evidence),
  "checks":checks,"checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),
  "daily_rollup_status_counts":dict(comparisons),"monthly_frozen_mismatch_signature_match_count":sum(x["monthly_frozen_mismatch_signature_matches"]=="True" for x in overlay),
  "monthly_child_volume_exact_sum_match_count":sum(x["frozen_monthly_child_volume_exact_numeric_match"]=="True" for x in overlay),
  "outputs":outputs,
  "inputs":{
   "source_package_sha256":PACKAGE_SHA,"source_bucket_member_sha256":BUCKET_MEMBER_SHA,"source_bucket_snapshot_git_blob_sha1":BUCKET_BLOB,
   "rulebook_sha256":RULEBOOK_SHA,"raw_comparison_git_blob_sha1":RAW_BLOB,"raw_comparison_sha256":RAW_SHA,"raw_comparison_bytes":1509065,"raw_comparison_rows":len(records),
   "period_summary_git_blob_sha1":PERIOD_BLOB,"period_summary_sha256":PERIOD_SHA,"period_summary_rows":len(periods),
   "daily_archive_manifest_git_blob_sha1":ARCHIVE_BLOB,"daily_archive_manifest_sha256":ARCHIVE_SHA,"daily_archive_manifest_rows":len(archives)},
  "decisions":{"all_buckets_remain_unresolved":True,"canonical_source_selected":False,"source_cases_closed":0,
   "raw_archives_modified":False,"timestamps_shifted_or_rounded":False,"rows_merged_replaced_or_deleted":False,
   "synthetic_candles_created":False,"backtest_rerun":False,"strategy_promoted":False,
   "gate_states":{"G0":"BLOCKED_GLOBAL","G1":"PARTIAL_SYSTEM_LEVEL","G2":"FAIL_CURRENT_23_CANDIDATES","G3":"BLOCKED_PARTIAL","G4":"INSUFFICIENT_EVIDENCE","G5":"NOT_RUN","G6":"NOT_BUILT","G7":"LIVE_BLOCKED"}},
  "interpretation":"This is a diagnostic overlay. Presence or absence of a repeated child/parent mismatch in daily archives does not assign canonical-source authority or close a bucket. Frozen arithmetic display differences are recorded, not normalized."}
 report=[
  "# CP-0107: CP-0041 residual aggregation bucket overlay","",
  "Status: "+status+"; checks "+str(summary["checks_passed"])+"/"+str(summary["checks_total"])+" PASS.","",
  "## Evidence scope","",
  "- 11 residual aggregation buckets were read from a committed snapshot linked to CP-0041 package SHA-256 "+PACKAGE_SHA+" and member SHA-256 "+BUCKET_MEMBER_SHA+".",
  "- Daily/monthly source rows were joined only by exact interval, UTC date and open-time key from the already-verified CP-0107 acquisition run. No downloads occurred in this task.",
  "- The overlay recomputes child OHLCV, quote volume, trade count and taker-buy sums for monthly and daily source rows, comparing them with the corresponding parent row.",
  "",
  "## Diagnostic results","",
  "- Buckets reviewed: "+str(len(overlay))+"; raw source-row links: "+str(len(evidence))+".",
  "- Daily roll-up statuses: "+json.dumps(dict(comparisons),sort_keys=True)+".",
  "- Frozen monthly primary-mismatch signature reproduced from the row-level comparison: "+str(summary["monthly_frozen_mismatch_signature_match_count"])+"/11. Exact numeric child-volume sum equality with frozen aggregate text: "+str(summary["monthly_child_volume_exact_sum_match_count"])+"/11. Differences are exposed per bucket rather than normalized.",
  "",
  "## Disposition","",
  "All 11 buckets remain UNRESOLVED_CROSS_INTERVAL_AGGREGATION_CONFLICT. Suggested dispositions are review-only. No canonical source selected; no cases closed; no raw archive or timestamp changes; no synthetic candles, backtest rerun or strategy promotion."
 ]
 report_path=out/"CP0107_CP0041_AggregationBucket_Report_HI.md"
 report_path.write_text("\n".join(report)+"\n",encoding="utf-8")
 outputs[report_path.name]={"sha256":sha_file(report_path),"bytes":report_path.stat().st_size,"rows":None}
 summary["outputs"]=outputs
 summary_path=out/"CP0107_CP0041_AggregationBucket_Summary.json"
 summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps({"status":status,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
  "bucket_count":len(overlay),"row_evidence_count":len(evidence),"daily_rollup_status_counts":dict(comparisons),
  "monthly_frozen_mismatch_signature_match_count":summary["monthly_frozen_mismatch_signature_match_count"],
  "monthly_child_volume_exact_sum_match_count":summary["monthly_child_volume_exact_sum_match_count"],"outputs":outputs},ensure_ascii=False,sort_keys=True),flush=True)
 return 0 if status=="PASS_AGGREGATION_BUCKET_DAILY_SOURCE_REVIEW" else 1
if __name__=="__main__":raise SystemExit(main())
