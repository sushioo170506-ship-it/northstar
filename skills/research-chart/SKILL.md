---
name: research-chart
description: 从已核验的 JSON 数据生成离线 SVG 研究图表。支持分组柱状图和多序列折线图；要求标题为结论句，并包含单位、时间范围和数据来源。
user-invocable: true
disable-model-invocation: false
metadata:
  openclaw:
    emoji: "📈"
    requires:
      bins: ["python3"]
---

# Research Chart

使用 `scripts/render_chart.py` 将结构化数据渲染为 SVG。脚本只使用 Python 标准库，不访问网络，也不上传数据。

## 输入数据

JSON 数组，每项必须包含：

```json
[
  {"x": "2024", "y": 18.2, "series": "A"},
  {"x": "2025", "y": 24.6, "series": "A"},
  {"x": "2024", "y": 15.1, "series": "B"},
  {"x": "2025", "y": 19.8, "series": "B"}
]
```

`series` 可省略，默认为单序列。

## 调用

```bash
python3 skills/research-chart/scripts/render_chart.py \
  --type line \
  --input data.json \
  --title "A 的增速连续两年高于 B" \
  --x-label "年份" \
  --y-label "市场份额（%）" \
  --source "来源：E012、E018；截至 2026-06-30" \
  --output output/topic/figures/market-share.svg
```

也可用 `--data` 传入行内 JSON。

## 图表选择

- `bar`：比较不同对象或离散时期。
- `line`：展示连续时间趋势。

图表不能表达关系时，使用 Markdown 表格或正文，不要强制作图。

## 规则

- 标题必须是图表所支持的结论句，而不是“市场份额图”之类标签。
- 数据必须来自证据台账或可复算分析结果。
- `--source` 必须包含来源证据 ID；时间敏感数据还要包含截止日期。
- Y 轴默认包含零点，禁止通过截断坐标轴夸大差异。
- 不生成 3D、饼图或双 Y 轴图。
- 图中不得包含机密数据，除非交付范围明确允许。
- SVG 生成后要核对数据标签与输入 JSON 一致。

