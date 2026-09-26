"""Offline, local-only quality gate for evidence-led CEO introductions. Never sends mail."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROUTES = {"verified-professional-ceo", "published-executive-office",
          "published-corporate-office", "published-country-office"}
PERSONAL = {"gmail.com", "yahoo.com", "icloud.com", "hotmail.com",
            "outlook.com", "proton.me"}
EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def cited_url(value):
    u = urlparse(value or "")
    return u.scheme == "https" and bool(u.hostname) and u.hostname not in {"example.com","example.org"}

def assess(dossier, root, sent):
    errors = []
    d = dossier
    company = str(d.get("company") or "").strip()
    ceo = str(d.get("ceo") or "").strip()
    rank = d.get("fortune_2026_rank")
    if not company or not ceo:
        errors.append("Research the current company and CEO.")
    if not isinstance(rank, int) or not (1 <= rank <= 200):
        errors.append("Verify Fortune Global 500 (2026) top-200 membership.")
    if not cited_url(d.get("ceo_source_url")):
        errors.append("Missing official CEO identity source.")
    sources = d.get("strategy_sources") or []
    if not sources or not all(isinstance(s, dict) and s.get("published_at")
                              and cited_url(s.get("url")) for s in sources):
        errors.append("Missing dated primary company strategy sources.")
    if len(str(d.get("value_thesis") or "").split()) < 12:
        errors.append("Missing specific first-paragraph value thesis.")
    reasons = d.get("supporting_reasons") or []
    if not (2 <= len(reasons) <= 4) or not all(
          len(str(r).split()) >= 6 for r in reasons):
        errors.append("Minto principle requires 2-4 supporting reasons.")
    if not d.get("approved_cv_evidence"):
        errors.append("Each CV achievement needs approved factual evidence.")
    route = d.get("contact_route") or {}
    address = str(route.get("address") or "").strip().lower()
    if not EMAIL.fullmatch(address) or address.rsplit("@", 1)[-1] in PERSONAL:
        errors.append("Professional address missing or not suitable.")
    if route.get("type") not in ROUTES or not cited_url(route.get("source_url")):
        errors.append("The office/contact route must have public source evidence.")
    if route.get("type") == "verified-professional-ceo" and not route.get("direct_verified"):
        errors.append("Never claim direct CEO access without verification.")
    if d.get("outreach_restricted") or d.get("opted_out"):
        errors.append("Company restriction or opt-out prevents outreach.")
    if route.get("type") != "verified-professional-ceo":
        cc = d.get("cc_contact") or {}
        deputy = str(cc.get("address") or "").strip().lower()
        if (not EMAIL.fullmatch(deputy) or deputy == address
            or deputy.rsplit("@", 1)[-1] in PERSONAL
            or not cc.get("full_name") or not cc.get("current_role")
            or not cc.get("professional_email_verified")
            or not cited_url(cc.get("email_source_url"))
            or not cited_url(cc.get("role_source_url"))):
            errors.append("No direct CEO contact: CC a named, publicly verified senior executive.")
        if str(d.get("cc") or "").strip().lower() != deputy:
            errors.append("CC must match the verified senior executive.")
    if d.get("to") and str(d["to"]).strip().lower() != address:
        errors.append("To must match the documented professional route.")
    if (company.casefold(), address) in sent or d.get("status") == "Sent":
        errors.append("Duplicate outreach blocked.")
    if not d.get("subject") or not d.get("message"):
        errors.append("Missing subject or company-specific email.")
    attachments = d.get("attachments") or {}
    for name in ("cv_pdf", "value_brief_pdf"):
        filename = attachments.get(name)
        path = (root / str(filename or "")).resolve()
        if not filename or path.suffix.lower() != ".pdf" or not path.is_file():
            errors.append("Missing " + name + " PDF.")
            continue
        if path.stat().st_size < 4096 or path.read_bytes()[:4] != b"%PDF":
            errors.append("Invalid or empty " + name + " PDF.")
            continue
        try:
            import fitz
            count = len(fitz.open(path))
            if (name == "cv_pdf" and count not in (2, 3)) or (
                name == "value_brief_pdf" and count != 1):
                errors.append("Incorrect page count: " + name)
        except ImportError:
            pass
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossiers", type=Path, help="Private local JSON list, never commit.")
    parser.add_argument("--files-root", type=Path, default=Path("."))
    parser.add_argument("--sent-ledger", type=Path)
    args = parser.parse_args()
    dossiers = json.loads(args.dossiers.read_text(encoding="utf-8"))
    if not isinstance(dossiers, list):
        raise SystemExit("Dossiers must be a JSON array.")
    sent = set()
    if args.sent_ledger and args.sent_ledger.is_file():
        for row in json.loads(args.sent_ledger.read_text(encoding="utf-8")):
            sent.add((row["company"].casefold(), row["address"].casefold()))
    report = []
    for d in dossiers:
        errors = assess(d, args.files_root, sent)
        report.append({"company": d.get("company"),
                       "status": "READY_FOR_HUMAN_REVIEW" if not errors else "BLOCKED",
                       "issues": errors})
    print(json.dumps(report, indent=2))
    if any(r["issues"] for r in report):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
