---
name: mr-step3-collect
description: Step 3 -- 根据大纲的素材需求，从多个渠道采集原始信息，不加工、不评判、先收进来。输入章节大纲和模型名称，输出 raw_data/ 原始素材文件夹。
---

# Step 3: 采素材

本阶段只采集，不加工、不筛选、不评判。"这数据可信吗"是 Step 4 之后的加工和复核要处理的事。你的目标是按大纲逐项把原始信息收进来，并保留来源。

## 输入

- `outline.md`（Step 2 产出，含素材需求标注）
- 模型名称

## 输出目录

生成 `raw_data/`：

```text
raw_data/
├── paper/                  # 论文原文或技术报告
│   ├── 001_technical_report.pdf
│   └── 002_arxiv_survey.pdf
├── official/               # 官方信息
│   ├── model_card.md
│   ├── blog_post.md
│   └── config.json
├── benchmarks/             # 评测数据
│   ├── official_benchmark.md
│   ├── open_llm_leaderboard.csv
│   └── community_test.txt
├── competitors/            # 竞品数据
│   └── competitor_matrix.csv
├── ecosystem/              # 生态信息
│   ├── license.txt
│   ├── github_stats.md
│   └── community_discussions.md
└── references.md           # 所有来源的引用清单
```

## 信息渠道优先级

| 优先级 | 渠道 | 采集内容 |
|---|---|---|
| 1（最高） | 官方技术报告 / arXiv 论文 | 架构、训练方法、官方 benchmark |
| 2 | 模型卡 / HuggingFace / GitHub | 基础参数、License、checkpoint 可用性 |
| 3 | 官方 API 文档 / 部署文档 | 推理参数、硬件需求、定价 |
| 4 | 第三方评测（Open LLM Leaderboard / LMSYS） | 独立 benchmark 分数 |
| 5 | 社区实测（Reddit / 知乎 / Twitter/X） | 真实使用体验、问题反馈 |
| 6 | 新闻 / 行业分析 | 发布背景、市场反应 |

## 采集粒度控制

| 素材类型 | 最低采集量 | 说明 |
|---|---:|---|
| 论文/技术报告 | >= 1 篇 | 官方技术报告必采；如果没有，标注缺失 |
| 基础参数 | >= 10 个字段 | 参数量、层数、head 数、上下文长度等 |
| Benchmark 数据 | >= 5 个主流 benchmark | MMLU / HumanEval / GSM8K / MATH / BBH 等 |
| 竞品数据 | >= 2 个直接竞品 | 同参数级/同时期的对标模型 |
| 社区评价 | >= 3 条独立来源 | 多样性验证 |
| 部署信息 | >= 3 个指标 | 显存 / 延迟 / 吞吐量 / 价格 |

## 操作规则

1. 按 `outline.md` 的章节素材需求逐项采集。
2. 每条素材必须标注来源 URL、访问时间戳、来源类型（official/thirdparty/community/news）。
3. 官方数据与第三方数据分开存放；文件名标注 `_official` 或 `_thirdparty`。
4. 采集不全不卡流程，但必须在 `references.md` 或单独备注中标注"待补采"。
5. 不要在本阶段下判断，不要写"因此说明..."；只保存原始事实、原文摘录、表格、链接。

## `references.md` 格式

```markdown
# References

| ID | 来源类型 | 标题 | URL | 访问时间 | 对应章节 | 备注 |
|---|---|---|---|---|---|---|
| R001 | official | ... | ... | YYYY-MM-DD | §1/§3 | 官方 benchmark |
```

## 质量卡口

- [ ] 官方技术报告/论文已采集，或明确标注不存在/未找到。
- [ ] 基础参数 >= 10 个字段，或缺失字段已列出。
- [ ] Benchmark 数据 >= 5 个，或解释为什么不足。
- [ ] 竞品数据 >= 2 个直接竞品，或说明直接竞品缺失。
- [ ] 每条素材标注了来源 URL 和访问时间。
- [ ] 官方与第三方数据已区分存放。

未通过时，继续 Step 3 补采；若大纲素材需求本身不合理，回退 Step 2。
