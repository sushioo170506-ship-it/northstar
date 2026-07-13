# 部署手册

## 本地/单容器

要求 Python 3.11+，运行时无第三方依赖。

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e ".[office]"
research-workflow --help
```

将 `--data-dir` 指向持久卷。目录中 `state.db` 保存关系状态，`vectors.db` 保存向量上下文，
`standards.db`保存版本化写作Profile与应用记录；三者均启用 WAL。备份时应同时备份数据库及其 WAL 文件，或在停止写入后使用 SQLite backup
API。目录包含用户研究资料，必须启用磁盘加密、最小权限和备份访问审计。

## 模型与外部检索

默认实现离线可运行，不会假装已访问互联网。生产环境通过 `TextGenerator` 注入模型调用，
通过 `extra.sources` 或 `SourceRetriever` 注入检索结果。发布至少需要 industry、academic、
social_media 三类来源，且每项必须有原始 URL。可选 Crawl4AI、GPT Researcher、Docling、
Semantic Scholar、Mermaid、Vega-Lite 和 Pandoc 适配边界见开源目录。密钥由部署平台的 Secret 注入，
不得写入配置、操作日志或产物元数据。

HTML可使用内置文本格式路径；飞书/Word/PDF必须部署DocumentRenderer。飞书应用至少申请
`docx:document`、`docx:document.block:convert`、`sheets:spreadsheet`，个人空间优先使用
OAuth `user_access_token`，组织自动化可用受限`tenant_access_token`。Secret只由部署平台注入。
飞书完整配置和真实租户验收见`WRITING_STANDARDS_AND_FEISHU.md`。

专业Word和PPTX使用可选`office`依赖（python-docx、python-pptx）；HTML Slides无额外运行时。
HTML Slides由工作流直接输出单个`.html`，使用`research-workflow export WORKFLOW_ID report.html`
落盘，不要求ZIP、Node、CDN或构建步骤。
私有报告不允许公开托管时，使用`output_format=slides`（映射`slides_zip`）并导出`.zip`；
发布清单固定`delivery_link_policy=file_only`且禁止Cursor预览链接。只有调用方明确选择
`slides_html`时才直接交付单HTML。
个人飞书测试使用`FeishuOAuthClient`获取`user_access_token`，支持开发者免审调试的权限无需
发布正式应用；正式版和不支持免审的权限仍须企业管理员审批。

飞书群聊调用使用：

```bash
research-workflow-feishu-bot --host 127.0.0.1 --port 8080 \
  --data-dir ./report-data
```

开放平台事件地址为`https://<domain>/feishu/events`，订阅
`im.message.receive_v1`；服务端必须设置`FEISHU_VERIFICATION_TOKEN`并由HTTPS网关反向代理。
机器人命令、消息权限和安全边界见`WRITING_STANDARDS_AND_FEISHU.md`第6节。

生产检索通过CompositeSourceRetriever组合Provider。仓库自带OpenAlex学术Provider；产业、
arXiv与Crossref无密钥Provider；产业、金融和社媒Provider必须使用组织授权API。Provider应设置
超时、限流和缓存。所有返回内容由source_snapshot冻结原文、抓取时间、Provider和SHA-256，
再由claim_verification完成原文片段、数字、独立来源与冲突硬验证。

根据任务风险选择Profile：quick 2次确认，standard 3次，deep/regulatory 5次；所有Profile
都必须在排版前确认最终输出格式。监管、投资
和高风险报告不得由调用方偷偷降为quick；API层应按角色限制Profile。

## 多实例

内置 SQLite 适合单写者，不支持跨主机协调。水平扩展时实现同等 StateStore/VectorStore
接口，推荐 PostgreSQL（事务状态）和 pgvector/Qdrant（语义索引），并增加：

1. `(workflow_id, node_id)` 租约和幂等键；
2. outbox 或事务事件保证产物与索引最终一致；
3. 对象存储承载超大分片，数据库保存 URI 和 checksum；
4. 租户隔离、静态/传输加密、保留期和删除策略；
5. Skill 服务版本固定、超时、重试、熔断和可观测性。

## 运维检查

- 每次发布运行 `python3 -m unittest discover -s tests -v`。
- 定期对产物执行 checksum 全量巡检。
- 监控 failed/running 超时节点、确认等待时长、索引滞后和数据库大小。
- 仅在备份验证成功后清理历史不可变产物。
