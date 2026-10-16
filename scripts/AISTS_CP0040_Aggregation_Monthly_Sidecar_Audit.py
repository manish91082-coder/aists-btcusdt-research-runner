#!/usr/bin/env python3
"""Verify official monthly .CHECKSUM provenance for the 11 open CP-0040 aggregation buckets.

Only current small checksum-text sidecars are requested. Monthly ZIP bytes are read
from the restored Actions cache and are never downloaded or modified.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_MANIFEST_SHA="e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a"
EXPECTED_BLOCKERS_SHA="f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36"
EXPECTED_SNAPSHOT_BLOB_SHA1="6e32188472ab45b43e1b90fe138399818c937277"
EXPECTED_BUCKET_SUMMARY_SHA="08221ec6baab7257b61f803fe78064cc26717ef5"
EXPECTED_DAILY_MANIFEST_SHA="78d909e837989548f23ccb6206d32a430071fc06979472e34c33fac55d7405db"
ALLOWED_INTERVALS={"5m","15m","30m","1h"}

def now(): return datetime.now(timezone.utc).isoformat()
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def git_blob_sha1(b): return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def read_csv(p):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write_json(p,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p,rows):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader()
        if rows:w.writerows(rows)
def report_text(status,reason=""):
    return ("# CP-0040: 11 open aggregation buckets ka monthly official checksum audit\n\n"
            f"- Status: {status}\n"
            "- Scope: official monthly checksum text only; no ZIP downloads or daily archive acquisition.\n"
            "- All 11 daily roll-up comparisons previously matched daily parents, while the frozen monthly mismatch signature remained in all 11.\n"
            f"- Sidecar result: {reason}\n"
            "- A sidecar PASS authenticates current cached monthly ZIP bytes only. It does not select a canonical source or close a bucket.\n"
            "- G0 remains BLOCKED_GLOBAL; all 11 blockers remain open; canonical source NONE; no backtest or strategy promotion.\n")

def blocked(out,started,reason,checks):
    s={"schema_version":1,"checkpoint":"CP-0040","task":"cp0040_aggregation_monthly_sidecar_audit",
       "status":"BLOCKED_MONTHLY_SIDECAR_INPUT_EVIDENCE_INVALID","started_at_utc":started,"finished_at_utc":now(),
       "blocking_reason":reason,"checks":checks,"checks_passed":sum(x["status"]=="PASS" for x in checks),
       "checks_total":len(checks),"network_used":False,"official_monthly_sidecar_requests":0,
       "monthly_zip_downloads":0,"daily_archive_downloads":0,"market_data_rest_api_used":False,
       "canonical_source_selected":False,"source_cases_closed":0,"unresolved_nonrow_aggregation_blockers":11,
       "g0":"BLOCKED_GLOBAL","canonical_source":"NONE","backtest_rerun":False,"strategy_promoted":False,
       "live_signing_broadcast_orders":"BLOCKED"}
    write_json(out/"CP0040_Aggregation_Monthly_Sidecar_Audit_Summary.json",s)
    (out/"CP0040_Aggregation_Monthly_Sidecar_Audit_Report_HI.md").write_text(report_text(s["status"],reason),encoding="utf-8")
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--monthly-cache",default=".cache/aists/binance-monthly-archives")
    ap.add_argument("--manifest-pointer",default="evidence/source_adjudication/CP0040_Current_Manifest.json")
    ap.add_argument("--bucket-snapshot",default="evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv")
    ap.add_argument("--bucket-summary",default="evidence/source_adjudication/CP0107_CP0041_AggregationBucket_Summary.json")
    ap.add_argument("--bucket-comparison",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Comparison.csv")
    ap.add_argument("--daily-archive-manifest",default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_DailyReference_Archive_Manifest.csv")
    ap.add_argument("--output-dir",default="results/cp0040_aggregation_monthly_sidecar_audit")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    checks=[];records=[]
    def ck(n,ok,d):checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    pointer=read_json(ROOT/a.manifest_pointer)
    manifest=ROOT/pointer.get("manifest_path","");blockers=ROOT/pointer.get("blockers_path","")
    source_summary=ROOT/pointer.get("summary_path","")
    snap=ROOT/a.bucket_snapshot; bucket_sum_path=ROOT/a.bucket_summary
    comp=ROOT/a.bucket_comparison; daily_manifest_path=ROOT/a.daily_archive_manifest
    required=(manifest,blockers,source_summary,snap,bucket_sum_path,comp,daily_manifest_path)
    paths_ok=all(p.is_file() for p in required)
    ck("frozen_evidence_paths_present",paths_ok,[str(p) for p in required])
    if not paths_ok:
        s=blocked(out,started,"At least one frozen evidence file is missing.",checks);print(json.dumps({"status":s["status"],"reason":s["blocking_reason"]}));return 0
    manifest_sha=sha_file(manifest);blocker_sha=sha_file(blockers)
    pointer_ok=pointer.get("manifest_sha256")==EXPECTED_MANIFEST_SHA and pointer.get("status")=="PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN" and pointer.get("candidate_eligibility_blocked") is True
    ck("cp0040_manifest_pointer_and_sha",pointer_ok and manifest_sha==EXPECTED_MANIFEST_SHA,f"pointer={pointer.get('manifest_sha256')} actual={manifest_sha}")
    ck("cp0040_nonrow_blocker_sha",blocker_sha==EXPECTED_BLOCKERS_SHA,f"actual={blocker_sha}")
    bsum=read_json(bucket_sum_path); snap_sha1=git_blob_sha1(snap.read_bytes())
    ck("bucket_snapshot_git_blob_sha1",snap_sha1==EXPECTED_SNAPSHOT_BLOB_SHA1,f"actual={snap_sha1}")
    ck("bucket_summary_sha256",sha_file(bucket_sum_path)==EXPECTED_BUCKET_SUMMARY_SHA,f"actual={sha_file(bucket_sum_path)}")
    compare_rows=read_csv(comp); compare_rec=bsum.get("outputs",{}).get("CP0107_CP0041_AggregationBucket_Comparison.csv",{})
    ck("bucket_comparison_rows_and_hash",len(compare_rows)==11 and sha_file(comp)==compare_rec.get("sha256"),f"rows={len(compare_rows)} sha={sha_file(comp)}")
    daily_rows=read_csv(daily_manifest_path); daily_sha=sha_file(daily_manifest_path)
    ck("daily_reference_manifest_sha_and_rows",daily_sha==EXPECTED_DAILY_MANIFEST_SHA and len(daily_rows)==16,f"sha={daily_sha} rows={len(daily_rows)}")
    if not (pointer_ok and manifest_sha==EXPECTED_MANIFEST_SHA and blocker_sha==EXPECTED_BLOCKERS_SHA and snap_sha1==EXPECTED_SNAPSHOT_BLOB_SHA1 and sha_file(bucket_sum_path)==EXPECTED_BUCKET_SUMMARY_SHA and len(compare_rows)==11 and sha_file(comp)==compare_rec.get("sha256") and daily_sha==EXPECTED_DAILY_MANIFEST_SHA and len(daily_rows)==16):
        s=blocked(out,started,"Frozen evidence hashes/counts did not pass; sidecar network requests were not made.",checks);print(json.dumps({"status":s["status"],"reason":s["blocking_reason"]}));return 0
    blocker_rows=read_csv(blockers);bucket_rows=read_csv(snap);manifest_rows=read_csv(manifest)
    blocker_ids={r.get("case_id","").strip() for r in blocker_rows};bucket_ids={r.get("case_id","").strip() for r in bucket_rows}
    ck("exact_11_open_cases_match_snapshot",len(blocker_rows)==11 and len(bucket_rows)==11 and blocker_ids==bucket_ids,f"blockers={len(blocker_rows)} snapshot={len(bucket_rows)}")
    ck("daily_rollup_previously_matches_for_all_11",all(r.get("daily_rollup_status")=="DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT" for r in compare_rows),"comparison rows="+str(len(compare_rows)))
    ck("all_buckets_remain_open",bsum.get("decisions",{}).get("all_buckets_remain_unresolved") is True and bsum.get("decisions",{}).get("source_cases_closed")==0 and bsum.get("decisions",{}).get("canonical_source_selected") is False,bsum.get("decisions",{}))
    cache= (ROOT/a.monthly_cache).resolve()
    if not cache.is_dir():
        s=blocked(out,started,"Monthly cache is absent; ZIP downloads are not permitted.",checks);print(json.dumps({"status":s["status"],"reason":s["blocking_reason"]}));return 0
    pairs=set()
    for row in bucket_rows:
        period=str(row.get("bucket_utc",""))[:7]
        child=str(row.get("child_interval","")).strip();parent=str(row.get("parent_interval","")).strip()
        if not re.fullmatch(r"\d{4}-\d{2}",period) or child not in ALLOWED_INTERVALS or parent not in ALLOWED_INTERVALS:
            s=blocked(out,started,"Invalid interval/period in frozen bucket snapshot; no sidecar fetch.",checks);print(json.dumps({"status":s["status"],"reason":s["blocking_reason"]}));return 0
        pairs.add((child,period));pairs.add((parent,period))
    expected=sorted(pairs); lookup={}
    for r in daily_rows:
        key=(str(r.get("interval","")).strip(),str(r.get("monthly_filename","")).strip())
        h=str(r.get("monthly_sha256","")).strip().lower()
        if key[1] and h: lookup.setdefault(key,set()).add(h)
    for interval,period in expected:
        filename=f"BTCUSDT-{interval}-{period}.zip";hashes=sorted(lookup.get((interval,filename),set()))
        rec={"interval":interval,"period":period,"filename":filename,"crosswalk_monthly_sha256":hashes[0] if len(hashes)==1 else "",
             "daily_crosswalk_rows":sum(1 for r in daily_rows if r.get("interval")==interval and r.get("monthly_filename")==filename),
             "crosswalk_hash_variants":hashes,"cache_match_count":0}
        found=[p for p in cache.rglob(filename) if p.is_file()];rec["cache_match_count"]=len(found)
        if len(hashes)!=1 or len(found)!=1:
            rec["precheck"]="BLOCKED_CROSSWALK_OR_CACHE_CARDINALITY";records.append(rec);continue
        p=found[0];actual=sha_file(p);rec.update({"cache_path":str(p.relative_to(ROOT)),"cache_bytes":p.stat().st_size,
            "cache_sha256":actual,"cached_zip_matches_crosswalk":actual==hashes[0]})
        try:
            with zipfile.ZipFile(p,"r") as z:
                bad=z.testzip();names=[zinfo.filename for zinfo in z.infolist() if not zinfo.is_dir()]
            rec["zip_crc"]="PASS" if bad is None else "FAIL"
            csvs=[n for n in names if n.lower().endswith(".csv")]
            rec["csv_member"]=csvs[0] if len(csvs)==1 else ""
            rec["precheck"]="PASS" if actual==hashes[0] and bad is None and len(names)==1 and len(csvs)==1 else "BLOCKED_CACHED_ZIP_INTEGRITY"
        except Exception as e:
            rec["zip_crc"]="FAIL";rec["precheck"]="BLOCKED_CACHED_ZIP_INTEGRITY";rec["cache_error"]=str(e)
        records.append(rec)
    ck("exact_14_unique_monthly_archives_in_scope",len(expected)==14,f"unique interval-month pairs={len(expected)}")
    ck("all_14_cached_monthly_zips_hash_and_crc_verified",len(records)==14 and all(r.get("precheck")=="PASS" for r in records),"precheck PASS="+str(sum(r.get("precheck")=="PASS" for r in records))+"/14")
    if not (len(expected)==14 and len(records)==14 and all(r.get("precheck")=="PASS" for r in records)):
        s=blocked(out,started,"Monthly cache bytes did not match all 14 frozen CP-0041 crosswalk hashes; no sidecar requests made.",checks)
        s["monthly_targets"]=records;write_json(out/"CP0040_Aggregation_Monthly_Sidecar_Audit_Summary.json",s)
        write_csv(out/"CP0040_Aggregation_Monthly_Sidecar_Audit_Details.csv",records)
        print(json.dumps({"status":s["status"],"verified_cached_archives":sum(r.get("precheck")=="PASS" for r in records),"expected":14}));return 0
    for rec in records:
        url=f"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/{rec['interval']}/{rec['filename']}.CHECKSUM"
        rec["url"]=url
        try:
            if urlparse(url).hostname!="data.binance.vision":raise ValueError("URL host not allowlisted")
            req=urllib.request.Request(url,headers={"User-Agent":"AISTS-CP0040-MonthlySidecarAudit/1.0","Accept":"text/plain"})
            with urllib.request.urlopen(req,timeout=25) as response:
                final_url=response.geturl();final=urlparse(final_url);status=getattr(response,"status",None);body=response.read(4097)
            rec["final_url"]=final_url;rec["http_status"]=status
            if final.scheme!="https" or final.hostname!="data.binance.vision":rec["sidecar_status"]="BLOCKED_REDIRECT_OUTSIDE_ALLOWLIST"
            elif status!=200:rec["sidecar_status"]="FAIL_HTTP_STATUS"
            elif not body or len(body)>4096:rec["sidecar_status"]="FAIL_SIDECAR_SIZE"
            else:
                txt=body.decode("utf-8",errors="strict").strip()
                toks=sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b",txt)))
                token_ok=len(toks)==1 and toks[0]==rec["cache_sha256"].lower()
                name_ok=rec["filename"] in txt
                rec.update({"sidecar_bytes":len(body),"sidecar_sha256":sha_bytes(body),"sidecar_text":txt,
                            "checksum_tokens":toks,"sidecar_names_exact_archive":name_ok,
                            "official_token_matches_cached_zip":token_ok,"archive_zip_downloaded":False,
                            "market_data_rest_api_used":False})
                rec["sidecar_status"]="PASS_OFFICIAL_SIDECAR_MATCHES_CACHED_ZIP" if token_ok and name_ok else "FAIL_TOKEN_OR_FILENAME"
        except Exception as e:
            rec.update({"sidecar_status":"FAIL_SIDECAR_FETCH","fetch_error_type":type(e).__name__,"fetch_error":str(e),
                        "archive_zip_downloaded":False,"market_data_rest_api_used":False})
    good=sum(r.get("sidecar_status")=="PASS_OFFICIAL_SIDECAR_MATCHES_CACHED_ZIP" for r in records)
    status="PASS_MONTHLY_SIDECARS_MATCH_CACHED_ARCHIVE_BYTES" if good==14 else "REVIEW_REQUIRED_MONTHLY_SIDECAR_PROVENANCE_INCOMPLETE"
    summary={"schema_version":1,"checkpoint":"CP-0040","task":"cp0040_aggregation_monthly_sidecar_audit",
        "status":status,"started_at_utc":started,"finished_at_utc":now(),
        "scope":"OFFICIAL_MONTHLY_CHECKSUM_TEXT_ONLY_FOR_11_OPEN_AGGREGATION_BUCKETS",
        "bucket_cases":11,"unique_monthly_archives_targeted":14,"monthly_sidecars_passed":good,
        "monthly_sidecars_failed_or_unavailable":14-good,"monthly_targets":records,
        "frozen_evidence":{"cp0040_manifest_sha256":manifest_sha,"cp0040_nonrow_blockers_sha256":blocker_sha,
            "bucket_snapshot_git_blob_sha1":snap_sha1,"bucket_summary_sha256":sha_file(bucket_sum_path),
            "bucket_comparison_sha256":sha_file(comp),"daily_reference_archive_manifest_sha256":daily_sha,
            "daily_reference_archive_manifest_rows":len(daily_rows)},
        "checks":checks,"checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),
        "external_network_used":True,"official_monthly_sidecar_requests":14,"monthly_zip_downloads":0,
        "daily_archive_downloads":0,"market_data_rest_api_used":False,"exchange_credentials_used":False,
        "raw_archives_modified":False,"canonical_source_selected":False,"source_cases_closed":0,
        "root_cause":"OPEN_NOT_ESTABLISHED","unresolved_nonrow_aggregation_blockers":11,
        "g0":"BLOCKED_GLOBAL","canonical_source":"NONE","backtest_rerun":False,"production_candidate_build":False,
        "strategy_promoted":False,"live_signing_broadcast_orders":"BLOCKED",
        "decision":"Sidecar results bind current official checksum tokens to cached monthly ZIP bytes only; they do not choose monthly over daily, resolve the conflict, or close any bucket."}
    write_json(out/"CP0040_Aggregation_Monthly_Sidecar_Audit_Summary.json",summary)
    write_csv(out/"CP0040_Aggregation_Monthly_Sidecar_Audit_Details.csv",records)
    (out/"CP0040_Aggregation_Monthly_Sidecar_Audit_Report_HI.md").write_text(report_text(status,f"{good}/14 official monthly checksum sidecars matched the cached monthly ZIP hashes. ZIP downloads=0; daily archive downloads=0."),encoding="utf-8")
    print(json.dumps({"status":status,"monthly_sidecars_passed":good,"monthly_sidecars_expected":14,
        "monthly_zip_downloads":0,"daily_archive_downloads":0,"market_data_rest_api_used":False,
        "all_11_remain_open":True},ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
