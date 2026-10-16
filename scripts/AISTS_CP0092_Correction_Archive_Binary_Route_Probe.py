#!/usr/bin/env python3
"""Bounded binary-route probe for the official Binance correction ZIP."""
from __future__ import annotations
import argparse,csv,hashlib,json,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URL="https://raw.githubusercontent.com/binance/binance-public-data/master/updates/2022-08-08_kline_updates.zip"
EXPECTED_GIT_BLOB_SHA1="90631298cf50ac2e1ee8372a087767b010d78a21"
EXPECTED_BYTES=6653240
MAX_BYTES=8_000_000
TARGETS=[
("FETCHREF-15m-2017-12-04","BTCUSDT-15m-2017-12-04.zip"),
("FETCHREF-15m-2018-02-05","BTCUSDT-15m-2018-02-05.zip"),
("FETCHREF-15m-2018-02-07","BTCUSDT-15m-2018-02-07.zip"),
("FETCHREF-15m-2018-03-04","BTCUSDT-15m-2018-03-04.zip"),
("FETCHREF-15m-2018-06-20","BTCUSDT-15m-2018-06-20.zip"),
("FETCHREF-15m-2018-09-05","BTCUSDT-15m-2018-09-05.zip"),
("FETCHREF-1h-2018-03-20","BTCUSDT-1h-2018-03-20.zip"),
("FETCHREF-30m-2017-12-04","BTCUSDT-30m-2017-12-04.zip"),
("FETCHREF-30m-2018-02-07","BTCUSDT-30m-2018-02-07.zip"),
("FETCHREF-30m-2018-03-04","BTCUSDT-30m-2018-03-04.zip"),
("FETCHREF-30m-2018-03-20","BTCUSDT-30m-2018-03-20.zip"),
("FETCHREF-30m-2018-06-20","BTCUSDT-30m-2018-06-20.zip"),
("FETCHREF-5m-2017-12-04","BTCUSDT-5m-2017-12-04.zip"),
("FETCHREF-5m-2018-02-05","BTCUSDT-5m-2018-02-05.zip"),
("FETCHREF-5m-2018-03-04","BTCUSDT-5m-2018-03-04.zip"),
("FETCHREF-5m-2018-09-05","BTCUSDT-5m-2018-09-05.zip")]
def now(): return datetime.now(timezone.utc).isoformat()
def sha256(b): return hashlib.sha256(b).hexdigest()
def blobsha(b): return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def write_json(p,o):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader()
        if rows:w.writerows(rows)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output-dir",default="results/cp0092_correction_archive_binary_probe")
    out=(ROOT/ap.parse_args().output_dir).resolve();out.mkdir(parents=True,exist_ok=True);started=now()
    checks=[];members=[];targets=[]
    def ck(n,ok,d):checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    body=b"";headers={};http_status=None;error=None
    try:
        req=urllib.request.Request(URL,headers={"Accept":"application/octet-stream","User-Agent":"AISTS-CP0092-CorrectionArchiveProbe/1.0"})
        with urllib.request.urlopen(req,timeout=45) as response:
            http_status=getattr(response,"status",None);headers={k.lower():v for k,v in response.headers.items()}
            ctype=headers.get("content-type","")
            if http_status!=200:raise RuntimeError("HTTP status is not 200")
            if "json" in ctype.lower():raise RuntimeError("Raw media type returned JSON, not raw bytes")
            body=response.read(MAX_BYTES+1)
        if len(body)>MAX_BYTES:raise RuntimeError("Response exceeded strict size cap")
        if not body:raise RuntimeError("No binary body delivered")
    except Exception as exc:error={"type":type(exc).__name__,"message":str(exc)}
    body_sha1=blobsha(body) if body else "";body_sha256=sha256(body) if body else ""
    binary=out/"source"/"2022-08-08_kline_updates.zip";crc="NOT_RUN";member_count=0
    if body:
        ck("raw_media_http_200",http_status==200,{"http_status":http_status,"content_type":headers.get("content-type","")})
        ck("archive_byte_count",len(body)==EXPECTED_BYTES,{"actual":len(body),"expected":EXPECTED_BYTES})
        ck("official_git_blob_sha1",body_sha1==EXPECTED_GIT_BLOB_SHA1,{"actual":body_sha1,"expected":EXPECTED_GIT_BLOB_SHA1})
        binary.parent.mkdir(parents=True,exist_ok=True);binary.write_bytes(body)
        try:
            with zipfile.ZipFile(binary,"r") as z:
                bad=z.testzip();infos=[i for i in z.infolist() if not i.is_dir()];member_count=len(infos)
                crc="PASS" if bad is None else "FAIL"
                for info in infos:
                    h=hashlib.sha256();n=0
                    with z.open(info,"r") as fh:
                        for chunk in iter(lambda:fh.read(1024*1024),b""):h.update(chunk);n+=len(chunk)
                    basename=info.filename.replace("\\","/").split("/")[-1]
                    hits=[cid for cid,name in TARGETS if basename==name]
                    members.append({"member_name":info.filename,"member_bytes":info.file_size,"member_sha256":h.hexdigest(),
                                    "zip_crc":"PASS" if bad is None else "FAIL","exact_missing_target_case_ids":";".join(hits),"exact_target_filename_match":bool(hits)})
        except Exception as exc:crc="FAIL";error={"type":type(exc).__name__,"message":str(exc)}
        ck("zip_crc_member_integrity",crc=="PASS" and member_count>0,{"crc":crc,"member_count":member_count,"error":error})
    else:
        ck("raw_media_http_200",False,{"http_status":http_status,"error":error})
        ck("archive_byte_count",False,"0 bytes received")
        ck("official_git_blob_sha1",False,"NOT_COMPUTABLE")
        ck("zip_crc_member_integrity",False,"NOT_RUN_NO_BYTES")
    for cid,name in TARGETS:
        hits=[m for m in members if m["member_name"].replace("\\","/").split("/")[-1]==name]
        targets.append({"case_id":cid,"target_filename":name,"exact_basename_member_count":len(hits),
            "target_member_sha256":hits[0]["member_sha256"] if len(hits)==1 else "",
            "exact_target_mapping_available":len(hits)==1,"source_authority":"UNDETERMINED","source_case_closed":False})
    success=bool(body) and len(body)==EXPECTED_BYTES and body_sha1==EXPECTED_GIT_BLOB_SHA1 and crc=="PASS"
    status="PASS_CORRECTION_ARCHIVE_BINARY_ACQUIRED_AND_VERIFIED" if success else ("REVIEW_CORRECTION_ARCHIVE_BYTES_DELIVERED_VALIDATION_FAILED" if body else "BLOCKED_NEW_BINARY_ROUTE_NO_BYTES")
    checks_total=len(checks);checks_passed=sum(c["status"]=="PASS" for c in checks)
    summary={"schema_version":1,"checkpoint":"CP-0092","task":"cp0092_correction_archive_binary_route_probe","status":status,
        "started_at_utc":started,"finished_at_utc":now(),"url":URL,
        "transport":{"route":"raw.githubusercontent.com fetched from GitHub-hosted Actions runner after local-container DNS failure","accept":"application/octet-stream","http_status":http_status,"content_type":headers.get("content-type",""),"error":error},
        "archive":{"expected_bytes":EXPECTED_BYTES,"actual_bytes":len(body),"expected_git_blob_sha1":EXPECTED_GIT_BLOB_SHA1,"actual_git_blob_sha1":body_sha1,
            "sha256":body_sha256,"zip_crc":crc,"member_count":member_count,"path":str(binary.relative_to(ROOT)) if body else None},
        "checks":checks,"checks_passed":checks_passed,"checks_total":checks_total,"members":members,"target_mappings":targets,
        "exact_target_basename_hits":sum(x["exact_target_mapping_available"] for x in targets),
        "official_daily_zip_checksum_pairs_acquired":0,"market_data_rest_api_used":False,"exchange_credentials_used":False,
        "canonical_source_selected":False,"source_cases_closed":0,"source_authority":"UNDETERMINED",
        "open_debt":{"daily_zip_checksum_pairs_before_probe":"0/16","shared_conflicts":60,"unmatched_rows_quarantined":909,
            "aggregation_buckets":11,"g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED"},
        "decision":"This attempt uses GitHub-hosted Actions egress, a different transport environment from the previously DNS-blocked local container. Archive acquisition alone does not prove per-target mapping or resolve source authority. Each target requires exact member/schema match and independent official daily ZIP plus .CHECKSUM validation."}
    write_json(out/"CP0092_Correction_Archive_Binary_Route_Summary.json",summary)
    write_csv(out/"CP0092_Correction_Archive_Member_Inventory.csv",members)
    write_csv(out/"CP0092_Missing_Daily_Target_Mapping.csv",targets)
    report=["# CP-0092: Correction archive binary route probe","", "Status: "+status,
        "Route: official raw.githubusercontent.com repository file, requested from the GitHub-hosted runner after the prior local-container DNS failure.",
        "HTTP status: "+str(http_status)+"; bytes received: "+str(len(body))+"; expected bytes: "+str(EXPECTED_BYTES)+".",
        "Expected Git blob SHA-1: "+EXPECTED_GIT_BLOB_SHA1+"; actual: "+(body_sha1 or "NOT_COMPUTABLE")+".",
        "SHA-256: "+(body_sha256 or "NOT_COMPUTABLE")+"; ZIP CRC: "+crc+"; members: "+str(member_count)+".",
        "Exact missing-target basename matches: "+str(summary["exact_target_basename_hits"])+"/16; daily ZIP plus .CHECKSUM pairs acquired: 0.",
        "No source case closed; canonical source NONE; G0 BLOCKED_GLOBAL; no backtest, candidate build, exchange, signing or broadcast action.",
        "Interpretation: verified correction ZIP bytes do not by themselves authorize row mapping or canonical source selection."]
    (out/"CP0092_Correction_Archive_Binary_Route_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"checks_passed":checks_passed,"checks_total":checks_total,"bytes":len(body),
        "git_blob_sha1":body_sha1,"sha256":body_sha256,"zip_crc":crc,"members":member_count,
        "exact_target_matches":summary["exact_target_basename_hits"],"daily_pairs_acquired":0,"g0":"BLOCKED_GLOBAL"},ensure_ascii=False,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
