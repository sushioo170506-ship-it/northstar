---
name: compose
description: 将素材整合、可视化、写作、引用优化与压力测试合并为成文节点。
license: MIT
version: 1.0.0
---

# Compose

输入需求、议题树、大纲、调研、证据流水线、数据处理与写作标准，输出 JSON 包：

- `draft`：定稿 Markdown
- `material_integration` / `visualization` / `pressure_test`：下游质控与发布所需结构

## 内部步骤

1. material_integration
2. visualization
3. writing
4. writing_finalize
5. pressure_test

## 硬规则

1. 不编造无来源支撑的事实。
2. 定稿必须保留可点击原始 URL、表格说明与连续编号。
3. 压力测试结果写入产物，供初稿确认与质量保障读取。
