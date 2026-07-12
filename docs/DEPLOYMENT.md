# 部署手册

## 本地/单容器

要求 Python 3.11+，运行时无第三方依赖。

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
research-workflow --help
```

将 `--data-dir` 指向持久卷。目录中 `state.db` 保存关系状态，`vectors.db` 保存向量上下文；
两者均启用 WAL。备份时应同时备份数据库及其 WAL 文件，或在停止写入后使用 SQLite backup
API。目录包含用户研究资料，必须启用磁盘加密、最小权限和备份访问审计。

## 模型与外部检索

默认实现离线可运行，不会假装已访问互联网。生产环境通过 `TextGenerator` 注入模型调用，
通过 `extra.sources` 或 `SourceRetriever` 注入检索结果。发布至少需要 industry、academic、
social_media 三类来源，且每项必须有原始 URL。可选 Crawl4AI、GPT Researcher、Docling、
Semantic Scholar、Mermaid、Vega-Lite 和 Pandoc 适配边界见开源目录。密钥由部署平台的 Secret 注入，
不得写入配置、操作日志或产物元数据。

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
