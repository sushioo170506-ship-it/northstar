# mr-step4-process

name: mr-step4-process  
description: Step 4 — 将原始素材加工为可直接写入报告的结构化内容块：归位、表格化、图表化、要点提炼、缺失检测。

## 作用
这是从“收集到的东西”到“能写进报告的东西”的转换层。

## 输入
- `archive/raw_data/`
- `archive/outline.md`

## 输出
写入 `archive/processed_data/`，推荐目录：

```text
processed_data/
├── section_1/
├── section_2/
├── section_3/
├── section_4/
├── section_5/
├── section_6/
├── section_7/
├── figures/
└── gaps.md
```

## 加工动作
1. **信息归位**：将素材按章节分配到 `section_X/`。
2. **表格化**：将参数、benchmark、竞品对比转成统一表格。
3. **提炼要点**：将长段落压缩为 3-5 条可写 bullet points。
4. **生成图表**：按大纲生成柱状图、雷达图、架构图、时间线等。
5. **缺失检测**：输出 `gaps.md`，逐章标明 `齐全/待补/缺失`。

## 质量卡口
- 所有素材已按章节归位。
- 关键参数/分数已表格化。
- 长篇论文描述已提炼为要点。
- 大纲标注图表已生成，或标注“因数据不足暂缺”。
- `gaps.md` 已完成且描述清晰。
- 若章节素材严重缺失：必须回退 Step 3 补采。

## 交接
将 `archive/processed_data/` 交给 `mr-step5-write`。

