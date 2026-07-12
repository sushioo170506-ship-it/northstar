from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_workflow.models import NodeStatus, WorkflowStatus
from research_workflow.orchestrator import ResearchReportOrchestrator


CHECKPOINTS = (
    "outline_confirmation",
    "draft_confirmation",
    "pre_review_confirmation",
)


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
            "extra": {
                "sources": [
                    {"id": "S1", "title": "政策原文", "content": "治理需要风险分级。"}
                ]
            },
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

    def test_checkpoints_resume_and_final_output(self) -> None:
        workflow_id = self.create()
        first = self.workflow.run(workflow_id)
        self.assertEqual(first.waiting_at, "outline_confirmation")

        reloaded = ResearchReportOrchestrator(self.root)
        reloaded.confirm(workflow_id, "outline_confirmation")
        second = reloaded.run(workflow_id)
        self.assertEqual(second.waiting_at, "draft_confirmation")
        reloaded.confirm(workflow_id, "draft_confirmation")
        third = reloaded.run(workflow_id)
        self.assertEqual(third.waiting_at, "pre_review_confirmation")
        reloaded.confirm(workflow_id, "pre_review_confirmation")
        final = reloaded.run(workflow_id)

        self.assertEqual(final.status, WorkflowStatus.COMPLETED)
        self.assertIn("# 生成式人工智能治理研究", reloaded.final_report(workflow_id))
        self.assertEqual(reloaded.state.node(workflow_id, "research")["attempts"], 1)

    def test_modification_only_reruns_descendants(self) -> None:
        workflow_id = self.create()
        complete(self.workflow, workflow_id)
        old_research = self.workflow.state.node_artifact(workflow_id, "research")["id"]
        old_outline = self.workflow.state.node_artifact(workflow_id, "outline")["id"]

        affected = self.workflow.modify(workflow_id, "writing", "加强风险讨论")
        self.assertNotIn("research", affected)
        self.assertNotIn("outline", affected)
        self.assertIn("review", affected)
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

    def test_twenty_deterministic_runs_meet_success_threshold(self) -> None:
        successes = 0
        for index in range(20):
            child = ResearchReportOrchestrator(self.root / f"batch-{index}")
            workflow_id = child.create(
                {
                    "topic": f"可靠性样例 {index}",
                    "expected_length": 500,
                    "output_format": "markdown",
                }
            )
            if complete(child, workflow_id).status == WorkflowStatus.COMPLETED:
                successes += 1
        self.assertGreaterEqual(successes / 20, 0.95)


if __name__ == "__main__":
    unittest.main()
