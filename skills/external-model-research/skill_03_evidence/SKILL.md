# mr-step3-collect

name: mr-step3-collect
description: Step 3 — 按大纲采集可追溯原始信息，覆盖官方、第三方、评测、竞品、政策与成本维度。

## 作用
按章节需求批量采素材，本阶段只采集，不评判“可信度结论”。

## 输入
- `archive/outline.md`
- 模型名称

## 输出
写入 `archive/raw_data/`，推荐目录：

```text
raw_data/
├── paper/
├── official/
├── benchmarks/
├── competitors/
├── ecosystem/
├── policy/
├── pricing/
└── references.md
```

## 渠道优先级
1. 官方技术报告 / arXiv 论文  
2. 模型卡 / HuggingFace / GitHub  
3. 官方 API 与部署文档  
4. 第三方评测（Open LLM Leaderboard / LMSYS）  
5. 社区实测（Reddit / 知乎 / X）  
6. 新闻与行业分析

## 最低采集粒度
- 论文/技术报告：>= 1 篇（官方技术报告必采）
- 基础参数：>= 10 个字段
- Benchmark：>= 5 个主流基准
- 竞品数据：>= 2 个直接竞品
- 社区评价：>= 3 条独立来源
- 部署信息：>= 3 个指标（显存/延迟/吞吐/价格）

## 长篇详实采集硬门槛
- 官方来源：>= 8（发布页、模型文档、系统卡、帮助中心、官方公告等）
- 第三方来源：>= 10（评测平台/媒体/社区/独立机构）
- 研究论文/技术文档：>= 12
- benchmark 指标：>= 25（覆盖 >=8 个能力维度）
- 直接竞品：>= 5
- 部署与成本字段：>= 10（上下文、输出、延迟、吞吐、价格、可用性、限制策略等）
- 政策与合规事件：>= 3（含时间线）
- 每条记录必须带：`来源URL + 抓取日期 + 口径说明 + 原文片段`

## 结构化索引（新增）
- 必须输出 `raw_data/source_index.csv`：
  - 字段：`source_id,type,channel,url,captured_at,official_or_thirdparty,section_mapping`
- 必须输出 `raw_data/data_inventory.md`：
  - 按章节统计素材数量与缺失项。
- 必须输出 `raw_data/benchmark_catalog.csv`：
  - 字段：`metric_id,dimension,benchmark_name,value,model,unit,source_id`
- 必须输出 `raw_data/competitor_catalog.csv`：
  - 字段：`model_name,release_window,strengths,weaknesses,pricing,source_id`

## 注意事项
- 每条素材必须标注来源 URL 与时间戳。
- 官方与第三方数据分开存放（文件名带 `_official` / `_thirdparty`）。
- 数字必须保留单位和统计口径（例如 pass@1 / F1 / Cap%）。
- 采集不全不阻塞：在后续加工阶段标注“待补采”。

## 质量卡口
- 官方技术报告/论文已采集。
- 基础参数 >= 10 字段。
- Benchmark >= 5。
- 竞品 >= 2。
- 每条素材有来源 URL。
- 官方与第三方数据已区分。
- `source_index.csv` 已生成且无空 URL。
- `benchmark_catalog.csv` 与 `competitor_catalog.csv` 已生成。
- 若报告深度为长篇，未达到硬门槛（来源/竞品/benchmark/文献）则判定不通过并补采。

## 交接
将 `archive/raw_data/` 交给 `mr-step4-process`。

