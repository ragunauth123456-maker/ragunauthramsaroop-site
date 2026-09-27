#!/usr/bin/env python3
"""Typeset the actual editable Guyana manuscript and source register as a working PDF.

This is a report builder, not a research agent or a peer-review substitute.
Use on GitHub-hosted Actions only. Dependencies: reportlab, pymupdf.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle, Flowable,
)
from reportlab.platypus.tableofcontents import TableOfContents
import fitz

BASE = Path(__file__).resolve().parent
NAVY = colors.HexColor("#14283b")
FOREST = colors.HexColor("#155847")
SAGE = colors.HexColor("#dcece4")
TEXT = colors.HexColor("#243444")
GRAY = colors.HexColor("#647688")

font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
font_bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
if font_path.exists() and font_bold.exists():
    pdfmetrics.registerFont(TTFont("Research", str(font_path)))
    pdfmetrics.registerFont(TTFont("ResearchBold", str(font_bold)))
    pdfmetrics.registerFontFamily("Research", normal="Research", bold="ResearchBold")
    FONTA, FONTB = "Research", "ResearchBold"
else:
    FONTA, FONTB = "Helvetica", "Helvetica-Bold"

s = getSampleStyleSheet()
s.add(ParagraphStyle(name="CoverKicker2", fontName=FONTB, fontSize=10, leading=16,
                     textColor=FOREST, spaceAfter=16, uppercase=True))
s.add(ParagraphStyle(name="CoverTitle2", fontName=FONTB, fontSize=28, leading=37,
                     textColor=NAVY, spaceAfter=20))
s.add(ParagraphStyle(name="CoverSubtitle2", fontName=FONTA, fontSize=13,
                     leading=20, textColor=TEXT, spaceAfter=24))
s.add(ParagraphStyle(name="Body2", fontName=FONTA, fontSize=9.4, leading=15.2,
                     textColor=TEXT, alignment=TA_LEFT, spaceAfter=8,
                     allowWidows=0, allowOrphans=0, splitLongWords=1))
s.add(ParagraphStyle(name="H12", fontName=FONTB, fontSize=17, leading=22,
                     textColor=NAVY, spaceBefore=22, spaceAfter=10, keepWithNext=1))
s.add(ParagraphStyle(name="H22", fontName=FONTB, fontSize=12.2, leading=17,
                     textColor=FOREST, spaceBefore=17, spaceAfter=8, keepWithNext=1))
s.add(ParagraphStyle(name="H32", fontName=FONTB, fontSize=10.5, leading=15,
                     textColor=NAVY, spaceBefore=11, spaceAfter=6, keepWithNext=1))
s.add(ParagraphStyle(name="Bullet2", parent=s["Body2"], leftIndent=18,
                     firstLineIndent=-11, spaceAfter=5))
s.add(ParagraphStyle(name="Ref2", fontName=FONTA, fontSize=8.1, leading=13,
                     textColor=TEXT, leftIndent=8, firstLineIndent=-8, spaceAfter=9,
                     splitLongWords=1))
s.add(ParagraphStyle(name="Small2", fontName=FONTA, fontSize=8.1, leading=12,
                     textColor=GRAY, spaceAfter=5))
s.add(ParagraphStyle(name="TocEntry2", fontName=FONTA, fontSize=10, leading=18,
                     textColor=TEXT, leftIndent=18, firstLineIndent=-18))

def markup(raw: str) -> str:
    value = html.escape(raw)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\[S(\d\d)\]", r'<font color="#155847">[S\1]</font>', value)
    return value.replace("  ", " ")

class Rule(Flowable):
    def __init__(self, width=166*mm):
        Flowable.__init__(self)
        self.width, self.height = width, 2*mm
    def draw(self):
        self.canv.setStrokeColor(FOREST)
        self.canv.setLineWidth(2)
        self.canv.line(0, 1*mm, self.width, 1*mm)

class Report(BaseDocTemplate):
    def __init__(self, path: Path):
        super().__init__(str(path), pagesize=A4, leftMargin=21*mm,
                         rightMargin=21*mm, topMargin=21*mm,
                         bottomMargin=20*mm, title="The Guyana Sequence: Working Research Edition",
                         author="Ragunauth Ramsaroop", allowSplitting=1)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width,
                      self.height, id="normal")
        self.addPageTemplates([PageTemplate(id="normal", frames=frame,
                                            onPage=self.page_background)])
        self.heading_counter = 0

    def beforeDocument(self):
        # multiBuild reuses this document instance across TOC layout passes.
        # Stable heading keys are required for second-pass TOC convergence.
        self.heading_counter = 0

    def page_background(self, canvas, doc):
        canvas.saveState()
        if doc.page == 1:
            canvas.setFillColor(FOREST)
            canvas.rect(0, 0, 10*mm, A4[1], stroke=0, fill=1)
        else:
            canvas.setStrokeColor(SAGE)
            canvas.line(21*mm, 15*mm, A4[0]-21*mm, 15*mm)
            canvas.setFont(FONTA, 7)
            canvas.setFillColor(GRAY)
            canvas.drawString(21*mm, 10.5*mm, "INDEPENDENT RESEARCH | WORKING DRAFT | 27 SEP 2026")
            canvas.drawRightString(A4[0]-21*mm, 10.5*mm, f"{doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flow):
        if isinstance(flow, Paragraph) and getattr(flow, "toc_level", None) is not None:
            self.heading_counter += 1
            name = f"heading_{self.heading_counter}"
            self.canv.bookmarkPage(name)
            self.notify("TOCEntry", (flow.toc_level, flow.getPlainText(), self.page, name))
            self.canv.addOutlineEntry(flow.getPlainText()[:100], name,
                                      level=min(flow.toc_level, 1), closed=False)

def top_heading(title: str) -> Paragraph:
    heading = Paragraph(markup(title), s["H12"])
    heading.toc_level = 0
    return heading


def markdown_flow(text: str, max_level=2) -> list:
    story, pending = [], []
    def flush():
        if pending:
            story.append(Paragraph(markup(" ".join(pending)), s["Body2"]))
            pending.clear()
    for line in text.splitlines():
        val = line.strip()
        if not val:
            flush()
            continue
        if val.startswith("# "):
            flush()
            p = Paragraph(markup(val[2:]), s["H12"])
            p.toc_level = 0
            story.append(p)
        elif val.startswith("## "):
            flush()
            p = Paragraph(markup(val[3:]), s["H12"])
            p.toc_level = 0
            story.append(p)
        elif val.startswith("### "):
            flush()
            p = Paragraph(markup(val[4:]), s["H22"])
            p.toc_level = 1
            story.append(p)
        elif val.startswith("**") and val.endswith("**") and len(val) < 130:
            flush()
            story.append(Paragraph(markup(val), s["H32"]))
        elif val.startswith(("- ", "* ")):
            flush()
            story.append(Paragraph("&#8226; " + markup(val[2:]), s["Bullet2"]))
        elif re.match(r"^\d+\.\s", val):
            flush()
            story.append(Paragraph(markup(val), s["Bullet2"]))
        elif val.startswith("|"):
            flush()
            # Markdown source register rendered later as tagged bibliography.
            pass
        else:
            pending.append(val)
    flush()
    return story

def add_snapshot(story: list) -> None:
    story.append(Paragraph("2026 observation snapshot", s["H12"]))
    rows = [
        ["2015", "May Liza commercial discovery", "[S01]"],
        ["Jan 2019", "NRF statute assented before first oil", "[S04]"],
        ["Dec 2019", "Liza Phase 1 first oil", "[S01]"],
        ["Aug 2025", "Yellowtail became fourth producing FPSO", "[S11]"],
        ["Jun 2026", "End-June NRF cash: USD 4.2942 billion", "[S07]"],
        ["Jun 2026", "H1 authorized withdrawals: USD 1.02 billion", "[S07]"],
    ]
    grid = [[Paragraph(markup(x), s["Small2"]) for x in row] for row in rows]
    t = Table(grid, colWidths=[25*mm, 122*mm, 17*mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, SAGE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([t, Spacer(1, 8*mm)])
    story.append(Paragraph(
        "Dates refer to distinct events. Production capacity is not actual annual output. "
        "Fund cash is not contracted or forecast future revenue.", s["Small2"]))

def add_revenue_exhibit(story: list):
    story.append(Paragraph("Worked fiscal exhibit: simplified 2016 Stabroek waterfall", s["H12"]))
    story.append(Paragraph(
        "Using the Guyana Revenue Authority's illustrative gross-revenue convention, "
        "royalty is separate and borne by the contractor group. A 75% cost-recovery "
        "cap is a maximum, not a permanent claim on every barrel. Values below are "
        "illustrative units out of 100, not observed 2026 receipts. [S02, S15]", s["Body2"]))
    rows = [["Recovery used", "State profit oil", "State royalty", "Combined state units"],
            ["75% (cap binding)", "12.5", "2.0", "14.5"],
            ["50% (illustrative)", "25.0", "2.0", "27.0"],
            ["20% (illustrative)", "40.0", "2.0", "42.0"]]
    grid = [[Paragraph(markup(cell), s["Small2"]) for cell in row] for row in rows]
    t = Table(grid, colWidths=[47*mm, 40*mm, 36*mm, 43*mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SAGE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, FOREST),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([t, Spacer(1, 7*mm)])

def source_entries(source_text: str) -> list:
    rows = []
    for line in source_text.splitlines():
        if re.match(r"^\|\s*S\d\d\s*\|", line):
            cells = [v.strip() for v in line.strip().strip("|").split("|")]
            if len(cells) >= 5:
                rows.append(cells[:5])
    assert len(rows) >= 25, f"Insufficient source records: {len(rows)}"
    return rows

def build() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(BASE/"working-research-edition.pdf"))
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    manuscript = (BASE/"MANUSCRIPT_WORKING_DRAFT.md").read_text(encoding="utf-8")
    brief = (BASE/"EXECUTIVE_BRIEF.md").read_text(encoding="utf-8")
    playbook = (BASE/"COUNTRY_PLAYBOOK.md").read_text(encoding="utf-8")
    sources = (BASE/"SOURCE_REGISTER.md").read_text(encoding="utf-8")
    assert len(manuscript.split()) > 6500, "Do not render an empty/placeholder manuscript"

    story = [Spacer(1, 23*mm),
             Paragraph("GUYANA | EXPLORATION TO PRODUCTION", s["CoverKicker2"]),
             Paragraph("THE GUYANA<br/>SEQUENCE", s["CoverTitle2"]),
             Rule(),
             Spacer(1, 7*mm),
             Paragraph("Petroleum Governance, Environmental Stewardship, "
                       "Natural Resource Fund Design and Lessons for Emerging Producers",
                       s["CoverSubtitle2"]),
             Spacer(1, 11*mm),
             Paragraph("Independent research by Ragunauth Ramsaroop", s["H22"]),
             Paragraph("Working research edition | 27 September 2026", s["Body2"]),
             Paragraph("First researched chapters and a documented source register. "
                       "The full 140-160 substantive-page publication and external "
                       "expert review remain pending.", s["Small2"]),
             Spacer(1, 8*mm),
             Paragraph("Source evidence cut-off: 27 September 2026. "
                       "Observed 2026 financial data are through June unless indicated.", s["Small2"]),
             PageBreak(),
             Paragraph("Contents", s["H12"])]
    toc = TableOfContents()
    toc.levelStyles = [s["TocEntry2"], s["TocEntry2"]]
    story.extend([toc, PageBreak(),
                  top_heading("Executive research brief")])
    story.extend(markdown_flow("\n".join(brief.splitlines()[3:])))
    story.append(PageBreak())
    add_snapshot(story)
    add_revenue_exhibit(story)
    story.extend([PageBreak(), top_heading("Substantive manuscript")])
    # Omit duplicated cover headings; start at the abstract.
    start = manuscript.find("### Abstract")
    story.extend(markdown_flow(manuscript[start:] if start != -1 else manuscript))
    story.extend([PageBreak(), top_heading("Transferable country handbook")])
    # The handbook is an original substantive companion annex, not repeated boilerplate.
    story.extend(markdown_flow(playbook))
    story.extend([PageBreak(), top_heading("Source register"),
                  Paragraph("Dated source IDs correspond to citations in the manuscript. "
                            "Public URLs link to originals. Key unresolved verification "
                            "tasks appear after the register.", s["Body2"])])
    source_rows = source_entries(sources)
    for ident, label, evidence, caveat, url in source_rows:
        safe_url = html.escape(url, quote=True)
        piece = (f'<b>{html.escape(ident)}</b>  {html.escape(label)}<br/>'
                 f'{html.escape(evidence)}<br/>'
                 f'<font color="#647688">Limit: {html.escape(caveat)}</font><br/>'
                 f'<link href="{safe_url}" color="#155847">{html.escape(url)}</link>')
        story.append(Paragraph(piece, s["Ref2"]))
    if "### Priority unresolved checks" in sources:
        story.extend([top_heading("Pending verification")] +
                     markdown_flow("### Priority unresolved checks" +
                     sources.split("### Priority unresolved checks", 1)[1]))

    doc = Report(out)
    doc.multiBuild(story)
    pdf = fitz.open(out)
    pages = pdf.page_count
    text_by_page = [p.get_text() for p in pdf]
    flat = "\n".join(text_by_page)
    assert pages >= 18, f"PDF unexpectedly short: {pages} pages"
    assert all(row[0] in flat for row in source_rows), "One or more registered source IDs are missing in PDF"
    assert "Natural Resource Fund" in flat and "Environmental" in flat
    substantive = sum(len(p.split()) >= 100 for p in text_by_page[2:])
    assert substantive >= max(12, int((pages-2)*.70)), (
        f"Too many sparse or filler pages: {substantive}/{pages}")
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    qa = {"document": out.name, "version": "0.1", "stage": "working_research",
          "pages_actual": pages, "manuscript_words": len(manuscript.split()),
          "playbook_words": len(playbook.split()),
          "combined_research_words": len(manuscript.split()) + len(playbook.split()),
          "brief_words": len(brief.split()), "source_records": len(source_rows),
          "substantive_pages_at_least_100_words": substantive,
          "sha256": sha, "citations_embedded": True,
          "external_peer_review": "pending", "full_volume_complete": False}
    (out.parent/"WORKING_PDF_AUDIT.json").write_text(
        json.dumps(qa, indent=2)+"\n", encoding="utf-8")
    for page_no in [0, min(3, pages-1), pages//2, pages-1]:
        pix = pdf[page_no].get_pixmap(matrix=fitz.Matrix(1.4, 1.4))
        pix.save(str(out.parent/f"_preview_{page_no+1}.png"))
    pdf.close()
    print(json.dumps(qa, indent=2))

if __name__ == "__main__":
    build()
