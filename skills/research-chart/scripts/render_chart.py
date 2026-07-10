#!/usr/bin/env python3
"""Render simple, dependency-free SVG charts from JSON records."""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path
from typing import Any


PALETTE = ("#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", choices=("bar", "line"), required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="JSON input file")
    source.add_argument("--data", help="Inline JSON array")
    parser.add_argument("--x-field", default="x")
    parser.add_argument("--y-field", default="y")
    parser.add_argument("--series-field", default="series")
    parser.add_argument("--title", required=True)
    parser.add_argument("--x-label", default="")
    parser.add_argument("--y-label", default="")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=560)
    return parser.parse_args()


def load_records(args: argparse.Namespace) -> list[dict[str, Any]]:
    raw = args.input.read_text(encoding="utf-8") if args.input else args.data
    records = json.loads(raw)
    if not isinstance(records, list) or not records:
        raise ValueError("input must be a non-empty JSON array")

    normalized = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"record {index} must be an object")
        if args.x_field not in record or args.y_field not in record:
            raise ValueError(f"record {index} must contain x and y fields")
        value = record[args.y_field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"record {index} y value must be numeric")
        if not math.isfinite(value):
            raise ValueError(f"record {index} y value must be finite")
        normalized.append(
            {
                "x": str(record[args.x_field]),
                "y": float(value),
                "series": str(record.get(args.series_field, "Value")),
            }
        )
    return normalized


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def svg_text(x: float, y: float, text: str, **attrs: Any) -> str:
    attributes = {"x": x, "y": y, **attrs}
    serialized = " ".join(
        f'{key.replace("_", "-")}="{html.escape(str(value), quote=True)}"'
        for key, value in attributes.items()
    )
    return f"<text {serialized}>{html.escape(text)}</text>"


def format_number(value: float) -> str:
    absolute = abs(value)
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.1f}K"
    if absolute >= 10:
        return f"{value:.0f}"
    return f"{value:.1f}".rstrip("0").rstrip(".")


def render(args: argparse.Namespace, records: list[dict[str, Any]]) -> str:
    if args.width < 480 or args.height < 320:
        raise ValueError("minimum chart size is 480x320")

    width, height = args.width, args.height
    left, right, top, bottom = 95, 35, 78, 105
    plot_width = width - left - right
    plot_height = height - top - bottom
    categories = unique([item["x"] for item in records])
    series = unique([item["series"] for item in records])
    values = [item["y"] for item in records]
    y_min = min(0.0, min(values))
    y_max = max(0.0, max(values))
    if y_min == y_max:
        y_max = y_min + 1
    padding = (y_max - y_min) * 0.08
    if y_min < 0:
        y_min -= padding
    y_max += padding

    def y_position(value: float) -> float:
        return top + (y_max - value) / (y_max - y_min) * plot_height

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"<title id=\"title\">{html.escape(args.title)}</title>",
        f"<desc id=\"desc\">{html.escape(args.source)}</desc>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        svg_text(left, 38, args.title, font_family="Arial, sans-serif", font_size=20, font_weight=700, fill="#111827"),
    ]

    for tick in range(6):
        value = y_min + (y_max - y_min) * tick / 5
        y = y_position(value)
        elements.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}" '
            'stroke="#d1d5db" stroke-width="1" stroke-dasharray="4 4"/>'
        )
        elements.append(
            svg_text(
                left - 12,
                y + 4,
                format_number(value),
                text_anchor="end",
                font_family="Arial, sans-serif",
                font_size=12,
                fill="#4b5563",
            )
        )

    baseline = y_position(0)
    elements.append(
        f'<line x1="{left}" y1="{baseline:.2f}" x2="{width-right}" y2="{baseline:.2f}" '
        'stroke="#111827" stroke-width="1.4"/>'
    )
    elements.append(
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" '
        'stroke="#111827" stroke-width="1.4"/>'
    )

    category_width = plot_width / len(categories)
    lookup = {(item["x"], item["series"]): item["y"] for item in records}

    if args.type == "bar":
        group_width = category_width * 0.72
        bar_width = group_width / max(1, len(series))
        for category_index, category in enumerate(categories):
            center = left + category_width * (category_index + 0.5)
            for series_index, series_name in enumerate(series):
                key = (category, series_name)
                if key not in lookup:
                    continue
                value = lookup[key]
                x = center - group_width / 2 + series_index * bar_width + 1
                y = min(y_position(value), baseline)
                bar_height = max(1.0, abs(y_position(value) - baseline))
                elements.append(
                    f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(1, bar_width-2):.2f}" '
                    f'height="{bar_height:.2f}" fill="{PALETTE[series_index % len(PALETTE)]}" rx="2"/>'
                )
    else:
        for series_index, series_name in enumerate(series):
            points = []
            for category_index, category in enumerate(categories):
                key = (category, series_name)
                if key in lookup:
                    x = left + category_width * (category_index + 0.5)
                    points.append((x, y_position(lookup[key])))
            if not points:
                continue
            color = PALETTE[series_index % len(PALETTE)]
            coordinates = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
            elements.append(
                f'<polyline points="{coordinates}" fill="none" stroke="{color}" '
                'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
            )
            for x, y in points:
                elements.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}"/>')

    for index, category in enumerate(categories):
        x = left + category_width * (index + 0.5)
        elements.append(
            svg_text(
                x,
                height - bottom + 24,
                category,
                text_anchor="middle",
                font_family="Arial, sans-serif",
                font_size=12,
                fill="#374151",
            )
        )

    if args.x_label:
        elements.append(
            svg_text(
                left + plot_width / 2,
                height - 48,
                args.x_label,
                text_anchor="middle",
                font_family="Arial, sans-serif",
                font_size=13,
                font_weight=600,
                fill="#111827",
            )
        )
    if args.y_label:
        elements.append(
            svg_text(
                22,
                top + plot_height / 2,
                args.y_label,
                transform=f"rotate(-90 22 {top + plot_height / 2:.2f})",
                text_anchor="middle",
                font_family="Arial, sans-serif",
                font_size=13,
                font_weight=600,
                fill="#111827",
            )
        )

    legend_x = max(left, width - right - len(series) * 125)
    for index, series_name in enumerate(series):
        x = legend_x + index * 125
        color = PALETTE[index % len(PALETTE)]
        elements.append(f'<rect x="{x}" y="52" width="13" height="13" fill="{color}" rx="2"/>')
        elements.append(
            svg_text(x + 19, 63, series_name, font_family="Arial, sans-serif", font_size=12, fill="#374151")
        )

    elements.append(
        svg_text(
            left,
            height - 14,
            args.source,
            font_family="Arial, sans-serif",
            font_size=10,
            fill="#6b7280",
        )
    )
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def main() -> None:
    args = parse_args()
    records = load_records(args)
    svg = render(args, records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    print(f"SVG saved to {args.output}")


if __name__ == "__main__":
    main()
