---
name: evidence_pipeline
description: 将来源快照与证据治理合并为一条证据流水线，冻结哈希并生成可追溯证据账本。
license: MIT
version: 1.0.0
---

# Evidence Pipeline

输入 `research`、`writing_standards`、`issue_tree`、`outline`，输出合并产物：

- `source_snapshot`：带 SHA-256、抓取时间与场景来源策略的不可变快照
- `evidence_governance`：可追溯性、独立性、红线与议题覆盖账本

## 内部步骤

1. `source_snapshot`（内部模块，不再作为独立 DAG 节点）
2. `evidence_governance`（内部模块，不再作为独立 DAG 节点）

论断级原文/数字核验已并入下游 `data_processing`。

## 硬规则

1. 每项来源必须保存标题、原始 URL、正文、Provider 与 SHA-256。
2. 空正文或缺 URL 不得视为完整证据。
3. 来源要求按场景区分，不得套用统一三支柱。
4. 下游必须引用快照哈希，不得直接信任可漂移网页。
