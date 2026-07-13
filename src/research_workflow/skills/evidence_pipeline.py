"""Composite evidence pipeline: snapshot → governance (claim verify runs in data_processing)."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult
from .evidence_governance import EvidenceGovernanceSkill
from .source_snapshot import SourceSnapshotSkill


class EvidencePipelineSkill(Skill):
    """One DAG node that freezes sources and builds the evidence ledger."""

    name = "evidence_pipeline"
    version = "1.0.0"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.snapshot = SourceSnapshotSkill()
        self.governance = EvidenceGovernanceSkill(generator=generator)

    def execute(self, request: SkillRequest) -> SkillResult:
        snapshot_result = self.snapshot.execute(request)
        self.snapshot.validate(snapshot_result)
        snapshot_payload = json.loads(snapshot_result.content)
        governance_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs={
                **request.inputs,
                "source_snapshot": snapshot_result.content,
            },
            context=request.context,
            feedback=request.feedback,
        )
        governance_result = self.governance.execute(governance_request)
        self.governance.validate(governance_result)
        governance_payload = json.loads(governance_result.content)
        payload = {
            "source_snapshot": snapshot_payload,
            "evidence_governance": governance_payload,
            "pipeline_steps": ["source_snapshot", "evidence_governance"],
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "evidence_pipeline",
            {
                "source_count": snapshot_result.metadata.get("source_count", 0),
                "policy_passed": snapshot_result.metadata.get("policy_passed", False),
                "red_line_count": governance_result.metadata.get("red_line_count", 0),
                "traceability_ratio": governance_result.metadata.get(
                    "traceability_ratio", 0.0
                ),
                "pipeline_steps": payload["pipeline_steps"],
                "scene": snapshot_result.metadata.get("scene"),
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"source_snapshot", "evidence_governance", "pipeline_steps"} <= payload.keys():
            raise ValueError("evidence_pipeline 缺少必要字段")
        self.snapshot.validate(
            SkillResult(
                json.dumps(payload["source_snapshot"], ensure_ascii=False),
                "source_snapshot",
                {},
            )
        )
        self.governance.validate(
            SkillResult(
                json.dumps(payload["evidence_governance"], ensure_ascii=False),
                "evidence_ledger",
                {},
            )
        )
