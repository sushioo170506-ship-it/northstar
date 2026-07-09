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

## 采集原则
- 官方优先、第三方补强、文献兜底；
- 任何数字都要带单位与统计口径；
- 任何结论都要有原始片段可回查。

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

## 质量卡口
- 来源 URL、抓取时间、口径说明齐全；
- 官方/第三方分层清晰；
- 索引文件完整且字段不缺失；
- 长篇未达硬门槛时，必须补采后再进入下一步。

## 交接
将 `archive/raw_data/` 交给 `mr-step4-process`。

