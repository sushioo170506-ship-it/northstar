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

## 结构化产物最低要求
- 每个章节至少包含两类内容块中的一种：
  - `key_points.md`（3-8条要点）
  - 结构化表格（csv/md）
  - 图表规格（mermaid 或绘图脚本）
- 长篇详实报告建议下限：
  - 表格 >= 6
  - 图表规格 >= 3
  - 含证据映射文件 `processed_data/evidence_map.csv`
    - 字段：`section,evidence_id,claim_id,strength`

## 加工动作
1. **信息归位**：将素材按章节分配到 `section_X/`。
2. **表格化**：将参数、benchmark、竞品对比转成统一表格。
3. **提炼要点**：将长段落压缩为 3-5 条可写 bullet points。
4. **生成图表**：按大纲生成柱状图、雷达图、架构图、时间线等。
5. **缺失检测**：输出 `gaps.md`，逐章标明 `齐全/待补/缺失`。

## 缺失分级规则（新增）
- P0（严重缺失）：关键章节无核心数据或无可追溯来源 -> 必须回退 Step 3
- P1（重要缺失）：有数据但对标不完整 -> 可继续但必须在报告显式声明
- P2（一般缺失）：补充材料不足，不影响主结论 -> 记录即可

## 质量卡口
- 所有素材已按章节归位。
- 关键参数/分数已表格化。
- 长篇论文描述已提炼为要点。
- 大纲标注图表已生成，或标注“因数据不足暂缺”。
- `gaps.md` 已完成且描述清晰。
- 若章节素材严重缺失：必须回退 Step 3 补采。
- `evidence_map.csv` 已生成，结论可追踪到证据。
- 若表图数量低于大纲门槛，必须回退补加工。

## 交接
将 `archive/processed_data/` 交给 `mr-step5-write`。

