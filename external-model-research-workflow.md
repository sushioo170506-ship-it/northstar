# 外部模型调研报告工作流（按七步技能编排）

> 主 Skill：`model-report-orchestrator`  
> 流程：定调 -> 搭大纲 -> 采素材 -> 加工素材 -> 写正文 -> 复核 -> 输出

---

## 1. 主 Skill（编排器）

**name**: `model-report-orchestrator`  
**description**: 外部模型调研报告自动生成工作流 — 输入模型名称，按七步输出完整报告。

**职责边界**：  
本 skill 只负责串联子 skill、传递中间产物、执行质量卡口。  
具体写大纲、采数据、加工素材、写正文由子 skill 负责。

**反草率硬门槛（长篇详实）**：
- 来源总数 >= 12
- benchmark 指标 >= 8
- 直接竞品 >= 3
- 可交付表格 >= 6
- 图表规格 >= 3
- 复核总分 >= 85（且事实性/逻辑一致性 >= 18/20）

---

## 2. 执行流程（严格顺序）

```text
Step 1: 定调        -> 报告企划书（读者画像 + 报告类型 + 结论形式）
Step 2: 搭大纲      -> 章节大纲（含素材需求标注）
Step 3: 采素材      -> raw_data/（原始素材，按章节分类）
Step 4: 加工素材    -> processed_data/（结构化内容块：表格/图表/要点）
                      (若缺素材 -> 回退 Step 3)
Step 5: 写正文      -> report.md（报告初稿）
Step 6: 复核        -> 复核清单（通过/不通过）
                      (不通过 -> 按问题类型回退)
Step 7: 输出        -> output/（最终交付件）
```

---

## 3. 子 Skill 定义

### Skill 1: `mr-step1-scope`（定调）

- 作用：确定读者画像、报告类型、结论形式和约束条件。
- 输入：模型名称 + 3个必答问题（谁看/看完做什么/最怕什么）。
- 输出：`archive/scope.md`（报告企划书）。
- 质量卡口：
  - 三个问题必须都有回答；
  - 读者画像必须具体到角色与决策场景；
  - 报告类型必须单选明确；
  - 结论形式必须可执行（推荐/有条件推荐/不推荐 或 绿黄红）。

### Skill 2: `mr-step2-outline`（搭大纲）

- 作用：生成章节骨架并标注每章素材需求。
- 输入：`archive/scope.md` + 模型名称。
- 输出：`archive/outline.md`。
- 规则：按报告类型使用预设骨架（技术选型/安全审查/投资研判/竞品追踪）并按读者与篇幅裁剪。
- 质量卡口：
  - 每章必须有核心问题；
  - 每章必须有素材需求；
  - 需要图表的章节必须显式标注。

### Skill 3: `mr-step3-collect`（采素材）

- 作用：按大纲采集原始信息，不做加工、不下判断。
- 输入：`archive/outline.md` + 模型名称。
- 输出：`archive/raw_data/`（paper/official/benchmarks/competitors/ecosystem/references）。
- 质量卡口：
  - 官方技术报告/论文必采；
  - 基础参数 >= 10 字段；
  - benchmark >= 5；
  - 直接竞品 >= 2；
  - 每条素材有 URL 与时间戳；
  - 官方与第三方素材分开存放。
  - 长篇模式下必须满足来源/benchmark/竞品下限。

### Skill 4: `mr-step4-process`（加工素材）

- 作用：把原始素材加工成可写入正文的结构化内容块。
- 输入：`archive/raw_data/` + `archive/outline.md`。
- 输出：`archive/processed_data/` + `archive/processed_data/gaps.md`。
- 动作：信息归位、表格化、要点提炼、图表生成、缺失检测。
- 质量卡口：
  - 素材按章节归位；
  - 关键参数/分数已表格化；
  - 图表按大纲需求生成（或标注暂缺）；
  - gaps 检测完整；
  - 素材严重缺失必须回退 Step 3。
  - 必须产出 evidence_map（结论可追溯到证据）。
  - 长篇模式下表图数量未达门槛则不通过。

### Skill 5: `mr-step5-write`（写正文）

- 作用：将内容块组装为连贯正文，结论在正文中自然形成。
- 输入：`archive/processed_data/` + `archive/outline.md` + `archive/scope.md`。
- 输出：`archive/report.md`。
- 写作规则：
  - 按依赖顺序写章节（优先 §3、§2、§4...）；
  - 每段一个职能（判断/发现/对比/解读/局限/行动）；
  - 关键数字后必须跟“这意味着...”；
  - 禁止背景套话开篇；
  - §7 结论必须给出场景化推荐。
  - 长篇模式下正文建议 3000-5000 字，核心章节需定量证据支撑。

### Skill 6: `mr-step6-review`（复核）

- 作用：按清单做事实性、完整性、读者视角、逻辑一致性、写作质量检查。
- 输入：`archive/report.md` + `archive/scope.md` + `archive/outline.md`。
- 输出：`archive/review_checklist.md`（通过/不通过 + 修正建议）。
- 回退规则：
  - 事实性不通过 -> Step 3；
  - 完整性不通过 -> Step 2 或 Step 4；
  - 读者视角/逻辑/写作质量不通过 -> Step 5。
  - 量化评分未达阈值（总分 < 85） -> 回退对应步骤。

### Skill 7: `mr-step7-output`（输出）

- 作用：按交付渠道转换格式并归档中间产物。
- 输入：`archive/report.md`（复核通过）+ `archive/scope.md` + `archive/review_checklist.md`。
- 输出：`archive/output/`：
  - `report.md`
  - `report.pdf`
  - `executive_summary.md`
  - `figures/`
  - `slides/`（可选）
- 质量卡口：
  - Executive Summary 可独立阅读；
  - 目标格式转换完成；
  - PDF 中文可读；
  - 图表显示正常；
  - 中间产物归档完整。
  - 长篇模式下表图数量未达门槛时，不得标记“最终交付”。

---

## 4. 目录约定

```text
archive/
├── scope.md
├── outline.md
├── raw_data/
├── processed_data/
│   ├── section_1/
│   ├── section_2/
│   ├── ...
│   ├── figures/
│   └── gaps.md
├── report.md
├── review_checklist.md
└── output/
    ├── report.md
    ├── report.pdf
    ├── executive_summary.md
    ├── figures/
    └── slides/
```

---

## 5. 7 个 Skill 速查表

| Skill | 一句话职责 | 输入 | 输出 | 回退 |
|---|---|---|---|---|
| mr-step1-scope | 定义读者、定位、结论形式 | 模型名称+3问 | scope.md | — |
| mr-step2-outline | 构建骨架并标注素材需求 | scope.md | outline.md | -> step1 |
| mr-step3-collect | 采集原始素材 | outline.md + 模型名 | raw_data/ | -> step2 |
| mr-step4-process | 素材加工成结构化块 | raw_data/ + outline.md | processed_data/ + gaps.md | -> step3 |
| mr-step5-write | 生成连贯正文 | processed_data/ + outline.md + scope.md | report.md | -> step4 |
| mr-step6-review | 质量复核与回退判定 | report.md + scope.md + outline.md | review_checklist.md | -> step2/3/4/5 |
| mr-step7-output | 格式转换与交付归档 | report.md + review_checklist.md | output/ | -> step6 |

