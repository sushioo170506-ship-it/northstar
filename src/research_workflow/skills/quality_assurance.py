"""Quality assurance: quant gates, review polish and release decision."""

from __future__ import annotations

import json

from ..contracts import Skill
from ..models import SkillRequest, SkillResult
from .quality_gate import QualityGateSkill
from .quant_finance_research import QuantFinanceResearchSkill
from .review import ReviewSkill


class QualityAssuranceSkill(Skill):
    name = "quality_assurance"
    version = "1.0.0"

    def __init__(self) -> None:
        self.quant = QuantFinanceResearchSkill()
        self.review = ReviewSkill()
        self.gate = QualityGateSkill()

    def execute(self, request: SkillRequest) -> SkillResult:
        quant = self.quant.execute(request)
        self.quant.validate(quant)
        review_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs={
                **request.inputs,
                "quant_finance_research": quant.content,
            },
            context=request.context,
            feedback=request.feedback,
        )
        reviewed = self.review.execute(review_request)
        self.review.validate(reviewed)
        gate_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs={
                **review_request.inputs,
                "review": reviewed.content,
            },
            context=request.context,
            feedback=request.feedback,
        )
        gate = self.gate.execute(gate_request)
        self.gate.validate(gate)
        gate_payload = json.loads(gate.content)
        payload = {
            "review": reviewed.content,
            "quality_gate": gate_payload,
            "quant_finance_research": json.loads(quant.content),
            "pipeline_steps": [
                "quant_finance_research",
                "review",
                "quality_gate",
            ],
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "quality_assurance",
            {
                **gate.metadata,
                "pipeline_steps": payload["pipeline_steps"],
                "quant_applicable": payload["quant_finance_research"].get(
                    "applicable", False
                ),
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"review", "quality_gate", "pipeline_steps"} <= payload.keys():
            raise ValueError("quality_assurance 缺少必要字段")
        if "passed" not in payload["quality_gate"]:
            raise ValueError("quality_assurance 缺少质量门结论")
