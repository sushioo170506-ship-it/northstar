"""Independent draft stress test kept separate from report prose."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult


class PressureTestSkill(Skill):
    name = "pressure_test"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        draft = request.inputs["writing"]
        outline_text = request.inputs["outline"]
        evidence_text = request.inputs["evidence_governance"]
        issue_tree_text = request.inputs["issue_tree"]
        if self.generator:
            prompt = (
                "独立审计初稿，不要把审查意见折叠进正文。执行逻辑、证据、最强反方论证、"
                "完整性四项审计，输出 JSON 弱点报告和定稿前修复清单。\n"
                f"初稿：{draft}\n大纲：{outline_text}\n证据账本：{evidence_text}\n"
                f"议题树：{issue_tree_text}"
            )
            content = self.generator.generate(
                system="你是持怀疑态度的独立报告压力测试员。",
                prompt=prompt, max_tokens=5000,
            )
            return SkillResult(content, "pressure_test", {"prompt_version": "1.0"})

        outline = json.loads(outline_text)
        evidence = json.loads(evidence_text)
        issue_tree = json.loads(issue_tree_text)
        logic_issues: list[dict[str, str]] = []
        evidence_gaps: list[dict[str, str]] = []
        completeness_issues: list[dict[str, str]] = []
        certainty_markers = ("因此必然", "已经证明", "一定会", "毫无疑问")
        for marker in certainty_markers:
            if marker in draft:
                logic_issues.append(
                    {
                        "severity": "high",
                        "location": "全文",
                        "message": f"检测到未经限定的确定性推断：{marker}",
                    }
                )
        if not evidence.get("sources"):
            evidence_gaps.append(
                {
                    "severity": "high",
                    "location": "全文",
                    "message": "没有任何可治理来源，不能作为决策报告发布",
                    "repair": "至少补充一个可追溯来源并重新执行证据治理",
                }
            )
        if "资料缺口" in draft:
            evidence_gaps.append(
                {
                    "severity": "medium",
                    "location": "全文",
                    "message": "报告明确存在待检索资料缺口",
                    "repair": "补充可追溯来源后重新执行证据治理",
                }
            )
        traceability = evidence.get("metrics", {}).get("traceability_ratio", 0.0)
        if traceability < 1.0 and evidence.get("sources"):
            evidence_gaps.append(
                {
                    "severity": "high",
                    "location": "证据账本",
                    "message": "部分来源不可完整追溯",
                    "repair": "补充来源标题、原文或 URL",
                }
            )
        for section in outline.get("sections", []):
            if section.get("title") and section["title"] not in draft:
                completeness_issues.append(
                    {
                        "severity": "high",
                        "location": section.get("id", "unknown"),
                        "message": f"缺少大纲章节：{section['title']}",
                    }
                )
        issue_questions = [item.get("question", "") for item in issue_tree.get("issues", [])]
        counterarguments = [
            {
                "target": "核心判断",
                "argument": "现有证据可能只反映特定时间窗口或样本，外推条件需要验证。",
                "invalidate_when": "关键来源过时、样本偏差显著或外部条件发生结构性变化",
            },
            {
                "target": "实施建议",
                "argument": "建议的成本、组织约束和机会成本可能高于预期收益。",
                "invalidate_when": "缺少资源、责任主体或可验证的阶段目标",
            },
        ]
        red_lines = list(evidence.get("red_lines", []))
        confidence = "low" if red_lines else (
            "medium" if evidence_gaps or not evidence.get("sources") else "high"
        )
        repair_actions = [
            item["repair"] for item in evidence_gaps if item.get("repair")
        ] + [
            f"补写或恢复 {item['location']}" for item in completeness_issues
        ]
        payload = {
            "overall_confidence": confidence,
            "logic_audit": {"issues": logic_issues},
            "evidence_audit": {"gaps": evidence_gaps, "red_lines": red_lines},
            "counterargument_audit": {"items": counterarguments},
            "completeness_audit": {
                "issues": completeness_issues,
                "issue_tree_questions_reviewed": issue_questions,
            },
            "repair_actions": repair_actions,
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "pressure_test",
            {
                "overall_confidence": confidence,
                "issue_count": len(logic_issues) + len(evidence_gaps)
                + len(completeness_issues),
                "red_line_count": len(red_lines),
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        required = {
            "logic_audit", "evidence_audit", "counterargument_audit",
            "completeness_audit", "repair_actions",
        }
        if not required <= payload.keys():
            raise ValueError("pressure_test 缺少必要审计维度")
