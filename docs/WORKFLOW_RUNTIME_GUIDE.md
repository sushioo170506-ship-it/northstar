# 研究报告工作流运行流程与核心功能说明

本文档对应 `northstar-research-workflow 0.1.0`，描述当前代码实际实现的能力、运行边界和
生产化建议。除特别标注为“建议”外，流程均可在现有实现中直接运行。

## 1. 整体架构与核心业务目标

### 1.1 核心业务目标

系统将研究报告从主题输入到终稿输出拆分为可审计、可确认、可恢复的标准流程，主要解决：

1. 统一主题、篇幅、风格和输出格式，避免各阶段参数漂移；
2. 将需求、议题树、大纲、调研、证据、素材、可视化、写作、压力测试、排版、审核和质量门解耦；
3. 在议题树、大纲、初稿、终审前强制人工确认，避免错误自动扩散；
4. 修改任意产物时只重跑受影响节点，保留无关的有效结果；
5. 持久化配置、节点状态、产物、反馈和操作记录，支持进程中断后恢复；
6. 通过精确产物读取管理十万字级必需上下文，并为自定义 Skill 提供辅助向量检索接口。

内置模式是可重复运行的离线实现，不会访问互联网，也不会把不存在的资料伪装成检索结果。
生产环境可以通过稳定接口接入外部检索、模型或远程 Skill。

### 1.2 逻辑架构

```text
用户/CLI/Python API
        |
        v
ReportConfig 参数校验与标准化
        |
        v
ResearchReportOrchestrator
  |-- DAG 调度、状态机、确认门、影响分析
  |-- SkillRegistry -------------------------------+
  |                                                |
  |   capability_sweep -> requirements_analysis -> skill_research
  |      -> issue_tree -> [主题与议题树确认]
  |      -> outline -> [大纲确认] -> research(产业/学术/实景)
  |      -> evidence_governance -> data_processing -> material_integration
  |      -> visualization -> writing -> pressure_test -> [初稿确认]
  |      -> formatting -> [终审前确认] -> review -> quality_gate -> publish
  |
  |-- SQLiteStateStore  -> state.db
  |      配置、节点状态、产物分片、确认、用户操作
  |
  +-- SQLiteVectorStore -> vectors.db
         检索分片、稀疏向量、作用域元数据、active 版本
```

### 1.3 物理部署边界

当前实现：

- 单进程或单主机部署；
- 两个 SQLite WAL 数据库；
- Python 3.11+，运行时无第三方依赖；
- Skill 与编排器在同一进程运行；
- 无内置网络服务、任务队列或模型供应商绑定。

当前实现不是真正的分布式系统。多主机部署应将状态存储替换为 PostgreSQL，将向量存储替换
为 pgvector/Qdrant 等生产后端，并加入节点租约、幂等键和分布式锁。

### 1.4 全局配置中心

`ReportConfig` 创建后冻结并写入 `workflows.config_json`，所有节点从同一记录读取：

| 参数 | 类型 | 默认值/限制 | 使用节点 |
|---|---|---|---|
| `topic` | string | 必填，1–500 字符，合并多余空白 | 全部 |
| `expected_length` | integer | 500–500000，默认 5000 | outline、writing、review |
| `style` | string | 专业、客观、证据驱动 | 模型 outline、formatting 元数据/模型 |
| `output_format` | enum | markdown/html/json/text | formatting、review |
| `language` | string | zh-CN | 已持久化；当前内置 Skill 尚未消费 |
| `output_type` | string | research_report | requirements_analysis、outline |
| `audience` | string | 通用专业读者 | requirements_analysis、outline、review |
| `content_boundaries` | string[] | 默认空 | requirements_analysis、review、quality_gate |
| `prior_thoughts` | string | 默认空 | requirements_analysis、issue_tree |
| `extra` | object | 默认空对象 | research/外部适配器 |

`md/htm/txt` 分别标准化为 `markdown/html/text`。离线 outline 不根据 style 改写结构，
离线 formatting 主要做格式转换并记录 style；实际风格生成依赖 TextGenerator。运行过程中
Skill 不能私自更改配置。来源可通过 `update_sources()` 合法替换，该操作更新配置并从
requirements_analysis 开始失效全部后代，用于修复证据红线；topic、篇幅、风格和格式仍需创建新工作流。已实现与
尚未验证的边界见 6.4。

## 2. 完整运行流程

### 2.1 正常时序

```text
create
  |
capability_sweep
  |
requirements_analysis
  |
skill_research
  |
issue_tree
  |
[issue_tree_confirmation] -- 未确认则暂停
  |
outline
  |
[outline_confirmation] -- 未确认则暂停
  |
research
  |
evidence_governance
  |
data_processing
  |
material_integration
  |
visualization
  |
writing
  |
pressure_test
  |
[draft_confirmation] -- 未确认则暂停
  |
formatting
  |
[pre_review_confirmation] -- 未确认则暂停
  |
review
  |
quality_gate -- 红线或低于 24/35 则阻断
  |
publish
  |
completed -> final_report
```

每次 `run(workflow_id)` 从 DAG 起点扫描：

1. 跳过状态为 `completed` 的节点；
2. 校验当前节点所有依赖均为 `completed`；
3. 普通节点进入 `running`，执行 Skill，验证并保存产物；
4. 确认节点未获批准时进入 `waiting_confirmation` 并立即返回；
5. 任一节点异常时记录 `failed` 和错误文本，停止本次运行；
6. review 完成后将工作流标记为 `completed` 并返回终稿产物 ID。

### 2.2 状态机

节点状态：

```text
节点记录不存在 -> running -> completed
                         \-> failed -> running（再次调用 run）
completed -> invalidated -> running（用户修改后）
确认节点 -> waiting_confirmation -> completed
```

工作流状态为 `running`、`waiting_confirmation`、`failed` 或 `completed`。节点状态是恢复
位置的依据；工作流状态用于快速呈现整体进度。`NodeStatus.PENDING` 是预留枚举，当前实现
不会预先创建 pending 行；工作流创建后立即为 running，节点行在首次执行时才产生。

### 2.3 节点详细说明

#### 2.3.1 capability_sweep：技能与外部能力遍历

- 触发：每个工作流第一个节点，禁止跳过。
- 逻辑：完整列出 16 个内置 Skill；遍历开源/外部集成目录，记录许可证、星数快照、
  configured/disabled/reviewed_not_configured 和原因。
- 输出：`capability_manifest`。内置清单缺项或外部目录未遍历完整时失败。
- 边界：盘点不等于执行；无许可证、无认证或不适用的第三方能力不得强行运行。

#### 2.3.2 requirements_analysis：需求拆解与意图识别

- 触发：工作流创建后首先执行。
- 输入：topic、output_type、style、audience、expected_length、output_format、language、
  content_boundaries、reference sources、prior_thoughts。
- 逻辑：完整提取九类需求维度，标记默认值和缺失资料，不从隐式会话猜测。
- 输出：`requirements_brief`，供全部业务节点作为统一需求基线。

#### 2.3.3 skill_research：第三方 Skill 研究与合规适配

- 输入：requirements_brief，以及可选 GitHub 实时检索、OpenClaw/其他仓库候选。
- 逻辑：按匹配度和采用度排序；核验来源、作者、版本、许可证和渠道；宽松许可证生成标准
  SkillRequest/SkillResult 适配草案，GPL 仅外部进程，非商业/专有/未知许可证拒绝。
- 输出：`skill_research_report`，含候选、决策理由、改造点、SKILL.md 草案和完整溯源。
- 安全：只生成 pending_human_review 适配规范，不在运行中安装或执行远程代码。

#### 2.3.4 issue_tree 与 issue_tree_confirmation

- 输入：requirements_brief。
- 逻辑：生成 3–7 个一级问题及二级问题；逐项记录必要性、写作价值、证据需求和保留状态，
  无价值问题进入 excluded_issues。
- 输出：`issue_tree`。人工确认同时确认最终主题和多层级问题，未确认不得搭建大纲。

#### 2.3.5 outline 与 outline_confirmation

- 输入：已确认议题树、需求简报、篇幅和文风。
- 逻辑：将每个有效问题映射到章节，分配稳定 ID、目标篇幅、核心目的和证据要求，记录受众、
  文风、产出形态和内容边界对齐信息。
- 输出：`outline`。用户确认后形成最终大纲，后续调研只能依据该版本执行。

#### 2.3.6 research：按最终大纲调研

- 输入：需求简报、议题树、已确认大纲、用户来源和可选 SourceRetriever。
- 逻辑：分别执行产业、学术、实景/社媒三个检索 pass，标准化 industry、academic、
  social_media 类别（official/primary 兼容归入 industry），保留
  title、content、published_at、original URL、issue_ids；不会伪造联网结果。
- 输出：`evidence_pack` 与 retrieval_summary。缺少任一必需类别时明确记录 evidence gap。

#### 2.3.7 evidence_governance：证据治理

- 输入：调研包和议题树。
- 逻辑：计算可追溯率、原始链接覆盖率、来源类别覆盖、议题证据映射、利益相关方独立验证，
  检测编造、关键来源不可追溯、单一利益相关方支撑三类红线。
- 输出：`evidence_ledger`。无法验证不会直接等同虚假，但三类来源或链接不足会在质量门阻断。

#### 2.3.8 data_processing：论断账本、交叉验证与评分

- 输入：调研包、证据账本、议题树和大纲。
- 逻辑：生成 claim ledger，提取数字及时间上下文，按 A+/A/B/C/D 分级，登记冲突和关键
  论断双重独立验证状态。
- 条件评分：只有配置 5–10 个候选、4–6 个维度、权重、实测值和 10/5 分锚点时才计算；
  否则输出 not_applicable，禁止主观排名。
- 输出：`processed_research_data`，供素材、图表、正文和质量门共同消费。

#### 2.3.9 material_integration：素材整合

- 输入：最终大纲、调研包、证据账本。
- 逻辑：按 issue_ids 和 outline.linked_issue 把每项材料挂载到对应章节；综合章节引用全部
  来源；保留 source_id、类别、URL、内容和用途。
- 输出：`section_materials` 和 mount_coverage，覆盖率不足会进入压力测试。

#### 2.3.10 visualization：可视化处理

- 输入：多层级议题树和章节素材。
- 逻辑：生成 Mermaid 研究问题逻辑图、Vega-Lite 来源类别图；存在量化素材时增加量化证据图。
- 输出：`visualization_assets`，默认 6–10 项，至少包含比较、结构和时间类规范。

#### 2.3.11 writing：完整报告生成

- 输入：需求、议题树、大纲、调研、证据账本、章节素材、可视化。
- 逻辑：按章节和目标篇幅写作，区分事实/分析/建议；事实章节附 `[source_id](original_url)`；
  可视化以 Mermaid/Vega-Lite 代码块嵌入；资料不足必须显式披露。
- 输出：`draft`。模型路径当前仍是单次 generate，生产适配器应改为章节级调用。

#### 2.3.12 pressure_test 与 draft_confirmation

- 逻辑：独立执行逻辑、证据、反方论证、完整性审计，并额外检查三类来源、URL、素材挂载和
  可视化，不把审查意见混入正文。
- 输出：`pressure_test` 和 repair_actions。用户确认初稿时可同时审阅弱点报告。

#### 2.3.13 formatting 与 pre_review_confirmation

- 输入：初稿、style、output_format。
- 逻辑：转换 Markdown、HTML、JSON 或 text，不新增事实。排版后的候选稿必须经审核前确认。
- 输出：`formatted_draft`。

#### 2.3.14 review：真实性与需求合规复核

- 输入：需求、调研、证据、大纲、素材、可视化、压力测试和格式化报告。
- 逻辑：检查三类来源、每项原始 URL 是否出现在对应报告、篇幅、格式、素材挂载率、可视化、
  受众/文风声明和“禁止/不得包含”边界。
- 输出：`final_report` 候选及 review_checks_passed、issues、checks。

#### 2.3.15 quality_gate：D1–D7 发布质量门

- 输入：能力清单、需求简报、证据账本、processed data、素材、可视化、压力测试和候选终稿。
- 逻辑：评分满分 35、默认通过线 24；能力目录未遍历、三支柱/高等级证据/claim/链接不足、
  素材错挂、可视化少于 6 项、篇幅/边界违规、红线或低分任一条件都会 block_release。
- 通过：允许进入 publish。
- 拒绝：评分产物保留，节点和工作流 failed，抛出 QualityGateRejected；修订路由或
  update_sources 将流程退回最早受影响节点后重跑。

#### 2.3.16 publish：报告交付

- 输入：已通过质量门的 review、visualization 和 capability_manifest。
- 输出：`published_report` 和 publish_manifest。
- 规则：正文不再改写；明确格式、字数、图数、渲染器、self-contained、PNG 状态和限制。
- 无真实 Mermaid/Vega/Pandoc 渲染器时不得声称 SVG/PNG 已完成；Markdown 可诚实降级。

## 3. 功能模块与交互规则

### 3.1 ResearchReportOrchestrator

设计目的：集中处理流程控制，禁止业务 Skill 各自维护隐式状态。

主要职责：

- 创建并读取统一配置；
- 按固定 DAG 调度；
- 检查依赖、确认和节点状态；
- 组装 `SkillRequest`；
- 校验 `SkillResult`；
- 保存关系产物和向量分片；
- 计算修改影响范围；
- 提供终稿读取保护。

交互规则：编排器可以依赖所有基础接口；业务 Skill 不反向依赖编排器，也不能直接修改状态库。

### 3.2 SkillRegistry 与标准协议

`SkillRegistry` 按唯一 name 注册实现，重复名称会报错。统一协议：

```text
SkillRequest:
  workflow_id, node_id, config, inputs, context, feedback

SkillResult:
  content, artifact_type, metadata
```

Skill 必须是显式输入到不可变输出的转换器。远程服务可以实现 Proxy Skill，通过 RPC 传输相同
结构；编排器无需了解供应商、模型或部署方式。

编排器会把最多 16 个相关向量分片放入 `SkillRequest.context`。当前十六个内置 Skill
均只消费 `inputs` 精确依赖，尚未读取 context；该字段目前供自定义/远程 Skill 使用。

### 3.3 TextGenerator

设计目的：隔离 LLM 供应商。接口仅暴露 system、prompt、max_tokens。

当前默认不注入生成器，使用确定性离线实现。生产适配器负责：

- 鉴权和密钥保护；
- 超时、限流、供应商重试；
- token 预算与章节分段；
- 返回内容安全检查；
- 供应商请求 ID 和成本指标采集。

### 3.4 SQLiteStateStore

主要数据表：

| 表 | 作用 |
|---|---|
| `workflows` | 全局配置、整体状态、创建/更新时间 |
| `node_runs` | 节点状态、尝试次数、输入 ID、输出 ID、错误 |
| `artifacts` | 产物类型、checksum、元数据、分片数 |
| `artifact_chunks` | 16384 字符无损分片 |
| `user_operations` | create/confirm/modify 操作审计 |
| `confirmations` | 四个确认节点的批准和意见 |

产物读取时按分片序号重组，并重新计算 SHA-256；不一致立即报错。历史产物不物理删除。
当前没有历史产物列举 API；节点失效后 `output_artifact_id` 会清空，若要读取旧版本须已知
artifact_id 后调用底层 `artifact()`，或补充版本查询接口。

### 3.5 SQLiteVectorStore

设计目的：在不一次载入全部历史内容的情况下提供辅助语义上下文。

实现逻辑：

- 2000 字符分片，200 字符重叠；
- 中文字符、中文二元组和英文/数字词元；
- BLAKE2b 哈希到 512 维稀疏向量并归一化；
- 查询先按 workflow_id、node_id、artifact_type、active 精确过滤，再计算余弦点积；
- 同一节点新产物入库时旧向量设为 `active=0`；
- 修改节点及其后代时对应向量立即失活，但历史记录保留。

必需依赖始终按产物 ID 从关系库完整读取，向量 top-k 仅为辅助上下文。这一规则避免语义检索
漏召回导致必要输入丢失。编排器请求 top-k=16，存储接口独立调用时默认 top-k=12。当前内置
Skill 尚未消费召回结果，因此十万字测试主要验证的是关系分片精确读取和向量 API/作用域，
不是向量内容参与生成的效果。

### 3.6 Prompt 模板

业务 Skill Prompt 集中在 `prompts.py` 并带版本元数据。调度本身由确定性的 Python DAG 和
状态机执行，不由 LLM Prompt 决定。`ORCHESTRATOR_PROMPT` 是对外部代理和 Skill 文档提供的
标准化示范模板，当前运行路径没有 import 或执行它。模板描述的约束包括：

- 只运行依赖已完成的节点；
- 四个确认点必须暂停；
- 修改时仅失效 DAG 后代；
- 调用前校验上下文和 checksum；
- 失败后从失败节点恢复；
- Skill 不读取隐式会话状态。

修改业务 Skill Prompt 可能改变模型路径输出，应同步提升 Skill 版本并执行回归测试；修改
`ORCHESTRATOR_PROMPT` 不会改变当前 Python 调度行为。

### 3.7 CLI

命令包括 `create`、`run`、`confirm`、`modify`、`revise`、`update-sources`、`status`、
`final`。结构化结果使用 JSON，
可预期的 ValueError/KeyError/RuntimeError 写入 stderr 并返回退出码 2。

CLI 是薄适配层，不保存会话状态；所有恢复均依赖显式 workflow_id 和 data directory。

## 4. 断点修改与上下文生命周期

### 4.1 影响分析

`modify(workflow_id, target_node, feedback)` 从目标节点出发计算全部传递后代：

| 修改目标 | 主要失效范围 |
|---|---|
| requirements_analysis | 全部后续节点和确认 |
| issue_tree | 议题树及全部后代；保留需求简报 |
| outline | outline 及全部后代；保留需求和已确认议题树 |
| research | 调研、证据、数据处理、素材、可视化及全部写作/复核后代 |
| evidence_governance | 证据治理、数据处理及下游；保留需求、议题树、大纲和原始调研 |
| data_processing | claim/评分、素材、可视化及写作/复核后代 |
| material_integration | 素材整合、可视化及写作/复核后代 |
| visualization | 可视化及写作/复核后代，不重跑素材整合 |
| writing | writing、pressure_test、初稿确认、formatting、终审前确认、review、quality_gate、publish |
| pressure_test | pressure_test、初稿确认、review、quality_gate、publish；不重跑 writing |
| formatting | formatting、终审前确认、review、quality_gate、publish |
| review | review、quality_gate、publish |
| quality_gate | quality_gate、publish |
| publish | 仅重新发布 |

修改确认节点本身不允许；用户应修改产生业务产物的节点。

### 4.2 修改执行

1. 校验目标节点和反馈非空；
2. 写入 `user_operations(operation="modify")`，记录反馈和影响集合；
3. 受影响且已存在的节点设为 `invalidated`；
4. 清除受影响确认记录；
5. 对应向量设为 inactive；
6. 工作流恢复为 running；
7. 下一次 run 从最早失效节点执行。

旧产物仍可用于审计，但不会作为当前节点输出或活跃向量参与新流程。
modify 当前不限制工作流整体状态；在 waiting/failed/completed 状态均可调用。它也没有与
同时进行的 run 建立互斥，因此即使在单主机，多进程并发 run/modify 也属于未定义且未验证
场景，调用层应先串行化同一 workflow 的写操作。

证据红线修复使用 `update_sources(workflow_id, sources, reason)`：新来源先经过 ReportConfig
校验并持久化，再记录不含正文的 update_sources 审计事件，随后以 requirements_analysis 为目标执行同一
影响分析。议题树等四个确认会重新打开，质量门通过前终稿始终不可读取。

自然语言修改使用 `request_revision()`/CLI `revise`，通过加权关键词而非首词匹配：主题、
受众、边界路由到需求节点；议题树/子问题到 issue_tree；大纲/框架到 outline；来源、事实、
数据、链接到 research；证据治理、素材整合、图表、压力测试、格式、复核、质量门均有独立
目标；篇幅、文风和论证路由到 writing。混合意见选择总权重最高且最早必要的节点，路由结果
和原始反馈写入审计表，再由 DAG 计算全部后代。

### 4.3 中断恢复

进程重启后使用相同 data directory 创建新 Orchestrator：

- completed 节点直接跳过；
- waiting_confirmation 继续等待同一确认；
- failed 或中断于 running 的节点再次执行；
- 输入按已完成依赖的当前产物 ID 重建；
- 尝试次数递增。

节点 Skill 应保持幂等。当前本地 Skill 没有外部副作用；远程 Skill 需要使用
`workflow_id + node_id + attempts/输入 checksum` 作为幂等键。

两个 SQLite 数据库之间没有跨库事务或两阶段提交。保存顺序是关系产物、向量分片、节点完成
状态；在步骤之间崩溃可能留下未被节点引用的 orphan artifact，或使节点停留在 running。
再次 run 会重做节点，新向量入库时旧向量失活，但 orphan 历史不会自动回收。生产版本应使用
outbox/修复任务保证跨存储一致性，并提供安全的历史清理策略。

## 5. 异常、重试、日志与告警

### 5.1 当前异常处理

| 异常 | 当前行为 |
|---|---|
| 配置非法 | create 抛出 ValueError，不创建工作流 |
| workflow/产物不存在 | 抛出 KeyError |
| 依赖未完成 | run 抛出 RuntimeError |
| Skill 返回空内容/无类型 | validate 抛出 ValueError |
| Skill 执行异常 | 节点设为 failed，保存错误文本，工作流设为 failed |
| checksum 不一致 | 读取产物时立即抛出 ValueError |
| 非等待状态确认 | confirm 拒绝并抛出 ValueError |
| 非法修改目标/空反馈 | modify 拒绝并抛出 ValueError |
| 质量门红线/低分 | 保存评分产物，节点和工作流 failed，抛出 QualityGateRejected |
| 终稿尚未完成 | final_report 拒绝读取 |

异常不会被静默吞掉。CLI 对已知业务异常返回 2；未预期的系统异常保留 Python traceback。
Python API 的 run 会在先持久化 failed 状态后把原异常继续抛给调用方，调用方必须捕获并决定
何时再次运行。CLI 只把 ValueError、KeyError、RuntimeError 规范化为 JSON；其他异常仍会
直接传播并产生 traceback。

### 5.2 当前重试策略

当前没有定时自动重试、指数退避或最大次数限制。重试方式是再次调用 `run(workflow_id)`：

- 已完成节点不会重复；
- 失败/运行中节点重新执行；
- `node_runs.attempts` 增加；
- 上一次错误在新状态写入时被替换。

这种方式适合本地可控运行，但不适合无人值守的外部模型调用。

生产建议：

1. 仅对超时、429、5xx、临时网络错误重试；
2. 对参数、协议、内容校验错误直接失败；
3. 使用指数退避加抖动，例如 2/4/8/16 秒；
4. 设置节点级最大尝试次数和总超时；
5. 保留每次 attempt 的独立历史，不能覆盖旧错误；
6. 外部调用必须携带幂等键，避免计费和副作用重复。

### 5.3 当前日志与审计

现有持久化记录：

- 工作流创建和更新时间；
- 节点状态、attempts、输入/输出产物 ID、最后错误、更新时间；
- 产物 checksum、Skill 名称和版本；
- create/confirm/modify 用户操作、意见和时间戳；
- 确认状态和评论。

当前没有结构化应用日志、请求 trace、操作者身份、IP、模型调用 token/成本、错误堆栈和日志
轮转。`user_operations` 是业务审计记录，不应被当作完整运维日志。

建议日志统一字段：

```text
timestamp, level, event, workflow_id, node_id, attempt,
skill_name, skill_version, input_artifact_ids, output_artifact_id,
duration_ms, error_type, retryable, trace_id, actor_id
```

禁止记录模型密钥和完整敏感资料。正文可用 artifact ID/checksum 引用，避免复制到日志。

### 5.4 当前告警配置

当前版本没有内置告警通道、阈值或通知集成。以下为建议配置，不是现有功能：

| 告警 | 建议条件 | 级别 |
|---|---|---|
| 节点持续失败 | 同节点连续失败 ≥3 次 | P1 |
| 工作流卡死 | running 超过节点 SLA 且无更新时间 | P1 |
| 索引不一致 | completed 产物无 active 向量或 checksum 失败 | P1 |
| 确认长期等待 | waiting_confirmation 超过业务时限 | P2/业务提醒 |
| 数据库容量 | 持久卷使用率 >70%/85% | P2/P1 |
| 模型限流 | 429 比例或供应商错误率超阈值 | P2 |
| 质量门拒绝 | quality_gate failed 或触发红线 | P1/发布阻断 |
| 成本异常 | 单工作流 token/费用超过预算 | P2 |

告警应发送到组织现有监控系统，并附 workflow/node/trace ID，不附报告全文。

## 6. 性能、资源占用与验证场景

### 6.1 自动化测试结果

2026-07-12 在 Linux 6.12、Python 3.12.3 上验证：

- 24 个测试全部通过；
- 20 个独立离线确定性工作流全部完成：20/20（测试阈值为 ≥95%）；该样本不代表外部模型、
  检索或生产环境 SLA；
- 105000 字目标端到端完成，最新基线终稿 118558 字（含来源与可视化规范）；
- 进程重启后从大纲确认点恢复；
- 四个确认门全部验证；
- 16 个内置 Skill 全部完成，11 个外部集成项全部遍历并记录未执行原因；
- 三支柱分别调用、claim ledger、锚点评分、7 项可视化和独立 publish 均进入真实 DAG；
- 显式编造关键来源会阻断发布并禁止读取终稿；
- 无来源报告会披露证据缺口并被质量门阻断；
- 模型质量门即使自行返回满分通过，也不能绕过确定性的来源、红线和分数策略；
- 来源 issue_ids 到议题树的证据覆盖映射已验证；
- 缺少学术或社媒类别会被阻断，三类原始 URL 均须出现在终稿；
- 图表反馈会路由到 visualization，保留未受影响的素材整合产物；
- “禁止/不得包含”边界命中后会阻断发布并列出违规项；
- 来源 issue_ids 与章节不匹配时，质量门重算挂载率并阻断；
- 修改 writing 后仅重跑后代，research 和 outline 产物 ID/执行次数不变；
- 旧 writing 向量失活，查询只返回新产物；
- Markdown、HTML、JSON、纯文本路径通过；
- Python 编译、包构建和 CLI 入口通过。

### 6.2 十万字离线性能基线（单次手工测量，N=1）

独立临时测量程序在同一环境创建一个全新 data directory，依次执行 create、四次
run/confirm 和最终 run，再使用 `time.perf_counter()`、`resource.getrusage()`、文件
`stat()` 采集结果。它不是 24 个 unittest 的计时，也尚未纳入 CI 基准脚本。基线输入包含
产业、学术、实景三类可追溯来源：

| 指标 | 结果 |
|---|---:|
| 目标篇幅 | 105000 字符 |
| 最终报告 | 118558 字符 |
| 端到端处理耗时 | 0.8664 秒 |
| 峰值 RSS | 38408 KiB（约 37.5 MiB） |
| state.db 文件族（含 WAL/SHM） | 1772920 bytes（约 1.69 MiB） |
| vectors.db 文件族（含 WAL/SHM） | 2973768 bytes（约 2.84 MiB） |
| 确认节点 | 4 个，全部按序命中 |
| 内置 Skill | 16，全部完成 |
| 外部集成目录 | 11，全部遍历 |
| skill_research 候选/草案 | 11 / 3 |
| Claim | 3 |
| 可视化资产 | 7 |
| D1–D7 质量分 | 33.0/35，通过 |
| 最终状态 | completed |

测量包含本地写作、格式化、关系库分片、向量计算和索引，不包含人工等待时间。数据仅表示
一个无修改历史的工作流，是单次开发环境基线，不是生产 SLA 或容量估算；文件大小还可能受
SQLite page、WAL checkpoint、操作系统缓存和历史版本影响。

### 6.3 性能特征

- 写作生成和关系产物存储大体随正文长度线性增长；
- vectors.db 的检索索引按约 1800 个新字符产生一个分片；state.db 使用 16384 字符无损分片；
- 当前查询把过滤后的候选向量读入 Python 逐个计算，候选规模大时为 O(n)；
- 完整产物读取会在内存拼接为一个字符串，因此峰值内存仍与最大单产物长度相关；
- SQLite WAL 适合单主机轻并发，不适合跨主机高写入并发；
- 接入 LLM 后，网络和模型生成时间将远大于本地编排时间。

### 6.4 已验证与未验证场景

已验证：

- 新建、三段确认、最终输出；
- 重启恢复；
- 选择性重跑和尝试次数；
- 配置标准化及非法输入；
- 多输出格式；
- 十万字级长内容；
- 活跃/失效上下文隔离；
- 20 次确定性批量运行。

尚未验证：

- 真实互联网文献检索及引用真实性；
- 任意 LLM 供应商的质量、限流、成本和超时；
- DOCX/PDF 发布；
- 多进程并发修改同一 workflow；
- 多主机部署、故障转移和灾备恢复；
- 百万级向量、持续高 QPS 和长期数据库膨胀；
- 恶意 Prompt、敏感数据泄漏、租户隔离；
- 真实用户对研究质量的人工评分。

## 7. 不足、风险点与优化方向

### 7.1 高优先级

1. **无生产级分布式协调**
   - 风险：两个执行器同时运行同一节点，可能重复调用外部模型并产生竞态。
   - 优化：PostgreSQL 行锁/租约、节点幂等键、队列消费者、事务 outbox。

2. **无自动重试和超时**
   - 风险：临时网络错误需要人工恢复；外部调用可能长期挂起。
   - 优化：错误分类、节点超时、指数退避、最大次数、死信队列。

3. **质量门评分仍是启发式规则**
   - 风险：已能阻断红线和低分报告，但 D1–D7 离线评分尚未通过真实人工标注集校准。
   - 优化：建立黄金评测集、双评审一致性指标、分场景阈值和受审计的人工豁免流程。

4. **检索不是实际联网检索**
   - 风险：未提供 sources 时只能标记资料缺口，不能自动满足全面研究要求。
   - 优化：接入 Crossref、OpenAlex、arXiv、组织知识库等；保存来源快照、许可和检索时间。

5. **操作审计缺少身份**
   - 风险：无法证明由谁确认或修改。
   - 优化：API 层注入 actor_id、角色、来源 IP、请求 ID，操作记录只追加不可覆盖。

### 7.2 中优先级

6. **内置向量质量有限**
   - 风险：哈希稀疏向量适合轻量检索，但不等价于语义 embedding。
   - 优化：可插拔 embedding、混合 BM25+向量检索、召回评测集、reranker。

7. **向量查询是内存线性扫描**
   - 风险：长期历史或多租户数据增长后延迟和内存上升。
   - 优化：HNSW/IVF 索引、分页、命名空间分区、归档失效向量。

8. **完整产物在 Skill 调用时一次性加载**
   - 风险：接近 500000 字上限或多份大证据包时内存增加，远程协议也可能超限。
   - 优化：流式 ArtifactReader、章节级输入引用、对象存储和增量模型调用。

9. **attempt 只保留汇总**
   - 风险：新重试会覆盖节点最后错误，无法完整分析每次失败。
   - 优化：新增 `node_attempts` 追加表，记录开始/结束、错误、耗时和供应商请求 ID。

10. **仅来源支持带影响分析的配置更新**
    - 风险：update_sources 已可从需求简报开始重跑以修复红线，但文风、篇幅或格式变化仍须新建工作流。
    - 优化：扩展参数到节点的影响映射；例如仅改输出格式时从 formatting 开始失效。

11. **HTML 转换器能力基础**
    - 风险：列表、表格、代码块和复杂引用没有完整 Markdown 语义。
    - 优化：引入有明确许可证的成熟渲染器，并做 XSS 清理和模板版本管理。

### 7.3 低优先级与演进能力

12. 增加 DOCX/PDF/引用格式发布 Skill；
13. 增加章节并行写作及最终一致性合并；
14. 增加产物版本比较、回滚和可视化 DAG；
15. 增加 OpenTelemetry trace、Prometheus 指标和告警模板；
16. 增加数据保留、删除、导出和租户配额；
17. 增加 Prompt/模型 A/B 测试和人工质量评分；
18. 增加来源事实核验、重复引用检测和引文覆盖率指标。

## 8. 建议的完善顺序

建议按风险优先级推进：

1. 质量阻断门、节点超时/重试、attempt 历史；
2. 结构化日志、身份审计、指标与告警；
3. 真实检索和引用验证；
4. PostgreSQL/生产向量库及并发租约；
5. 流式长文本、对象存储和章节并行；
6. DOCX/PDF 发布、可视化和高级质量评测。

在修改前应先确定部署规模、模型供应商、允许的来源、合规等级、质量阻断规则和目标 SLA。
这些选择会直接决定存储、重试、审计和告警的具体实现。
