"""Causal decision-artifact validation for offline research.

Validates timestamp ordering, exact candle-file binding and snapshot integrity.
It cannot prove that feature values were genuinely computed from the declared source.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any, Mapping, Sequence


DECISION_SCHEMA = "aists.causal_research_decisions.v1"
_ACTIONS = {"BUY_CANDIDATE", "SELL_CANDIDATE", "NO_TRADE"}
_TIMEFRAMES = {"5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class DecisionLineageError(ValueError):
    """Raised when a decision artifact lacks causal, hash-bound lineage."""


def canonical_sha256(value: Mapping[str, Any]) -> str:
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise DecisionLineageError("snapshot must be finite JSON-compatible data") from exc
    return hashlib.sha256(raw).hexdigest()


def validate_causal_decision_artifact(
    artifact: Mapping[str, Any],
    *,
    candle_csv_sha256: str,
    candle_close_times_ms: Sequence[int],
) -> dict[str, Any]:
    """Validate decision IDs, exact input binding, snapshot hash and no-future features."""
    if not isinstance(artifact, Mapping) or artifact.get("schema_version") != DECISION_SCHEMA:
        raise DecisionLineageError("unsupported causal decision artifact schema")
    if artifact.get("status") != "PASS":
        raise DecisionLineageError("decision artifact status is not PASS")
    if not isinstance(candle_csv_sha256, str) or not _SHA256.fullmatch(candle_csv_sha256):
        raise DecisionLineageError("candle_csv_sha256 must be lowercase SHA-256")
    if artifact.get("source_csv_sha256") != candle_csv_sha256:
        raise DecisionLineageError("decision artifact is not bound to this exact candle CSV")

    brain_version = artifact.get("brain_version")
    strategy_version = artifact.get("strategy_version")
    if not isinstance(brain_version, str) or not brain_version.strip():
        raise DecisionLineageError("brain_version must be a non-empty string")
    if not isinstance(strategy_version, str) or not strategy_version.strip():
        raise DecisionLineageError("strategy_version must be a non-empty string")
    known_closes = set(candle_close_times_ms)
    decisions = artifact.get("decisions")
    if not isinstance(decisions, list):
        raise DecisionLineageError("decisions must be a list")

    previous_asof = -1
    seen_ids: set[str] = set()
    validated = []
    for index, decision in enumerate(decisions):
        if not isinstance(decision, Mapping):
            raise DecisionLineageError(f"decision {index} must be an object")
        decision_id = decision.get("decision_id")
        as_of_ms = decision.get("as_of_ms")
        action = decision.get("action")
        if not isinstance(decision_id, str) or not decision_id.strip() or decision_id in seen_ids:
            raise DecisionLineageError(f"decision {index} has an empty or duplicate decision_id")
        if isinstance(as_of_ms, bool) or not isinstance(as_of_ms, int) or as_of_ms < 0:
            raise DecisionLineageError(f"decision {index} as_of_ms must be a non-negative integer")
        if as_of_ms <= previous_asof:
            raise DecisionLineageError("decision timestamps must be strictly increasing")
        if as_of_ms not in known_closes:
            raise DecisionLineageError(f"decision {decision_id} does not reference a supplied candle close")
        if action not in _ACTIONS:
            raise DecisionLineageError(f"decision {decision_id} has unsupported action")
        snapshot = decision.get("snapshot")
        if not isinstance(snapshot, Mapping):
            raise DecisionLineageError(f"decision {decision_id} missing snapshot object")
        if snapshot.get("as_of_ms") != as_of_ms:
            raise DecisionLineageError(f"decision {decision_id} snapshot cutoff mismatch")
        if snapshot.get("brain_version") != brain_version:
            raise DecisionLineageError(f"decision {decision_id} brain version mismatch")
        if snapshot.get("strategy_version") != strategy_version:
            raise DecisionLineageError(f"decision {decision_id} strategy version mismatch")
        claimed_snapshot_hash = decision.get("snapshot_sha256")
        if not isinstance(claimed_snapshot_hash, str) or not _SHA256.fullmatch(claimed_snapshot_hash):
            raise DecisionLineageError(f"decision {decision_id} has invalid snapshot SHA-256")
        if canonical_sha256(snapshot) != claimed_snapshot_hash:
            raise DecisionLineageError(f"decision {decision_id} snapshot hash mismatch")
        observations = snapshot.get("feature_observations")
        if not isinstance(observations, list) or not observations:
            raise DecisionLineageError(f"decision {decision_id} requires feature observations")
        for feature_index, feature in enumerate(observations):
            if not isinstance(feature, Mapping):
                raise DecisionLineageError(f"decision {decision_id} feature {feature_index} must be an object")
            name, timeframe = feature.get("feature_name"), feature.get("timeframe")
            observed = feature.get("observed_close_time_ms")
            source_hash = feature.get("source_sha256")
            value = feature.get("value")
            if not isinstance(name, str) or not name.strip():
                raise DecisionLineageError(f"decision {decision_id} feature name missing")
            if timeframe not in _TIMEFRAMES:
                raise DecisionLineageError(f"decision {decision_id} has unsupported feature timeframe")
            if isinstance(observed, bool) or not isinstance(observed, int) or observed < 0:
                raise DecisionLineageError(f"decision {decision_id} feature timestamp invalid")
            if observed > as_of_ms:
                raise DecisionLineageError(f"decision {decision_id} contains future feature data")
            if not isinstance(source_hash, str) or not _SHA256.fullmatch(source_hash):
                raise DecisionLineageError(f"decision {decision_id} feature source hash invalid")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise DecisionLineageError(f"decision {decision_id} feature value must be finite numeric")
        validated.append({"decision_id": decision_id, "as_of_ms": as_of_ms, "action": action})
        seen_ids.add(decision_id)
        previous_asof = as_of_ms

    return {
        "schema_version": "aists.causal_decision_validation.v1",
        "status": "PASS_CAUSAL_CONTRACT",
        "mode": "OFFLINE_RESEARCH_ONLY",
        "brain_version": brain_version,
        "strategy_version": strategy_version,
        "decision_count": len(validated),
        "decisions": validated,
        "limitations": [
            "timestamp checks do not prove feature values were computed from their declared source artifacts",
            "hashes prove artifact identity, not truth or independent provenance",
            "no signal generation, profitability validation or exchange execution is performed",
        ],
    }
