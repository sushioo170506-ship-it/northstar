---
name: outline
description: 调研前以“定刺→拆骨→填肉→设门→埋钩”设计可争论、可证伪的大纲。
license: MIT
version: 1.0.0
---

# Outline Design

独立实现：`research_workflow.skills.outline.OutlineSkill`。

输入 `requirements_analysis`、已确认 `issue_tree` 及统一 `ReportConfig`，在调研前先确定
最终写作框架。输出 `artifact_type="outline"` 的 JSON，章节包含稳定 ID、标题、目标篇幅、
目的、对应议题和证据需求，并记录受众、文风、产出类型、内容边界对齐信息。

```python
result = OutlineSkill(generator=None).execute(request)
```

主编排器必须在本节点后触发 `outline_confirmation`。修改大纲会失效大纲及所有后代，
但保留需求简报和已确认议题树。

## WHEN / INPUT / OUTPUT

- WHEN：issue_tree_confirmation=completed。
- INPUT：requirements_brief、issue_tree、ReportConfig。
- OUTPUT：`outline`；不得输出正文。

## 五步构建法

1. **定刺**：继承 provisional_thesis，写明一句话判断、反对意见、证伪条件和行动价值。
2. **拆骨**：每章必须是判断而非话题；章节逻辑应形成“因为→所以→因此”。
3. **填肉**：每章至少配置数据锚、案例锚或对比锚；锚点必须声明数值、时间、来源、口径需求。
4. **设门**：开头 15–25 字制造数据冲突；每节首段 ≤100 字；结尾回扣判断与边界。
5. **埋钩**：前 30% 放最强判断，中 40% 放评分/假说检验，后 30% 放行动含义和闭环。

## 质量卡口

- 核心判断可争论、可证伪、可行动。
- 每章含 chapter_claim、reader_challenge、anchor_requirements、target_length。
- 至少 3 个竞争性假说及检验方法。
- narrative_gates 与节奏预算齐全。
- 仅描述“背景/现状/趋势”的章节不得通过。

## MUST NOT / ON_FAIL

- 不得在大纲阶段编造数据或假装锚点已找到。
- 不得提前执行 research、评分或写作。
- 找不到锚点时保留数据需求，不删除问题。
- 结构不闭合退回 outline；研究主题有误退回 issue_tree。
