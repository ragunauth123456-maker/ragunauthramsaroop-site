#!/usr/bin/env python3
"""Edition 2 development audit: fail closed for financial arithmetic; never equate word count with quality."""
from __future__ import annotations
import csv, hashlib, json, re
from collections import Counter,defaultdict
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

BASE=Path(__file__).resolve().parent
PARTS="I II III IV V VI VII VIII IX X".split()
word_re=re.compile(r"\b[A-Za-z0-9]+(?:[-'’][A-Za-z0-9]+)*\b")
texts={part:(BASE/f"FLAGSHIP_PART_{part}_MANUSCRIPT.md").read_text(encoding="utf-8") for part in PARTS}
words={part:len(word_re.findall(text)) for part,text in texts.items()}
core_words=sum(words.values())
source_text=(BASE/"SOURCE_REGISTER.md").read_text(encoding="utf-8")
source_rows={}
for line in source_text.splitlines():
    if re.match(r"^\|\s*S\d{2,3}\s*\|",line):
        parts=[s.strip() for s in line.strip().strip("|").split("|")]
        if len(parts)<5: raise AssertionError(f"Truncated source row: {line[:100]}")
        sid=parts[0]
        if sid in source_rows: raise AssertionError(f"Duplicate source ID {sid}")
        source_rows[sid]=parts
nums=sorted(int(s[1:]) for s in source_rows)
assert len(nums)>=136 and nums==list(range(1,max(nums)+1)), "Missing or non-sequential source IDs"
bad_urls=[]
for sid,parts in source_rows.items():
    p=urlparse(parts[4])
    if p.scheme not in ("https","http") or not p.netloc or " " in parts[4]:bad_urls.append(sid)
assert not bad_urls, f"Malformed source URLs: {bad_urls}"
def refs(t):
    results=set()
    for bracket in re.findall(r"\[([^\]]*S\d{2,3}[^\]]*)\]",t):
        for first,last in re.findall(r"S(\d{2,3})\s*-\s*S?(\d{2,3})",bracket):
            results.update(f"S{k:02d}" for k in range(int(first),int(last)+1))
        results.update(f"S{int(k):02d}" for k in re.findall(r"S(\d{2,3})",bracket))
    return results
core_refs={part:refs(t) for part,t in texts.items()}
unknown=sorted(set().union(*core_refs.values())-source_rows.keys())
assert not unknown, f"Unregistered manuscript source IDs: {unknown}"
# A duplicate diagnostic is not a license to delete passages without editorial review.
long_paras=[]
for part,t in texts.items():
    for paragraph in re.split(r"\n\s*\n",t):
        if len(word_re.findall(paragraph))>=75 and not paragraph.lstrip().startswith("#"):
            norm=" ".join(word_re.findall(paragraph.lower()))
            long_paras.append((part,norm))
counts=Counter(p for _,p in long_paras)
exact_repeat=sum(v-1 for v in counts.values() if v>1)
repeated_openings=defaultdict(list)
for part,p in long_paras:
    repeated_openings[" ".join(p.split()[:18])].append(part)
near_repeat_candidates={k:v for k,v in repeated_openings.items() if len(v)>1}
# Include all high-risk claims and any source register updates.
claims=(BASE/"CLAIM_SOURCE_MATRIX.md").read_text(encoding="utf-8")
claim_rows=[]
for line in claims.splitlines():
    if re.match(r"^\|\s*C\d{3}\s*\|",line):
        cells=[x.strip() for x in line.strip().strip("|").split("|")]
        claim_rows.append(cells)
assert len(claim_rows)>=50
bad_claim_refs=[]
for row in claim_rows:
    for k in re.findall(r"S(\d{2,3})",row[2]):
        if f"S{int(k):02d}" not in source_rows:bad_claim_refs.append((row[0],k))
assert not bad_claim_refs, f"High-risk claims cite unknown sources: {bad_claim_refs}"
# Every table must be syntactically machine-readable and every explicit source ID registered.
datasets=sorted(BASE.glob("*.csv"))
dataset_issues=[]
for path in datasets:
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f);header=reader.fieldnames or []
        if not header or len(set(header))!=len(header):dataset_issues.append((path.name,"duplicate or empty headers"))
        for i,row in enumerate(reader,2):
            if None in row or any(v is None for v in row.values()):
                dataset_issues.append((path.name,f"malformed csv row {i}"))
            for field,v in row.items():
                if field and ("source" in field.lower()) and v:
                    for k in re.findall(r"S(\d{2,3})",v):
                        if f"S{int(k):02d}" not in source_rows:
                            dataset_issues.append((path.name,f"unknown source ID S{k} row {i}"))
assert not dataset_issues, f"Dataset problems: {dataset_issues[:20]}"
# Use exact decimal arithmetic; 0.03 USD million tolerance allows published 2-decimal rounding.
with (BASE/"NRF_ANNUAL_LEDGER.csv").open(newline="",encoding="utf-8") as f:
    ledger={row["year"]:row for row in csv.DictReader(f)}
D=lambda x:Decimal(str(x))
residuals={}
for year in ("2022","2023","2024","2025"):
    row=ledger[year]
    opening,inflow,ret,withdraw,close=(D(row[k]) for k in [
       "opening_balance_usd_m","petroleum_and_other_inflows_usd_m",
       "investment_return_usd_m","withdrawals_usd_m","closing_balance_usd_m"])
    residual=close-(opening+inflow+ret-withdraw)
    residuals[year]=str(residual)
    assert abs(residual)<=D("0.03"),f"{year} does not reconcile: {residual} USDm"
for y in ("2020","2021"):
    assert "PROVISIONAL" in ledger[y]["status"],f"{y} wrongly marked verified"
h1=ledger["2026-H1"]
assert not h1["petroleum_and_other_inflows_usd_m"],"H1 2026 must not mislabel gross receipts as bank fund inflows"
assert "OPEN" in h1["status"],"H1 2026 must remain explicitly unreconciled"
o,ret,w,c,gov=(D(h1[k]) for k in ["opening_balance_usd_m",
"investment_return_usd_m","withdrawals_usd_m","closing_balance_usd_m",
"government_reported_receipts_usd_m"])
implied=c-o+w-ret; gap=gov-implied
assert abs(implied-D("1812.77"))<=D("0.03"),f"unexpected H1 implied inflows: {implied}"
assert abs(gap-D("184.23"))<=D("0.03"),f"unexpected H1 recognition gap: {gap}"
assert abs(D(h1["receipt_to_implied_inflow_gap_usd_m"])-gap)<=D("0.03")
required=["OFFSHORE_PROJECT_REGISTER.csv","MASTER_CHRONOLOGY.csv",
"LOCAL_CONTENT_VALUE_ADDED_FRAMEWORK.csv","COMPARATOR_MECHANISM_MATRIX.csv",
"PUBLIC_INVESTMENT_DELIVERY_REGISTER.csv","OFFSHORE_ENVIRONMENTAL_ASSURANCE_MATRIX.csv",
"PSA_CLAUSE_CROSSWALK.csv","NEW_PRODUCER_READINESS_CHECKLIST.csv",
"PETROLEUM_GOVERNANCE_RACI.csv","ADVERSE_SCENARIO_PLAYBOOK.csv"]
assert all((BASE/n).is_file() for n in required),"Missing operating blueprint dataset"
audit={
 "edition":"2.0-development","evidence_cutoff":"2026-09-27",
 "core_lexical_words":core_words,"target_minimum_core_words":120000,
 "core_word_target_met":core_words>=120000,"parts":words,
 "sources_registered":len(source_rows),"source_ids_sequential":True,
 "source_url_syntax_valid":True,"source_urls_live_checked":False,
 "core_unique_source_ids":len(set().union(*core_refs.values())),
 "core_sources_by_part":{k:len(v) for k,v in core_refs.items()},
 "high_risk_claims":len(claim_rows),"exact_repeated_long_paragraphs":exact_repeat,
 "near_duplicate_leading_phrase_candidates":len(near_repeat_candidates),
 "csv_files_validated":len(datasets),"nrf_rounded_residual_usd_m":residuals,
 "nrf_2026_h1_implied_inflows_usd_m":str(implied),
 "nrf_2026_h1_unreconciled_recognition_gap_usd_m":str(gap),
 "nrf_2026_h1_reconciled":False,
 "publication_complete":False,"external_peer_review":"pending",
 "pdf_release_gate_passed":False
}
(BASE/"EDITION2_PROGRESS_AUDIT.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
with (BASE/"EDITION2_PART_COVERAGE.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f);w.writerow(["part","lexical_words","registered_source_ids_used","word_target_met"])
    for p in PARTS:w.writerow([p,words[p],len(core_refs[p]),words[p]>=12000])
print(json.dumps(audit,indent=2))
