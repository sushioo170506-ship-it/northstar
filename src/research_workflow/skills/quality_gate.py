"""D1-D7 quality scoring and red-line release decision."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult


DIMENSIONS = (
    "D1 事实准确性",
    "D2 逻辑严密性",
    "D3 事实与观点分离",
    "D4 结构完整性",
    "D5 So What 检验",
    "D6 时效性与边界感",
    "D7 量级感",
)


class QualityGateSkill(Skill):
    name = "quality_gate"

    def __init__(
        self, generator: TextGenerator | None = None, pass_score: float = 24.0
    ) -> None:
        self.generator = generator
        self.pass_score = pass_score

    def execute(self, request: SkillRequest) -> SkillResult:
        final_report = request.inputs["review"]
        evidence_text = request.inputs["evidence_governance"]
        pressure_text = request.inputs["pressure_test"]
        evidence = json.loads(evidence_text)
        if self.generator:
            prompt = (
                "先检查红线，再按 D1事实准确性、D2逻辑严密性、D3事实观点分离、"
                "D4结构完整性、D5 So What、D6边界感、D7量级感各评 0-5 分。"
                f"总分低于 {self.pass_score} 或触发红线必须拒绝。严格输出 JSON。\n"
                f"终稿：{final_report}\n证据账本：{evidence_text}\n压力测试：{pressure_text}"
            )
            content = self.generator.generate(
                system="你是拥有发布否决权的独立质量门审核员。",
                prompt=prompt, max_tokens=4000,
            )
            generated = json.loads(content)
            dimensions = generated.get("dimensions", {})
            total = round(sum(float(dimensions.get(name, 0.0)) for name in DIMENSIONS), 1)
            red_lines = list(evidence.get("red_lines", []))
            for item in generated.get("red_lines", []):
                if item not in red_lines:
                    red_lines.append(item)
            source_count = evidence.get("metrics", {}).get("source_count", 0)
            passed = not red_lines and source_count > 0 and total >= self.pass_score
            generated.update(
                {
                    "passed": passed,
                    "pass_score": self.pass_score,
                    "total_score": total,
                    "maximum_score": 35,
                    "red_lines": red_lines,
                    "decision": "allow_release" if passed else "block_release",
                }
            )
            content = json.dumps(generated, ensure_ascii=False, indent=2)
            return SkillResult(
                content,
                "quality_gate",
                {
                    "prompt_version": "1.0",
                    "quality_passed": passed,
                    "total_score": total,
                    "red_line_count": len(red_lines),
                    "pass_score": self.pass_score,
                },
            )

        pressure = json.loads(pressure_text)
        source_count = evidence.get("metrics", {}).get("source_count", 0)
        traceability = evidence.get("metrics", {}).get("traceability_ratio", 0.0)
        logic_issues = pressure.get("logic_audit", {}).get("issues", [])
        completeness = pressure.get("completeness_audit", {}).get("issues", [])
        evidence_gaps = pressure.get("evidence_audit", {}).get("gaps", [])
        red_lines = list(evidence.get("red_lines", []))
        for item in pressure.get("evidence_audit", {}).get("red_lines", []):
            if item not in red_lines:
                red_lines.append(item)

        d1 = 3.0 if source_count == 0 else max(1.0, round(5.0 * traceability, 1))
        d2 = max(0.0, 5.0 - len(logic_issues))
        d3 = 4.5 if ("资料缺口" in final_report or "待检索" in final_report) else 4.0
        d4 = max(0.0, 5.0 - len(completeness))
        d5 = 5.0 if "建议" in final_report else 3.0
        d6 = 5.0 if ("风险" in final_report or "局限" in final_report) else 3.0
        d7 = 3.5
        scores = dict(zip(DIMENSIONS, (d1, d2, d3, d4, d5, d6, d7), strict=True))
        total = round(sum(scores.values()), 1)
        passed = source_count > 0 and not red_lines and total >= self.pass_score
        problems = []
        if evidence_gaps:
            problems.append("存在证据缺口，需在决策使用时披露")
        if source_count == 0:
            problems.append("没有可追溯来源，不能发布决策报告")
        if completeness:
            problems.append("存在未覆盖的大纲章节")
        if red_lines:
            problems.append("触发证据红线")
        if total < self.pass_score:
            problems.append(f"总分 {total} 低于门槛 {self.pass_score}")
        payload = {
            "passed": passed,
            "pass_score": self.pass_score,
            "total_score": total,
            "maximum_score": 35,
            "red_lines": red_lines,
            "dimensions": scores,
            "problems": problems,
            "required_actions": pressure.get("repair_actions", []),
            "decision": "allow_release" if passed else "block_release",
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "quality_gate",
            {
                "quality_passed": passed,
                "total_score": total,
                "red_line_count": len(red_lines),
                "pass_score": self.pass_score,
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not isinstance(payload.get("passed"), bool):
            raise ValueError("quality_gate 必须返回布尔 passed")
        if set(payload.get("dimensions", {})) != set(DIMENSIONS):
            raise ValueError("quality_gate 必须返回完整 D1-D7 评分")
        scores = payload["dimensions"]
        if any(
            not isinstance(score, (int, float)) or not 0 <= score <= 5
            for score in scores.values()
        ):
            raise ValueError("quality_gate 每个维度必须为 0-5 分")
        total = round(sum(float(score) for score in scores.values()), 1)
        if payload.get("total_score") != total:
            raise ValueError("quality_gate 总分与维度评分不一致")
        expected = (
            not payload.get("red_lines")
            and total >= float(payload.get("pass_score", self.pass_score))
        )
        if payload["passed"] and not expected:
            raise ValueError("quality_gate 发布决定与红线或分数不一致")
        expected_decision = "allow_release" if payload["passed"] else "block_release"
        if payload.get("decision") != expected_decision:
            raise ValueError("quality_gate decision 与 passed 不一致")
