#!/usr/bin/env python3
"""CP-0103: cache-only source adjudication diagnostics for frozen AISTS conflicts.

Reads already checksum-verified Binance downloadable archive caches. It never downloads ZIP
market data, edits raw archives, shifts timestamps, selects a canonical source, closes a case,
or reruns/promotes strategies. It fetches only official .CHECKSUM sidecars for the 24 target
monthly ZIPs to establish byte provenance; daily ZIP sidecars are already cached.
"""
from __future__ import annotations
import argparse, bisect, csv, hashlib, io, json, re, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

SYMBOL="BTCUSDT"
INTERVALS=("5m","15m","30m","1h","4h","1d")
STEP_MS={"5m":300_000,"15m":900_000,"30m":1_800_000,"1h":3_600_000,"4h":14_400_000,"1d":86_400_000}
COMPARE_FIELDS=("open","high","low","close","volume","close_time","quote_asset_volume",
                "number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume")
VALUE_FIELDS=("open","high","low","close","volume","quote_asset_volume","number_of_trades",
              "taker_buy_base_asset_volume","taker_buy_quote_asset_volume")
TARGET_DATES=("2017-09-06","2018-02-08","2018-02-09","2018-02-10","2018-02-11","2019-11-25","2020-12-21")
USER_AGENT="AISTS-CP0103-Source-Adjudication-Diagnostic/1.0"
OFFICIAL_REDIRECT_HOSTS={
 "data.binance.vision","s3.amazonaws.com","s3-ap-northeast-1.amazonaws.com",
 "s3.ap-northeast-1.amazonaws.com","s3.dualstack.ap-northeast-1.amazonaws.com",
 "data.binance.vision.s3.amazonaws.com","data.binance.vision.s3-ap-northeast-1.amazonaws.com",
 "data.binance.vision.s3.ap-northeast-1.amazonaws.com"
}

def now_utc(): return datetime.now(timezone.utc).isoformat()
def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def sha256_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def normalize_epoch(raw):
    n=int(str(raw).strip())
    return n//1000 if n>=100_000_000_000_000 else n
def utc_dt(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc)
def utc_iso(ms): return utc_dt(ms).isoformat()
def utc_day(ms): return utc_dt(ms).date().isoformat()
def nearest_grid_delta(ms,step):
    rem=ms%step
    return rem if rem*2<=step else rem-step
def grid_neighbors(ms,step):
    floor=(ms//step)*step
    ceil=floor if ms==floor else floor+step
    rem=ms-floor
    return floor,ceil,rem,nearest_grid_delta(ms,step)

def official_object_path_ok(url, original_path=None):
    p=urlparse(url)
    if p.scheme!="https" or p.username or p.password or p.fragment or p.port not in (None,443):
        return False
    if not (p.path.endswith(".zip") or p.path.endswith(".zip.CHECKSUM")):
        return False
    if p.hostname=="data.binance.vision":
        return p.path.startswith("/data/spot/")
    if p.hostname in OFFICIAL_REDIRECT_HOSTS and original_path:
        return p.path in {original_path,"/data.binance.vision"+original_path}
    return False
class OfficialRedirect(HTTPRedirectHandler):
    def __init__(self,original_path): super().__init__(); self.original_path=original_path
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not official_object_path_ok(newurl,self.original_path):
            raise HTTPError(newurl,code,"Redirect outside official archive/checksum path allowlist",headers,fp)
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def official_get(url,timeout=25):
    original=urlparse(url)
    if original.hostname!="data.binance.vision" or not official_object_path_ok(url):
        raise ValueError("Blocked non-official Binance downloadable object URL")
    with build_opener(OfficialRedirect(original.path)).open(Request(url,headers={"User-Agent":USER_AGENT}),timeout=timeout) as r:
        final=r.geturl()
        if not official_object_path_ok(final,original.path):
            raise ValueError("Final URL failed official host/path validation")
        return r.status,r.read()
def parse_checksum(payload,filename):
    text=payload.decode("utf-8",errors="replace").strip()
    hashes=sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b",text)))
    if len(hashes)!=1: raise ValueError(f"Expected one SHA-256 token; found {len(hashes)}")
    if filename not in text: raise ValueError("Official checksum sidecar is not bound to the requested filename")
    return hashes[0],text

def zip_inventory(path):
    with zipfile.ZipFile(path,"r") as z:
        bad=z.testzip()
        files=[x for x in z.infolist() if not x.is_dir()]
        csvs=[x.filename for x in files if x.filename.lower().endswith(".csv")]
        if bad: raise ValueError(f"ZIP CRC failure in {bad}")
        if len(files)!=1 or len(csvs)!=1: raise ValueError(f"Expected one CSV member; files={len(files)}, csvs={len(csvs)}")
        return csvs[0]

def parse_candle(row,line_no,member):
    if len(row)<12: raise ValueError(f"short row: {len(row)} fields")
    t=normalize_epoch(row[0]); c=normalize_epoch(row[6])
    d={"open_time_ms":t,"close_time_ms":c,"open_time_raw":str(row[0]),"close_time_raw":str(row[6]),
       "line_number":line_no,"inner_csv":member,"raw_row":row[:12]}
    for col,name in [(1,"open"),(2,"high"),(3,"low"),(4,"close"),(5,"volume"),(7,"quote_asset_volume"),
                     (9,"taker_buy_base_asset_volume"),(10,"taker_buy_quote_asset_volume")]:
        d[name]=Decimal(str(row[col]).strip())
        if not d[name].is_finite(): raise ValueError(f"non-finite {name}")
    d["number_of_trades"]=int(str(row[8]).strip())
    d["ignore"]=str(row[11])
    return d

def read_zip_day(path,day):
    member=zip_inventory(path)
    out={}
    duplicate=0
    with zipfile.ZipFile(path,"r") as z:
        with z.open(member,"r") as raw:
            for line_no,row in enumerate(csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline="")),1):
                if not row: continue
                c=parse_candle(row,line_no,member)
                if utc_day(c["open_time_ms"])!=day: continue
                key=c["open_time_ms"]
                if key in out: duplicate+=1
                else: out[key]=c
    return out,duplicate,member

def verify_daily_zip(cache_root,interval,day):
    filename=f"{SYMBOL}-{interval}-{day}.zip"
    folder=cache_root/interval
    candidates=[folder/filename]
    candidates+=sorted(folder.glob(filename+".*.verified"))
    path=next((p for p in candidates if p.is_file()),None)
    if path is None: raise FileNotFoundError(f"Verified daily cache archive missing: {folder/filename}")
    side=path.with_suffix(path.suffix+".CHECKSUM")
    if not side.is_file(): raise FileNotFoundError(f"Cached daily sidecar missing: {side}")
    text=side.read_text(encoding="utf-8",errors="replace")
    hashes=sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b",text)))
    if len(hashes)!=1 or filename not in text: raise ValueError(f"Daily .CHECKSUM filename/hash binding invalid for {filename}")
    actual=sha256_file(path)
    if actual!=hashes[0]: raise ValueError(f"Daily ZIP hash mismatch for {filename}")
    member=zip_inventory(path)
    return path,side,actual,sha256_file(side),member

def verify_monthly_zip(cache_root,interval,day,timeout=25):
    year,month=map(int,day[:7].split("-"))
    filename=f"{SYMBOL}-{interval}-{year:04d}-{month:02d}.zip"
    path=cache_root/interval/f"{year:04d}-{month:02d}"/filename
    if not path.is_file(): raise FileNotFoundError(f"Verified monthly cache archive missing: {path}")
    rel=f"/monthly/klines/{SYMBOL}/{interval}/{filename}"
    url="https://data.binance.vision/data/spot"+rel+".CHECKSUM"
    _,payload=official_get(url,timeout)
    official,text=parse_checksum(payload,filename)
    actual=sha256_file(path)
    if actual!=official: raise ValueError(f"Monthly ZIP hash mismatch for {filename}")
    member=zip_inventory(path)
    return path,actual,sha256_bytes(payload),member,url,official

def write_csv(path,rows,fields=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    if fields is None: fields=list(dict.fromkeys(k for r in rows for k in r))
    if not fields: fields=["status","note"]
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k:(json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(dict,list,tuple)) else v) for k,v in r.items()})

def source_mismatch_fields(a,b):
    out=[]
    for key in COMPARE_FIELDS:
        av=a["close_time_ms"] if key=="close_time" else a[key]
        bv=b["close_time_ms"] if key=="close_time" else b[key]
        if av!=bv: out.append(key)
    return out
def nearest_opposite(timestamp,other_keys):
    if not other_keys: return None,None
    i=bisect.bisect_left(other_keys,timestamp)
    options=[]
    if i<len(other_keys): options.append(other_keys[i])
    if i>0: options.append(other_keys[i-1])
    key=min(options,key=lambda x:(abs(x-timestamp),x))
    return key,timestamp-key
def aggregate_children(children,parent_ms,interval):
    step=STEP_MS[interval]
    expected_n=step//STEP_MS["5m"]
    expected_keys=[parent_ms+i*STEP_MS["5m"] for i in range(expected_n)]
    keyed={r["open_time_ms"]:r for r in children}
    missing=[x for x in expected_keys if x not in keyed]
    if missing: return None,expected_n,missing
    bars=[keyed[x] for x in expected_keys]
    agg={"open":bars[0]["open"],"high":max(x["high"] for x in bars),"low":min(x["low"] for x in bars),
         "close":bars[-1]["close"],"close_time_ms":parent_ms+step-1,
         "volume":sum((x["volume"] for x in bars),Decimal("0")),
         "quote_asset_volume":sum((x["quote_asset_volume"] for x in bars),Decimal("0")),
         "number_of_trades":sum(x["number_of_trades"] for x in bars),
         "taker_buy_base_asset_volume":sum((x["taker_buy_base_asset_volume"] for x in bars),Decimal("0")),
         "taker_buy_quote_asset_volume":sum((x["taker_buy_quote_asset_volume"] for x in bars),Decimal("0"))}
    return agg,expected_n,[]

def self_tests():
    tests=[]
    def add(n,ok,detail=""): tests.append({"test":n,"status":"PASS" if ok else "FAIL","detail":detail})
    add("interval_step_registry",set(STEP_MS)==set(INTERVALS) and all(v>0 for v in STEP_MS.values()))
    add("grid_exact",nearest_grid_delta(600000,300000)==0)
    add("grid_after_floor",nearest_grid_delta(794789,300000)==-105211)
    floor,ceil,rem,near=grid_neighbors(794789,300000)
    add("grid_neighborhood_explicit_no_rounding",floor==600000 and ceil==900000 and rem==194789 and near==-105211)
    add("target_date_count",len(TARGET_DATES)==7)
    return {"passed":sum(t["status"]=="PASS" for t in tests),"total":len(tests),"tests":tests}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--monthly-cache",required=True)
    ap.add_argument("--daily-cache",required=True)
    ap.add_argument("--output-dir",required=True)
    args=ap.parse_args()
    monthly_cache=Path(args.monthly_cache).resolve()
    daily_cache=Path(args.daily_cache).resolve()
    out=Path(args.output_dir).resolve()
    out.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc)
    tests=self_tests()
    (out/"CP0103_Self_Tests.json").write_text(json.dumps(tests,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    archive_rows=[]; monthly_meta={}; verified_daily={}; errors=[]
    month_targets=sorted({(iv,day[:7]) for day in TARGET_DATES for iv in INTERVALS})
    month_dates_by_key={(iv,ym):next(day for day in TARGET_DATES if day[:7]==ym) for iv,ym in month_targets}
    def verify_month(item):
        iv,ym=item
        return item,verify_monthly_zip(monthly_cache,iv,month_dates_by_key[item])
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(verify_month,k):k for k in month_targets}
        for fut in as_completed(futures):
            iv,ym=futures[fut]
            try:
                key,result=fut.result()
                path,actual,side_hash,member,url,official=result
                monthly_meta[key]=(path,actual,side_hash,member,url,official)
                archive_rows.append({"source":"MONTHLY","interval":iv,"period":ym,"filename":path.name,"archive_path":str(path),
                    "zip_sha256":actual,"official_sha256":official,"checksum_sidecar_sha256":side_hash,"zip_crc":"PASS","csv_member":member,"status":"PASS"})
            except Exception as exc:
                errors.append({"source":"MONTHLY","interval":iv,"period":ym,"error":f"{type(exc).__name__}: {exc}"})
                archive_rows.append({"source":"MONTHLY","interval":iv,"period":ym,"filename":f"{SYMBOL}-{iv}-{ym}.zip",
                    "archive_path":"","zip_sha256":"","official_sha256":"","checksum_sidecar_sha256":"","zip_crc":"NOT_VERIFIED","csv_member":"","status":"FAIL","error":repr(exc)})
    for day in TARGET_DATES:
        for iv in INTERVALS:
            try:
                path,side,actual,side_hash,member=verify_daily_zip(daily_cache,iv,day)
                verified_daily[(iv,day)]=(path,actual,side_hash,member)
                archive_rows.append({"source":"DAILY","interval":iv,"period":day,"filename":path.name,"archive_path":str(path),
                    "zip_sha256":actual,"official_sha256":actual,"checksum_sidecar_sha256":side_hash,"zip_crc":"PASS","csv_member":member,"status":"PASS"})
            except Exception as exc:
                errors.append({"source":"DAILY","interval":iv,"period":day,"error":f"{type(exc).__name__}: {exc}"})
                archive_rows.append({"source":"DAILY","interval":iv,"period":day,"filename":f"{SYMBOL}-{iv}-{day}.zip",
                    "archive_path":"","zip_sha256":"","official_sha256":"","checksum_sidecar_sha256":"","zip_crc":"NOT_VERIFIED","csv_member":"","status":"FAIL","error":repr(exc)})
    write_csv(out/"CP0103_Source_Archive_Verification.csv",archive_rows)

    monthly_rows={}; daily_rows={}; monthly_duplicates={}; daily_duplicates={}
    if not errors:
        # Read each needed monthly archive once, preserving exact open-time integers and raw timestamp tokens.
        for iv,ym in month_targets:
            path=monthly_meta[(iv,ym)][0]
            member=monthly_meta[(iv,ym)][3]
            target_dates={d for d in TARGET_DATES if d[:7]==ym}
            rows={d:{} for d in target_dates}; dup_by_day={d:0 for d in target_dates}
            with zipfile.ZipFile(path,"r") as z:
                with z.open(member,"r") as raw:
                    for line_no,row in enumerate(csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline="")),1):
                        if not row: continue
                        candle=parse_candle(row,line_no,member)
                        day=utc_day(candle["open_time_ms"])
                        if day not in target_dates: continue
                        if candle["open_time_ms"] in rows[day]: dup_by_day[day]+=1
                        else: rows[day][candle["open_time_ms"]]=candle
            for day in target_dates: monthly_rows[(iv,day)]=rows[day]
            monthly_duplicates[(iv,ym)]=dup_by_day
        for day in TARGET_DATES:
            for iv in INTERVALS:
                daily_rows[(iv,day)],daily_duplicates[(iv,day)],_=read_zip_day(verified_daily[(iv,day)][0],day)

    summary_rows=[]; unmatched_rows=[]; mismatch_rows=[]; close_time_only=[]; feb_offsets={}
    raw_data_for_rollup={}
    if not errors:
        for day in TARGET_DATES:
            for iv in INTERVALS:
                step=STEP_MS[iv]; m=monthly_rows[(iv,day)]; d=daily_rows[(iv,day)]
                mk,dk=set(m),set(d); common=sorted(mk&dk); mo=sorted(mk-dk); do=sorted(dk-mk)
                value_mismatch=[(t,source_mismatch_fields(m[t],d[t])) for t in common]
                value_mismatch=[(t,fields) for t,fields in value_mismatch if fields]
                off_m=[t for t in mk if t%step!=0]; off_d=[t for t in dk if t%step!=0]
                summary_rows.append({"date":day,"interval":iv,"monthly_rows":len(m),"daily_rows":len(d),
                    "exact_open_key_matches":len(common),"value_mismatch_shared_keys":len(value_mismatch),
                    "monthly_only_rows":len(mo),"daily_only_rows":len(do),"monthly_off_grid_rows":len(off_m),
                    "daily_off_grid_rows":len(off_d),"monthly_duplicate_target_open_times":monthly_duplicates.get((iv,day[:7]),{}).get(day,0),
                    "daily_duplicate_target_open_times":daily_duplicates.get((iv,day),0),"status":"REVIEW_ONLY"})
                raw_data_for_rollup[(day,iv,"MONTHLY")]=m
                raw_data_for_rollup[(day,iv,"DAILY")]=d
                for t,fields in value_mismatch:
                    entry={"date":day,"interval":iv,"open_time_ms":t,"open_time_utc":utc_iso(t),
                        "monthly_open_time_raw":m[t]["open_time_raw"],"daily_open_time_raw":d[t]["open_time_raw"],
                        "different_fields":fields,"different_fields_json":json.dumps(fields),
                        "monthly_close_time_raw":m[t]["close_time_raw"],"daily_close_time_raw":d[t]["close_time_raw"],
                        "expected_close_time_utc":utc_iso(t+step-1),
                        "monthly_close_matches_expected":m[t]["close_time_ms"]==t+step-1,
                        "daily_close_matches_expected":d[t]["close_time_ms"]==t+step-1,
                        "monthly_close_delta_ms":m[t]["close_time_ms"]-(t+step-1),
                        "daily_close_delta_ms":d[t]["close_time_ms"]-(t+step-1)}
                    mismatch_rows.append(entry)
                    if fields==["close_time"]: close_time_only.append(entry)
                for side,keys,opposite in (("MONTHLY_ONLY",mo,sorted(dk)),("DAILY_ONLY",do,sorted(mk))):
                    current=m if side=="MONTHLY_ONLY" else d
                    other=d if side=="MONTHLY_ONLY" else m
                    for t in keys:
                        candle=current[t]; floor,ceil,rem,near=grid_neighbors(t,step)
                        near_key,delta=nearest_opposite(t,opposite)
                        near_candle=other.get(near_key) if near_key is not None else None
                        unmatched_rows.append({"date":day,"interval":iv,"source_side":side,"open_time_ms":t,
                            "open_time_raw":candle["open_time_raw"],"open_time_utc":utc_iso(t),"interval_ms":step,
                            "offset_after_floor_grid_ms":rem,"floor_grid_open_utc":utc_iso(floor),"ceil_grid_open_utc":utc_iso(ceil),
                            "signed_delta_to_nearest_grid_ms":near,"nearest_opposite_open_time_ms":near_key,
                            "nearest_opposite_open_time_utc":utc_iso(near_key) if near_key is not None else "",
                            "current_minus_nearest_opposite_ms":delta if delta is not None else "",
                            "nearest_opposite_open_time_raw":near_candle["open_time_raw"] if near_candle else "",
                            "nearest_is_exact_key":False,
                            "interpretation":"NEAREST-TIME DISPLAY ONLY; NOT A MATCH, SHIFT, ROUNDING OR SOURCE DECISION"})
                if day in ("2018-02-09","2018-02-10","2018-02-11"):
                    for t in mk:
                        k=(iv,t%step); feb_offsets[k]=feb_offsets.get(k,0)+1
    # CP-0104 follow-on diagnostic: compare exact economic signatures across unmatched keys.
    # Signatures exclude open_time and close_time. Candidate pairs never mutate data.
    feb_cluster_dates={"2018-02-09","2018-02-10","2018-02-11"}
    economic_fields=("open","high","low","close","volume","quote_asset_volume","number_of_trades",
                     "taker_buy_base_asset_volume","taker_buy_quote_asset_volume")
    sig_groups={}
    sig_payloads={}
    for item in unmatched_rows:
        iv=item["interval"]; day=item["date"]; side=item["source_side"]
        t=int(item["open_time_ms"])
        dataset="MONTHLY" if side=="MONTHLY_ONLY" else "DAILY"
        candle=raw_data_for_rollup[(day,iv,dataset)][t]
        signature=tuple(candle[field] for field in economic_fields)
        cluster="2018-02-09_TO_2018-02-11" if day in feb_cluster_dates else day
        key=(cluster,iv,signature)
        sig_groups.setdefault(key,{"MONTHLY_ONLY":[],"DAILY_ONLY":[]})
        sig_groups[key][side].append((item,candle))
        sig_payloads[key]=[
            format(candle[field].normalize(),"f") if isinstance(candle[field],Decimal) else str(candle[field])
            for field in economic_fields
        ]
    signature_candidate_rows=[]
    unique_signature_pairs=[]
    signature_summary={}
    for key,sides in sorted(sig_groups.items(),key=lambda kv:(kv[0][0],kv[0][1],str(kv[0][2]))):
        cluster,iv,signature=key
        monthly=sides["MONTHLY_ONLY"]
        daily=sides["DAILY_ONLY"]
        if len(monthly)==1 and len(daily)==1:
            status="UNIQUE_ECONOMIC_SIGNATURE_CANDIDATE"
            m_item,m_candle=monthly[0]
            d_item,d_candle=daily[0]
            delta=int(m_item["open_time_ms"])-int(d_item["open_time_ms"])
            unique_signature_pairs.append({
                "cluster":cluster,"interval":iv,
                "monthly_date":m_item["date"],"monthly_open_time_ms":int(m_item["open_time_ms"]),
                "monthly_open_time_utc":m_item["open_time_utc"],"monthly_open_time_raw":m_item["open_time_raw"],
                "daily_date":d_item["date"],"daily_open_time_ms":int(d_item["open_time_ms"]),
                "daily_open_time_utc":d_item["open_time_utc"],"daily_open_time_raw":d_item["open_time_raw"],
                "monthly_minus_daily_open_delta_ms":delta,
                "monthly_minus_daily_open_delta_seconds":Decimal(delta)/Decimal(1000),
                "economic_signature_sha256":sha256_bytes(json.dumps(sig_payloads[key],separators=(",",":")).encode()),
                "signature_fields":json.dumps(economic_fields),
                "pairing_status":status,
                "interpretation":"UNIQUE VALUE-SIGNATURE CANDIDATE ONLY; no timestamp shift, join, correction, or source-authority decision"
            })
        elif not monthly or not daily:
            status="NO_EXACT_ECONOMIC_SIGNATURE_MATCH"
        else:
            status="AMBIGUOUS_DUPLICATE_ECONOMIC_SIGNATURE"
        for side_name,entries,opposite in (("MONTHLY_ONLY",monthly,daily),("DAILY_ONLY",daily,monthly)):
            for item,candle in entries:
                candidate=opposite[0] if len(monthly)==1 and len(daily)==1 else None
                if side_name=="MONTHLY_ONLY":
                    candidate_date=candidate[0]["date"] if candidate else ""
                    candidate_time=candidate[0]["open_time_ms"] if candidate else ""
                    candidate_raw=candidate[0]["open_time_raw"] if candidate else ""
                    delta=int(item["open_time_ms"])-int(candidate[0]["open_time_ms"]) if candidate else ""
                else:
                    candidate_date=candidate[0]["date"] if candidate else ""
                    candidate_time=candidate[0]["open_time_ms"] if candidate else ""
                    candidate_raw=candidate[0]["open_time_raw"] if candidate else ""
                    delta=int(candidate[0]["open_time_ms"])-int(item["open_time_ms"]) if candidate else ""
                signature_candidate_rows.append({
                    "cluster":cluster,"interval":iv,"source_side":side_name,"date":item["date"],
                    "open_time_ms":int(item["open_time_ms"]),"open_time_utc":item["open_time_utc"],
                    "open_time_raw":item["open_time_raw"],
                    "economic_signature_sha256":sha256_bytes(json.dumps(sig_payloads[key],separators=(",",":")).encode()),
                    "own_signature_count":len(entries),"opposite_signature_count":len(opposite),
                    "pairing_status":status,"candidate_date":candidate_date,"candidate_open_time_ms":candidate_time,
                    "candidate_open_time_raw":candidate_raw,"monthly_minus_daily_open_delta_ms":delta,
                    "signature_fields":json.dumps(economic_fields),
                    "interpretation":"Exact numeric economic fields only; evidence candidate, not a source or timestamp decision"
                })
                skey=(cluster,iv,status)
                signature_summary[skey]=signature_summary.get(skey,0)+1
    signature_summary_rows=[
        {"cluster":cluster,"interval":iv,"pairing_status":status,"unmatched_row_count":count}
        for (cluster,iv,status),count in sorted(signature_summary.items())
    ]
    write_csv(out/"CP0103_Unmatched_Economic_Signature_Candidates.csv",signature_candidate_rows)
    write_csv(out/"CP0103_Unique_Economic_Signature_Pairs.csv",unique_signature_pairs)
    write_csv(out/"CP0103_Economic_Signature_Summary.csv",signature_summary_rows)
    write_csv(out/"CP0103_Date_Interval_Source_Reconciliation.csv",summary_rows)
    write_csv(out/"CP0103_Unmatched_Timestamp_Neighborhoods.csv",unmatched_rows)
    write_csv(out/"CP0103_Exact_Key_Value_Mismatches.csv",mismatch_rows)
    write_csv(out/"CP0103_CloseTime_Only_Review.csv",close_time_only)
    offset_rows=[{"interval":iv,"offset_after_floor_grid_ms":rem,"count":count,"interval_ms":STEP_MS[iv],
                  "offset_after_floor_grid_seconds":Decimal(rem)/Decimal(1000)}
                 for (iv,rem),count in sorted(feb_offsets.items())]
    write_csv(out/"CP0103_Feb2018_Offset_Histogram.csv",offset_rows)

    rollup_rows=[]
    if not errors:
        day="2020-12-21"
        children_by_source={src:raw_data_for_rollup[(day,"5m",src)] for src in ("MONTHLY","DAILY")}
        for parent_interval in ("15m","30m","1h"):
            pstep=STEP_MS[parent_interval]
            start=int(datetime(2020,12,21,12,0,tzinfo=timezone.utc).timestamp()*1000)
            end=int(datetime(2020,12,21,16,0,tzinfo=timezone.utc).timestamp()*1000)
            parents=[t for t in sorted(set(raw_data_for_rollup[(day,parent_interval,"MONTHLY")])|
                                       set(raw_data_for_rollup[(day,parent_interval,"DAILY")])) if start<=t<end]
            for source in ("MONTHLY","DAILY"):
                children=list(children_by_source[source].values())
                direct=raw_data_for_rollup[(day,parent_interval,source)]
                for parent_ms in parents:
                    agg,expected_n,missing=aggregate_children(children,parent_ms,parent_interval)
                    obs=direct.get(parent_ms); mismatch_fields=[]
                    if agg is not None and obs is not None:
                        for field in VALUE_FIELDS:
                            if agg[field]!=obs[field]: mismatch_fields.append(field)
                        if agg["close_time_ms"]!=obs["close_time_ms"]: mismatch_fields.append("close_time")
                    elif agg is None: mismatch_fields=["MISSING_CHILDREN"]
                    elif obs is None: mismatch_fields=["PARENT_ROW_MISSING"]
                    record={"date":day,"source":source,"parent_interval":parent_interval,
                        "parent_open_time_utc":utc_iso(parent_ms),"expected_child_5m_bars":expected_n,
                        "available_exact_child_5m_bars":expected_n-len(missing),
                        "missing_child_open_times_utc":[utc_iso(x) for x in missing],"parent_row_present":obs is not None,
                        "derived_aggregate_available":agg is not None,"aggregate_vs_direct_parent_mismatch_fields":mismatch_fields,
                        "aggregate_vs_direct_parent_mismatch_json":json.dumps(mismatch_fields),
                        "status":"EXACT_MATCH" if agg is not None and obs is not None and not mismatch_fields else "REVIEW_REQUIRED"}
                    if agg is not None:
                        for field in ("open","high","low","close","volume","number_of_trades","quote_asset_volume","taker_buy_base_asset_volume","taker_buy_quote_asset_volume"):
                            record["derived_"+field]=str(agg[field])
                    if obs:
                        for field in ("open","high","low","close","volume","number_of_trades","quote_asset_volume","taker_buy_base_asset_volume","taker_buy_quote_asset_volume"):
                            record["direct_"+field]=str(obs[field])
                        record["direct_close_time_raw"]=obs["close_time_raw"]
                        record["direct_close_time_utc"]=utc_iso(obs["close_time_ms"])
                        record["expected_close_time_utc"]=utc_iso(parent_ms+pstep-1)
                    rollup_rows.append(record)
    write_csv(out/"CP0103_2020_December_Rollup_Chain.csv",rollup_rows)

    all_sources_ok=bool(archive_rows) and all(r.get("status")=="PASS" for r in archive_rows)
    no_errors=not errors
    summary={"checkpoint":"CP-0103",
        "purpose":"Targeted source-adjudication diagnostics for February 2018 timestamp alignment, 2020-12-21 roll-up impact, and eight metadata-only close-time conflicts.",
        "started_at_utc":started.isoformat(),"finished_at_utc":now_utc(),
        "status":"PASS_DIAGNOSTICS_ONLY" if all_sources_ok and no_errors and tests["passed"]==tests["total"] else "BLOCKED_SOURCE_OR_READ_ERROR",
        "source_cache_only_for_zip_objects":True,"official_sidecar_metadata_requests_for_monthly_objects":len(month_targets),
        "monthly_archive_objects_expected":len(month_targets),"daily_archive_objects_expected":len(TARGET_DATES)*len(INTERVALS),
        "verified_archive_objects":sum(r.get("status")=="PASS" for r in archive_rows),"archive_errors":errors,
        "source_archive_manifest_rows":len(archive_rows),"target_dates":list(TARGET_DATES),"target_intervals":list(INTERVALS),
        "date_interval_comparison_rows":len(summary_rows),"unmatched_timestamp_rows_detail":len(unmatched_rows),
        "exact_key_value_mismatch_rows":len(mismatch_rows),"close_time_only_conflicts_detailed":len(close_time_only),
        "unmatched_economic_signature_rows":len(signature_candidate_rows),"unique_economic_signature_candidate_pairs":len(unique_signature_pairs),
        "economic_signature_pairing_status_counts":{status:sum(r["pairing_status"]==status for r in signature_candidate_rows) for status in ("UNIQUE_ECONOMIC_SIGNATURE_CANDIDATE","AMBIGUOUS_DUPLICATE_ECONOMIC_SIGNATURE","NO_EXACT_ECONOMIC_SIGNATURE_MATCH")},
        "feb2018_off_grid_residue_groups":sum(1 for (iv,rem) in feb_offsets if rem!=0),
        "feb2018_grid_aligned_residue_groups":sum(1 for (iv,rem) in feb_offsets if rem==0),
        "feb2018_all_residue_groups":len(offset_rows),"rollup_chain_rows":len(rollup_rows),
        "automatic_corrections_applied":0,"timestamp_rounding_or_shift_applied":False,"raw_archive_mutation":False,
        "canonical_source_selected":False,"source_cases_closed":0,"candidate_or_strategy_promoted":False,
        "backtest_rerun":False,"exchange_rest_api_used":False,"exchange_credentials_used":False,
        "live_order_or_signing":False,
        "interpretation":"Nearest-time offsets and roll-up checks are diagnostic evidence only. They do not prove source authority, excuse a mismatch, or authorize data correction.",
        "self_tests":tests}
    (out/"CP0103_Run_Summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    hashes=[]
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name!="CP0103_Report_SHA256.csv":
            hashes.append({"file":p.name,"bytes":p.stat().st_size,"sha256":sha256_file(p)})
    write_csv(out/"CP0103_Report_SHA256.csv",hashes,["file","bytes","sha256"])
    print(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True))
    return 0 if summary["status"]=="PASS_DIAGNOSTICS_ONLY" else 1

if __name__=="__main__":
    raise SystemExit(main())
