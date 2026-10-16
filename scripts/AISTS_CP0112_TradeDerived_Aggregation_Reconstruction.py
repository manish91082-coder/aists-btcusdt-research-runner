#!/usr/bin/env python3
"""Reconstruct exact target candle windows from official daily Spot trades and compare frozen rows."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOST = "data.binance.vision"
EXPECTED_RULEBOOK_SHA256 = "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0"
TARGET_INTERVALS_MS = {"5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000}
TRADE_COLUMNS = 7
TIMEOUT_SECONDS = 90
MAX_SIDECAR_BYTES = 4096
MAX_ARCHIVE_BYTES_EACH = 512 * 1024 * 1024
MAX_ARCHIVE_BYTES_TOTAL = 2 * 1024 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024
DATES = (
    "2017-12-04",
    "2018-02-05",
    "2018-02-07",
    "2018-03-04",
    "2018-03-20",
    "2018-06-20",
    "2018-09-05",
)
METRIC_MAP = {
    "open": "raw_open",
    "high": "raw_high",
    "low": "raw_low",
    "close": "raw_close",
    "volume": "raw_volume",
    "quote_asset_volume": "raw_quote_asset_volume",
    "number_of_trades": "raw_number_of_trades",
    "taker_buy_base_asset_volume": "raw_taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume": "raw_taker_buy_quote_asset_volume",
}
DECIMAL_METRICS = {
    "open", "high", "low", "close", "volume", "quote_asset_volume",
    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume",
}


class SameHostHTTPSRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
            raise urllib.error.HTTPError(
                newurl, code, "Blocked redirect outside official HTTPS host", headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK_BYTES), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def utc_ms(value: str) -> int:
    dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def build_archive_urls(day: str) -> dict:
    filename = "BTCUSDT-trades-" + day + ".zip"
    base = "https://" + OFFICIAL_HOST + "/data/spot/daily/trades/BTCUSDT/"
    for u in (base + filename, base + filename + ".CHECKSUM"):
        parsed = urlparse(u)
        if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
            raise ValueError("Fixed target failed official-host allowlist")
    return {
        "utc_date": day,
        "archive_filename": filename,
        "archive_url": base + filename,
        "sidecar_url": base + filename + ".CHECKSUM",
        "sidecar_filename": filename + ".CHECKSUM",
    }


def fetch_sidecar(target: dict, opener) -> dict:
    request = urllib.request.Request(
        target["sidecar_url"],
        headers={"User-Agent": "AISTS-CP0112-TradeDerived-Reconstruction/1.0", "Accept": "text/plain"},
        method="GET",
    )
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
        final_url = response.geturl()
        status = getattr(response, "status", None)
        body = response.read(MAX_SIDECAR_BYTES + 1)
    final = urlparse(final_url)
    if final.scheme != "https" or final.hostname != OFFICIAL_HOST or status != 200:
        raise ValueError("Checksum sidecar did not return HTTP 200 from the allowlisted host")
    if len(body) > MAX_SIDECAR_BYTES:
        raise ValueError("Checksum sidecar exceeded text-size limit")
    text = body.decode("utf-8", errors="strict").strip()
    tokens = re.findall(r"(?i)(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text)
    if len(tokens) != 1 or target["archive_filename"] not in text:
        raise ValueError("Checksum sidecar filename/token validation failed")
    return {
        "sidecar_http_status": status,
        "sidecar_final_url": final_url,
        "sidecar_body_bytes": len(body),
        "sidecar_body_sha256": sha_bytes(body),
        "sidecar_body_text": text,
        "expected_archive_sha256": tokens[0].lower(),
    }


def download_archive(target: dict, expected_sha256: str, opener, target_dir: Path,
                     remaining_budget: int) -> dict:
    archive_path = target_dir / target["archive_filename"]
    request = urllib.request.Request(
        target["archive_url"],
        headers={"User-Agent": "AISTS-CP0112-TradeDerived-Reconstruction/1.0", "Accept": "application/zip"},
        method="GET",
    )
    digest = hashlib.sha256()
    size = 0
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response, archive_path.open("wb") as output:
        final_url = response.geturl()
        status = getattr(response, "status", None)
        headers = response.headers
        final = urlparse(final_url)
        if final.scheme != "https" or final.hostname != OFFICIAL_HOST or status != 200:
            raise ValueError("Trade archive did not return HTTP 200 from allowlisted host")
        declared_text = headers.get("Content-Length")
        declared = int(declared_text) if declared_text and declared_text.isdigit() else None
        if declared is not None and declared > MAX_ARCHIVE_BYTES_EACH:
            raise ValueError("Archive exceeds fixed per-file download budget")
        if declared is not None and declared > remaining_budget:
            raise ValueError("Archive exceeds remaining aggregate download budget")
        while True:
            block = response.read(CHUNK_BYTES)
            if not block:
                break
            size += len(block)
            if size > MAX_ARCHIVE_BYTES_EACH or size > remaining_budget:
                raise ValueError("Streamed archive exceeded fixed download budget")
            digest.update(block)
            output.write(block)
        output.flush()
    actual_sha256 = digest.hexdigest()
    content_length_matches = declared == size if declared is not None else None
    sha_matches = actual_sha256 == expected_sha256
    return {
        "archive_http_status": status,
        "archive_final_url": final_url,
        "archive_last_modified": headers.get("Last-Modified"),
        "archive_etag": headers.get("ETag"),
        "archive_content_length_header": declared,
        "archive_bytes": size,
        "archive_actual_sha256": actual_sha256,
        "archive_sha256_matches_sidecar": sha_matches,
        "content_length_matches_downloaded_bytes": content_length_matches,
        "archive_path": str(archive_path),
        "integrity_status": (
            "PASS" if sha_matches and content_length_matches is not False else "FAIL"
        ),
    }


def interval_ms(interval: str) -> int:
    if interval not in TARGET_INTERVALS_MS:
        raise ValueError("Unexpected bucket interval " + interval)
    return TARGET_INTERVALS_MS[interval]


def create_target_bars(bucket_rows: list[dict]) -> tuple[dict, list[dict]]:
    bars = {}
    memberships = []
    for row in bucket_rows:
        case_id = row["case_id"]
        child_interval = row["child_interval"]
        parent_interval = row["parent_interval"]
        start = utc_ms(row["bucket_utc"])
        child_ms = interval_ms(child_interval)
        parent_ms = interval_ms(parent_interval)
        if parent_ms % child_ms:
            raise ValueError("Parent interval is not an integer multiple of child interval: " + case_id)
        case_keys = []
        parent_key = (parent_interval, start)
        for role, interval, bar_start in [("PARENT", parent_interval, start)]:
            key = (interval, bar_start)
            case_keys.append((role, key))
        for i in range(parent_ms // child_ms):
            key = (child_interval, start + i * child_ms)
            case_keys.append(("CHILD", key))
        for role, key in case_keys:
            interval, open_ms = key
            if key not in bars:
                bars[key] = {
                    "interval": interval,
                    "open_time_ms": open_ms,
                    "open_time_utc": datetime.fromtimestamp(open_ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                    "duration_ms": interval_ms(interval),
                    "end_time_ms": open_ms + interval_ms(interval),
                    "case_ids": [],
                    "roles": [],
                    "trade_count": 0,
                    "open": None,
                    "high": None,
                    "low": None,
                    "close": None,
                    "volume": Decimal(0),
                    "quote_asset_volume": Decimal(0),
                    "number_of_trades": 0,
                    "taker_buy_base_asset_volume": Decimal(0),
                    "taker_buy_quote_asset_volume": Decimal(0),
                    "first_trade_id": None,
                    "last_trade_id": None,
                    "previous_close_used_for_zero_trade_bar": False,
                    "zero_trade_ohlc_unavailable": False,
                    "finalized": False,
                }
            if case_id not in bars[key]["case_ids"]:
                bars[key]["case_ids"].append(case_id)
            if role not in bars[key]["roles"]:
                bars[key]["roles"].append(role)
        memberships.append({
            "case_id": case_id,
            "child_interval": child_interval,
            "parent_interval": parent_interval,
            "bucket_utc": row["bucket_utc"],
            "start_time_ms": start,
            "child_bar_count": parent_ms // child_ms,
            "parent_key": parent_key,
            "child_keys": [(child_interval, start + i * child_ms) for i in range(parent_ms // child_ms)],
        })
    return bars, memberships


def load_frozen_rows(path: Path, bars: dict) -> tuple[dict, dict]:
    data = read_csv(path)
    keyed = {"DAILY": {}, "MONTHLY": {}}
    duplicate_rows = 0
    unresolved_rows = 0
    conflicts = []
    metric_names = list(METRIC_MAP)
    for row in data:
        source = row.get("source", "")
        if source not in keyed:
            continue
        if row.get("row_found") != "True":
            unresolved_rows += 1
            continue
        interval = row.get("interval", "")
        open_ms = int(row.get("expected_open_time_ms", ""))
        key = (interval, open_ms)
        if key not in bars:
            continue
        identity = (source, key)
        compare_values = tuple(row.get(METRIC_MAP[name], "") for name in metric_names) + (
            row.get("raw_open_time", ""), row.get("raw_close_time", "")
        )
        if key in keyed[source]:
            duplicate_rows += 1
            old = keyed[source][key]
            old_values = tuple(old.get(METRIC_MAP[name], "") for name in metric_names) + (
                old.get("raw_open_time", ""), old.get("raw_close_time", "")
            )
            if old_values != compare_values:
                conflicts.append({"source": source, "interval": interval, "open_time_ms": open_ms, "case_id": row.get("bucket_case_id", "")})
        else:
            keyed[source][key] = row
    coverage = {
        "row_evidence_rows": len(data),
        "daily_unique_target_keys": len(keyed["DAILY"]),
        "monthly_unique_target_keys": len(keyed["MONTHLY"]),
        "expected_unique_target_bars": len(bars),
        "daily_missing_keys": [
            {"interval": i, "open_time_ms": t} for i, t in sorted(bars) if (i, t) not in keyed["DAILY"]
        ],
        "monthly_missing_keys": [
            {"interval": i, "open_time_ms": t} for i, t in sorted(bars) if (i, t) not in keyed["MONTHLY"]
        ],
        "duplicate_evidence_rows": duplicate_rows,
        "conflicting_duplicate_rows": conflicts,
        "unresolved_row_records": unresolved_rows,
    }
    return keyed, coverage


def set_zero_trade_ohlc(bar: dict, previous_price: Decimal | None) -> None:
    if bar["trade_count"] != 0:
        bar["finalized"] = True
        return
    if previous_price is None:
        bar["zero_trade_ohlc_unavailable"] = True
    else:
        bar["open"] = previous_price
        bar["high"] = previous_price
        bar["low"] = previous_price
        bar["close"] = previous_price
        bar["previous_close_used_for_zero_trade_bar"] = True
    bar["finalized"] = True


def apply_trade(bar: dict, trade_id: int, price: Decimal, qty: Decimal,
                quote_qty: Decimal, is_buyer_maker: bool) -> None:
    if bar["trade_count"] == 0:
        bar["open"] = price
        bar["high"] = price
        bar["low"] = price
        bar["first_trade_id"] = trade_id
    else:
        if price > bar["high"]:
            bar["high"] = price
        if price < bar["low"]:
            bar["low"] = price
    bar["close"] = price
    bar["trade_count"] += 1
    bar["number_of_trades"] += 1
    bar["volume"] += qty
    bar["quote_asset_volume"] += quote_qty
    if not is_buyer_maker:
        bar["taker_buy_base_asset_volume"] += qty
        bar["taker_buy_quote_asset_volume"] += quote_qty
    bar["last_trade_id"] = trade_id


def reconstruct_day(target: dict, archive_path: Path, bars: dict) -> dict:
    day_bars = [
        b for b in bars.values()
        if datetime.fromtimestamp(b["open_time_ms"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d") == target["utc_date"]
    ]
    day_bars.sort(key=lambda b: (b["end_time_ms"], b["open_time_ms"], b["interval"]))
    for b in day_bars:
        b["finalized"] = False
    by_key = {(b["interval"], b["open_time_ms"]): b for b in day_bars}
    day_start_ms = utc_ms(target["utc_date"] + "T00:00:00Z")
    day_end_ms = day_start_ms + 86_400_000
    archive_checks = {
        "trade_rows": 0,
        "first_trade_id": None,
        "last_trade_id": None,
        "first_trade_time_ms": None,
        "last_trade_time_ms": None,
        "rows_outside_day": 0,
        "invalid_rows": 0,
        "trade_id_gaps": 0,
        "trade_id_duplicates": 0,
        "trade_id_decreases": 0,
        "timestamp_decreases": 0,
        "gap_examples": [],
    }
    previous_id = None
    previous_time = None
    previous_price = None
    end_index = 0
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            members = [m for m in zf.infolist() if not m.is_dir()]
            expected_member = target["archive_filename"][:-4] + ".csv"
            if len(members) != 1 or Path(members[0].filename).name != expected_member:
                raise ValueError("Unexpected ZIP member layout for " + target["utc_date"])
            bad_member = zf.testzip()
            if bad_member is not None:
                raise ValueError("ZIP CRC failed: " + str(bad_member))
            with zf.open(members[0], "r") as raw, io.TextIOWrapper(raw, encoding="utf-8", errors="strict", newline="") as text:
                reader = csv.reader(text)
                for row in reader:
                    if len(row) != TRADE_COLUMNS:
                        archive_checks["invalid_rows"] += 1
                        continue
                    try:
                        trade_id = int(row[0])
                        price = Decimal(row[1])
                        qty = Decimal(row[2])
                        quote_qty = Decimal(row[3])
                        trade_time = int(row[4])
                        if not (price.is_finite() and qty.is_finite() and quote_qty.is_finite()):
                            raise InvalidOperation("non-finite numeric")
                        if price <= 0 or qty < 0 or quote_qty < 0:
                            raise InvalidOperation("invalid price/quantity")
                        if row[5] not in ("True", "False", "true", "false") or row[6] not in ("True", "False", "true", "false"):
                            raise ValueError("invalid boolean token")
                        is_buyer_maker = row[5].lower() == "true"
                    except Exception:
                        archive_checks["invalid_rows"] += 1
                        continue
                    if previous_id is not None:
                        if trade_id == previous_id:
                            archive_checks["trade_id_duplicates"] += 1
                        elif trade_id < previous_id:
                            archive_checks["trade_id_decreases"] += 1
                        elif trade_id > previous_id + 1:
                            archive_checks["trade_id_gaps"] += 1
                            if len(archive_checks["gap_examples"]) < 5:
                                archive_checks["gap_examples"].append([previous_id, trade_id])
                    if previous_time is not None and trade_time < previous_time:
                        archive_checks["timestamp_decreases"] += 1
                    if archive_checks["trade_rows"] == 0:
                        archive_checks["first_trade_id"] = trade_id
                        archive_checks["first_trade_time_ms"] = trade_time
                    archive_checks["last_trade_id"] = trade_id
                    archive_checks["last_trade_time_ms"] = trade_time
                    archive_checks["trade_rows"] += 1
                    if not (day_start_ms <= trade_time < day_end_ms):
                        archive_checks["rows_outside_day"] += 1
                    if previous_time is not None and trade_time < previous_time:
                        raise ValueError("Timestamp order violation prevents exact interval streaming reconstruction")
                    while end_index < len(day_bars) and day_bars[end_index]["end_time_ms"] <= trade_time:
                        set_zero_trade_ohlc(day_bars[end_index], previous_price)
                        end_index += 1
                    for interval, duration in TARGET_INTERVALS_MS.items():
                        open_ms = (trade_time // duration) * duration
                        bar = by_key.get((interval, open_ms))
                        if bar is not None:
                            apply_trade(bar, trade_id, price, qty, quote_qty, is_buyer_maker)
                    previous_id = trade_id
                    previous_time = trade_time
                    previous_price = price
        while end_index < len(day_bars):
            set_zero_trade_ohlc(day_bars[end_index], previous_price)
            end_index += 1
    except Exception as exc:
        return {
            "utc_date": target["utc_date"],
            "status": "REVIEW_REQUIRED_TRADE_STREAM_RECONSTRUCTION",
            "error": type(exc).__name__ + ": " + str(exc)[:500],
            "archive_checks": archive_checks,
        }
    status = (
        "PASS_RECONSTRUCTED_TRADE_STREAM"
        if archive_checks["trade_rows"] > 0
        and archive_checks["invalid_rows"] == 0
        and archive_checks["rows_outside_day"] == 0
        and archive_checks["trade_id_gaps"] == 0
        and archive_checks["trade_id_duplicates"] == 0
        and archive_checks["trade_id_decreases"] == 0
        and archive_checks["timestamp_decreases"] == 0
        and all(b["finalized"] for b in day_bars)
        and all(not b["zero_trade_ohlc_unavailable"] for b in day_bars)
        else "REVIEW_REQUIRED_TRADE_STREAM_QUALITY"
    )
    return {"utc_date": target["utc_date"], "status": status, "archive_checks": archive_checks}


def decimal_string(v: Decimal | None) -> str:
    if v is None:
        return ""
    return format(v, "f")


def reconstructed_metrics(bar: dict) -> dict:
    return {
        "open": decimal_string(bar["open"]),
        "high": decimal_string(bar["high"]),
        "low": decimal_string(bar["low"]),
        "close": decimal_string(bar["close"]),
        "volume": decimal_string(bar["volume"]),
        "quote_asset_volume": decimal_string(bar["quote_asset_volume"]),
        "number_of_trades": str(bar["number_of_trades"]),
        "taker_buy_base_asset_volume": decimal_string(bar["taker_buy_base_asset_volume"]),
        "taker_buy_quote_asset_volume": decimal_string(bar["taker_buy_quote_asset_volume"]),
    }


def compare_source(bar: dict, source_row: dict | None) -> dict:
    if source_row is None:
        return {"source_row_present": False, "matched_fields": 0, "compared_fields": len(METRIC_MAP), "mismatch_fields": list(METRIC_MAP)}
    derived = reconstructed_metrics(bar)
    mismatches = []
    for metric, raw_name in METRIC_MAP.items():
        raw_value = source_row.get(raw_name, "")
        derived_value = derived[metric]
        if raw_value == "" or derived_value == "":
            mismatches.append(metric)
            continue
        try:
            if metric in DECIMAL_METRICS:
                same = Decimal(raw_value) == Decimal(derived_value)
            elif metric == "number_of_trades":
                same = int(raw_value) == int(derived_value)
            else:
                same = raw_value == derived_value
        except Exception:
            same = False
        if not same:
            mismatches.append(metric)
    close_time_expected = bar["end_time_ms"] - 1
    source_open_match = int(source_row.get("raw_open_time", "-1")) == bar["open_time_ms"]
    source_close_match = int(source_row.get("raw_close_time", "-1")) == close_time_expected
    return {
        "source_row_present": True,
        "matched_fields": len(METRIC_MAP) - len(mismatches),
        "compared_fields": len(METRIC_MAP),
        "mismatch_fields": mismatches,
        "source_open_time_match": source_open_match,
        "source_close_time_matches_expected_boundary": source_close_match,
    }


def rollup_child_bars(child_bars: list[dict]) -> dict:
    child_bars = sorted(child_bars, key=lambda b: b["open_time_ms"])
    metrics = {
        "open": child_bars[0]["open"],
        "high": max(b["high"] for b in child_bars if b["high"] is not None),
        "low": min(b["low"] for b in child_bars if b["low"] is not None),
        "close": child_bars[-1]["close"],
        "volume": sum((b["volume"] for b in child_bars), Decimal(0)),
        "quote_asset_volume": sum((b["quote_asset_volume"] for b in child_bars), Decimal(0)),
        "number_of_trades": sum(b["number_of_trades"] for b in child_bars),
        "taker_buy_base_asset_volume": sum((b["taker_buy_base_asset_volume"] for b in child_bars), Decimal(0)),
        "taker_buy_quote_asset_volume": sum((b["taker_buy_quote_asset_volume"] for b in child_bars), Decimal(0)),
    }
    return metrics


def compare_parent_to_rollup(parent: dict, rollup: dict) -> list[str]:
    parent_metrics = reconstructed_metrics(parent)
    mismatches = []
    for metric in METRIC_MAP:
        p = parent_metrics[metric]
        c = decimal_string(rollup[metric]) if metric in DECIMAL_METRICS else str(rollup[metric])
        if metric in DECIMAL_METRICS:
            same = Decimal(p) == Decimal(c) if p != "" and c != "" else False
        else:
            same = int(p) == int(c) if p != "" and c != "" else False
        if not same:
            mismatches.append(metric)
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-evidence", default="evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv")
    parser.add_argument("--bucket-snapshot", default="evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv")
    parser.add_argument("--rulebook", default="evidence/source_adjudication/CP0040_Original_Frozen_Strategy_Acceptance_Rulebook_HI.md")
    parser.add_argument("--output-dir", default="results/cp0112_trade_derived_reconstruction")
    args = parser.parse_args()
    row_path = (ROOT / args.row_evidence).resolve()
    bucket_path = (ROOT / args.bucket_snapshot).resolve()
    rulebook_path = (ROOT / args.rulebook).resolve()
    output = (ROOT / args.output_dir).resolve()
    if not all(ROOT in p.parents for p in (row_path, bucket_path, rulebook_path, output)):
        raise ValueError("All paths must remain inside repository root")
    for p in (row_path, bucket_path, rulebook_path):
        if not p.is_file():
            raise FileNotFoundError(str(p))
    rulebook_sha256 = sha_file(rulebook_path)
    if rulebook_sha256 != EXPECTED_RULEBOOK_SHA256:
        raise ValueError("Frozen CP-0040 rulebook SHA-256 mismatch; refusing reconstruction")
    row_evidence_sha256 = sha_file(row_path)
    bucket_snapshot_sha256 = sha_file(bucket_path)
    bucket_rows = read_csv(bucket_path)
    if len(bucket_rows) != 11:
        raise ValueError("Expected exactly 11 frozen CP-0107 aggregation buckets")
    bars, memberships = create_target_bars(bucket_rows)
    sources, source_coverage = load_frozen_rows(row_path, bars)
    if source_coverage["conflicting_duplicate_rows"]:
        raise ValueError("Frozen row evidence repeats a target key with conflicting raw values")
    opener = urllib.request.build_opener(SameHostHTTPSRedirectHandler())
    targets = [build_archive_urls(day) for day in DATES]
    date_set = {datetime.fromtimestamp(b["open_time_ms"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d") for b in bars.values()}
    if date_set != set(DATES):
        raise ValueError("Target dates and frozen buckets do not match")
    archive_checks = []
    total_download_bytes = 0
    with tempfile.TemporaryDirectory(prefix="cp0112-trade-rebuild-", dir=str(output if output.exists() else ROOT)) as temp:
        temp_dir = Path(temp)
        for target in targets:
            rec = {**target, "status": "NOT_RUN", "market_data_rest_api_used": False}
            try:
                sidecar = fetch_sidecar(target, opener)
                rec.update(sidecar)
                downloaded = download_archive(
                    target, sidecar["expected_archive_sha256"], opener, temp_dir,
                    MAX_ARCHIVE_BYTES_TOTAL - total_download_bytes
                )
                rec.update(downloaded)
                total_download_bytes += downloaded["archive_bytes"]
                if downloaded["integrity_status"] != "PASS":
                    rec["status"] = "FAIL_ARCHIVE_INTEGRITY"
                    archive_checks.append(rec)
                    continue
                day = reconstruct_day(target, Path(downloaded["archive_path"]), bars)
                rec.update(day)
                rec["status"] = day["status"]
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError, zipfile.BadZipFile) as exc:
                rec["status"] = "ERROR_OR_INTEGRITY_FAILURE"
                rec["error"] = type(exc).__name__ + ": " + str(exc)[:500]
            except Exception as exc:
                rec["status"] = "UNEXPECTED_RECONSTRUCTION_ERROR"
                rec["error"] = type(exc).__name__ + ": " + str(exc)[:500]
            archive_checks.append(rec)

    # Independent comparison to preserved daily/monthly rows.
    bar_rows = []
    for key, bar in sorted(bars.items(), key=lambda item: (item[0][1], interval_ms(item[0][0]), item[0][0])):
        daily_compare = compare_source(bar, sources["DAILY"].get(key))
        monthly_compare = compare_source(bar, sources["MONTHLY"].get(key))
        reconstructed = reconstructed_metrics(bar)
        bar_rows.append({
            "interval": bar["interval"],
            "open_time_ms": bar["open_time_ms"],
            "open_time_utc": bar["open_time_utc"],
            "end_time_ms_exclusive": bar["end_time_ms"],
            "case_ids": ";".join(bar["case_ids"]),
            "roles": ";".join(bar["roles"]),
            "zero_trade_ohlc_carried_previous_close": bar["previous_close_used_for_zero_trade_bar"],
            "zero_trade_ohlc_unavailable": bar["zero_trade_ohlc_unavailable"],
            **{"trade_" + key: value for key, value in reconstructed.items()},
            "daily_row_present": daily_compare["source_row_present"],
            "daily_match_fields": daily_compare["matched_fields"],
            "daily_compared_fields": daily_compare["compared_fields"],
            "daily_mismatch_fields": ";".join(daily_compare.get("mismatch_fields", [])),
            "daily_open_time_exact": daily_compare.get("source_open_time_match", False),
            "daily_close_time_boundary_exact": daily_compare.get("source_close_time_matches_expected_boundary", False),
            "monthly_row_present": monthly_compare["source_row_present"],
            "monthly_match_fields": monthly_compare["matched_fields"],
            "monthly_compared_fields": monthly_compare["compared_fields"],
            "monthly_mismatch_fields": ";".join(monthly_compare.get("mismatch_fields", [])),
            "monthly_open_time_exact": monthly_compare.get("source_open_time_match", False),
            "monthly_close_time_boundary_exact": monthly_compare.get("source_close_time_matches_expected_boundary", False),
        })

    bucket_rows_out = []
    for m in memberships:
        parent = bars[m["parent_key"]]
        children = [bars[k] for k in m["child_keys"]]
        rollup = rollup_child_bars(children)
        internal_mismatches = compare_parent_to_rollup(parent, rollup)
        all_keys = [m["parent_key"]] + m["child_keys"]
        source_results = {}
        for source in ("DAILY", "MONTHLY"):
            compares = [compare_source(bars[k], sources[source].get(k)) for k in all_keys]
            source_results[source] = {
                "all_exact": all(x["source_row_present"] and not x["mismatch_fields"]
                                 and x.get("source_open_time_match") is True
                                 and x.get("source_close_time_matches_expected_boundary") is True for x in compares),
                "exact_bars": sum(1 for x in compares if x["source_row_present"] and not x["mismatch_fields"]),
                "bar_count": len(all_keys),
                "mismatch_fields": sorted(set(y for x in compares for y in x.get("mismatch_fields", []))),
                "open_or_close_boundary_issue_count": sum(
                    1 for x in compares if x["source_row_present"] and (
                        x.get("source_open_time_match") is not True
                        or x.get("source_close_time_matches_expected_boundary") is not True
                    )
                ),
            }
        bucket_rows_out.append({
            "case_id": m["case_id"],
            "child_interval": m["child_interval"],
            "parent_interval": m["parent_interval"],
            "bucket_utc": m["bucket_utc"],
            "child_key_count": len(children),
            "direct_trade_parent_rollup_mismatch_fields": ";".join(internal_mismatches),
            "direct_trade_parent_rollup_exact": not internal_mismatches,
            "daily_all_target_bars_exactly_match_trade_reconstruction": source_results["DAILY"]["all_exact"],
            "daily_exact_target_bars": source_results["DAILY"]["exact_bars"],
            "daily_compared_target_bars": source_results["DAILY"]["bar_count"],
            "daily_mismatch_fields": ";".join(source_results["DAILY"]["mismatch_fields"]),
            "daily_open_close_boundary_issue_count": source_results["DAILY"]["open_or_close_boundary_issue_count"],
            "monthly_all_target_bars_exactly_match_trade_reconstruction": source_results["MONTHLY"]["all_exact"],
            "monthly_exact_target_bars": source_results["MONTHLY"]["exact_bars"],
            "monthly_compared_target_bars": source_results["MONTHLY"]["bar_count"],
            "monthly_mismatch_fields": ";".join(source_results["MONTHLY"]["mismatch_fields"]),
            "monthly_open_close_boundary_issue_count": source_results["MONTHLY"]["open_or_close_boundary_issue_count"],
            "canonical_source_selected": False,
            "case_closed": False,
        })

    integrity_pass = len(archive_checks) == len(DATES) and all(
        r.get("archive_sha256_matches_sidecar") is True
        and r.get("integrity_status") == "PASS"
        and r.get("status") == "PASS_RECONSTRUCTED_TRADE_STREAM"
        for r in archive_checks
    )
    target_rows_complete = (
        not source_coverage["daily_missing_keys"]
        and not source_coverage["monthly_missing_keys"]
        and len(bars) > 0
        and all(not b["zero_trade_ohlc_unavailable"] for b in bars.values())
    )
    internal_rollups_pass = len(bucket_rows_out) == 11 and all(r["direct_trade_parent_rollup_exact"] for r in bucket_rows_out)
    if integrity_pass and target_rows_complete and internal_rollups_pass:
        status = "PASS_TRADE_DERIVED_RECONSTRUCTION_COMPLETE_SOURCE_AUTHORITY_OPEN"
    else:
        status = "REVIEW_REQUIRED_TRADE_DERIVED_RECONSTRUCTION_INPUT_OR_ROLLUP_GAP"

    daily_exact_bars = sum(1 for r in bar_rows if r["daily_row_present"] and not r["daily_mismatch_fields"])
    monthly_exact_bars = sum(1 for r in bar_rows if r["monthly_row_present"] and not r["monthly_mismatch_fields"])
    daily_match_fields = sum(r["daily_match_fields"] for r in bar_rows)
    monthly_match_fields = sum(r["monthly_match_fields"] for r in bar_rows)
    archive_fields = [
        "utc_date","archive_filename","archive_url","sidecar_url","expected_archive_sha256",
        "sidecar_body_sha256","sidecar_body_bytes","archive_bytes","archive_actual_sha256",
        "archive_sha256_matches_sidecar","archive_http_status","archive_last_modified","archive_etag",
        "integrity_status","status","trade_rows","first_trade_id","last_trade_id",
        "first_trade_time_ms","last_trade_time_ms","rows_outside_day","invalid_rows","trade_id_gaps",
        "trade_id_duplicates","trade_id_decreases","timestamp_decreases","gap_examples","error",
    ]
    for r in archive_checks:
        if isinstance(r.get("gap_examples"), list):
            r["gap_examples"] = json.dumps(r["gap_examples"], separators=(",", ":"))
    output = (ROOT / args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    archive_csv = output / "CP0112_Trade_Archive_Integrity.csv"
    bar_csv = output / "CP0112_TradeDerived_Bar_Comparison.csv"
    bucket_csv = output / "CP0112_Aggregation_Bucket_TradeReconstruction.csv"
    summary_path = output / "CP0112_TradeDerived_Reconstruction_Summary.json"
    report_path = output / "CP0112_TradeDerived_Reconstruction_Report_HI.md"
    write_csv(archive_csv, archive_checks, archive_fields)
    bar_fields = list(bar_rows[0].keys()) if bar_rows else ["interval","open_time_ms"]
    write_csv(bar_csv, bar_rows, bar_fields)
    bucket_fields = list(bucket_rows_out[0].keys()) if bucket_rows_out else ["case_id"]
    write_csv(bucket_csv, bucket_rows_out, bucket_fields)

    rulebook_identity = {
        "path": str(rulebook_path.relative_to(ROOT)),
        "sha256": rulebook_sha256,
    }
    summary = {
        "schema_version": 1,
        "checkpoint": "CP-0112",
        "task": "cp0112_trade_derived_aggregation_reconstruction",
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "frozen_buckets": len(bucket_rows_out),
            "unique_target_bars": len(bars),
            "expected_trade_archive_dates": list(DATES),
            "trade_archives_sha256_verified_and_stream_reconstructed": sum(1 for r in archive_checks if r.get("status") == "PASS_RECONSTRUCTED_TRADE_STREAM"),
            "archive_bytes_downloaded_total": total_download_bytes,
            "daily_exact_bar_matches_to_trade_reconstruction": daily_exact_bars,
            "monthly_exact_bar_matches_to_trade_reconstruction": monthly_exact_bars,
            "daily_metric_fields_matching": daily_match_fields,
            "monthly_metric_fields_matching": monthly_match_fields,
            "direct_trade_parent_child_rollups_pass": sum(1 for r in bucket_rows_out if r["direct_trade_parent_rollup_exact"]),
            "canonical_source_selected": False,
            "source_cases_closed": 0,
            "raw_kline_archives_modified": False,
            "market_data_rest_api_used": False,
            "candidate_build_performed": False,
            "backtest_performed": False,
            "strategy_promoted": False,
            "live_signing_enabled": False,
            "public_broadcast_enabled": False,
            "binance_orders_placed": False,
        },
        "inputs": {
            "row_evidence_path": str(row_path.relative_to(ROOT)),
            "row_evidence_sha256": row_evidence_sha256,
            "bucket_snapshot_path": str(bucket_path.relative_to(ROOT)),
            "bucket_snapshot_sha256": bucket_snapshot_sha256,
            "rulebook": rulebook_identity,
            "rulebook_sha256_verified_against_frozen_expected": True,
        },
        "row_evidence_coverage": source_coverage,
        "archives": [
            {
                k: r.get(k) for k in (
                    "utc_date","archive_filename","archive_url","expected_archive_sha256",
                    "sidecar_body_sha256","archive_bytes","archive_actual_sha256",
                    "archive_sha256_matches_sidecar","integrity_status","status",
                    "trade_rows","first_trade_id","last_trade_id","first_trade_time_ms",
                    "last_trade_time_ms","trade_id_gaps","trade_id_duplicates","trade_id_decreases",
                    "timestamp_decreases","rows_outside_day","invalid_rows","error"
                )
            } for r in archive_checks
        ],
        "buckets": bucket_rows_out,
        "limitations": [
            "The seven trades ZIPs are downloaded from official data.binance.vision, verified against current .CHECKSUM sidecars, streamed to reconstruct these exact target keys, then deleted with the temporary working directory. No raw kline source was changed.",
            "The trade archive and its current checksum authenticate these downloaded bytes but do not establish a historical version timeline or guarantee that all trades needed to recreate the original published klines are present.",
            "Zero-trade candles use the previous trade price as OHLC for reconstruction. Those are derived comparisons, not synthetic rows inserted into source data.",
            "No source authority is selected from a match pattern alone. CP-0040 remains the governing rulebook, and case closure requires its evidence standard.",
        ],
        "outputs": {},
    }
    report_lines = [
        "# CP-0112: Trade-derived aggregation reconstruction",
        "",
        "Status: " + status,
        "",
        "## Summary",
        "",
        "- Frozen aggregation buckets analyzed: " + str(len(bucket_rows_out)) + "/11",
        "- Unique child/parent candle keys reconstructed: " + str(len(bars)),
        "- Daily archive bars exactly matching the reconstructed trade metrics: " + str(daily_exact_bars) + "/" + str(len(bars)),
        "- Monthly archive bars exactly matching the reconstructed trade metrics: " + str(monthly_exact_bars) + "/" + str(len(bars)),
        "- Independent trade-derived parent = child rollup checks passed: " + str(summary["scope"]["direct_trade_parent_child_rollups_pass"]) + "/11",
        "- Canonical source selected / cases closed: false / 0",
        "",
        "## Bucket-level comparison",
        "",
        "| Case | UTC bucket | Trade parent = child rollup | Daily rows exact | Monthly rows exact | Daily mismatch fields | Monthly mismatch fields |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for r in bucket_rows_out:
        report_lines.append(
            "| " + r["case_id"] + " | " + r["bucket_utc"] + " | "
            + ("PASS" if r["direct_trade_parent_rollup_exact"] else "REVIEW") + " | "
            + str(r["daily_exact_target_bars"]) + "/" + str(r["daily_compared_target_bars"]) + " | "
            + str(r["monthly_exact_target_bars"]) + "/" + str(r["monthly_compared_target_bars"]) + " | "
            + str(r["daily_mismatch_fields"]) + " | " + str(r["monthly_mismatch_fields"]) + " |"
        )
    report_lines.extend([
        "",
        "## Method and boundaries",
        "",
        "Seven official daily Spot-trades ZIPs were downloaded and each ZIP byte hash was compared to its current .CHECKSUM sidecar. ZIP CRC and the seven-column trade row schema were checked. For each exact target candle key in the frozen CP-0107 row evidence, trades within [open_time, end_time) were streamed to derive open/high/low/close, base and quote volume, trade count, and taker-buy base/quote volumes. Zero-trade bars use the preceding trade price as OHLC for comparison and are explicitly flagged.",
        "",
        "The direct parent candle reconstructed from trades was compared with the rollup of the reconstructed child candles for every bucket. The reconstructed fields were then compared to the exact raw daily/monthly candle rows in the committed CP-0107 RowEvidence CSV; numeric fields use exact Decimal comparisons with no rounding.",
        "",
        "This is independent diagnostic evidence, not a canonical-source decision. Even a full daily match / monthly mismatch pattern does not by itself prove version provenance, a complete historical kline snapshot, or that the frozen rulebook's source-authority requirement is satisfied. No bucket is auto-closed.",
        "",
        "## Non-actions",
        "",
        "- No monthly/daily kline archive was edited or replaced.",
        "- No timestamp shifting, rounding, row merge, or source repair.",
        "- No synthesized candle was written to research inputs; zero-trade carry-forward exists only in this diagnostic derivation.",
        "- No Binance market-data REST endpoint, exchange credential, signing, public broadcast or order.",
        "- No candidate build, backtest or strategy promotion.",
        "",
    ])
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    for out_path in (archive_csv, bar_csv, bucket_csv, report_path):
        summary["outputs"][out_path.name] = {
            "bytes": out_path.stat().st_size,
            "sha256": sha_file(out_path),
        }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "checkpoint": "CP-0112",
        "status": status,
        "buckets": len(bucket_rows_out),
        "unique_target_bars": len(bars),
        "daily_exact_bar_matches": daily_exact_bars,
        "monthly_exact_bar_matches": monthly_exact_bars,
        "daily_metric_fields_matching": daily_match_fields,
        "monthly_metric_fields_matching": monthly_match_fields,
        "direct_trade_parent_child_rollups_pass": summary["scope"]["direct_trade_parent_child_rollups_pass"],
        "archives": summary["archives"],
        "bucket_results": bucket_rows_out,
        "output_hashes": summary["outputs"],
        "source_authority_selected": False,
        "source_cases_closed": 0,
    }, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
