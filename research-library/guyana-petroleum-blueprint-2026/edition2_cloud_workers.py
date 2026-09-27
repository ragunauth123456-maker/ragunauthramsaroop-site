#!/usr/bin/env python3
"""Cloud-only, read-only evidence workers for Edition 2.0.
Jobs produce development artifacts, never unreviewed research claims or a final PDF.
"""
from __future__ import annotations
import argparse, csv, hashlib, html, ipaddress, json, re, socket, sys, urllib.error, urllib.parse, urllib.request, zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent.parent / "edition2-worker-artifacts"
PARTS="I II III IV V VI VII VIII IX X".split()
WORDS=re.compile(r"\b[A-Za-z0-9]+(?:[-'’][A-Za-z0-9]+)*\b")
SOURCES=re.compile(r"^\|\s*(S\d{2,3})\s*\|")
TARGETS={"I":12000,"II":16000,"III":11000,"IV":14000,"V":15000,"VI":11000,"VII":13000,"VIII":9000,"IX":11000,"X":12000}

def write(name,text):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(text,encoding="utf-8")
def dump(name,obj):
    write(name,json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
def source_rows():
    out={}
    for line in (ROOT/"SOURCE_REGISTER.md").read_text(encoding="utf-8").splitlines():
        m=SOURCES.match(line)
        if not m: continue
        parts=[p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts)<5: raise ValueError("truncated source row "+m[1])
        if m[1] in out: raise ValueError("duplicate "+m[1])
        out[m[1]]={"label":parts[1],"url":parts[4],"caveat":parts[3]}
    if sorted(int(k[1:]) for k in out)!=list(range(1,len(out)+1)):
        raise ValueError("source IDs are not sequential")
    return out

def parse_refs(text):
    matches=set()
    for b in re.findall(r"\[([^\]]*S\d{2,3}[^\]]*)\]",text):
        for a,z in re.findall(r"S(\d{2,3})\s*-\s*S?(\d{2,3})",b):
            if int(z)<int(a) or int(z)-int(a)>150:
                raise ValueError("bad source range "+a+"-"+z)
            matches.update("S"+str(i).zfill(2) for i in range(int(a),int(z)+1))
        matches.update("S"+str(int(i)).zfill(2) for i in re.findall(r"S(\d{2,3})",b))
    return matches

def editorial():
    sources=source_rows()
    out={"stage":"development","pdf_final":False,"parts":{},"source_register_count":len(sources),
         "target_minimum_core_words":120000,"claim_level_fact_check":"not performed",
         "external_peer_review":"pending"}
    allref=set();total=0;long=[];seen_heads={}
    for part in PARTS:
        t=(ROOT/f"FLAGSHIP_PART_{part}_MANUSCRIPT.md").read_text(encoding="utf-8")
        w=len(WORDS.findall(t));refs=parse_refs(t)
        unknown=refs-set(sources)
        if unknown:raise ValueError(f"Part {part}: unregistered citations {unknown}")
        ptxt=[]
        for paragraph in re.split(r"\n\s*\n",t):
            if paragraph.lstrip().startswith(("#","|")): continue
            tokens=[x.lower() for x in WORDS.findall(paragraph)]
            if len(tokens)>=75:
                norm=" ".join(tokens)
                long.append((part,norm))
                if len(tokens)>=100:
                    head=" ".join(tokens[:18])
                    seen_heads.setdefault(head,[]).append(part)
                    ptxt.append(len(tokens))
        total+=w;allref.update(refs)
        out["parts"][part]={"lexical_words":w,"target_words":TARGETS[part],
                            "remaining_to_target":max(0,TARGETS[part]-w),
                            "registered_source_ids_cited":len(refs),
                            "long_paragraph_count":len(ptxt)}
    cnt=Counter(s for p,s in long)
    out.update({"core_lexical_words":total,"core_word_minimum_met":total>=120000,
        "registered_source_ids_used":len(allref),
        "exact_duplicate_long_paragraphs":sum(v-1 for v in cnt.values() if v>1),
        "similar_opening_review_candidates":sum(len(v)-1 for v in seen_heads.values() if len(v)>1),
        "nrf_2026_h1_reconciliation":"OPEN"})
    dump("manuscript_gap_audit.json",out)
    md=["# Edition 2 cloud editorial worker","",
        "**Development audit only:** lexical counts do not prove factual correctness or editorial originality.","",
        f"Core lexical words: **{total:,}** / 120,000 minimum.",
        f"Source register: {len(sources)} records; {len(allref)} cited by the core.",
        f"Exact repeated long paragraphs: {out['exact_duplicate_long_paragraphs']}.",
        f"Similar paragraph openings for editorial review: {out['similar_opening_review_candidates']}.","",
        "| Part | Words | Minimum target | Additional words to target | Cited sources |",
        "|---|---:|---:|---:|---:|"]
    for p,d in out["parts"].items():
        md.append(f"| {p} | {d['lexical_words']:,} | {d['target_words']:,} | {d['remaining_to_target']:,} | {d['registered_source_ids_cited']} |")
    md += ["","## Release blockers","",
           "- Word minimum unmet unless explicitly shown as met above.",
           "- URL reachability is not source-to-claim verification.",
           "- NRF H1 2026 cash/accrual difference remains open.",
           "- Specialist external peer review pending.",
           "- This job does not assemble a final PDF."]
    write("manuscript_gap_audit.md","\n".join(md)+"\n")
    print(json.dumps({"worker":"editorial","words":total,"source_count":len(sources),
                      "exact_duplicates":out["exact_duplicate_long_paragraphs"]}))
    if out["exact_duplicate_long_paragraphs"]: 
        print("WARNING: exact repeats need human editorial review")
    return 0

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None

def public_url(url):
    p=urllib.parse.urlsplit(url)
    host=(p.hostname or "").lower().rstrip(".")
    if p.scheme not in ("https","http") or not host or p.username or p.password: return False
    if p.port not in (None,80,443):return False
    if host in ("localhost","metadata.google.internal") or host.endswith((".local",".internal")):return False
    try:
        addr=ipaddress.ip_address(host)
        return addr.is_global
    except ValueError:
        return True

def check_one(item):
    sid,rec=item;url=rec["url"]
    if not public_url(url):return {"id":sid,"status":"invalid_or_unsafe_url","http":None,"url":url}
    req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":"Edition2-Source-Availability-Audit/1.0 (research metadata only)"})
    opener=urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req,timeout=11) as resp:
            status=resp.status
    except urllib.error.HTTPError as e:
        status=e.code
        if status in (405,501):
            try:
                req=urllib.request.Request(url,method="GET",headers={"Range":"bytes=0-0","User-Agent":"Edition2-Source-Availability-Audit/1.0"})
                with opener.open(req,timeout=11) as response:
                    status=response.status
                    response.read(1)
            except urllib.error.HTTPError as e2:status=e2.code
            except Exception:return {"id":sid,"status":"inconclusive_connection","http":None,"url":url}
    except Exception:
        return {"id":sid,"status":"inconclusive_connection","http":None,"url":url}
    classification=("reachable" if 200<=status<300 else
       "redirect_unfollowed" if 300<=status<400 else
       "blocked_or_rate_limited" if status in (401,403,429,451) else
       "not_found_review" if status in (404,410) else "server_or_other")
    return {"id":sid,"status":classification,"http":status,"url":url}

def live_sources():
    rows=source_rows();results=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs={pool.submit(check_one,item):item[0] for item in rows.items()}
        for future in as_completed(futs):
            try: results.append(future.result())
            except Exception as exc:results.append({"id":futs[future],"status":"inconclusive_worker_error","error":str(exc)[:180]})
    results.sort(key=lambda r:int(r["id"][1:]))
    counts=dict(Counter(x["status"] for x in results))
    audit={"stage":"source_availability_only","checked_at_utc":datetime.now(timezone.utc).isoformat(),
           "source_count":len(results),"status_counts":counts,
           "important":"HTTP reachability neither authenticates a document nor validates any claim/citation",
           "links":results}
    dump("source_availability_audit.json",audit)
    with (OUT/"source_availability_audit.csv").open("w",encoding="utf-8",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=["id","status","http","url"],extrasaction="ignore");wr.writeheader();wr.writerows(results)
    print(json.dumps({"worker":"source_availability","counts":counts}))
    return 0

def read_ledger():
    with (ROOT/"NRF_ANNUAL_LEDGER.csv").open(newline="",encoding="utf-8") as f:
        return {r["year"]:r for r in csv.DictReader(f)}

def svg_doc(title,description,content):
    return ('<svg xmlns="http://www.w3.org/2000/svg" role="img" viewBox="0 0 1080 650">'
        '<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'
        '<rect width="1080" height="650" fill="#f7faf8"/>'
        '<text x="64" y="70" font-family="sans-serif" font-weight="700" font-size="34" fill="#123047">'+html.escape(title)+'</text>'
        +content+'</svg>')

def exhibits():
    sources=source_rows();data={}
    for p in PARTS:
        t=(ROOT/f"FLAGSHIP_PART_{p}_MANUSCRIPT.md").read_text(encoding="utf-8")
        data[p]=len(WORDS.findall(t))
    content='<line x1="100" y1="530" x2="1000" y2="530" stroke="#496077"/>'
    colors=["#25765a","#466f99"]*5
    for i,p in enumerate(PARTS):
        x=118+i*87;h=340*data[p]/max(TARGETS.values());th=340*TARGETS[p]/max(TARGETS.values())
        content+=f'<rect x="{x}" y="{530-th:.1f}" width="30" height="{th:.1f}" fill="#dbe9e0"/>'
        content+=f'<rect x="{x}" y="{530-h:.1f}" width="30" height="{h:.1f}" fill="#25765a"/>'
        content+=f'<text x="{x+15}" y="555" text-anchor="middle" font-family="sans-serif" font-size="17">{p}</text>'
        content+=f'<text x="{x+15}" y="{523-h:.1f}" text-anchor="middle" font-family="sans-serif" font-size="15">{data[p]/1000:.1f}k</text>'
    content+='<text x="100" y="610" font-family="sans-serif" font-size="17" fill="#3a5567">Green: core words | Pale: minimum per-Part target. Editorial quality and external review remain open.</text>'
    write("chapter_coverage.svg",svg_doc("Edition 2.0 | Core manuscript", "Words per part and planned minimums, not a research-quality measure.",content))
    ledger=read_ledger();years=["2022","2023","2024","2025"]
    charts=[("Fund balance","closing_balance_usd_m","#145a43"),("Petroleum inflows","petroleum_and_other_inflows_usd_m","#3273a1"),("Budget withdrawals","withdrawals_usd_m","#ad7538")]
    content='<line x1="110" y1="510" x2="960" y2="510" stroke="#496077"/>'
    for j,(title,key,color) in enumerate(charts):
        for i,yr in enumerate(years):
            value=float(ledger[yr][key]);x=128+i*208+j*43;y=510-300*value/3600
            content+=f'<rect x="{x}" y="{y:.1f}" width="34" height="{510-y:.1f}" fill="{color}"/>'
        content+=f'<rect x="{125+j*270}" y="560" width="18" height="18" fill="{color}"/>'
        content+=f'<text x="{149+j*270}" y="576" font-family="sans-serif" font-size="15">{html.escape(title)}</text>'
    for i,yr in enumerate(years):
        content+=f'<text x="{167+i*208}" y="535" text-anchor="middle" font-family="sans-serif" font-size="19">{yr}</text>'
    content+='<text x="94" y="125" font-family="sans-serif" font-size="15" fill="#42586b">USD millions; rounded. 2026 H1 excluded: cash/accrual bridge unresolved.</text>'
    content+='<text x="94" y="620" font-family="sans-serif" font-size="15" fill="#42586b">Sources: BoG audited NRF statements S44, S88 and Q4 report S109. Preliminary design exhibit.</text>'
    write("nrf_2022_2025.svg",svg_doc("Natural Resource Fund | 2022–25", "Rounded NRF opening/flows from repository ledger. 2026 excluded pending exact reconciliation.",content))
    dump("exhibit_manifest.json",{"status":"draft original reproducible exhibits","sources":["S44","S88","S109"],
      "excluded":"2026-H1 pending reconciliation",
      "figures":["chapter_coverage.svg","nrf_2022_2025.svg"],
      "note":"The SVG files are aids for the editable manuscript; they are not final graphical proof of every sourced number."})
    print(json.dumps({"worker":"figures","figures":["chapter_coverage.svg","nrf_2022_2025.svg"]}))
    return 0

def package():
    source_rows();OUT.mkdir(parents=True,exist_ok=True)
    fixed=[ROOT/f"FLAGSHIP_PART_{p}_MANUSCRIPT.md" for p in PARTS]
    fixed += [ROOT/n for n in ["SOURCE_REGISTER.md","CLAIM_SOURCE_MATRIX.md","LEGAL_EVIDENCE_LEDGER.md","CORRECTIONS_REGISTER.md","EDITION_2_CORE_EXPANSION_STANDARD.md"]]
    fixed += sorted(ROOT.glob("*.csv"))
    fixed += [OUT/"manuscript_gap_audit.json",OUT/"manuscript_gap_audit.md"]
    missing=[p.name for p in fixed if not p.is_file()]
    if missing:raise FileNotFoundError("Missing package components: "+", ".join(missing))
    manifest={"edition":"2.0-DEVELOPMENT","publication_complete":False,"peer_review":"pending",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in fixed}}
    dump("working_package_sha256.json",manifest)
    target=OUT/"edition2-editable-development-package.zip"
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in fixed:z.write(p,p.name)
        z.write(OUT/"working_package_sha256.json","working_package_sha256.json")
    print(json.dumps({"worker":"package","files":len(fixed),"zip_bytes":target.stat().st_size,"publication_complete":False}))
    return 0

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("task",choices=["editorial","sources","exhibits","package"])
    args=parser.parse_args()
    sys.exit({"editorial":editorial,"sources":live_sources,"exhibits":exhibits,"package":package}[args.task]())
