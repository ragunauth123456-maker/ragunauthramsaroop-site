"""Build the local public search index directly from current static HTML."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets/search-index.json"
SKIP_PARTS={"_next","pagefind",".pagefind-public","node_modules","skills",".git"}
PROFILE=json.loads((ROOT/"data/public-profile.json").read_text(encoding="utf-8"))

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title=[]
        self.text=[]
        self.description=""
        self.in_title=False
        self.skip=0
        self.refresh=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="title": self.in_title=True
        if tag in {"script","style","svg","noscript"}: self.skip+=1
        if tag=="meta":
            name=(attrs.get("name") or "").lower()
            equiv=(attrs.get("http-equiv") or "").lower()
            if name=="description": self.description=attrs.get("content","")
            if equiv=="refresh": self.refresh=True
    def handle_endtag(self,tag):
        if tag=="title": self.in_title=False
        if tag in {"script","style","svg","noscript"} and self.skip: self.skip-=1
    def handle_data(self,data):
        s=re.sub(r"\s+"," ",data).strip()
        if not s: return
        if self.in_title: self.title.append(s)
        if not self.skip: self.text.append(s)

def public_url(path):
    rel=path.relative_to(ROOT).as_posix()
    if rel=="index.html": return "/"
    if rel.endswith("/index.html"): return "/"+rel[:-10]
    return "/"+rel

def doc_type(url):
    if url.startswith(("/research-library/","/white-papers/","/insights/","/book/")): return "Research"
    if url.startswith("/tools/"): return "Tool"
    if url.startswith(("/guides/","/learning-paths/","/academy/")): return "Guide"
    if url.startswith(("/executive-profile/","/2126/","/authority/","/media/","/recognition-media/","/recruiter-","/board-ceo-mode/","/decision-brief/","/leadership/","/corporate-affairs/","/esg-social-impact/","/compliance-governance/","/international-mandates/","/sectors/","/resume")): return "Professional"
    return "Hub"

docs=[]
for path in sorted(ROOT.rglob("*.html")):
    rel=path.relative_to(ROOT)
    if any(part in SKIP_PARTS for part in rel.parts): continue
    try: raw=path.read_text(encoding="utf-8",errors="replace")
    except OSError: continue
    parser=Extractor()
    try: parser.feed(raw)
    except Exception: continue
    if parser.refresh: continue
    title=" ".join(parser.title).strip()
    if not title: continue
    title=re.sub(r"\s*\|\s*Ragunauth Ramsaroop\s*$","",title).strip()
    visible=" ".join(parser.text)
    visible=re.sub(r"\s+"," ",visible).strip()
    url=public_url(path)
    docs.append({
        "title":title,
        "description":parser.description.strip(),
        "url":url,
        "type":doc_type(url),
        "text":visible[:24000]
    })

payload={"version":2,"updated":PROFILE["reviewed"],"documents":docs}
OUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print("SEARCH_INDEX",len(docs),"documents",OUT.stat().st_size,"bytes")
