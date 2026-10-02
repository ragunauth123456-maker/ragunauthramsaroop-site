#!/usr/bin/env python3
import json
import os
import smtplib
import ssl
import sys
from pathlib import Path

from send_icloud_smtp import (
    CV_SOURCE,
    build_cv_pdf,
    build_overlay_source,
    load_payload,
    send_one,
)

SMTP_HOST = "smtp.mail.me.com"
SMTP_PORT = 587


def attachment_for(payload: dict, index: int):
    filename = payload.get("attachment_filename") or "Ragunauth_Ramsaroop_Executive_CV_2026.pdf"
    if not isinstance(filename, str) or not filename.lower().endswith(".pdf") or "/" in filename or "\\" in filename:
        raise ValueError("attachment_filename must be a simple PDF filename.")

    attachment_path_raw = payload.get("attachment_path")
    if attachment_path_raw is not None:
        attachment_path = Path(attachment_path_raw)
        if not isinstance(attachment_path_raw, str) or not attachment_path_raw.startswith("career-assets/outreach-pdfs/") or attachment_path.suffix.lower() != ".pdf" or not attachment_path.exists():
            raise ValueError("attachment_path must be an existing PDF under career-assets/outreach-pdfs/.")
        return attachment_path.read_bytes(), filename

    overlay = payload.get("cv_overlay")
    overlay_path_raw = payload.get("cv_overlay_path")
    if overlay is None and overlay_path_raw is not None:
        overlay_path = Path(overlay_path_raw)
        if not isinstance(overlay_path_raw, str) or not overlay_path_raw.startswith("career-assets/overlays/") or overlay_path.suffix.lower() != ".json" or not overlay_path.exists():
            raise ValueError("cv_overlay_path must be an existing JSON file under career-assets/overlays/.")
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))

    if overlay is not None:
        if not isinstance(overlay, dict):
            raise ValueError("cv_overlay must be an object.")
        source = build_overlay_source(
            CV_SOURCE,
            overlay,
            Path(f"/tmp/Ragunauth_Ramsaroop_Tailored_CV_{index:02d}.md"),
        )
    else:
        source_raw = payload.get("cv_source") or str(CV_SOURCE)
        source = Path(source_raw)
        if not isinstance(source_raw, str) or not source_raw.startswith("career-assets/") or source.suffix.lower() != ".md" or not source.exists():
            raise ValueError("cv_source must be an existing Markdown file under career-assets/.")

    pdf = Path(f"/tmp/Ragunauth_Ramsaroop_Tailored_CV_{index:02d}.pdf")
    build_cv_pdf(source, pdf)
    return pdf.read_bytes(), filename


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: send_icloud_batch.py <manifest.batch.json>")

    manifest_path = Path(sys.argv[1])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("approved") is not True:
        raise ValueError("Batch manifest must set approved=true.")

    files = manifest.get("payload_files")
    if not isinstance(files, list) or not files or len(files) > 30:
        raise ValueError("payload_files must contain 1 to 30 approved payload paths.")

    sender = os.environ.get("ICLOUD_SMTP_USER", "").strip()
    password = os.environ.get("ICLOUD_APP_PASSWORD", "").strip()
    if not sender or not password:
        raise SystemExit("Missing ICLOUD_SMTP_USER or ICLOUD_APP_PASSWORD.")

    prepared = []
    for index, raw in enumerate(files, start=1):
        if not isinstance(raw, str) or not (raw.startswith("outreach/icloud-outbox/") or raw.startswith("outreach/icloud-staged/")) or not raw.endswith(".json") or raw.endswith(".batch.json"):
            raise ValueError(f"Invalid payload path: {raw}")
        path = Path(raw)
        if not path.exists():
            raise ValueError(f"Payload not found: {raw}")
        payload = load_payload(path)
        if payload.get("dry_run") is True:
            raise ValueError(f"Batch refuses dry-run payload: {raw}")
        attachment, filename = attachment_for(payload, index)
        prepared.append((raw, payload, attachment, filename))

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender, password)
        for raw, payload, attachment, filename in prepared:
            for item in payload["messages"]:
                send_one(server, sender, item, attachment, filename)
            print(f"Completed approved payload: {raw}")


if __name__ == "__main__":
    main()
