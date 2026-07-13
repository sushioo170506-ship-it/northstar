"""Helpers for reading nested evidence / finalize pipeline inputs."""

from __future__ import annotations

import json


def evidence_governance_text(inputs: dict[str, str]) -> str:
    if "evidence_governance" in inputs:
        return inputs["evidence_governance"]
    if "evidence_pipeline" in inputs:
        pipeline = json.loads(inputs["evidence_pipeline"])
        return json.dumps(pipeline["evidence_governance"], ensure_ascii=False)
    raise KeyError("evidence_governance")


def source_snapshot_text(inputs: dict[str, str]) -> str:
    if "source_snapshot" in inputs:
        return inputs["source_snapshot"]
    if "evidence_pipeline" in inputs:
        pipeline = json.loads(inputs["evidence_pipeline"])
        return json.dumps(pipeline["source_snapshot"], ensure_ascii=False)
    raise KeyError("source_snapshot")


def claim_verification_text(inputs: dict[str, str]) -> str:
    if "claim_verification" in inputs:
        return inputs["claim_verification"]
    if "data_processing" in inputs:
        processed = json.loads(inputs["data_processing"])
        nested = processed.get("claim_verification")
        if isinstance(nested, dict):
            return json.dumps(nested, ensure_ascii=False)
    return "{}"


def finalized_draft_text(inputs: dict[str, str]) -> str:
    return inputs.get(
        "writing_finalize",
        inputs.get(
            "content_optimization",
            inputs.get("citation_management", inputs.get("writing", "")),
        ),
    )
