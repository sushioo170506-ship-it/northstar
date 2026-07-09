#!/usr/bin/env python3
"""Lint style consistency for external-model-research skill docs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


REQUIRED_H2 = ["定位与作用", "输入", "输出", "质量卡口", "交接"]
METHOD_H2_KEYWORDS = [
    "方法",
    "执行动作",
    "写作方法",
    "采集原则",
    "编排流程",
    "复核框架",
    "流程",
]
FIVE_PART_TERMS = ["定位", "能力", "场景", "边界", "启示"]


def extract_h2(lines: list[str]) -> list[str]:
    result: list[str] = []
    for line in lines:
        m = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if m:
            result.append(m.group(1))
    return result


def table_ratio(lines: list[str]) -> float:
    in_code = False
    table_lines = 0
    content_lines = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if stripped.startswith("|"):
            table_lines += 1
        if not stripped.startswith("#"):
            content_lines += 1
    if content_lines == 0:
        return 0.0
    return table_lines / content_lines


def repeated_paragraphs(lines: list[str]) -> list[str]:
    in_code = False
    norms: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if stripped.startswith(("#", "-", "*")):
            continue
        if len(stripped) < 24:
            continue
        norm = re.sub(r"\s+", "", stripped)
        norms.append(norm)
    dup = [k for k, v in Counter(norms).items() if v > 1]
    return dup[:5]


def check_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    h2 = extract_h2(lines)
    h2_set = set(h2)
    h2_counter = Counter(h2)

    failures: list[str] = []
    warnings: list[str] = []

    if not re.search(r"^name:\s+\S+", text, re.M):
        failures.append("missing `name:` field")
    if not re.search(r"^description:\s+.+", text, re.M):
        failures.append("missing `description:` field")

    for section in REQUIRED_H2:
        if section not in h2_set:
            failures.append(f"missing required section: `{section}`")

    if not any(any(k in title for k in METHOD_H2_KEYWORDS) for title in h2):
        failures.append("missing method/execution section (e.g. 写作方法/执行动作/流程)")

    dup_h2 = [k for k, v in h2_counter.items() if v > 1]
    if dup_h2:
        failures.append(f"duplicate h2 headings: {', '.join(dup_h2)}")

    ratio = table_ratio(lines)
    if ratio > 0.45:
        warnings.append(f"table-heavy layout ratio={ratio:.2f} (>0.45)")

    dup_paras = repeated_paragraphs(lines)
    if dup_paras:
        warnings.append("potential repeated prose paragraphs detected")

    conclusion_sensitive = bool(re.search(r"(结论章节|§7|结论输出框架)", text))
    if conclusion_sensitive and not all(term in text for term in FIVE_PART_TERMS):
        warnings.append("conclusion mentions found but five-part terminology may be incomplete")

    return {
        "file": str(path),
        "failures": failures,
        "warnings": warnings,
        "h2_count": len(h2),
        "table_ratio": round(ratio, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check skill docs style consistency.")
    parser.add_argument(
        "--root",
        default="/workspace/skills/external-model-research",
        help="Skills root directory",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON summary")
    args = parser.parse_args()

    root = Path(args.root)
    skill_files = sorted(root.glob("**/SKILL.md"))
    if not skill_files:
        print(f"No skill files found under {root}", file=sys.stderr)
        return 2

    results = [check_file(p) for p in skill_files]
    fail_count = sum(1 for r in results if r["failures"])
    warn_count = sum(len(r["warnings"]) for r in results)

    summary = {
        "root": str(root),
        "files_checked": len(results),
        "files_failed": fail_count,
        "warning_count": warn_count,
        "results": results,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Checked {len(results)} files, failures: {fail_count}, warnings: {warn_count}")
        for r in results:
            rel = Path(r["file"]).relative_to(root)
            print(f"- {rel}")
            for f in r["failures"]:
                print(f"  FAIL: {f}")
            for w in r["warnings"]:
                print(f"  WARN: {w}")

    return 1 if fail_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
