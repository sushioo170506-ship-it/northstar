# Skill 选型与修改日志

## 开源组件筛选

2026-07-12 检查了仓库已有远程分支中从 OpenClaw Hub 获取的候选：

| 候选 | 版本 | 结论 |
|---|---:|---|
| anisafifi/academic-research-hub | 0.1.0 | `SKILL.md` 明示 Proprietary，不复制或修改 |
| kaisersong/kai-report-creator | 1.23.3 | 快照未附可确认的源码许可证，不复制 |
| teamolab/academic-writing | 1.0.0 | 快照未附可确认的源码许可证，不复制 |
| nitishgargiitd/data-cog | 快照版本 | 快照未附可确认的源码许可证，不复制 |

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

## 存储实现

- `state.db`：关系事务状态及 16384 字符无损产物分片。
- `vectors.db`：512 维确定性稀疏哈希嵌入、2000 字符检索分片和元数据过滤。
- 两个存储均为自研标准库实现，无第三方代码或依赖。
