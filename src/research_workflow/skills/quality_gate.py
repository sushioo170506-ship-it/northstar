"""D1-D7 quality scoring and red-line release decision."""

from __future__ import annotations

import json
import re

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult
from ..profiles import WORKFLOW_PROFILES
from ..renderers import MarkdownTableParser


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
    REQUIRED_SOURCE_CATEGORIES = {"industry", "academic", "social_media"}

    def __init__(
        self, generator: TextGenerator | None = None, pass_score: float = 24.0
    ) -> None:
        self.generator = generator
        self.pass_score = pass_score

    def execute(self, request: SkillRequest) -> SkillResult:
        final_report = request.inputs["review"]
        capability = json.loads(request.inputs["capability_sweep"])
        skill_research = json.loads(request.inputs["skill_research"])
        requirements = json.loads(request.inputs["requirements_analysis"])
        profile = WORKFLOW_PROFILES[request.config.workflow_profile]
        pass_score = float(
            request.config.extra.get(
                "quality_pass_score", profile.quality_pass_score
            )
        )
        requirements["minimum_visual_assets"] = int(
            request.config.extra.get(
                "minimum_visual_assets", profile.minimum_visual_assets
            )
        )
        outline = json.loads(request.inputs["outline"])
        cited_draft = request.inputs.get(
            "content_optimization", request.inputs["citation_management"]
        )
        evidence_text = request.inputs["evidence_governance"]
        processed = json.loads(request.inputs["data_processing"])
        materials = json.loads(request.inputs["material_integration"])
        visualizations = json.loads(request.inputs["visualization"])
        pressure_text = request.inputs["pressure_test"]
        writing_standard = json.loads(request.inputs["writing_standards"])
        evidence = json.loads(evidence_text)
        evidence_grades = processed.get("evidence_grades", {})
        graded_total = sum(evidence_grades.values())
        high_grade_ratio = (
            sum(evidence_grades.get(grade, 0) for grade in ("A+", "A", "B"))
            / graded_total if graded_total else 0.0
        )
        minimum_high_grade_ratio = float(
            request.config.extra.get(
                "minimum_high_grade_ratio", profile.minimum_high_grade_ratio
            )
        )
        requirements_policy = self._requirements_policy(
            final_report, requirements, evidence, processed, materials,
            visualizations, capability, skill_research, outline, cited_draft,
        )
        reference_status = writing_standard["reference_selection"]["status"]
        reference_required = bool(
            request.config.extra.get("require_verified_reference_templates", False)
        )
        standards_compliant = (
            (
                request.config.output_format != "feishu"
                or writing_standard["security"]["external_delivery_allowed"]
            )
            and (
                not reference_required
                or reference_status in {"verified", "builtin_authority"}
            )
        )
        requirements_policy["writing_standard_compliant"] = standards_compliant
        requirements_policy["compliant"] = (
            requirements_policy["compliant"] and standards_compliant
        )
        if self.generator:
            prompt = (
                "先检查红线，再按 D1事实准确性、D2逻辑严密性、D3事实观点分离、"
                "D4结构完整性、D5 So What、D6边界感、D7量级感各评 0-5 分。"
                f"总分低于 {pass_score} 或触发红线必须拒绝。严格输出 JSON。\n"
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
            metrics = evidence.get("metrics", {})
            categories = set(metrics.get("source_categories", []))
            link_coverage = metrics.get("original_link_coverage", 0.0)
            all_links_present = all(
                source.get("original_url") in final_report
                for source in evidence.get("sources", []) if source.get("original_url")
            )
            passed = (
                not red_lines
                and source_count > 0
                and self.REQUIRED_SOURCE_CATEGORIES <= categories
                and link_coverage == 1.0
                and all_links_present
                and requirements_policy["compliant"]
                and high_grade_ratio >= minimum_high_grade_ratio
                and total >= pass_score
            )
            generated.update(
                {
                    "passed": passed,
                    "pass_score": pass_score,
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
                    "pass_score": pass_score,
                },
            )

        pressure = json.loads(pressure_text)
        source_count = evidence.get("metrics", {}).get("source_count", 0)
        traceability = evidence.get("metrics", {}).get("traceability_ratio", 0.0)
        link_coverage = evidence.get("metrics", {}).get("original_link_coverage", 0.0)
        categories = set(evidence.get("metrics", {}).get("source_categories", []))
        category_coverage = len(self.REQUIRED_SOURCE_CATEGORIES & categories) / len(
            self.REQUIRED_SOURCE_CATEGORIES
        )
        logic_issues = pressure.get("logic_audit", {}).get("issues", [])
        completeness = pressure.get("completeness_audit", {}).get("issues", [])
        evidence_gaps = pressure.get("evidence_audit", {}).get("gaps", [])
        red_lines = list(evidence.get("red_lines", []))
        for item in pressure.get("evidence_audit", {}).get("red_lines", []):
            if item not in red_lines:
                red_lines.append(item)

        d1 = (
            0.0 if source_count == 0
            else round(
                5.0 * min(
                    traceability, link_coverage, category_coverage, high_grade_ratio
                ),
                1,
            )
        )
        d2 = max(0.0, 5.0 - len(logic_issues))
        d3 = 4.5 if ("资料缺口" in final_report or "待检索" in final_report) else 4.0
        d4 = max(0.0, 5.0 - len(completeness))
        d5 = 5.0 if "建议" in final_report else 3.0
        d6 = 5.0 if ("风险" in final_report or "局限" in final_report) else 3.0
        d7 = 3.5
        scores = dict(zip(DIMENSIONS, (d1, d2, d3, d4, d5, d6, d7), strict=True))
        total = round(sum(scores.values()), 1)
        missing_categories = requirements_policy["missing_source_categories"]
        missing_report_links = requirements_policy["missing_report_links"]
        minimum_length = requirements_policy["minimum_length"]
        maximum_length = requirements_policy["maximum_length"]
        prose_length = requirements_policy["prose_length"]
        length_compliant = requirements_policy["length_compliant"]
        boundary_violations = requirements_policy["boundary_violations"]
        passed = (
            source_count > 0
            and not missing_categories
            and link_coverage == 1.0
            and not missing_report_links
            and not boundary_violations
            and length_compliant
            and requirements_policy["compliant"]
            and high_grade_ratio >= minimum_high_grade_ratio
            and not red_lines
            and total >= pass_score
        )
        problems = []
        if evidence_gaps:
            problems.append("存在证据缺口，需在决策使用时披露")
        if source_count == 0:
            problems.append("没有可追溯来源，不能发布决策报告")
        if missing_categories:
            problems.append("缺少来源类别：" + "、".join(missing_categories))
        if missing_report_links:
            problems.append("终稿缺少原始链接：" + "、".join(missing_report_links))
        if requirements_policy["missing_inline_source_links"]:
            problems.append(
                "来源链接仅集中在文末或未出现在对应章节："
                + "、".join(requirements_policy["missing_inline_source_links"])
            )
        if boundary_violations:
            problems.append("违反内容边界：" + "、".join(boundary_violations))
        if not length_compliant:
            problems.append(
                f"报告正文篇幅 {prose_length} 不在 {minimum_length}-{maximum_length} 范围"
            )
        if requirements_policy["material_mount_coverage"] < 1.0:
            problems.append("存在未映射到对应议题章节的素材")
        if requirements_policy["visual_asset_count"] < 1:
            problems.append("没有可视化成果")
        if requirements_policy["conflicted_claim_count"]:
            problems.append("存在未解决的冲突论断")
        if not requirements_policy["critical_claims_verified"]:
            problems.append("关键论断未达到双重独立来源验证")
        if not requirements_policy["capability_catalog_traversed"]:
            problems.append("Skill/集成能力目录未完整遍历")
        if not requirements_policy["skill_provenance_complete"]:
            problems.append("第三方 Skill 候选或改造草案缺少合规溯源字段")
        if not requirements_policy["citation_integrity"]:
            problems.append("引用锚点、内联引用或文末参考资料不完整")
        if not requirements_policy["content_structure_compliant"]:
            problems.append("流程图、表格说明、编号或全量链接索引不符合统一规范")
        if not requirements_policy["writing_standard_compliant"]:
            problems.append("写作规范参照或外部发布安全条件未满足")
        if high_grade_ratio < minimum_high_grade_ratio:
            problems.append(
                f"A+/A/B 级证据占比 {high_grade_ratio:.1%} 低于"
                f" {minimum_high_grade_ratio:.1%}"
            )
        if completeness:
            problems.append("存在未覆盖的大纲章节")
        if red_lines:
            problems.append("触发证据红线")
        if total < pass_score:
            problems.append(f"总分 {total} 低于门槛 {pass_score}")
        payload = {
            "passed": passed,
            "pass_score": pass_score,
            "total_score": total,
            "maximum_score": 35,
            "red_lines": red_lines,
            "dimensions": scores,
            "problems": problems,
            "required_actions": pressure.get("repair_actions", []),
            "requirements_checks": {
                "audience": requirements.get("audience"),
                "style": requirements.get("style"),
                "minimum_length": minimum_length,
                "maximum_length": maximum_length,
                "actual_length": len(final_report),
                "prose_length": prose_length,
                "length_compliant": length_compliant,
                "boundary_violations": boundary_violations,
                "missing_source_categories": missing_categories,
                "missing_report_links": missing_report_links,
                "missing_inline_source_links": requirements_policy[
                    "missing_inline_source_links"
                ],
                "inline_source_coverage": requirements_policy[
                    "inline_source_coverage"
                ],
                "material_mount_coverage": requirements_policy[
                    "material_mount_coverage"
                ],
                "visual_asset_count": requirements_policy["visual_asset_count"],
                "claim_issue_coverage": requirements_policy["claim_issue_coverage"],
                "high_grade_ratio": high_grade_ratio,
                "minimum_high_grade_ratio": minimum_high_grade_ratio,
                "critical_claims_verified": requirements_policy[
                    "critical_claims_verified"
                ],
                "conflicted_claim_count": requirements_policy[
                    "conflicted_claim_count"
                ],
                "capability_catalog_traversed": requirements_policy[
                    "capability_catalog_traversed"
                ],
                "skill_provenance_complete": requirements_policy[
                    "skill_provenance_complete"
                ],
                "citation_integrity": requirements_policy[
                    "citation_integrity"
                ],
                "content_structure_compliant": requirements_policy[
                    "content_structure_compliant"
                ],
                "writing_standard_profile": writing_standard["profile"]["id"],
                "writing_standard_compliant": requirements_policy[
                    "writing_standard_compliant"
                ],
                "reference_template_status": reference_status,
            },
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
                "pass_score": pass_score,
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

    def _requirements_policy(
        self,
        final_report: str,
        requirements: dict,
        evidence: dict,
        processed: dict,
        materials: dict,
        visualizations: dict,
        capability: dict,
        skill_research: dict,
        outline: dict,
        cited_draft: str,
    ) -> dict:
        categories = set(evidence.get("metrics", {}).get("source_categories", []))
        missing_categories = sorted(self.REQUIRED_SOURCE_CATEGORIES - categories)
        missing_report_links = [
            source["id"] for source in evidence.get("sources", [])
            if not source.get("original_url") or source["original_url"] not in final_report
        ]
        section_segments = self._section_segments(final_report, outline)
        inline_missing = []
        for source in evidence.get("sources", []):
            source_id = source.get("id")
            url = source.get("original_url")
            target_sections = [
                section_id
                for section_id, section in materials.get("sections", {}).items()
                if section.get("linked_issue")
                and any(
                    material.get("source_id") == source_id
                    for material in section.get("materials", [])
                )
            ]
            if (
                not url
                or not target_sections
                or not any(
                    url in section_segments.get(section_id, "")
                    for section_id in target_sections
                )
            ):
                inline_missing.append(str(source_id))
        source_total = len(evidence.get("sources", []))
        inline_source_coverage = (
            (source_total - len(inline_missing)) / source_total
            if source_total else 0.0
        )
        expected_length = int(requirements["deliverable"]["expected_length"])
        minimum_length = int(expected_length * 0.75)
        maximum_length = max(int(expected_length * 1.25), expected_length + 2_000)
        prose = re.sub(r"```.*?```", "", cited_draft, flags=re.DOTALL)
        prose = re.sub(r"<[^>]+>", "", prose)
        prose = re.split(
            r"(?m)^##\s+(?:统一)?参考资料\s*$", prose, maxsplit=1
        )[0]
        prose_length = len(prose)
        length_compliant = minimum_length <= prose_length <= maximum_length
        boundary_violations = []
        for boundary in requirements.get("content_boundaries", []):
            for prefix in ("不得包含:", "不得包含：", "禁止:", "禁止："):
                if boundary.startswith(prefix):
                    forbidden = boundary[len(prefix):].strip()
                    if forbidden and forbidden in final_report:
                        boundary_violations.append(forbidden)
        source_issue_ids = {
            source["id"]: set(source.get("issue_ids", []))
            for source in evidence.get("sources", [])
        }
        correctly_mounted: set[str] = set()
        for section in materials.get("sections", {}).values():
            linked_issue = section.get("linked_issue")
            if not linked_issue:
                continue
            for material in section.get("materials", []):
                source_id = material.get("source_id")
                if linked_issue in source_issue_ids.get(source_id, set()):
                    correctly_mounted.add(source_id)
        material_mount_coverage = (
            len(correctly_mounted) / len(source_issue_ids) if source_issue_ids else 0.0
        )
        visual_asset_count = len(visualizations.get("assets", []))
        claims = processed.get("claims", [])
        claim_issue_coverage = (
            sum(bool(claim.get("issue_ids")) for claim in claims) / len(claims)
            if claims else 0.0
        )
        triangulation = processed.get("triangulation", {})
        critical_claims_verified = triangulation.get(
            "critical_claim_count", 0
        ) == triangulation.get("critical_verified_count", 0)
        conflicted_claim_count = triangulation.get("conflicted_claim_count", 0)
        capability_metrics = capability.get("metrics", {})
        capability_catalog_traversed = capability_metrics.get(
            "external_catalog_count"
        ) == capability_metrics.get("external_traversed_count")
        provenance_fields = {
            "name", "source_url", "author", "license", "version", "channel"
        }
        skill_provenance_complete = all(
            provenance_fields <= candidate.keys()
            for candidate in skill_research.get("candidates", [])
        ) and all(
            provenance_fields <= adapted.get("attribution", {}).keys()
            and bool(adapted.get("modifications"))
            for adapted in skill_research.get("adapted_skill_specs", [])
        )
        citation_integrity = bool(
            re.search(r"(?m)^##\s+(统一)?参考资料", cited_draft)
        )
        for source in evidence.get("sources", []):
            safe_id = re.sub(
                r"[^A-Za-z0-9_-]", "-", str(source.get("id"))
            )
            url = str(source.get("original_url") or "")
            if (
                not url
                or cited_draft.count(url) < 2
                or f'id="ref-{safe_id}"' not in cited_draft
                or f'id="cite-{safe_id}-1"' not in cited_draft
            ):
                citation_integrity = False
                break
        minimum_visual_assets = int(
            requirements.get("minimum_visual_assets", 6)
        )
        table_count = sum(
            kind == "table"
            for kind, _ in MarkdownTableParser.split_document(cited_draft)
        )
        table_explanation_count = cited_draft.count("> **表格说明：**")
        has_external_links = bool(
            re.search(r"\[[^\]]+\]\(https?://[^)]+\)", cited_draft)
        )
        repeated_numbering = bool(
            re.search(r"(?m)^1\.\s.+\n1\.\s", cited_draft)
        )
        plain_flow = bool(
            re.search(
                r"```(?:text|txt)\s*\n(?:(?!```).)*(?:→|⇄|<->|->|↓)"
                r"(?:(?!```).)*```",
                cited_draft,
                re.DOTALL,
            )
        )
        content_structure_compliant = (
            table_explanation_count >= table_count
            and not repeated_numbering
            and not plain_flow
            and (not has_external_links or "## 全量关联链接" in cited_draft)
        )
        return {
            "missing_source_categories": missing_categories,
            "missing_report_links": missing_report_links,
            "missing_inline_source_links": inline_missing,
            "inline_source_coverage": inline_source_coverage,
            "minimum_length": minimum_length,
            "maximum_length": maximum_length,
            "prose_length": prose_length,
            "length_compliant": length_compliant,
            "boundary_violations": boundary_violations,
            "material_mount_coverage": material_mount_coverage,
            "visual_asset_count": visual_asset_count,
            "minimum_visual_assets": minimum_visual_assets,
            "claim_issue_coverage": claim_issue_coverage,
            "critical_claims_verified": critical_claims_verified,
            "conflicted_claim_count": conflicted_claim_count,
            "capability_catalog_traversed": capability_catalog_traversed,
            "skill_provenance_complete": skill_provenance_complete,
            "citation_integrity": citation_integrity,
            "content_structure_compliant": content_structure_compliant,
            "compliant": (
                not missing_categories
                and not missing_report_links
                and not inline_missing
                and length_compliant
                and not boundary_violations
                and material_mount_coverage == 1.0
                and visual_asset_count >= minimum_visual_assets
                and claim_issue_coverage == 1.0
                and critical_claims_verified
                and conflicted_claim_count == 0
                and capability_catalog_traversed
                and skill_provenance_complete
                and citation_integrity
                and content_structure_compliant
            ),
        }

    @staticmethod
    def _section_segments(final_report: str, outline: dict) -> dict[str, str]:
        located = []
        for section in outline.get("sections", []):
            title = str(section.get("title", ""))
            position = -1
            escaped = re.escape(title)
            patterns = (
                rf"(?m)^#{{1,6}}\s+[^\n]*{escaped}",
                rf"<h[1-6]>[^<]*{escaped}",
                rf"\\n#{{1,6}}\s+[^\"\\]*{escaped}",
                rf"(?m)^[^#\[\]\n]*{escaped}[^\n]*$",
            )
            for pattern in patterns:
                match = re.search(pattern, final_report)
                if match:
                    position = match.start()
                    break
            if title and position >= 0:
                located.append((position, section["id"]))
        located.sort()
        segments = {}
        for index, (position, section_id) in enumerate(located):
            end = (
                located[index + 1][0]
                if index + 1 < len(located)
                else len(final_report)
            )
            segments[section_id] = final_report[position:end]
        return segments
