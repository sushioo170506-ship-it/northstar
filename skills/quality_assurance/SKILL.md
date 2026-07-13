---
name: quality_assurance
description: 合并量化校验、独立审核与发布质量门，作为唯一发布阻断节点。
license: MIT
version: 1.0.0
---

# Quality Assurance

输入需求、证据、成文包、排版稿与写作标准，输出 JSON：

- `review`：审核后候选正文
- `quality_gate`：发布决策与硬门结果
- `quant_finance_research`：量化场景校验（非量化则为 not_applicable）

## 内部步骤

1. quant_finance_research（条件逻辑）
2. review
3. quality_gate

## 硬规则

1. `quality_gate.passed=false` 时编排器阻断发布。
2. 量化报告缺回测披露时硬门失败。
3. 来源快照、论断验证、红线仍为硬门，D1-D7 仅诊断。
