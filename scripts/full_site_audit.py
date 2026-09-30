#!/usr/bin/env python3
"""Whole-site integrity and executive-content audit for ragunauthramsaroop.com."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import argparse, json, re, sys, time

ROOT=Path(__file__).resolve().parents[1]
DOMAIN="https://ragunauthramsaroop.com"
SKIP_DIRS={".git","node_modules","_next","pagefind",".pagefind-public","skills"}
PLACEHOLDERS=re.compile(r"\b(lorem ipsum|todo\b|tbd\b|coming soon|placeholder text)\b",re.I)
LEGACY=re.compile(r"ragunauth123456(?:-maker)?",re.I)
EXEC_TERMS=re.compile(r"\b(decision|strategy|strategic|governance|evidence|leadership|executive|risk|stakeholder|institution|responsib|value|outcome|method|regulat|operat|investment|research|professional)\w*",re.I)

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title=[]; self.h1=[]; self.text=[]; self.links=[]; self.assets=[]
        self.desc=""; self.canonical=""; self.viewport=False; self.lang=""
        self._title=False; self._h1=0; self._skip=0; self.refresh=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="html": self.lang=a.get("lang","")
        if tag=="title": self._title=True
        if tag=="h1": self._h1+=1
        if tag in {"script","style","svg","noscript","template"}: self._skip+=1
        if tag=="meta":
            n=(a.get("name") or "").lower()
            if n=="description": self.desc=a.get("content","").strip()
            if n=="viewport": self.viewport=True
            if (a.get("http-equiv") or "").lower()=="refresh": self.refresh=True
        if tag=="link":
            if (a.get("rel") or "").lower()=="canonical": self.canonical=a.get("href","").strip()
            href=a.get("href","")
            if href: self.assets.append(href) if (a.get("rel") or "").lower()=="stylesheet" else None
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag in {"img","script","source","video","audio","iframe"} and a.get("src"): self.assets.append(a["src"])
        if a.get("srcset"):
            self.assets += [x.strip().split()[0] for x in a["srcset"].split(",") if x.strip()]
    def handle_endtag(self,tag):
        if tag=="title": self._title=False
        if tag=="h1" and self._h1: self._h1-=1
        if tag in {"script","style","svg","noscript","template"} and self._skip: self._skip-=1
    def handle_data(self,data):
        s=re.sub(r"\s+"," ",data).strip()
        if not s: return
        if self._title: self.title.append(s)
        if self._h1: self.h1.append(s)
        if not self._skip: self.text.append(s)

def html_files():
    out=[]
    for p in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts): continue
        out.append(p)
    return sorted(out)

def route_for(p:Path):
    rel=p.relative_to(ROOT).as_posix()
    if rel=="index.html": return "/"
    if rel.endswith("/index.html"): return "/"+rel[:-10]
    return "/"+rel

def resolve_local(ref, source:Path):
    ref=ref.strip()
    if not ref or ref.startswith(("#","mailto:","tel:","data:","javascript:","blob:")): return None
    u=urlparse(ref)
    if u.scheme in {"http","https"}:
        if u.netloc not in {"ragunauthramsaroop.com","www.ragunauthramsaroop.com"}: return None
        path=unquote(u.path)
    elif u.scheme or u.netloc: return None
    else: path=unquote(u.path)
    if not path: return None
    if path.startswith("/"): base=ROOT/path.lstrip("/")
    else: base=(source.parent/path).resolve()
    try: base.relative_to(ROOT)
    except ValueError: return ("escape",str(base))
    candidates=[base]
    if path.endswith("/"): candidates=[base/"index.html"]
    elif not base.suffix: candidates=[base,base/"index.html",Path(str(base)+".html")]
    return candidates

def static_audit(report_path:Path):
    pages=html_files(); issues=[]; page_rows=[]; titles={}
    for p in pages:
        raw=p.read_text(encoding="utf-8",errors="replace")
        parser=P()
        try: parser.feed(raw)
        except Exception as e: issues.append(("ERROR",p.relative_to(ROOT).as_posix(),f"HTML parse error: {e}"))
        rel=p.relative_to(ROOT).as_posix(); route=route_for(p)
        title=" ".join(parser.title).strip(); h1=" ".join(parser.h1).strip()
        visible=" ".join(parser.text); words=re.findall(r"\b[\w’'-]+\b",visible)
        if parser.refresh:
            page_rows.append({"path":rel,"route":route,"redirect":True,"words":len(words)})
            continue
        if not title: issues.append(("ERROR",rel,"Missing <title>"))
        elif len(title)<12: issues.append(("WARN",rel,f"Very short title: {title}"))
        else: titles.setdefault(title.lower(),[]).append(rel)
        if not h1: issues.append(("ERROR",rel,"Missing H1"))
        if not parser.viewport: issues.append(("ERROR",rel,"Missing viewport meta"))
        if not parser.lang: issues.append(("WARN",rel,"Missing html lang"))
        if not parser.desc: issues.append(("WARN",rel,"Missing meta description"))
        elif len(parser.desc)<55: issues.append(("WARN",rel,f"Thin meta description ({len(parser.desc)} chars)"))
        if not parser.canonical: issues.append(("WARN",rel,"Missing canonical URL"))
        if PLACEHOLDERS.search(visible): issues.append(("ERROR",rel,"Placeholder/draft language visible"))
        if LEGACY.search(raw): issues.append(("ERROR",rel,"Legacy GitHub identity present"))
        min_words=55 if rel in {"contact.html","brief-me.html"} or rel.startswith(("contact/","embed/","install/","subscribe/","feedback/","api/")) else 90
        if len(words)<min_words: issues.append(("WARN",rel,f"Thin visible content ({len(words)} words)"))
        exec_hits=len(EXEC_TERMS.findall(visible))
        if len(words)>=min_words and exec_hits<2 and not rel.startswith(("es/","fr/","pt/")):
            issues.append(("WARN",rel,"Low executive/decision-information signal"))
        broken=[]
        for ref in parser.links+parser.assets:
            resolved=resolve_local(ref,p)
            if not resolved: continue
            if isinstance(resolved,tuple):
                broken.append(ref); continue
            if not any(x.exists() for x in resolved): broken.append(ref)
        for ref in sorted(set(broken))[:30]:
            issues.append(("ERROR",rel,f"Broken internal reference: {ref}"))
        page_rows.append({"path":rel,"route":route,"title":title,"h1":h1,"description":parser.desc,"canonical":parser.canonical,"words":len(words),"executiveSignals":exec_hits})
    for title,paths in titles.items():
        if len(paths)>1:
            for rel in paths: issues.append(("WARN",rel,f"Duplicate title across {len(paths)} pages"))
    summary={"pages":len(pages),"errors":sum(i[0]=="ERROR" for i in issues),"warnings":sum(i[0]=="WARN" for i in issues)}
    report={"summary":summary,"issues":[{"severity":a,"path":b,"message":c} for a,b,c in issues],"pages":page_rows}
    report_path.parent.mkdir(parents=True,exist_ok=True); report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("STATIC_AUDIT",json.dumps(summary))
    for i in report["issues"][:240]: print(i["severity"],i["path"],i["message"])
    return summary, page_rows

def live_one(route):
    url=DOMAIN+route
    last=""
    for attempt in range(3):
        try:
            req=Request(url,headers={"User-Agent":"RR-Site-Integrity/1.0","Accept":"text/html,*/*"})
            with urlopen(req,timeout=18) as r:
                status=getattr(r,"status",200); body=r.read(4096); final=r.geturl()
                if status==200 and body: return {"route":route,"status":status,"final":final,"ok":True}
                last=f"HTTP {status}, empty={not bool(body)}"
        except HTTPError as e: last=f"HTTP {e.code}"
        except (URLError,TimeoutError,OSError) as e: last=str(e)
        time.sleep(2*(attempt+1))
    return {"route":route,"ok":False,"error":last}

def live_audit(rows, report_path:Path):
    routes=sorted({r["route"] for r in rows if not r.get("redirect")})
    results=[]
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs=[ex.submit(live_one,r) for r in routes]
        for f in as_completed(futs): results.append(f.result())
    results.sort(key=lambda x:x["route"]); failed=[x for x in results if not x["ok"]]
    report={"summary":{"routes":len(routes),"failed":len(failed)},"failures":failed,"results":results}
    report_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("LIVE_AUDIT",json.dumps(report["summary"]))
    for x in failed: print("LIVE_FAIL",x)
    return len(failed)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--live",action="store_true"); ap.add_argument("--strict",action="store_true")
    args=ap.parse_args()
    summary,rows=static_audit(ROOT/"audit/site-audit.json")
    failed_live=live_audit(rows,ROOT/"audit/live-audit.json") if args.live else 0
    if args.strict and (summary["errors"] or failed_live): return 1
    return 0
if __name__=="__main__": raise SystemExit(main())
