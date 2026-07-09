# mr-step3-collect

name: mr-step3-collect  
description: Step 3 — 根据大纲素材需求采集原始信息，不加工、不筛选、先收集。

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

## 注意事项
- 每条素材必须标注来源 URL 与时间戳。
- 官方与第三方数据分开存放（文件名带 `_official` / `_thirdparty`）。
- 采集不全不阻塞：在后续加工阶段标注“待补采”。

## 质量卡口
- 官方技术报告/论文已采集。
- 基础参数 >= 10 字段。
- Benchmark >= 5。
- 竞品 >= 2。
- 每条素材有来源 URL。
- 官方与第三方数据已区分。

## 交接
将 `archive/raw_data/` 交给 `mr-step4-process`。

