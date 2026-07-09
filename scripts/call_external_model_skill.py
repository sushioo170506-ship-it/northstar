#!/usr/bin/env python3
"""One-command wrapper for external model research skills.

Examples:
  python3 scripts/call_external_model_skill.py "/model-report GPT-5.6"
  python3 scripts/call_external_model_skill.py "/step4 GPT-5.6"
  python3 scripts/call_external_model_skill.py --interactive
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = REPO_ROOT / "archive" / "runs" / "gpt-5.6-full"
WORKFLOW_SCRIPT = REPO_ROOT / "scripts" / "run_external_model_workflow_gpt56_full.py"

COMMAND_TO_SKILL = {
    "/model-report": "model-report-orchestrator",
    "/orchestrator": "model-report-orchestrator",
    "/step1": "mr-step1-scope",
    "/step2": "mr-step2-outline",
    "/step3": "mr-step3-collect",
    "/step4": "mr-step4-process",
    "/step5": "mr-step5-write",
    "/step6": "mr-step6-review",
    "/step7": "mr-step7-output",
}

SKILL_TO_ARTIFACT = {
    "model-report-orchestrator": "archive/runs/gpt-5.6-full/output/report.md",
    "mr-step1-scope": "archive/runs/gpt-5.6-full/scope.md",
    "mr-step2-outline": "archive/runs/gpt-5.6-full/outline.md",
    "mr-step3-collect": "archive/runs/gpt-5.6-full/raw_data/",
    "mr-step4-process": "archive/runs/gpt-5.6-full/processed_data/",
    "mr-step5-write": "archive/runs/gpt-5.6-full/report.md",
    "mr-step6-review": "archive/runs/gpt-5.6-full/review_checklist.md",
    "mr-step7-output": "archive/runs/gpt-5.6-full/output/",
}


def normalize_model(raw: str) -> str:
    model = raw.strip().lower().replace("_", "-")
    if model in {"gpt-5.6", "gpt56", "gpt-56"}:
        return "GPT-5.6"
    raise ValueError(
        f"Unsupported model '{raw}'. Currently supported: GPT-5.6 "
        "(aliases: gpt-5.6, gpt56, gpt-56)."
    )


def parse_slash_command(text: str) -> tuple[str, str, str]:
    parts = shlex.split(text.strip())
    if not parts:
        raise ValueError("Empty command.")

    command = parts[0]
    if command == "/help":
        return "/help", "", ""
    if command == "/list":
        return "/list", "", ""
    if command not in COMMAND_TO_SKILL:
        allowed = ", ".join(sorted(COMMAND_TO_SKILL))
        raise ValueError(f"Unknown command '{command}'. Allowed: {allowed}, /list, /help")

    model = "GPT-5.6" if len(parts) < 2 else normalize_model(parts[1])
    skill = COMMAND_TO_SKILL[command]
    return command, skill, model


def print_help() -> None:
    print("Quick skill commands:")
    print("  /model-report GPT-5.6  -> run model-report-orchestrator")
    print("  /step1 GPT-5.6         -> focus on mr-step1-scope outputs")
    print("  /step2 GPT-5.6         -> focus on mr-step2-outline outputs")
    print("  /step3 GPT-5.6         -> focus on mr-step3-collect outputs")
    print("  /step4 GPT-5.6         -> focus on mr-step4-process outputs")
    print("  /step5 GPT-5.6         -> focus on mr-step5-write outputs")
    print("  /step6 GPT-5.6         -> focus on mr-step6-review outputs")
    print("  /step7 GPT-5.6         -> focus on mr-step7-output outputs")
    print("  /list                  -> list command -> skill mapping")


def print_list() -> None:
    print("Slash command mapping:")
    for command, skill in sorted(COMMAND_TO_SKILL.items()):
        print(f"  {command:<14} -> {skill}")


def run_skill(skill: str, model: str, slash_command: str) -> int:
    proc = subprocess.run([sys.executable, str(WORKFLOW_SCRIPT)], cwd=str(REPO_ROOT), check=False)
    if proc.returncode != 0:
        return proc.returncode

    summary = {
        "status": "PASS",
        "slash_command": slash_command,
        "skill": skill,
        "model": model,
        "run_dir": str(RUN_DIR),
        "focus_artifact": SKILL_TO_ARTIFACT[skill],
        "note": (
            "Current backend executes the full orchestrator pipeline and then returns "
            "the requested skill's focus artifact."
        ),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Call external model research skills with slash-like commands.")
    parser.add_argument(
        "slash_command",
        nargs="?",
        help='Slash-like command, e.g. "/model-report GPT-5.6" or "/step4 GPT-5.6"',
    )
    parser.add_argument("--interactive", action="store_true", help="Prompt for slash command input.")
    parser.add_argument("--list", action="store_true", help="List command -> skill mapping.")
    args = parser.parse_args()

    if args.list:
        print_list()
        return 0

    command_text = args.slash_command
    if args.interactive or not command_text:
        print_help()
        command_text = input("\n请输入命令（例如 /model-report GPT-5.6）：").strip()

    try:
        command, skill, model = parse_slash_command(command_text)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if command == "/help":
        print_help()
        return 0
    if command == "/list":
        print_list()
        return 0

    return run_skill(skill=skill, model=model, slash_command=command_text)


if __name__ == "__main__":
    raise SystemExit(main())
