---
name: writing_standards
description: 按技术、行业投研、公众号、官方内参场景匹配并固化版本化写作规范。
license: MIT
version: 1.0.0
---

# Writing Standards

独立实现：`research_workflow.skills.writing_standards.WritingStandardsSkill`。

输入 `requirements_analysis`，从 `standards.db` 解析一个活动 Profile，输出
`artifact_type="writing_standard"`。Profile 必须包含适用场景、调用触发词、结构、引用、
术语/数据/版式规则、禁止项、依据来源和版本。

## 场景

- `technical_arxiv`：摘要、引言、相关工作、方法、实验、结果、局限、结论；公式使用
  LaTeX，术语首现定义，披露数据集、基线、指标、消融和不确定性。arXiv 是预印本平台，
  不是统一文体标准；结构参照同领域论文，投稿格式服从目标会议/期刊。
- `industry_investment`：产业链、供需、竞争、盈利、估值、催化、风险闭环。细分领域前三
  券商参照必须带榜单来源、日期、报告链接和擅长领域；没有证据时标记
  `verification_required`，不得硬编码“前三”。
- `wechat_public_account`：标题信息增量、前100字钩子、移动端节奏、互动、版权和多媒体
  替代文本。蓝V参照必须记录主页、样文、认证状态和核验日期。
- `official_internal`：依据《党政机关公文处理工作条例》和GB/T 9704-2012判定文种、
  行文和版式；企业内参另标版本、阅读范围和责任人。

## 持久化与一键调用

内置和个性化 Profile 存入 `standards.db`，保留不可变版本。`profile.id` 是一键调用键；
通过 `extra.writing_standard_profile` 精确选择，或按触发词自动匹配。个性化 Profile
必须通过编排器注册，禁止 Skill 在执行中静默改写规范。

## 安全红线

`秘密/机密/绝密` 内容禁止发送至外部飞书或公共模型。`internal` 写入飞书必须同时确认
目标租户和数据驻留审批。密级标注不代表系统已取得处理涉密信息的资质。
