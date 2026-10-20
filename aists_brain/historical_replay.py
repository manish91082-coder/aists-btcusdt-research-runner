'''Deterministic, provenance-gated historical decision replay.

This harness replays timestamped, precomputed causal brain inputs. It does not
load/download market data, repair candles, calculate P&L, or place orders.
'''
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from .multi_timeframe_selector import select_multi_timeframe_candidate

REPLAY_SCHEMA = "aists.historical_decision_replay.v1"


def replay_decisions(records: Sequence[Mapping[str, Any]], *, provenance_gate: str,
                     source_manifest: Mapping[str, Any],
                     min_confirming_timeframes: int = 3) -> dict[str, Any]:
    """Replay precomputed snapshots in strictly increasing as-of order."""
    if provenance_gate != "PASS":
        raise RuntimeError("historical replay blocked: provenance_gate must be PASS")
    sources = source_manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source_manifest.sources must be a non-empty list")
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise ValueError(f"source_manifest.sources[{index}] must be an object")
        digest = source.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
            raise ValueError(f"source_manifest.sources[{index}] requires a 64-character SHA-256")

    decisions: list[dict[str, Any]] = []
    previous_as_of: int | None = None
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise ValueError(f"records[{index}] must be an object")
        as_of = record.get("as_of_ms")
        if isinstance(as_of, bool) or not isinstance(as_of, int) or as_of < 0:
            raise ValueError(f"records[{index}].as_of_ms must be a non-negative integer")
        if previous_as_of is not None and as_of <= previous_as_of:
            raise ValueError("replay as_of_ms timestamps must be strictly increasing")
        previous_as_of = as_of
        snapshot = record.get("snapshot")
        candidates = record.get("candidates_by_timeframe")
        if not isinstance(snapshot, Mapping) or not isinstance(candidates, Mapping):
            raise ValueError(f"records[{index}] requires snapshot and candidates_by_timeframe objects")
        snapshot_as_of = snapshot.get("as_of_ms")
        if snapshot_as_of is not None and (isinstance(snapshot_as_of, bool) or not isinstance(snapshot_as_of, int) or snapshot_as_of > as_of):
            raise ValueError(f"records[{index}] snapshot timestamp exceeds replay as-of time")
        result = select_multi_timeframe_candidate(snapshot, candidates, min_confirming_timeframes=min_confirming_timeframes)
        decisions.append({"sequence": index, "as_of_ms": as_of, "decision": deepcopy(result)})

    manifest_canonical = json.dumps(source_manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {
        "schema_version": REPLAY_SCHEMA,
        "status": "REPLAYED_NO_PNL",
        "record_count": len(decisions),
        "provenance_gate": provenance_gate,
        "source_manifest_sha256": sha256(manifest_canonical.encode("utf-8")).hexdigest(),
        "decision_counts": {
            "research_candidate_only": sum(d["decision"]["status"] == "RESEARCH_CANDIDATE_ONLY" for d in decisions),
            "no_trade_or_abstain": sum(d["decision"]["selected_action"] == "NO_TRADE" for d in decisions),
        },
        "decisions": decisions,
        "limitations": [
            "input snapshots and candidate evaluations must already be causally constructed",
            "caller-provided provenance_gate is not independently adjudicated by this module",
            "no P&L, fees, slippage, fills, portfolio accounting, or profitability is calculated",
            "no data is downloaded, synthesized, forward-filled, or repaired",
            "no exchange API, signing, order placement, or public broadcast",
        ],
    }
