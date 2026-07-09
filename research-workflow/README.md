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
- [ ] `wcget-data` 数据
- [ ] `wcget-process` 评分/数据处理
- [ ] `wcget-write` 正文
- [ ] `wcget-figure` 图表
- [ ] `wcget-build` 报告组装
- [ ] 端到端试跑（Mythos5）
