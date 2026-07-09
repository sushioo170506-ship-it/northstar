# mr-step3-collect

name: mr-step3-collect
description: Step 3 — 按大纲采集可追溯证据，建立来源分层与结构化索引。

## 定位与作用
本步骤是“证据输入层”，只负责采集与标注，不在此阶段下结论。  
目标是让后续每个结论都能回链到具体来源与口径。

## 输入
- `archive/outline.md`
- 模型名称

## 输出
写入 `archive/raw_data/`，至少包含：
- `official/`、`benchmarks/`、`competitors/`、`paper/`、`ecosystem/`、`policy/`、`pricing/`
- `references.md`
- `source_index.csv`
- `benchmark_catalog.csv`
- `competitor_catalog.csv`
- `data_inventory.md`
- `collection_findings.md`（采集阶段结论：已证实/待证实/冲突项）
- `claim_evidence_pool.csv`（按 `conclusion_id` 聚合候选证据）

## 采集原则
- 官方优先、第三方补强、文献兜底；
- 任何数字都要带单位与统计口径；
- 任何结论都要有原始片段可回查；
- 对冲突来源必须保留原始差异，不在本步骤“强行统一口径”。

## 长篇硬门槛
- 官方来源 >= 8，第三方来源 >= 10；
- 研究文献 >= 12；
- benchmark 指标 >= 25（覆盖维度 >= 8）；
- 直接竞品 >= 5；
- 部署与成本字段 >= 10；
- 政策/合规事件 >= 3。

## 差异化说明
本步骤与 Step4 的区别：  
Step3 只保证“采得到、标得清”；Step4 才负责“加工成可写作证据块”。

## 逻辑链条要求
Step3 不输出最终业务结论，但必须输出“采集阶段结论”：
1. 结论侧：每个 `conclusion_id` 至少形成“候选证据簇”（不少于 2 条来源）；
2. 过程侧：每个采集模块要产出“当前成果与价值”一句话总结，写入 `collection_findings.md`；
3. 冲突侧：对口径冲突项明确标注“冲突点/可能原因/待验证动作”。

`claim_evidence_pool.csv` 建议字段：  
`conclusion_id, source_id, source_type, metric, value, unit, as_of, quote, confidence`

## 质量卡口
- 来源 URL、抓取时间、口径说明齐全；
- 官方/第三方分层清晰；
- 索引文件完整且字段不缺失；
- 长篇未达硬门槛时，必须补采后再进入下一步；
- 每个核心 `conclusion_id` 都有候选证据簇，且不存在“无证据结论占位”；
- 每个主要采集过程都有“成果与价值”总结，禁止只记录操作过程。

## 交接
将 `archive/raw_data/` 交给 `mr-step4-process`。

