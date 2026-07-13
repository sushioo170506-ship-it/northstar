# 开源 Skill 与工具筛选目录

检查日期：2026-07-13。星数仅是采用度信号，不等于质量保证；许可证和维护状态优先。当前
交付采用“适配器目录”而非复制第三方源码，运行时仅在部署方显式配置后调用。

## 已纳入能力目录

| 项目 | 原作者/组织 | 原始版本快照 | Stars | 原许可证 | 来源地址 | 接入方式 |
|---|---|---|---:|---|---|---|
| Crawl4AI | unclecode | v0.9.1 | 72,391 | Apache-2.0 | https://github.com/unclecode/crawl4ai | SourceRetriever/web-to-Markdown |
| Docling | docling-project | main@2026-07-12 | 63,028 | MIT | https://github.com/docling-project/docling | 文档解析适配器 |
| GPT Researcher | assafelovic | v3.5.1 | 28,264 | Apache-2.0 | https://github.com/assafelovic/gpt-researcher | Deep Research provider |
| Semantic Scholar Skill | Agents365-ai | v0.8.1 | 53 | MIT | https://github.com/Agents365-ai/semanticscholar-skill | 学术 pass |
| Orchestra AI Research Skills | Orchestra-Research | v1.7.2 | 10,628 | MIT | https://github.com/Orchestra-Research/AI-Research-SKILLs | AI 主题条件 Skill |
| K-Dense Scientific Agent Skills | K-Dense-AI | v2.53.0 | 30,726 | 顶层 MIT；子 Skill 单独核验 | https://github.com/K-Dense-AI/scientific-agent-skills | 仅加载许可兼容子 Skill |
| Mermaid | mermaid-js | develop@2026-07-12 | 89,188 | MIT | https://github.com/mermaid-js/mermaid | 图/架构渲染 |
| Vega-Lite | vega | main@2026-07-12 | 5,404 | BSD-3-Clause | https://github.com/vega/vega-lite | 统计图渲染 |
| Pandoc | jgm/John MacFarlane | main@2026-07-12 | 45,344 | GPL-2.0 | https://github.com/jgm/pandoc | 仅外部 CLI |
| MiniMax DOCX Skill | MiniMax-AI | main@2026-07-13 | 13,030 | MIT | https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-docx | 参考OOXML模板/校验方法；clean-room Python适配 |
| Frontend Slides | Zara Zhang（张咋啦） | main@2026-07-13 | 25,376 | MIT | https://github.com/zarazhangrui/frontend-slides | 参考单HTML、自包含和视觉发现；clean-room SlidesRenderer |
| Marp | marp-team | main@2026-07-13 | 12,172 | MIT | https://github.com/marp-team/marp | 可选CLI；PPTX/HTML多格式参照 |
| OpenClaw Deep Research Agent | MilleniumGenAI | main@2026-03-10 | 2 | MIT-0 | https://github.com/MilleniumGenAI/deep-research-openclaw-agent | claim-verified research |
| OpenClaw Deep Research Pro | parags | main@2026-02-03 | 7 | MIT | https://github.com/parags/deep-research-pro | 低优先级 fallback |

星数取 GitHub API 快照。目录保存在 `research_workflow.integrations.DEFAULT_INTEGRATIONS`，
每次运行由 capability_sweep 全量遍历并记录 configured/disabled/reviewed_not_configured。

`skill_research` 在 requirements_analysis 之后进一步按当前用户需求排序这些候选。启用
`live_skill_research` 时，它还会通过 GitHub Search API 检索新候选；OpenClaw Hub 或其他渠道
候选可通过结构化 `skill_candidates` 输入。所有候选均输出作者、来源、版本、许可证、渠道、
决策理由和修改清单。

GitHub 默认硬门槛为 500 Stars，OpenClaw Hub 为 300 Stars。目录中低于门槛的历史候选仍可
被遍历用于能力观察，但运行时 decision 为 `below_threshold`，不得进入适配草案。

## 未直接纳入

| 候选 | 原因 |
|---|---|
| Imbad0202/academic-research-skills | 37k+ Stars，但 CC BY-NC 4.0，不适合默认商业复用 |
| lingzhi227/agent-research-skills | 能力相关，但 GitHub API 未识别许可证 |
| ClawHub Research Cog | 依赖付费 credits/私有服务，不属于可随仓库部署的开源实现 |
| ClawHub Research Report Generator | 页面未提供可核验源码仓库/许可证 |
| 旧 academic-research-hub 快照 | 明示 Proprietary |
| kai-report-creator / academic-writing 快照 | 缺少可确认源码许可证 |
| 通用社媒 scraper | 维护、平台条款和账号风险高；优先官方 API/用户授权导出 |

## 外部能力调用政策

1. 所有目录项每次必须被遍历，但只有 configured 项实际执行。
2. 配置不等于成功：对应节点产物必须记录 provider、版本、请求范围、状态和错误。
3. 无认证、配额或许可证时结构化跳过，不得静默回退为伪数据。
4. 同功能多 provider 先并行采集、后统一去重治理，不把重复抓取计为独立验证。
5. 社媒必须遵守平台条款、隐私和删除要求；匿名帖子只能作 C/D 级辅助证据。
6. 第三方升级必须重新核验许可证、schema 和基准测试，禁止自动漂移到未验证版本。
