#!/usr/bin/env python3
"""Frozen CP-0040 exact-key quarantine sensitivity diagnostic.

Fail-closed gates: verify official CP-0040 artifacts, decode the frozen CP-0031
engine, reconstruct hash-anchored inputs from cached ZIPs with no network, and
reproduce baseline metric anchors BEFORE calculating any quarantine scenario.
No production builder, source-authority decision, strategy promotion, or live I/O.
"""
from __future__ import annotations
import argparse
import base64
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import math
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPO = "manish91082-coder/aists-btcusdt-research-runner"
COMPARATOR = "MTF_BREAKOUT_4H_D1"
INTERVALS = ("4h", "1d", "1mo")
PERIODS = ("TRAIN", "DEVELOPMENT_CHECK", "CONSUMED_OOS_DIAGNOSTIC")
BASELINE_ROWS = {"4h": 19975, "1d": 3332, "1mo": 110}
EXPECTED_QUARANTINE_MATCHES = {"4h": 6, "1d": 3, "1mo": 0}
FROZEN_ENGINE_SHA256 = "6b92b0956522ad6e6a7bdcaa364ee677c97b8926e3705d6250866c17cc70ceec"
BASELINE_INPUT_SNAPSHOT_SHA256 = "1e5f528d1c09fb8b598e75f5c08b23530f0073882553cb272558aa89b047981f"
EXPECTED_MANIFEST_SHA256 = "e5cd62a67685b4ff1bc32c2434b5e373fe2dd76d74e2424b67a4cc5aee7c720a"
EXPECTED_BLOCKERS_SHA256 = "f45431edcaf657404b9f5405b239f25cd7761af21e9e8115cd71002f7be1bf36"
RULEBOOK_SHA256 = "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
NUMERIC_TOL = 1e-8
METRIC_FIELDS = (
    "net_return_pct", "max_intrabar_drawdown_proxy_pct", "closed_round_trips",
    "profit_factor", "win_rate_pct", "net_realized_pnl_usdt", "fees_paid_usdt",
    "estimated_slippage_cost_usdt", "final_equity_usdt",
)


class BlockedDiagnostic(Exception):
    """Known evidence/gate block; diagnostic should finish without performance claims."""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise BlockedDiagnostic(f"Cannot read required JSON {path}: {type(exc).__name__}: {exc}") from exc


def read_csv_rows(path: Path):
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        raise BlockedDiagnostic(f"Cannot read required CSV {path}: {type(exc).__name__}: {exc}") from exc


def write_csv(path: Path, rows: list[dict], fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("status\nNO_ROWS\n", encoding="utf-8")
        return
    names = fieldnames or list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=names, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def load_engine(payload_path: Path, temp_root: Path):
    encoded = payload_path.read_text(encoding="ascii").strip()
    try:
        compressed = base64.b64decode(encoded, validate=True)
        source = gzip.decompress(compressed)
    except Exception as exc:
        raise BlockedDiagnostic(f"Frozen engine payload decode failed: {type(exc).__name__}: {exc}") from exc
    actual_sha = sha_bytes(source)
    if actual_sha != FROZEN_ENGINE_SHA256 or len(source) != 49284:
        raise BlockedDiagnostic(
            f"Frozen engine source mismatch: bytes={len(source)} sha256={actual_sha}; "
            f"expected bytes=49284 sha256={FROZEN_ENGINE_SHA256}"
        )
    engine_path = temp_root / "AISTS_CP0031_Research_Engine_R1.py"
    engine_path.write_bytes(source)
    spec = importlib.util.spec_from_file_location("aists_cp0031_frozen_engine", engine_path)
    if spec is None or spec.loader is None:
        raise BlockedDiagnostic("Unable to import verified frozen CP-0031 engine")
    import types
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, {"bytes": len(source), "sha256": actual_sha, "payload_sha256": sha_file(payload_path)}


def validate_gate(anchors_path: Path, metric_anchors_path: Path, pointer_path: Path, scope_lock_path: Path):
    anchors = read_json(anchors_path)
    if anchors.get("anchor_id") != "CP0040-BASELINE-RECONSTRUCTION-ANCHORS-20261016-01":
        raise BlockedDiagnostic("Unexpected input reconstruction anchor identity")
    if anchors.get("created_from", {}).get("package_sha256") != BASELINE_INPUT_SNAPSHOT_SHA256:
        raise BlockedDiagnostic("Frozen snapshot hash in input anchor does not match CP-0040 manifest")
    if anchors.get("frozen_engine", {}).get("sha256") != FROZEN_ENGINE_SHA256:
        raise BlockedDiagnostic("Frozen engine SHA in input anchor differs from required engine")
    for iv in INTERVALS:
        item = anchors.get("input_content_anchors", {}).get(iv, {})
        if not item.get("decompressed_sha256") or int(item.get("rows", -1)) != BASELINE_ROWS[iv]:
            raise BlockedDiagnostic(f"Missing/invalid frozen decompressed-content anchor for {iv}")

    metric_anchors = read_json(metric_anchors_path)
    if metric_anchors.get("anchor_id") != "CP0040-MTF-BREAKOUT-4H-D1-HISTORIC-METRIC-ANCHORS-20261016-01":
        raise BlockedDiagnostic("Unexpected historic metric-anchor identity")
    if metric_anchors.get("comparator") != COMPARATOR:
        raise BlockedDiagnostic("Historic metric-anchor comparator is not the frozen comparator")
    if metric_anchors.get("source", {}).get("frozen_engine_sha256") != FROZEN_ENGINE_SHA256:
        raise BlockedDiagnostic("Historic metric anchors are not bound to the frozen engine SHA")

    pointer = read_json(pointer_path)
    if pointer.get("manifest_sha256") != EXPECTED_MANIFEST_SHA256:
        raise BlockedDiagnostic("Current CP-0040 manifest pointer SHA differs from the frozen scope lock")
    if pointer.get("candidate_eligibility_blocked") is not True:
        raise BlockedDiagnostic("Current CP-0040 pointer does not preserve the candidate-eligibility block")
    if pointer.get("status") != "PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN":
        raise BlockedDiagnostic("Current CP-0040 manifest status is not the expected bounded status")
    manifest_path = ROOT / pointer.get("manifest_path", "")
    blockers_path = ROOT / pointer.get("blockers_path", "")
    manifest_sha = sha_file(manifest_path) if manifest_path.is_file() else ""
    blockers_sha = sha_file(blockers_path) if blockers_path.is_file() else ""
    if manifest_sha != EXPECTED_MANIFEST_SHA256:
        raise BlockedDiagnostic(f"Manifest SHA-256 mismatch: actual={manifest_sha}")
    if blockers_sha != EXPECTED_BLOCKERS_SHA256:
        raise BlockedDiagnostic(f"Non-row blocker ledger SHA-256 mismatch: actual={blockers_sha}")

    summary_path = ROOT / "evidence/source_adjudication/CP0040_Run_38883792900/CP0040_ExactKey_Quarantine_Manifest_Summary.json"
    summary = read_json(summary_path)
    if summary.get("row_level_manifest", {}).get("sha256") != EXPECTED_MANIFEST_SHA256:
        raise BlockedDiagnostic("CP-0040 summary disagrees with current manifest SHA")
    if summary.get("nonrow_blockers", {}).get("sha256") != EXPECTED_BLOCKERS_SHA256:
        raise BlockedDiagnostic("CP-0040 summary disagrees with non-row blocker SHA")
    blockers = read_csv_rows(blockers_path)
    manifest = read_csv_rows(manifest_path)
    if len(blockers) != 11 or summary.get("nonrow_blockers", {}).get("rows") != 11:
        raise BlockedDiagnostic(f"Expected exactly 11 open non-row aggregation blockers, got {len(blockers)}")
    if len(manifest) != 1427 or len({(r["interval"], r["open_time_ms"]) for r in manifest}) != 1427:
        raise BlockedDiagnostic("Manifest must contain 1,427 unique exact (interval, open_time_ms) keys")
    if any(r.get("canonical_source", "").upper() != "NONE" or r.get("case_closed", "").lower() != "false" for r in manifest):
        raise BlockedDiagnostic("Manifest contains selected source authority or closed cases")
    # The separate non-row blocker ledger is row/relationship-oriented; openness is
    # established by its frozen 11-row hash and the canonical summary's eligibility gate.

    lock_text = scope_lock_path.read_text(encoding="utf-8")
    if COMPARATOR not in lock_text or RULEBOOK_SHA256 not in lock_text:
        raise BlockedDiagnostic("Frozen scope-lock text does not name the comparator and rulebook SHA")
    return anchors, metric_anchors, pointer, manifest, blockers, {
        "input_anchor_file_sha256": sha_file(anchors_path),
        "metric_anchor_file_sha256": sha_file(metric_anchors_path),
        "manifest_sha256": manifest_sha,
        "blockers_sha256": blockers_sha,
        "manifest_rows": len(manifest),
        "nonrow_blocker_rows": len(blockers),
        "canonical_source": "NONE",
        "candidate_eligibility_blocked": True,
    }


def construct_quarantine_variant(source_paths: dict, target_root: Path, manifest_rows: list[dict], anchors: dict):
    quarantine_keys = {
        (str(r.get("interval", "")).strip(), str(r.get("open_time_ms", "")).strip()): r
        for r in manifest_rows
    }
    scope_rows = [r for (iv, _), r in quarantine_keys.items() if iv in ("4h", "1d", "1mo")]
    expected = EXPECTED_QUARANTINE_MATCHES
    scope_counts = {iv: sum(1 for r in scope_rows if r.get("interval") == iv) for iv in INTERVALS}
    if scope_counts != expected:
        raise BlockedDiagnostic(f"Comparator-specific exact-key scope changed: actual={scope_counts}; expected={expected}")

    rows_by_interval = {}
    key_audit = []
    byte_copy_audit = []
    for iv in INTERVALS:
        source_path = source_paths[iv]
        raw_bytes = gzip.decompress(source_path.read_bytes())
        text = raw_bytes.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text, newline=""))
        headers = list(reader.fieldnames or [])
        if not headers or "open_time_ms" not in headers:
            raise BlockedDiagnostic(f"{iv}: candidate CSV header is absent or lacks open_time_ms")
        rows = list(reader)
        ts_tokens = [r.get("open_time_ms", "") for r in rows]
        if any(not x.isdigit() for x in ts_tokens) or len(set(ts_tokens)) != len(ts_tokens):
            raise BlockedDiagnostic(f"{iv}: candidate keys are not unique integer timestamp tokens")
        anchor = anchors["input_content_anchors"][iv]
        if len(rows) != int(anchor["rows"]) or sha_bytes(raw_bytes) != anchor["decompressed_sha256"]:
            raise BlockedDiagnostic(f"{iv}: content changed after baseline reconstruction was verified")
        selected = []
        removed = []
        for row in rows:
            token = row["open_time_ms"]
            item = quarantine_keys.get((iv, token))
            if item is None:
                selected.append(row)
            else:
                removed.append(row)
                key_audit.append({
                    "interval": iv,
                    "open_time_ms": token,
                    "open_time_utc": row.get("open_time_utc", ""),
                    "case_id": item.get("case_id", ""),
                    "case_class": item.get("case_class", ""),
                    "baseline_row_removed": True,
                    "replacement_row_added": False,
                    "raw_timestamp_token_preserved_for_comparison": token,
                    "disposition": item.get("disposition", ""),
                    "canonical_source": "NONE",
                    "case_closed": "false",
                })
        if len(removed) != expected[iv]:
            raise BlockedDiagnostic(f"{iv}: exact-key removal count={len(removed)} expected={expected[iv]}")

        kept_text = io.StringIO(newline="")
        writer = csv.DictWriter(kept_text, fieldnames=headers, extrasaction="raise")
        writer.writeheader()
        writer.writerows(selected)
        gz_bytes = gzip.compress(kept_text.getvalue().encode("utf-8"), compresslevel=6, mtime=0)
        out_path = target_root / "derived" / "research_candidate_v1" / "BTCUSDT" / "intervals" / source_path.name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(gz_bytes)
        actual_gz_sha = sha_file(out_path)
        actual_raw_sha = sha_bytes(gzip.decompress(out_path.read_bytes()))
        if actual_raw_sha != sha_bytes(kept_text.getvalue().encode("utf-8")):
            raise BlockedDiagnostic(f"{iv}: quarantined output GZIP did not round-trip byte-identically")
        rows_by_interval[iv] = selected
        byte_copy_audit.append({
            "interval": iv,
            "baseline_rows": len(rows),
            "removed_exact_key_rows": len(removed),
            "quarantine_rows_after_filter": len(selected),
            "compressed_bytes": len(gz_bytes),
            "compressed_sha256": actual_gz_sha,
            "decompressed_csv_sha256": actual_raw_sha,
            "baseline_decompressed_csv_sha256": sha_bytes(raw_bytes),
            "output_content_roundtrip": True,
            "replacements_added": 0,
        })

    target_root.joinpath("reports").mkdir(parents=True, exist_ok=True)
    variant_manifest = {"schema_version": 1, "checkpoint": "CP-0040", "scope": "TEMPORARY_DIAGNOSTIC_ONLY",
                        "results": {iv: {
                            "status": "PASS_TEMPORARY_EXACT_KEY_QUARANTINE_DIAGNOSTIC",
                            "sha256": sha_file(target_root / "derived" / "research_candidate_v1" / "BTCUSDT" / "intervals" / f"BTCUSDT-{iv}-research-candidate.csv.gz"),
                            "candidate_rows": len(rows_by_interval[iv]),
                        } for iv in INTERVALS}}
    (target_root / "reports" / "cp0026_research_candidate_manifest.json").write_text(
        json.dumps(variant_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return key_audit, byte_copy_audit, quarantine_keys, rows_by_interval


def load_feature_scenario(engine, root: Path):
    frames, quality, manifest_path = engine.load_inputs(root)
    daily_features = engine.add_features(frames["1d"], "1d")
    local_4h = engine.add_features(frames["4h"], "4h")
    featured_4h = engine.attach_completed_regime(local_4h, daily_features, "1d")
    # A separate raw higher-timeframe regime signal exposes data/indicator changes, not trade events.
    return frames, daily_features, featured_4h


def metric_value_matches(actual, expected):
    if actual is None or expected is None:
        return actual is expected
    try:
        a = float(actual); e = float(expected)
    except (TypeError, ValueError):
        return actual == expected
    if math.isnan(a) or math.isnan(e):
        return math.isnan(a) and math.isnan(e)
    if math.isinf(a) or math.isinf(e):
        return a == e
    return abs(a - e) <= NUMERIC_TOL


def compare_metric_anchors(engine, baseline_featured, metric_anchors):
    actuals = {}
    mismatches = []
    for period in PERIODS:
        start, end = engine.get_window_indices(baseline_featured, period)
        if end - start < 2:
            raise BlockedDiagnostic(f"Frozen baseline {period} has fewer than two bars")
        result = engine.simulate(baseline_featured, COMPARATOR, start, end, 10.0, 5.0, 0.25, True)
        actuals[period] = result
        expected = metric_anchors["metrics"][period]
        for field in METRIC_FIELDS:
            ok = metric_value_matches(result.get(field), expected.get(field))
            if not ok:
                mismatches.append({"period": period, "metric": field, "actual": result.get(field),
                                   "expected": expected.get(field), "absolute_tolerance": NUMERIC_TOL})
    return actuals, mismatches


def build_metric_rows(engine, base_featured, variant_featured, metric_anchors):
    rows = []
    actual_baseline, mismatches = compare_metric_anchors(engine, base_featured, metric_anchors)
    if mismatches:
        return rows, actual_baseline, {}, mismatches
    quarantine_metrics = {}
    for period in PERIODS:
        bs, be = engine.get_window_indices(base_featured, period)
        qs, qe = engine.get_window_indices(variant_featured, period)
        btimes = base_featured.iloc[bs:be]["open_time_ms"].tolist()
        qtimes = variant_featured.iloc[qs:qe]["open_time_ms"].tolist()
        if not btimes or not qtimes or btimes[0] != qtimes[0] or btimes[-1] != qtimes[-1]:
            raise BlockedDiagnostic(f"{period}: baseline and quarantine windows do not preserve the same endpoint timestamps")
        q = engine.simulate(variant_featured, COMPARATOR, qs, qe, 10.0, 5.0, 0.25, True)
        quarantine_metrics[period] = q
        b = actual_baseline[period]
        row = {
            "comparator": COMPARATOR, "period": period,
            "window_first_open_time_ms": int(btimes[0]), "window_last_open_time_ms": int(btimes[-1]),
            "fee_bps_per_side": 10, "extra_slippage_bps_per_side": 5,
            "initial_capital_usdt": 10000, "allocation_fraction": 0.25,
            "baseline_metric_anchors_match": True,
            "baseline_net_return_pct": b["net_return_pct"],
            "quarantine_net_return_pct": q["net_return_pct"],
            "delta_net_return_percentage_points": q["net_return_pct"] - b["net_return_pct"],
        }
        for field in METRIC_FIELDS:
            bval = b.get(field); qval = q.get(field)
            row[f"baseline_{field}"] = bval
            row[f"quarantine_{field}"] = qval
            if isinstance(bval, (float, int)) and isinstance(qval, (float, int)):
                row[f"delta_{field}"] = qval - bval
            else:
                row[f"delta_{field}"] = ""
        rows.append(row)
    return rows, actual_baseline, quarantine_metrics, []


def flags_for_4h(engine, frame):
    import numpy as np
    out = frame.copy()
    ph = out["prior_high20"].to_numpy(dtype=float)
    pl = out["prior_low10"].to_numpy(dtype=float)
    cl = out["close"].to_numpy(dtype=float)
    regime = out["regime_up"].to_numpy(dtype=bool)
    out["entry_bar_flag"] = regime & np.isfinite(ph) & (cl > ph)
    out["exit_bar_flag"] = (~regime) | (np.isfinite(pl) & (cl < pl))
    return out


def signal_impact_rows(bframes, bdaily, b4h, qframes, qdaily, q4h, quarantine_keys, key_audit):
    base4 = flags_for_4h(None, b4h)
    q4 = flags_for_4h(None, q4h)
    base_by_ts = {str(int(r.open_time_ms)): r for r in base4.itertuples(index=False)}
    q_by_ts = {str(int(r.open_time_ms)): r for r in q4.itertuples(index=False)}
    common_ts = sorted(set(base_by_ts) & set(q_by_ts), key=int)
    def val(row, field):
        return getattr(row, field)
    entry_flips = exit_flips = regime_flips = prior_high_changes = prior_low_changes = 0
    for ts in common_ts:
        b = base_by_ts[ts]; q = q_by_ts[ts]
        entry_flips += int(bool(val(b,"entry_bar_flag")) != bool(val(q,"entry_bar_flag")))
        exit_flips += int(bool(val(b,"exit_bar_flag")) != bool(val(q,"exit_bar_flag")))
        regime_flips += int(bool(val(b,"regime_up")) != bool(val(q,"regime_up")))
        for col, counter_name in (("prior_high20","prior_high_changes"),("prior_low10","prior_low_changes")):
            bv = val(b,col); qv = val(q,col)
            different = (
                (not math.isnan(float(bv)) and math.isnan(float(qv))) or
                (math.isnan(float(bv)) and not math.isnan(float(qv))) or
                (not math.isnan(float(bv)) and not math.isnan(float(qv)) and abs(float(bv)-float(qv)) > NUMERIC_TOL)
            )
            if different:
                if counter_name == "prior_high_changes": prior_high_changes += 1
                else: prior_low_changes += 1

    bdaily_by_ts = {str(int(r.open_time_ms)): r for r in bdaily.itertuples(index=False)}
    qdaily_by_ts = {str(int(r.open_time_ms)): r for r in qdaily.itertuples(index=False)}
    daily_common = sorted(set(bdaily_by_ts) & set(qdaily_by_ts), key=int)
    daily_regime_flips = sum(bool(bdaily_by_ts[t].regime_up) != bool(qdaily_by_ts[t].regime_up) for t in daily_common)
    removed_entry_flags = removed_exit_flags = removed_regime_up_flags = 0
    for row in key_audit:
        if row["interval"] == "4h":
            b = base_by_ts.get(row["open_time_ms"])
            if b is not None:
                removed_entry_flags += int(bool(b.entry_bar_flag))
                removed_exit_flags += int(bool(b.exit_bar_flag))
                removed_regime_up_flags += int(bool(b.regime_up))
    return [
        {"metric":"4h_common_timestamps","baseline_value":len(base_by_ts),"quarantine_value":len(q_by_ts),"common_timestamps":len(common_ts),"changed_or_flipped":"" ,"meaning":"4h timestamps retained in both input scenarios"},
        {"metric":"4h_regime_up_flips_at_common_timestamps","baseline_value":"","quarantine_value":"","common_timestamps":len(common_ts),"changed_or_flipped":regime_flips,"meaning":"Changes to attached completed-1d regime state at common 4h bars"},
        {"metric":"4h_entry_bar_flag_flips_pre_position","baseline_value":"","quarantine_value":"","common_timestamps":len(common_ts),"changed_or_flipped":entry_flips,"meaning":"Pre-position breakout entry-rule boolean flips; not actual filled entries"},
        {"metric":"4h_exit_bar_flag_flips_pre_position","baseline_value":"","quarantine_value":"","common_timestamps":len(common_ts),"changed_or_flipped":exit_flips,"meaning":"Pre-position exit-rule boolean flips; not actual exits"},
        {"metric":"4h_prior_high20_changed_at_common_timestamps","baseline_value":"","quarantine_value":"","common_timestamps":len(common_ts),"changed_or_flipped":prior_high_changes,"meaning":"Rolling breakout threshold value changed or became/ceased missing"},
        {"metric":"4h_prior_low10_changed_at_common_timestamps","baseline_value":"","quarantine_value":"","common_timestamps":len(common_ts),"changed_or_flipped":prior_low_changes,"meaning":"Rolling exit threshold value changed or became/ceased missing"},
        {"metric":"1d_daily_ema_regime_flips_at_common_timestamps","baseline_value":"","quarantine_value":"","common_timestamps":len(daily_common),"changed_or_flipped":daily_regime_flips,"meaning":"Daily EMA20>EMA50 regime boolean flips, which is the higher-timeframe input to the 4h comparator"},
        {"metric":"removed_4h_rows_with_baseline_entry_bar_flag","baseline_value":removed_entry_flags,"quarantine_value":0,"common_timestamps":len(key_audit),"changed_or_flipped":removed_entry_flags,"meaning":"Removed bars that met the raw entry-rule boolean before position-state logic"},
        {"metric":"removed_4h_rows_with_baseline_exit_bar_flag","baseline_value":removed_exit_flags,"quarantine_value":0,"common_timestamps":len(key_audit),"changed_or_flipped":removed_exit_flags,"meaning":"Removed bars that met the raw exit-rule boolean before position-state logic"},
        {"metric":"removed_4h_rows_with_regime_up","baseline_value":removed_regime_up_flags,"quarantine_value":0,"common_timestamps":len(key_audit),"changed_or_flipped":removed_regime_up_flags,"meaning":"Removed bars where the attached daily regime was up"},
    ]


def trade_impact_rows(base_metrics, quarantine_metrics):
    rows = []
    for period in PERIODS:
        base_trades = base_metrics[period].get("trades", [])
        q_trades = quarantine_metrics[period].get("trades", [])
        def key(tr):
            return (str(tr.get("entry_time_utc","")), str(tr.get("exit_time_utc","")))
        bmap = {key(t):t for t in base_trades}
        qmap = {key(t):t for t in q_trades}
        shared = sorted(set(bmap) & set(qmap))
        base_only = sorted(set(bmap) - set(qmap))
        q_only = sorted(set(qmap) - set(bmap))
        rows.append({
            "period":period,
            "baseline_trade_count":len(base_trades),
            "quarantine_trade_count":len(q_trades),
            "shared_entry_exit_pairs":len(shared),
            "baseline_only_entry_exit_pairs":len(base_only),
            "quarantine_only_entry_exit_pairs":len(q_only),
            "baseline_only_pairs":";".join(f"{a}|{b}" for a,b in base_only),
            "quarantine_only_pairs":";".join(f"{a}|{b}" for a,b in q_only),
            "interpretation":"Trade-event comparison by exact (entry_time_utc, exit_time_utc), not by row count."
        })
    return rows


def make_report(summary: dict, performance_rows: list[dict], signal_rows: list[dict], trade_rows: list[dict]):
    lines = [
        "# CP-0040 Exact-Key Quarantine Sensitivity Audit",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Comparator: `{COMPARATOR}` (frozen; diagnostic-only)",
        "- Strategy and cost parameters were not tuned.",
        "- No network calls or market-data acquisition; production candidate builder not invoked.",
        "- Baseline replay must match frozen CP-0031 metric anchors before quarantine results are allowed.",
        "",
        "## Input impact (exact key only)",
        "",
        "| Interval | Baseline rows | Exact-key rows removed | Rows retained |",
        "|---|---:|---:|---:|",
    ]
    for rec in summary.get("input_impact",[]):
        lines.append(f"| {rec['interval']} | {rec['baseline_rows']} | {rec['removed_exact_key_rows']} | {rec['quarantine_rows_after_filter']} |")
    lines += ["", "## Metric deltas (quarantine minus baseline)", ""]
    if performance_rows:
        lines += ["| Period | Baseline net return % | Quarantine net return % | Delta percentage points | Baseline DD proxy % | Quarantine DD proxy % |",
                  "|---|---:|---:|---:|---:|---:|"]
        for r in performance_rows:
            lines.append(f"| {r['period']} | {float(r['baseline_net_return_pct']):.9f} | {float(r['quarantine_net_return_pct']):.9f} | {float(r['delta_net_return_percentage_points']):+.9f} | {float(r['baseline_max_intrabar_drawdown_proxy_pct']):.9f} | {float(r['quarantine_max_intrabar_drawdown_proxy_pct']):.9f} |")
    else:
        lines.append("Quarantine performance was not calculated because the prerequisite baseline metric reproducibility gate did not pass.")
    lines += ["", "## Signal/input effect (separate from PnL)", ""]
    for r in signal_rows:
        lines.append(f"- **{r['metric']}**: changed/flipped={r.get('changed_or_flipped','')}; common timestamps={r.get('common_timestamps','')}. {r['meaning']}")
    lines += ["", "## Actual trade-event deltas", ""]
    for r in trade_rows:
        lines.append(f"- **{r['period']}**: baseline trades={r['baseline_trade_count']}; quarantine trades={r['quarantine_trade_count']}; shared pairs={r['shared_entry_exit_pairs']}; baseline-only={r['baseline_only_entry_exit_pairs']}; quarantine-only={r['quarantine_only_entry_exit_pairs']}.")
    lines += [
        "",
        "## Interpretation and restrictions",
        "- This is a temporary exact-key omission sensitivity diagnostic. It does not declare daily or monthly archives canonical and does not resolve any row-level or aggregation blocker.",
        "- The TRAIN, DEVELOPMENT_CHECK and CONSUMED_OOS_DIAGNOSTIC windows are historic examined windows; none is pristine untouched OOS evidence.",
        "- The 1mo input is part of the frozen engine input bundle but has no exact-key overlap with the scoped manifest and is unchanged.",
        "- G0 remains `BLOCKED_GLOBAL`; all 11 non-row aggregation blockers remain open; candidate promotion and live signing/broadcast/orders remain blocked.",
    ]
    return "\n".join(lines) + "\n"


def main():
    from g0_execution_guard import require_authenticated_g0
    require_authenticated_g0("cp0040_quarantine_sensitivity_run")
    ap = argparse.ArgumentParser()
    ap.add_argument("--monthly-cache", default=".cache/aists/binance-monthly-archives")
    ap.add_argument("--daily-cache", default=".cache/aists/binance-daily-references")
    ap.add_argument("--anchors", default="evidence/source_adjudication/CP0040_Baseline_Reconstruction_Anchors.json")
    ap.add_argument("--metric-anchors", default="evidence/source_adjudication/CP0040_MTF_BREAKOUT_4H_D1_Metric_Anchors.json")
    ap.add_argument("--manifest-pointer", default="evidence/source_adjudication/CP0040_Current_Manifest.json")
    ap.add_argument("--scope-lock", default="evidence/source_adjudication/CP0040_Quarantine_Sensitivity_Scope_Lock_HI.md")
    ap.add_argument("--engine-payload", default="scripts/vendor/CP0031_Engine_R1.py.gz.b64")
    ap.add_argument("--flagged-dates", default="evidence/runs/38725478106_flagged_dates.csv")
    ap.add_argument("--output-dir", default="results/cp0040_quarantine_sensitivity_audit")
    args = ap.parse_args()
    output = (ROOT / args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    checks = []
    performance_rows = []
    signal_rows = []
    trade_rows = []
    key_audit = []
    input_impact = []
    baseline_metrics = {}
    quarantine_metrics = {}
    evidence = {}
    status = "FAIL_CLOSED_UNEXPECTED_ERROR"
    blocking_reason = ""

    def record(check_id, ok, detail):
        checks.append({"check_id":check_id,"status":"PASS" if ok else "FAIL","detail":str(detail)})
        if not ok:
            raise BlockedDiagnostic(f"{check_id}: {detail}")

    try:
        anchors, metric_anchors, pointer, manifest_rows, blockers, gate_evidence = validate_gate(
            ROOT/args.anchors, ROOT/args.metric_anchors, ROOT/args.manifest_pointer, ROOT/args.scope_lock
        )
        record("frozen_scope_and_gate_integrity", True, gate_evidence)

        with tempfile.TemporaryDirectory(prefix="cp0040-sensitivity-") as temp_name:
            temp = Path(temp_name)
            engine, engine_evidence = load_engine(ROOT/args.engine_payload, temp)
            evidence["engine"] = engine_evidence
            synthetic = engine.run_synthetic_tests()
            record("frozen_engine_synthetic_tests", synthetic.get("failed", 1) == 0, synthetic)

            reconstruction_output = temp/"reconstruction-output"
            reconstruction_stage = temp/"reconstructed-inputs"
            argv = [
                sys.executable, str(ROOT/"scripts/AISTS_CP0040_Baseline_Reconstruction_Audit.py"),
                "--monthly-cache", args.monthly_cache,
                "--daily-cache", args.daily_cache,
                "--anchors", args.anchors,
                "--flagged-dates", args.flagged_dates,
                "--output-dir", str(reconstruction_output),
                "--copy-reconstructed-to", str(reconstruction_stage),
            ]
            try:
                proc = subprocess.run(argv, cwd=str(ROOT), text=True, capture_output=True, timeout=1800)
            except subprocess.TimeoutExpired as exc:
                raise BlockedDiagnostic(f"Cache-only baseline reconstruction audit timed out: {exc}") from exc
            reconstruction_summary_path = reconstruction_output/"CP0040_Baseline_Reconstruction_Audit_Summary.json"
            reconstruction_summary = read_json(reconstruction_summary_path) if reconstruction_summary_path.is_file() else {}
            if proc.returncode != 0 or reconstruction_summary.get("status") != "PASS_BASELINE_INPUTS_RECONSTRUCTED":
                reason = reconstruction_summary.get("blocking_reason", proc.stderr[-3000:] or proc.stdout[-3000:] or "reconstruction status did not PASS")
                raise BlockedDiagnostic(f"Baseline input reconstruction gate failed: {reason}")
            record("cache_only_inputs_reconstructed", True, {
                "monthly_archives": reconstruction_summary.get("monthly_archives_used"),
                "daily_archives": reconstruction_summary.get("daily_reference_archives_used"),
                "daily_sidecars": reconstruction_summary.get("official_daily_sidecars_verified"),
                "network_used": reconstruction_summary.get("network_used"),
                "candidate_content_results": {
                    k:v.get("matches_frozen_content_anchor") for k,v in reconstruction_summary.get("candidate_content_results",{}).items()
                },
            })
            source_paths = {}
            for iv in INTERVALS:
                p = reconstruction_stage/f"BTCUSDT-{iv}-research-candidate.csv.gz"
                if not p.is_file():
                    raise BlockedDiagnostic(f"Reconstruction did not stage expected interval file: {iv}")
                anchor_item = anchors["input_content_anchors"][iv]
                raw = gzip.decompress(p.read_bytes())
                check_ok = sha_bytes(raw) == anchor_item["decompressed_sha256"] and len(raw) == int(anchor_item["decompressed_bytes"])
                record(f"staged_frozen_content_anchor:{iv}", check_ok, f"sha256={sha_bytes(raw)}; rows_anchor={anchor_item['rows']}")
                source_paths[iv] = p

            baseline_root = temp/"baseline-root"
            variant_root = temp/"quarantine-root"
            for target_root in (baseline_root,):
                for iv in INTERVALS:
                    dst = target_root/"derived"/"research_candidate_v1"/"BTCUSDT"/"intervals"/source_paths[iv].name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source_paths[iv], dst)
                (target_root/"reports").mkdir(parents=True, exist_ok=True)
                bm = {"schema_version":1,"checkpoint":"CP-0040","scope":"TEMPORARY_BASELINE_REPLAY",
                      "results":{iv:{"status":"PASS_HASH_ANCHORED_BASELINE","sha256":sha_file(target_root/"derived"/"research_candidate_v1"/"BTCUSDT"/"intervals"/source_paths[iv].name),
                                    "candidate_rows":int(anchors["input_content_anchors"][iv]["rows"])} for iv in INTERVALS}}
                write_json(target_root/"reports"/"cp0026_research_candidate_manifest.json",bm)
            key_audit, input_impact, qkey_map, quarantined_rows_by_iv = construct_quarantine_variant(
                source_paths, variant_root, manifest_rows, anchors
            )
            write_csv(output/"CP0040_Quarantine_Key_Application.csv", key_audit)
            write_csv(output/"CP0040_Input_Impact.csv", input_impact)
            record("exact_key_only_filter_scope", len(key_audit)==9 and sum(x["removed_exact_key_rows"] for x in input_impact)==9,
                   {"removed_keys":len(key_audit),"interval_counts":{x["interval"]:x["removed_exact_key_rows"] for x in input_impact}})

            bframes, bdaily, b4h = load_feature_scenario(engine, baseline_root)
            qframes, qdaily, q4h = load_feature_scenario(engine, variant_root)

            # Baseline metric gate is mandatory. Do not calculate quarantine performance if it fails.
            baseline_metrics, mismatches = compare_metric_anchors(engine, b4h, metric_anchors)
            if mismatches:
                summary = {
                    "schema_version":1,"checkpoint":"CP-0040","task":"cp0040_quarantine_sensitivity_run",
                    "status":"BLOCKED_BASELINE_METRICS_NOT_REPRODUCIBLE","started_at_utc":started,"finished_at_utc":utc_now(),
                    "network_used":False,"market_data_downloads":0,"production_candidate_build":False,"backtest_run":True,
                    "baseline_replay_run":True,"quarantine_sensitivity_run":False,"baseline_metric_gate":"FAIL","metric_mismatches":mismatches,"checks":checks,
                    "engine":engine_evidence,"gate":gate_evidence,"blocking_reason":"Frozen baseline metrics differ from historic CP-0031 anchors; quarantine scenario not simulated.",
                    "unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL","canonical_source":"NONE","strategy_promoted":False,
                    "live_signing_broadcast_orders":"BLOCKED",
                }
                write_json(output/"CP0040_Quarantine_Sensitivity_Audit_Summary.json",summary)
                (output/"CP0040_Quarantine_Sensitivity_Audit_Report_HI.md").write_text(
                    make_report(summary, [], [], []) + "\n## Baseline metric gate failed\n\n" +
                    json.dumps(mismatches,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
                write_csv(output/"CP0040_Baseline_Metric_Mismatches.csv",mismatches)
                print(json.dumps({"status":summary["status"],"mismatches":len(mismatches),"quarantine_performance_run":False},ensure_ascii=False))
                return 0
            record("historic_baseline_metrics_match", True, {"periods":list(PERIODS),"tolerance":NUMERIC_TOL,"metric_count":len(METRIC_FIELDS)*len(PERIODS)})

            # From this point only, run the single frozen comparator on the exact-key omission variant.
            performance_rows, baseline_metrics, quarantine_metrics, second_mismatches = build_metric_rows(
                engine, b4h, q4h, metric_anchors
            )
            if second_mismatches:
                raise BlockedDiagnostic(f"Unexpected baseline mismatch on metric row build: {second_mismatches}")
            trade_rows = trade_impact_rows(baseline_metrics, quarantine_metrics)
            signal_rows = signal_impact_rows(bframes, bdaily, b4h, qframes, qdaily, q4h, qkey_map, key_audit)

            write_csv(output/"CP0040_Quarantine_Performance.csv", performance_rows)
            write_csv(output/"CP0040_Quarantine_Signal_Impact.csv", signal_rows)
            write_csv(output/"CP0040_Quarantine_Trade_Impact.csv", trade_rows)
            write_csv(output/"CP0040_Quarantine_Key_Application.csv", key_audit)
            write_csv(output/"CP0040_Input_Impact.csv", input_impact)
            summary = {
                "schema_version":1,
                "checkpoint":"CP-0040",
                "task":"cp0040_quarantine_sensitivity_run",
                "status":"PASS_QUARANTINE_SENSITIVITY_DIAGNOSTIC_COMPLETE",
                "started_at_utc":started,"finished_at_utc":utc_now(),
                "scope":"SINGLE_FROZEN_COMPARATOR_EXACT_KEY_QUARANTINE_ONLY",
                "comparator":COMPARATOR,
                "baseline_metric_gate":"PASS",
                "baseline_metric_gate_tolerance_absolute":NUMERIC_TOL,
                "engine":engine_evidence,
                "anchors":{**gate_evidence,"snapshot_sha256":BASELINE_INPUT_SNAPSHOT_SHA256,
                           "baseline_input_anchors":anchors["input_content_anchors"]},
                "cache_reconstruction":{"monthly_archives":reconstruction_summary.get("monthly_archives_used"),
                    "daily_reference_archives":reconstruction_summary.get("daily_reference_archives_used"),
                    "official_daily_sidecars_verified":reconstruction_summary.get("official_daily_sidecars_verified"),
                    "network_used":False},
                "input_impact":input_impact,
                "removed_key_rows":key_audit,
                "baseline_metrics":{p:{k:baseline_metrics[p].get(k) for k in METRIC_FIELDS} for p in PERIODS},
                "quarantine_metrics":{p:{k:quarantine_metrics[p].get(k) for k in METRIC_FIELDS} for p in PERIODS},
                "performance_delta_semantics":"quarantine minus baseline; percentages in percentage points for return/drawdown/rates",
                "signal_impact":signal_rows,
                "trade_impact":trade_rows,
                "checks":checks,
                "checks_passed":sum(c["status"]=="PASS" for c in checks),
                "checks_total":len(checks),
                "network_used":False,"market_data_network_calls":0,"market_data_downloads":0,
                "backtest_run":True,"baseline_replay_run":True,"quarantine_sensitivity_run":True,
                "production_candidate_build":False,"canonical_source_selected":False,"strategy_promoted":False,
                "unresolved_nonrow_aggregation_blockers":11,
                "g0":"BLOCKED_GLOBAL","canonical_source":"NONE","candidate_promotion":"BLOCKED",
                "live_signing_broadcast_orders":"BLOCKED",
                "limitations":[
                    "No archive acquisition, exchange API, order placement, signing or broadcast occurred.",
                    "This diagnostic removes matching exact interval + open_time_ms keys only; it does not replace candles or round timestamps.",
                    "Signal rule flags are pre-position booleans; actual trade effects are separately compared using exact entry/exit timestamp pairs.",
                    "TRAIN, DEVELOPMENT_CHECK and CONSUMED_OOS_DIAGNOSTIC are previously inspected historical windows; none is pristine OOS.",
                    "The result cannot resolve the 11 aggregation relationship blockers or select a canonical source.",
                ],
            }
            write_json(output/"CP0040_Quarantine_Sensitivity_Audit_Summary.json", summary)
            (output/"CP0040_Quarantine_Sensitivity_Audit_Report_HI.md").write_text(
                make_report(summary, performance_rows, signal_rows, trade_rows),encoding="utf-8"
            )
            print(json.dumps({"status":summary["status"],"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
                              "input_impact":{x["interval"]:x["removed_exact_key_rows"] for x in input_impact},
                              "baseline_metric_gate":"PASS",
                              "deltas":{p:performance_rows[i]["delta_net_return_percentage_points"] for i,p in enumerate(PERIODS)},
                              "network_used":False,"backtest_run":True},ensure_ascii=False,sort_keys=True))
            return 0
    except BlockedDiagnostic as exc:
        blocking_reason = str(exc)
        status = "BLOCKED_CP0040_SENSITIVITY_GATE"
        summary = {
            "schema_version":1,"checkpoint":"CP-0040","task":"cp0040_quarantine_sensitivity_run",
            "status":status,"started_at_utc":started,"finished_at_utc":utc_now(),
            "scope":"SINGLE_FROZEN_COMPARATOR_EXACT_KEY_QUARANTINE_ONLY",
            "blocking_reason":blocking_reason,"checks":checks,"checks_passed":sum(c["status"]=="PASS" for c in checks),
            "checks_total":len(checks),"network_used":False,"market_data_network_calls":0,"market_data_downloads":0,
            "production_candidate_build":False,"backtest_run":False,"canonical_source_selected":False,
            "strategy_promoted":False,"unresolved_nonrow_aggregation_blockers":11,"g0":"BLOCKED_GLOBAL",
            "canonical_source":"NONE","candidate_promotion":"BLOCKED","live_signing_broadcast_orders":"BLOCKED",
        }
        write_json(output/"CP0040_Quarantine_Sensitivity_Audit_Summary.json",summary)
        (output/"CP0040_Quarantine_Sensitivity_Audit_Report_HI.md").write_text(
            make_report(summary, performance_rows, signal_rows, trade_rows) + f"\n## Block reason\n\n- {blocking_reason}\n",
            encoding="utf-8")
        if key_audit: write_csv(output/"CP0040_Quarantine_Key_Application.csv",key_audit)
        if input_impact: write_csv(output/"CP0040_Input_Impact.csv",input_impact)
        print(json.dumps({"status":status,"blocking_reason":blocking_reason,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"]},ensure_ascii=False))
        return 0
    except Exception as exc:
        summary = {
            "schema_version":1,"checkpoint":"CP-0040","task":"cp0040_quarantine_sensitivity_run",
            "status":"FAIL_CLOSED_UNEXPECTED_ERROR","started_at_utc":started,"finished_at_utc":utc_now(),
            "error_type":type(exc).__name__,"error":str(exc),"checks":checks,
            "network_used":False,"market_data_downloads":0,"production_candidate_build":False,
            "backtest_run":False,"strategy_promoted":False,"g0":"BLOCKED_GLOBAL","canonical_source":"NONE",
            "unresolved_nonrow_aggregation_blockers":11,"live_signing_broadcast_orders":"BLOCKED",
        }
        write_json(output/"CP0040_Quarantine_Sensitivity_Audit_Summary.json",summary)
        (output/"CP0040_Quarantine_Sensitivity_Audit_Report_HI.md").write_text(
            "# CP-0040 Quarantine Sensitivity Audit\n\n- Status: `FAIL_CLOSED_UNEXPECTED_ERROR`\n- Error: " +
            type(exc).__name__ + ": " + str(exc) + "\n- No promotion or live exchange action occurred.\n",encoding="utf-8")
        print(json.dumps({"status":summary["status"],"error_type":type(exc).__name__,"error":str(exc)},ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
