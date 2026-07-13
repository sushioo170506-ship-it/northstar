"""Portable Agent Skill and agent-facing CLI tests."""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from research_workflow.cli import main as cli_main


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "agent-skills" / "research-report-workflow"
ADAPTERS = (
    ROOT / ".cursor" / "skills" / "research-report-workflow",
    ROOT / ".claude" / "skills" / "research-report-workflow",
    ROOT / ".agents" / "skills" / "research-report-workflow",
    ROOT / ".trae" / "skills" / "research-report-workflow",
    ROOT / ".qoder" / "skills" / "research-report-workflow",
    ROOT / ".codebuddy" / "skills" / "research-report-workflow",
)


def tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    }


class PortableSkillTests(unittest.TestCase):
    def test_all_platform_adapters_match_canonical_bundle(self) -> None:
        canonical = tree_bytes(CANONICAL)
        self.assertIn("SKILL.md", canonical)
        self.assertIn(
            b"name: research-report-workflow", canonical["SKILL.md"]
        )
        for adapter in ADAPTERS:
            self.assertEqual(tree_bytes(adapter), canonical, str(adapter))

    def test_portable_launcher_finds_repository(self) -> None:
        completed = subprocess.run(
            [
                "python3",
                str(CANONICAL / "scripts" / "workflow.py"),
                "--help",
            ],
            cwd="/tmp",
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("research-workflow", completed.stdout)
        self.assertIn("create-config", completed.stdout)
        self.assertIn("artifact", completed.stdout)

    def test_cli_create_config_and_read_checkpoint_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "topic": "跨Agent调用测试",
                        "expected_length": 500,
                        "workflow_profile": "deep",
                        "output_format": "markdown",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    cli_main(
                        [
                            "--data-dir",
                            str(root / "data"),
                            "create-config",
                            str(config_path),
                        ]
                    ),
                    0,
                )
            workflow_id = json.loads(output.getvalue())["workflow_id"]

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    cli_main(
                        [
                            "--data-dir",
                            str(root / "data"),
                            "run",
                            workflow_id,
                        ]
                    ),
                    0,
                )
            self.assertEqual(
                json.loads(output.getvalue())["waiting_at"],
                "issue_tree_confirmation",
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    cli_main(
                        [
                            "--data-dir",
                            str(root / "data"),
                            "artifact",
                            workflow_id,
                            "issue_tree",
                        ]
                    ),
                    0,
                )
            self.assertIn("ISSUE-01", output.getvalue())


if __name__ == "__main__":
    unittest.main()
