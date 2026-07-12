"""Optional real document renderers."""

from __future__ import annotations

import base64
import shutil
import subprocess
import tempfile
from pathlib import Path

from .contracts import DocumentRenderer


class PandocDocumentRenderer(DocumentRenderer):
    """Render canonical Markdown to DOCX/PDF through an installed Pandoc CLI."""

    def __init__(
        self,
        executable: str = "pandoc",
        *,
        timeout_seconds: int = 120,
        pdf_engine: str | None = None,
    ) -> None:
        resolved = shutil.which(executable)
        if not resolved:
            raise ValueError(f"找不到 Pandoc 可执行文件: {executable}")
        self.executable = resolved
        self.timeout_seconds = timeout_seconds
        self.pdf_engine = pdf_engine

    def render(self, *, content, output_format, visualizations):
        if output_format not in {"docx", "pdf"}:
            raise ValueError(f"Pandoc renderer 不支持: {output_format}")
        with tempfile.TemporaryDirectory(prefix="research-render-") as directory:
            root = Path(directory)
            source = root / "report.md"
            target = root / f"report.{output_format}"
            source.write_text(content, encoding="utf-8")
            command = [
                self.executable,
                str(source),
                "--from=gfm",
                f"--to={output_format}",
                "--output",
                str(target),
            ]
            if output_format == "pdf" and self.pdf_engine:
                command.extend(["--pdf-engine", self.pdf_engine])
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
            if completed.returncode != 0 or not target.exists():
                raise RuntimeError(
                    "Pandoc 渲染失败: "
                    + (completed.stderr.strip() or completed.stdout.strip())
                )
            data = target.read_bytes()
        return (
            base64.b64encode(data).decode("ascii"),
            {
                "rendered": True,
                "renderer": "pandoc",
                "output_format": output_format,
                "media_type": (
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                    if output_format == "docx"
                    else "application/pdf"
                ),
                "encoding": "base64",
                "byte_count": len(data),
                "visual_asset_count": len(visualizations.get("assets", [])),
            },
        )
