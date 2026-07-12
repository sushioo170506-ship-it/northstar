---
name: citation_management
description: 将正文来源统一转换为章节内联引用、文末参考资料和双向跳转锚点。
license: MIT
version: 1.0.0
---

# Citation Management

## 职责

只管理引用，不修改事实、观点、来源等级或正文结构。

## 输入输出

- INPUT：writing、evidence_governance、material_integration。
- OUTPUT：`cited_draft`。
- 支持格式：GB/T 7714风格（默认）、APA、MLA、Chicago、numeric。

## 必须规则

1. 正文来源保留原始URL，并追加 `[[n]](#ref-id)` 文末跳转。
2. 每个正文引用建立 `cite-id-n` 锚点。
3. 文末每条参考资料建立 `ref-id` 锚点和返回正文的 `↩`。
4. 自动生成完整参考资料列表；已有参考资料时生成“统一参考资料”。
5. 输出引用数、参考资料数、遗漏来源、覆盖率和格式。

## 错误处理

- 来源无URL：记录missing，不伪造。
- 来源未在正文出现：覆盖率下降，quality_gate阻断。
- 重复引用保留多个正文锚点，文末合并为一条来源。
- 文献格式无法完整生成时保留原始元数据并标记，不补写作者或年份。
