"""Professional DOCX and slide renderers adapted from vetted open-source practices."""

from __future__ import annotations

import base64
import html
import io
import re
from datetime import date
from typing import Any

from .contracts import DocumentRenderer
from .renderers import MarkdownTableParser


def _strip_markup(text: str) -> str:
    text = re.sub(r'<a\s+id="[^"]+"></a>', "", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return re.sub(r"(\*\*|__|`)", "", text).strip()


def _document_title(content: str) -> str:
    match = re.search(r"(?m)^#\s+(.+)$", content)
    return _strip_markup(match.group(1)) if match else "研究报告"


def _slide_sections(content: str) -> list[tuple[str, str]]:
    title = _document_title(content)
    matches = list(re.finditer(r"(?m)^##\s+(.+)$", content))
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        sections.append((_strip_markup(match.group(1)), content[match.end():end].strip()))
    return [(title, ""), *sections]


class CompositeDocumentRenderer(DocumentRenderer):
    """Route output formats to dedicated renderers."""

    def __init__(self, renderers: dict[str, DocumentRenderer]) -> None:
        self.renderers = dict(renderers)

    def render(self, *, content, output_format, visualizations):
        renderer = self.renderers.get(output_format)
        if renderer is None:
            raise ValueError(f"未配置 {output_format} 对应的文档渲染器")
        return renderer.render(
            content=content,
            output_format=output_format,
            visualizations=visualizations,
        )


class AestheticDocxRenderer(DocumentRenderer):
    """Create a polished, editable DOCX with stable OOXML styles."""

    def render(self, *, content, output_format, visualizations):
        if output_format != "docx":
            raise ValueError(f"AestheticDocxRenderer 不支持: {output_format}")
        try:
            from docx import Document
            from docx.enum.section import WD_SECTION
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            from docx.shared import Cm, Pt, RGBColor
        except ImportError as exc:
            raise RuntimeError(
                "专业Word渲染需要安装可选依赖: pip install python-docx"
            ) from exc

        document = Document()
        section = document.sections[0]
        section.top_margin = Cm(2.2)
        section.bottom_margin = Cm(2.0)
        section.left_margin = section.right_margin = Cm(2.4)
        section.header_distance = Cm(0.8)
        section.footer_distance = Cm(0.8)

        styles = document.styles
        normal = styles["Normal"]
        normal.font.name = "Arial"
        normal._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
        normal.font.size = Pt(10.5)
        normal.paragraph_format.line_spacing = 1.5
        normal.paragraph_format.space_after = Pt(6)
        colors = ("17365D", "1F4E79", "2F75B5", "5B9BD5")
        for level in range(1, 5):
            style = styles[f"Heading {level}"]
            style.font.name = "Arial"
            style._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
            style.font.color.rgb = RGBColor.from_string(colors[level - 1])
            style.font.size = Pt(20 - level * 2)
            style.font.bold = True
            style.paragraph_format.space_before = Pt(12)
            style.paragraph_format.space_after = Pt(6)

        header = section.header.paragraphs[0]
        header.text = "NORTHSTAR RESEARCH  ·  研究报告"
        header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        header.runs[0].font.size = Pt(8)
        header.runs[0].font.color.rgb = RGBColor(120, 120, 120)
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.add_run("第 ")
        field = OxmlElement("w:fldSimple")
        field.set(qn("w:instr"), "PAGE")
        footer._p.append(field)
        footer.add_run(" 页")

        title = _document_title(content)
        cover = document.add_paragraph()
        cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cover.paragraph_format.space_before = Pt(130)
        run = cover.add_run(title)
        run.bold = True
        run.font.size = Pt(28)
        run.font.color.rgb = RGBColor.from_string("17365D")
        subtitle = document.add_paragraph()
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle.add_run(f"专业研究报告  ·  {date.today().isoformat()}").italic = True
        document.add_page_break()

        toc_title = document.add_paragraph("目录", style="Heading 1")
        toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        toc = document.add_paragraph()
        toc_field = OxmlElement("w:fldSimple")
        toc_field.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
        toc._p.append(toc_field)
        document.add_page_break()

        in_code = False
        code_lines: list[str] = []
        for line in content.splitlines()[1:]:
            if line.startswith("```"):
                if in_code:
                    self._add_code_or_flow(document, code_lines)
                    code_lines = []
                in_code = not in_code
                continue
            if in_code:
                code_lines.append(line)
                continue
            heading = re.match(r"^(#{2,6})\s+(.+)$", line)
            if heading:
                document.add_heading(
                    _strip_markup(heading.group(2)),
                    level=min(len(heading.group(1)) - 1, 4),
                )
                continue
            if not line.strip():
                continue
            if line.lstrip().startswith("|"):
                continue
            item = re.match(r"^(\s*)(\d+\.\s+|-\s+)(.+)$", line)
            paragraph = document.add_paragraph(
                style=(
                    "List Number" if item and item.group(2)[0].isdigit()
                    else "List Bullet" if item else None
                )
            )
            text = item.group(3) if item else line.lstrip("> ")
            paragraph.add_run(_strip_markup(text))

        for kind, value in MarkdownTableParser.split_document(content):
            if kind != "table":
                continue
            rows = value.values
            table = document.add_table(rows=len(rows), cols=len(rows[0]))
            table.style = "Light Shading Accent 1"
            table.autofit = True
            for row_index, row in enumerate(rows):
                for column_index, cell in enumerate(row):
                    target = table.cell(row_index, column_index)
                    target.text = cell
                    if row_index == 0:
                        target.paragraphs[0].runs[0].bold = True

        buffer = io.BytesIO()
        document.save(buffer)
        data = buffer.getvalue()
        return (
            base64.b64encode(data).decode("ascii"),
            {
                "rendered": True,
                "renderer": "aesthetic_docx",
                "output_format": "docx",
                "media_type": (
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                "encoding": "base64",
                "byte_count": len(data),
                "editable": True,
                "style_profile": "professional_blue",
                "provenance": [
                    "https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-docx",
                    "https://clawhub.ai/ivangdavila/word-docx",
                ],
            },
        )

    @staticmethod
    def _add_code_or_flow(document, lines: list[str]) -> None:
        if lines and lines[0].strip().startswith("flowchart"):
            paragraph = document.add_paragraph()
            paragraph.style = "Intense Quote"
            flow_lines = [
                re.sub(r"^\s*N\d+\[\"|\"\]\s*$", "", line).strip()
                for line in lines[1:]
                if '["' in line
            ]
            paragraph.add_run("  →  ".join(filter(None, flow_lines)) or "结构化流程图")
            return
        paragraph = document.add_paragraph()
        run = paragraph.add_run("\n".join(lines))
        run.font.name = "Consolas"
        run.font.size = 8


class SlidesRenderer(DocumentRenderer):
    """Generate self-contained HTML slides or editable PPTX."""

    def render(self, *, content, output_format, visualizations):
        if output_format == "slides_html":
            rendered = self._html(content)
            return (
                rendered,
                {
                    "rendered": True,
                    "renderer": "northstar_html_slides",
                    "output_format": "slides_html",
                    "media_type": "text/html",
                    "encoding": "utf-8",
                    "slide_count": len(_slide_sections(content)),
                    "self_contained": True,
                    "provenance": [
                        "https://github.com/zarazhangrui/frontend-slides",
                        "https://github.com/marp-team/marp",
                    ],
                },
            )
        if output_format != "pptx":
            raise ValueError(f"SlidesRenderer 不支持: {output_format}")
        return self._pptx(content)

    @staticmethod
    def _html(content: str) -> str:
        sections = _slide_sections(content)
        slides = []
        for index, (title, body) in enumerate(sections):
            paragraphs = [
                _strip_markup(line)
                for line in body.splitlines()
                if line.strip() and not line.startswith(("|", "```", "<a "))
            ][:8]
            body_html = "".join(f"<p>{html.escape(item)}</p>" for item in paragraphs)
            slides.append(
                f'<section class="slide{" active" if index == 0 else ""}">'
                f"<h1>{html.escape(title)}</h1>{body_html}"
                f'<span class="page">{index + 1}/{len(sections)}</span></section>'
            )
        return """<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>研究报告汇报</title><style>
*{box-sizing:border-box}body{margin:0;background:#0b1220;color:#eaf2ff;
font-family:Inter,"Microsoft YaHei",sans-serif}.slide{display:none;width:100vw;
height:100vh;padding:8vh 8vw;background:linear-gradient(135deg,#0b1220,#17365d)}
.slide.active{display:block}.slide h1{font-size:4vw;margin:0 0 5vh;color:#8fc7ff}
.slide p{font-size:1.65vw;line-height:1.6;max-width:84vw}.page{position:absolute;
right:4vw;bottom:3vh;color:#8aa4c4}nav{position:fixed;left:3vw;bottom:3vh}
button{padding:.6rem 1rem;margin-right:.5rem;background:#2f75b5;color:white;
border:0;border-radius:.4rem}</style><body>""" + "".join(slides) + """
<nav><button onclick="move(-1)">上一页</button><button onclick="move(1)">下一页</button></nav>
<script>let i=0,s=[...document.querySelectorAll('.slide')];function move(d){
s[i].classList.remove('active');i=(i+d+s.length)%s.length;s[i].classList.add('active')}
addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key===' ')move(1);
if(e.key==='ArrowLeft')move(-1)});</script></body></html>"""

    @staticmethod
    def _pptx(content: str):
        try:
            from pptx import Presentation
            from pptx.dml.color import RGBColor
            from pptx.enum.text import PP_ALIGN
            from pptx.util import Inches, Pt
        except ImportError as exc:
            raise RuntimeError(
                "PPTX渲染需要安装可选依赖: pip install python-pptx"
            ) from exc
        presentation = Presentation()
        presentation.slide_width = Inches(13.333)
        presentation.slide_height = Inches(7.5)
        sections = _slide_sections(content)
        for index, (title, body) in enumerate(sections):
            slide = presentation.slides.add_slide(
                presentation.slide_layouts[6]
            )
            background = slide.background.fill
            background.solid()
            background.fore_color.rgb = RGBColor(11, 18, 32)
            title_box = slide.shapes.add_textbox(
                Inches(0.8), Inches(0.6), Inches(11.7), Inches(1.0)
            )
            title_frame = title_box.text_frame
            title_frame.text = title
            title_frame.paragraphs[0].font.size = Pt(28 if index else 34)
            title_frame.paragraphs[0].font.bold = True
            title_frame.paragraphs[0].font.color.rgb = RGBColor(143, 199, 255)
            title_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
            body_box = slide.shapes.add_textbox(
                Inches(0.9), Inches(1.8), Inches(11.4), Inches(4.8)
            )
            frame = body_box.text_frame
            frame.word_wrap = True
            paragraphs = [
                _strip_markup(line)
                for line in body.splitlines()
                if line.strip()
                and not line.startswith(("|", "```", "<a ", "> **表格说明"))
            ][:8]
            if not paragraphs and index == 0:
                paragraphs = ["专业研究汇报", date.today().isoformat()]
            for paragraph_index, item in enumerate(paragraphs):
                paragraph = frame.paragraphs[0] if paragraph_index == 0 else frame.add_paragraph()
                paragraph.text = item
                paragraph.font.size = Pt(17)
                paragraph.font.color.rgb = RGBColor(234, 242, 255)
                paragraph.space_after = Pt(8)
            slide.shapes.add_textbox(
                Inches(11.8), Inches(6.9), Inches(0.8), Inches(0.3)
            ).text_frame.text = str(index + 1)
        buffer = io.BytesIO()
        presentation.save(buffer)
        data = buffer.getvalue()
        return (
            base64.b64encode(data).decode("ascii"),
            {
                "rendered": True,
                "renderer": "northstar_pptx",
                "output_format": "pptx",
                "media_type": (
                    "application/vnd.openxmlformats-officedocument."
                    "presentationml.presentation"
                ),
                "encoding": "base64",
                "byte_count": len(data),
                "slide_count": len(sections),
                "editable": True,
                "provenance": [
                    "https://github.com/zarazhangrui/frontend-slides",
                    "https://github.com/marp-team/marp",
                ],
            },
        )
