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
    recipients = data.get("messages")
    if not isinstance(recipients, list) or not recipients:
        raise ValueError("Payload must contain a non-empty messages list.")
    if len(recipients) > 10:
        raise ValueError("Safety gate: no more than 10 messages per payload.")
    return data


def send_one(server: smtplib.SMTP, sender: str, item: dict, attachment: bytes) -> None:
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
        filename="Ragunauth_Ramsaroop_Executive_CV_2026.pdf",
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
    build_cv_pdf(CV_SOURCE, CV_PDF)
    attachment = CV_PDF.read_bytes()

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender, password)
        for item in payload["messages"]:
            send_one(server, sender, item, attachment)


if __name__ == "__main__":
    main()
