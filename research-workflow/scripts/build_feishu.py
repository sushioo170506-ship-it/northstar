#!/usr/bin/env python3
"""Wcget Step 6 — 生成飞书可导入的 Markdown（方式2，无 API 凭证时兜底）。
- 图表引用改指向 figures_png/*.png（飞书导入本地图片更稳）
- 评分表/决策表用原生 Markdown 表格（飞书导入转原生表格，可在线复核）
- 追加「待跟进问题」清单块，便于团队评论
说明：若已配置飞书开放平台凭证，应改用方式1（docx.v1 块）直接建云文档。
"""
import os, re

BASE = os.path.join(os.path.dirname(__file__), "..", "output")
MD = os.path.join(BASE, "report.md")
OUT = os.path.join(BASE, "report.feishu.md")

SCORE_TABLE = """
| 模型 | 编码 | 推理 | 生态 | 可用性 | 成本 | 综合 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|
| Fable/Mythos 5 | 10.0 | 10.0 | 10.0 | 2.5 | 1.0 | 6.1 |
| GPT-5.5 | 5.7 | 6.3 | 9.5 | 3.5 | 2.0 | 5.2 |
| Gemini 3.1 Pro | 4.8 | 6.0 | 8.5 | 3.0 | 2.5 | 4.7 |
| DeepSeek V4 Pro | 4.4 | — | 7.0 | 9.0 | 8.5 | 7.2 |
| Kimi K2.6 | 5.7 | 6.8 | 6.5 | 9.0 | 9.5 | 7.6 |
| GLM-5.1/5.2 | 5.7 | — | 7.0 | 9.5 | 9.0 | 7.9 |
| Qwen 3.6 | 4.8 | — | 7.5 | 9.0 | 9.0 | 7.6 |
"""

DECISION_TABLE = """
| 角色 | 推荐选型 | 理由 | 否决条件 |
|------|----------|------|----------|
| 模型厂商 | 补长程 Agent + 双轨制度 | 差距在 FrontierCode 长程工程 | 只追单次跑分 |
| 应用企业 | 国内旗舰为主链路 | 中文+合规+价格差 30–70 倍 | 把 Fable 设为唯一依赖 |
| 安全合规 | 断供演练 + 数据不出境 | 18 天停服 + 30 天留存 | 涉密数据流向 Mythos 级 |
| 投资研究 | 看长程+生态+可用性组合 | 单一跑分会误判座次 | 以某一基准绝对分排名 |
"""

FOLLOWUP = """
---

## 待跟进问题（团队可在此评论）

- [ ] 用我方真实任务集复测 Fable 5 vs GLM-5.2 / Kimi K2.6 的中文工程表现
- [ ] 核实 DeepSeek V4 Pro 官方最新定价（多源口径相差逾 2 倍）
- [ ] 出口管制是否会再次触发？评估对现有链路的断供风险
- [ ] 明确哪些敏感/涉密数据禁止流向 Mythos 级模型（30 天留存条款）
- [ ] 持续跟踪 Mythos 5 Trusted Access 是否对更多地区/行业开放
"""

def build():
    with open(MD, encoding="utf-8") as f:
        txt = f.read()
    # 图表引用：figures/xxx.svg -> figures_png/xxx.png
    txt = re.sub(r"\(figures/([^)]+?)\.svg\)", r"(figures_png/\1.png)", txt)
    # 评分表 / 决策表 PNG 引用后追加原生 Markdown 表格（便于在线编辑）
    txt = txt.replace(
        "![表1：七款模型五维评分矩阵（中国团队视角）](figures_png/table_01_score.png)",
        "**表1  七款模型五维评分矩阵（中国团队视角）**\n" + SCORE_TABLE)
    txt = txt.replace(
        "![表2：分角色决策表（场景 → 推荐 → 理由 → 否决条件）](figures_png/table_02_decision.png)",
        "**表2  分角色决策表**\n" + DECISION_TABLE)
    txt += FOLLOWUP
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(txt)
    print("Feishu Markdown ->", OUT)

if __name__ == "__main__":
    build()
