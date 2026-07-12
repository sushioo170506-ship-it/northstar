# Northstar Research Workflow

可持久化、可恢复、可选择性重跑的研究报告 Skill 工作流。系统包含一个主编排 Skill 和十二个
低耦合功能 Skill，覆盖需求拆解、多层级议题树、大纲确认、三类来源调研、证据治理、章节素材
映射、可视化、写作、独立压力测试和 D1–D7 发布阻断，并提供四个人工确认门、长上下文存储及
完整审计记录。

```bash
python3 -m pip install -e .
research-workflow create --topic "生成式人工智能治理" --length 8000 \
  --format markdown --audience "企业管理层" --sources-json sources.json
```

`sources.json` 必须提供 `sources` 数组；发布至少需要 official、academic、social_media 三类
来源及各自原始 URL。没有生产检索适配器时，缺失类别会被质量门阻断而不是生成伪来源。

`run` 会依次停在 `issue_tree_confirmation`、`outline_confirmation`、`draft_confirmation` 和
`pre_review_confirmation`；确认后用同一 workflow ID 继续。

文档：

- [工作流运行流程、核心功能、运维与风险说明](docs/WORKFLOW_RUNTIME_GUIDE.md)
- [架构与长上下文设计](docs/ARCHITECTURE.md)
- [API、Skill 接口与调用指南](docs/API.md)
- [部署手册](docs/DEPLOYMENT.md)
- [组件筛选与修改日志](docs/MODIFICATION_LOG.md)
- [测试报告](docs/TEST_REPORT.md)
- [主编排 Skill 与完整 Prompt](skills/research-report-orchestrator/SKILL.md)

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

项目采用 [MIT License](LICENSE)。内置实现不会访问互联网或编造检索结果；生产部署可通过
标准 `TextGenerator`/`Skill` 接口接入模型、检索服务和远程 Skill。
