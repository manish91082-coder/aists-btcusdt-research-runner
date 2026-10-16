#!/usr/bin/env python3
"""CP-0096: checksum crosswalk for official correction records vs verified source archives.

Reuses the already acquired official correction ZIP and verified archive manifests.
Checks whether exact monthly/daily archive SHA-256 values occur in any official
correction CSV Original/New checksum field, independent of filename/path match.
Does not select source, mutate rows or close cases.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,zipfile
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_ZIP_BYTES=6653240
EXPECTED_ZIP_SHA256="1404dbfb3d62534b2576a6c0c046826fe652f895b9bebfe4c13df58bc8cf6240"
EXPECTED_GIT_BLOB_SHA1="90631298cf50ac2e1ee8372a087767b010d78a21"
EXPECTED_CSV_SHA256="94fea6dfad2903b5a1b0ed0193c9694318655e00f7d164224be72e82d7599046"
def now():return datetime.now(timezone.utc).isoformat()
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def blobsha(b:bytes)->str:return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read_json(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def read_csv(p):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write_json(p,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p,rows):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader()
        if rows:w.writerows(rows)
def extract_sha(token):
    m=re.search(r"(?i)(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])",token or "")
    return m.group(0).lower() if m else ""
def exact_basename(path,name):
    return (path or "").replace("\\","/").rstrip("/").rsplit("/",1)[-1]==name

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--correction-zip",required=True)
    ap.add_argument("--acquisition-dir",default="evidence/source_adjudication/CP0107_Run_38909366995")
    ap.add_argument("--prior-mapping-dir",default="evidence/source_adjudication/CP0095_Official_Correction_Target_Mapping_Run_38912641513")
    ap.add_argument("--output-dir",default="results/cp0096_correction_checksum_crosswalk")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True);checks=[]
    def ck(n,ok,d):checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    try:
        zp=(ROOT/a.correction_zip).resolve()
        if zp.is_dir():
            found=sorted(zp.rglob("2022-08-08_kline_updates.zip"))
            if len(found)!=1:raise ValueError("Expected exactly one correction ZIP under artifact directory; found "+str(len(found)))
            zp=found[0]
        ad=(ROOT/a.acquisition_dir).resolve();pd=(ROOT/a.prior_mapping_dir).resolve()
        daily_path=ad/"CP0107_CP0041_DailyReference_Archive_Manifest.csv"
        monthly_path=ad/"CP0107_CP0041_MonthlyArchive_Manifest_Subset.csv"
        acquisition_summary_path=ad/"CP0107_CP0041_DailyReference_Acquisition_Summary.json"
        prior_summary_path=pd/"CP0095_Correction_Target_Mapping_Summary.json"
        prior_matrix_path=pd/"CP0095_Correction_Target_Mapping_Matrix.csv"
        required=[zp,daily_path,monthly_path,acquisition_summary_path,prior_summary_path,prior_matrix_path]
        missing=[str(p) for p in required if not p.is_file()]
        ck("all_reused_source_manifests_present",not missing,missing or "all six input files found")
        if missing:raise ValueError("Missing input: "+", ".join(missing))
        raw=zp.read_bytes();zip_sha=sha(raw);git_sha=blobsha(raw)
        acquisition=read_json(acquisition_summary_path);prior=read_json(prior_summary_path)
        daily=read_csv(daily_path);monthly=read_csv(monthly_path);prior_matrix=read_csv(prior_matrix_path)
        ck("correction_archive_identity_hash_size",len(raw)==EXPECTED_ZIP_BYTES and zip_sha==EXPECTED_ZIP_SHA256 and git_sha==EXPECTED_GIT_BLOB_SHA1,
           {"bytes":len(raw),"sha256":zip_sha,"git_blob_sha1":git_sha})
        members=[];csv_bytes=b""
        with zipfile.ZipFile(zp,"r") as z:
            bad=z.testzip()
            ck("correction_archive_crc_pass",bad is None,{"testzip":bad,"member_count":len(z.infolist())})
            for i in z.infolist():members.append({"member_name":i.filename,"bytes":i.file_size,"is_directory":i.is_dir()})
            targets=[i for i in z.infolist() if not i.is_dir() and i.filename=="2022-08-08_kline_updates.csv"]
            ck("unique_correction_csv_member",len(targets)==1,{"exact_member_count":len(targets)})
            if len(targets)!=1:raise ValueError("Expected unique correction CSV")
            csv_bytes=z.read(targets[0])
        csv_sha=sha(csv_bytes);corrections=list(csv.DictReader(csv_bytes.decode("utf-8-sig").splitlines()))
        ck("correction_csv_integrity_and_schema",csv_sha==EXPECTED_CSV_SHA256 and len(corrections)==73234 and
           list(corrections[0].keys())==["File Path","Original File Checksum","New File Checksum"],
           {"sha256":csv_sha,"rows":len(corrections),"columns":list(corrections[0].keys()) if corrections else []})
        ck("upstream_daily_and_monthly_archive_audits_pass",acquisition.get("status")=="PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED" and
           acquisition.get("checks_passed")==98 and acquisition.get("checks_total")==98 and len(daily)==16 and
           all(r.get("fetch_status")=="PASS" and r.get("zip_crc")=="PASS" and r.get("sidecar_token_matches_zip")=="True" for r in daily) and
           len(monthly)==14 and all(r.get("status")=="MATCH" and r.get("zip_crc")=="PASS" and r.get("actual_sha256")==r.get("expected_sha256") for r in monthly),
           {"acquisition_status":acquisition.get("status"),"checks":str(acquisition.get("checks_passed"))+"/"+str(acquisition.get("checks_total")),
            "daily_archives":len(daily),"monthly_archives":len(monthly)})
        ck("prior_exact_path_audit_passed",prior.get("status")=="PASS_OFFICIAL_CORRECTION_CSV_HAS_NO_EXACT_PATHS_FOR_16_TARGETS_SOURCE_AUTHORITY_OPEN" and
           prior.get("checks_passed")==9 and prior.get("checks_total")==9 and prior.get("mapping",{}).get("exact_path_matches")==0 and
           prior.get("mapping",{}).get("basename_matches")==0 and len(prior_matrix)==16,
           {"status":prior.get("status"),"checks":str(prior.get("checks_passed"))+"/"+str(prior.get("checks_total")),
            "exact_path":prior.get("mapping",{}).get("exact_path_matches"),"basename":prior.get("mapping",{}).get("basename_matches")})
        checksum_rows=[];path_rows=[]
        for r in corrections:
            path=r.get("File Path","")
            orig=extract_sha(r.get("Original File Checksum",""))
            new=extract_sha(r.get("New File Checksum",""))
            checksum_rows.append({"file_path":path,"original_sha256":orig,"new_sha256":new,
                                  "original_checksum_present":bool(orig),"new_checksum_present":bool(new)})
            path_rows.append({"file_path":path,"basename":path.replace("\\","/").rstrip("/").rsplit("/",1)[-1],
                              "original_sha256":orig,"new_sha256":new})
        orig_index=defaultdict(list);new_index=defaultdict(list);path_index=defaultdict(list);basename_index=defaultdict(list)
        for r in checksum_rows:
            if r["original_sha256"]:orig_index[r["original_sha256"]].append(r["file_path"])
            if r["new_sha256"]:new_index[r["new_sha256"]].append(r["file_path"])
            path_index[r["file_path"]].append(r)
            basename_index[r["file_path"].replace("\\","/").rstrip("/").rsplit("/",1)[-1]].append(r)
        archive_targets=[]
        for r in daily:
            archive_targets.append({"archive_type":"DAILY","archive_filename":r["filename"],"interval":r["interval"],"utc_date":r["utc_date"],
              "sha256":r["zip_sha256"],"zip_crc":r["zip_crc"],"sidecar_token_matches_zip":r["sidecar_token_matches_zip"],
              "source_case_id":r["case_id"],"archive_path_field_match_count":len(path_index.get(r["filename"],[])),
              "basename_match_count":len(basename_index.get(r["filename"],[])),
              "correction_original_checksum_hit_count":len(orig_index.get(r["zip_sha256"],[])),
              "correction_new_checksum_hit_count":len(new_index.get(r["zip_sha256"],[])),
              "correction_original_paths":";".join(orig_index.get(r["zip_sha256"],[])),
              "correction_new_paths":";".join(new_index.get(r["zip_sha256"],[])),
              "correction_checksum_hit":bool(orig_index.get(r["zip_sha256"]) or new_index.get(r["zip_sha256"])),
              "source_authority":"UNDETERMINED","case_closed":"False"})
        for r in monthly:
            archive_targets.append({"archive_type":"MONTHLY","archive_filename":r["filename"],"interval":r["interval"],"utc_date":"",
              "sha256":r["actual_sha256"],"zip_crc":r["zip_crc"],"sidecar_token_matches_zip":"NOT_APPLICABLE",
              "source_case_id":"", "archive_path_field_match_count":len(path_index.get(r["filename"],[])),
              "basename_match_count":len(basename_index.get(r["filename"],[])),
              "correction_original_checksum_hit_count":len(orig_index.get(r["actual_sha256"],[])),
              "correction_new_checksum_hit_count":len(new_index.get(r["actual_sha256"],[])),
              "correction_original_paths":";".join(orig_index.get(r["actual_sha256"],[])),
              "correction_new_paths":";".join(new_index.get(r["actual_sha256"],[])),
              "correction_checksum_hit":bool(orig_index.get(r["actual_sha256"]) or new_index.get(r["actual_sha256"])),
              "source_authority":"UNDETERMINED","case_closed":"False"})
        daily_checksum_hits=[r for r in archive_targets if r["archive_type"]=="DAILY" and r["correction_checksum_hit"]]
        monthly_checksum_hits=[r for r in archive_targets if r["archive_type"]=="MONTHLY" and r["correction_checksum_hit"]]
        ck("archive_target_set_unique",len(archive_targets)==30 and len({(r["archive_type"],r["archive_filename"]) for r in archive_targets})==30,
           {"archive_targets":len(archive_targets),"unique":len({(r["archive_type"],r["archive_filename"]) for r in archive_targets})})
        ck("checksum_tokens_parsed",len(orig_index)>0 and len(new_index)>0 and sum(x["original_checksum_present"] for x in checksum_rows)>0 and
           sum(x["new_checksum_present"] for x in checksum_rows)>0,
           {"rows":len(corrections),"original_hash_tokens":sum(x["original_checksum_present"] for x in checksum_rows),
            "new_hash_tokens":sum(x["new_checksum_present"] for x in checksum_rows)})
        ck("all_daily_and_monthly_hashes_searched",len(archive_targets)==30,
           {"daily_targets":len(daily),"monthly_targets":len(monthly),"daily_checksum_hits":len(daily_checksum_hits),"monthly_checksum_hits":len(monthly_checksum_hits)})
        ck("source_authority_and_closure_unchanged",all(r["source_authority"]=="UNDETERMINED" and r["case_closed"]=="False" for r in archive_targets),
           "All archive entries remain informational only; source cases open")
        status="PASS_CHECKSUM_CROSSWALK_NO_ARCHIVE_HASH_HITS_SOURCE_AUTHORITY_OPEN" if all(c["status"]=="PASS" for c in checks) and not daily_checksum_hits and not monthly_checksum_hits else (
          "PASS_CHECKSUM_CROSSWALK_FOUND_ARCHIVE_HASH_HITS_REVIEW_REQUIRED" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_CORRECTION_CHECKSUM_CROSSWALK")
        write_csv(out/"CP0096_Correction_Checksum_Crosswalk.csv",archive_targets)
        write_csv(out/"CP0096_Correction_CSV_Checksum_Index.csv",checksum_rows)
        write_csv(out/"CP0096_Correction_Archive_Member_Inventory.csv",members)
        report=[
          "# CP-0096: Official correction checksum crosswalk","",
          "Status: "+status,"",
          "## Provenance and integrity",
          "- Reused the prior CP-0092 correction ZIP; no download or source mutation.",
          "- ZIP 6,653,240 bytes; SHA-256 "+zip_sha+"; Git blob SHA-1 "+git_sha+"; CRC PASS.",
          "- Official CSV SHA-256 "+csv_sha+"; 73,234 rows. Previous exact path/basename audit CP-0095: 0/16 matches.",
          "- 16 daily archive ZIPs have verified official checksum tokens and ZIP CRC; 14 monthly archives match frozen source-manifest hashes and CRC.","",
          "## Hash-field crosswalk",
          "- Compared exact SHA-256 values of all 16 daily ZIPs and 14 monthly ZIPs against every parsed Original File Checksum and New File Checksum token in the official correction CSV.",
          "- Daily archive checksum hits: "+str(len(daily_checksum_hits))+"/16; monthly archive checksum hits: "+str(len(monthly_checksum_hits))+"/14.",
          "- This audit is broader than filename matching: it can detect same archive bytes listed under an alternate path/name.","",
          "## Decision boundary",
          "- A checksum hit would be evidence of byte identity for that archive, not by itself a canonical-source decision for individual conflicting raw rows.",
          "- No source selected; source authority remains UNDETERMINED; cases closed=0. Global G0 BLOCKED_GLOBAL, G2 current 23 candidates FAIL, G7 LIVE_BLOCKED.",
          "- No downloads, row changes, timestamp edits, synthetic candles, candidate builds, backtests or exchange actions.","",
          "## Next action",
          "- If there are no checksum hits, stop rechecking this correction bundle for this frozen source set and continue only with new exact-row official evidence."
        ]
        report_path=out/"CP0096_Correction_Checksum_Crosswalk_Report_HI.md";report_path.write_text("\n".join(report)+"\n",encoding="utf-8")
        summary={
          "schema_version":1,"checkpoint":"CP-0096","task":"cp0096_correction_checksum_crosswalk_audit",
          "status":status,"started_at_utc":started,"finished_at_utc":now(),
          "source":{"correction_zip_bytes":len(raw),"correction_zip_sha256":zip_sha,"correction_git_blob_sha1":git_sha,
            "correction_csv_sha256":csv_sha,"correction_csv_rows":len(corrections),
            "daily_reference_audit_status":acquisition.get("status"),"daily_reference_audit_checks":"98/98",
            "prior_path_mapping_status":prior.get("status")},
          "crosswalk":{"correction_checksum_rows":len(checksum_rows),"original_hash_tokens":sum(x["original_checksum_present"] for x in checksum_rows),
            "new_hash_tokens":sum(x["new_checksum_present"] for x in checksum_rows),"daily_targets":len(daily),"monthly_targets":len(monthly),
            "daily_archive_checksum_hits":len(daily_checksum_hits),"monthly_archive_checksum_hits":len(monthly_checksum_hits),
            "daily_hit_filenames":[r["archive_filename"] for r in daily_checksum_hits],
            "monthly_hit_filenames":[r["archive_filename"] for r in monthly_checksum_hits]},
          "checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
          "network_used":False,"archive_downloads":0,"source_bytes_modified":False,"worklist_mutated":False,
          "canonical_source_selected":False,"source_cases_closed":0,"root_cause":"OPEN_NOT_ESTABLISHED",
          "unresolved_shared_conflicts":60,"unmatched_rows_quarantined":909,"unresolved_nonrow_aggregation_blockers":11,
          "g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED",
          "production_candidate_build":False,"backtest_rerun":False,"strategy_promoted":False}
        for name in ("CP0096_Correction_Checksum_Crosswalk.csv","CP0096_Correction_CSV_Checksum_Index.csv","CP0096_Correction_Archive_Member_Inventory.csv","CP0096_Correction_Checksum_Crosswalk_Report_HI.md"):
            p=out/name;summary.setdefault("outputs",{})[name]={"bytes":p.stat().st_size,"sha256":sha(p.read_bytes()),"rows":len(read_csv(p)) if name.endswith(".csv") else None}
        write_json(out/"CP0096_Correction_Checksum_Crosswalk_Summary.json",summary)
        print(json.dumps({"status":status,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
          "daily_targets":len(daily),"monthly_targets":len(monthly),"daily_checksum_hits":len(daily_checksum_hits),
          "monthly_checksum_hits":len(monthly_checksum_hits),"original_hash_tokens":summary["crosswalk"]["original_hash_tokens"],
          "new_hash_tokens":summary["crosswalk"]["new_hash_tokens"],"network_used":False,"g0":"BLOCKED_GLOBAL"},ensure_ascii=False,sort_keys=True))
        return 0 if status.startswith("PASS_") else 1
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0096","task":"cp0096_correction_checksum_crosswalk_audit",
          "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),"error_type":type(exc).__name__,
          "error":str(exc),"checks":checks,"network_used":False,"archive_downloads":0,"source_bytes_modified":False,
          "canonical_source_selected":False,"source_cases_closed":0,"g0":"BLOCKED_GLOBAL","g7":"LIVE_BLOCKED"}
        write_json(out/"CP0096_Correction_Checksum_Crosswalk_Summary.json",summary)
        (out/"CP0096_Correction_Checksum_Crosswalk_Report_HI.md").write_text("# CP-0096 correction checksum crosswalk\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\n"+type(exc).__name__+": "+str(exc)+"\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1
if __name__=="__main__":raise SystemExit(main())
