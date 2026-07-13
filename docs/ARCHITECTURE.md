# 研究报告工作流架构

## 组件

- 主编排器：固定 DAG、确认门、依赖分析、状态恢复、Skill 注册。
- 配置中心：`ReportConfig` 校验并冻结主题、篇幅、风格、格式和扩展参数。
- Profile中心：Quick/Standard/Deep/Regulatory控制确认点和质量阈值。
- Provider层：CompositeSourceRetriever组合OpenAlex及组织产业/金融/社媒数据源。
- 写作标准库：`standards.db` 保存四类内置Profile、个性化版本、触发词和应用审计。
- Renderer层：DocumentRenderer隔离Pandoc、专业Word、PPTX、HTML Slides及飞书远程发布。
- 关系存储：SQLite WAL 保存工作流、节点运行、输入/输出 ID、分片产物、确认和用户操作。
- 向量存储：独立 SQLite WAL 数据库保存 2000 字符分片、200 字符重叠、稀疏哈希向量及
  元数据；查询先按 workflow/node/type 精确过滤，再做相似度排序。
- 二十三个可执行 Skill：能力遍历、需求、Skill研究、写作标准、议题树、大纲、场景化调研、
  来源快照、证据治理、数据处理、逐论断验证、量化金工校验、素材整合、可视化、写作、引用、内容优化、
  压力测试、排版、审核、质量门、发布和
  自进化；`research_report_orchestrator`主编排Skill不计入DAG执行节点。

关系库是执行状态的唯一事实来源；向量库只负责相关上下文召回。完整依赖产物通过产物
ID 从关系库无损读取，向量召回不替代精确依赖，因此不会因 top-k 丢失必要输入。

## DAG 与影响范围

```text
capability_sweep -> requirements_analysis -> skill_research -> writing_standards
  -> issue_tree -> [确认主题与议题树]
  -> outline -> [确认大纲] -> research(场景化来源pass) -> source_snapshot
  -> evidence_governance -> data_processing -> claim_verification
  -> quant_finance_research
  -> material_integration -> visualization
  -> writing -> citation_management -> content_optimization -> pressure_test
  -> [确认初稿] -> formatting
  -> [审核前确认] -> review -> quality_gate -> publish -> experience_evolution -> completed

精确依赖补充：
outline              <- requirements_analysis + issue_tree
skill_research       <- requirements_analysis
writing_standards    <- requirements_analysis + skill_research
research             <- requirements_analysis + issue_tree + confirmed outline
source_snapshot      <- research + writing_standards + outline
data_processing      <- source_snapshot + evidence_governance + issue_tree + outline
claim_verification   <- data_processing + source_snapshot + evidence_governance + outline
quant_finance_research <- claim_verification + data_processing + source_snapshot + writing_standards
material_integration <- outline + research + evidence_governance + data_processing
visualization        <- issue_tree + material_integration + data_processing
citation_management  <- writing + evidence_governance + material_integration
content_optimization <- citation_management + writing_standards
review               <- requirements + writing_standards + research + evidence + processed data + materials + visuals + pressure + formatting
quality_gate         <- capability + requirements + writing_standards + evidence + processed data + materials + visuals + pressure + review
publish              <- capability + writing_standards + visuals + review + quality_gate
experience_evolution <- user operations + skill_research + quality_gate + publish
```

修改节点时，编排器计算传递后代。例如修改 `writing` 只失效 writing、citation_management、
content_optimization、pressure_test、
draft_confirmation、formatting、pre_review_confirmation、review、quality_gate、publish；research、
issue_tree、evidence_governance、material_integration、visualization 和 outline 的产物 ID 保持不变。
旧产物不删除，便于审计或版本比较。

## 一致性与恢复

每个节点依次经历 `running -> completed`；异常进入 `failed`。产物先分片落库并建立向量索引，
随后节点才写入输出 ID。进程中断后，重新构造编排器并用相同 data directory 调用 `run()`；
completed 节点跳过，failed/running 节点安全重试。读取产物时重新计算 SHA-256。

当前单机实现使用三个独立 SQLite 数据库，适合本地和单副本容器。多实例部署时应保持接口，
将状态库替换为 PostgreSQL、向量库替换为 pgvector/Qdrant，并为节点执行增加租约或分布式锁。
本项目没有把单机 SQLite 描述成真正的分布式存储。

## 长上下文策略

1. 原始产物按 16384 字符无损分片，读取时按序增量拼接并校验 checksum。
2. 检索副本按 2000 字符、200 重叠分片，避免跨边界语义丢失。
3. 依赖内容按 ID 精确加载；辅助历史上下文按元数据过滤和相似度 top-k 加载。
4. Skill 可进一步按章节调用模型，避免一次传入十万字。

“100% 调取”限定为必需依赖产物的 ID 精确读取和 checksum 验证；语义检索本身是排序算法，
不能严谨承诺对任意自然语言查询达到 100% 召回率。
