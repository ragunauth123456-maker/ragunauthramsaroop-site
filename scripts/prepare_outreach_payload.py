#!/usr/bin/env python3
"""Prepare and validate outreach payloads before SMTP send.

Executive-company outreach must use a bespoke strategic value brief addressed to a
named senior decision-maker. The final attachment is the strategic brief followed by
Ragunauth Ramsaroop's three-page executive CV.

Recruiter and ATS/application campaigns remain CV-first and are not converted here.
"""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from send_icloud_smtp import CV_SOURCE, build_cv_pdf, build_overlay_source

POLICY_VERSION = "executive-whitepaper-v1"
GENERATED_DIR = Path("career-assets/outreach-pdfs/generated")

PERSONAL_DOMAINS = {
    "gmail.com", "yahoo.com", "icloud.com", "hotmail.com", "outlook.com",
    "proton.me", "aol.com", "live.com",
}

GENERIC_LOCAL_PARTS = {
    "press", "media", "mediarelations", "media.relations", "communications",
    "communication", "corpcomm", "corporatecommunications", "corporatecomms",
    "pr", "publicrelations", "investor", "investors", "investorrelations",
    "investor.relations", "ir", "careers", "career", "jobs", "job", "talent",
    "recruitment", "recruiting", "recruit", "hr", "humanresources", "info",
    "information", "contact", "contactus", "hello", "support", "sales",
    "enquiry", "enquiries", "office", "admin", "team", "executiveoffice",
    "ceo", "president", "chairman", "chair", "leadership",
}

GENERIC_TOKENS = (
    "press", "media", "relations", "communications", "comms", "investor",
    "recruit", "career", "talent", "humanresources", "publicrelations",
)

SENIOR_TITLE = re.compile(
    r"\b(ceo|chief\b|president\b|chair(?:man|woman)?\b|managing director\b|"
    r"country director\b|country manager\b|executive vice president\b|evp\b|"
    r"senior vice president\b|svp\b|vice president\b|vp\b|head of\b|"
    r"group director\b|regional director\b|executive director\b)"
    , re.IGNORECASE,
)


def https_url(value: object) -> bool:
    parsed = urlparse(str(value or "").strip())
    return parsed.scheme == "https" and bool(parsed.hostname)


def safe_slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_")
    return text[:80] or "Executive"


def clean_text(value: object) -> str:
    text = str(value or "").strip()
    return (
        text.replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .replace("\u00a0", " ")
    )


def generic_address(address: str) -> bool:
    local = address.split("@", 1)[0].lower().strip()
    compact = re.sub(r"[^a-z0-9]", "", local)
    if local in GENERIC_LOCAL_PARTS or compact in {re.sub(r"[^a-z0-9]", "", x) for x in GENERIC_LOCAL_PARTS}:
        return True
    return any(token in compact for token in GENERIC_TOKENS)


def validate_executive_recipient(item: dict) -> None:
    address = clean_text(item.get("to")).lower()
    if "@" not in address:
        raise ValueError("Executive outreach requires one valid recipient email address.")
    domain = address.rsplit("@", 1)[1]
    if domain in PERSONAL_DOMAINS:
        raise ValueError("Executive outreach requires a verified company business email, not a personal mailbox.")
    if generic_address(address):
        raise ValueError(f"Generic or functional inbox is blocked for executive outreach: {address}")

    name = clean_text(item.get("recipient_name"))
    title = clean_text(item.get("recipient_title"))
    if len(name.split()) < 2 or any(word in name.lower() for word in ("team", "office", "leadership")):
        raise ValueError("Executive outreach requires a named individual recipient.")
    if not SENIOR_TITLE.search(title):
        raise ValueError("Recipient title is not sufficiently senior for executive-company outreach.")
    if item.get("email_verified") is not True:
        raise ValueError("Executive recipient business email must be marked email_verified=true.")
    if not clean_text(item.get("email_verification_source")):
        raise ValueError("Executive recipient requires an email_verification_source.")
    if not https_url(item.get("recipient_role_source_url")):
        raise ValueError("Executive recipient requires a current-role source URL.")


def validate_brief(brief: dict) -> None:
    required_text = {
        "company": 1,
        "title": 4,
        "executive_summary": 60,
        "company_context": 80,
    }
    for key, min_words in required_text.items():
        value = clean_text(brief.get(key))
        if len(value.split()) < min_words:
            raise ValueError(f"strategic_brief.{key} is missing or too thin.")

    opportunities = brief.get("opportunities")
    if not isinstance(opportunities, list) or not (3 <= len(opportunities) <= 5):
        raise ValueError("strategic_brief.opportunities must contain 3 to 5 company-specific opportunities.")
    for index, item in enumerate(opportunities, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Opportunity {index} must be an object.")
        if len(clean_text(item.get("title")).split()) < 2:
            raise ValueError(f"Opportunity {index} needs a specific title.")
        if len(clean_text(item.get("rationale")).split()) < 25:
            raise ValueError(f"Opportunity {index} rationale is too thin.")
        if len(clean_text(item.get("how_i_can_help")).split()) < 20:
            raise ValueError(f"Opportunity {index} needs a substantive value contribution.")

    framework = brief.get("action_framework")
    if not isinstance(framework, dict):
        raise ValueError("strategic_brief.action_framework is required.")
    for key in ("days_0_30", "days_31_60", "days_61_90", "days_91_180"):
        value = framework.get(key)
        if not value:
            raise ValueError(f"strategic_brief.action_framework.{key} is required.")

    for key, minimum in (("potential_impact", 3), ("background_relevance", 3)):
        values = brief.get(key)
        if not isinstance(values, list) or len(values) < minimum:
            raise ValueError(f"strategic_brief.{key} must contain at least {minimum} items.")

    sources = brief.get("sources")
    if not isinstance(sources, list) or len(sources) < 3:
        raise ValueError("strategic_brief.sources must contain at least 3 dated sources.")
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise ValueError(f"Source {index} must be an object.")
        if not clean_text(source.get("title")) or not clean_text(source.get("published_at")):
            raise ValueError(f"Source {index} requires title and published_at.")
        if not https_url(source.get("url")):
            raise ValueError(f"Source {index} requires a valid HTTPS URL.")


def register_fonts() -> tuple[str, str]:
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if Path(regular).is_file() and Path(bold).is_file():
            pdfmetrics.registerFont(TTFont("ExecRegular", regular))
            pdfmetrics.registerFont(TTFont("ExecBold", bold))
            return "ExecRegular", "ExecBold"
    except Exception:
        pass
    return "Helvetica", "Helvetica-Bold"


def build_whitepaper_pdf(brief: dict, output: Path) -> None:
    regular_font, bold_font = register_fonts()
    styles = getSampleStyleSheet()

    cover = ParagraphStyle(
        "Cover", parent=styles["Title"], fontName=bold_font,
        fontSize=24, leading=29, alignment=TA_CENTER,
        textColor=colors.HexColor("#142743"), spaceAfter=10,
    )
    cover_sub = ParagraphStyle(
        "CoverSub", parent=styles["Normal"], fontName=regular_font,
        fontSize=11, leading=15, alignment=TA_CENTER,
        textColor=colors.HexColor("#4B5563"), spaceAfter=8,
    )
    heading = ParagraphStyle(
        "Heading", parent=styles["Heading1"], fontName=bold_font,
        fontSize=16, leading=20, textColor=colors.HexColor("#142743"),
        spaceAfter=8,
    )
    subheading = ParagraphStyle(
        "Subheading", parent=styles["Heading2"], fontName=bold_font,
        fontSize=11.5, leading=15, textColor=colors.HexColor("#8A6425"),
        spaceBefore=5, spaceAfter=4,
    )
    body = ParagraphStyle(
        "Body", parent=styles["BodyText"], fontName=regular_font,
        fontSize=9.3, leading=13.2, textColor=colors.HexColor("#1F2937"),
        spaceAfter=6,
    )
    bullet = ParagraphStyle(
        "Bullet", parent=body, leftIndent=11, firstLineIndent=-7,
        spaceAfter=4,
    )
    source_style = ParagraphStyle(
        "Source", parent=body, fontSize=7.6, leading=10.2,
        textColor=colors.HexColor("#4B5563"), spaceAfter=3,
    )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(regular_font, 7)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(15 * mm, 9 * mm, f"Strategic Value Creation Brief | {clean_text(brief['company'])}")
        canvas.drawRightString(195 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output), pagesize=A4,
        rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=15 * mm, bottomMargin=16 * mm,
        title=clean_text(brief["title"]),
        author="Ragunauth Ramsaroop",
    )

    story = []
    company = clean_text(brief["company"])
    prepared_for = clean_text(brief.get("prepared_for"))
    prepared_for_title = clean_text(brief.get("prepared_for_title"))

    story += [
        Spacer(1, 32 * mm),
        Paragraph(escape(clean_text(brief["title"])), cover),
        Paragraph(escape(company), cover_sub),
        Spacer(1, 8 * mm),
    ]
    if prepared_for:
        story.append(Paragraph(escape(f"Prepared for {prepared_for}"), cover_sub))
    if prepared_for_title:
        story.append(Paragraph(escape(prepared_for_title), cover_sub))
    story += [
        Spacer(1, 18 * mm),
        Paragraph("Prepared by Ragunauth Ramsaroop", cover_sub),
        Paragraph("Executive strategy | Government relations | ESG | Stakeholder leadership", cover_sub),
        PageBreak(),
    ]

    story += [
        Paragraph("Executive Brief", heading),
        Paragraph(escape(clean_text(brief["executive_summary"])), body),
        Spacer(1, 4 * mm),
        Paragraph("Purpose", subheading),
        Paragraph(
            escape(
                "This paper is designed as a practical executive discussion document. It identifies specific areas where my operating experience in government relations, ESG, corporate affairs, strategic partnerships and regulated-market stakeholder execution may support the company's priorities."
            ),
            body,
        ),
        PageBreak(),
        Paragraph("Company Strategic Context", heading),
        Paragraph(escape(clean_text(brief["company_context"])), body),
        PageBreak(),
        Paragraph("Strategic Opportunities", heading),
    ]

    opportunities = brief["opportunities"]
    split = 2 if len(opportunities) >= 4 else len(opportunities)
    for index, item in enumerate(opportunities, start=1):
        block = [
            Paragraph(escape(f"{index}. {clean_text(item['title'])}"), subheading),
            Paragraph(escape(clean_text(item["rationale"])), body),
            Paragraph("How I can add value", subheading),
            Paragraph(escape(clean_text(item["how_i_can_help"])), body),
        ]
        story.append(KeepTogether(block))
        if index == split and index < len(opportunities):
            story += [PageBreak(), Paragraph("Strategic Opportunities - Continued", heading)]

    story += [
        PageBreak(),
        Paragraph("90-180 Day Action Framework", heading),
    ]
    labels = (
        ("days_0_30", "Days 0-30 | Diagnose and map"),
        ("days_31_60", "Days 31-60 | Prioritize and align"),
        ("days_61_90", "Days 61-90 | Execute and institutionalize"),
        ("days_91_180", "Days 91-180 | Scale, measure and embed"),
    )
    framework = brief["action_framework"]
    for key, label in labels:
        story.append(Paragraph(escape(label), subheading))
        value = framework[key]
        if isinstance(value, list):
            for point in value:
                story.append(Paragraph("- " + escape(clean_text(point)), bullet))
        else:
            story.append(Paragraph(escape(clean_text(value)), body))

    story += [
        PageBreak(),
        Paragraph("Potential Business Impact", heading),
    ]
    for point in brief["potential_impact"]:
        story.append(Paragraph("- " + escape(clean_text(point)), bullet))

    story += [
        Spacer(1, 3 * mm),
        Paragraph("Why My Background Is Relevant", heading),
    ]
    for point in brief["background_relevance"]:
        story.append(Paragraph("- " + escape(clean_text(point)), bullet))

    story += [
        PageBreak(),
        Paragraph("Research Sources", heading),
        Paragraph(
            "The strategic observations above are based on publicly available information and are intended to support an executive discussion, not to imply access to non-public company information.",
            body,
        ),
    ]
    for index, source in enumerate(brief["sources"], start=1):
        citation = f"{index}. {clean_text(source['title'])} | {clean_text(source['published_at'])} | {clean_text(source['url'])}"
        story.append(Paragraph(escape(citation), source_style))

    story += [
        Spacer(1, 5 * mm),
        Paragraph("Supporting Executive Profile", heading),
        Paragraph(
            "The following three pages contain my executive CV as supporting evidence of the experience referenced in this paper.",
            body,
        ),
    ]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def build_cv(payload: dict, output: Path) -> None:
    overlay = payload.get("cv_overlay")
    if overlay is not None:
        if not isinstance(overlay, dict):
            raise ValueError("cv_overlay must be an object.")
        source = build_overlay_source(
            CV_SOURCE,
            overlay,
            Path("/tmp/Ragunauth_Ramsaroop_Executive_Whitepaper_CV.md"),
        )
    else:
        source = CV_SOURCE
    build_cv_pdf(source, output)
    pages = len(PdfReader(str(output)).pages)
    if pages != 3:
        raise ValueError(f"Executive white-paper mode requires the CV to be exactly 3 pages; generated CV has {pages} pages.")


def merge_pdf(whitepaper: Path, cv: Path, output: Path) -> None:
    writer = PdfWriter()
    for page in PdfReader(str(whitepaper)).pages:
        writer.add_page(page)
    cv_reader = PdfReader(str(cv))
    if len(cv_reader.pages) != 3:
        raise ValueError("Final CV append check failed: CV is not 3 pages.")
    for page in cv_reader.pages:
        writer.add_page(page)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        writer.write(handle)

    final_reader = PdfReader(str(output))
    if len(final_reader.pages) < 9:
        raise ValueError("Combined executive attachment is unexpectedly short.")


def prepare_single(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("approved") is not True:
        raise ValueError(f"{path}: approved=true is required.")

    campaign_type = payload.get("campaign_type")
    if campaign_type in {"recruiter", "ats_application"}:
        print(f"PREPARED {path}: {campaign_type} campaign remains CV-first.")
        return
    if campaign_type != "executive_company":
        raise ValueError(
            f"{path}: campaign_type is required. Use executive_company, recruiter, or ats_application. "
            "Legacy untyped company outreach is blocked."
        )

    messages = payload.get("messages")
    if not isinstance(messages, list) or len(messages) != 1:
        raise ValueError("Executive-company payloads must contain exactly one company-specific message.")
    validate_executive_recipient(messages[0])

    brief = payload.get("strategic_brief")
    if not isinstance(brief, dict):
        raise ValueError("Executive-company outreach requires strategic_brief.")
    validate_brief(brief)

    company = clean_text(brief["company"])
    recipient = clean_text(messages[0]["recipient_name"])
    brief["prepared_for"] = brief.get("prepared_for") or recipient
    brief["prepared_for_title"] = brief.get("prepared_for_title") or clean_text(messages[0]["recipient_title"])

    whitepaper = Path("/tmp/executive_value_brief.pdf")
    cv = Path("/tmp/executive_value_cv.pdf")
    build_whitepaper_pdf(brief, whitepaper)
    build_cv(payload, cv)

    filename = f"Ragunauth_Ramsaroop_{safe_slug(company)}_Strategic_Value_Brief_2026.pdf"
    output = GENERATED_DIR / filename
    merge_pdf(whitepaper, cv, output)

    payload["strategic_brief"] = brief
    payload["attachment_path"] = str(output)
    payload["attachment_filename"] = filename
    payload["outreach_policy_version"] = POLICY_VERSION
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    total_pages = len(PdfReader(str(output)).pages)
    print(f"PREPARED {path}: executive strategic brief + 3-page CV, {total_pages} total pages -> {output}")


def prepare(path: Path) -> None:
    if path.name.endswith(".secure.json"):
        print(f"PREPARED {path}: encrypted recruiter workflow unchanged.")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    if path.name.endswith(".batch.json"):
        files = data.get("payload_files")
        if not isinstance(files, list) or not files:
            raise ValueError("Batch manifest requires payload_files.")
        for raw in files:
            child = Path(str(raw))
            if not child.is_file():
                raise ValueError(f"Batch payload not found: {child}")
            prepare_single(child)
        return

    prepare_single(path)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: prepare_outreach_payload.py <payload.json>")
    path = Path(sys.argv[1])
    if not path.is_file():
        raise SystemExit(f"Payload not found: {path}")
    prepare(path)


if __name__ == "__main__":
    main()
