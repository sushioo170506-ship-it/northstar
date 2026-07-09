# 研究报告工作流（Wcget）

基于 Cursor Rules 的完整版研究报告自动生成工作流。

**试跑主题**：Mythos5 模型调研报告

## 目录结构

```
.cursor/rules/                 # Cursor 可发现的规则（Skill）— 放在仓库根
  wcget.mdc                    # 主编排器 ✅
  wcget-outline.mdc … build    # 子 Skill（占位 → 逐步填充）
research-workflow/
├── templates/                 # 固定输出模板
├── output/                    # 每次跑报告的产物
│   ├── research_data.md
│   ├── report.md
│   ├── report.html
│   ├── figures/
│   └── figures_png/
└── README.md
```

## 六步流水线

| Step | 规则文件 | 职责 | 产出 |
|------|---------|------|------|
| 1 | `wcget-outline.mdc` | 可争论大纲 | 对话中输出大纲 |
| 2 | `wcget-data.mdc` | 三支柱数据采集 | `output/research_data.md` |
| 3 | `wcget-process.mdc` | 多维评分 | 追加写入 `research_data.md` |
| 4 | `wcget-write.mdc` | 撰写正文 | `output/report.md` |
| 5 | `wcget-figure.mdc` | 生成图表 | `output/figures/*.svg` |
| 6 | `wcget-build.mdc` | 组装终稿 | `output/report.html` + PNG |

主编排器：`wcget.mdc`（只调度，不干活）

## 怎么用

在 Cursor Agent 中输入：

```
按 Wcget 工作流，生成主题「Mythos5 模型调研报告」的完整研究报告。
从 Step 1 开始，逐步执行，每步通过质量卡口后再进入下一步。
```

## 落地进度

- [x] 阶段 0：目录骨架 + 模板空壳
- [x] 节点 1：主编排器 `wcget.mdc`
- [x] 节点 2：大纲 Skill `wcget-outline.mdc`（五步构建法全文）
- [ ] 节点 3：数据 Skill
- [ ] 节点 4：评分 Skill
- [ ] 节点 5：正文 Skill
- [ ] 节点 6：图表 Skill
- [ ] 节点 7：组装 Skill
