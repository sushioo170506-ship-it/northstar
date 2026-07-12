# Skill 选型与修改日志

## 开源组件筛选

2026-07-12 检查了仓库已有远程分支中从 OpenClaw Hub 获取的候选：

| 候选 | 版本 | 结论 |
|---|---:|---|
| anisafifi/academic-research-hub | 0.1.0 | `SKILL.md` 明示 Proprietary，不复制或修改 |
| kaisersong/kai-report-creator | 1.23.3 | 快照未附可确认的源码许可证，不复制 |
| teamolab/academic-writing | 1.0.0 | 快照未附可确认的源码许可证，不复制 |
| nitishgargiitd/data-cog | 快照版本 | 快照未附可确认的源码许可证，不复制 |
| elysia-ball/Strategy-Analyst | main（2026-07-12 检查） | GitHub 未声明许可证；仅作能力对比，不复制文本或实现 |

许可证不明确不等于开源。为避免违反用户要求中的“保留原始开源协议”，本交付没有把上述
代码伪装为可复用开源组件，也没有复制其实现。所有提交代码为本项目 MIT 许可下的 clean-room
实现；候选仅用于能力边界调研。未来引入第三方 Skill 时，必须把原始 LICENSE、来源 URL、
精确版本和未修改源码一并放入 `vendor/`，在本文件逐项记录差异。

## 自研 Skill 变更

### research_report_orchestrator 1.0.0

- 新增固定 DAG、三个人工确认门、全局配置持久化。
- 新增节点输入/输出/尝试/错误状态和用户操作审计。
- 新增传递后代分析、选择性失效、断点恢复和 checksum 校验。

### research 1.0.0

- 新增主题五维拆解、用户来源标准化、资料缺口标记。
- 新增可替换 `TextGenerator` 边界；离线模式禁止虚构来源。

### outline 1.0.0

- 新增章节稳定 ID、篇幅预算、论证目的和证据需求。

### writing 1.0.0

- 新增按章节增量写作、来源/资料缺口标记和用户反馈应用。
- 支持 500000 字配置上限，避免依赖单次模型上下文。

### formatting 1.0.0

- 新增 Markdown、HTML、JSON、纯文本输出和格式别名。

### review 1.0.0

- 新增长度、标题、来源和格式检查；审核元数据与终稿分离。

### issue_tree 1.0.0

- 新增 3–7 个可证据回答的子问题、假设和证据需求。
- 新增强制 `issue_tree_confirmation` 人工确认节点。

### evidence-governance 1.0.0

- 新增来源可追溯性、发布时间、利益相关性和独立验证账本。
- 新增编造来源、关键来源不可追溯、单一利益相关方支撑红线。

### pressure-test 1.0.0

- 新增逻辑、证据、反方论证、完整性四类独立审计和修复清单。
- 压力测试作为独立产物，不将自我审查混入初稿。

### quality_gate 1.0.0

- 新增 D1–D7 共 35 分评分，默认 24 分通过线。
- 新增红线和低分发布阻断；拒绝结果持久化并抛出 `QualityGateRejected`。

### requirements_analysis 1.0.0

- 新增产出形态、主题、文风、受众、篇幅、格式、边界、资料和前置思考九类需求抽取。
- ReportConfig 新增 output_type、audience、content_boundaries、prior_thoughts。

### material_integration 1.0.0

- 新增来源到最终大纲章节的 issue_id 映射和素材挂载覆盖率。
- 每项素材保留来源类别、原始 URL、正文和预期用途。

### visualization 1.0.0

- 新增 Mermaid 多层级议题图和 Vega-Lite 来源类别/量化素材图。
- 可视化作为版本化 JSON 产物进入写作、压力测试和复核。

### 既有 Skill 标准流程升级

- issue_tree 改为消费需求简报，增加二级问题、必要性、价值和排除项。
- outline 移至调研前并绑定最终议题树及需求对齐信息。
- research 移至大纲确认后，新增 SourceRetriever 和三类来源覆盖摘要。
- evidence-governance 新增原始链接及来源类别覆盖率。
- writing 新增章节素材、原始 URL 引用和可视化嵌入。
- pressure_test/review/quality_gate 新增三类来源、URL、素材、可视化和需求边界检查。
- research/evidence-governance/pressure-test 的模型输出改为辅助分析，确定性来源指标和红线
  不能被模型 JSON 覆盖。
- quality_gate 根据 issue_ids 重算素材挂载率，并硬性检查可视化和正文篇幅上下限。
- orchestrator 新增加权关键词 `request_revision` 精确退回规则，处理混合修改意图。
- 所有 SKILL.md frontmatter `name` 与 Python `Skill.name`/DAG node 统一，消除双轨命名。

### capability_sweep 1.0.0

- 新增每轮内置 Skill 和外部集成目录全量遍历。
- 未配置/禁用能力必须结构化记录状态和原因，禁止静默跳过。

### data_processing 1.0.0

- 新增 claim ledger、数字提取、A+/A/B/C/D 分级、冲突与三角验证。
- 新增仅在 5–10 候选、4–6 锚定维度齐全时执行的数据评分；否则 not_applicable。

### publish 1.0.0

- 新增质量门后的独立发布节点和 publish manifest。
- 未配置渲染器时明确披露 Mermaid/Vega/Pandoc/PNG 限制，不伪报产物。

### 2026-07-12 开源能力目录

- 纳入 Crawl4AI、GPT Researcher、Docling、Semantic Scholar Skill、Orchestra Research
  Skills、K-Dense Scientific Skills、Mermaid、Vega-Lite、Pandoc 和两个 OpenClaw Deep
  Research 集成的元数据与适配边界。
- 未复制第三方源码；星数和许可证快照见 `docs/OPEN_SOURCE_SKILL_CATALOG.md`。
- official 类别兼容迁移为 industry，与 academic、social_media 构成三支柱。

### skill_research 1.0.0

- 新增按用户需求检索 GitHub、OpenClaw Hub 和结构化外部仓库候选的元技能。
- 新增 MIT/MIT-0/Apache-2.0/BSD 自动允许、GPL 外部进程、NC/专有/未知拒绝策略。
- 新增标准化二次改造草案，强制包含原作者、来源 URL、版本、许可证和逐项修改日志。
- 所有动态候选安装状态为 pending_human_review，禁止同一运行内执行远程代码。
- 新增 GitHub≥500、OpenClaw Hub≥300 星硬门槛；低于门槛统一 observe_only。

### Skill 清单统一

- 目录名、frontmatter name、Python Skill.name 和 DAG node 全部使用 canonical underscore 名称。
- 维护口径统一为 1 个主编排 Skill + 16 个可执行 Skill = 17 个 SKILL.md。

### 竞争性假说改为可选

- 删除 issue_tree 和 outline 的默认强制假说要求。
- 仅当 `extra.enable_competitive_hypotheses=true` 时生成和校验竞争性假说。
- 普通行业研究使用研究问题、情景条件和判断失效条件，不为满足模板强行设置假说。

### 输出、来源和复核规则增强

- 大纲新增 percentage，摘要默认约6%且硬上限8%。
- 新增 feishu、webpage别名和DOCX/PDF DocumentRenderer契约。
- social_media扩展微信公众号及国内外平台，并增加platform归一化。
- 风险章节按模型、ETF/基金、产业主题生成专属risk_scope。
- quality_gate新增章节级inline_source_coverage，文末链接不能替代正文内联。
- skill_research新增“名称/来源/功能/Stars/协议/结论”Markdown参考表。

### 优化建议落地

- 新增quick/standard/deep/regulatory Profile及差异化确认和质量阈值。
- 新增CompositeSourceRetriever与无密钥OpenAlexRetriever。
- 新增PandocDocumentRenderer，真实渲染DOCX/PDF并返回base64与MIME元数据。
- 新增节点评论与actor审计接口，评论不自动使产物失效。

### citation_management 1.0.0

- 新增正文内联来源、文末统一参考资料和双向跳转锚点。
- 支持GB/T 7714、APA、MLA、Chicago和numeric基础格式。
- quality_gate新增引用完整性硬检查。

### experience_evolution 1.0.0

- 新增用户修改/评论经验提取、分类、频次、置信度和有效性验证。
- validated_candidate须人工approved_by后才能写入Skill受控区。
- 新增季度自进化复盘，汇总工作流、提案、已验证候选和平均质量分。

## 存储实现

- `state.db`：关系事务状态及 16384 字符无损产物分片。
- `vectors.db`：512 维确定性稀疏哈希嵌入、2000 字符检索分片和元数据过滤。
- 两个存储均为自研标准库实现，无第三方代码或依赖。
