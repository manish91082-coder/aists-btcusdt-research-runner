#!/usr/bin/env python3
"""CP-0171: bounded official Binance Vision daily-archive acquisition only."""
from __future__ import annotations
import concurrent.futures, csv, hashlib, io, json, re, urllib.error, urllib.request, zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

TASK="cp0171_daily_archive_acquisition"
START=date(2026,10,1)
END=date(2026,10,18)
INTERVALS=("5m","15m","30m","1h","4h","1d")
STEP_MS={"5m":300_000,"15m":900_000,"30m":1_800_000,"1h":3_600_000,"4h":14_400_000,"1d":86_400_000}
EXPECTED_ROWS={"5m":288,"15m":96,"30m":48,"1h":24,"4h":6,"1d":1}
HOST="data.binance.vision"
UA="AISTS-CP0171-Official-Daily-Archive-Acquisition/1.0"
ALLOWED_HOSTS={HOST,"s3.amazonaws.com","s3-ap-northeast-1.amazonaws.com","s3.ap-northeast-1.amazonaws.com","s3.dualstack.ap-northeast-1.amazonaws.com","data.binance.vision.s3.amazonaws.com","data.binance.vision.s3-ap-northeast-1.amazonaws.com","data.binance.vision.s3.ap-northeast-1.amazonaws.com"}

def sha256(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def parse_checksum(text:str,filename:str)->str|None:
    hits=set()
    for line in text.splitlines():
        m=re.match(r"^\s*([0-9a-fA-F]{64})\s+\*?(\S+)\s*$",line)
        if m and m.group(2).rsplit("/",1)[-1]==filename:
            hits.add(m.group(1).lower())
    return next(iter(hits)) if len(hits)==1 else None

def official_url(url:str,expected_path:str)->bool:
    p=urlparse(url)
    return p.scheme=="https" and p.hostname==HOST and p.path==expected_path and not p.query and not p.fragment

class AllowOfficialRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        src,dst=urlparse(req.full_url),urlparse(newurl)
        paths={src.path,"/data.binance.vision"+src.path}
        s3=dst.hostname in ALLOWED_HOSTS and dst.hostname!=HOST
        if dst.scheme!="https" or dst.hostname not in ALLOWED_HOSTS or dst.path not in paths or (dst.query and not s3) or dst.fragment:
            raise urllib.error.HTTPError(req.full_url,code,"blocked non-allowlisted redirect",headers,fp)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def request_bytes(url:str,expected_path:str,max_bytes:int,timeout:int=30):
    if not official_url(url,expected_path):
        return {"status":"BLOCKED_URL_VALIDATION","error":"URL did not match exact official HTTPS host/path"}
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    try:
        with urllib.request.build_opener(AllowOfficialRedirects()).open(req,timeout=timeout) as response:
            final=urlparse(response.geturl()); status=getattr(response,"status",None); body=response.read(max_bytes+1)
        if final.scheme!="https" or final.hostname not in ALLOWED_HOSTS or final.path not in {expected_path,"/data.binance.vision"+expected_path}:
            return {"status":"BLOCKED_REDIRECT_VALIDATION","error":"Final URL outside allowlisted official object path"}
        if status!=200: return {"status":"HTTP_ERROR","http_status":status,"error":f"unexpected HTTP status {status}"}
        if len(body)>max_bytes: return {"status":"SIZE_LIMIT_EXCEEDED","error":f"response exceeded {max_bytes} bytes"}
        return {"status":"FETCHED","http_status":status,"bytes":body,"error":""}
    except urllib.error.HTTPError as e:
        if e.code==404: return {"status":"NOT_AVAILABLE_404","http_status":404,"error":"official object not available"}
        return {"status":"HTTP_ERROR","http_status":e.code,"error":f"HTTP {e.code}: {e.reason}"}
    except (urllib.error.URLError,TimeoutError,OSError,ValueError) as e:
        return {"status":"FETCH_ERROR","error":f"{type(e).__name__}: {e}"}

def ts_ms(raw:str)->int:
    n=int(raw)
    if 1_000_000_000_000<=n<100_000_000_000_000: return n
    if 1_000_000_000_000_000<=n<100_000_000_000_000_000 and n%1000==0: return n//1000
    raise ValueError(f"unsupported open_time epoch unit: {raw}")

def inspect_zip(payload:bytes,interval:str,target_day:date):
    q={"zip_crc":"FAIL","csv_members":0,"row_count":0,"duplicate_open_times":0,"off_grid_open_times":0,"wrong_utc_date_rows":0,"malformed_rows":0,"expected_rows":EXPECTED_ROWS[interval],"row_count_status":"UNKNOWN","error":""}
    try:
        with zipfile.ZipFile(io.BytesIO(payload),"r") as zf:
            bad=zf.testzip(); q["zip_crc"]="PASS" if bad is None else "FAIL"
            if bad is not None: q["error"]=f"CRC failure in member {bad}"; return q
            members=[n for n in zf.namelist() if n.lower().endswith(".csv")]; q["csv_members"]=len(members)
            if len(members)!=1: q["error"]=f"expected exactly one CSV member; found {len(members)}"; return q
            opens=[]
            with zf.open(members[0],"r") as raw:
                for line_no,row in enumerate(csv.reader(io.TextIOWrapper(raw,encoding="utf-8-sig",newline="")),1):
                    if not row: continue
                    try:
                        op=ts_ms(row[0])
                        if len(row)<12: raise ValueError("fewer than 12 kline fields")
                        opens.append(op)
                    except (ValueError,IndexError):
                        if line_no!=1: q["malformed_rows"]+=1
            q["row_count"]=len(opens); q["duplicate_open_times"]=len(opens)-len(set(opens))
            day_start=int(datetime(target_day.year,target_day.month,target_day.day,tzinfo=timezone.utc).timestamp()*1000)
            q["wrong_utc_date_rows"]=sum(not day_start<=x<day_start+86_400_000 for x in opens)
            q["off_grid_open_times"]=sum(x%STEP_MS[interval]!=0 for x in opens)
            q["row_count_status"]="EXPECTED_COUNT" if len(opens)==EXPECTED_ROWS[interval] else "ROW_COUNT_DEVIATION"
            return q
    except (zipfile.BadZipFile,OSError,UnicodeError,ValueError) as e:
        q["error"]=f"{type(e).__name__}: {e}"; return q

def target_days():
    cur=START
    while cur<=END:
        yield cur
        cur+=timedelta(days=1)

def acquire_one(interval:str,day:date,out_root:Path):
    name=f"BTCUSDT-{interval}-{day.isoformat()}.zip"
    rel=f"/data/spot/daily/klines/BTCUSDT/{interval}/{name}"
    url="https://"+HOST+rel; checksum_url=url+".CHECKSUM"
    row={"interval":interval,"utc_date":day.isoformat(),"archive_name":name,"archive_url":url,"checksum_url":checksum_url,"archive_status":"NOT_ATTEMPTED","sidecar_status":"NOT_ATTEMPTED","official_sha256":"","actual_sha256":"","archive_bytes":0,"sidecar_sha256":"","sidecar_bytes":0,"zip_crc":"NOT_CHECKED","csv_members":0,"row_count":0,"expected_rows":EXPECTED_ROWS[interval],"row_count_status":"UNKNOWN","duplicate_open_times":0,"off_grid_open_times":0,"wrong_utc_date_rows":0,"malformed_rows":0,"error":""}
    side=request_bytes(checksum_url,rel+".CHECKSUM",4096); row["sidecar_status"]=side["status"]
    if side["status"]!="FETCHED":
        row["archive_status"]="NOT_AVAILABLE_404" if side["status"]=="NOT_AVAILABLE_404" else "NOT_ATTEMPTED"
        row["error"]=side.get("error",""); return row
    sb=side["bytes"]; row["sidecar_bytes"]=len(sb); row["sidecar_sha256"]=sha256(sb)
    try: st=sb.decode("utf-8-sig",errors="strict").strip()
    except UnicodeError as e: row["sidecar_status"]="INVALID_ENCODING"; row["error"]=str(e); return row
    official=parse_checksum(st,name)
    if not official:
        row["sidecar_status"]="INVALID_OR_AMBIGUOUS_FILENAME_BOUND_HASH"; row["error"]="No unique SHA-256 bound to exact archive filename"; return row
    row["official_sha256"]=official
    sp=out_root/"raw"/interval/(name+".CHECKSUM"); sp.parent.mkdir(parents=True,exist_ok=True); sp.write_bytes(sb)
    archive=request_bytes(url,rel,100_000_000); row["archive_status"]=archive["status"]
    if archive["status"]!="FETCHED": row["error"]=archive.get("error",""); return row
    data=archive["bytes"]; row["archive_bytes"]=len(data); row["actual_sha256"]=sha256(data)
    ap=out_root/"raw"/interval/name; ap.parent.mkdir(parents=True,exist_ok=True); ap.write_bytes(data)
    if row["actual_sha256"]!=official: row["archive_status"]="HASH_MISMATCH"; row["error"]="Archive bytes differ from filename-bound official SHA-256"; return row
    row["archive_status"]="DOWNLOADED_HASH_MATCH"
    q=inspect_zip(data,interval,day)
    for k,v in q.items():
        if k in row: row[k]=v
    if q["zip_crc"]!="PASS" or q["csv_members"]!=1 or q["malformed_rows"]:
        row["archive_status"]="HASH_MATCH_REVIEW_REQUIRED_ARCHIVE_OR_SCHEMA"; row["error"]=q["error"] or "ZIP/schema/row parse QA failed"
    elif q["duplicate_open_times"] or q["off_grid_open_times"] or q["wrong_utc_date_rows"]:
        row["archive_status"]="HASH_MATCH_REVIEW_REQUIRED_TIMESTAMP_QA"; row["error"]="Duplicate, off-grid or wrong-UTC-date open timestamps"
    elif q["row_count_status"]!="EXPECTED_COUNT":
        row["archive_status"]="HASH_MATCH_REVIEW_REQUIRED_ROW_COUNT_DEVIATION"; row["error"]="Expected per-day row count differs; preserved for review"
    return row

def self_test():
    checks=[]
    def add(name,ok): checks.append({"test":name,"status":"PASS" if ok else "FAIL"})
    name="BTCUSDT-4h-2026-10-01.zip"; path="/data/spot/daily/klines/BTCUSDT/4h/"+name
    add("exact_official_url",official_url("https://"+HOST+path,path))
    add("reject_lookalike_host",not official_url("https://data.binance.vision.evil.test/data/spot/x","/data/spot/x"))
    add("reject_http",not official_url("http://data.binance.vision/data/spot/x","/data/spot/x"))
    add("checksum_exact_filename",parse_checksum("a"*64+"  "+name,name)=="a"*64)
    add("reject_wrong_filename_checksum",parse_checksum("a"*64+"  other.zip",name) is None)
    add("fixed_scope_108_archives",len(tuple(target_days()))*len(INTERVALS)==108)
    add("expected_daily_rows",EXPECTED_ROWS=={"5m":288,"15m":96,"30m":48,"1h":24,"4h":6,"1d":1})
    sample=io.BytesIO()
    with zipfile.ZipFile(sample,"w",compression=zipfile.ZIP_DEFLATED) as z:
        start=int(datetime(2026,10,1,tzinfo=timezone.utc).timestamp()*1000); lines=[]
        for i in range(6):
            op=start+i*STEP_MS["4h"]; lines.append(",".join(map(str,[op,"1","1","1","1","0",op+STEP_MS["4h"]-1,"0","0","0","0","0"])))
        z.writestr(name.replace(".zip",".csv"),"\n".join(lines)+"\n")
    q=inspect_zip(sample.getvalue(),"4h",date(2026,10,1))
    add("synthetic_zip_crc_and_grid",q["zip_crc"]=="PASS" and q["row_count"]==6 and q["off_grid_open_times"]==0 and q["wrong_utc_date_rows"]==0)
    return {"task":TASK,"checks_total":len(checks),"checks_passed":sum(x["status"]=="PASS" for x in checks),"checks":checks}

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",default="results/cp0171_daily_archive_acquisition"); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    if args.self_test:
        result=self_test(); print(json.dumps(result,sort_keys=True)); raise SystemExit(0 if result["checks_passed"]==result["checks_total"] else 1)
    out=Path(args.output_dir).resolve(); out.mkdir(parents=True,exist_ok=True); started=datetime.now(timezone.utc).isoformat()
    tasks=[(i,d) for d in target_days() for i in INTERVALS]; rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(acquire_one,i,d,out):(i,d) for i,d in tasks}
        for future in concurrent.futures.as_completed(futures):
            i,d=futures[future]
            try: rows.append(future.result())
            except Exception as e: rows.append({"interval":i,"utc_date":d.isoformat(),"archive_name":f"BTCUSDT-{i}-{d.isoformat()}.zip","archive_status":"UNHANDLED_ERROR","sidecar_status":"UNKNOWN","error":f"{type(e).__name__}: {e}"})
    rows.sort(key=lambda r:(r.get("utc_date",""),INTERVALS.index(r.get("interval","1d")) if r.get("interval") in INTERVALS else 99))
    fields=sorted({k for r in rows for k in r}); manifest=out/"CP0171_Daily_Archive_Acquisition_Manifest.csv"
    with manifest.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n"); w.writeheader(); w.writerows(rows)
    counts={}
    for r in rows:
        s=r.get("archive_status","UNKNOWN"); counts[s]=counts.get(s,0)+1
    verified=sum(1 for r in rows if r.get("actual_sha256") and r.get("actual_sha256")==r.get("official_sha256"))
    failures=[r for r in rows if r.get("archive_status") in {"HASH_MISMATCH","UNHANDLED_ERROR","BLOCKED_URL_VALIDATION","BLOCKED_REDIRECT_VALIDATION","SIZE_LIMIT_EXCEEDED"} or r.get("sidecar_status") in {"INVALID_ENCODING","INVALID_OR_AMBIGUOUS_FILENAME_BOUND_HASH"}]
    reviews=[r for r in rows if "REVIEW_REQUIRED" in r.get("archive_status","")]
    status="FAIL_INTEGRITY" if failures else ("REVIEW_REQUIRED" if reviews else "PASS_INTEGRITY")
    summary={"schema_version":1,"checkpoint":"CP-0171","task":TASK,"status":status,"started_at_utc":started,"finished_at_utc":datetime.now(timezone.utc).isoformat(),
      "scope":{"symbol":"BTCUSDT","market":"Spot","source":"official Binance Vision downloadable daily ZIP + filename-bound .CHECKSUM sidecar","intervals":list(INTERVALS),"start_date_utc":START.isoformat(),"end_date_utc":END.isoformat(),"expected_archive_count":len(tasks),"candidate_build":False,"backtest":False,"exchange_api":False,"source_authority_selected":False},
      "archive_status_counts":counts,"expected_archives":len(tasks),"archives_with_sidecar_verified_sha":verified,"review_required_rows":len(reviews),"integrity_failure_rows":len(failures),"manifest_path":manifest.name,"manifest_sha256":sha256(manifest.read_bytes()),
      "gates":{"G0":"BLOCKED_GLOBAL","canonical_source":"NONE","G2":"FAIL_CURRENT_23_CANDIDATES","G3":"BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT","G4":"INSUFFICIENT_EVIDENCE","G6":"NOT_BUILT","G7":"LIVE_BLOCKED","profitability":"NOT_ESTABLISHED"},
      "limitations":["Checksum verifies bytes, not canonical historical source authority.","404s are recorded, never fabricated or filled.","Timestamp and row-count anomalies are preserved for review, not auto-corrected.","Raw ZIPs are workflow artifacts, not committed to Git."]}
    (out/"CP0171_Daily_Archive_Acquisition_Summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,sort_keys=True))
    if failures: raise SystemExit(2)

if __name__=="__main__": main()
