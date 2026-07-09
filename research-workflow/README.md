# 研究报告工作流（Wcget）

按知乎《研究报告工作流》思路在 Cursor 中落地：

**主 Skill 编排 → 再逐个完善子 Skill → 全部就绪后再用主题试跑。**

默认主题（试跑用，可改）：Mythos5 模型调研报告

## 搭建顺序（与文章一致）

```
① 主 Skill（Wcget）     ← 只编排，不写方法论
② outline 子 Skill
③ data 子 Skill
④ process 子 Skill（数据处理/评分）
⑤ write 子 Skill（正文）
⑥ figure 子 Skill（图表）
⑦ build 子 Skill（报告组装）
⑧ 用真实主题端到端试跑
```

## 目录

```
.cursor/rules/
  wcget.mdc                 # 主 Skill ✅
  wcget-outline.mdc         # ⏳ 占位
  wcget-data.mdc            # ⏳ 占位
  wcget-process.mdc         # ⏳ 占位
  wcget-write.mdc           # ⏳ 占位
  wcget-figure.mdc          # ⏳ 占位
  wcget-build.mdc           # ⏳ 占位
research-workflow/
  templates/                # 输出模板空壳
  output/                   # 跑报告时的产物
  output/_archive/          # 早期试跑归档（不参与编排）
  README.md
```

## 主 Skill 串联关系

```
大纲 → 数据 → 数据处理(评分) → 正文 → 图表 → 报告组装
```

每个子 Skill 相互独立；主 Skill 只负责顺序、传路径、卡口、回退。

## 怎么用（子 Skill 全部完善后）

```
按 Wcget 主 Skill 编排，主题：「Mythos5 模型调研报告」。
从 Step 1 起逐步执行；子 Skill 未完善则停止并提示。
```

## 落地进度

- [x] 主 Skill `wcget.mdc`（编排器）
- [x] `wcget-outline` 大纲（五步构建法 + 支持自定义骨架）
- [x] `wcget-data` 数据（三支柱七线 + 三角交叉验证 + 可信度分级）
- [x] `wcget-process` 评分/数据处理（数据锚点法：维度→赋分公式→未量产惩罚→6 条边界声明）
- [x] `wcget-write` 正文（语言宪法 + 数据三要素 + 刺点五段式 + 节奏映射）
- [x] `wcget-figure` 图表（类型决策树 + 视觉风格 + 表格 SVG + 6–10 张配置）
- [x] `wcget-build` 报告组装（HTML + PNG，按需 Word[公文/通用] + 飞书文档）
- [x] 端到端试跑（Mythos5）— 全格式产出，见下

## 端到端试跑产物（Mythos5，2026-07-09）

主题「Mythos5 模型调研报告」按 Step 1→6 完整跑通，所有格式产出：

| 产物 | 说明 |
|------|------|
| `output/outline.md` | Step 1 大纲（定刺：对中国团队 Mythos5 是地缘样本非可购 API） |
| `output/research_data.md` | Step 2 数据（33 数据点+交叉验证）+ Step 3 评分矩阵 |
| `output/report.md` | Step 4 正文（~3.5K 字，5 段首判断句，0 禁止词） |
| `output/figures/*.svg` | Step 5：5 图 + 2 表（SWE-Bench 对比/价格象限/雷达/时间线/排名） |
| `output/report.html` | Step 6：自包含 HTML，7 SVG 全内联 |
| `output/figures_png/*.png` | Step 6：7 张 PNG（2×） |
| `output/report.docx` | Step 6：Word 通用研报格式 |
| `output/report.gongwen.docx` | Step 6：Word 党政机关公文格式（GB/T 9704-2012） |
| `output/report.feishu.md` | Step 6：飞书可导入 Markdown（原生表格+待跟进块） |

复现：`python3 scripts/make_figures.py && python3 scripts/svg_to_png.py && python3 scripts/build_report.py && python3 scripts/build_feishu.py && python3 scripts/build_docx.py general && python3 scripts/build_docx.py gongwen`

> 依赖：`matplotlib cairosvg python-docx` + `fonts-noto-cjk`（PNG/图表）、`pandoc`/`libreoffice`（可选）。

> 六个子 Skill 均已按知乎原文全文落地；原文引用的外部工具（`nature-*` / `render_tables.py` / `build_html.py` / `svg2png.py`）在 Cursor 环境标注为「可选/可替换」，可由 Agent 用等价 Python 实现。
