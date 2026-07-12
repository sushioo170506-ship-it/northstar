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

### research-report-orchestrator 1.0.0

- 新增固定 DAG、三个人工确认门、全局配置持久化。
- 新增节点输入/输出/尝试/错误状态和用户操作审计。
- 新增传递后代分析、选择性失效、断点恢复和 checksum 校验。

### topic-research 1.0.0

- 新增主题五维拆解、用户来源标准化、资料缺口标记。
- 新增可替换 `TextGenerator` 边界；离线模式禁止虚构来源。

### outline-design 1.0.0

- 新增章节稳定 ID、篇幅预算、论证目的和证据需求。

### content-writing 1.0.0

- 新增按章节增量写作、来源/资料缺口标记和用户反馈应用。
- 支持 500000 字配置上限，避免依赖单次模型上下文。

### format-style 1.0.0

- 新增 Markdown、HTML、JSON、纯文本输出和格式别名。

### quality-review 1.0.0

- 新增长度、标题、来源和格式检查；审核元数据与终稿分离。

### issue-tree 1.0.0

- 新增 3–7 个可证据回答的子问题、假设和证据需求。
- 新增强制 `issue_tree_confirmation` 人工确认节点。

### evidence-governance 1.0.0

- 新增来源可追溯性、发布时间、利益相关性和独立验证账本。
- 新增编造来源、关键来源不可追溯、单一利益相关方支撑红线。

### pressure-test 1.0.0

- 新增逻辑、证据、反方论证、完整性四类独立审计和修复清单。
- 压力测试作为独立产物，不将自我审查混入初稿。

### quality-gate 1.0.0

- 新增 D1–D7 共 35 分评分，默认 24 分通过线。
- 新增红线和低分发布阻断；拒绝结果持久化并抛出 `QualityGateRejected`。

### requirements-analysis 1.0.0

- 新增产出形态、主题、文风、受众、篇幅、格式、边界、资料和前置思考九类需求抽取。
- ReportConfig 新增 output_type、audience、content_boundaries、prior_thoughts。

### material-integration 1.0.0

- 新增来源到最终大纲章节的 issue_id 映射和素材挂载覆盖率。
- 每项素材保留来源类别、原始 URL、正文和预期用途。

### visualization 1.0.0

- 新增 Mermaid 多层级议题图和 Vega-Lite 来源类别/量化素材图。
- 可视化作为版本化 JSON 产物进入写作、压力测试和复核。

### 既有 Skill 标准流程升级

- issue-tree 改为消费需求简报，增加二级问题、必要性、价值和排除项。
- outline 移至调研前并绑定最终议题树及需求对齐信息。
- research 移至大纲确认后，新增 SourceRetriever 和三类来源覆盖摘要。
- evidence-governance 新增原始链接及来源类别覆盖率。
- writing 新增章节素材、原始 URL 引用和可视化嵌入。
- pressure-test/review/quality-gate 新增三类来源、URL、素材、可视化和需求边界检查。
- research/evidence-governance/pressure-test 的模型输出改为辅助分析，确定性来源指标和红线
  不能被模型 JSON 覆盖。
- quality-gate 根据 issue_ids 重算素材挂载率，并硬性检查可视化和正文篇幅上下限。
- orchestrator 新增加权关键词 `request_revision` 精确退回规则，处理混合修改意图。

## 存储实现

- `state.db`：关系事务状态及 16384 字符无损产物分片。
- `vectors.db`：512 维确定性稀疏哈希嵌入、2000 字符检索分片和元数据过滤。
- 两个存储均为自研标准库实现，无第三方代码或依赖。
