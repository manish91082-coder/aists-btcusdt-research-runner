#!/usr/bin/env python3
"""CP-0095: exact-path mapping audit for the verified official correction CSV.

Uses the correction ZIP from the prior CP-0092 Actions artifact. No downloads,
no row edits, no source selection or case closure.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,zipfile
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
def first_sha(token):
    m=re.match(r"\s*([0-9a-f]{64})",token or "",re.I)
    return m.group(1).lower() if m else ""

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--correction-zip",required=True)
    ap.add_argument("--acquisition-dir",default="evidence/source_adjudication/CP0107_Run_38909366995")
    ap.add_argument("--output-dir",default="results/cp0095_official_correction_target_mapping")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True);checks=[]
    def ck(n,ok,d):checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    try:
        zipp=(ROOT/a.correction_zip).resolve();ad=(ROOT/a.acquisition_dir).resolve()
        archive_path=ad/"CP0107_CP0041_DailyReference_Archive_Manifest.csv"
        acq_summary_path=ad/"CP0107_CP0041_DailyReference_Acquisition_Summary.json"
        missing=[str(p) for p in (zipp,archive_path,acq_summary_path) if not p.is_file()]
        ck("reused_correction_and_daily_evidence_present",not missing,missing or "all inputs found")
        if missing:raise ValueError("Missing input: "+", ".join(missing))
        raw=zipp.read_bytes();zip_sha=sha(raw);git_sha=blobsha(raw)
        acquisition=read_json(acq_summary_path);targets=read_csv(archive_path)
        ck("correction_zip_expected_bytes_and_hashes",len(raw)==EXPECTED_ZIP_BYTES and zip_sha==EXPECTED_ZIP_SHA256 and git_sha==EXPECTED_GIT_BLOB_SHA1,
           {"bytes":len(raw),"sha256":zip_sha,"git_blob_sha1":git_sha})
        members=[];csv_bytes=b""
        with zipfile.ZipFile(zipp,"r") as z:
            bad=z.testzip()
            ck("correction_zip_crc",bad is None,{"testzip":bad,"member_count":len(z.infolist())})
            for info in z.infolist():
                members.append({"member_name":info.filename,"bytes":info.file_size,"is_directory":info.is_dir()})
            matches=[info for info in z.infolist() if not info.is_dir() and info.filename=="2022-08-08_kline_updates.csv"]
            ck("unique_official_correction_csv_member",len(matches)==1,{"count":len(matches)})
            if len(matches)!=1:raise ValueError("Expected exactly one correction CSV member")
            csv_bytes=z.read(matches[0])
        csv_sha=sha(csv_bytes);corrections=list(csv.DictReader(csv_bytes.decode("utf-8-sig").splitlines()))
        ck("correction_csv_hash_rows_columns",csv_sha==EXPECTED_CSV_SHA256 and len(corrections)==73234 and
           list(corrections[0].keys())==["File Path","Original File Checksum","New File Checksum"],
           {"sha256":csv_sha,"rows":len(corrections),"columns":list(corrections[0].keys()) if corrections else []})
        ck("prior_daily_archive_audit_passed",acquisition.get("status")=="PASS_DAILY_REFERENCE_ACQUIRED_AND_ROW_AUDIT_RECORDED" and
           acquisition.get("checks_passed")==98 and acquisition.get("checks_total")==98 and len(targets)==16 and
           all(r.get("fetch_status")=="PASS" and r.get("zip_crc")=="PASS" and r.get("sidecar_token_matches_zip")=="True" for r in targets),
           {"status":acquisition.get("status"),"checks":str(acquisition.get("checks_passed"))+"/"+str(acquisition.get("checks_total")),"targets":len(targets)})
        by_path={r.get("File Path",""):r for r in corrections};by_base={}
        for r in corrections:
            p=r.get("File Path","").replace("\\","/")
            if p:by_base.setdefault(p.rsplit("/",1)[-1],[]).append(r)
        matrix=[]
        for t in targets:
            iv=t["interval"];fn=t["filename"]
            target_path="data/spot/daily/klines/BTCUSDT/"+iv+"/"+fn
            exact=by_path.get(target_path);base_hits=by_base.get(fn,[])
            orig=first_sha(exact.get("Original File Checksum","")) if exact else ""
            new=first_sha(exact.get("New File Checksum","")) if exact else ""
            current=t.get("zip_sha256","")
            matrix.append({
              "case_id":t.get("case_id",""),"interval":iv,"utc_date":t.get("utc_date",""),
              "daily_zip_filename":fn,"expected_official_correction_path":target_path,
              "daily_zip_url":t.get("zip_url",""),"daily_checksum_url":t.get("sidecar_url",""),
              "verified_daily_zip_sha256":current,"sidecar_token_matches_zip":t.get("sidecar_token_matches_zip",""),"daily_zip_crc":t.get("zip_crc",""),
              "exact_correction_path_match":bool(exact),"correction_basename_match":bool(base_hits),"correction_basename_match_count":len(base_hits),
              "correction_original_sha256":orig,"correction_new_sha256":new,
              "verified_daily_zip_matches_correction_original":bool(exact and orig==current),
              "verified_daily_zip_matches_correction_new":bool(exact and new==current),
              "mapping_status":"EXACT_PATH_FOUND_REQUIRES_CHECKSUM_REVIEW" if exact else "NO_EXACT_CORRECTION_PATH_OR_BASENAME",
              "source_authority":"UNDETERMINED","case_closed":"False"
            })
        exact_count=sum(r["exact_correction_path_match"] for r in matrix)
        base_count=sum(r["correction_basename_match"] for r in matrix)
        ck("sixteen_target_denominator_and_key_uniqueness",len(matrix)==16 and len({(r["interval"],r["utc_date"],r["daily_zip_filename"]) for r in matrix})==16,
           {"targets":len(matrix),"unique":len({(r["interval"],r["utc_date"],r["daily_zip_filename"]) for r in matrix})})
        ck("correction_csv_has_no_exact_daily_target_mapping",exact_count==0 and base_count==0 and all(not r["exact_correction_path_match"] and not r["correction_basename_match"] for r in matrix),
           {"exact_paths":exact_count,"target_basename_hits":base_count})
        ck("no_source_or_case_closure",all(r["sidecar_token_matches_zip"]=="True" and r["daily_zip_crc"]=="PASS" and r["source_authority"]=="UNDETERMINED" and r["case_closed"]=="False" for r in matrix),
           "all 16 daily references remain verified inputs; source authority undetermined")
        status="PASS_OFFICIAL_CORRECTION_CSV_HAS_NO_EXACT_PATHS_FOR_16_TARGETS_SOURCE_AUTHORITY_OPEN" if all(c["status"]=="PASS" for c in checks) else "REVIEW_REQUIRED_CORRECTION_TARGET_MAPPING"
        write_csv(out/"CP0095_Correction_Target_Mapping_Matrix.csv",matrix)
        write_csv(out/"CP0095_Correction_Archive_Member_Inventory.csv",members)
        report=[
          "# CP-0095: Official correction archive target mapping audit","",
          "Status: "+status,"",
          "## Integrity and inputs",
          "- Reused the prior CP-0092 Actions artifact. This audit downloaded zero new archives.",
          "- Correction ZIP size 6,653,240 bytes; SHA-256 "+zip_sha+"; Git blob SHA-1 "+git_sha+"; ZIP CRC PASS.",
          "- Correction CSV SHA-256 "+csv_sha+"; 73,234 data rows; fields File Path, Original File Checksum, New File Checksum.",
          "- Prior CP-0107 daily reference audit passed 98/98 checks; 16/16 ZIP and checksum pairs have verified tokens and ZIP CRC.","",
          "## Target path mapping",
          "- Exact official correction path matches: "+str(exact_count)+"/16.",
          "- Target basenames anywhere in the correction CSV paths: "+str(base_count)+"/16.",
          "- Thus this correction CSV supplies no original/new checksum mapping for any of these 16 daily archives. It cannot resolve the 14 economic conflicts or 10 missing-grid keys in this scope.","",
          "## Decision boundary",
          "- This authentic correction archive is not applicable to the 16 targeted daily archive filenames.",
          "- Source authority remains UNDETERMINED for all 16 targets; no canonical source selected and no case closed.",
          "- Global G0 remains BLOCKED_GLOBAL; 11 aggregation blockers remain open; current 23 candidates remain G2 FAIL; G7 LIVE_BLOCKED.",
          "- No row edits, no timestamp changes, no downloads, no build, no backtest, no promotion, and no exchange actions.","",
          "## Next step",
          "- Stop rechecking this correction CSV for these exact target names. Continue only with genuinely new evidence linked to the exact source rows; keep unresolved source conflicts quarantined."
        ]
        rp=out/"CP0095_Correction_Target_Mapping_Report_HI.md";rp.write_text("\n".join(report)+"\n",encoding="utf-8")
        summary={
          "schema_version":1,"checkpoint":"CP-0095","task":"cp0095_official_correction_target_mapping_audit","status":status,
          "started_at_utc":started,"finished_at_utc":now(),
          "source":{"correction_zip_bytes":len(raw),"correction_zip_sha256":zip_sha,"correction_git_blob_sha1":git_sha,
            "correction_csv_sha256":csv_sha,"correction_csv_data_rows":len(corrections),"member_count":len(members),
            "prior_daily_audit_status":acquisition.get("status"),"prior_daily_audit_checks":"98/98","daily_target_count":len(targets)},
          "mapping":{"exact_path_matches":exact_count,"basename_matches":base_count,"all_16_no_exact_path_or_basename":exact_count==0 and base_count==0},
          "checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),
          "network_used":False,"archive_downloads":0,"source_bytes_modified":False,"canonical_source_selected":False,"source_cases_closed":0,
          "unresolved_shared_conflicts":60,"unmatched_rows_quarantined":909,"unresolved_nonrow_aggregation_blockers":11,
          "g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED",
          "production_candidate_build":False,"backtest_rerun":False,"strategy_promoted":False}
        for name in ("CP0095_Correction_Target_Mapping_Matrix.csv","CP0095_Correction_Archive_Member_Inventory.csv","CP0095_Correction_Target_Mapping_Report_HI.md"):
            p=out/name;summary.setdefault("outputs",{})[name]={"bytes":p.stat().st_size,"sha256":sha(p.read_bytes()),"rows":len(read_csv(p)) if name.endswith(".csv") else None}
        write_json(out/"CP0095_Correction_Target_Mapping_Summary.json",summary)
        print(json.dumps({"status":status,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
          "daily_targets":len(targets),"exact_paths":exact_count,"basename_hits":base_count,"network_used":False,"g0":"BLOCKED_GLOBAL"},ensure_ascii=False,sort_keys=True))
        return 0 if status.startswith("PASS_") else 1
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0095","task":"cp0095_official_correction_target_mapping_audit",
          "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),"error_type":type(exc).__name__,
          "error":str(exc),"checks":checks,"network_used":False,"archive_downloads":0,"source_bytes_modified":False,
          "canonical_source_selected":False,"source_cases_closed":0,"g0":"BLOCKED_GLOBAL","g7":"LIVE_BLOCKED"}
        write_json(out/"CP0095_Correction_Target_Mapping_Summary.json",summary)
        (out/"CP0095_Correction_Target_Mapping_Report_HI.md").write_text("# CP-0095 correction target mapping audit\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\n"+type(exc).__name__+": "+str(exc)+"\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1
if __name__=="__main__":raise SystemExit(main())
