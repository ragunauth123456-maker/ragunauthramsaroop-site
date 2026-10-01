#!/usr/bin/env python3
import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr
from html import escape
from pathlib import Path

SMTP_HOST = "smtp.mail.me.com"
SMTP_PORT = 587
SENDER_NAME = "Ragunauth Ramsaroop"
CV_SOURCE = Path("career-assets/Ragunauth_Ramsaroop_Executive_CV_2026.md")
CV_PDF = Path("/tmp/Ragunauth_Ramsaroop_Executive_CV_2026.pdf")


def build_cv_pdf(source: Path, output: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "CVTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=18, leading=21, spaceAfter=4, alignment=TA_CENTER,
        textColor=colors.HexColor("#111827")
    )
    subtitle = ParagraphStyle(
        "CVSubtitle", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=8.5, leading=11, spaceAfter=5, alignment=TA_CENTER,
        textColor=colors.HexColor("#374151")
    )
    heading = ParagraphStyle(
        "CVHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=10.2, leading=12.5, spaceBefore=6, spaceAfter=3,
        textColor=colors.HexColor("#111827")
    )
    body = ParagraphStyle(
        "CVBody", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=8.2, leading=10.4, spaceAfter=2.7,
        textColor=colors.HexColor("#1f2937")
    )
    bullet = ParagraphStyle(
        "CVBullet", parent=body, leftIndent=10, firstLineIndent=-6,
        bulletIndent=4, spaceAfter=1.8
    )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawString(16 * mm, 9 * mm, "Ragunauth Ramsaroop | Executive CV | 2026")
        canvas.drawRightString(194 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output), pagesize=A4,
        rightMargin=15 * mm, leftMargin=15 * mm,
        topMargin=12 * mm, bottomMargin=15 * mm,
        title="Ragunauth Ramsaroop Executive CV",
        author="Ragunauth Ramsaroop"
    )

    story = []
    lines = source.read_text(encoding="utf-8").splitlines()
    for raw in lines:
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 1.8 * mm))
            continue
        if line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), title))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:]).upper(), heading))
        elif line.startswith("### "):
            story.append(Paragraph(escape(line[4:]), heading))
        elif line.startswith("- "):
            story.append(Paragraph("• " + escape(line[2:]), bullet))
        elif line.startswith("SUBTITLE: "):
            story.append(Paragraph(escape(line.replace("SUBTITLE: ", "", 1)), subtitle))
        else:
            story.append(Paragraph(escape(line), body))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def load_payload(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("approved") is not True:
        raise ValueError("Payload must set approved=true.")
    if data.get("recipients_from_env") is True:
        raw = os.environ.get("ICLOUD_OUTREACH_TO", "").strip()
        recipients = [item.strip() for item in raw.split(",") if item.strip()]
        if not recipients:
            raise ValueError("ICLOUD_OUTREACH_TO is not configured as a GitHub Actions secret.")
        template = data.get("message_template") or {}
        if not isinstance(template.get("subject"), str) or not template["subject"].strip():
            raise ValueError("Secure-recipient payload requires message_template.subject.")
        if not isinstance(template.get("body"), str) or not template["body"].strip():
            raise ValueError("Secure-recipient payload requires message_template.body.")
        data["messages"] = [
            {"to": address, "subject": template["subject"], "body": template["body"]}
            for address in recipients
        ]

    recipients = data.get("messages")
    if not isinstance(recipients, list) or not recipients:
        raise ValueError("Payload must contain a non-empty messages list.")
    if len(recipients) > 10:
        raise ValueError("Safety gate: no more than 10 messages per payload.")
    return data


def send_one(server: smtplib.SMTP, sender: str, item: dict, attachment: bytes, attachment_filename: str) -> None:
    to = item.get("to")
    subject = item.get("subject")
    body = item.get("body")
    if not isinstance(to, str) or "@" not in to:
        raise ValueError("Each message needs one valid recipient address.")
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("Each message needs a subject.")
    if not isinstance(body, str) or not body.strip():
        raise ValueError("Each message needs a body.")

    msg = EmailMessage()
    msg["From"] = formataddr((SENDER_NAME, sender))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Reply-To"] = sender
    msg.set_content(body)
    msg.add_attachment(
        attachment,
        maintype="application",
        subtype="pdf",
        filename=attachment_filename,
    )
    server.send_message(msg, from_addr=sender, to_addrs=[to])
    print(f"Sent iCloud SMTP outreach to {to}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: send_icloud_smtp.py <payload.json>")

    sender = os.environ.get("ICLOUD_SMTP_USER", "").strip()
    password = os.environ.get("ICLOUD_APP_PASSWORD", "").strip()
    if not sender or not password:
        raise SystemExit("Missing ICLOUD_SMTP_USER or ICLOUD_APP_PASSWORD.")

    payload = load_payload(Path(sys.argv[1]))
    if payload.get("dry_run") is True:
        print("Dry run validated. No email was sent.")
        return

    attachment_filename = payload.get("attachment_filename") or "Ragunauth_Ramsaroop_Executive_CV_2026.pdf"
    if not isinstance(attachment_filename, str) or not attachment_filename.lower().endswith(".pdf") or "/" in attachment_filename or "\\" in attachment_filename:
        raise ValueError("attachment_filename must be a simple PDF filename.")

    attachment_path_raw = payload.get("attachment_path")
    if attachment_path_raw is not None:
        if not isinstance(attachment_path_raw, str):
            raise ValueError("attachment_path must be a string.")
        attachment_path = Path(attachment_path_raw)
        if not attachment_path_raw.startswith("career-assets/outreach-pdfs/") or attachment_path.suffix.lower() != ".pdf" or not attachment_path.exists():
            raise ValueError("attachment_path must be an existing PDF under career-assets/outreach-pdfs/.")
        attachment = attachment_path.read_bytes()
    else:
        cv_source_raw = payload.get("cv_source") or str(CV_SOURCE)
        if not isinstance(cv_source_raw, str):
            raise ValueError("cv_source must be a string.")
        cv_source = Path(cv_source_raw)
        if not cv_source_raw.startswith("career-assets/") or cv_source.suffix.lower() != ".md" or not cv_source.exists():
            raise ValueError("cv_source must be an existing Markdown file under career-assets/.")
        build_cv_pdf(cv_source, CV_PDF)
        attachment = CV_PDF.read_bytes()

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender, password)
        for item in payload["messages"]:
            send_one(server, sender, item, attachment, attachment_filename)


if __name__ == "__main__":
    main()
