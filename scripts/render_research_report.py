"""Render the GPT-Live Markdown report to DOCX, PDF, and Feishu-ready Markdown."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "gpt-live-application-research"
SOURCE = OUTPUT / "gpt-live应用探索研究报告.md"
DOCX = OUTPUT / "gpt-live应用探索研究报告.docx"
PDF = OUTPUT / "gpt-live应用探索研究报告.pdf"
FEISHU = OUTPUT / "gpt-live应用探索研究报告-飞书导入.md"
MANIFEST = OUTPUT / "gpt-live应用探索研究报告-飞书发布清单.json"

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\(https?://[^)]+\))")


def blocks(markdown: str):
    lines = markdown.splitlines()
    index = 0
    paragraph: list[str] = []
    while index < len(lines):
        line = lines[index]
        if paragraph and (
            not line.strip()
            or line.startswith("#")
            or line.startswith("|")
            or line.startswith("```")
            or re.match(r"^\d+\.\s", line)
            or line.startswith("- ")
            or line.startswith("> ")
        ):
            yield "paragraph", " ".join(paragraph)
            paragraph = []
        if not line.strip():
            index += 1
            continue
        if line.startswith("```"):
            language = line[3:].strip()
            content = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                content.append(lines[index])
                index += 1
            yield "code", (language, "\n".join(content))
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and re.match(
            r"^\|?\s*:?-{3,}", lines[index + 1]
        ):
            rows = [table_cells(line)]
            index += 2
            while index < len(lines) and lines[index].startswith("|"):
                rows.append(table_cells(lines[index]))
                index += 1
            yield "table", rows
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            yield "heading", (len(heading.group(1)), heading.group(2))
            index += 1
            continue
        if line.startswith("> "):
            yield "quote", line[2:]
            index += 1
            continue
        item = re.match(r"^(\d+\.\s+|-\s+)(.+)$", line)
        if item:
            yield "list", (item.group(1)[0].isdigit(), item.group(2))
            index += 1
            continue
        paragraph.append(line.strip())
        index += 1
    if paragraph:
        yield "paragraph", " ".join(paragraph)


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def clean(value: str) -> str:
    value = LINK.sub(lambda match: f"{match.group(1)} ({match.group(2)})", value)
    return re.sub(r"(\*\*|`)", "", value)


def add_docx_runs(paragraph, text: str) -> None:
    cursor = 0
    for match in INLINE.finditer(text):
        paragraph.add_run(text[cursor:match.start()])
        token = match.group(0)
        link = LINK.fullmatch(token)
        if link:
            add_hyperlink(paragraph, link.group(1), link.group(2))
        elif token.startswith("**"):
            paragraph.add_run(token[2:-2]).bold = True
        else:
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
        cursor = match.end()
    paragraph.add_run(text[cursor:])


def add_hyperlink(paragraph, text: str, url: str) -> None:
    relationship = paragraph.part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship)
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    properties.extend((color, underline))
    run.append(properties)
    text_element = OxmlElement("w:t")
    text_element.text = text
    run.append(text_element)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def render_docx(markdown: str) -> None:
    document = Document()
    section = document.sections[0]
    section.top_margin = section.bottom_margin = Cm(2.2)
    section.left_margin = section.right_margin = Cm(2.4)
    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    normal.font.size = Pt(10.5)
    for kind, value in blocks(markdown):
        if kind == "heading":
            level, title = value
            paragraph = document.add_heading(clean(title), level=min(level, 4))
            if level == 1:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif kind in {"paragraph", "quote"}:
            paragraph = document.add_paragraph()
            if kind == "quote":
                paragraph.style = "Quote"
            add_docx_runs(paragraph, value)
        elif kind == "list":
            ordered, text = value
            paragraph = document.add_paragraph(
                style="List Number" if ordered else "List Bullet"
            )
            add_docx_runs(paragraph, text)
        elif kind == "code":
            language, code = value
            paragraph = document.add_paragraph()
            paragraph.style = "No Spacing"
            run = paragraph.add_run((language + "\n" if language else "") + code)
            run.font.name = "Consolas"
            run.font.size = Pt(8)
        elif kind == "table":
            rows = value
            table = document.add_table(rows=len(rows), cols=max(map(len, rows)))
            table.style = "Table Grid"
            for row_index, row in enumerate(rows):
                for column_index, cell in enumerate(row):
                    target = table.cell(row_index, column_index)
                    target.text = clean(cell)
                    if row_index == 0:
                        for run in target.paragraphs[0].runs:
                            run.bold = True
    document.save(DOCX)


def pdf_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", escaped)
    escaped = LINK.sub(
        lambda match: (
            f"<link href='{html.escape(match.group(2))}' color='#0563C1'>"
            f"{html.escape(match.group(1))}</link>"
        ),
        escaped,
    )
    return escaped


def render_pdf(markdown: str) -> None:
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    base = getSampleStyleSheet()
    normal = ParagraphStyle(
        "ChineseBody",
        parent=base["BodyText"],
        fontName="STSong-Light",
        fontSize=9.5,
        leading=15,
        spaceAfter=7,
        wordWrap="CJK",
    )
    quote = ParagraphStyle(
        "ChineseQuote",
        parent=normal,
        leftIndent=12,
        borderColor=colors.HexColor("#D9D9D9"),
        borderWidth=1,
        borderPadding=6,
        backColor=colors.HexColor("#F7F7F7"),
    )
    headings = {
        level: ParagraphStyle(
            f"H{level}",
            parent=normal,
            fontName="STSong-Light",
            fontSize=max(11, 21 - level * 2),
            leading=max(15, 25 - level * 2),
            spaceBefore=12,
            spaceAfter=8,
            alignment=TA_CENTER if level == 1 else 0,
            textColor=colors.HexColor("#17365D"),
        )
        for level in range(1, 7)
    }
    story = []
    for kind, value in blocks(markdown):
        if kind == "heading":
            level, title = value
            if level == 1 and story:
                story.append(PageBreak())
            story.append(Paragraph(pdf_markup(title), headings[level]))
        elif kind == "paragraph":
            story.append(Paragraph(pdf_markup(value), normal))
        elif kind == "quote":
            story.append(Paragraph(pdf_markup(value), quote))
        elif kind == "list":
            ordered, text = value
            bullet = "1." if ordered else "•"
            story.append(Paragraph(pdf_markup(text), normal, bulletText=bullet))
        elif kind == "code":
            language, code = value
            story.append(
                Paragraph(
                    pdf_markup((language + "\n" if language else "") + code).replace(
                        "\n", "<br/>"
                    ),
                    ParagraphStyle(
                        "Code", parent=normal, fontName="STSong-Light",
                        fontSize=7.5, backColor=colors.HexColor("#F4F4F4"),
                        borderPadding=5,
                    ),
                )
            )
        elif kind == "table":
            rows = [
                [Paragraph(pdf_markup(cell), normal) for cell in row]
                for row in value
            ]
            table = Table(rows, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7B7B7")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.extend((table, Spacer(1, 0.2 * cm)))
    document = SimpleDocTemplate(
        str(PDF),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
        title="GPT-Live应用探索研究报告",
        author="Northstar Research Workflow",
    )
    document.build(story)


def render_feishu(markdown: str) -> None:
    shutil.copyfile(SOURCE, FEISHU)
    tables = sum(kind == "table" for kind, _ in blocks(markdown))
    MANIFEST.write_text(
        json.dumps(
            {
                "format": "feishu-ready-markdown",
                "source": FEISHU.name,
                "native_sheet_candidates": tables,
                "inline_links_preserved": True,
                "publish_status": "pending_user_oauth",
                "note": (
                    "注入FeishuDocumentRenderer后，正文转Docx块，Markdown表格转"
                    "原生Sheet Block；当前环境没有用户飞书凭证，未生成虚假链接。"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    render_docx(markdown)
    render_pdf(markdown)
    render_feishu(markdown)
    print(
        json.dumps(
            {
                "markdown": str(SOURCE),
                "docx": str(DOCX),
                "pdf": str(PDF),
                "feishu": str(FEISHU),
                "manifest": str(MANIFEST),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
