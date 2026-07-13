# 研究报告工作流架构

## 组件

- 主编排器：固定 DAG、确认门、依赖分析、状态恢复、Skill 注册、条件节点跳过。
- 配置中心：`ReportConfig` 校验并冻结主题、篇幅、风格、格式和扩展参数。
- Profile中心：Quick/Standard/Deep/Regulatory控制确认点和质量阈值。
- Provider层：CompositeSourceRetriever组合OpenAlex及组织产业/金融/社媒数据源。
- 写作标准库：`standards.db` 保存场景 Profile、个性化版本、触发词和应用审计。
- Renderer层：DocumentRenderer隔离Pandoc、专业Word、PPTX、HTML Slides及飞书远程发布。
- 关系存储：SQLite WAL 保存工作流、节点运行、输入/输出 ID、分片产物、确认和用户操作。
- 向量存储：独立 SQLite WAL 数据库保存检索分片与稀疏哈希向量。
- 十二个可执行 Skill：需求分析（内含能力遍历）、写作标准（内含技能研究）、议题树、大纲、
  调研、证据流水线、数据处理、成文、排版、质量保障、发布、条件化经验进化；
  `research_report_orchestrator`主编排Skill不计入DAG执行节点。

## DAG 与影响范围

```text
requirements_analysis(内含 capability_sweep)
  -> writing_standards(内含 skill_research)
  -> issue_tree -> [确认议题树]
  -> outline -> [确认大纲]
  -> research -> evidence_pipeline -> data_processing
  -> compose(内含 material/visualization/writing/finalize/pressure)
  -> [确认初稿] -> formatting
  -> [审核前确认] -> quality_assurance(内含 quant/review/quality_gate)
  -> publish -> experience_evolution(条件) -> completed
```

修改节点时，编排器计算传递后代。例如修改 `compose` 只失效 compose、draft_confirmation、
formatting、pre_review_confirmation、quality_assurance、publish 与条件进化节点；
research / evidence_pipeline / outline 产物保持不变。

## 一致性与恢复

每个节点依次经历 `running -> completed`；异常进入 `failed`。产物先分片落库并建立向量索引，
随后节点才写入输出 ID。进程中断后，重新构造编排器并用相同 data directory 调用 `run()`；
completed 节点跳过，failed/running 节点安全重试。

## 长上下文策略

1. 原始产物按 16384 字符无损分片，读取时按序增量拼接并校验 checksum。
2. 检索副本按 2000 字符、200 重叠分片。
3. 依赖内容按 ID 精确加载；辅助历史上下文按元数据过滤和相似度 top-k 加载。
