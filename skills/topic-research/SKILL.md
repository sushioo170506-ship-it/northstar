---
name: topic-research
description: 拆解研究主题，将用户资料标准化为可追溯证据包并标记资料缺口。
license: MIT
version: 1.0.0
---

# Topic Research

独立实现：`research_workflow.skills.research.ResearchSkill`。

在最终大纲确认后执行。输入 requirements_analysis、issue_tree、outline，以及
`config.extra.sources`；输出 `SkillResult(artifact_type="evidence_pack")`，内容包含
research_questions、sources、outline_sections、retrieval_summary 和 evidence_gaps。

未配置检索器时只整理已提供来源且绝不伪造检索结果。注入 `SourceRetriever` 后按 official、
academic、social_media 三类检索；缺少任一类时保持 evidence gap，最终质量门阻断发布。

```python
result = ResearchSkill(generator=None).execute(request)
```

校验：主题非空；每个来源应具有稳定 ID；无来源时必须输出明确资料缺口。
