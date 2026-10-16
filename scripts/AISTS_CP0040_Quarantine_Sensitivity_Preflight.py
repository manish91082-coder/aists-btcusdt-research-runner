#!/usr/bin/env python3
"""CP-0040 cache-only baseline reproducibility preflight. No network or market-data mutation."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIRS = [ROOT/".cache/aists/binance-monthly-archives", ROOT/".cache/aists/binance-daily-references"]
SEARCH_ROOTS = [ROOT/"evidence", ROOT/"results"]
NAME_RE = re.compile(r"(baseline|backtest|metric|equity|trade.?log|candidate.?dataset|signal|position|performance)", re.I)
EXCLUDE_PARTS = {".git", "__pycache__"}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_files(root: Path):
    if not root.exists():
        return []
    out=[]
    for p in root.rglob("*"):
        if not p.is_file() or any(part in EXCLUDE_PARTS for part in p.parts):
            continue
        try:
            st=p.stat()
        except OSError:
            continue
        out.append(p)
    return out

def main():
    generated=datetime.now(timezone.utc).isoformat()
    cache_inventory=[]
    for root in CACHE_DIRS:
        files=safe_files(root)
        zips=[p for p in files if p.suffix.lower()==".zip"]
        sidecars=[p for p in files if ".checksum" in p.name.lower() or p.suffix.lower()==".sha256"]
        cache_inventory.append({
            "path":str(root.relative_to(ROOT)),
            "exists":root.is_dir(),
            "file_count":len(files),
            "zip_count":len(zips),
            "sidecar_count":len(sidecars),
            "zip_bytes_total":sum(p.stat().st_size for p in zips),
            "sample_files":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha256(p)} for p in sorted(zips)[:3]]
        })
    candidate_evidence=[]
    for root in SEARCH_ROOTS:
        for p in safe_files(root):
            if NAME_RE.search(p.name) and p.suffix.lower() in {".csv",".json",".parquet",".feather",".pkl",".pickle",".md",".txt"}:
                try:
                    size=p.stat().st_size
                    candidate_evidence.append({"path":str(p.relative_to(ROOT)),"bytes":size,"sha256":sha256(p)})
                except OSError:
                    pass
    candidate_evidence.sort(key=lambda x:x["path"])
    # This preflight inventories evidence only; it does not infer reproducibility from archive presence.
    baseline_like=[x for x in candidate_evidence if re.search(r"(baseline|backtest|metric|equity|trade.?log|candidate.?dataset|signal|position|performance)",Path(x["path"]).name,re.I)]
    status="BASELINE_EVIDENCE_CANDIDATES_FOUND_REQUIRES_CONTENT_VALIDATION" if baseline_like else "BLOCKED_INPUTS_NOT_REPRODUCIBLE"
    summary={
        "checkpoint":"CP-0040",
        "task":"cp0040_quarantine_sensitivity_preflight",
        "status":status,
        "generated_at_utc":generated,
        "scope":"READ_ONLY_CACHE_AND_COMMITTED_EVIDENCE_INVENTORY",
        "network_used":False,
        "market_data_requested":False,
        "raw_source_archives_modified":False,
        "production_candidate_build":False,
        "backtest_run":False,
        "strategy_promoted":False,
        "current_manifest_path":"evidence/source_adjudication/CP0040_Current_Manifest.json",
        "current_manifest_sha256":sha256(ROOT/"evidence/source_adjudication/CP0040_Current_Manifest.json") if (ROOT/"evidence/source_adjudication/CP0040_Current_Manifest.json").is_file() else None,
        "cache_inventory":cache_inventory,
        "baseline_like_evidence_count":len(baseline_like),
        "baseline_like_evidence":baseline_like,
        "other_candidate_named_evidence_count":len(candidate_evidence),
        "limitations":["A cache hit proves cache restoration only, not baseline-input reproducibility.","No archive download, strategy execution, signal generation, or metric recomputation was performed.","Any found evidence must be content-validated before a sensitivity run."]
    }
    out=ROOT/"results/cp0040_quarantine_sensitivity_preflight"
    out.mkdir(parents=True,exist_ok=True)
    (out/"CP0040_Quarantine_Sensitivity_Preflight_Summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    report=[
        "# CP-0040 Quarantine Sensitivity Preflight",
        "",
        f"- Status: `{status}`",
        f"- Generated UTC: {generated}",
        "- Scope: read-only inventory of committed evidence and restored caches; no network, acquisition, backtest, or source edits.",
        f"- Baseline-like evidence files: {len(baseline_like)}",
        "",
        "## Cache inventory",
    ]
    for item in cache_inventory:
        report += [f"- `{item['path']}`: exists={item['exists']}; files={item['file_count']}; ZIPs={item['zip_count']}; sidecars={item['sidecar_count']}; ZIP bytes={item['zip_bytes_total']}"]
    report += ["","## Baseline-like evidence files"]
    report += [f"- `{x['path']}` ({x['bytes']} bytes; SHA-256 `{x['sha256']}`)" for x in baseline_like] or ["- None found by the conservative filename inventory."]
    report += ["","## Decision","- Archive-cache presence alone is not baseline reproducibility.","- No production candidate build/backtest was run; no strategy was promoted.","- If baseline-like outputs are absent, stop with `BLOCKED_INPUTS_NOT_REPRODUCIBLE`; do not infer metrics."]
    (out/"CP0040_Quarantine_Sensitivity_Preflight_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"cache_inventory":cache_inventory,"baseline_like_evidence_count":len(baseline_like),"summary_path":str(out/"CP0040_Quarantine_Sensitivity_Preflight_Summary.json")},ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
