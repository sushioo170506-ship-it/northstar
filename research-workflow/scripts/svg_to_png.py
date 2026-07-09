#!/usr/bin/env python3
"""Wcget Step 6 — 将 figures/*.svg 批量转 PNG（2×），供 docx/feishu 复用。"""
import os, cairosvg

BASE = os.path.join(os.path.dirname(__file__), "..", "output")
FIG = os.path.join(BASE, "figures")
OUT = os.path.join(BASE, "figures_png")
os.makedirs(OUT, exist_ok=True)

def run():
    svgs = sorted(f for f in os.listdir(FIG) if f.endswith(".svg"))
    ok = 0
    for s in svgs:
        dst = os.path.join(OUT, s[:-4] + ".png")
        cairosvg.svg2png(url=os.path.join(FIG, s), write_to=dst, scale=2, background_color="white")
        ok += 1
    print(f"PNG: {ok}/{len(svgs)} ->", OUT)

if __name__ == "__main__":
    run()
