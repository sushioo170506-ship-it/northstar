#!/usr/bin/env python3
"""Wcget Step 6 — 将 report.md + figures/*.svg 组装为自包含 HTML。
- 内联所有 SVG
- 图/表容器区分（fig_ → 深色图容器；table_ → 浅色表容器）
- 响应式 + 打印样式
"""
import os, re, html

BASE = os.path.join(os.path.dirname(__file__), "..", "output")
MD = os.path.join(BASE, "report.md")
FIG = os.path.join(BASE, "figures")
OUT = os.path.join(BASE, "report.html")

def inline(m):
    return m.group(0)

def md_inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text

def load_svg(path):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    # 去掉 xml 声明/doctype，仅保留 <svg>
    s = re.sub(r"<\?xml.*?\?>", "", s, flags=re.S)
    s = re.sub(r"<!DOCTYPE.*?>", "", s, flags=re.S)
    return s.strip()

def build():
    with open(MD, encoding="utf-8") as f:
        lines = f.read().split("\n")

    body = []
    i = 0
    fig_no = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        s = line.strip()
        if not s:
            i += 1; continue
        # 图片/图表引用
        m = re.match(r"!\[(.*?)\]\((.*?)\)", s)
        if m:
            alt, path = m.group(1), m.group(2)
            fname = os.path.basename(path)
            svg_path = os.path.join(FIG, fname)
            is_table = fname.startswith("table_")
            cls = "tfg" if is_table else "fg"
            svg = load_svg(svg_path) if os.path.exists(svg_path) else f"<em>缺图 {fname}</em>"
            cap = md_inline(alt)
            body.append(f'<figure class="{cls}">{svg}<figcaption>{cap}</figcaption></figure>')
            i += 1; continue
        # H1
        if s.startswith("# "):
            body.append(f'<div class="titlewrap"><div class="pill">研究报告 · Wcget</div><h1>{md_inline(s[2:])}</h1></div>')
            i += 1; continue
        # H2
        if s.startswith("## "):
            fig_no += 1
            body.append(f'<h2><span class="num">{fig_no:02d}</span>{md_inline(s[3:])}</h2>')
            i += 1; continue
        # HR
        if s == "---":
            body.append('<hr/>')
            i += 1; continue
        # blockquote (可能多行)
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            body.append(f'<blockquote>{md_inline(" ".join(buf))}</blockquote>')
            continue
        # 有序参考列表
        if re.match(r"^\d+\.\s", s):
            buf = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                buf.append(md_inline(re.sub(r"^\d+\.\s", "", lines[i].strip())))
                i += 1
            items = "".join(f"<li>{b}</li>" for b in buf)
            body.append(f'<ol class="refs">{items}</ol>')
            continue
        # 普通段落
        body.append(f'<p>{md_inline(s)}</p>')
        i += 1

    content = "\n".join(body)
    css = """
:root{--ink:#0b1120;--blue:#005AB5;--muted:#5a6170;}
*{box-sizing:border-box;}
body{margin:0;background:#f5f6fa;color:#1a2233;
  font-family:"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.75;}
.wrap{max-width:860px;margin:0 auto;padding:48px 28px 80px;}
.titlewrap{text-align:center;margin:8px 0 28px;padding-bottom:22px;border-bottom:2px solid #e6e9f0;}
.pill{display:inline-block;background:#e8f0fe;color:var(--blue);font-size:12px;
  padding:4px 14px;border-radius:20px;letter-spacing:1px;margin-bottom:14px;}
h1{font-size:27px;line-height:1.4;margin:6px 0;color:var(--ink);}
h2{font-size:20px;margin:38px 0 14px;color:var(--ink);display:flex;align-items:center;gap:12px;}
h2 .num{display:inline-flex;align-items:center;justify-content:center;min-width:34px;height:34px;
  background:var(--blue);color:#fff;border-radius:9px;font-size:15px;flex:0 0 auto;}
p{margin:12px 0;font-size:15.5px;}
strong{color:var(--ink);}
code{background:#eef1f6;padding:1px 6px;border-radius:5px;font-size:13px;
  font-family:"JetBrains Mono",Consolas,monospace;}
blockquote{margin:18px 0;padding:14px 18px;background:linear-gradient(90deg,#eef4ff,#f7faff);
  border-left:4px solid var(--blue);border-radius:8px;color:#33415a;font-size:14.5px;}
hr{border:none;border-top:1px solid #e6e9f0;margin:30px 0;}
figure{margin:22px 0;text-align:center;}
figure.fg{background:var(--ink);border-radius:12px;padding:16px 14px 8px;}
figure.tfg{background:transparent;padding:6px;
  filter:drop-shadow(0 2px 10px rgba(11,17,32,.08));}
figure svg{max-width:100%;height:auto;}
figcaption{font-size:12.5px;margin-top:8px;}
figure.fg figcaption{color:#c9d4e6;}
figure.tfg figcaption{color:var(--muted);}
ol.refs{font-size:13px;color:var(--muted);padding-left:22px;}
ol.refs li{margin:5px 0;}
@media (max-width:640px){h1{font-size:22px;}h2{font-size:17px;}.wrap{padding:28px 16px 60px;}p{font-size:14.5px;}}
@media print{body{background:#fff;}figure.fg{background:var(--ink)!important;-webkit-print-color-adjust:exact;print-color-adjust:exact;}figure,table{break-inside:avoid;}}
"""
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Mythos5 模型调研报告</title>
<style>{css}</style></head>
<body><div class="wrap">{content}</div></body></html>"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("HTML ->", OUT, f"({len(doc)//1024} KB)")

if __name__ == "__main__":
    build()
