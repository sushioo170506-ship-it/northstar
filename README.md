# Northstar Research Workflow

可持久化、可恢复、可选择性重跑的研究报告 Skill 工作流。系统包含一个主编排 Skill 和九个
低耦合功能 Skill，提供四个人工确认门、证据治理、独立压力测试、D1–D7 质量阻断、关系库与
向量库混合上下文、十万字级分片处理及完整审计记录。

```bash
python3 -m pip install -e .
research-workflow create --topic "生成式人工智能治理" --length 8000 --format markdown
```

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
