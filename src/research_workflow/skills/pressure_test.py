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
        draft = request.inputs.get(
            "content_optimization",
            request.inputs.get("citation_management", request.inputs.get("writing", "")),
        )
        requirements_text = request.inputs["requirements_analysis"]
        outline_text = request.inputs["outline"]
        research_text = request.inputs["research"]
        evidence_text = request.inputs["evidence_governance"]
        issue_tree_text = request.inputs["issue_tree"]
        materials_text = request.inputs["material_integration"]
        visualizations_text = request.inputs["visualization"]
        verification = json.loads(request.inputs.get("claim_verification", "{}"))
        quant = json.loads(request.inputs.get("quant_finance_research", "{}"))
        model_analysis = None
        if self.generator:
            prompt = (
                "独立审计初稿，不要把审查意见折叠进正文。执行逻辑、证据、最强反方论证、"
                "完整性四项审计，输出 JSON 弱点报告和定稿前修复清单。\n"
                f"初稿：{draft}\n大纲：{outline_text}\n证据账本：{evidence_text}\n"
                f"议题树：{issue_tree_text}\n需求：{requirements_text}\n"
                f"调研：{research_text}\n素材映射：{materials_text}\n"
                f"可视化：{visualizations_text}"
            )
            generated = self.generator.generate(
                system="你是持怀疑态度的独立报告压力测试员。",
                prompt=prompt, max_tokens=5000,
            )
            try:
                model_analysis = json.loads(generated)
            except json.JSONDecodeError:
                model_analysis = {"raw": generated, "parse_error": True}

        outline = json.loads(outline_text)
        research = json.loads(research_text)
        evidence = json.loads(evidence_text)
        issue_tree = json.loads(issue_tree_text)
        materials = json.loads(materials_text)
        visualizations = json.loads(visualizations_text)
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
        missing_categories = research.get("retrieval_summary", {}).get(
            "missing_categories", []
        )
        if missing_categories:
            evidence_gaps.append(
                {
                    "severity": "high",
                    "location": "调研来源",
                    "message": "缺少来源类别：" + "、".join(missing_categories),
                    "repair": "从官方、学术和主流社交媒体补齐三类来源",
                }
            )
        if evidence.get("metrics", {}).get("original_link_coverage", 0.0) < 1.0:
            evidence_gaps.append(
                {
                    "severity": "high",
                    "location": "证据账本",
                    "message": "部分素材缺少原始来源链接",
                    "repair": "补充每项事实和数据的原始 URL",
                }
            )
        if verification.get("unsupported_claim_ids"):
            evidence_gaps.append(
                {
                    "severity": "high",
                    "location": "论断验证",
                    "message": "存在未验证论断："
                    + "、".join(verification["unsupported_claim_ids"]),
                    "repair": "补充原文证据片段或修正数字、冲突和来源独立性",
                }
            )
        if quant.get("applicable") and not quant.get("hard_gates_passed"):
            evidence_gaps.append(
                {
                    "severity": "high",
                    "location": "量化金融工程",
                    "message": "；".join(quant.get("issues", [])),
                    "repair": "补齐数据口径、绩效来源、交易成本和样本外偏差检查",
                }
            )
        if materials.get("metrics", {}).get("mount_coverage", 0.0) < 1.0:
            completeness_issues.append(
                {
                    "severity": "high",
                    "location": "章节素材",
                    "message": "存在未挂载到大纲章节的素材",
                }
            )
        if not visualizations.get("assets"):
            completeness_issues.append(
                {
                    "severity": "medium",
                    "location": "可视化",
                    "message": "未生成任何可视化成果",
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
            "model_analysis": model_analysis,
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
                "prompt_version": "1.0" if self.generator else None,
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
