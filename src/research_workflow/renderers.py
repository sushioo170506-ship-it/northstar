"""Optional real document renderers."""

from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

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


@dataclass(frozen=True)
class MarkdownTable:
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    alignments: tuple[str, ...]
    cell_styles: tuple[tuple[dict[str, bool], ...], ...] = ()

    @property
    def values(self) -> list[list[str]]:
        return [list(self.headers), *(list(row) for row in self.rows)]

    @property
    def feishu_values(self) -> list[list[Any]]:
        return [
            [self._feishu_value(value) for value in row]
            for row in self.values
        ]

    @staticmethod
    def _feishu_value(value: str) -> Any:
        if value.startswith("="):
            return {"type": "formula", "text": value}
        link = re.fullmatch(r"(.+?) \((https?://[^)]+)\)", value)
        if link:
            return {"type": "url", "text": link.group(1), "link": link.group(2)}
        return value


class MarkdownTableParser:
    """Parse GFM pipe tables without losing escaped pipes or empty cells."""

    SEPARATOR = re.compile(r"^:?-{3,}:?$")

    @classmethod
    def split_document(
        cls, content: str
    ) -> list[tuple[str, str | MarkdownTable]]:
        lines = content.splitlines()
        result: list[tuple[str, str | MarkdownTable]] = []
        markdown: list[str] = []
        index = 0
        while index < len(lines):
            if index + 1 < len(lines):
                header = cls._cells(lines[index])
                separator = cls._cells(lines[index + 1])
                is_table = (
                    len(header) > 0
                    and len(header) == len(separator)
                    and all(cls.SEPARATOR.fullmatch(cell.strip()) for cell in separator)
                )
                if is_table:
                    if markdown:
                        result.append(("markdown", "\n".join(markdown).strip()))
                        markdown = []
                    rows = []
                    raw_body_rows = []
                    index += 2
                    while index < len(lines):
                        cells = cls._cells(lines[index])
                        if len(cells) != len(header):
                            break
                        raw_body_rows.append(cells)
                        rows.append(tuple(cls._clean(cell) for cell in cells))
                        index += 1
                    alignments = tuple(cls._alignment(cell) for cell in separator)
                    raw_rows = [header, *raw_body_rows]
                    styles = tuple(
                        tuple(cls._style(cell) for cell in row)
                        for row in raw_rows
                    )
                    result.append(
                        (
                            "table",
                            MarkdownTable(
                                tuple(cls._clean(cell) for cell in header),
                                tuple(rows),
                                alignments,
                                styles,
                            ),
                        )
                    )
                    continue
            markdown.append(lines[index])
            index += 1
        if markdown:
            result.append(("markdown", "\n".join(markdown).strip()))
        return [(kind, value) for kind, value in result if value]

    @staticmethod
    def _cells(line: str) -> list[str]:
        if "|" not in line:
            return []
        text = line.strip()
        if text.startswith("|"):
            text = text[1:]
        if text.endswith("|") and not text.endswith(r"\|"):
            text = text[:-1]
        cells: list[str] = []
        buffer: list[str] = []
        escaped = False
        for char in text:
            if escaped:
                buffer.append(char)
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "|":
                cells.append("".join(buffer).strip())
                buffer = []
            else:
                buffer.append(char)
        if escaped:
            buffer.append("\\")
        cells.append("".join(buffer).strip())
        return cells

    @staticmethod
    def _clean(value: str) -> str:
        value = value.replace("<br>", "\n").replace("<br/>", "\n")
        value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", value)
        return re.sub(r"(?<!\\)(\*\*|__|\*|_|`)(.+?)\1", r"\2", value).strip()

    @staticmethod
    def _style(value: str) -> dict[str, bool]:
        stripped = value.strip()
        return {
            "bold": (
                (stripped.startswith("**") and stripped.endswith("**"))
                or (stripped.startswith("__") and stripped.endswith("__"))
            ),
            "italic": (
                (stripped.startswith("*") and stripped.endswith("*")
                 and not stripped.startswith("**"))
                or (
                    stripped.startswith("_") and stripped.endswith("_")
                    and not stripped.startswith("__")
                )
            ),
            "code": stripped.startswith("`") and stripped.endswith("`"),
        }

    @staticmethod
    def _alignment(separator: str) -> str:
        value = separator.strip()
        if value.startswith(":") and value.endswith(":"):
            return "center"
        if value.endswith(":"):
            return "right"
        return "left"


class FeishuApiClient:
    """Small stdlib Feishu Open API client with an injectable test transport."""

    def __init__(
        self,
        *,
        app_id: str | None = None,
        app_secret: str | None = None,
        access_token: str | None = None,
        base_url: str = "https://open.feishu.cn",
        timeout_seconds: int = 30,
        token_provider: Callable[[], str] | None = None,
        auth_mode: str | None = None,
        transport: Callable[
            [str, str, dict[str, Any] | None, dict[str, str]], dict[str, Any]
        ] | None = None,
    ) -> None:
        if not access_token and not token_provider and not (app_id and app_secret):
            raise ValueError(
                "飞书客户端需要 access_token、token_provider 或 app_id/app_secret"
            )
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.transport = transport
        self.token_provider = token_provider
        self.auth_mode = auth_mode or (
            "user_oauth" if access_token or token_provider else "tenant"
        )

    def _token(self) -> str:
        if self.access_token:
            return self.access_token
        if self.token_provider:
            token = self.token_provider()
            if not token:
                raise RuntimeError("飞书token_provider返回空Token")
            return token
        response = self._raw_request(
            "POST",
            "/open-apis/auth/v3/tenant_access_token/internal",
            {"app_id": self.app_id, "app_secret": self.app_secret},
            {},
        )
        token = response.get("tenant_access_token")
        if not token:
            raise RuntimeError("飞书鉴权响应缺少 tenant_access_token")
        self.access_token = str(token)
        return self.access_token

    def request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        response = self._raw_request(
            method,
            path,
            payload,
            {
                "Authorization": f"Bearer {self._token()}",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        if response.get("code", 0) != 0:
            raise RuntimeError(
                f"飞书 API 失败 code={response.get('code')}: "
                f"{response.get('msg', 'unknown error')}"
            )
        return response

    def _raw_request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        if self.transport:
            return self.transport(method, path, payload, headers)
        data = (
            json.dumps(payload, ensure_ascii=False).encode("utf-8")
            if payload is not None else None
        )
        request = urllib.request.Request(
            self.base_url + path, data=data, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_seconds
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"飞书 API 请求失败: {path}: {exc}") from exc

    def create_document(self, title: str, folder_token: str | None = None) -> str:
        payload = {"title": title[:256]}
        if folder_token:
            payload["folder_token"] = folder_token
        response = self.request("POST", "/open-apis/docx/v1/documents", payload)
        document = response.get("data", {}).get("document", {})
        document_id = document.get("document_id") or document.get("id")
        if not document_id:
            raise RuntimeError("飞书创建文档响应缺少 document_id")
        return str(document_id)

    def append_markdown(self, document_id: str, markdown: str) -> None:
        if not markdown.strip():
            return
        converted = self.request(
            "POST",
            "/open-apis/docx/v1/documents/blocks/convert",
            {"content_type": "markdown", "content": markdown},
        ).get("data", {})
        blocks = converted.get("blocks", [])
        self._remove_readonly_merge_info(blocks)
        children = converted.get("first_level_block_ids", [])
        if blocks and children:
            self.request(
                "POST",
                f"/open-apis/docx/v1/documents/{document_id}/blocks/"
                f"{document_id}/descendant?document_revision_id=-1",
                {"children_id": children, "descendants": blocks},
            )

    def append_sheet(self, document_id: str, table: MarkdownTable) -> dict[str, str]:
        rows = max(1, min(9, len(table.rows) + 1))
        columns = max(1, min(9, len(table.headers)))
        created = self.request(
            "POST",
            f"/open-apis/docx/v1/documents/{document_id}/blocks/"
            f"{document_id}/children?document_revision_id=-1",
            {
                "children": [
                    {
                        "block_type": 30,
                        "sheet": {"row_size": rows, "column_size": columns},
                    }
                ]
            },
        )
        children = created.get("data", {}).get("children", [])
        token = children[0].get("sheet", {}).get("token") if children else None
        if not token or "_" not in token:
            raise RuntimeError("飞书 Sheet Block 响应缺少可拆分 token")
        spreadsheet_token, sheet_id = str(token).rsplit("_", 1)
        end = f"{self._column_name(len(table.headers))}{len(table.rows) + 1}"
        range_name = f"{sheet_id}!A1:{end}"
        self.request(
            "PUT",
            f"/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values",
            {"valueRange": {"range": range_name, "values": table.feishu_values}},
        )
        last_column = self._column_name(len(table.headers))
        last_row = len(table.rows) + 1
        style_data = [
            {
                "ranges": [f"{sheet_id}!A1:{last_column}{last_row}"],
                "style": {
                    "borderType": "FULL_BORDER",
                    "borderColor": "#D9D9D9",
                },
            },
            {
                "ranges": [f"{sheet_id}!A1:{last_column}1"],
                "style": {
                    "font": {"bold": True},
                    "backColor": "#E8F0FE",
                    "hAlign": 1,
                },
            },
        ]
        alignment_codes = {"left": 0, "center": 1, "right": 2}
        for index, alignment in enumerate(table.alignments, start=1):
            column = self._column_name(index)
            style_data.append(
                {
                    "ranges": [f"{sheet_id}!{column}2:{column}{last_row}"],
                    "style": {"hAlign": alignment_codes[alignment]},
                }
            )
        for row_index, row in enumerate(table.cell_styles, start=1):
            for column_index, style in enumerate(row, start=1):
                if not any(style.values()):
                    continue
                column = self._column_name(column_index)
                style_data.append(
                    {
                        "ranges": [
                            f"{sheet_id}!{column}{row_index}:"
                            f"{column}{row_index}"
                        ],
                        "style": {
                            "font": {
                                "bold": style["bold"],
                                "italic": style["italic"],
                            },
                            "backColor": "#F5F5F5" if style["code"] else "#FFFFFF",
                        },
                    }
                )
        self.request(
            "PUT",
            f"/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/"
            "styles_batch_update",
            {"data": style_data},
        )
        self.request(
            "POST",
            f"/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/"
            "sheets_batch_update",
            {
                "requests": [
                    {
                        "updateSheet": {
                            "properties": {
                                "sheetId": sheet_id,
                                "frozenRowCount": 1,
                            }
                        }
                    }
                ]
            },
        )
        readback = self.request(
            "GET",
            f"/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/"
            f"values/{range_name}",
        )
        values = readback.get("data", {}).get("valueRange", {}).get("values")
        if values is not None and values != table.feishu_values:
            raise RuntimeError("飞书电子表格回读校验失败：数据与Markdown表格不一致")
        return {
            "spreadsheet_token": spreadsheet_token,
            "sheet_id": sheet_id,
            "range": range_name,
        }

    @staticmethod
    def _remove_readonly_merge_info(value: Any) -> None:
        if isinstance(value, dict):
            value.pop("merge_info", None)
            for child in value.values():
                FeishuApiClient._remove_readonly_merge_info(child)
        elif isinstance(value, list):
            for child in value:
                FeishuApiClient._remove_readonly_merge_info(child)

    @staticmethod
    def _column_name(count: int) -> str:
        if count < 1:
            raise ValueError("列数必须大于0")
        value = count
        name = ""
        while value:
            value, remainder = divmod(value - 1, 26)
            name = chr(65 + remainder) + name
        return name


class FeishuDocumentRenderer(DocumentRenderer):
    """Publish Markdown as Docx blocks and embedded native Sheet blocks."""

    def __init__(
        self,
        client: FeishuApiClient,
        *,
        title: str = "研究报告",
        folder_token: str | None = None,
        document_id: str | None = None,
    ) -> None:
        self.client = client
        self.title = title
        self.folder_token = folder_token
        self.document_id = document_id

    def render(self, *, content, output_format, visualizations):
        if output_format != "feishu":
            raise ValueError(f"Feishu renderer 不支持: {output_format}")
        document_id = self.document_id or self.client.create_document(
            self.title, self.folder_token
        )
        sheet_refs = []
        clean = re.sub(r'<a\s+id="[^"]+"></a>', "", content)
        for kind, value in MarkdownTableParser.split_document(clean):
            if kind == "markdown":
                self.client.append_markdown(document_id, str(value))
            else:
                assert isinstance(value, MarkdownTable)
                sheet_refs.append(self.client.append_sheet(document_id, value))
        return (
            f"https://feishu.cn/docx/{document_id}",
            {
                "rendered": True,
                "renderer": "feishu_open_api",
                "output_format": "feishu",
                "document_id": document_id,
                "document_url": f"https://feishu.cn/docx/{document_id}",
                "native_sheet_count": len(sheet_refs),
                "native_sheets": sheet_refs,
                "tables_editable": True,
                "filters_supported": True,
                "formulas_supported": True,
                "readback_verified": True,
                "visual_asset_count": len(visualizations.get("assets", [])),
                "auth_mode": self.client.auth_mode,
            },
        )
