#!/usr/bin/env python3
"""Wcget Step 5 — 生成 Mythos5 报告的 SVG 图表与表格。
风格：色盲友好、无 3D、仅水平网格线、标题为学术结论句、含数据来源、文字可编辑。
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

# ---- 中文字体 ----
CJK = None
for cand in ["Noto Sans CJK SC", "Noto Sans CJK JP", "Noto Serif CJK SC", "WenQuanYi Zen Hei", "SimHei"]:
    for f in fm.fontManager.ttflist:
        if f.name == cand:
            CJK = cand
            break
    if CJK:
        break
plt.rcParams["font.sans-serif"] = [CJK] if CJK else ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "none"   # 文字可编辑
plt.rcParams["font.size"] = 11

OUT = os.path.join(os.path.dirname(__file__), "..", "output", "figures")
os.makedirs(OUT, exist_ok=True)

# 色盲友好配色
C_OVERSEAS = "#005AB5"   # 蓝：海外锚
C_DOMESTIC = "#DC3220"   # 橙红：国内
C_MID = "#994F00"        # 棕：海外中坚
GREY = "#666666"
SRC = "数据来源: Anthropic 官方 / DataCamp / SuperCLUE / NextFuture / Lushbinary（2026）"

def src_note(fig):
    fig.text(0.01, 0.01, SRC, fontsize=6, color=GREY, ha="left", va="bottom")

def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#000000"); ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_color("#000000"); ax.spines["bottom"].set_linewidth(0.8)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.4, color="#cccccc")
    ax.set_axisbelow(True)

# ---------- fig1: SWE-Bench Pro 分组柱状（结构分化） ----------
def fig1():
    models = ["Fable/\nMythos 5", "GPT-5.5", "Kimi\nK2.6", "GLM-5.1", "Gemini\n3.1 Pro", "Qwen\n3.6", "DeepSeek\nV4 Pro"]
    vals = [80.3, 58.6, 58.6, 58.4, 54.2, 54.0, 52.0]
    colors = [C_OVERSEAS, C_MID, C_DOMESTIC, C_DOMESTIC, C_MID, C_DOMESTIC, C_DOMESTIC]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    bars = ax.bar(range(len(models)), vals, color=colors, width=0.62)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.8, f"{v:.1f}", ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.axhspan(52, 58.6, color="#DC3220", alpha=0.07)
    ax.set_xticks(range(len(models))); ax.set_xticklabels(models, fontsize=8)
    ax.set_ylabel("SWE-Bench Pro 得分 (%)", fontsize=9)
    ax.set_ylim(0, 90)
    ax.set_title("Mythos 5 领先 22 分，但国内旗舰已挤入 58% 同一梯队", fontsize=12, fontweight="bold", pad=12)
    ax.annotate("国内梯队 52–58.6%", xy=(3.0, 70), fontsize=8, color="#DC3220", ha="center")
    style_ax(ax)
    src_note(fig)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(os.path.join(OUT, "fig1_swebench.svg"))
    plt.close(fig)

# ---------- fig2: 能力—价格 象限散点 ----------
def fig2():
    # name, SWE-Bench Pro, blended price (input+output)/2 USD/MTok
    # name, cap, price, color, (label_x, label_y) in data coords
    data = [
        ("Fable/Mythos 5", 80.3, 30.0, C_OVERSEAS, (12.0, 81.0)),
        ("GPT-5.5", 58.6, 17.5, C_MID, (19.0, 59.4)),
        ("Kimi K2.6", 58.6, 1.0, C_DOMESTIC, (1.25, 60.0)),
        ("GLM-5.1", 58.4, 1.05, C_DOMESTIC, (1.35, 57.0)),
        ("Qwen 3.6", 54.0, 1.0, C_DOMESTIC, (1.25, 54.3)),
        ("DeepSeek V4 Pro", 52.0, 1.5, C_DOMESTIC, (1.9, 51.8)),
        ("Gemini 3.1 Pro", 54.2, 12.0, C_MID, (13.5, 54.3)),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for name, cap, price, col, (lx, ly) in data:
        ax.scatter(price, cap, s=130, color=col, alpha=0.85, edgecolor="white", linewidth=1, zorder=3)
        ax.annotate(name, (price, cap), xytext=(lx, ly), fontsize=8, color="#222222")
    ax.set_xscale("log")
    ax.set_xlabel("blended 单价 (USD/百万 token，越左越便宜) — 对数轴", fontsize=9)
    ax.set_ylabel("SWE-Bench Pro (%)", fontsize=9)
    ax.set_title("为 22 分能力支付 30–70 倍价格：海外旗舰居右上，国内居左中", fontsize=12, fontweight="bold", pad=12)
    ax.axvspan(0.5, 3, color="#DC3220", alpha=0.06)
    ax.text(0.9, 49.5, "国内：够用·低价区", fontsize=8, color="#DC3220", ha="center")
    style_ax(ax)
    ax.xaxis.grid(False)
    src_note(fig)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(os.path.join(OUT, "fig2_price_capability.svg"))
    plt.close(fig)

# ---------- fig3: 雷达（多维对比） ----------
def fig3():
    dims = ["编码", "长程推理", "生态/成熟度", "真实场景\n可用性", "成本效率"]
    series = {
        "Fable/Mythos 5": ([10.0, 10.0, 10.0, 2.5, 1.0], C_OVERSEAS),
        "GLM-5.1/5.2": ([5.7, 6.0, 7.0, 9.5, 9.0], C_DOMESTIC),
        "Kimi K2.6": ([5.7, 6.8, 6.5, 9.0, 9.5], "#009E73"),
        "DeepSeek V4 Pro": ([4.4, 5.5, 7.0, 9.0, 8.5], "#CC79A7"),
    }
    N = len(dims)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6.6, 5.6), subplot_kw=dict(polar=True))
    for name, (vals, col) in series.items():
        v = vals + vals[:1]
        ax.plot(angles, v, color=col, linewidth=2, label=name)
        ax.fill(angles, v, color=col, alpha=0.08)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(dims, fontsize=9)
    ax.set_ylim(0, 10); ax.set_yticks([2,4,6,8,10]); ax.set_yticklabels(["2","4","6","8","10"], fontsize=7, color=GREY)
    ax.set_title("海外锚强在编码/推理/生态，国内旗舰强在可用性/成本", fontsize=12, fontweight="bold", pad=22)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12), fontsize=8, frameon=False)
    src_note(fig)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(os.path.join(OUT, "fig3_radar.svg"))
    plt.close(fig)

# ---------- fig4: 时间线 ----------
def fig4():
    events = [
        ("04-XX", "Mythos Preview\n经 Glasswing 发布"),
        ("06-09", "Fable 5 / Mythos 5\n双轨发布 $10/$50"),
        ("06-12", "美出口管制令\n全球下线（含本土）"),
        ("06-26", "US 批准部分\n恢复 Mythos"),
        ("06-30", "管制解除\nFable 07-01 全球恢复"),
    ]
    xs = [0, 2, 2.6, 4.2, 5]
    fig, ax = plt.subplots(figsize=(8.0, 3.4))
    ax.axhline(0, color="#000000", linewidth=1)
    for i, (d, label) in enumerate(events):
        col = "#DC3220" if d in ("06-12",) else ("#009E73" if d in ("06-30",) else C_OVERSEAS)
        ax.scatter(xs[i], 0, s=90, color=col, zorder=3)
        up = (i % 2 == 0)
        y = 0.5 if up else -0.5
        va = "bottom" if up else "top"
        ax.annotate(f"2026-{d}", (xs[i], 0), xytext=(xs[i], y*0.35), ha="center", va=va, fontsize=8, fontweight="bold")
        ax.annotate(label, (xs[i], 0), xytext=(xs[i], y), ha="center", va=va, fontsize=7.5, color="#333333")
    ax.annotate("← 18 天全球不可用 →", xy=(3.0, 0), xytext=(3.0, -0.9), ha="center", fontsize=8, color="#DC3220", fontweight="bold")
    ax.set_ylim(-1.3, 1.3); ax.set_xlim(-0.6, 5.6)
    ax.axis("off")
    ax.set_title("发布 3 天即被关停 18 天：Mythos/Fable 5 的可用性是政策变量", fontsize=12, fontweight="bold", pad=6)
    src_note(fig)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(os.path.join(OUT, "fig4_timeline.svg"))
    plt.close(fig)

# ---------- fig5: 综合评分排名（横向条形） ----------
def fig5():
    data = [("GLM-5.1/5.2", 7.9, C_DOMESTIC), ("Kimi K2.6", 7.6, C_DOMESTIC),
            ("Qwen 3.6", 7.6, C_DOMESTIC), ("DeepSeek V4 Pro", 7.2, C_DOMESTIC),
            ("Fable/Mythos 5", 6.1, C_OVERSEAS), ("GPT-5.5", 5.2, C_MID),
            ("Gemini 3.1 Pro", 4.7, C_MID)]
    data.sort(key=lambda x: x[1])
    names = [d[0] for d in data]; vals = [d[1] for d in data]; cols = [d[2] for d in data]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.barh(range(len(names)), vals, color=cols, height=0.6)
    for i, v in enumerate(vals):
        ax.text(v + 0.08, i, f"{v:.1f}", va="center", fontsize=8, fontweight="bold")
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(0, 9)
    ax.set_xlabel("综合评分（可用性权重 25% 最高，中国团队视角）", fontsize=9)
    ax.set_title("当可用性权重最高时，国内旗舰综合分反超海外锚", fontsize=12, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.xaxis.grid(True, linestyle="--", linewidth=0.4, color="#cccccc"); ax.set_axisbelow(True)
    src_note(fig)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(os.path.join(OUT, "fig5_ranking.svg"))
    plt.close(fig)

# ---------- 通用表格渲染 ----------
def render_table(filename, title, col_headers, rows, col_align=None, col_widths=None, fontsize=9.5):
    ncol = len(col_headers)
    nrow = len(rows)
    if col_widths is None:
        col_widths = [1.0] * ncol
    total_w = sum(col_widths)
    fig_w = min(8.4, max(6.4, total_w * 0.9))
    row_h = 0.42
    fig_h = 0.9 + row_h * (nrow + 1)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    ax.set_xlim(0, total_w); ax.set_ylim(0, nrow + 1.6)
    if title:
        ax.text(total_w/2, nrow + 1.25, title, ha="center", va="center", fontsize=11.5, fontweight="bold")
    xstarts = []
    x = 0
    for w in col_widths:
        xstarts.append(x); x += w
    header_y = nrow + 0.5
    ax.add_patch(plt.Rectangle((0, header_y - 0.05), total_w, row_h + 0.1, color="#0b1120", zorder=1))
    for j, h in enumerate(col_headers):
        ax.text(xstarts[j] + col_widths[j]/2, header_y + row_h/2, h, ha="center", va="center",
                color="white", fontsize=fontsize+0.5, fontweight="bold", zorder=2)
    for i, row in enumerate(rows):
        y = header_y - (i + 1) * row_h
        if i % 2 == 1:
            ax.add_patch(plt.Rectangle((0, y - 0.0), total_w, row_h, color="#fafbfc", zorder=0))
        ax.plot([0, total_w], [y, y], color="#f0f0f0", linewidth=0.5, zorder=0)
        for j, cell in enumerate(row):
            align = (col_align[j] if col_align else "left")
            if align == "left":
                tx = xstarts[j] + 0.08; ha = "left"
            elif align == "right":
                tx = xstarts[j] + col_widths[j] - 0.08; ha = "right"
            else:
                tx = xstarts[j] + col_widths[j]/2; ha = "center"
            color = "#222222"; fw = "normal"
            if align == "center" and j == ncol - 1:
                color = "#553c9a"; fw = "bold"
            ax.text(tx, y + row_h/2, str(cell), ha=ha, va="center", fontsize=fontsize, color=color, fontweight=fw)
    ax.plot([0, total_w], [header_y - 0.05, header_y - 0.05], color="#0b1120", linewidth=2)
    ax.plot([0, total_w], [header_y - nrow*row_h, header_y - nrow*row_h], color="#0b1120", linewidth=2)
    fig.text(0.01, 0.01, SRC, fontsize=6, color=GREY, ha="left", va="bottom")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, filename))
    plt.close(fig)

def table01():
    headers = ["模型", "编码", "推理", "生态", "可用性", "成本", "综合"]
    rows = [
        ["Fable/Mythos 5", "10.0", "10.0", "10.0", "2.5", "1.0", "6.1"],
        ["GPT-5.5", "5.7", "6.3", "9.5", "3.5", "2.0", "5.2"],
        ["Gemini 3.1 Pro", "4.8", "6.0", "8.5", "3.0", "2.5", "4.7"],
        ["DeepSeek V4 Pro", "4.4", "—", "7.0", "9.0", "8.5", "7.2"],
        ["Kimi K2.6", "5.7", "6.8", "6.5", "9.0", "9.5", "7.6"],
        ["GLM-5.1/5.2", "5.7", "—", "7.0", "9.5", "9.0", "7.9"],
        ["Qwen 3.6", "4.8", "—", "7.5", "9.0", "9.0", "7.6"],
    ]
    align = ["left", "center", "center", "center", "center", "center", "center"]
    widths = [2.2, 0.9, 0.9, 0.9, 1.0, 0.9, 1.0]
    render_table("table_01_score.svg", "表1  七款模型五维评分矩阵（中国团队视角，权重：编码20/推理15/生态20/可用性25/成本20）",
                 headers, rows, align, widths, fontsize=9)

def table02():
    headers = ["角色", "推荐选型", "理由", "否决条件"]
    rows = [
        ["模型厂商", "补长程 Agent + 双轨制度", "差距在 FrontierCode 长程工程", "只追单次跑分"],
        ["应用企业", "国内旗舰为主链路", "中文+合规+价格差 30–70 倍", "把 Fable 设为唯一依赖"],
        ["安全合规", "做断供演练 + 数据不出境", "18天停服 + 30天留存", "涉密数据流向 Mythos 级"],
        ["投资研究", "看长程+生态+可用性组合", "单一跑分会误判座次", "以某一基准绝对分排名"],
    ]
    align = ["left", "left", "left", "left"]
    widths = [1.2, 2.1, 2.4, 2.0]
    render_table("table_02_decision.svg", "表2  分角色决策表（场景 → 推荐 → 理由 → 否决条件）",
                 headers, rows, align, widths, fontsize=8.5)

if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    table01(); table02()
    print("figures:", sorted(os.listdir(OUT)))
    print("font used:", CJK)
