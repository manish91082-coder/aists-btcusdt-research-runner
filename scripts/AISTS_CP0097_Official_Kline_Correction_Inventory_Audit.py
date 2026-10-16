#!/usr/bin/env python3
"""CP-0097: bind the official update inventory to prior correction applicability evidence.

Read-only reconciliation only. It authenticates the saved upstream README bytes,
checks the exhaustive Updates table, and joins the existing CP-0094/95/96 outputs.
No network, downloads, row edits, source selection or case closure.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
README_BLOB_SHA1="e01e34a0b0cd91d62386a5a237190a3167138bae"
CP0095_STATUS="PASS_OFFICIAL_CORRECTION_CSV_HAS_NO_EXACT_PATHS_FOR_16_TARGETS_SOURCE_AUTHORITY_OPEN"
CP0096_STATUS="PASS_CHECKSUM_CROSSWALK_NO_ARCHIVE_HASH_HITS_SOURCE_AUTHORITY_OPEN"
CP0094_STATUS="PASS_24_ACQUISITION_KEYS_CONFIRMED_QUARANTINED_SOURCE_AUTHORITY_OPEN"
def now(): return datetime.now(timezone.utc).isoformat()
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def blobsha(b:bytes)->str:return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read_json(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def write_json(p,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
def write_csv(p,rows):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) if rows else ["status"]
    with Path(p).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader()
        if rows:w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--official-readme",default="evidence/source_adjudication/CP0097_Official_Binance_Public_Data_README_master.md")
    ap.add_argument("--cp0094-summary",default="evidence/source_adjudication/CP0094_Acquisition_Quarantine_Coverage_Run_38911689643/CP0094_Acquisition_Quarantine_Coverage_Summary.json")
    ap.add_argument("--cp0095-summary",default="evidence/source_adjudication/CP0095_Official_Correction_Target_Mapping_Run_38912641513/CP0095_Correction_Target_Mapping_Summary.json")
    ap.add_argument("--cp0096-summary",default="evidence/source_adjudication/CP0096_Correction_Checksum_Crosswalk_Run_38913040361/CP0096_Correction_Checksum_Crosswalk_Summary.json")
    ap.add_argument("--manifest-pointer",default="evidence/source_adjudication/CP0040_Current_Manifest.json")
    ap.add_argument("--output-dir",default="results/cp0097_official_kline_correction_inventory_audit")
    a=ap.parse_args();started=now();out=(ROOT/a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True);checks=[]
    def ck(name,ok,detail):checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
    try:
        readme_path=(ROOT/a.official_readme).resolve()
        cp94_path=(ROOT/a.cp0094_summary).resolve();cp95_path=(ROOT/a.cp0095_summary).resolve();cp96_path=(ROOT/a.cp0096_summary).resolve()
        pointer_path=(ROOT/a.manifest_pointer).resolve()
        required=[readme_path,cp94_path,cp95_path,cp96_path,pointer_path]
        missing=[str(p) for p in required if not p.is_file()]
        ck("all_official_snapshot_and_prior_results_present",not missing,missing or "all inputs present")
        if missing:raise ValueError("Missing required input: "+", ".join(missing))
        rb=readme_path.read_bytes();text=rb.decode("utf-8")
        cp94=read_json(cp94_path);cp95=read_json(cp95_path);cp96=read_json(cp96_path);mp=read_json(pointer_path)
        rb_blob=blobsha(rb);rb_sha=sha(rb)
        ck("official_readme_blob_exact_match",rb_blob==README_BLOB_SHA1,{"bytes":len(rb),"git_blob_sha1":rb_blob,"expected":README_BLOB_SHA1,"sha256":rb_sha})
        updates_section=text.split("### Updates",1)[1].split("## Dataset Terms",1)[0] if "### Updates" in text and "## Dataset Terms" in text else ""
        update_rows=[line.strip() for line in updates_section.splitlines() if re.match(r"^\|\s*20\d{2}-\d{2}-\d{2}\s*\|",line.strip())]
        kline_rows=[line for line in update_rows if re.search(r"updates/[^|)]*kline[^|)]*\.zip",line,re.I)]
        agg_rows=[line for line in update_rows if re.search(r"updates/[^|)]*aggregate_trade[^|)]*\.zip",line,re.I)]
        ck("readme_declares_exhaustive_updates_inventory","exhaustive list of updates performed to the archive" in updates_section,updates_section[:500])
        ck("official_updates_table_exact_two_rows_and_types",len(update_rows)==2 and len(kline_rows)==1 and len(agg_rows)==1,
           {"total_rows":len(update_rows),"kline_rows":len(kline_rows),"aggregate_trade_rows":len(agg_rows),"rows":update_rows})
        ck("only_officially_listed_kline_bundle_is_cp0092_target",
           "updates/2022-08-08_kline_updates.zip" in kline_rows[0] and
           "updates/2022-04-21_aggregate_trade_updates.zip" in agg_rows[0],
           {"kline_update":kline_rows[0] if kline_rows else None,"aggregate_trade_update":agg_rows[0] if agg_rows else None})
        ck("CP0095_exact_path_applicability_audit_passed",cp95.get("status")==CP0095_STATUS and cp95.get("checks_passed")==9 and cp95.get("checks_total")==9 and
           cp95.get("mapping",{}).get("exact_path_matches")==0 and cp95.get("mapping",{}).get("basename_matches")==0 and cp95.get("source",{}).get("daily_target_count")==16,
           {"status":cp95.get("status"),"checks":str(cp95.get("checks_passed"))+"/"+str(cp95.get("checks_total")),
            "exact_paths":cp95.get("mapping",{}).get("exact_path_matches"),"basenames":cp95.get("mapping",{}).get("basename_matches")})
        c96=cp96.get("crosswalk",{})
        ck("CP0096_hash_applicability_audit_passed",cp96.get("status")==CP0096_STATUS and cp96.get("checks_passed")==11 and cp96.get("checks_total")==11 and
           c96.get("daily_targets")==16 and c96.get("monthly_targets")==14 and c96.get("daily_archive_checksum_hits")==0 and c96.get("monthly_archive_checksum_hits")==0,
           {"status":cp96.get("status"),"checks":str(cp96.get("checks_passed"))+"/"+str(cp96.get("checks_total")),
            "daily_hash_hits":c96.get("daily_archive_checksum_hits"),"monthly_hash_hits":c96.get("monthly_archive_checksum_hits")})
        c94=cp94.get("coverage",{})
        ck("CP0094_disputed_keys_remain_quarantined",cp94.get("status")==CP0094_STATUS and cp94.get("checks_passed")==15 and cp94.get("checks_total")==15 and
           c94.get("economic_exact_keys_quarantined")==14 and c94.get("monthly_only_exact_keys_quarantined")==10 and c94.get("all_24_quarantined") is True,
           {"status":cp94.get("status"),"checks":str(cp94.get("checks_passed"))+"/"+str(cp94.get("checks_total")),"coverage":c94})
        ck("global_source_authority_and_safety_gates_still_open",
           mp.get("candidate_eligibility_blocked") is True and mp.get("status")=="PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN" and
           cp96.get("canonical_source_selected") is False and cp96.get("source_cases_closed")==0 and cp96.get("unresolved_nonrow_aggregation_blockers")==11 and
           cp96.get("g0")=="BLOCKED_GLOBAL" and cp96.get("g2")=="FAIL_CURRENT_23_CANDIDATES" and cp96.get("g7")=="LIVE_BLOCKED",
           {"manifest_status":mp.get("status"),"g0":cp96.get("g0"),"g2":cp96.get("g2"),"g7":cp96.get("g7")})
        passed=sum(c["status"]=="PASS" for c in checks);total=len(checks)
        status="PASS_OFFICIAL_KLINE_CORRECTION_ROUTE_EXHAUSTED_FOR_FROZEN_TARGET_SET" if passed==total else "REVIEW_REQUIRED_OFFICIAL_CORRECTION_INVENTORY"
        inventory=[]
        for line in update_rows:
            m=re.match(r"^\|\s*(20\d{2}-\d{2}-\d{2})\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*(.*?)\s*\|?$",line)
            inventory.append({"date":m.group(1) if m else "","label":m.group(2) if m else "",
              "path":m.group(3) if m else "","note":m.group(4) if m else line,
              "data_class":"KLINE" if "kline" in (m.group(3) if m else "").lower() else "AGGREGATE_TRADE" if "aggregate_trade" in (m.group(3) if m else "").lower() else "UNCLASSIFIED",
              "source_blob_sha1":rb_blob,"target_set_path_match_count":cp95.get("mapping",{}).get("exact_path_matches",0) if "kline" in (m.group(3) if m else "").lower() else 0,
              "target_set_checksum_hit_count":c96.get("daily_archive_checksum_hits",0)+c96.get("monthly_archive_checksum_hits",0) if "kline" in (m.group(3) if m else "").lower() else 0})
        write_csv(out/"CP0097_Official_Update_Inventory.csv",inventory)
        report=[
          "# CP-0097: official correction inventory closure audit","",
          "Status: "+status,"",
          "## Official source snapshot",
          "- Repository: binance/binance-public-data; path README.md; ref master.",
          "- The stored snapshot's Git blob SHA-1 exactly matches the official read result: "+rb_blob+"; SHA-256 "+rb_sha+"; bytes "+str(len(rb))+".",
          "- The README calls its Updates table the exhaustive list of archive updates. Parsed rows: 2 total; one kline correction, one aggregate-trade update.","",
          "## Cross-check against the disputed source set",
          "- The only listed kline update is updates/2022-08-08_kline_updates.zip.",
          "- CP-0095 exact file path and basename scan: 0/16 daily targets.",
          "- CP-0096 checksum scan: 0/16 daily archive hash hits and 0/14 monthly archive hash hits in Original/New checksum columns.",
          "- Therefore, the documented official kline correction bundle has no applicable filename or checksum mapping to this frozen source target set.","",
          "## Decision",
          "- Mark this one correction-bundle route as EXHAUSTED_FOR_FROZEN_TARGET_SET. This does not prove the conflicting archives are equivalent or choose either side as canonical.",
          "- CP-0094 continues to show the 14 economic-conflict keys and 10 missing-grid keys quarantined. All remain open; source authority NONE/UNDETERMINED.",
          "- Global G0 remains BLOCKED_GLOBAL; 11 aggregation blockers remain open; G2 current 23 candidates FAIL; G7 LIVE_BLOCKED.",
          "- No network activity, download, source-row change, worklist mutation, candidate build, backtest, strategy promotion or exchange action.","",
          "## Next permitted direction",
          "- Stop repeating the README/CP0092/CP0095/CP0096 correction-bundle route for this source set.",
          "- Continue only with independent exact-row official evidence for the 14 economic conflicts and 10 missing-grid keys, or maintain quarantine if no such evidence is available."
        ]
        rp=out/"CP0097_Official_Kline_Correction_Inventory_Report_HI.md"
        rp.write_text("\n".join(report)+"\n",encoding="utf-8")
        summary={
          "schema_version":1,"checkpoint":"CP-0097","task":"cp0097_official_kline_correction_inventory_audit",
          "status":status,"started_at_utc":started,"finished_at_utc":now(),
          "official_readme":{"repository":"binance/binance-public-data","path":"README.md","ref":"master",
            "git_blob_sha1":rb_blob,"expected_git_blob_sha1":README_BLOB_SHA1,"sha256":rb_sha,"bytes":len(rb),
            "exhaustive_updates_statement_present":"exhaustive list of updates performed to the archive" in updates_section,
            "rows":inventory},
          "decision":{"documented_kline_correction_bundles":len(kline_rows),"only_kline_bundle":"updates/2022-08-08_kline_updates.zip",
            "cp0095_exact_daily_target_paths":cp95.get("mapping",{}).get("exact_path_matches"),
            "cp0095_target_basename_hits":cp95.get("mapping",{}).get("basename_matches"),
            "cp0096_daily_archive_hash_hits":c96.get("daily_archive_checksum_hits"),
            "cp0096_monthly_archive_hash_hits":c96.get("monthly_archive_checksum_hits"),
            "correction_route":"EXHAUSTED_FOR_FROZEN_TARGET_SET",
            "canonical_source_selected":False,"source_cases_closed":0,"disputed_keys_remain_quarantined":c94.get("all_24_quarantined") is True},
          "checks":checks,"checks_passed":passed,"checks_total":total,
          "network_used":False,"archive_downloads":0,"source_bytes_modified":False,"worklist_mutated":False,
          "unresolved_shared_conflicts":60,"unmatched_rows_quarantined":909,"unresolved_nonrow_aggregation_blockers":11,
          "g0":"BLOCKED_GLOBAL","g2":"FAIL_CURRENT_23_CANDIDATES","g7":"LIVE_BLOCKED",
          "production_candidate_build":False,"backtest_rerun":False,"strategy_promoted":False}
        for name in ("CP0097_Official_Update_Inventory.csv","CP0097_Official_Kline_Correction_Inventory_Report_HI.md"):
            p=out/name;summary.setdefault("outputs",{})[name]={"bytes":p.stat().st_size,"sha256":sha(p.read_bytes()),"rows":len(read_csv(p)) if name.endswith(".csv") else None}
        write_json(out/"CP0097_Official_Kline_Correction_Inventory_Summary.json",summary)
        print(json.dumps({"status":status,"checks_passed":passed,"checks_total":total,
          "official_update_rows":len(update_rows),"kline_bundles":len(kline_rows),"target_paths":cp95.get("mapping",{}).get("exact_path_matches"),
          "daily_hash_hits":c96.get("daily_archive_checksum_hits"),"monthly_hash_hits":c96.get("monthly_archive_checksum_hits"),
          "g0":"BLOCKED_GLOBAL"},ensure_ascii=False,sort_keys=True))
        return 0 if status.startswith("PASS_") else 1
    except Exception as exc:
        summary={"schema_version":1,"checkpoint":"CP-0097","task":"cp0097_official_kline_correction_inventory_audit",
          "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":now(),"error_type":type(exc).__name__,
          "error":str(exc),"checks":checks,"network_used":False,"archive_downloads":0,"source_bytes_modified":False,
          "canonical_source_selected":False,"source_cases_closed":0,"g0":"BLOCKED_GLOBAL","g7":"LIVE_BLOCKED"}
        write_json(out/"CP0097_Official_Kline_Correction_Inventory_Summary.json",summary)
        (out/"CP0097_Official_Kline_Correction_Inventory_Report_HI.md").write_text("# CP-0097 Official Kline Correction Inventory Audit\n\nStatus: FAIL_CLOSED_UNEXPECTED_ERROR\n\n"+type(exc).__name__+": "+str(exc)+"\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1
if __name__=="__main__":raise SystemExit(main())
