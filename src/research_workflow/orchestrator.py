"""Persistent DAG orchestrator with checkpoints and selective invalidation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import DocumentRenderer, SkillRegistry, SourceRetriever
from .models import (
    NodeStatus,
    ReportConfig,
    RunOutcome,
    SkillRequest,
    WorkflowStatus,
)
from .profiles import WORKFLOW_PROFILES
from .skills import (
    CapabilitySweepSkill,
    CitationManagementSkill,
    DataProcessingSkill,
    EvidenceGovernanceSkill,
    ExperienceEvolutionSkill,
    FormattingSkill,
    IssueTreeSkill,
    MaterialIntegrationSkill,
    OutlineSkill,
    PressureTestSkill,
    PublishSkill,
    QualityGateSkill,
    ResearchSkill,
    RequirementsAnalysisSkill,
    ReviewSkill,
    SkillResearchSkill,
    VisualizationSkill,
    WritingSkill,
    WritingStandardsSkill,
)
from .standards_store import SQLiteWritingStandardStore, WritingStandardProfile
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
    NodeSpec("capability_sweep", (), "capability_sweep"),
    NodeSpec(
        "requirements_analysis",
        ("capability_sweep",),
        "requirements_analysis",
    ),
    NodeSpec(
        "skill_research",
        ("requirements_analysis",),
        "skill_research",
        ("requirements_analysis",),
    ),
    NodeSpec(
        "writing_standards",
        ("requirements_analysis", "skill_research"),
        "writing_standards",
        ("requirements_analysis",),
    ),
    NodeSpec(
        "issue_tree",
        ("requirements_analysis", "skill_research", "writing_standards"),
        "issue_tree",
        ("requirements_analysis",),
    ),
    NodeSpec("issue_tree_confirmation", ("issue_tree",), checkpoint=True),
    NodeSpec(
        "outline",
        (
            "requirements_analysis", "writing_standards", "issue_tree",
            "issue_tree_confirmation",
        ),
        "outline",
        ("requirements_analysis", "writing_standards", "issue_tree"),
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
        "data_processing",
        ("research", "evidence_governance", "issue_tree", "outline"),
        "data_processing",
        ("research", "evidence_governance", "issue_tree", "outline"),
    ),
    NodeSpec(
        "material_integration",
        ("outline", "research", "evidence_governance", "data_processing"),
        "material_integration",
        ("outline", "research", "evidence_governance", "data_processing"),
    ),
    NodeSpec(
        "visualization",
        ("issue_tree", "material_integration", "data_processing"),
        "visualization",
        ("issue_tree", "material_integration", "data_processing"),
    ),
    NodeSpec(
        "writing",
        (
            "requirements_analysis", "issue_tree", "outline", "research",
            "evidence_governance", "data_processing", "material_integration",
            "visualization", "writing_standards",
        ),
        "writing",
        (
            "requirements_analysis", "issue_tree", "outline", "research",
            "evidence_governance", "data_processing", "material_integration",
            "visualization", "writing_standards",
        ),
    ),
    NodeSpec(
        "citation_management",
        ("writing", "evidence_governance", "material_integration"),
        "citation_management",
        ("writing", "evidence_governance", "material_integration"),
    ),
    NodeSpec(
        "pressure_test",
        (
            "requirements_analysis", "issue_tree", "outline", "research",
            "evidence_governance", "data_processing", "material_integration",
            "visualization", "writing", "citation_management",
        ),
        "pressure_test",
        (
            "requirements_analysis", "issue_tree", "outline", "research",
            "evidence_governance", "data_processing", "material_integration",
            "visualization", "citation_management",
        ),
    ),
    NodeSpec(
        "draft_confirmation",
        ("writing", "citation_management", "pressure_test"),
        checkpoint=True,
    ),
    NodeSpec(
        "formatting",
        ("citation_management", "writing_standards", "draft_confirmation"),
        "formatting",
        ("citation_management", "writing_standards"),
    ),
    NodeSpec("pre_review_confirmation", ("formatting",), checkpoint=True),
    NodeSpec(
        "review",
        (
            "requirements_analysis", "research", "evidence_governance", "outline",
            "data_processing", "material_integration", "visualization",
            "pressure_test", "writing_standards", "formatting",
            "pre_review_confirmation",
        ),
        "review",
        (
            "requirements_analysis", "research", "evidence_governance", "outline",
            "data_processing", "material_integration", "visualization",
            "pressure_test", "writing_standards", "formatting",
        ),
    ),
    NodeSpec(
        "quality_gate",
        (
            "capability_sweep", "skill_research", "requirements_analysis", "outline",
            "evidence_governance",
            "data_processing", "material_integration", "visualization",
            "citation_management", "pressure_test", "writing_standards", "review",
        ),
        "quality_gate",
        (
            "capability_sweep", "skill_research", "requirements_analysis", "outline",
            "evidence_governance",
            "data_processing", "material_integration", "visualization",
            "citation_management", "pressure_test", "writing_standards", "review",
        ),
        quality_gate=True,
    ),
    NodeSpec(
        "publish",
        (
            "capability_sweep", "skill_research", "visualization", "review",
            "writing_standards", "quality_gate",
        ),
        "publish",
        (
            "capability_sweep", "skill_research", "visualization", "review",
            "writing_standards", "quality_gate",
        ),
    ),
    NodeSpec(
        "experience_evolution",
        ("skill_research", "quality_gate", "publish"),
        "experience_evolution",
        ("skill_research", "quality_gate", "publish"),
    ),
)
NODE_MAP = {node.id: node for node in NODES}


def default_registry(
    *,
    source_retriever: SourceRetriever | None = None,
    document_renderer: DocumentRenderer | None = None,
    writing_standard_store: SQLiteWritingStandardStore | None = None,
) -> SkillRegistry:
    if writing_standard_store is None:
        writing_standard_store = SQLiteWritingStandardStore(":memory:")
    registry = SkillRegistry()
    for skill in (
        CapabilitySweepSkill(), RequirementsAnalysisSkill(), SkillResearchSkill(),
        WritingStandardsSkill(writing_standard_store),
        IssueTreeSkill(),
        OutlineSkill(), ResearchSkill(retriever=source_retriever),
        EvidenceGovernanceSkill(),
        DataProcessingSkill(), MaterialIntegrationSkill(), VisualizationSkill(),
        WritingSkill(), CitationManagementSkill(), PressureTestSkill(),
        FormattingSkill(), ReviewSkill(), QualityGateSkill(),
        PublishSkill(renderer=document_renderer), ExperienceEvolutionSkill(),
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
        source_retriever: SourceRetriever | None = None,
        document_renderer: DocumentRenderer | None = None,
    ) -> None:
        root = Path(data_dir)
        self.state = SQLiteStateStore(root / "state.db")
        self.context = SQLiteVectorStore(root / "vectors.db")
        self.writing_standards = SQLiteWritingStandardStore(root / "standards.db")
        self.registry = registry or default_registry(
            source_retriever=source_retriever,
            document_renderer=document_renderer,
            writing_standard_store=self.writing_standards,
        )

    def create(self, raw_config: dict[str, Any], workflow_id: str | None = None) -> str:
        config = ReportConfig.from_dict(raw_config)
        custom = config.extra.get("writing_standard")
        if custom is not None:
            if not isinstance(custom, dict):
                raise ValueError("extra.writing_standard 必须是对象")
            profile = self.register_writing_standard(custom)
            updated = config.to_dict()
            updated["extra"] = {
                **config.extra,
                "writing_standard_profile": profile.id,
            }
            config = ReportConfig.from_dict(updated)
        workflow_id = self.state.create_workflow(config, workflow_id)
        self.state.record_operation(workflow_id, "create", {"config": config.to_dict()})
        return workflow_id

    def register_writing_standard(
        self, definition: dict[str, Any]
    ) -> WritingStandardProfile:
        """Persist a custom, triggerable profile and return its immutable version."""
        required = {"name", "scene", "trigger_keywords", "rules"}
        if not required <= definition.keys():
            raise ValueError(
                "个性化写作标准必须包含 name、scene、trigger_keywords、rules"
            )
        triggers = definition["trigger_keywords"]
        references = definition.get("references", [])
        if not isinstance(triggers, (list, tuple)):
            raise ValueError("trigger_keywords 必须是字符串数组")
        if not isinstance(references, (list, tuple)):
            raise ValueError("references 必须是对象数组")
        return self.writing_standards.register_custom(
            name=str(definition["name"]),
            scene=str(definition["scene"]),
            trigger_keywords=list(triggers),
            rules=definition["rules"],
            references=list(references),
            profile_id=(
                str(definition["id"]) if definition.get("id") else None
            ),
        )

    def list_writing_standards(self) -> list[dict[str, Any]]:
        return [
            profile.to_dict()
            for profile in self.writing_standards.list_profiles()
        ]

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
                profile = WORKFLOW_PROFILES[config.workflow_profile]
                if spec.id not in profile.confirmation_nodes:
                    self.state.set_node(
                        workflow_id, spec.id, NodeStatus.COMPLETED
                    )
                    self.state.record_operation(
                        workflow_id,
                        "auto_skip_checkpoint",
                        {
                            "checkpoint_id": spec.id,
                            "workflow_profile": config.workflow_profile,
                        },
                        spec.id,
                    )
                    continue
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
        final = self.state.node_artifact(workflow_id, "publish", internal=True)
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
        if spec.id == "experience_evolution":
            inputs["_user_operations"] = json.dumps(
                self.state.operations(workflow_id), ensure_ascii=False
            )
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
        routes: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = (
            (
                "requirements_analysis",
                (
                    ("目标受众", 3), ("内容边界", 3), ("前置思考", 3),
                    ("产出形态", 3), ("主题", 1), ("需求", 1),
                    ("audience", 3), ("scope", 2),
                ),
            ),
            (
                "issue_tree",
                (
                    ("议题树", 4), ("子问题", 3), ("问题拆解", 3),
                    ("mece", 3), ("核心问题", 2),
                ),
            ),
            (
                "skill_research",
                (
                    ("检索技能", 4), ("技能仓库", 4), ("github skill", 4),
                    ("openclaw", 4), ("第三方技能", 4), ("技能改造", 4),
                ),
            ),
            (
                "writing_standards",
                (
                    ("写作规范", 5), ("写作标准", 5), ("模板", 3),
                    ("触发词", 4), ("券商模板", 4), ("arxiv格式", 4),
                    ("蓝v", 4), ("公文规范", 4),
                ),
            ),
            (
                "outline",
                (("大纲", 3), ("文章框架", 3), ("章节", 1), ("结构", 1), ("outline", 3)),
            ),
            (
                "research",
                (
                    ("来源", 3), ("链接", 3), ("事实", 2), ("数据", 2),
                    ("材料", 2), ("调研", 2), ("引用", 2),
                    ("source", 3), ("citation", 3),
                ),
            ),
            (
                "evidence_governance",
                (("证据治理", 4), ("可追溯", 3), ("利益相关方", 3), ("证据红线", 3)),
            ),
            (
                "data_processing",
                (
                    ("数据处理", 4), ("评分模型", 4), ("交叉验证", 3),
                    ("论断账本", 4), ("claim ledger", 4),
                ),
            ),
            (
                "material_integration",
                (("素材挂载", 4), ("素材整合", 4), ("章节素材", 3)),
            ),
            (
                "visualization",
                (
                    ("图表", 3), ("可视化", 3), ("流程图", 4),
                    ("架构图", 4), ("chart", 3), ("diagram", 3),
                ),
            ),
            (
                "pressure_test",
                (("压力测试", 4), ("反方论证", 3), ("完整性审计", 3)),
            ),
            (
                "formatting",
                (("格式", 3), ("排版", 3), ("html", 3), ("json", 3), ("markdown", 3)),
            ),
            (
                "review",
                (("复核", 3), ("审核", 2), ("真实性校验", 4), ("合规校验", 4)),
            ),
            (
                "quality_gate",
                (("质量门", 4), ("发布阻断", 4), ("质量分", 3)),
            ),
            (
                "publish",
                (("png导出", 4), ("svg导出", 4), ("报告发布", 4), ("发布包", 3)),
            ),
            (
                "writing",
                (
                    ("篇幅", 3), ("文风", 3), ("措辞", 2), ("论证", 2),
                    ("内容", 1), ("语气", 2), ("style", 3),
                ),
            ),
        )
        scores = {
            candidate: sum(
                weight for keyword, weight in weighted_keywords if keyword in normalized
            )
            for candidate, weighted_keywords in routes
        }
        target = max(scores, key=scores.get) if max(scores.values(), default=0) else "writing"
        self.state.record_operation(
            workflow_id,
            "route_revision",
            {"feedback": feedback, "target_node": target},
            target,
        )
        return target, self.modify(workflow_id, target, feedback)

    def add_comment(
        self,
        workflow_id: str,
        node_id: str,
        comment: str,
        *,
        actor_id: str,
    ) -> None:
        if node_id not in NODE_MAP:
            raise ValueError(f"未知节点: {node_id}")
        if not actor_id.strip() or not comment.strip():
            raise ValueError("actor_id 和 comment 不能为空")
        self.state.config(workflow_id)
        self.state.record_operation(
            workflow_id,
            "comment",
            {"actor_id": actor_id.strip(), "comment": comment.strip()},
            node_id,
        )

    def list_comments(
        self, workflow_id: str, node_id: str | None = None
    ) -> list[dict[str, Any]]:
        comments = self.state.operations(workflow_id, "comment")
        if node_id is not None:
            comments = [item for item in comments if item["node_id"] == node_id]
        return comments

    def apply_approved_learning(
        self,
        workflow_id: str,
        proposal_id: str,
        *,
        approved_by: str,
        skills_root: str | Path,
    ) -> Path:
        if not approved_by.strip():
            raise ValueError("approved_by 不能为空")
        artifact = self.state.node_artifact(
            workflow_id, "experience_evolution", internal=True
        )
        if not artifact:
            raise ValueError("工作流尚无自进化产物")
        payload = json.loads(artifact["content"])
        proposal = next(
            (
                item for item in payload.get("proposals", [])
                if item["id"] == proposal_id
            ),
            None,
        )
        if not proposal:
            raise ValueError(f"学习提案不存在: {proposal_id}")
        if proposal["status"] != "validated_candidate":
            raise ValueError("只有 validated_candidate 可写入 Skill 文档")
        target = proposal["target_skill"]
        allowed = set(self.registry.names) | {"research_report_orchestrator"}
        if target not in allowed:
            raise ValueError(f"提案目标 Skill 不在允许清单: {target}")
        standard_profile = None
        if target == "writing_standards":
            config = self.state.config(workflow_id)
            standard_profile = self.writing_standards.resolve(
                " ".join(
                    (config.topic, config.output_type, config.style, config.audience)
                ),
                config.extra.get("writing_standard_profile"),
            )
            standard_profile = self.writing_standards.append_managed_rule(
                standard_profile.id,
                proposal_id=proposal_id,
                rule=proposal["rule"],
            )
        root = Path(skills_root).resolve()
        skill_file = (root / target / "SKILL.md").resolve()
        if root not in skill_file.parents or not skill_file.exists():
            raise ValueError(f"Skill 文件不存在或越界: {skill_file}")
        text = skill_file.read_text(encoding="utf-8")
        if proposal_id in text:
            return skill_file
        start = "<!-- MANAGED_LEARNINGS_START -->"
        end = "<!-- MANAGED_LEARNINGS_END -->"
        entry = (
            f"- `{proposal_id}` {proposal['rule']} "
            f"(confidence={proposal['confidence']}, approved_by={approved_by})"
        )
        if start in text and end in text:
            text = text.replace(end, entry + "\n" + end)
        else:
            text = text.rstrip() + (
                "\n\n## Managed Learnings\n\n"
                f"{start}\n{entry}\n{end}\n"
            )
        skill_file.write_text(text, encoding="utf-8")
        self.state.record_operation(
            workflow_id,
            "apply_learning",
            {
                "proposal_id": proposal_id,
                "target_skill": target,
                "approved_by": approved_by,
                "path": str(skill_file),
                "writing_standard_profile": (
                    standard_profile.id if standard_profile else None
                ),
                "writing_standard_version": (
                    standard_profile.version if standard_profile else None
                ),
            },
            target if target in NODE_MAP else None,
        )
        return skill_file

    def quarterly_evolution_report(self, year: int, quarter: int) -> str:
        if quarter not in {1, 2, 3, 4}:
            raise ValueError("quarter 必须为 1-4")
        period = f"{year}-Q{quarter}"
        reports = []
        for artifact in self.state.artifacts_by_node("experience_evolution"):
            payload = json.loads(artifact["content"])
            if payload.get("period") == period:
                reports.append(payload)
        proposals = [
            proposal
            for report in reports
            for proposal in report.get("proposals", [])
        ]
        validated = [
            item for item in proposals
            if item["status"] == "validated_candidate"
        ]
        lines = [
            f"# 自进化效果复盘 — {period}",
            "",
            f"- 工作流样本：{len(reports)}",
            f"- 经验提案：{len(proposals)}",
            f"- 已验证候选：{len(validated)}",
            f"- 平均质量分：{self._average_quality(reports):.2f}",
            "",
            "## 已验证候选",
            "",
        ]
        lines.extend(
            f"- {item['target_skill']} · {item['rule']} "
            f"(confidence={item['confidence']})"
            for item in validated
        )
        if not validated:
            lines.append("- 无")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _average_quality(reports: list[dict[str, Any]]) -> float:
        scores = [
            report.get("effectiveness", {}).get("quality_score")
            for report in reports
        ]
        numeric = [float(score) for score in scores if score is not None]
        return sum(numeric) / len(numeric) if numeric else 0.0

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
        artifact = self.state.node_artifact(workflow_id, "publish")
        if not artifact:
            raise ValueError("工作流尚未生成终稿")
        return artifact["content"]


class QualityGateRejected(RuntimeError):
    """Raised after persisting a quality decision that blocks release."""
