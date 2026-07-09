# 外部模型调研报告自动化工作流（Skill 编排文档）

> 目标：输入一个模型名，自动生成一份可用于技术选型/安全审查/竞品追踪的外部模型调研报告。  
> 设计参考：你提供的“研究报告工作流”思路（主 Skill 编排 + 子 Skill 串联 + 质量卡口 + 回路修正）。

---

## 1. 设计原则（参考文章后的落地约束）

本工作流采用「**1 个主流程 + 7 个独立 Skill**」的串联模型：

1. **单步单责**：每个 Skill 只做一类事情，避免职责重叠。
2. **标准输入输出**：每步都输出结构化文件，供下一步消费。
3. **质量卡口**：每步完成后强校验，通过才进入下一步。
4. **失败回路**：复核失败自动回流到写作或证据步骤，不带病发布。
5. **可追溯**：所有关键结论必须能回溯到来源与版本。

---

## 2. 总流程（7 步 = 7 Skills）

```text
Step 1 定调 (skill_01_brief)
   -> Step 2 搭大纲 (skill_02_outline)
   -> Step 3 证据采集与核验 (skill_03_evidence)
   -> Step 4 信息处理与编排 (skill_04_orchestration)
   -> Step 5 结构化写作与结论 (skill_05_write_decide)
   -> Step 6 复核 (skill_06_review)
   -> Step 7 输出与归档 (skill_07_publish)
```

失败回路：
- `skill_06_review` 未通过且属于表达/逻辑问题 -> 回 `skill_05_write_decide`
- `skill_06_review` 未通过且属于证据缺口 -> 回 `skill_03_evidence`

---

## 3. Skill 编排清单（职责、输入、输出、卡口）

### Skill 01 — `skill_01_brief`（定调）

**作用**  
把“模型名”转成可执行任务定义，确定读者、决策目标、报告类型和交付格式。

**输入**  
- `model_name`（必填）
- `report_type`（默认 `tech-selection`）
- `audience`（默认 `tech-lead`）
- `output_formats`（默认 `md,pdf`）
- `depth`（`quick/standard/deep`）

**输出**  
- `output/brief.json`

**质量卡口**  
- 明确“看完后做什么决策”
- 明确结论表达方式（推荐/有条件推荐/不推荐 或 绿黄红）
- 明确不评估边界

---

### Skill 02 — `skill_02_outline`（搭大纲）

**作用**  
生成章节骨架，并为每章标注核心问题、证据需求和完成标准（DoD）。

**输入**  
- `output/brief.json`

**输出**  
- `output/outline.json`

**质量卡口**  
- 每章必须包含：核心问题 + 证据类型 + DoD
- 大纲结构可映射回决策目标

---

### Skill 03 — `skill_03_evidence`（证据采集与核验）

**作用**  
按大纲批量采集资料并做交叉验证、去重和可信度分级。

**输入**  
- `output/brief.json`
- `output/outline.json`

**输出**  
- `output/evidence_base.json`
- `output/references.bib`（可选）

**质量卡口**  
- 核心 claim 至少 2 个独立来源（无法满足要显式标注）
- 关键数据需包含“数字 + 时间 + 来源”
- A+/A/B 采信比例建议 >= 80%
- 冲突数据需保留并标注处理策略

---

### Skill 04 — `skill_04_orchestration`（信息处理与编排）

**作用**  
在写正文前完成“证据映射 + 可视化规划 + 叙事排序”，避免直接堆料写作。

**输入**  
- `output/outline.json`
- `output/evidence_base.json`

**输出**  
- `output/section_mapping.json`（证据 -> 章节）
- `output/asset_plan.json`（图表/表格/流程图计划）
- `output/writing_pack.json`（段落级写作输入包）

**质量卡口**  
- 每章至少 1 条高可信主证据
- 每个核心判断都绑定证据 ID
- 图表计划字段可追溯来源

---

### Skill 05 — `skill_05_write_decide`（结构化写作与结论）

**作用**  
基于写作包生成正文，同时产出可执行结论和行动建议。

**输入**  
- `output/brief.json`
- `output/writing_pack.json`
- `output/asset_plan.json`
- `output/evidence_base.json`

**输出**  
- `output/draft.md`
- `output/decision.json`

**质量卡口**  
- 结论与正文证据一致
- 给出明确决策分级（推荐/有条件推荐/不推荐）
- 包含适用边界、风险与下一步动作

---

### Skill 06 — `skill_06_review`（复核）

**作用**  
执行事实、逻辑、一致性、完整性和可用性检查，输出修订稿。

**输入**  
- `output/draft.md`
- `output/decision.json`
- `output/outline.json`
- `output/evidence_base.json`

**输出**  
- `output/review_report.json`
- `output/revised_draft.md`

**质量卡口**  
- `critical = 0` 才允许发布
- `major > 0` 则必须返修

---

### Skill 07 — `skill_07_publish`（输出与归档）

**作用**  
生成交付件并归档版本元数据，支持后续审计和增量更新。

**输入**  
- `output/revised_draft.md`
- `output/decision.json`
- `output/asset_plan.json`
- `output/review_report.json`

**输出**  
- `output/final.md`
- `output/final.pdf`
- `output/executive_summary.md`
- `output/archive.json`

**质量卡口**  
- 各格式核心结论一致
- 图表和引用链接可用
- 记录数据截止时间、模型版本和产物清单

---

## 4. 标准目录结构

```text
output/
├── brief.json
├── outline.json
├── evidence_base.json
├── references.bib
├── section_mapping.json
├── asset_plan.json
├── writing_pack.json
├── draft.md
├── decision.json
├── review_report.json
├── revised_draft.md
├── final.md
├── final.pdf
├── executive_summary.md
└── archive.json
```

---

## 5. 运行入口参数（最小集）

```yaml
model_name: "示例模型名"
report_type: "tech-selection"
audience: "tech-lead"
depth: "standard"
output_formats: ["md", "pdf"]
time_window: "last_12_months"
```

---

## 6. 编排策略建议（主 Skill / Orchestrator 逻辑）

主编排器只做三件事：

1. **按顺序调用** `01 -> 07`
2. **检查卡口结果**，不通过则回退
3. **记录中间产物与状态**，保障可恢复执行

建议状态机：

```text
pending -> running -> passed -> (next)
                     \-> failed -> retry_once -> failed -> route_back
```

---

## 7. 与“研究报告工作流”思路的映射关系

- “主 skill 串联子 skill” -> 这里的主编排器 + 7 个独立 Skill
- “先大纲后数据后处理后写作” -> 这里的 Step 02/03/04/05
- “图表与输出独立步骤” -> 并入编排层与发布层（通过 `asset_plan` 和 `publish` 保证）
- “质量终检” -> Step 06 作为强门禁，未通过不允许发布

---

## 8. 使用建议（第一版上线）

1. 先跑 `tech-selection` 类型，减少分支复杂度。
2. 先保证结构化产物完整，再优化文风。
3. 先做“可追溯正确”，再做“自动图表美化”。
4. 发布后保留 `archive.json`，用于后续增量更新（模型新版本发布时复跑 Step 03~07）。

