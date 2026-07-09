# 模型调研报告工作流（ModelResearch）

一套**专为「大模型调研/评估报告」**设计的 Cursor 工作流，沿用 Wcget 的搭建思路
（编排器 + 相互独立、串联、各带质量卡口、靠文件传产物的子 Skill），
但语域从"公众号观点文"换成**中立、可复现、可追责且对得起特定读者**的评估文档。

> - 研究"一个市场/趋势/观点" → 用 `research-workflow/`（Wcget）
> - 评估"一个具体模型：能干什么、干不了什么、要不要用、替代谁" → 用本工作流

## 一份优质模型报告 = 8 维骨架（不遗漏）+ 3 问主体匹配（有人看、看完有用）

- **骨架（8 维）**：定位背景 / 架构创新 / 训练细节 / 评测表现 / 推理部署 / 优势短板 / 应用场景 / 版本迭代
- **灵魂（3 问）**：Q1 谁在看（→ 8 维权重）· Q2 下一步做什么（→ 结论形式）· Q3 最怕什么（→ 风险权重）

## Skill 组成：5 个专属 + 3 个复用 Wcget

> skill 是封装好的工具；8 维 / 3 问 / 7 步流程是装进工具里的方法论，不是一步一个 skill。

| Step | Skill | 处置 | 职责 | 产出 |
|------|-------|------|------|------|
| 1 | `modelresearch-outline` | 专属 | 读者三问 → 8 维加权大纲 + 结论形式 + 风险权重 | `outline.md` |
| 2 | `modelresearch-data` | 专属 | 信息收集 + 技术解构 + 评测对照（来源分级/口径/contamination） | `data.md` |
| 3 | `modelresearch-testing` | 专属 | 场景化验证：实测/红队/部署（按报告类型分支） | `testing.md` |
| 4 | `wcget-process` | 复用 | 需量化排序时：数据锚点评分 | 追加 `data.md` |
| 5 | `modelresearch-write` | 专属 | 对比分析 + 主体适配撰写（金字塔/结论形式/风险登记/复现附录） | `report.md` |
| 6 | `wcget-figure` + `wcget-build` | 复用 | 客观图表 + 多格式（HTML/PNG/Word[公文/通用]/飞书） | `report.*` |

**复核**不单设 skill → 编排器"交付前终检"（含来源时间/官方vs三方/利益冲突/读者能否决策）+ write 自检。

## 流水线

```
outline → data → testing → [process 可选] → write → figure+build → 复核终检
```

## 与 Wcget 的关键区别

| | Wcget | ModelResearch |
|--|-------|---------------|
| 立场 | 判断驱动、单一刺点 | 中立、结论从证据浮现 |
| 证据 | 数据点缀观点 | 口径可复现 + 证据分级（自测/三方/自报/二手） |
| 独有 | 头门/埋钩/金句 | ModelCard/能力矩阵/一手实测/TCO/复现附录 |
| 结论 | 传播金句 | 服从读者下一步（Yes/No / 复现成本 / 绿黄红 / 部署可行性） |

## 目录

```
.cursor/rules/
  modelresearch.mdc            # 主编排器
  modelresearch-outline.mdc    # Step 1
  modelresearch-data.mdc       # Step 2
  modelresearch-testing.mdc    # Step 3
  modelresearch-write.mdc      # Step 5
  （Step 4/6 复用 wcget-process / wcget-figure / wcget-build）
model-research/
  templates/                   # outline / data / testing / report
  output/                      # 跑报告时的产物
  README.md
```

## 怎么用

```
按 ModelResearch 主 Skill 编排，评估模型：「<模型名>」。
读者：<研究员/PM/开发者/投资人/监管>；决策问题：<要不要用/替代谁/用在哪/能否传播>。
从 Step 1 起逐步执行，每步过质量卡口后再进下一步。
```

## 落地进度

- [x] 主编排器 `modelresearch`（新链条 + 复用 + 复核终检）
- [x] `modelresearch-outline`（3 问 → 8 维加权大纲）
- [x] `modelresearch-data`（信息收集 + 技术解构 + 评测对照）
- [x] `modelresearch-testing`（实测 / 红队 / 部署，按读者分支）
- [x] `modelresearch-write`（对比分析 + 主体适配 + 结论形式 + 复现附录）
- [x] 复用 `wcget-process / wcget-figure / wcget-build`
- [ ] 端到端试跑（待确认读者 + 决策问题 + 是否需一手实测）
