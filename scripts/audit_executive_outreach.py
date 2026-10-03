#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path("outreach/icloud-staged")
GENERIC_EXACT = {
    "press", "media", "mediarelations", "media.relations", "media-relations",
    "press.office", "pressoffice", "press.services", "pr", "corporatepr",
    "communications", "communication", "comms", "globalmedia",
    "investorrelations", "investor.relations", "investors", "ir",
    "talent", "talentacquisition", "recruiting", "recruitment", "careers", "career", "jobs",
    "hr", "humanresources", "people", "info", "information", "contact", "contactus",
    "support", "help", "sales", "office", "corporate", "admin", "enquiries", "inquiries",
    "webmaster", "marketing", "events", "customerservice", "service"
}
GENERIC_TOKENS = (
    "press", "media", "communications", "comms", "investor", "talent", "recruit",
    "career", "jobs", "humanresources", "contact", "support", "sales", "customer",
    "enquir", "inquir", "corporatepr"
)
RECRUITER_HINTS = (
    "robert-walters", "michael-page", "jac-recruitment", "monroe-consulting", "boyden",
    "rgf", "persolkelly", "nes-fircroft", "peak-recruitment", "iesf", "korn-ferry",
    "globe-24-7", "acre", "barton", "cf-search", "dober"
)
TEAM_SALUTATIONS = (
    " team", "department", "office", "public relations", "media relations", "communications team",
    "recruitment team", "talent acquisition", "hiring team", "careers team", "sir/madam", "to whom"
)

def classify(address: str, body: str, path: str):
    if "@" not in address:
        return "invalid", ["invalid-email"]
    local = address.split("@", 1)[0].lower().strip()
    reasons = []
    if local in GENERIC_EXACT:
        reasons.append("generic-local-part")
    if any(tok in local for tok in GENERIC_TOKENS):
        reasons.append("functional-mailbox-pattern")
    first_line = ""
    for line in (body or "").splitlines():
        if line.strip():
            first_line = line.strip().lower()
            break
    if first_line.startswith("dear ") and any(x in first_line for x in TEAM_SALUTATIONS):
        reasons.append("team-salutation")
    if any(h in path.lower() for h in RECRUITER_HINTS):
        return "recruiter-review", reasons
    if reasons:
        return "generic-only", sorted(set(reasons))
    return "named-or-specific", []


def main():
    rows = []
    for path in sorted(ROOT.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({"path": str(path), "status": "parse-error", "error": str(exc)})
            continue
        company = (data.get("cv_overlay") or {}).get("company") or path.stem
        for item in data.get("messages") or []:
            address = str(item.get("to") or "").strip()
            body = str(item.get("body") or "")
            status, reasons = classify(address, body, str(path))
            rows.append({
                "path": str(path),
                "company": company,
                "to": address,
                "status": status,
                "reasons": reasons,
                "subject": item.get("subject") or ""
            })

    generic = [r for r in rows if r.get("status") == "generic-only"]
    recruiter = [r for r in rows if r.get("status") == "recruiter-review"]
    named = [r for r in rows if r.get("status") == "named-or-specific"]

    print(f"AUDIT_TOTAL={len(rows)}")
    print(f"AUDIT_GENERIC_ONLY={len(generic)}")
    print(f"AUDIT_RECRUITER_REVIEW={len(recruiter)}")
    print(f"AUDIT_NAMED_OR_SPECIFIC={len(named)}")
    print("GENERIC_ONLY_BEGIN")
    for r in generic:
        print(json.dumps(r, ensure_ascii=True, separators=(",", ":")))
    print("GENERIC_ONLY_END")
    print("RECRUITER_REVIEW_BEGIN")
    for r in recruiter:
        print(json.dumps(r, ensure_ascii=True, separators=(",", ":")))
    print("RECRUITER_REVIEW_END")

if __name__ == "__main__":
    main()
