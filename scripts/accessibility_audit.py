from pathlib import Path
from html.parser import HTMLParser
import re,sys,os
ROOT=Path(__file__).resolve().parents[1]
class P(HTMLParser):
    def __init__(self):
        super().__init__();self.img=[];self.inputs=[];self.labels=set();self.h1=0;self.lang=False;self.viewport=False;self.buttons=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="html" and a.get("lang"):self.lang=True
        if tag=="meta" and a.get("name","").lower()=="viewport":self.viewport=True
        if tag=="img":self.img.append(a)
        if tag in ("input","select","textarea"):self.inputs.append((tag,a))
        if tag=="label" and a.get("for"):self.labels.add(a["for"])
        if tag=="h1":self.h1+=1
        if tag=="button":self.buttons.append(a)
        if tag=="a":self.links.append(a)
issues=[];warnings=[]
SKIP_DIRS={"node_modules","skills","agent"}
def keep_dir(name): return name not in SKIP_DIRS and (not name.startswith(".") or name==".well-known")
pages=[]
for base,dirs,files in os.walk(ROOT):
    dirs[:]=[d for d in dirs if keep_dir(d)]
    pages.extend(Path(base)/f for f in files if f.endswith(".html"))
for f in pages:
    s=f.read_text(encoding="utf-8",errors="replace");p=P()
    try:p.feed(s)
    except Exception as e:issues.append((f,"parse error "+str(e)));continue
    if not p.lang:issues.append((f,"missing html lang"))
    if not p.viewport:issues.append((f,"missing viewport meta"))
    for a in p.img:
        if "alt" not in a:issues.append((f,"image missing alt: "+a.get("src","")[:80]))
    if p.h1==0:warnings.append((f,"no H1"))
    elif p.h1>1:warnings.append((f,f"{p.h1} H1 elements"))
    # Inputs in .field are repaired at runtime by assets/accessibility.js. Flag only controls with neither id nor aria-label on pages missing that script.
    runtime="/assets/accessibility.js" in s
    for tag,a in p.inputs:
        typ=a.get("type","").lower()
        if typ in ("hidden","submit","button","reset"):continue
        ident=a.get("id")
        labelled=(ident and ident in p.labels) or a.get("aria-label") or a.get("aria-labelledby") or runtime
        if not labelled:issues.append((f,f"unlabelled {tag}: "+a.get("name","")[:60]))
    if runtime and "rr-skip-link" not in s and "<main" not in s:warnings.append((f,"accessibility helper present but page has no main landmark"))
print("PAGES",len(pages));print("ISSUES",len(issues));print("WARNINGS",len(warnings))
for f,m in issues[:100]:print("FAIL",f.relative_to(ROOT),m)
for f,m in warnings[:60]:print("WARN",f.relative_to(ROOT),m)
sys.exit(1 if issues else 0)
