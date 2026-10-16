#!/usr/bin/env python3
"""Inspect the official GitHub kline-correction bundle against the frozen CP-0041 monthly archive names."""
from __future__ import annotations
import argparse,base64,csv,hashlib,io,json,re,shutil,zipfile
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
from urllib.request import Request,urlopen,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlparse

BLOB_URL="https://api.github.com/repos/binance/binance-public-data/git/blobs/90631298cf50ac2e1ee8372a087767b010d78a21"
EXPECTED_GIT_BLOB_SHA1="90631298cf50ac2e1ee8372a087767b010d78a21"
EXPECTED_BYTES=6653240
UPSTREAM_TREE_SHA="f446ce3812bd4e5521f21faecd4ae3c6460e49fc"
TARGET_INVENTORY_PATH="evidence/source_adjudication/CP0107_Official_Update_Target_Monthly_Archive_Filenames.csv"
TARGET_INVENTORY_SHA256="b1bce4a37f9ac416ef02d27f2af7aefcf2e08ebae8b2d918b08596a9ed700e2d"
SOURCE_PACKAGE_SHA256="23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc"
SOURCE_WORKLIST_SHA256="f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f"
SOURCE_MONTHLY_MANIFEST_SHA256="1fa5c6ff022d7ff10f293c55c9fb933599c16b3d5d68adc86f2a9425c1e16b65"
RULEBOOK_SHA256="5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
README_URL="https://github.com/binance/binance-public-data"
MAX_BUNDLE_BYTES=9_000_000
ALLOWED_HOSTS={"api.github.com"}

def sha256(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()
def log(s):print("[CP0107-OFFICIAL-UPDATE] "+s,flush=True)
class SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        old=urlparse(req.full_url);new=urlparse(newurl)
        if new.scheme!="https" or new.hostname not in ALLOWED_HOSTS or new.path!=old.path:
            raise HTTPError(newurl,code,"redirect outside the fixed official GitHub blob endpoint",headers,fp)
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch_github_blob()->tuple[bytes,str,str]:
    p=urlparse(BLOB_URL)
    if p.scheme!="https" or p.hostname!="api.github.com" or p.path!="/repos/binance/binance-public-data/git/blobs/"+EXPECTED_GIT_BLOB_SHA1:
        raise ValueError("Blob URL differs from the fixed official GitHub repository object")
    req=Request(BLOB_URL,headers={"Accept":"application/vnd.github.raw","X-GitHub-Api-Version":"2022-11-28",
                                  "User-Agent":"AISTS-CP0107-Official-Update-Provenance-Audit/1.0"})
    with build_opener(SameHostRedirect()).open(req,timeout=60) as response:
        final=response.geturl();content_type=response.headers.get("Content-Type","")
        data=response.read(MAX_BUNDLE_BYTES+1)
        status=getattr(response,"status",None)
    if status!=200:raise ValueError("Official GitHub blob fetch returned HTTP "+str(status))
    if len(data)>MAX_BUNDLE_BYTES:raise ValueError("Bundle exceeded bounded response size")
    if "json" in content_type.lower() or data.lstrip().startswith(b"{"):
        obj=json.loads(data.decode("utf-8"))
        if obj.get("sha")!=EXPECTED_GIT_BLOB_SHA1 or obj.get("encoding")!="base64":
            raise ValueError("GitHub JSON fallback did not identify the frozen blob and base64 encoding")
        data=base64.b64decode(obj["content"],validate=False)
        if len(data)!=int(obj.get("size",-1)):raise ValueError("Decoded GitHub blob size differs from returned metadata")
    return data,final,content_type
def read_targets(path:Path)->list[dict]:
    if not path.is_file():raise FileNotFoundError("Frozen CP-0041 target archive inventory absent: "+str(path))
    raw=path.read_bytes()
    if sha256(raw)!=TARGET_INVENTORY_SHA256:raise ValueError("Target monthly archive inventory SHA-256 mismatch")
    with path.open("r",encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
    if len(rows)!=33 or len({r["filename"] for r in rows})!=33:raise ValueError("Expected 33 unique frozen target monthly archive names")
    if any(r.get("source_pack_sha256")!=SOURCE_PACKAGE_SHA256 or r.get("source_member_sha256")!=SOURCE_MONTHLY_MANIFEST_SHA256 for r in rows):
        raise ValueError("Target inventory source package/member references differ from frozen CP-0041")
    return rows
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--repo-root",default=".")
    args=ap.parse_args()
    root=Path(args.repo_root).resolve();out=Path(args.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    # Publisher has frozen CP-0107 baseline row-count guards; carry forward the verified baseline files unchanged.
    baseline=root/"evidence/source_adjudication/CP0107_Run_38771142900"
    baseline_names=("CP0107_Feb2018_OffGrid_RawRows.csv","CP0107_Feb2018_DailyCoverage_RawRows.csv",
                    "CP0107_Feb2018_SourceVerification.csv","CP0107_Feb2018_SegmentCoverage.csv",
                    "CP0107_Feb2018_Extraction_Summary.json")
    for name in baseline_names:
        src=baseline/name
        if not src.is_file():raise FileNotFoundError("Verified CP-0107 baseline evidence missing: "+str(src))
        shutil.copy2(src,out/name)
    checks=[]
    def check(name,ok,detail):checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
    target_path=root/TARGET_INVENTORY_PATH
    targets=read_targets(target_path)
    check("frozen_cp0041_765_manifest_target_subset",len(targets)==33 and sha256(target_path.read_bytes())==TARGET_INVENTORY_SHA256,
          "33 distinct monthly ZIP names associated with CP-0041 worklist; inventory SHA-256="+TARGET_INVENTORY_SHA256)
    data,final_url,content_type=fetch_github_blob()
    check("fixed_official_github_blob_endpoint",urlparse(final_url).scheme=="https" and urlparse(final_url).hostname=="api.github.com",
          "URL="+final_url+"; content_type="+content_type)
    actual_git_sha=git_blob_sha1(data)
    check("official_git_blob_identity",actual_git_sha==EXPECTED_GIT_BLOB_SHA1,
          "expected="+EXPECTED_GIT_BLOB_SHA1+"; actual="+actual_git_sha)
    check("official_bundle_size",len(data)==EXPECTED_BYTES,"expected="+str(EXPECTED_BYTES)+"; actual="+str(len(data)))
    bundle_sha=sha256(data)
    bundle_path=out/"2022-08-08_kline_updates.zip"
    bundle_path.write_bytes(data)
    entries=[]
    member_content=[]
    with zipfile.ZipFile(io.BytesIO(data),"r") as z:
        bad=z.testzip()
        check("official_update_zip_crc",bad is None,"bad_member="+str(bad))
        infos=[x for x in z.infolist() if not x.is_dir()]
        for info in infos:
            blob=z.read(info.filename)
            basename=PurePosixPath(info.filename).name
            is_zip=basename.lower().endswith(".zip")
            entries.append({"member_name":info.filename,"basename":basename,"uncompressed_bytes":info.file_size,
                "compressed_bytes":info.compress_size,"crc32_hex":format(info.CRC,"08x"),
                "is_nested_zip":str(is_zip),"member_sha256":sha256(blob)})
            member_content.append((info.filename,basename,blob,is_zip))
    check("nonempty_update_inventory",len(entries)>0,"non_directory_members="+str(len(entries)))
    target_names={x["filename"] for x in targets}
    target_by_name={x["filename"]:x for x in targets}
    matches=[]
    for target in targets:
        name=target["filename"];expected=target["expected_sha256"]
        name_hits=[];sha_hits=[];member_digest_matches=[]
        for member_path,base,blob,is_zip in member_content:
            if base==name:
                digest=sha256(blob)
                name_hits.append({"member":member_path,"sha256":digest,"bytes":len(blob),
                    "matches_frozen_current_monthly_sha256":digest==expected,"kind":"EXACT_ARCHIVE_BASENAME"})
                if digest==expected:member_digest_matches.append(member_path)
            elif not is_zip and (b"\n" in blob or blob.lstrip().startswith((b"filename",b"file_path",b"path",b"Date,"))):
                if name.encode("utf-8") in blob:
                    name_hits.append({"member":member_path,"sha256":sha256(blob),"bytes":len(blob),
                        "matches_frozen_current_monthly_sha256":False,"kind":"TEXT_FILENAME_REFERENCE"})
                if expected.encode("ascii") in blob:
                    sha_hits.append({"member":member_path,"kind":"FROZEN_CURRENT_SHA256_TOKEN"})
            if expected.encode("ascii") in blob and not is_zip and not any(x["member"]==member_path for x in sha_hits):
                sha_hits.append({"member":member_path,"kind":"FROZEN_CURRENT_SHA256_TOKEN"})
        matches.append({
            "target_filename":name,"interval":target["interval"],"frozen_current_monthly_sha256":expected,
            "worklist_case_count":int(target["worklist_case_count"]),
            "exact_archive_member_name_hit_count":sum(x["kind"]=="EXACT_ARCHIVE_BASENAME" for x in name_hits),
            "text_filename_reference_hit_count":sum(x["kind"]=="TEXT_FILENAME_REFERENCE" for x in name_hits),
            "frozen_hash_token_hit_count":len(sha_hits),
            "archive_member_sha256_matches_frozen_current":bool(member_digest_matches),
            "member_name_hits_json":json.dumps(name_hits,sort_keys=True),
            "hash_token_hits_json":json.dumps(sha_hits,sort_keys=True),
            "source_disposition":"EVIDENCE_LINK_ONLY; no source-selection conclusion"
        })
    check("all_33_cp0041_target_names_checked",len(matches)==33,"target_names_checked="+str(len(matches)))
    all_output_rows=sum(1 for _ in entries)
    with (out/"CP0107_Official_Update_Package_Entry_Inventory.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(entries[0].keys()),lineterminator="\n");w.writeheader();w.writerows(entries)
    with (out/"CP0107_Official_Update_Package_Target_Matches.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(matches[0].keys()),lineterminator="\n");w.writeheader();w.writerows(matches)
    nested_zip_count=sum(x["is_nested_zip"]=="True" for x in entries)
    exact_member_hits=sum(x["exact_archive_member_name_hit_count"]>0 for x in matches)
    text_name_hits=sum(x["text_filename_reference_hit_count"]>0 for x in matches)
    hash_token_hits=sum(x["frozen_hash_token_hit_count"]>0 for x in matches)
    member_sha_current=sum(x["archive_member_sha256_matches_frozen_current"] for x in matches)
    checks_passed=sum(x["status"]=="PASS" for x in checks)
    status="PASS_OFFICIAL_UPDATE_PACKAGE_INSPECTED_SOURCE_AUTHORITY_OPEN" if checks_passed==len(checks) else "FAIL_OFFICIAL_UPDATE_PACKAGE_INSPECTION"
    output_names=["2022-08-08_kline_updates.zip","CP0107_Official_Update_Package_Entry_Inventory.csv","CP0107_Official_Update_Package_Target_Matches.csv"]
    output_manifest={}
    for name in output_names:
        p=out/name
        output_manifest[name]={"bytes":p.stat().st_size,"sha256":sha256(p.read_bytes()),
            "rows":sum(1 for _ in p.open("r",encoding="utf-8",newline=""))-1 if p.suffix.lower()==".csv" else None}
    summary={
      "checkpoint":"CP-0107","task":"cp0107_official_update_package_audit","status":status,
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),"checks":checks,"checks_passed":checks_passed,"checks_total":len(checks),
      "source":{"authority":"official Binance public-data GitHub repository","readme_url":README_URL,
        "blob_url":BLOB_URL,"correction_package_path":"updates/2022-08-08_kline_updates.zip","upstream_tree_sha":UPSTREAM_TREE_SHA,
        "official_git_blob_sha1":EXPECTED_GIT_BLOB_SHA1,"actual_git_blob_sha1":actual_git_sha,"bytes":len(data),
        "sha256":bundle_sha,"zip_crc":"PASS" if any(x["check_id"]=="official_update_zip_crc" and x["status"]=="PASS" for x in checks) else "FAIL",
        "fetch_route":"GitHub git-blob endpoint with raw media-type request; no Binance market-data endpoint"}
      ,"cp0041_target_inventory":{"path":TARGET_INVENTORY_PATH,"sha256":TARGET_INVENTORY_SHA256,"rows":len(targets),
        "source_pack_sha256":SOURCE_PACKAGE_SHA256,"source_monthly_manifest_member_sha256":SOURCE_MONTHLY_MANIFEST_SHA256}
      ,"package_inventory":{"member_count":len(entries),"nested_zip_member_count":nested_zip_count,
        "target_monthly_archive_names_checked":len(matches),"exact_archive_member_name_hits":exact_member_hits,
        "text_filename_reference_hits":text_name_hits,"frozen_current_sha_token_hits":hash_token_hits,
        "member_bytes_equal_frozen_current_sha":member_sha_current}
      ,"decision":{"monthly_daily_canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
        "archive_files_replaced_or_mutated":False,"timestamp_shifted_or_rounded":False,"rows_merged_replaced_or_deleted":False,
        "synthetic_candles_created":False,"backtest_rerun":False,"strategy_promoted":False,
        "interpretation":"A match can identify a version/update record only; it does not alone authorize canonical-source selection under CP-0040."}
      ,"gate_states":{"G0":"BLOCKED_GLOBAL","G1":"PARTIAL_SYSTEM_LEVEL","G2":"FAIL_CURRENT_23_CANDIDATES","G3":"BLOCKED_PARTIAL","G4":"INSUFFICIENT_EVIDENCE","G5":"NOT_RUN","G6":"NOT_BUILT","G7":"LIVE_BLOCKED"},
      "outputs":output_manifest}
    report=[
      "# CP-0107: official kline update package inventory audit","",
      "Status: "+status+"; checks "+str(checks_passed)+"/"+str(len(checks))+" PASS.","",
      "- Official GitHub blob object: "+EXPECTED_GIT_BLOB_SHA1+"; bytes "+str(len(data))+"; SHA-256 "+bundle_sha+"; ZIP CRC "+summary["source"]["zip_crc"]+".",
      "- Frozen CP-0041 target set: 33 distinct monthly archive filenames from the verified 765-row monthly manifest, cross-referenced to the 996-row worklist.",
      "- Update package member count: "+str(len(entries))+"; nested ZIP members: "+str(nested_zip_count)+".",
      "- Exact package-member basename hits for the 33 target monthly ZIP names: "+str(exact_member_hits)+"/33; text filename-reference hits: "+str(text_name_hits)+"/33; current frozen SHA token hits: "+str(hash_token_hits)+"/33; nested/member bytes equal current frozen SHA: "+str(member_sha_current)+"/33.",
      "",
      "## Decision","",
      "These are version/provenance diagnostics only. Do not assume daily beats monthly, or that a correction-bundle filename identifies the current canonical archive. Canonical source NONE; cases closed 0; root cause OPEN_NOT_ESTABLISHED. No Binance market-data REST API, no monthly/daily market ZIP acquisition, no raw edits, no backtest or strategy promotion."
    ]
    (out/"CP0107_Official_Update_Package_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    output_manifest["CP0107_Official_Update_Package_Report_HI.md"]={"bytes":(out/"CP0107_Official_Update_Package_Report_HI.md").stat().st_size,"sha256":sha256((out/"CP0107_Official_Update_Package_Report_HI.md").read_bytes()),"rows":None}
    summary["outputs"]=output_manifest
    (out/"CP0107_Official_Update_Package_Summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    log(json.dumps({"status":status,"checks":str(checks_passed)+"/"+str(len(checks)),"blob_sha1":actual_git_sha,"bundle_sha256":bundle_sha,
        "member_count":len(entries),"target_archives":len(matches),"exact_member_hits":exact_member_hits,"text_name_hits":text_name_hits,
        "frozen_sha_token_hits":hash_token_hits,"member_bytes_match_current_sha":member_sha_current},sort_keys=True))
    return 0 if status=="PASS_OFFICIAL_UPDATE_PACKAGE_INSPECTED_SOURCE_AUTHORITY_OPEN" else 1
if __name__=="__main__":raise SystemExit(main())
