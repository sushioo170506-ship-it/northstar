---
name: topic-research
description: 大纲确认后按产业×学术×实景三 pass 采集、去重并登记可追溯来源。
license: MIT
version: 1.0.0
---

# Topic Research

独立实现：`research_workflow.skills.research.ResearchSkill`。

在最终大纲确认后执行。输入 requirements_analysis、issue_tree、outline，以及
`config.extra.sources`；输出 `SkillResult(artifact_type="evidence_pack")`，内容包含
research_questions、sources、outline_sections、retrieval_summary 和 evidence_gaps。

未配置检索器时只整理已提供来源且绝不伪造检索结果。注入 `SourceRetriever` 后按 industry、
academic、social_media 三类分别调用；official/primary 兼容归入 industry。

```python
result = ResearchSkill(generator=None).execute(request)
```

校验：主题非空；每个来源应具有稳定 ID；无来源时必须输出明确资料缺口。

## 三支柱七线

| 支柱 | 必跑检索线 | 回答 |
|---|---|---|
| 产业 industry | 市场/格局、技术参数、政策标准、财务/融资 | 多大、多快、谁领先 |
| 学术 academic | 综述、基准/SOTA、争议对比、局限 | 为什么、机制、天花板 |
| 实景 social_media | 独立实测、投诉/故障、用户/开发者反馈 | 实际好不好、差在哪里 |

SourceRetriever 必须按单一 category 调用三次；每次记录 completed/missing/error、数量和错误。
任何一 pass 失败都继续保存其他来源，但质量门不得发布。

## 提取字段

每个来源至少包含 id、title、category、url、published_at、content、issue_ids。数字还应保存
单位、样本、统计口径；论文尽量保存 DOI、venue、研究类型、关键数值和作者自述局限。

## 来源优先级

1. 官方统计、监管、财报、产品文档；
2. 同行评议论文和可复现实验；
3. 独立行业研究和实验室评测；
4. 有样本说明的用户/开发者实测；
5. 厂商自评、媒体和匿名社区仅作辅助，必须标注立场。

## MUST / MUST NOT / ON_FAIL

- MUST：每个议题有检索记录；中英文关键词各至少一组；相同 URL 去重；缺口显式。
- MUST NOT：只读搜索摘要；把厂商自评当独立验证；绕过平台条款抓取私密社媒；伪造论文。
- ON_FAIL：网络错误记录 pass error；无链接来源降级；缺支柱退回 research/update_sources。
