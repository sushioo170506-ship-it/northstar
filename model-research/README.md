# 模型调研报告工作流（ModelResearch）

一套**专为「大模型调研/评估报告」**设计的 Cursor 工作流，沿用 Wcget 的搭建思路——
**编排器 + 相互独立、串联、各带质量卡口、靠文件传产物的子 Skill**——
但语域从"公众号观点文"换成**中立、可复现、可追责的技术评估文档**。

> 与 `research-workflow/`（Wcget，判断驱动的传播型深度长文）互补：
> - 研究"一个市场/趋势" → 用 Wcget
> - 研究"一个具体模型制品：能干什么、干不了什么、要不要用、替代谁" → 用 ModelResearch

## 与 Wcget 的关键区别

| 维度 | Wcget（公众号研究文） | ModelResearch（模型调研报告） |
|------|----------------------|------------------------------|
| 目标 | 可争论的判断 + 传播 | 可复核的选型决策支持 |
| 立场 | 判断驱动、单一刺点 | 中立评估，结论从证据浮现 |
| 结构 | 全景→评比→推演→决策（叙事） | 目的→档案→能力→实测→对标→结论（评估） |
| 证据 | 数据点缀观点 | **评测口径可复现**：版本/harness/effort/pass@k/日期/自报vs第三方vs自测 |
| 独有 | 头门/埋钩/金句 | Model Card、能力矩阵、一手实测、TCO、复现附录 |
| 禁忌 | 套话 | 套话 **+ 立场先行 + 传播节奏 + 未标口径的跑分** |

## 流水线（七步）

```
Step 1 scope    → 调研目的·读者·决策问题·版本快照·评估维度      output/scope.md
Step 2 profile  → Model Card 事实基线（规格/家族/定价/可得性/API）  output/model_card.md
Step 3 eval     → 能力评估框架 + 基准口径 + 证据分级             output/eval_data.md
Step 4 handson  → 一手实测（私有 eval / 延迟 / 成本 / 失败模式）   output/handson.md
Step 5 assess   → 纵横对标 + 安全合规可得性 + TCO + 适配矩阵      output/assessment.md
Step 6 write    → 中立评估正文 + 风险登记 + 复现附录             output/report.md
Step 7 build    → 图表 + 多格式（HTML/PNG/Word[公文/通用]/飞书）   output/report.*
```

主编排器 `modelresearch.mdc` 只做：串联顺序、传路径、卡口、回退。方法论全在子 Skill。

## 目录

```
.cursor/rules/
  modelresearch.mdc            # 主编排器
  modelresearch-scope.mdc
  modelresearch-profile.mdc
  modelresearch-eval.mdc
  modelresearch-handson.mdc
  modelresearch-assess.mdc
  modelresearch-write.mdc
  modelresearch-build.mdc
model-research/
  templates/                   # 各步产物模板
  output/                      # 跑报告时的产物
  README.md
```

## 怎么用

```
按 ModelResearch 主 Skill 编排，评估模型：「<模型名>」。
读者：<内部选型/对外交付/投研/学术>；决策问题：<要不要用/替代谁/用在哪>。
从 Step 1 起逐步执行，每步过质量卡口后再进下一步。
```

## 落地进度

- [x] 主编排器 `modelresearch.mdc`
- [x] `modelresearch-scope`（目的/读者/决策问题/版本快照/维度选择）
- [x] `modelresearch-profile`（Model Card 事实基线）
- [x] `modelresearch-eval`（能力框架 + 基准口径 + 证据分级）
- [x] `modelresearch-handson`（一手实测 / 不可得声明）
- [x] `modelresearch-assess`（纵横对标 + 安全合规可得性 + TCO + 适配矩阵）
- [x] `modelresearch-write`（中立评估语域 + 风险登记 + 复现附录）
- [x] `modelresearch-build`（客观图表 + 多格式，复用 research-workflow/scripts）
- [ ] 端到端试跑（待用户确认读者/决策问题/是否需一手实测后进行）
