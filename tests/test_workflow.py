from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_workflow.contracts import FunctionGenerator
from research_workflow.models import (
    NodeStatus,
    ReportConfig,
    SkillRequest,
    WorkflowStatus,
)
from research_workflow.orchestrator import QualityGateRejected, ResearchReportOrchestrator
from research_workflow.skills.quality_gate import DIMENSIONS, QualityGateSkill


CHECKPOINTS = (
    "issue_tree_confirmation",
    "outline_confirmation",
    "draft_confirmation",
    "pre_review_confirmation",
)


def compliant_sources(prefix: str = "S"):
    return [
        {
            "id": f"{prefix}-OFFICIAL",
            "title": "官方政策原文",
            "content": "官方数据显示相关指标为 42%。",
            "url": "https://official.example/policy",
            "published_at": "2026-07-01",
            "category": "official",
            "source_type": "primary",
            "issue_ids": ["ISSUE-01"],
        },
        {
            "id": f"{prefix}-ACADEMIC",
            "title": "同行评审研究",
            "content": "学术研究样本量为 1200。",
            "url": "https://academic.example/paper",
            "published_at": "2026-06-01",
            "category": "academic",
            "source_type": "independent",
            "issue_ids": ["ISSUE-02"],
        },
        {
            "id": f"{prefix}-SOCIAL",
            "title": "主流社交平台公开讨论",
            "content": "公开讨论中有 35% 的样本关注实施风险。",
            "url": "https://social.example/post",
            "published_at": "2026-07-10",
            "category": "social_media",
            "source_type": "stakeholder",
            "issue_ids": ["ISSUE-03"],
        },
    ]


def complete(orchestrator: ResearchReportOrchestrator, workflow_id: str):
    for checkpoint in CHECKPOINTS:
        outcome = orchestrator.run(workflow_id)
        assert outcome.waiting_at == checkpoint
        orchestrator.confirm(workflow_id, checkpoint, "测试确认")
    return orchestrator.run(workflow_id)


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workflow = ResearchReportOrchestrator(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def create(self, **overrides) -> str:
        config = {
            "topic": "生成式人工智能治理研究",
            "expected_length": 1200,
            "style": "专业、客观",
            "output_format": "markdown",
            "output_type": "决策研究报告",
            "audience": "企业管理层",
            "content_boundaries": ["不得包含：未经来源支持的确定性结论"],
            "prior_thoughts": "需要平衡创新收益与治理风险。",
            "extra": {"sources": compliant_sources()},
        }
        config.update(overrides)
        return self.workflow.create(config)

    def test_input_validation_and_normalization(self) -> None:
        workflow_id = self.workflow.create(
            {"topic": "  AI   治理 ", "expected_length": "800", "output_format": "md"}
        )
        config = self.workflow.state.config(workflow_id)
        self.assertEqual(config.topic, "AI 治理")
        self.assertEqual(config.expected_length, 800)
        self.assertEqual(config.output_format, "markdown")
        with self.assertRaises(ValueError):
            self.workflow.create({"topic": "", "expected_length": 100})

    def test_missing_source_categories_block_release(self) -> None:
        workflow_id = self.create(extra={"sources": [compliant_sources()[0]]})
        for checkpoint in CHECKPOINTS:
            outcome = self.workflow.run(workflow_id)
            self.assertEqual(outcome.waiting_at, checkpoint)
            self.workflow.confirm(workflow_id, checkpoint)
        with self.assertRaises(QualityGateRejected):
            self.workflow.run(workflow_id)
        gate = json.loads(
            self.workflow.state.node_artifact(workflow_id, "quality_gate")["content"]
        )
        self.assertEqual(
            gate["requirements_checks"]["missing_source_categories"],
            ["academic", "social_media"],
        )

    def test_content_boundary_violation_blocks_release(self) -> None:
        workflow_id = self.create(content_boundaries=["禁止：本节围绕"])
        for checkpoint in CHECKPOINTS:
            outcome = self.workflow.run(workflow_id)
            self.assertEqual(outcome.waiting_at, checkpoint)
            self.workflow.confirm(workflow_id, checkpoint)
        with self.assertRaises(QualityGateRejected):
            self.workflow.run(workflow_id)
        gate = json.loads(
            self.workflow.state.node_artifact(workflow_id, "quality_gate")["content"]
        )
        self.assertEqual(
            gate["requirements_checks"]["boundary_violations"], ["本节围绕"]
        )

    def test_unmapped_materials_block_release(self) -> None:
        sources = compliant_sources("UNMAPPED")
        for source in sources:
            source["issue_ids"] = ["ISSUE-UNKNOWN"]
        workflow_id = self.create(extra={"sources": sources})
        for checkpoint in CHECKPOINTS:
            outcome = self.workflow.run(workflow_id)
            self.assertEqual(outcome.waiting_at, checkpoint)
            self.workflow.confirm(workflow_id, checkpoint)
        with self.assertRaises(QualityGateRejected):
            self.workflow.run(workflow_id)
        gate = json.loads(
            self.workflow.state.node_artifact(workflow_id, "quality_gate")["content"]
        )
        self.assertEqual(
            gate["requirements_checks"]["material_mount_coverage"], 0.0
        )

    def test_checkpoints_resume_and_final_output(self) -> None:
        workflow_id = self.create()
        first = self.workflow.run(workflow_id)
        self.assertEqual(first.waiting_at, "issue_tree_confirmation")

        reloaded = ResearchReportOrchestrator(self.root)
        reloaded.confirm(workflow_id, "issue_tree_confirmation")
        issue_tree = reloaded.run(workflow_id)
        self.assertEqual(issue_tree.waiting_at, "outline_confirmation")
        reloaded.confirm(workflow_id, "outline_confirmation")
        second = reloaded.run(workflow_id)
        self.assertEqual(second.waiting_at, "draft_confirmation")
        reloaded.confirm(workflow_id, "draft_confirmation")
        third = reloaded.run(workflow_id)
        self.assertEqual(third.waiting_at, "pre_review_confirmation")
        reloaded.confirm(workflow_id, "pre_review_confirmation")
        final = reloaded.run(workflow_id)

        self.assertEqual(final.status, WorkflowStatus.COMPLETED)
        final_report = reloaded.final_report(workflow_id)
        self.assertIn("# 生成式人工智能治理研究", final_report)
        self.assertIn("https://official.example/policy", final_report)
        self.assertIn("https://academic.example/paper", final_report)
        self.assertIn("https://social.example/post", final_report)
        self.assertEqual(reloaded.state.node(workflow_id, "research")["attempts"], 1)
        self.assertEqual(
            reloaded.state.node(workflow_id, "quality_gate")["status"], NodeStatus.COMPLETED
        )
        gate = reloaded.state.node_artifact(workflow_id, "quality_gate")
        self.assertTrue(json.loads(gate["content"])["passed"])
        ledger = json.loads(
            reloaded.state.node_artifact(workflow_id, "evidence_governance")["content"]
        )
        self.assertEqual(ledger["issue_coverage"]["ISSUE-01"], ["S-OFFICIAL"])
        issue_tree = json.loads(
            reloaded.state.node_artifact(workflow_id, "issue_tree")["content"]
        )
        self.assertTrue(all(issue["children"] for issue in issue_tree["issues"]))
        self.assertTrue(all(issue["necessity"] for issue in issue_tree["issues"]))
        brief = json.loads(
            reloaded.state.node_artifact(workflow_id, "requirements_analysis")["content"]
        )
        self.assertEqual(brief["audience"], "企业管理层")
        materials = reloaded.state.node_artifact(workflow_id, "material_integration")
        self.assertEqual(json.loads(materials["content"])["metrics"]["mount_coverage"], 1.0)
        visuals = reloaded.state.node_artifact(workflow_id, "visualization")
        self.assertGreaterEqual(json.loads(visuals["content"])["metrics"]["asset_count"], 2)

    def test_modification_only_reruns_descendants(self) -> None:
        workflow_id = self.create()
        complete(self.workflow, workflow_id)
        old_research = self.workflow.state.node_artifact(workflow_id, "research")["id"]
        old_outline = self.workflow.state.node_artifact(workflow_id, "outline")["id"]

        affected = self.workflow.modify(workflow_id, "writing", "加强风险讨论")
        self.assertNotIn("research", affected)
        self.assertNotIn("outline", affected)
        self.assertIn("pressure_test", affected)
        self.assertIn("review", affected)
        self.assertIn("quality_gate", affected)
        self.assertEqual(
            self.workflow.state.node(workflow_id, "writing")["status"],
            NodeStatus.INVALIDATED,
        )
        self.assertEqual(
            self.workflow.state.node_artifact(workflow_id, "research")["id"], old_research
        )
        self.assertEqual(
            self.workflow.state.node_artifact(workflow_id, "outline")["id"], old_outline
        )

        self.assertEqual(self.workflow.run(workflow_id).waiting_at, "draft_confirmation")
        self.workflow.confirm(workflow_id, "draft_confirmation")
        self.assertEqual(
            self.workflow.run(workflow_id).waiting_at, "pre_review_confirmation"
        )
        self.workflow.confirm(workflow_id, "pre_review_confirmation")
        self.assertEqual(self.workflow.run(workflow_id).status, WorkflowStatus.COMPLETED)
        self.assertEqual(self.workflow.state.node(workflow_id, "research")["attempts"], 1)
        self.assertEqual(self.workflow.state.node(workflow_id, "writing")["attempts"], 2)
        active = self.workflow.context.query(
            workflow_id, "风险讨论", node_ids={"writing"}, limit=100
        )
        active_artifact_ids = {item.metadata["artifact_id"] for item in active}
        self.assertEqual(len(active_artifact_ids), 1)
        self.assertEqual(
            active_artifact_ids,
            {self.workflow.state.node_artifact(workflow_id, "writing")["id"]},
        )

    def test_formats_are_valid(self) -> None:
        for output_format in ("html", "json", "text"):
            child = ResearchReportOrchestrator(self.root / output_format)
            workflow_id = child.create(
                {
                    "topic": "格式测试",
                    "expected_length": 500,
                    "output_format": output_format,
                    "extra": {"sources": compliant_sources(f"FORMAT-{output_format}")},
                }
            )
            complete(child, workflow_id)
            report = child.final_report(workflow_id)
            if output_format == "html":
                self.assertTrue(report.startswith("<!doctype html>"))
            elif output_format == "json":
                self.assertEqual(json.loads(report)["title"], "格式测试")
            else:
                self.assertNotIn("# ", report)

    def test_revision_router_returns_to_precise_stage(self) -> None:
        workflow_id = self.create()
        complete(self.workflow, workflow_id)
        target, affected = self.workflow.request_revision(
            workflow_id, "请调整图表和架构图的表达"
        )
        self.assertEqual(target, "visualization")
        self.assertIn("writing", affected)
        self.assertIn("quality_gate", affected)
        self.assertNotIn("material_integration", affected)
        snapshot = self.workflow.state.snapshot(workflow_id)
        operations = [row["operation"] for row in snapshot["operations"]]
        self.assertIn("route_revision", operations)
        routing_id = self.create()
        target, _ = self.workflow.request_revision(routing_id, "调整主题下的议题树和子问题")
        self.assertEqual(target, "issue_tree")
        target, _ = self.workflow.request_revision(routing_id, "修改章节里的来源链接")
        self.assertEqual(target, "research")

    def test_long_context_is_chunked_losslessly_and_retrievable(self) -> None:
        workflow_id = self.create(expected_length=105_000)
        outcome = complete(self.workflow, workflow_id)
        self.assertEqual(outcome.status, WorkflowStatus.COMPLETED)
        report = self.workflow.final_report(workflow_id)
        self.assertGreater(len(report), 100_000)
        artifact = self.workflow.state.node_artifact(workflow_id, "writing")
        self.assertGreater(artifact["chunk_count"], 6)
        self.assertEqual(len(artifact["content"]), len(report))
        matches = self.workflow.context.query(
            workflow_id, "风险 局限 潜在偏差", node_ids={"writing"}, limit=5
        )
        self.assertTrue(matches)
        self.assertTrue(all(item.node_id == "writing" for item in matches))

    def test_evidence_red_line_blocks_release(self) -> None:
        workflow_id = self.create(
            extra={
                "sources": [
                    {
                        "id": "BAD-1",
                        "title": "虚构材料",
                        "content": "不可用于决策",
                        "critical": True,
                        "fabricated": True,
                    }
                ]
            }
        )
        for checkpoint in CHECKPOINTS:
            outcome = self.workflow.run(workflow_id)
            self.assertEqual(outcome.waiting_at, checkpoint)
            self.workflow.confirm(workflow_id, checkpoint)
        with self.assertRaises(QualityGateRejected):
            self.workflow.run(workflow_id)
        self.assertEqual(
            self.workflow.state.workflow_status(workflow_id), WorkflowStatus.FAILED
        )
        gate_node = self.workflow.state.node(workflow_id, "quality_gate")
        self.assertEqual(gate_node["status"], NodeStatus.FAILED)
        gate = self.workflow.state.artifact(gate_node["output_artifact_id"])
        decision = json.loads(gate["content"])
        self.assertFalse(decision["passed"])
        self.assertEqual(decision["decision"], "block_release")
        self.assertTrue(decision["red_lines"])
        with self.assertRaises(ValueError):
            self.workflow.final_report(workflow_id)
        with self.assertRaises(PermissionError):
            self.workflow.state.node_artifact(workflow_id, "review")
        with self.assertRaises(QualityGateRejected):
            self.workflow.run(workflow_id)
        with self.assertRaises(ValueError):
            self.workflow.update_sources(workflow_id, [], "错误地清空来源")
        affected = self.workflow.update_sources(
            workflow_id,
            compliant_sources("REPLACEMENT"),
            "移除编造来源并替换为官方材料",
        )
        self.assertIn("quality_gate", affected)
        recovered = complete(self.workflow, workflow_id)
        self.assertEqual(recovered.status, WorkflowStatus.COMPLETED)
        recovered_gate = json.loads(
            self.workflow.state.node_artifact(workflow_id, "quality_gate")["content"]
        )
        self.assertTrue(recovered_gate["passed"])

    def test_no_sources_are_disclosed_and_block_release(self) -> None:
        workflow_id = self.workflow.create(
            {
                "topic": "无来源报告",
                "expected_length": 500,
                "output_format": "markdown",
            }
        )
        for checkpoint in CHECKPOINTS:
            outcome = self.workflow.run(workflow_id)
            self.assertEqual(outcome.waiting_at, checkpoint)
            self.workflow.confirm(workflow_id, checkpoint)
        with self.assertRaises(QualityGateRejected):
            self.workflow.run(workflow_id)
        pressure = json.loads(
            self.workflow.state.node_artifact(workflow_id, "pressure_test")["content"]
        )
        self.assertTrue(pressure["evidence_audit"]["gaps"])
        gate = self.workflow.state.node_artifact(workflow_id, "quality_gate")
        self.assertFalse(json.loads(gate["content"])["passed"])

    def test_generator_cannot_bypass_missing_source_gate(self) -> None:
        generated = json.dumps(
            {
                "passed": True,
                "total_score": 35,
                "red_lines": [],
                "dimensions": {name: 5 for name in DIMENSIONS},
                "decision": "allow_release",
            },
            ensure_ascii=False,
        )
        skill = QualityGateSkill(
            FunctionGenerator(lambda _system, _prompt, _max_tokens: generated)
        )
        request = SkillRequest(
            workflow_id="generator-test",
            node_id="quality_gate",
            config=ReportConfig.from_dict({"topic": "模型门控测试"}),
            inputs={
                "review": "# 报告\n风险、建议与资料缺口",
                "requirements_analysis": json.dumps(
                    {
                        "deliverable": {"expected_length": 500},
                        "audience": "测试受众",
                        "style": "专业",
                        "content_boundaries": [],
                    }
                ),
                "evidence_governance": json.dumps(
                    {"metrics": {"source_count": 0}, "red_lines": []}
                ),
                "material_integration": json.dumps(
                    {"sections": {}, "metrics": {"mount_coverage": 0.0}}
                ),
                "visualization": json.dumps({"assets": []}),
                "pressure_test": json.dumps({"repair_actions": []}),
            },
        )
        result = skill.execute(request)
        skill.validate(result)
        decision = json.loads(result.content)
        self.assertFalse(decision["passed"])
        self.assertEqual(decision["decision"], "block_release")
        red_line_request = SkillRequest(
            workflow_id="generator-red-line-test",
            node_id="quality_gate",
            config=request.config,
            inputs={
                **request.inputs,
                "evidence_governance": json.dumps(
                    {
                        "metrics": {"source_count": 1},
                        "red_lines": [{"code": "FABRICATED_SOURCE"}],
                    }
                ),
            },
        )
        red_line_result = skill.execute(red_line_request)
        skill.validate(red_line_result)
        self.assertFalse(json.loads(red_line_result.content)["passed"])

    def test_twenty_deterministic_runs_meet_success_threshold(self) -> None:
        successes = 0
        for index in range(20):
            child = ResearchReportOrchestrator(self.root / f"batch-{index}")
            workflow_id = child.create(
                {
                    "topic": f"可靠性样例 {index}",
                    "expected_length": 500,
                    "output_format": "markdown",
                    "extra": {"sources": compliant_sources(f"BATCH-{index}")},
                }
            )
            if complete(child, workflow_id).status == WorkflowStatus.COMPLETED:
                successes += 1
        self.assertGreaterEqual(successes / 20, 0.95)


if __name__ == "__main__":
    unittest.main()
