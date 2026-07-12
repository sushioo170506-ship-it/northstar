---
name: topic-research
description: 拆解研究主题，将用户资料标准化为可追溯证据包并标记资料缺口。
license: MIT
version: 1.0.0
---

# Topic Research

独立实现：`research_workflow.skills.research.ResearchSkill`。

输入为 `SkillRequest`：读取 `config.topic`、`config.extra.sources`、`feedback`；不依赖其他
节点。输出 `SkillResult(artifact_type="evidence_pack")`，内容为包含 `topic`、
`research_questions`、`sources`、`evidence_gaps` 的 JSON。

未配置模型时使用确定性本地实现，只整理已提供来源且绝不伪造检索结果。注入
`TextGenerator` 后可对接检索增强模型，外部适配器仍须返回相同契约。独立调用：

```python
result = ResearchSkill(generator=None).execute(request)
```

校验：主题非空；每个来源应具有稳定 ID；无来源时必须输出明确资料缺口。
