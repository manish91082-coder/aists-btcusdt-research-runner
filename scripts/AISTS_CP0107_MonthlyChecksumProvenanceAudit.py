#!/usr/bin/env python3
"""Fetch only official .CHECKSUM text files to close the CP-0107 sidecar evidence gap."""
from __future__ import annotations
import argparse,csv,hashlib,json,re,shutil,urllib.request,urllib.error
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
TARGETS=(
 {"source":"MONTHLY","interval":"5m","period":"2020-12","filename":"BTCUSDT-5m-2020-12.zip",
  "url":"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2020-12.zip.CHECKSUM",
  "sidecar_name":"BTCUSDT-5m-2020-12.zip.CHECKSUM"},
 {"source":"DAILY","interval":"5m","period":"2020-12-21","filename":"BTCUSDT-5m-2020-12-21.zip",
  "url":"https://data.binance.vision/data/spot/daily/klines/BTCUSDT/5m/BTCUSDT-5m-2020-12-21.zip.CHECKSUM",
  "sidecar_name":"BTCUSDT-5m-2020-12-21.zip.CHECKSUM"},
)
BASE_FILES=(
 "CP0107_Feb2018_Extraction_Summary.json","CP0107_Feb2018_OffGrid_RawRows.csv",
 "CP0107_Feb2018_DailyCoverage_RawRows.csv","CP0107_Feb2018_SegmentCoverage.csv",
 "CP0107_Feb2018_SourceVerification.csv","CP0107_Feb2018_Extraction_Report_HI.md","CP0107_Feb2018_Checks.csv",
 "CP0107_Dec2020_ChildWindow_Audit_Summary.json","CP0107_Dec2020_5m_ActualRows_Window.csv",
 "CP0107_Dec2020_5m_ChildCoverage.csv","CP0107_Dec2020_ReviewRollup_ChildCoverage.csv","CP0107_Dec2020_5m_SourceVerification.csv",
 "CP0107_Dec2020_FieldReview_Summary.json","CP0107_Dec2020_FieldReview_Report_HI.md",
 "CP0107_Dec2020_Shared_5m_RawField_Comparison.csv","CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv",
 "CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv",
)
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):return sha_bytes(Path(p).read_bytes())
def read_csv(p):
 with Path(p).open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write_text_bytes(path,b):
 Path(path).write_bytes(b)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source-dir",required=True);ap.add_argument("--manifest",required=True);ap.add_argument("--output-dir",required=True)
 a=ap.parse_args();src=ROOT/a.source_dir;manifest_path=ROOT/a.manifest;out=ROOT/a.output_dir
 out.mkdir(parents=True,exist_ok=True)
 for name in BASE_FILES:
  p=src/name
  if not p.is_file():raise FileNotFoundError("Previously committed evidence absent: "+str(p))
  shutil.copy2(p,out/name)
 manifests=read_csv(manifest_path)
 records=[]
 checks=[]
 def ck(name,ok,detail):checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
 for target in TARGETS:
  matches=[r for r in manifests if r.get("source")==target["source"] and r.get("interval")==target["interval"] and r.get("period")==target["period"] and r.get("filename")==target["filename"]]
  if len(matches)!=1:raise ValueError("Expected exactly one frozen CP-0106 manifest record for "+target["filename"])
  frozen=matches[0]
  if frozen.get("zip_sha256")!=frozen.get("official_sha256"):raise ValueError("Frozen zip/official SHA disagree for "+target["filename"])
  u=urlparse(target["url"])
  if u.scheme!="https" or u.hostname!="data.binance.vision":raise ValueError("URL not allowlisted")
  req=urllib.request.Request(target["url"],headers={"User-Agent":"AISTS-CP0107-SidecarAudit/1.0","Accept":"text/plain"})
  with urllib.request.urlopen(req,timeout=20) as response:
   final=urlparse(response.geturl())
   body=response.read(4097)
   http_status=getattr(response,"status",None)
  if final.scheme!="https" or final.hostname!="data.binance.vision":raise ValueError("Official checksum request redirected outside allowlisted HTTPS host")
  if http_status!=200:raise ValueError("Checksum HTTP status not 200 for "+target["filename"])
  if not body or len(body)>4096:raise ValueError("Unexpected sidecar size for "+target["filename"])
  text=body.decode("utf-8",errors="strict").strip()
  tokens=sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b",text)))
  token_match=len(tokens)==1 and tokens[0]==frozen["zip_sha256"].lower()
  name_match=target["filename"] in text
  sidecar_hash=sha_bytes(body)
  sidecar_manifest_match=sidecar_hash==frozen["checksum_sidecar_sha256"]
  sidecar_path=out/target["sidecar_name"]
  write_text_bytes(sidecar_path,body)
  re_read=sidecar_path.read_bytes()
  ck(target["source"]+"_official_host_http",final.hostname=="data.binance.vision" and final.scheme=="https" and http_status==200,target["url"])
  ck(target["source"]+"_content_names_target_archive",name_match,target["filename"] in text)
  ck(target["source"]+"_checksum_token_matches_frozen_archive_sha",token_match,tokens)
  ck(target["source"]+"_sidecar_sha_matches_frozen_manifest",sidecar_manifest_match,sidecar_hash)
  ck(target["source"]+"_persisted_sidecar_bytes_identical",re_read==body,len(body))
  rec={"source":target["source"],"interval":target["interval"],"period":target["period"],"filename":target["filename"],
   "url":target["url"],"final_url":response.geturl(),"http_status":http_status,"sidecar_name":target["sidecar_name"],
   "sidecar_content_utf8":text,"sidecar_bytes":len(body),"sidecar_sha256":sidecar_hash,
   "frozen_sidecar_sha256":frozen["checksum_sidecar_sha256"],"sidecar_manifest_sha_match":sidecar_manifest_match,
   "checksum_tokens":tokens,"frozen_archive_sha256":frozen["zip_sha256"],"official_archive_sha256":frozen["official_sha256"],
   "archive_sha_match":token_match,"archive_zip_downloaded":False,"market_data_rest_api_used":False,
   "fetch_status":"PASS" if name_match and token_match and sidecar_manifest_match else "FAIL"}
  records.append(rec)
 outputs={}
 for target in TARGETS:
  name=target["sidecar_name"];p=out/name
  outputs[name]={"sha256":sha_file(p),"bytes":p.stat().st_size,"content_exactly_fetched":True}
 status_ok=(len(records)==2 and all(r["fetch_status"]=="PASS" for r in records) and all(c["status"]=="PASS" for c in checks))
 summary={"checkpoint":"CP-0107","task":"cp0107_monthly_checksum_provenance_audit",
  "status":"PASS_OFFICIAL_SIDECAR_PROVENANCE" if status_ok else "FAIL_OFFICIAL_SIDECAR_PROVENANCE",
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),"source_count":len(records),"sources":records,
  "checks":checks,"checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),
  "outputs":outputs,"external_network_used":True,"network_scope":"Two HTTPS text-only .CHECKSUM files on data.binance.vision",
  "archive_zip_downloaded":False,"market_data_rest_api_used":False,"exchange_credentials_used":False,
  "raw_archives_modified":False,"timestamps_shifted_or_rounded":False,"synthetic_candles_created":False,
  "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
  "backtest_rerun":False,"strategy_promoted":False,
  "frozen_rule":"CP-0106 manifest sidecar SHA and archive SHA are references to verify, not automatic authority for row-level data acceptance."}
 (out/"CP0107_Monthly_Checksum_Provenance_Summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 report=[
  "# CP-0107: official .CHECKSUM provenance audit",
  "",
  "Status: "+summary["status"]+"; checks "+str(summary["checks_passed"])+"/"+str(summary["checks_total"])+".",
  "",
  "Only two official text .CHECKSUM URLs were requested from HTTPS host data.binance.vision. No ZIP archive was downloaded and no Binance market-data REST endpoint was called.",
  "",
  "| Source | Sidecar SHA-256 | Matches frozen sidecar hash | Embedded archive SHA matches manifest |",
  "|---|---|---|---|",
 ]
 for r in records:
  report.append("| "+r["source"]+" | "+r["sidecar_sha256"]+" | "+str(r["sidecar_manifest_sha_match"])+" | "+str(r["archive_sha_match"])+" |")
 report.extend(["","## Interpretation","",
  "A PASS confirms the fetched .CHECKSUM content exactly matches the recorded CP-0106 sidecar digest and its embedded archive hash matches the frozen official archive SHA. This authenticates this sidecar/archive hash linkage only; it does not adjudicate disputed kline rows or establish a canonical data source.",
  "Affected row dispositions remain OPEN; root cause OPEN; canonical source NONE; no backtest rerun or strategy promotion."])
 (out/"CP0107_Monthly_Checksum_Provenance_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
 print(json.dumps({"status":summary["status"],"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
  "sources":[{"source":x["source"],"sidecar_sha256":x["sidecar_sha256"],"manifest_match":x["sidecar_manifest_sha_match"],"archive_sha_match":x["archive_sha_match"]} for x in records]},ensure_ascii=False,sort_keys=True),flush=True)
 return 0 if status_ok else 1
if __name__=="__main__":raise SystemExit(main())
