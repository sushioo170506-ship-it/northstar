#!/usr/bin/env python3
"""Portable launcher that finds and runs the repository workflow CLI."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def repository_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        pyproject = candidate / "pyproject.toml"
        if pyproject.exists() and "northstar-research-workflow" in pyproject.read_text(
            encoding="utf-8"
        ):
            return candidate
    raise RuntimeError(
        "找不到 northstar-research-workflow 仓库；请在仓库内安装并调用此Skill"
    )


def main() -> int:
    root = repository_root(Path(__file__).resolve().parent)
    sys.path.insert(0, str(root / "src"))
    os.chdir(root)
    from research_workflow.cli import main as cli_main

    return cli_main(
        ["--data-dir", str(root / ".research-workflow"), *sys.argv[1:]]
    )


if __name__ == "__main__":
    raise SystemExit(main())
