---
name: skill_research
description: 根据用户需求从 GitHub、OpenClaw Hub 和合规技能仓库发现、筛选并生成可审查的第三方 Skill 适配规范。
license: MIT
version: 1.0.0
---

# Skill Research

## 与 research 的区别

- `skill_research`：研究“有哪些第三方技能可复用”，属于元技能。
- `research`：研究报告主题的数据和资料，属于内容调研技能。

两者名称、输入、产物和 DAG 节点不得混用。

## WHEN / INPUT / OUTPUT

- WHEN：requirements_analysis 完成后、issue_tree 之前；每轮必跑。
- INPUT：requirements_brief、可选 live_skill_research、skill_candidates、
  max_adapted_skills。
- OUTPUT：`skill_research_report`，包含 query、candidates、adapted_skill_specs、
  reference_table、live_search_errors、policy、metrics。

## 检索渠道

1. GitHub：使用官方 Search API，按主题、产出类型、agent skills/SKILL.md 搜索并按采用度排序。
2. OpenClaw Hub：遍历已核验的 ClawHub/GitHub 对应目录；平台候选必须能回溯源码仓库。
3. 其他仓库：由部署方以 skill_candidates 显式传入，不接受无来源文本。

网络搜索默认关闭，避免每次普通报告引入速率和供应链风险；设置
`extra.live_skill_research=true` 才执行 GitHub 实时搜索。搜索失败必须记录 channel/error，
不能伪造候选。

## 合规决策

| 许可证 | 自动动作 |
|---|---|
| MIT / MIT-0 / Apache-2.0 / BSD-3-Clause | adapt_allowed |
| GPL | external_process_only，不复制或链接源码 |
| CC BY-NC / Proprietary / NOASSERTION | reject |
| 其他 | review_required |

GitHub Stars 仅用于排序，不代表安全或质量。许可证必须来自仓库元数据和 LICENSE 文件；子目录
Skill 可覆盖顶层许可证，需再次核验。

## 星标硬门槛

- GitHub：默认 `github_skill_min_stars=500`；
- OpenClaw Hub：默认 `openclaw_skill_min_stars=300`；
- 低于门槛或星数未知：decision=`below_threshold`，只进入观察名单；
- below_threshold 不得生成 adapted_skill_specs，即使许可证为 MIT；
- 其他合规仓库默认不套用上述两平台门槛，可由部署配置另行审核。

## 二次改造规则

允许候选会生成标准化适配草案，而不是立即执行远程代码：

1. 包装为 `SkillRequest -> SkillResult`；
2. 将隐式状态改为显式输入；
3. 增加超时、错误分类、幂等和审计；
4. 统一 artifact_type 并声明 DAG 位置；
5. 保留原作者、URL、版本、许可证和修改日志；
6. installation_status 固定为 pending_human_review。

## 必需溯源字段

每个候选和改造 Skill 必须记录：

- 原名称；
- 原作者/组织；
- 原始仓库或 Skill URL；
- 原版本、tag 或 commit；
- 原许可证；
- 渠道；
- Stars 快照及检查日期；
- 本项目修改点；
- 安装和审核状态。

缺少任一核心字段不得进入适配清单。

每次输出必须附 Markdown 专业组件表，至少包含 Skill 名称、来源地址、功能定位、Stars、
许可证和适配结论，供团队学习与人工审批。

## MUST NOT / 错误处理

- 不自动执行、安装或导入搜索结果；
- 不复制无许可证、非商业或专有内容；
- 不把 README 的许可证徽章当作子 Skill 最终许可证；
- 不以高星数绕过安全、维护性和接口审查；
- live 搜索失败时保留 curated/configured 结果并标记 partial；
- 候选 schema 或许可证冲突时节点 failed，退回 skill_research。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
