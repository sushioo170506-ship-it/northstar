"""Compose materials, visuals, draft, finalize and pressure-test into one node."""

from __future__ import annotations

import json

from ..contracts import Skill
from ..models import SkillRequest, SkillResult
from .material_integration import MaterialIntegrationSkill
from .pressure_test import PressureTestSkill
from .visualization import VisualizationSkill
from .writing import WritingSkill
from .writing_finalize import WritingFinalizeSkill


class ComposeSkill(Skill):
    name = "compose"
    version = "1.0.0"

    def __init__(self) -> None:
        self.material = MaterialIntegrationSkill()
        self.visualization = VisualizationSkill()
        self.writing = WritingSkill()
        self.finalize = WritingFinalizeSkill()
        self.pressure = PressureTestSkill()

    def execute(self, request: SkillRequest) -> SkillResult:
        material = self.material.execute(request)
        self.material.validate(material)
        viz_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs={**request.inputs, "material_integration": material.content},
            context=request.context,
            feedback=request.feedback,
        )
        # Provide not_applicable quant placeholder unless already present.
        if "quant_finance_research" not in viz_request.inputs:
            viz_request = SkillRequest(
                workflow_id=viz_request.workflow_id,
                node_id=viz_request.node_id,
                config=viz_request.config,
                inputs={
                    **viz_request.inputs,
                    "quant_finance_research": json.dumps(
                        {
                            "applicable": False,
                            "status": "deferred_to_quality_assurance",
                            "hard_gates_passed": True,
                        },
                        ensure_ascii=False,
                    ),
                },
                context=viz_request.context,
                feedback=viz_request.feedback,
            )
        visualization = self.visualization.execute(viz_request)
        self.visualization.validate(visualization)
        writing_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs={
                **viz_request.inputs,
                "material_integration": material.content,
                "visualization": visualization.content,
            },
            context=request.context,
            feedback=request.feedback,
        )
        writing = self.writing.execute(writing_request)
        self.writing.validate(writing)
        finalize_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs={
                **writing_request.inputs,
                "writing": writing.content,
            },
            context=request.context,
            feedback=request.feedback,
        )
        finalized = self.finalize.execute(finalize_request)
        self.finalize.validate(finalized)
        pressure_request = SkillRequest(
            workflow_id=request.workflow_id,
            node_id=request.node_id,
            config=request.config,
            inputs={
                **finalize_request.inputs,
                "writing_finalize": finalized.content,
                "content_optimization": finalized.content,
            },
            context=request.context,
            feedback=request.feedback,
        )
        pressure = self.pressure.execute(pressure_request)
        self.pressure.validate(pressure)
        payload = {
            "draft": finalized.content,
            "writing": writing.content,
            "writing_finalize": finalized.content,
            "material_integration": json.loads(material.content),
            "visualization": json.loads(visualization.content),
            "pressure_test": json.loads(pressure.content),
            "pipeline_steps": [
                "material_integration",
                "visualization",
                "writing",
                "writing_finalize",
                "pressure_test",
            ],
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "composed_report",
            {
                "pipeline_steps": payload["pipeline_steps"],
                "visual_asset_count": len(
                    payload["visualization"].get("assets", [])
                ),
                "pressure_issue_count": len(
                    payload["pressure_test"].get("repair_actions", [])
                ),
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        required = {
            "draft",
            "material_integration",
            "visualization",
            "pressure_test",
            "pipeline_steps",
        }
        if not required <= payload.keys():
            raise ValueError("compose 缺少必要字段")
        if not str(payload["draft"]).strip():
            raise ValueError("compose 草稿为空")
