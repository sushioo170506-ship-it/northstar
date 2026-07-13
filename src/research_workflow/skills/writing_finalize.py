"""Composite writing finalize: citations → structural content optimization."""

from __future__ import annotations

import json

from ..contracts import Skill
from ..models import SkillRequest, SkillResult
from .citation_management import CitationManagementSkill
from .content_optimization import ContentOptimizationSkill


class WritingFinalizeSkill(Skill):
    """One DAG node that cites sources then optimizes diagrams/tables/lists/links."""

    name = "writing_finalize"
    version = "1.0.0"

    def __init__(self) -> None:
        self.citation = CitationManagementSkill()
        self.optimization = ContentOptimizationSkill()

    def execute(self, request: SkillRequest) -> SkillResult:
        cite_inputs = dict(request.inputs)
        if (
            "evidence_governance" not in cite_inputs
            and "evidence_pipeline" in cite_inputs
        ):
            pipeline = json.loads(cite_inputs["evidence_pipeline"])
            cite_inputs["evidence_governance"] = json.dumps(
                pipeline["evidence_governance"], ensure_ascii=False
            )
        cite_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs=cite_inputs,
            context=request.context,
            feedback=request.feedback,
        )
        cited = self.citation.execute(cite_request)
        self.citation.validate(cited)
        optimize_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs={
                **cite_inputs,
                "citation_management": cited.content,
                "writing_standards": request.inputs.get(
                    "writing_standards", "{}"
                ),
            },
            context=request.context,
            feedback=request.feedback,
        )
        optimized = self.optimization.execute(optimize_request)
        self.optimization.validate(optimized)
        return SkillResult(
            optimized.content,
            "finalized_draft",
            {
                **cited.metadata,
                **optimized.metadata,
                "pipeline_steps": [
                    "citation_management",
                    "content_optimization",
                ],
                "feedback_applied": list(request.feedback),
            },
        )
