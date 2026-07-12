---
name: quality_gate
description: 按 D1-D7 评分并根据证据红线作出允许或阻断发布的最终决定。
license: MIT
version: 1.0.0
---

# Quality Gate

实现：`research_workflow.skills.quality_gate.QualityGateSkill`。

输入 capability_sweep、skill_research、requirements_analysis、review、evidence_governance、data_processing、
material_integration、visualization、pressure_test，输出
`artifact_type="quality_gate"`，包含：

- D1 事实准确性
- D2 逻辑严密性
- D3 事实与观点分离
- D4 结构完整性
- D5 So What
- D6 时效性与边界感
- D7 量级感
- 红线、问题、必需修复项和发布决定

默认通过线为 24/35。缺少 industry、academic、social_media 任一来源类别、原始 URL 覆盖
不足 100%、终稿未包含全部来源链接、违反内容边界、篇幅不足、任一红线或总分不足，都会
持久化评估产物并阻断发布。质量门还会从证据 issue_ids 和章节 linked_issue 重新计算素材
挂载覆盖率，并默认要求至少 6 项结构完整的可视化资产，不能只信任上游自报指标。

## 唯一硬阻断规则

- 能力目录未完整遍历；
- 第三方候选或改造草案缺少来源、作者、版本、许可证、渠道或修改记录；
- 三支柱缺失、链接覆盖<100%、A+/A/B 证据占比<80%；
- 关键 claim 未获两个独立来源、claim 冲突未解决或未映射议题；
- 来源只出现在文末、未内联到对应章节，inline_source_coverage<100%；
- 素材严格挂载率<100%、可视化少于 6 项；
- 篇幅/内容边界不合规、证据红线、D1–D7 总分<24。

## D1–D7

D1 事实准确性；D2 逻辑严密；D3 事实/观点分离；D4 结构完整；D5 So What；D6 时效与边界；
D7 量级感。每维 0–5，总分 35。分数是解释层，硬红线优先：高分不能抵消红线。

门槛由workflow_profile提供，用户可通过明确extra字段覆盖，但覆盖值必须写入质量产物：
quick 22/60%/3图，standard 24/75%/4图，deep 24/80%/6图，regulatory 30/90%/6图。

## 错误处理

拒绝时仍保存完整 gate artifact、problems、required_actions 和最早修复节点，工作流置 failed；
publish 不得执行。模型生成的 allow_release 必须被确定性规则重新计算覆盖。
