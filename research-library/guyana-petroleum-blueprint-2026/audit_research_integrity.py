#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
src = (BASE / "SOURCE_REGISTER.md").read_text(encoding="utf-8")
claims = (BASE / "CLAIM_SOURCE_MATRIX.md").read_text(encoding="utf-8")
ledger = (BASE / "LEGAL_EVIDENCE_LEDGER.md").read_text(encoding="utf-8")
corrections = (BASE / "CORRECTIONS_REGISTER.md").read_text(encoding="utf-8")
core = "\n".join(
    (BASE / f"FLAGSHIP_PART_{x}_MANUSCRIPT.md").read_text(encoding="utf-8")
    for x in ["I","II","III","IV","V","VI","VII","VIII","IX","X"]
)
core += "\n" + (BASE / "FLAGSHIP_HARDENING_ADDENDUM.md").read_text(encoding="utf-8")

rows = []
for line in src.splitlines():
    m = re.match(r"^\|\s*(S\d{2,3})\s*\|", line)
    if m:
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        rows.append(cells)

ids = [row[0] for row in rows]
nums = [int(x[1:]) for x in ids]
assert len(ids) >= 106, f"source register below scrutiny gate: {len(ids)}"
assert len(ids) == len(set(ids)), "duplicate source IDs"
assert nums == list(range(min(nums), max(nums) + 1)), "source IDs are not sequential"

urls = [row[4] for row in rows]
url_syntax = []
for sid, url in zip(ids, urls):
    p = urlparse(url)
    ok = p.scheme in ("http", "https") and bool(p.netloc) and " " not in url
    url_syntax.append((sid, url, ok))
assert all(x[2] for x in url_syntax), "malformed source URL"

def expand_refs(text):
    out = set()
    for bracket in re.findall(r"\[([^\]]*S\d+[^\]]*)\]", text):
        for a, b in re.findall(r"S(\d{2,3})\s*-\s*S?(\d{2,3})", bracket):
            for n in range(int(a), int(b) + 1):
                out.add(f"S{n:02d}")
        for n in re.findall(r"S(\d{2,3})", bracket):
            out.add(f"S{int(n):02d}")
    return out

core_refs = expand_refs(core)
registered = set(ids)
unknown_core = sorted(core_refs - registered)
assert not unknown_core, f"unknown source IDs in core: {unknown_core}"

claim_rows = []
claim_source_refs = set()
open_claims = []
for line in claims.splitlines():
    if re.match(r"^\|\s*C\d{3}\s*\|", line):
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        claim_rows.append(cells)
        source_cell = cells[2]
        for a, b in re.findall(r"S(\d{2,3})\s*-\s*S?(\d{2,3})", source_cell):
            for n in range(int(a), int(b) + 1):
                claim_source_refs.add(f"S{n:02d}")
        for n in re.findall(r"S(\d{2,3})", source_cell):
            claim_source_refs.add(f"S{int(n):02d}")
        if any(tag in cells[3].upper() for tag in ("OPEN", "PARTIAL", "LIMITED")):
            open_claims.append(cells[0])

assert len(claim_rows) >= 50, f"high-risk claim matrix below scrutiny gate: {len(claim_rows)}"
unknown_claim_sources = sorted(claim_source_refs - registered)
assert not unknown_claim_sources, f"unknown sources in claim matrix: {unknown_claim_sources}"

ledger_ids = sorted(set(re.findall(r"\bL\d{3}\b", ledger)))
assert len(ledger_ids) >= 14, f"legal evidence ledger below scrutiny gate: {len(ledger_ids)}"

correction_ids = sorted(set(re.findall(r"\bR\d{3}\b", corrections)))
assert len(correction_ids) >= 16, f"corrections register below scrutiny gate: {len(correction_ids)}"

dup_urls = sorted({u for u in urls if urls.count(u) > 1})
audit = {
    "source_records": len(ids),
    "first_source_id": ids[0],
    "last_source_id": ids[-1],
    "source_ids_unique": True,
    "source_ids_sequential": True,
    "source_url_syntax_valid": True,
    "duplicate_source_urls": dup_urls,
    "core_registered_source_refs": len(core_refs),
    "core_unknown_source_refs": unknown_core,
    "high_risk_claims": len(claim_rows),
    "high_risk_claim_source_refs": len(claim_source_refs),
    "high_risk_claim_source_refs_valid": True,
    "open_or_limited_high_risk_claims": open_claims,
    "legal_evidence_ledger_entries": len(ledger_ids),
    "corrections_register_entries": len(correction_ids),
    "external_peer_review": "pending",
}

integrity_path = BASE / "RESEARCH_INTEGRITY_AUDIT.json"
integrity_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

manifest_path = BASE / "PUBLICATION_MANIFEST.json"
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.setdefault("file_sha256", {})[integrity_path.name] = hashlib.sha256(integrity_path.read_bytes()).hexdigest()
    manifest["integrity_audit_status"] = "passed"
    manifest["source_records"] = len(ids)
    manifest["high_risk_claims"] = len(claim_rows)
    manifest["legal_evidence_ledger_entries"] = len(ledger_ids)
    manifest["corrections_register_entries"] = len(correction_ids)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

print(json.dumps(audit, indent=2))
