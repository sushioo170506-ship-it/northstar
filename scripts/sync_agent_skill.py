#!/usr/bin/env python3
"""Copy the canonical portable Skill into supported project locations."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "agent-skills" / "research-report-workflow"
TARGETS = (
    ROOT / ".cursor" / "skills" / "research-report-workflow",
    ROOT / ".claude" / "skills" / "research-report-workflow",
    ROOT / ".agents" / "skills" / "research-report-workflow",
    ROOT / ".trae" / "skills" / "research-report-workflow",
    ROOT / ".qoder" / "skills" / "research-report-workflow",
    ROOT / ".codebuddy" / "skills" / "research-report-workflow",
)


def main() -> int:
    if not (SOURCE / "SKILL.md").exists():
        raise FileNotFoundError(f"canonical skill missing: {SOURCE}")
    for target in TARGETS:
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            SOURCE,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        print(target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
