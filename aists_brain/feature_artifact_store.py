"""Create-only persistence and integrity verification for causal feature artifacts.

The store preserves the producer artifact, adds a hash-bound storage envelope,
and refuses to overwrite existing output. Hashes establish byte identity, not
market-data provenance, feature truth, strategy validity, or profitability.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from aists_brain.decision_lineage import (
    DecisionLineageError,
    canonical_sha256,
    validate_causal_decision_artifact,
)


STORE_SCHEMA = "aists.causal_feature_store.v1"


class FeatureArtifactStoreError(ValueError):
    """Raised when an artifact cannot be safely persisted or verified."""


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise FeatureArtifactStoreError(
            "artifact must be finite JSON-compatible data"
        ) from exc


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def persist_feature_artifact(
    artifact: Mapping[str, Any],
    destination: str | Path,
    *,
    candle_close_times_ms: Sequence[int],
) -> dict[str, Any]:
    """Validate and atomically publish an artifact without overwriting a path.

    A temporary file is written and fsynced in the destination directory. A
    hard-link publishes it atomically only if the destination does not exist.
    """
    if not isinstance(artifact, Mapping):
        raise FeatureArtifactStoreError("artifact must be a mapping")
    if "artifact_store" in artifact:
        raise FeatureArtifactStoreError("artifact already contains storage metadata")
    source_hash = artifact.get("source_csv_sha256")
    try:
        lineage = validate_causal_decision_artifact(
            artifact,
            candle_csv_sha256=source_hash,
            candle_close_times_ms=candle_close_times_ms,
        )
    except (DecisionLineageError, TypeError) as exc:
        raise FeatureArtifactStoreError(f"causal artifact validation failed: {exc}") from exc

    payload = dict(artifact)
    payload_hash = canonical_sha256(payload)
    envelope = dict(payload)
    envelope["artifact_store"] = {
        "schema_version": STORE_SCHEMA,
        "payload_sha256": payload_hash,
        "source_csv_sha256": source_hash,
        "brain_version": lineage["brain_version"],
        "strategy_version": lineage["strategy_version"],
        "timeframe": artifact.get("timeframe"),
        "decision_count": lineage["decision_count"],
        "mode": "OFFLINE_RESEARCH_ONLY",
        "limitations": [
            "storage hashes establish artifact identity, not truth or external provenance",
            "this store does not authorize simulation, candidate promotion, or trading",
        ],
    }
    raw = _canonical_bytes(envelope)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".aists-feature-", suffix=".tmp", dir=target.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp_path, target)
        except FileExistsError as exc:
            raise FeatureArtifactStoreError(
                f"refusing to overwrite existing artifact: {target}"
            ) from exc
        except OSError as exc:
            if target.exists():
                raise FeatureArtifactStoreError(
                    f"refusing to overwrite existing artifact: {target}"
                ) from exc
            raise FeatureArtifactStoreError(
                f"atomic create-only publication failed: {exc}"
            ) from exc
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass

    verified = load_feature_artifact(
        target, candle_close_times_ms=candle_close_times_ms
    )
    file_hash = _sha256_bytes(target.read_bytes())
    if canonical_sha256(verified["artifact"]) != payload_hash:
        raise FeatureArtifactStoreError("persisted artifact payload hash mismatch")
    return {
        "schema_version": STORE_SCHEMA,
        "status": "PERSISTED_AND_RELOADED",
        "path": str(target),
        "file_sha256": file_hash,
        "payload_sha256": payload_hash,
        "source_csv_sha256": source_hash,
        "brain_version": lineage["brain_version"],
        "strategy_version": lineage["strategy_version"],
        "timeframe": artifact.get("timeframe"),
        "decision_count": lineage["decision_count"],
        "mode": "OFFLINE_RESEARCH_ONLY",
    }


def load_feature_artifact(
    source: str | Path,
    *,
    candle_close_times_ms: Sequence[int],
) -> dict[str, Any]:
    """Reload a stored artifact, checking envelope hashes and causal lineage."""
    path = Path(source)
    try:
        raw = path.read_bytes()
        envelope = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FeatureArtifactStoreError(f"cannot read stored artifact: {exc}") from exc
    if not isinstance(envelope, dict):
        raise FeatureArtifactStoreError("stored artifact must be a JSON object")
    metadata = envelope.get("artifact_store")
    if not isinstance(metadata, dict) or metadata.get("schema_version") != STORE_SCHEMA:
        raise FeatureArtifactStoreError("missing or unsupported artifact-store metadata")
    payload = dict(envelope)
    payload.pop("artifact_store")
    if canonical_sha256(payload) != metadata.get("payload_sha256"):
        raise FeatureArtifactStoreError("stored artifact payload hash mismatch")
    if payload.get("source_csv_sha256") != metadata.get("source_csv_sha256"):
        raise FeatureArtifactStoreError("stored source hash metadata mismatch")
    if payload.get("brain_version") != metadata.get("brain_version"):
        raise FeatureArtifactStoreError("stored brain version metadata mismatch")
    if payload.get("strategy_version") != metadata.get("strategy_version"):
        raise FeatureArtifactStoreError("stored strategy version metadata mismatch")
    try:
        lineage = validate_causal_decision_artifact(
            payload,
            candle_csv_sha256=payload.get("source_csv_sha256"),
            candle_close_times_ms=candle_close_times_ms,
        )
    except (DecisionLineageError, TypeError) as exc:
        raise FeatureArtifactStoreError(f"stored causal lineage invalid: {exc}") from exc
    if metadata.get("decision_count") != lineage["decision_count"]:
        raise FeatureArtifactStoreError("stored decision count metadata mismatch")
    return {
        "schema_version": STORE_SCHEMA,
        "status": "VERIFIED_RELOADED",
        "file_sha256": _sha256_bytes(raw),
        "payload_sha256": metadata["payload_sha256"],
        "artifact": payload,
        "metadata": metadata,
        "mode": "OFFLINE_RESEARCH_ONLY",
        "limitations": [
            "integrity checks do not authenticate source provenance or feature derivation",
            "successful reload is not evidence of profitability or strategy acceptance",
        ],
    }
