---
name: writing_finalize
description: 将引用管理与内容结构优化合并为成文定稿节点，输出可排版的最终草稿。
license: MIT
version: 1.0.0
---

# Writing Finalize

输入 `writing`、`evidence_pipeline`（或 `evidence_governance`）、`material_integration`、
`writing_standards`，输出定稿 Markdown。

## 内部步骤

1. `citation_management`：内联引用、文末参考资料、双向锚点
2. `content_optimization`：流程图 Mermaid 化、表格说明、编号归一、全量链接索引

## 硬规则

1. 不修改事实、观点、来源等级。
2. 正文来源保留原始 URL，并追加文末跳转。
3. 业务流程图必须转为结构化 flowchart；统计表必须附说明。
4. 列表编号在同一二级标题内连续，不得重复从 1 重启错误。
