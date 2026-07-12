"""Persistent DAG orchestrator with checkpoints and selective invalidation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import SkillRegistry
from .models import (
    NodeStatus,
    ReportConfig,
    RunOutcome,
    SkillRequest,
    WorkflowStatus,
)
from .skills import (
    EvidenceGovernanceSkill,
    FormattingSkill,
    IssueTreeSkill,
    MaterialIntegrationSkill,
    OutlineSkill,
    PressureTestSkill,
    QualityGateSkill,
    ResearchSkill,
    RequirementsAnalysisSkill,
    ReviewSkill,
    VisualizationSkill,
    WritingSkill,
)
from .storage import SQLiteStateStore, SQLiteVectorStore


@dataclass(frozen=True)
class NodeSpec:
    id: str
    dependencies: tuple[str, ...]
    skill: str | None = None
    input_nodes: tuple[str, ...] = ()
    checkpoint: bool = False
    quality_gate: bool = False


NODES = (
    NodeSpec("requirements_analysis", (), "requirements_analysis"),
    NodeSpec(
        "issue_tree",
        ("requirements_analysis",),
        "issue_tree",
        ("requirements_analysis",),
    ),
    NodeSpec("issue_tree_confirmation", ("issue_tree",), checkpoint=True),
    NodeSpec(
        "outline",
        ("requirements_analysis", "issue_tree", "issue_tree_confirmation"),
        "outline",
        ("requirements_analysis", "issue_tree"),
    ),
    NodeSpec("outline_confirmation", ("outline",), checkpoint=True),
    NodeSpec(
        "research",
        ("requirements_analysis", "issue_tree", "outline", "outline_confirmation"),
        "research",
        ("requirements_analysis", "issue_tree", "outline"),
    ),
    NodeSpec(
        "evidence_governance",
        ("research", "issue_tree", "outline"),
        "evidence_governance",
        ("research", "issue_tree"),
    ),
    NodeSpec(
        "material_integration",
        ("outline", "research", "evidence_governance"),
        "material_integration",
        ("outline", "research", "evidence_governance"),
    ),
    NodeSpec(
        "visualization",
        ("issue_tree", "material_integration"),
        "visualization",
        ("issue_tree", "material_integration"),
    ),
    NodeSpec(
        "writing",
        (
            "requirements_analysis", "issue_tree", "outline", "research",
            "evidence_governance", "material_integration", "visualization",
        ),
        "writing",
        (
            "requirements_analysis", "issue_tree", "outline", "research",
            "evidence_governance", "material_integration", "visualization",
        ),
    ),
    NodeSpec(
        "pressure_test",
        (
            "requirements_analysis", "issue_tree", "outline", "research",
            "evidence_governance", "material_integration", "visualization", "writing",
        ),
        "pressure_test",
        (
            "requirements_analysis", "issue_tree", "outline", "research",
            "evidence_governance", "material_integration", "visualization", "writing",
        ),
    ),
    NodeSpec("draft_confirmation", ("writing", "pressure_test"), checkpoint=True),
    NodeSpec(
        "formatting", ("writing", "draft_confirmation"), "formatting", ("writing",)
    ),
    NodeSpec("pre_review_confirmation", ("formatting",), checkpoint=True),
    NodeSpec(
        "review",
        (
            "requirements_analysis", "research", "evidence_governance", "outline",
            "material_integration", "visualization", "pressure_test", "formatting",
            "pre_review_confirmation",
        ),
        "review",
        (
            "requirements_analysis", "research", "evidence_governance", "outline",
            "material_integration", "visualization", "pressure_test", "formatting",
        ),
    ),
    NodeSpec(
        "quality_gate",
        ("requirements_analysis", "evidence_governance", "pressure_test", "review"),
        "quality_gate",
        ("requirements_analysis", "evidence_governance", "pressure_test", "review"),
        quality_gate=True,
    ),
)
NODE_MAP = {node.id: node for node in NODES}


def default_registry() -> SkillRegistry:
    registry = SkillRegistry()
    for skill in (
        RequirementsAnalysisSkill(), IssueTreeSkill(), OutlineSkill(), ResearchSkill(),
        EvidenceGovernanceSkill(), MaterialIntegrationSkill(), VisualizationSkill(),
        WritingSkill(), PressureTestSkill(), FormattingSkill(), ReviewSkill(),
        QualityGateSkill(),
    ):
        registry.register(skill)
    return registry


class ResearchReportOrchestrator:
    """Coordinates replaceable skills without giving them shared mutable state."""

    def __init__(
        self,
        data_dir: str | Path = ".research-workflow",
        *,
        registry: SkillRegistry | None = None,
    ) -> None:
        root = Path(data_dir)
        self.state = SQLiteStateStore(root / "state.db")
        self.context = SQLiteVectorStore(root / "vectors.db")
        self.registry = registry or default_registry()

    def create(self, raw_config: dict[str, Any], workflow_id: str | None = None) -> str:
        config = ReportConfig.from_dict(raw_config)
        workflow_id = self.state.create_workflow(config, workflow_id)
        self.state.record_operation(workflow_id, "create", {"config": config.to_dict()})
        return workflow_id

    def run(self, workflow_id: str) -> RunOutcome:
        config = self.state.config(workflow_id)
        self.state.set_workflow_status(workflow_id, WorkflowStatus.RUNNING)
        for spec in NODES:
            current = self.state.node(workflow_id, spec.id)
            if current and current["status"] == NodeStatus.COMPLETED:
                continue
            if not self._dependencies_complete(workflow_id, spec):
                raise RuntimeError(f"节点 {spec.id} 的依赖未完成")
            if spec.checkpoint:
                if self.state.is_confirmed(workflow_id, spec.id):
                    self.state.set_node(workflow_id, spec.id, NodeStatus.COMPLETED)
                    continue
                self.state.set_node(
                    workflow_id, spec.id, NodeStatus.WAITING_CONFIRMATION
                )
                self.state.set_workflow_status(
                    workflow_id, WorkflowStatus.WAITING_CONFIRMATION
                )
                return RunOutcome(
                    workflow_id, WorkflowStatus.WAITING_CONFIRMATION, waiting_at=spec.id
                )
            try:
                artifact_id = self._execute_skill(workflow_id, config, spec)
            except Exception as exc:
                self.state.set_node(
                    workflow_id, spec.id, NodeStatus.FAILED, error=str(exc)
                )
                self.state.set_workflow_status(workflow_id, WorkflowStatus.FAILED)
                raise
            if spec.quality_gate:
                gate_artifact = self.state.artifact(artifact_id)
                if not gate_artifact["metadata"].get("quality_passed", False):
                    score = gate_artifact["metadata"].get("total_score", "unknown")
                    error = f"质量门拒绝发布，总分: {score}"
                    self.state.set_node(
                        workflow_id, spec.id, NodeStatus.FAILED,
                        inputs=self._input_artifact_ids(workflow_id, spec),
                        output_artifact_id=artifact_id, error=error,
                    )
                    self.state.set_workflow_status(workflow_id, WorkflowStatus.FAILED)
                    raise QualityGateRejected(error)
            self.state.set_node(
                workflow_id, spec.id, NodeStatus.COMPLETED,
                inputs=self._input_artifact_ids(workflow_id, spec),
                output_artifact_id=artifact_id,
            )
        final = self.state.node_artifact(workflow_id, "review", internal=True)
        self.state.set_workflow_status(workflow_id, WorkflowStatus.COMPLETED)
        return RunOutcome(
            workflow_id, WorkflowStatus.COMPLETED,
            final_artifact_id=final["id"] if final else None,
        )

    def _execute_skill(
        self, workflow_id: str, config: ReportConfig, spec: NodeSpec
    ) -> str:
        assert spec.skill is not None
        input_artifacts = {
            node_id: self.state.node_artifact(workflow_id, node_id, internal=True)
            for node_id in spec.input_nodes
        }
        if any(value is None for value in input_artifacts.values()):
            raise RuntimeError(f"节点 {spec.id} 缺少输入产物")
        inputs = {
            node_id: artifact["content"] for node_id, artifact in input_artifacts.items()
            if artifact is not None
        }
        feedback = self.state.feedback(workflow_id, spec.id)
        context = self.context.query(
            workflow_id,
            f"{config.topic} {' '.join(feedback)}",
            node_ids=set(spec.input_nodes) or None,
            limit=16,
        )
        request = SkillRequest(
            workflow_id=workflow_id,
            node_id=spec.id,
            config=config,
            inputs=inputs,
            context=context,
            feedback=feedback,
        )
        self.state.set_node(
            workflow_id, spec.id, NodeStatus.RUNNING,
            inputs=self._input_artifact_ids(workflow_id, spec),
            increment_attempt=True,
        )
        skill = self.registry.get(spec.skill)
        result = skill.execute(request)
        skill.validate(result)
        artifact_id = self.state.add_artifact(
            workflow_id, spec.id, result.artifact_type, result.content,
            {**result.metadata, "skill": skill.name, "skill_version": skill.version},
        )
        self.context.upsert_chunks(
            workflow_id=workflow_id, node_id=spec.id,
            artifact_type=result.artifact_type, artifact_id=artifact_id,
            content=result.content,
        )
        return artifact_id

    def _input_artifact_ids(self, workflow_id: str, spec: NodeSpec) -> dict[str, str]:
        result: dict[str, str] = {}
        for node_id in spec.input_nodes:
            artifact = self.state.node_artifact(workflow_id, node_id, internal=True)
            if artifact:
                result[node_id] = artifact["id"]
        return result

    def _dependencies_complete(self, workflow_id: str, spec: NodeSpec) -> bool:
        return all(
            (node := self.state.node(workflow_id, dependency)) is not None
            and node["status"] == NodeStatus.COMPLETED
            for dependency in spec.dependencies
        )

    def confirm(self, workflow_id: str, checkpoint_id: str, comment: str = "") -> None:
        spec = NODE_MAP.get(checkpoint_id)
        if not spec or not spec.checkpoint:
            raise ValueError(f"不是有效确认节点: {checkpoint_id}")
        current = self.state.node(workflow_id, checkpoint_id)
        if not current or current["status"] != NodeStatus.WAITING_CONFIRMATION:
            raise ValueError(f"确认节点当前不可确认: {checkpoint_id}")
        self.state.confirm(workflow_id, checkpoint_id, comment)
        self.state.set_node(workflow_id, checkpoint_id, NodeStatus.COMPLETED)
        self.state.set_workflow_status(workflow_id, WorkflowStatus.RUNNING)

    def modify(self, workflow_id: str, target_node: str, feedback: str) -> set[str]:
        if target_node not in NODE_MAP or NODE_MAP[target_node].checkpoint:
            raise ValueError(f"只能修改产物节点: {target_node}")
        feedback = feedback.strip()
        if not feedback:
            raise ValueError("修改意见不能为空")
        affected = self.affected_nodes(target_node)
        self.state.record_operation(
            workflow_id, "modify", {"feedback": feedback, "affected": sorted(affected)},
            target_node,
        )
        checkpoints: set[str] = set()
        for node_id in affected:
            spec = NODE_MAP[node_id]
            previous = self.state.node(workflow_id, node_id)
            if previous:
                self.state.set_node(workflow_id, node_id, NodeStatus.INVALIDATED)
            if spec.checkpoint:
                checkpoints.add(node_id)
        self.context.deactivate_nodes(
            workflow_id, {node_id for node_id in affected if not NODE_MAP[node_id].checkpoint}
        )
        self.state.clear_confirmations(workflow_id, checkpoints)
        self.state.set_workflow_status(workflow_id, WorkflowStatus.RUNNING)
        return affected

    def update_sources(
        self,
        workflow_id: str,
        sources: list[dict[str, Any] | str],
        reason: str = "更新研究来源",
    ) -> set[str]:
        if not isinstance(sources, list):
            raise ValueError("sources 必须是数组")
        if not sources:
            raise ValueError("修复证据时 sources 不能为空")
        if any(not isinstance(source, (str, dict)) for source in sources):
            raise ValueError("每个 source 必须是字符串或对象")
        config = self.state.config(workflow_id)
        raw = config.to_dict()
        raw["extra"] = {**config.extra, "sources": sources}
        updated = ReportConfig.from_dict(raw)
        self.state.update_config(workflow_id, updated)
        self.state.record_operation(
            workflow_id,
            "update_sources",
            {"source_count": len(sources), "reason": reason},
            "requirements_analysis",
        )
        return self.modify(workflow_id, "requirements_analysis", reason)

    def request_revision(self, workflow_id: str, feedback: str) -> tuple[str, set[str]]:
        normalized = feedback.strip().lower()
        if not normalized:
            raise ValueError("修改意见不能为空")
        routes = (
            (
                "requirements_analysis",
                ("主题", "受众", "边界", "前置思考", "需求", "产出形态", "audience", "scope"),
            ),
            ("outline", ("大纲", "框架", "章节", "结构", "outline")),
            (
                "research",
                ("来源", "链接", "事实", "数据", "材料", "调研", "引用", "source", "citation"),
            ),
            (
                "visualization",
                ("图表", "可视化", "流程图", "架构图", "chart", "diagram"),
            ),
            ("formatting", ("格式", "排版", "html", "json", "markdown")),
            ("writing", ("篇幅", "文风", "措辞", "论证", "内容", "语气", "style")),
        )
        target = "writing"
        for candidate, keywords in routes:
            if any(keyword in normalized for keyword in keywords):
                target = candidate
                break
        self.state.record_operation(
            workflow_id,
            "route_revision",
            {"feedback": feedback, "target_node": target},
            target,
        )
        return target, self.modify(workflow_id, target, feedback)

    @staticmethod
    def affected_nodes(target_node: str) -> set[str]:
        if target_node not in NODE_MAP:
            raise ValueError(f"未知节点: {target_node}")
        affected = {target_node}
        changed = True
        while changed:
            changed = False
            for spec in NODES:
                if spec.id not in affected and any(dep in affected for dep in spec.dependencies):
                    affected.add(spec.id)
                    changed = True
        return affected

    def final_report(self, workflow_id: str) -> str:
        if self.state.workflow_status(workflow_id) != WorkflowStatus.COMPLETED:
            raise ValueError("工作流尚未生成终稿")
        artifact = self.state.node_artifact(workflow_id, "review")
        if not artifact:
            raise ValueError("工作流尚未生成终稿")
        return artifact["content"]


class QualityGateRejected(RuntimeError):
    """Raised after persisting a quality decision that blocks release."""
