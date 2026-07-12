# 研究报告工作流运行流程与核心功能说明

本文档对应 `northstar-research-workflow 0.1.0`，描述当前代码实际实现的能力、运行边界和
生产化建议。除特别标注为“建议”外，流程均可在现有实现中直接运行。

## 1. 整体架构与核心业务目标

### 1.1 核心业务目标

系统将研究报告从主题输入到终稿输出拆分为可审计、可确认、可恢复的标准流程，主要解决：

1. 统一主题、篇幅、风格和输出格式，避免各阶段参数漂移；
2. 将研究、议题树、证据治理、大纲、写作、压力测试、排版、审核和质量门解耦；
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
  |   research -> issue_tree -> [议题树确认] -> evidence_governance
  |      -> outline -> [大纲确认] -> writing -> pressure_test -> [初稿确认]
  |      -> formatting -> [终审前确认] -> review -> quality_gate
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
| `extra` | object | 默认空对象 | research/外部适配器 |

`md/htm/txt` 分别标准化为 `markdown/html/text`。离线 outline 不根据 style 改写结构，
离线 formatting 主要做格式转换并记录 style；实际风格生成依赖 TextGenerator。运行过程中
Skill 不能私自更改配置；如需变更全局参数，当前版本应创建新工作流，后续可增加带影响分析
的配置变更 API。已实现与尚未验证的边界见 6.4。

## 2. 完整运行流程

### 2.1 正常时序

```text
create
  |
research
  |
issue_tree
  |
[issue_tree_confirmation] -- 未确认则暂停
  |
evidence_governance
  |
outline
  |
[outline_confirmation] -- 未确认则暂停
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

#### 2.3.1 research：主题拆解与证据整理

- 触发条件：工作流已创建；无前置节点；当前节点未完成或已失效/失败。
- 输入：
  - `config.topic`；
  - `config.extra.sources`，可选字符串或对象数组；
  - 针对 research 的历史修改意见。
- 标准来源字段：`id`、`title`、`content`；缺失 ID/标题时按本次输入顺序生成序号。输入重排
  会改变自动 ID，生产来源适配器应提供跨运行稳定 ID。
- 执行逻辑：
  1. 按概念范围、现状驱动、关键机制、风险局限、结论建议拆分研究问题；
  2. 标准化用户提供的来源；
  3. 没有来源时生成明确的 `evidence_gaps`，不伪造引用；
  4. 注入 `TextGenerator` 后可改由模型处理，但仍须维持相同输出契约。
- 输出：
  - `artifact_type="evidence_pack"`；
  - JSON 字段：`topic`、`research_questions`、`sources`、`evidence_gaps`、
    `feedback_applied`；
  - 元数据：来源数量、是否需要外部检索。
- 后继：issue_tree；同时作为 evidence_governance、outline、writing 和 review 的精确依赖。

#### 2.3.2 issue_tree：议题树

- 触发条件：research 已完成。
- 输入：`inputs["research"]`、topic、针对 issue_tree 的修改意见。
- 执行逻辑：
  1. 生成 3–7 个可由证据回答的子问题；
  2. 每个子问题包含稳定 ID、初始假设、证据需求和状态；
  3. validate 强制检查子问题数量；
  4. MECE 完整性由后续人工确认和模型适配器增强。
- 输出：`artifact_type="issue_tree"`，JSON 包含 main_question、issues、coverage。
- 后继：`issue_tree_confirmation`。

#### 2.3.3 issue_tree_confirmation 与 evidence_governance

- 确认触发条件：issue_tree 已完成；未确认时工作流暂停。
- 证据治理触发条件：research、issue_tree 和确认节点均完成。
- 输入：完整 evidence_pack 与已确认 issue_tree。
- 执行逻辑：
  1. 为来源记录主体、类型、发布时间、可追溯性、利益相关性和独立验证；
  2. 计算来源可追溯率、关键来源数量和独立覆盖率；
  3. 将一般缺失信息记为 issue，不把“无法验证”直接等同于“虚假”；
  4. 检测显式编造来源、无法追溯的关键来源、单一利益相关方关键支撑三类红线。
- 输出：`artifact_type="evidence_ledger"`，包含 sources、issue_coverage、metrics、issues、
  red_lines。
- 后继：outline，并作为 writing、pressure_test、review、quality_gate 的精确依赖。

#### 2.3.4 outline：大纲架构设计

- 触发条件：research 已完成。
- 输入：
  - `inputs["research"]`：完整 evidence_pack；
  - `inputs["issue_tree"]`：已确认议题树；
  - `inputs["evidence_governance"]`：证据治理账本；
  - topic、expected_length、style；
  - 针对 outline 的修改意见。
- 执行逻辑：
  1. 创建摘要、背景、发现、机制、风险、结论等章节；
  2. 为每节分配稳定 ID、目标篇幅、论证目的和证据需求；
  3. 记录 evidence_pack 的 SHA-256 提示，便于追踪输入版本。
- 输出：
  - `artifact_type="outline"`；
  - JSON 字段：标题、章节列表、总目标篇幅、已应用反馈、
    `evidence_checksum_hint`。
- 后继：必须先进入 `outline_confirmation`。

#### 2.3.5 outline_confirmation：大纲确认

- 触发条件：outline 已完成。
- 输入：workflow_id、可选人工确认意见。
- 执行逻辑：
  - 未确认：写入 `waiting_confirmation`，工作流暂停；
  - 调用 `confirm(workflow_id, "outline_confirmation", comment)`：写入确认和用户操作；
  - confirm 调用会立即把确认节点设为 completed、工作流设为 running；再次运行时跳过该节点。
- 输出：没有业务产物，仅有确认记录和节点状态。
- 后继：writing。

#### 2.3.6 writing：内容撰写

- 触发条件：research、issue_tree、evidence_governance、outline 和 outline_confirmation
  均已完成。
- 输入：
  - `inputs["research"]`；
  - `inputs["issue_tree"]`；
  - `inputs["evidence_governance"]`；
  - `inputs["outline"]`；
  - expected_length；
  - 针对 writing 的累计修改意见。
- 执行逻辑：
  1. 离线实现按大纲逐节确定性生成；
  2. 事实、分析、建议分离；
  3. 仅引用证据包中存在的来源；
  4. 来源不足时保留“资料缺口：待检索”；
  5. 将修改意见附入修订说明或交给模型适配器执行。
- 模型路径限制：当前 `TextGenerator` 分支进行一次 generate 调用，并可能请求很大的
  max_tokens；十万字生产写作必须由适配器分段，或后续把 WritingSkill 改为章节级模型调用。
- 输出：
  - `artifact_type="draft"`；
  - Markdown 结构初稿；
  - 元数据：字符数、章节数、Skill 版本。
- 后继：`pressure_test`。

#### 2.3.7 pressure_test：独立压力测试

- 触发条件：issue_tree、evidence_governance、outline、writing 均已完成。
- 输入：初稿、议题树、大纲和证据治理账本。
- 执行逻辑：独立执行逻辑、证据、最强反方论证、完整性四项审计；不把审查内容混入正文。
- 输出：`artifact_type="pressure_test"`，包含 overall_confidence、四类 audit、
  repair_actions、红线和元数据。
- 后继：`draft_confirmation`。用户确认时可同时审阅初稿和独立弱点报告。

#### 2.3.8 draft_confirmation：初稿确认

- 触发条件：writing 已完成。
- 输入/输出及确认规则与 outline_confirmation 相同。
- 业务含义：用户确认报告内容方向后才允许排版，减少在错误内容上的格式化成本。
- 后继：formatting。

#### 2.3.9 formatting：格式排版与风格统一

- 触发条件：writing、draft_confirmation 已完成。
- 输入：
  - `inputs["writing"]`；
  - style、output_format；
  - 针对 formatting 的修改意见。
- 执行逻辑：
  1. 规范连续空行和标题层级；
  2. 按目标格式转换：
     - markdown：保留规范化 Markdown；
     - html：转义正文并生成 h1/h2/p 和 UTF-8 页面；
     - json：输出 title、style、content_markdown；
     - text：移除 Markdown 标题标记；
  3. 不新增事实或证据。
- 输出：
  - `artifact_type="formatted_draft"`；
  - 对应格式的完整内容；
  - 元数据：格式和风格。
- 后继：`pre_review_confirmation`。

#### 2.3.10 pre_review_confirmation：终稿审核前确认

- 触发条件：formatting 已完成。
- 业务含义：用户确认排版后的完整候选稿，再执行最终质量审核。
- 输入/输出及确认规则与其他确认节点相同。
- 后继：review。

#### 2.3.11 review：质量审核与润色

- 触发条件：research、evidence_governance、outline、pressure_test、formatting、
  pre_review_confirmation 均已完成。
- 输入：
  - `inputs["research"]`、`inputs["evidence_governance"]`、`inputs["outline"]`、
    `inputs["pressure_test"]`、`inputs["formatting"]`；
  - expected_length、output_format；
  - 针对 review 的修改意见。
- 执行逻辑：
  1. 检查内容非空、目标格式、来源数量；
  2. Markdown 检查一级标题；
  3. 检查正文是否达到目标篇幅的 75%；
  4. 无来源时保留风险说明，不补造引文；
  5. 按格式安全地附加审核反馈。
- 当前限制：outline 虽作为精确输入传入，但内置 ReviewSkill 尚未使用它执行大纲一致性检查；
  该输入为后续增强和自定义审核 Skill 保留。
- 输出：
  - `artifact_type="final_report"`；
  - 终稿正文；
  - 元数据：`quality_passed`、`issues`、`checks`。
- 后继：quality_gate。

#### 2.3.12 quality_gate：D1–D7 发布质量门

- 触发条件：evidence_governance、pressure_test、review 均已完成。
- 输入：证据账本、独立压力测试和终稿。
- 执行逻辑：
  1. 汇总证据红线；
  2. 对事实准确性、逻辑严密性、事实观点分离、结构完整性、So What、边界感、量级感评分；
  3. 总分满分 35，默认通过线为 24；
  4. 任一红线或总分不足时作出 `block_release` 决定。
- 输出：`artifact_type="quality_gate"`，包含 passed、total_score、D1–D7、red_lines、
  problems、required_actions 和 decision。
- 通过：节点和工作流 completed，终稿可读取。
- 拒绝：评估产物仍被保存，节点和工作流 failed，抛出 `QualityGateRejected`，终稿读取被拒绝。

ReviewSkill 自身仍会生成 issues 元数据；最终发布权由 quality_gate 决定。

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

编排器会把最多 16 个相关向量分片放入 `SkillRequest.context`。当前九个内置离线 Skill
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

命令包括 `create`、`run`、`confirm`、`modify`、`status`、`final`。结构化结果使用 JSON，
可预期的 ValueError/KeyError/RuntimeError 写入 stderr 并返回退出码 2。

CLI 是薄适配层，不保存会话状态；所有恢复均依赖显式 workflow_id 和 data directory。

## 4. 断点修改与上下文生命周期

### 4.1 影响分析

`modify(workflow_id, target_node, feedback)` 从目标节点出发计算全部传递后代：

| 修改目标 | 主要失效范围 |
|---|---|
| research | 全部后续节点和确认 |
| issue_tree | 议题树及全部后代；保留 research |
| evidence_governance | 证据治理及下游；保留 research、issue_tree 和确认 |
| outline | outline 及其全部后代；保留上游证据成果 |
| writing | writing、pressure_test、初稿确认、formatting、终审前确认、review、quality_gate |
| pressure_test | pressure_test、初稿确认、review、quality_gate；不重跑 writing |
| formatting | formatting、终审前确认、review、quality_gate |
| review | review、quality_gate |
| quality_gate | 仅 quality_gate |

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

- 6 个测试全部通过；
- 20 个独立离线确定性工作流全部完成：20/20（测试阈值为 ≥95%）；该样本不代表外部模型、
  检索或生产环境 SLA；
- 105000 字目标端到端完成，终稿 105082 字；
- 进程重启后从大纲确认点恢复；
- 三个确认门全部验证；
- 修改 writing 后仅重跑后代，research 和 outline 产物 ID/执行次数不变；
- 旧 writing 向量失活，查询只返回新产物；
- Markdown、HTML、JSON、纯文本路径通过；
- Python 编译、包构建和 CLI 入口通过。

### 6.2 十万字离线性能基线（单次手工测量，N=1）

独立临时测量程序在同一环境创建一个全新 data directory，依次执行 create、三次
run/confirm 和最终 run，再使用 `time.perf_counter()`、`resource.getrusage()`、文件
`stat()` 采集结果。它不是 6 个 unittest 的计时，也尚未纳入 CI 基准脚本：

| 指标 | 结果 |
|---|---:|
| 目标篇幅 | 105000 字符 |
| 最终报告 | 105082 字符 |
| 端到端处理耗时 | 0.5446 秒 |
| 峰值 RSS | 33396 KiB（约 32.6 MiB） |
| state.db | 57344 bytes（约 56 KiB） |
| vectors.db | 598016 bytes（约 584 KiB） |
| 确认节点 | 3 个，全部按序命中 |
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

10. **配置创建后不能就地修改**
    - 风险：风格或篇幅变化必须新建工作流，不能复用已验证上游成果。
    - 优化：参数到节点的影响映射；例如仅改输出格式时从 formatting 开始失效。

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
