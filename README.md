# Northstar Research Workflow

可持久化、可恢复、可选择性重跑的研究报告 Skill 工作流。系统维护一个主编排 Skill 和十八个
名称与 DAG 完全一致的可执行 Skill，覆盖能力遍历、第三方 Skill 研究、需求、议题树、大纲、
产业/学术/实景三支柱调研、证据治理、
论断账本与数据锚点评分、素材映射、6–10 项可视化、写作、引用管理、压力测试、复核、
发布阻断、交付和受控自进化。
输出支持 Markdown、网页、飞书、JSON、纯文本，并通过 DocumentRenderer 适配 Word/PDF；
未配置真实渲染器时不会伪报二进制导出成功。
Quick/Standard/Deep/Regulatory Profile分别提供1/2/4/4次确认；生产调研可注入
CompositeSourceRetriever、OpenAlex和组织授权的产业/社媒Provider。

```bash
python3 -m pip install -e .
research-workflow create --topic "生成式人工智能治理" --length 8000 \
  --format markdown --audience "企业管理层" --sources-json sources.json
```

`sources.json` 必须提供 `sources` 数组；发布至少需要 industry、academic、social_media 三类
来源及各自原始 URL。没有生产检索适配器时，缺失类别会被质量门阻断而不是生成伪来源。

`run` 会依次停在 `issue_tree_confirmation`、`outline_confirmation`、`draft_confirmation` 和
`pre_review_confirmation`；确认后用同一 workflow ID 继续。

文档：

- [工作流运行流程、核心功能、运维与风险说明](docs/WORKFLOW_RUNTIME_GUIDE.md)
- [开源 Skill 与工具筛选目录](docs/OPEN_SOURCE_SKILL_CATALOG.md)
- [Skill 唯一清单与数量口径](docs/SKILL_INVENTORY.md)
- [架构与长上下文设计](docs/ARCHITECTURE.md)
- [API、Skill 接口与调用指南](docs/API.md)
- [部署手册](docs/DEPLOYMENT.md)
- [组件筛选与修改日志](docs/MODIFICATION_LOG.md)
- [测试报告](docs/TEST_REPORT.md)
- [主编排 Skill 与完整 Prompt](skills/research_report_orchestrator/SKILL.md)

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

项目采用 [MIT License](LICENSE)。内置实现不会访问互联网或编造检索结果；生产部署可通过
标准 `TextGenerator`/`Skill` 接口接入模型、检索服务和远程 Skill。
