---
name: content_optimization
description: 将业务链路标准化为流程图，为表格补充解释，修复编号并生成全量链接索引。
license: MIT
version: 1.0.0
---

# Content Optimization

输入`citation_management`，输出`optimized_draft`。本Skill只重组已有内容，不增加事实。

## 强制规则

1. 含明确业务流程、逻辑链路或路径走向的纯文本代码块必须转换为Mermaid
   `flowchart TD/LR`；节点名称来自原文，边方向与双向关系不得改变。
2. 每张Markdown统计/说明表后必须追加“表格说明”，覆盖字段/指标定义、数据逻辑和
   结论推导口径；不得创造表外结论。
3. 同层有序列表必须从1开始连续递增；子层按缩进独立计数；代码块不改写。
4. 文末生成“全量关联链接”，去重收录正文全部外部URL并保持可点击。
5. 后续`pressure_test`、`formatting`、`review`和`quality_gate`必须消费优化后产物。

## 失败处理

流程无法可靠识别时保留原文并报告，不得生成错误连线；表格字段不完整时仍给出基于表头的
保守说明；任何转换都不得删除原始链接、引用锚点、数值或表格单元格。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
