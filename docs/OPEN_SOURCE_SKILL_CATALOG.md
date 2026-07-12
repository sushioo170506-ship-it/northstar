# 开源 Skill 与工具筛选目录

检查日期：2026-07-12。星数仅是采用度信号，不等于质量保证；许可证和维护状态优先。当前
交付采用“适配器目录”而非复制第三方源码，运行时仅在部署方显式配置后调用。

## 已纳入能力目录

| 项目 | 检查时 Stars | 许可证 | 对应阶段 | 接入方式 |
|---|---:|---|---|---|
| Crawl4AI | 72,391 | Apache-2.0 | 产业网页采集 | 可选 SourceRetriever/web-to-Markdown |
| Docling | 63,028 | MIT | PDF/DOCX/PPTX/表格解析 | 可选文档解析适配器 |
| GPT Researcher | 28,264 | Apache-2.0 | 多源深度调研 | 可选 Research provider |
| Semantic Scholar Skill | 53 | MIT | 论文/引用图检索 | 学术 pass 适配器 |
| Orchestra AI Research Skills | 10,628 | MIT | AI 研究方法 | AI 主题条件 Skill |
| K-Dense Scientific Agent Skills | 30,726 | 顶层 MIT；子 Skill 单独核验 | 科学领域方法 | 仅加载许可证兼容子 Skill |
| Mermaid | 89,188 | MIT | 流程/架构图渲染 | visualization renderer |
| Vega-Lite | 5,404 | BSD-3-Clause | 统计图渲染 | visualization renderer |
| Pandoc | 45,344 | GPL-2.0 | 文档发布 | 仅外部 CLI，不复制/链接源码 |
| OpenClaw Deep Research Agent | 2 | MIT-0 | claim-verified research | OpenClaw 条件适配器 |
| OpenClaw Deep Research Pro | 7 | MIT | 无密钥轻量检索 | 低优先级 fallback |

星数取 GitHub API 快照。目录保存在 `research_workflow.integrations.DEFAULT_INTEGRATIONS`，
每次运行由 capability_sweep 全量遍历并记录 configured/disabled/reviewed_not_configured。

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
