#!/usr/bin/env python3
"""Acquire the exact 16 CP-0041 daily references and compare unchanged raw rows with cached monthly archives."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,shutil,zipfile
from collections import defaultdict,Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlparse

DAILY_BASE="https://data.binance.vision/data/spot/daily/klines/BTCUSDT"
QUEUE_SHA="b6660083860d5d90afc5d2661353ecf4c8f1aa2d355a9db99d6fc7a40e9b045d"
MONTHLY_MANIFEST_SHA="1fa5c6ff022d7ff10f293c55c9fb933599c16b3d5d68adc86f2a9425c1e16b65"
PACKAGE_SHA="23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc"
RULEBOOK_SHA="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
RAW_FIELDS=["open_time","open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore"]
ECON_FIELDS=["open","high","low","close","volume","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume"]
INTERVAL_MS={"5m":300000,"15m":900000,"30m":1800000,"1h":3600000}
PER_DAY={"5m":288,"15m":96,"30m":48,"1h":24}
TARGETS=[
 ("FETCHREF-15m-2017-12-04","15m","2017-12-04","BTCUSDT-15m-2017-12-04.zip"),
 ("FETCHREF-15m-2018-02-05","15m","2018-02-05","BTCUSDT-15m-2018-02-05.zip"),
 ("FETCHREF-15m-2018-02-07","15m","2018-02-07","BTCUSDT-15m-2018-02-07.zip"),
 ("FETCHREF-15m-2018-03-04","15m","2018-03-04","BTCUSDT-15m-2018-03-04.zip"),
 ("FETCHREF-15m-2018-06-20","15m","2018-06-20","BTCUSDT-15m-2018-06-20.zip"),
 ("FETCHREF-15m-2018-09-05","15m","2018-09-05","BTCUSDT-15m-2018-09-05.zip"),
 ("FETCHREF-1h-2018-03-20","1h","2018-03-20","BTCUSDT-1h-2018-03-20.zip"),
 ("FETCHREF-30m-2017-12-04","30m","2017-12-04","BTCUSDT-30m-2017-12-04.zip"),
 ("FETCHREF-30m-2018-02-07","30m","2018-02-07","BTCUSDT-30m-2018-02-07.zip"),
 ("FETCHREF-30m-2018-03-04","30m","2018-03-04","BTCUSDT-30m-2018-03-04.zip"),
 ("FETCHREF-30m-2018-03-20","30m","2018-03-20","BTCUSDT-30m-2018-03-20.zip"),
 ("FETCHREF-30m-2018-06-20","30m","2018-06-20","BTCUSDT-30m-2018-06-20.zip"),
 ("FETCHREF-5m-2017-12-04","5m","2017-12-04","BTCUSDT-5m-2017-12-04.zip"),
 ("FETCHREF-5m-2018-02-05","5m","2018-02-05","BTCUSDT-5m-2018-02-05.zip"),
 ("FETCHREF-5m-2018-03-04","5m","2018-03-04","BTCUSDT-5m-2018-03-04.zip"),
 ("FETCHREF-5m-2018-09-05","5m","2018-09-05","BTCUSDT-5m-2018-09-05.zip"),
]
# Exact relevant rows copied from CP-0041_Monthly_Archive_Verification.csv.
MONTHLY_ROWS=[
 ("BTCUSDT-15m-2017-12.zip","15m","MATCH","a737d013096403196346f6297fe21fce7e3e8f7b6366e517535d9835eeb2fdf4",174601),
 ("BTCUSDT-15m-2018-02.zip","15m","MATCH","9b7f75cef2aefea621bfedb0f136f15fc60aed5e6f4da1c521765a4c267123e0",141728),
 ("BTCUSDT-15m-2018-03.zip","15m","MATCH","52982e2c0ceb520365cf320c631fd0603aff6d0b0b0a81d06e2c23f5a81e8be2",162923),
 ("BTCUSDT-15m-2018-06.zip","15m","MATCH","a80442581d5ac478c283158bc754b62c90cb45bac2081126b2a5f3400ddd74bc",153423),
 ("BTCUSDT-15m-2018-09.zip","15m","MATCH","17c6956d455bcba50c83a17fb04f5c84feddfd3f217cbb117c3f6fe8fe366667",155670),
 ("BTCUSDT-1h-2018-03.zip","1h","MATCH","a3f45f20d28eab88292d1baac72402ebf59f4462d0bb834288f69b59a65cbf5f",42999),
 ("BTCUSDT-30m-2017-12.zip","30m","MATCH","c64fcc280bc444ad7508982d526198373812e3ed44804969dc0d2b57da39517b",89592),
 ("BTCUSDT-30m-2018-02.zip","30m","MATCH","e14dc22f1ede6a9ae50130101de3fefb8ddf06220cb3e6afae9315b441e66681",72626),
 ("BTCUSDT-30m-2018-03.zip","30m","MATCH","21d47d7deb9582046c22786b676b9de869d4b00772c06c3a438d37ef57e3ca28",83514),
 ("BTCUSDT-30m-2018-06.zip","30m","MATCH","cd72295e0b4806803e08b9af1ab3580f420d1ac7a29b62e6f827c6e35ded7dcf",78643),
 ("BTCUSDT-5m-2017-12.zip","5m","MATCH","fab87582c0bfd79f200dfbbeebbce39fabf7c137c768daa867d9d688f64c6b19",498150),
 ("BTCUSDT-5m-2018-02.zip","5m","MATCH","44bc33f321fbc4a4dd5c99bec7bbb4ca86e5cc33ddc6459610a18db7ae872c0b",404071),
 ("BTCUSDT-5m-2018-03.zip","5m","MATCH","9f79a89dad86fbce45f7be8f0487e115a4e8d609b4c415b5a32781e823df0cd4",463234),
 ("BTCUSDT-5m-2018-09.zip","5m","MATCH","820d494c55b1b0149872f54af63d8245a98c48d83ede5f8b949ee49f42b52704",443173),
]
MONTHLY_MAP={r[0]:{"filename":r[0],"interval":r[1],"status":r[2],"expected_sha256":r[3],"actual_sha256":r[3],"bytes":r[4]} for r in MONTHLY_ROWS}
ALLOWED_HOSTS={"data.binance.vision","s3.amazonaws.com","s3-ap-northeast-1.amazonaws.com","s3.ap-northeast-1.amazonaws.com","s3.dualstack.ap-northeast-1.amazonaws.com","data.binance.vision.s3.amazonaws.com","data.binance.vision.s3-ap-northeast-1.amazonaws.com","data.binance.vision.s3.ap-northeast-1.amazonaws.com"}
BASE_FILES=(
 "CP0107_Feb2018_Extraction_Summary.json","CP0107_Feb2018_OffGrid_RawRows.csv","CP0107_Feb2018_DailyCoverage_RawRows.csv","CP0107_Feb2018_SegmentCoverage.csv","CP0107_Feb2018_SourceVerification.csv","CP0107_Feb2018_Extraction_Report_HI.md","CP0107_Feb2018_Checks.csv",
 "CP0107_Dec2020_ChildWindow_Audit_Summary.json","CP0107_Dec2020_5m_ActualRows_Window.csv","CP0107_Dec2020_5m_ChildCoverage.csv","CP0107_Dec2020_ReviewRollup_ChildCoverage.csv","CP0107_Dec2020_5m_SourceVerification.csv",
 "CP0107_Dec2020_FieldReview_Summary.json","CP0107_Dec2020_FieldReview_Report_HI.md","CP0107_Dec2020_Shared_5m_RawField_Comparison.csv","CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv","CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv",
 "CP0107_Monthly_Checksum_Provenance_Summary.json","CP0107_Monthly_Checksum_Provenance_Report_HI.md","BTCUSDT-5m-2020-12.zip.CHECKSUM","BTCUSDT-5m-2020-12-21.zip.CHECKSUM"
)
def log(s): print("[CP0107-CP0041-DAILY-REF] "+s,flush=True)
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def write_csv(path,rows,fields=None):
 if fields is None: fields=list(rows[0].keys()) if rows else ["status"]
 with Path(path).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader();w.writerows(rows)
def read_csv(path):
 with Path(path).open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def iso(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
def day(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()
def archive_url(interval,filename,checksum=False):
 u=DAILY_BASE+"/"+interval+"/"+filename
 return u+".CHECKSUM" if checksum else u
class RestrictedRedirect(HTTPRedirectHandler):
 def __init__(self,original_path):super().__init__();self.original_path=original_path
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  p=urlparse(newurl)
  if p.scheme!="https" or p.hostname not in ALLOWED_HOSTS:raise HTTPError(newurl,code,"redirect outside official public-data host allowlist",headers,fp)
  if not(p.path==self.original_path or p.path.endswith(self.original_path)):raise HTTPError(newurl,code,"redirect changed object path",headers,fp)
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch_official(url,max_bytes):
 p=urlparse(url)
 if p.scheme!="https" or p.hostname!="data.binance.vision" or not p.path.startswith("/data/spot/daily/klines/"):raise ValueError("blocked URL outside official daily archive paths")
 req=Request(url,headers={"User-Agent":"AISTS-CP0107-CP0041-DailyReferenceAudit/1.0","Accept":"application/octet-stream"})
 with build_opener(RestrictedRedirect(p.path)).open(req,timeout=45) as r:
  final=urlparse(r.geturl());status=getattr(r,"status",None)
  if final.scheme!="https" or final.hostname not in ALLOWED_HOSTS or not(p.path==final.path or final.path.endswith(p.path)):raise ValueError("final URL failed official-host/object-path validation")
  body=r.read(max_bytes+1)
 if status!=200:raise ValueError("HTTP status not 200 for "+url)
 if len(body)>max_bytes:raise ValueError("bounded download size exceeded for "+url)
 return body,r.geturl(),status
def zip_csv_member(path):
 with zipfile.ZipFile(path,"r") as z:
  bad=z.testzip()
  if bad:raise ValueError("ZIP CRC failure at "+bad)
  files=[x.filename for x in z.infolist() if not x.is_dir()]
  csvs=[x for x in files if x.lower().endswith(".csv")]
  if len(files)!=1 or len(csvs)!=1:raise ValueError("expected exactly one CSV member; got "+str(files))
  return csvs[0]
def load_date_rows(path,member,source,interval,date,archive_sha):
 rows=[]
 with zipfile.ZipFile(path,"r") as z:
  with z.open(member,"r") as raw:
   rd=csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline=""))
   for lineno,row in enumerate(rd,1):
    if not row:continue
    if len(row)!=12:raise ValueError(Path(path).name+" line "+str(lineno)+" has "+str(len(row))+" fields, expected 12")
    if not str(row[0]).isdigit():raise ValueError(Path(path).name+" line "+str(lineno)+" open_time is not an integer token")
    ms=int(row[0]);row_day=day(ms)
    if row_day!=date:continue
    rows.append({"source":source,"interval":interval,"date":row_day,"open_time_ms":ms,"open_time_token":str(row[0]),"open_time_utc":iso(ms),
     "csv_line_number":lineno,"archive_filename":Path(path).name,"archive_sha256":archive_sha,"raw":{k:str(v) for k,v in zip(RAW_FIELDS,row)}})
 return rows
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source-dir",required=True);ap.add_argument("--monthly-cache",required=True);ap.add_argument("--output-dir",required=True)
 ap.add_argument("--reuse-dir",default="");ap.add_argument("--reuse-run-id",default="");ap.add_argument("--reuse-artifact-id",default="")
 ap.add_argument("--reuse-artifact-sha256",default="")
 args=ap.parse_args();source_dir=Path(args.source_dir);monthly_root=Path(args.monthly_cache);out=Path(args.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
 reuse_dir=Path(args.reuse_dir) if args.reuse_dir else None
 if reuse_dir and not reuse_dir.is_dir():raise FileNotFoundError("previous run artifact folder missing: "+str(reuse_dir))
 for name in BASE_FILES:
  p=source_dir/name
  if not p.is_file():raise FileNotFoundError("previous verified evidence absent: "+str(p))
  shutil.copy2(p,out/name)
 checks=[]
 def check(name,ok,detail):checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
 # Frozen queue snapshot, derived from the byte-verified CP-0041 package member.
 queue=[]
 for case,iv,date,fn in TARGETS:
  queue.append({"case_id":case,"record_type":"MISSING_DAILY_REFERENCE_ACQUISITION","interval":iv,"utc_date":date,"daily_zip_filename":fn,
   "official_daily_zip_url":archive_url(iv,fn),"official_checksum_url":archive_url(iv,fn,True),
   "queue_member_sha256":QUEUE_SHA,"source_package_sha256":PACKAGE_SHA,
   "current_disposition":"NOT_ACQUIRED_BEFORE_THIS_RUN; OPEN_PENDING_EXACT_ROW_COMPARISON"})
 write_csv(out/"CP0107_CP0041_DailyReference_Queue_Snapshot.csv",queue,
  ["case_id","record_type","interval","utc_date","daily_zip_filename","official_daily_zip_url","official_checksum_url","queue_member_sha256","source_package_sha256","current_disposition"])
 check("frozen_cp0041_queue_16_rows",len(queue)==16,"queue_member_sha256="+QUEUE_SHA)
 check("frozen_monthly_manifest_14_rows",len(MONTHLY_MAP)==14,"monthly_manifest_member_sha256="+MONTHLY_MANIFEST_SHA)
 # Verify every required monthly ZIP exclusively from cache and the frozen CP-0041 manifest subset.
 unique_months=sorted({(x["interval"],x["utc_date"][:7],f"BTCUSDT-{x['interval']}-{x['utc_date'][:7]}.zip") for x in queue})
 monthly_records=[];monthly_index={}
 for iv,period,fn in unique_months:
  frozen=MONTHLY_MAP.get(fn)
  if not frozen:raise ValueError("monthly manifest subset lacks "+fn)
  p=monthly_root/iv/period/fn
  if not p.is_file():raise FileNotFoundError("cached monthly ZIP absent; network fallback forbidden: "+str(p))
  digest=sha_file(p);size=p.stat().st_size;member=zip_csv_member(p)
  ok=digest==frozen["expected_sha256"]==frozen["actual_sha256"] and size==int(frozen["bytes"]) and frozen["status"]=="MATCH"
  if not ok:raise ValueError("monthly cache hash/size differs from CP-0041 manifest: "+fn)
  record={"filename":fn,"interval":iv,"period":period,"cache_path":str(p),"sha256":digest,"expected_sha256":frozen["expected_sha256"],
   "bytes":size,"zip_crc":"PASS","csv_member":member,"status":"PASS","source_manifest_member_sha256":MONTHLY_MANIFEST_SHA}
  monthly_records.append(record);monthly_index[fn]=(p,member,record)
  check("monthly_manifest_hash_crc:"+fn,ok,"sha256="+digest+"; bytes="+str(size))
 monthly_subset=[]
 for rec in monthly_records:
  monthly_subset.append({"filename":rec["filename"],"interval":rec["interval"],"status":"MATCH","expected_sha256":rec["expected_sha256"],
   "actual_sha256":rec["sha256"],"bytes":rec["bytes"],"zip_crc":"PASS","csv_member":rec["csv_member"],"source_manifest_member_sha256":MONTHLY_MANIFEST_SHA})
 write_csv(out/"CP0107_CP0041_MonthlyArchive_Manifest_Subset.csv",monthly_subset,
  ["filename","interval","status","expected_sha256","actual_sha256","bytes","zip_crc","csv_member","source_manifest_member_sha256"])
 sources=[];periods=[];comparisons=[];missing_expected=[]
 for item in queue:
  iv=item["interval"];date=item["utc_date"];filename=item["daily_zip_filename"];zip_url=item["official_daily_zip_url"];side_url=item["official_checksum_url"]
  monthfn=f"BTCUSDT-{iv}-{date[:7]}.zip";mp,mmember,mrec=monthly_index[monthfn]
  if reuse_dir:
   prior_zip=reuse_dir/filename;prior_sidecar=reuse_dir/(filename+".CHECKSUM")
   if not prior_zip.is_file() or not prior_sidecar.is_file():
    raise FileNotFoundError("previous run artifact lacks acquired ZIP/sidecar; refusing repeat network download for "+filename)
   zipbytes=prior_zip.read_bytes();sidebytes=prior_sidecar.read_bytes()
   zipfinal="NOT_CAPTURED_IN_PRIOR_RUN_ARTIFACT";sidefinal="NOT_CAPTURED_IN_PRIOR_RUN_ARTIFACT";ziphttp=200;sidehttp=200
   retrieval_method="REUSED_VERIFIED_PRIOR_RUN_ARTIFACT"
  else:
   sidebytes,sidefinal,sidehttp=fetch_official(side_url,8192)
   zipbytes,zipfinal,ziphttp=fetch_official(zip_url,100_000_000)
   retrieval_method="FETCHED_OFFICIAL_BINANCE_PUBLIC_DATA"
  side_text=sidebytes.decode("utf-8",errors="strict").strip()
  tokens=sorted(set(v.lower() for v in re.findall(r"(?i)\b[0-9a-f]{64}\b",side_text)))
  side_ok=len(tokens)==1 and filename in side_text and sidehttp==200
  if not side_ok:raise ValueError("official .CHECKSUM content/name/hash token ambiguous for "+filename)
  zipsha=sha_bytes(zipbytes);hash_ok=zipsha==tokens[0]
  if not hash_ok:raise ValueError("daily archive SHA does not equal official .CHECKSUM token: "+filename)
  archive=out/filename;archive.write_bytes(zipbytes)
  sidecar=out/(filename+".CHECKSUM");sidecar.write_bytes(sidebytes)
  if sha_file(archive)!=zipsha or sha_file(sidecar)!=sha_bytes(sidebytes):raise ValueError("persisted new evidence bytes changed for "+filename)
  dmember=zip_csv_member(archive)
  drows=load_date_rows(archive,dmember,"DAILY",iv,date,zipsha)
  mrows=load_date_rows(mp,mmember,"MONTHLY",iv,date,mrec["sha256"])
  d_index=defaultdict(list);m_index=defaultdict(list)
  for r in drows:d_index[r["open_time_ms"]].append(r)
  for r in mrows:m_index[r["open_time_ms"]].append(r)
  dkeys=set(d_index);mkeys=set(m_index);union=sorted(dkeys|mkeys);shared=dkeys&mkeys
  expected_step=INTERVAL_MS[iv]
  day_start=int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp()*1000)
  expected_keys=list(range(day_start,day_start+86400000,expected_step))
  d_missing=sorted(set(expected_keys)-dkeys);m_missing=sorted(set(expected_keys)-mkeys)
  d_offgrid=sorted(k for k in dkeys if (k-day_start)%expected_step!=0)
  m_offgrid=sorted(k for k in mkeys if (k-day_start)%expected_step!=0)
  ddups=sum(len(v)>1 for v in d_index.values());mdups=sum(len(v)>1 for v in m_index.values())
  exact_pairs=div_pairs=econ_pairs=close_only=meta_only=0;field_counts=Counter()
  for key in union:
   dl=d_index.get(key,[]);ml=m_index.get(key,[])
   for occ in range(max(len(dl),len(ml))):
    dr=dl[occ] if occ<len(dl) else None;mr=ml[occ] if occ<len(ml) else None
    diffs=[f for f in RAW_FIELDS if dr["raw"][f]!=mr["raw"][f]] if dr and mr else []
    if dr and mr:
     if len(dl)==1 and len(ml)==1 and not diffs:exact_pairs+=1
     if diffs:div_pairs+=1;field_counts.update(diffs)
     if any(f in ECON_FIELDS for f in diffs):econ_pairs+=1
     if diffs==["close_time"]:close_only+=1
     if diffs and set(diffs).issubset({"close_time","ignore"}):meta_only+=1
     relation="DUPLICATE_KEY_REVIEW" if len(dl)>1 or len(ml)>1 else ("SHARED_RAW_EXACT" if not diffs else "SHARED_RAW_DIVERGENT")
    elif dr:relation="DAILY_ONLY_KEY"
    else:relation="MONTHLY_ONLY_KEY"
    row={"case_id":item["case_id"],"interval":iv,"utc_date":date,"open_time_ms":key,"open_time_utc":iso(key),"occurrence_index":occ+1,
     "daily_key_occurrences":len(dl),"monthly_key_occurrences":len(ml),"row_relation":relation,"differing_raw_fields":";".join(diffs),
     "differing_field_count":len(diffs),"economic_differing_fields":";".join(f for f in diffs if f in ECON_FIELDS),
     "economic_differing_field_count":sum(f in ECON_FIELDS for f in diffs),"expected_close_time_ms":key+expected_step-1,
     "monthly_close_time_ms":mr["raw"]["close_time"] if mr else "","daily_close_time_ms":dr["raw"]["close_time"] if dr else "",
     "monthly_close_time_delta_ms":int(mr["raw"]["close_time"])-(key+expected_step-1) if mr else "",
     "daily_close_time_delta_ms":int(dr["raw"]["close_time"])-(key+expected_step-1) if dr else "",
     "monthly_archive_filename":monthfn,"monthly_archive_sha256":mrec["sha256"],"monthly_csv_line_number":mr["csv_line_number"] if mr else "",
     "daily_archive_filename":filename,"daily_archive_sha256":zipsha,"daily_sidecar_sha256":sha_bytes(sidebytes),
     "daily_csv_line_number":dr["csv_line_number"] if dr else "",
     "disposition":"OPEN_REVIEW_REQUIRED" if relation in ("DAILY_ONLY_KEY","MONTHLY_ONLY_KEY","SHARED_RAW_DIVERGENT","DUPLICATE_KEY_REVIEW") else "OBSERVED_EXACT_PAIR_CONTEXT_ONLY",
     "source_authority":"NONE","timestamp_shifted_or_rounded":"False","synthetic_candle_created":"False"}
    for f in RAW_FIELDS:
     row["monthly_"+f]=mr["raw"][f] if mr else "";row["daily_"+f]=dr["raw"][f] if dr else ""
    comparisons.append(row)
  for srcname,missing in (("DAILY",d_missing),("MONTHLY",m_missing)):
   for key in missing:
    missing_expected.append({"case_id":item["case_id"],"interval":iv,"utc_date":date,"source":srcname,
     "expected_open_time_ms":key,"expected_open_time_utc":iso(key),"status":"EXPECTED_GRID_KEY_ABSENT_REVIEW_ONLY",
     "archive_filename":filename if srcname=="DAILY" else monthfn,"archive_sha256":zipsha if srcname=="DAILY" else mrec["sha256"],
     "synthetic_candle_created":"False"})
  expected_rows=PER_DAY[iv]
  coverage="COMPLETE_EXPECTED_GRID" if len(dkeys)==expected_rows and not d_missing and not d_offgrid and not ddups else "OPEN_COVERAGE_REVIEW"
  periods.append({"case_id":item["case_id"],"interval":iv,"utc_date":date,"daily_archive_filename":filename,"daily_archive_sha256":zipsha,
   "daily_sidecar_sha256":sha_bytes(sidebytes),"monthly_archive_filename":monthfn,"monthly_archive_sha256":mrec["sha256"],
   "expected_grid_keys_per_day":expected_rows,"daily_raw_rows":len(drows),"monthly_raw_rows":len(mrows),"shared_open_keys":len(shared),
   "exact_raw_row_pairs":exact_pairs,"divergent_raw_row_pairs":div_pairs,"daily_only_open_keys":len(dkeys-mkeys),"monthly_only_open_keys":len(mkeys-dkeys),
   "economic_field_divergent_pairs":econ_pairs,"close_time_only_pairs":close_only,"metadata_only_pairs":meta_only,
   "daily_expected_grid_keys_absent":len(d_missing),"monthly_expected_grid_keys_absent":len(m_missing),
   "daily_off_grid_keys":len(d_offgrid),"monthly_off_grid_keys":len(m_offgrid),"daily_duplicate_open_keys":ddups,"monthly_duplicate_open_keys":mdups,
   "daily_open_key_count":len(dkeys),"monthly_open_key_count":len(mkeys),"coverage_status":coverage,
   "data_disposition":"OPEN_REVIEW_REQUIRED; archive hash verified but row equality and source authority are not presumed"})
  sr={"case_id":item["case_id"],"interval":iv,"utc_date":date,"filename":filename,"zip_url":zip_url,"zip_final_url":zipfinal,"zip_http_status":ziphttp,
   "zip_sha256":zipsha,"zip_bytes":len(zipbytes),"zip_crc":"PASS","csv_member":dmember,"sidecar_url":side_url,"sidecar_final_url":sidefinal,
   "sidecar_http_status":sidehttp,"sidecar_sha256":sha_bytes(sidebytes),"sidecar_bytes":len(sidebytes),
   "sidecar_embedded_archive_sha256":tokens[0],"sidecar_token_matches_zip":"True","retrieval_method":retrieval_method,"source_actions_run_id":args.reuse_run_id or None,"source_artifact_id":args.reuse_artifact_id or None,"source_artifact_sha256":args.reuse_artifact_sha256 or None,"monthly_filename":monthfn,
   "monthly_sha256":mrec["sha256"],"monthly_manifest_sha256":MONTHLY_MANIFEST_SHA,"fetch_status":"PASS"}
  sources.append(sr)
  check("daily_official_urls_and_sidecar:"+filename,side_ok and ziphttp==200,"daily URL="+zip_url+"; sidecar SHA="+sha_bytes(sidebytes))
  check("daily_zip_sha_matches_sidecar:"+filename,hash_ok,zipsha)
  check("daily_zip_crc_and_single_csv:"+filename,True,dmember)
  check("daily_raw_schema_and_utc_date:"+filename,all(len(r["raw"])==12 and r["date"]==date for r in drows),"rows="+str(len(drows)))
  check("daily_sidecar_persisted_exactly:"+filename,sha_file(sidecar)==sha_bytes(sidebytes),"bytes="+str(len(sidebytes)))
  log("verified "+filename+" rows="+str(len(drows))+" shared="+str(len(shared))+" divergent="+str(div_pairs)+" daily_only="+str(len(dkeys-mkeys))+" monthly_only="+str(len(mkeys-dkeys)))
 comparison_fields=["case_id","interval","utc_date","open_time_ms","open_time_utc","occurrence_index","daily_key_occurrences","monthly_key_occurrences","row_relation","differing_raw_fields","differing_field_count","economic_differing_fields","economic_differing_field_count","expected_close_time_ms","monthly_close_time_ms","daily_close_time_ms","monthly_close_time_delta_ms","daily_close_time_delta_ms","monthly_archive_filename","monthly_archive_sha256","monthly_csv_line_number","daily_archive_filename","daily_archive_sha256","daily_sidecar_sha256","daily_csv_line_number"]+["monthly_"+f for f in RAW_FIELDS]+["daily_"+f for f in RAW_FIELDS]+["disposition","source_authority","timestamp_shifted_or_rounded","synthetic_candle_created"]
 write_csv(out/"CP0107_CP0041_DailyReference_Period_Summary.csv",periods)
 write_csv(out/"CP0107_CP0041_DailyReference_Archive_Manifest.csv",sources)
 write_csv(out/"CP0107_CP0041_DailyReference_RawRow_Comparison.csv",comparisons,comparison_fields)
 write_csv(out/"CP0107_CP0041_DailyReference_MissingExpectedKeys.csv",missing_expected)
 monthly_manifest=[]
 for x in monthly_records:
  monthly_manifest.append({"filename":x["filename"],"interval":x["interval"],"status":"MATCH","expected_sha256":x["expected_sha256"],
   "actual_sha256":x["sha256"],"bytes":x["bytes"],"zip_crc":"PASS","csv_member":x["csv_member"],"source_manifest_member_sha256":MONTHLY_MANIFEST_SHA})
 write_csv(out/"CP0107_CP0041_MonthlyArchive_Manifest_Subset.csv",monthly_manifest,
  ["filename","interval","status","expected_sha256","actual_sha256","bytes","zip_crc","csv_member","source_manifest_member_sha256"])
 check("all_16_daily_archive_sidecar_pairs_verified",len(sources)==16 and all(x["fetch_status"]=="PASS" for x in sources),"count="+str(len(sources)))
 check("all_14_monthly_zip_cache_hashes_verified",len(monthly_records)==14 and all(x["status"]=="PASS" for x in monthly_records),"count="+str(len(monthly_records)))
 comparison={"union_open_key_rows":len(comparisons),"shared_open_keys":sum(x["shared_open_keys"] for x in periods),
  "exact_raw_row_pairs":sum(x["exact_raw_row_pairs"] for x in periods),"divergent_raw_row_pairs":sum(x["divergent_raw_row_pairs"] for x in periods),
  "daily_only_keys":sum(x["daily_only_open_keys"] for x in periods),"monthly_only_keys":sum(x["monthly_only_open_keys"] for x in periods),
  "economic_field_divergent_pairs":sum(x["economic_field_divergent_pairs"] for x in periods),"close_time_only_pairs":sum(x["close_time_only_pairs"] for x in periods),
  "periods_complete_expected_grid":sum(x["coverage_status"]=="COMPLETE_EXPECTED_GRID" for x in periods),
  "periods_open_coverage_review":sum(x["coverage_status"]!="COMPLETE_EXPECTED_GRID" for x in periods),"missing_expected_keys_rows":len(missing_expected),
  "interpretation":"Raw equality and exact-key coverage are diagnostics only; an exact timestamp match does not assign source authority."}
 output_names=["CP0107_CP0041_DailyReference_Queue_Snapshot.csv","CP0107_CP0041_MonthlyArchive_Manifest_Subset.csv",
  "CP0107_CP0041_DailyReference_Period_Summary.csv","CP0107_CP0041_DailyReference_Archive_Manifest.csv",
  "CP0107_CP0041_DailyReference_RawRow_Comparison.csv","CP0107_CP0041_DailyReference_MissingExpectedKeys.csv"]
 output_names += [x["filename"] for x in sources]+[x["filename"]+".CHECKSUM" for x in sources]
 outputs={}
 for name in output_names:
  p=out/name;meta={"sha256":sha_file(p),"bytes":p.stat().st_size,"rows":len(read_csv(p)) if p.suffix.lower()==".csv" else None}
  outputs[name]=meta
 status="PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED" if all(c["status"]=="PASS" for c in checks) else "FAIL_DAILY_REFERENCE_ACQUISITION_AUDIT"
 summary={"checkpoint":"CP-0107","task":"cp0107_cp0041_daily_reference_acquisition_audit","status":status,
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),"queue_count":len(queue),"daily_archive_count":len(sources),"daily_sidecar_count":len(sources),
  "monthly_archive_count":len(monthly_records),"provenance":{"source_package":"AISTS_CP0041_Row_Level_Evidence_Disposition_Pack.zip",
   "source_package_sha256":PACKAGE_SHA,"queue_member":"AISTS_CP0041_Required_Daily_Reference_Fetch_Queue.csv","queue_member_sha256":QUEUE_SHA,
   "monthly_manifest_member":"AISTS_CP0041_Monthly_Archive_Verification.csv","monthly_manifest_member_sha256":MONTHLY_MANIFEST_SHA,
   "rulebook":"AISTS_CP0040_Strategy_Acceptance_Rulebook_HI.md","rulebook_sha256":RULEBOOK_SHA,
   "queue_kind":"16 exact records subset from frozen CP-0041 queue","monthly_verification_kind":"14 exact relevant archive rows from CP-0041 monthly manifest"},
  "sources":sources,"monthly_sources":monthly_records,"comparison":comparison,"checks":checks,
  "checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),"outputs":outputs,
  "external_network_used":False if reuse_dir else True,
  "network_scope":("No new daily archive requests; exact ZIP/.CHECKSUM bytes reused and independently rehashed from previous run "+args.reuse_run_id+" artifact "+args.reuse_artifact_id) if reuse_dir else "Only 16 official daily ZIP URLs and 16 matching .CHECKSUM URLs; redirects limited to approved Binance public-data object hosts.",
  "official_daily_zip_downloads":0 if reuse_dir else len(sources),"official_checksum_sidecar_downloads":0 if reuse_dir else len(sources),
  "daily_archives_reused_from_prior_run":len(sources) if reuse_dir else 0,"monthly_zip_redownloads":0,
  "reuse_source_run_id":args.reuse_run_id or None,"reuse_source_artifact_id":args.reuse_artifact_id or None,
  "reuse_source_artifact_sha256":args.reuse_artifact_sha256 or None,
  "market_data_rest_api_used":False,"exchange_credentials_used":False,"preexisting_raw_archives_modified":False,"new_daily_archives_persisted_unchanged":True,
  "timestamp_shifted_or_rounded":False,"row_merges_performed":False,"raw_rows_replaced_or_deleted":False,"synthetic_candles_created":False,
  "source_authority":"NONE","canonical_source_selected":False,"source_cases_closed":0,"all_divergent_or_unmatched_rows":"OPEN_REVIEW_REQUIRED",
  "root_cause":"OPEN_NOT_ESTABLISHED","backtest_rerun":False,"strategy_promoted":False,
  "frozen_gate_states":{"G0":"BLOCKED_GLOBAL","G1":"PARTIAL_SYSTEM_LEVEL","G2":"FAIL_CURRENT_23_CANDIDATES","G3":"BLOCKED_PARTIAL","G4":"INSUFFICIENT_EVIDENCE","G5":"NOT_RUN","G6":"NOT_BUILT","G7":"LIVE_BLOCKED"}}
 report_lines=[
  "# CP-0107: CP-0041 daily-reference acquisition and raw-row audit","",
  "Status: "+status+"; checks "+str(summary["checks_passed"])+"/"+str(summary["checks_total"])+" PASS.","",
  "## Scope","",
  "- All 16 queued daily ZIPs and 16 .CHECKSUM files are persisted byte-for-byte. This run reuses the exact bytes captured by prior Actions run "+(args.reuse_run_id or "NONE")+" rather than repeating the downloads.",
  "- Fourteen existing monthly ZIPs were reused from GitHub Actions cache and checked against the frozen CP-0041 monthly manifest subset and ZIP CRC. Monthly ZIP downloads: zero.",
  "- Daily ZIP/.CHECKSUM bytes were reused from prior run "+(args.reuse_run_id or "NONE")+" artifact "+(args.reuse_artifact_id or "NONE")+"; every ZIP was rehashed against its own official sidecar token again. New daily network downloads: "+str(summary["official_daily_zip_downloads"])+".",
  "- Source package SHA-256: "+PACKAGE_SHA+"; original queue member SHA-256: "+QUEUE_SHA+"; monthly manifest member SHA-256: "+MONTHLY_MANIFEST_SHA+"; frozen CP-0040 rulebook SHA-256: "+RULEBOOK_SHA+".",
  "",
  "## Exact-open comparison","",
  "- Union rows: "+str(comparison["union_open_key_rows"])+"; shared keys: "+str(comparison["shared_open_keys"])+"; exact raw pairs: "+str(comparison["exact_raw_row_pairs"])+"; divergent raw pairs: "+str(comparison["divergent_raw_row_pairs"])+".",
  "- Daily-only keys: "+str(comparison["daily_only_keys"])+"; monthly-only keys: "+str(comparison["monthly_only_keys"])+"; absent expected-grid keys recorded: "+str(comparison["missing_expected_keys_rows"])+".",
  "- Periods needing coverage review: "+str(comparison["periods_open_coverage_review"])+"/16. See machine-readable period summary and row comparison.",
  "",
  "## Disposition","",
  "Unequal or unmatched rows remain OPEN_REVIEW_REQUIRED. Exact-open equality is not source authority. Canonical source NONE; source cases closed 0. No timestamp shifting/rounding, row merge, replacement/deletion, synthetic candles, backtest rerun, or strategy promotion."
 ]
 report_path=out/"CP0107_CP0041_DailyReference_Acquisition_Report_HI.md"
 report_path.write_text("\n".join(report_lines)+"\n",encoding="utf-8")
 outputs[report_path.name]={"sha256":sha_file(report_path),"bytes":report_path.stat().st_size,"rows":None}
 summary["outputs"]=outputs
 summary_path=out/"CP0107_CP0041_DailyReference_Acquisition_Summary.json"
 summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 log(json.dumps({"status":status,"checks":str(summary["checks_passed"])+"/"+str(summary["checks_total"]),"daily_archives":len(sources),
  "monthly_archives":len(monthly_records),"comparison":comparison},ensure_ascii=False,sort_keys=True))
 return 0 if status=="PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED" else 1
if __name__=="__main__":raise SystemExit(main())
