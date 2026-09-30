from pathlib import Path
from html.parser import HTMLParser
import sys,os
ROOT=Path(__file__).resolve().parents[1]
class P(HTMLParser):
    def __init__(self):super().__init__();self.scripts=[];self.img=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="script" and a.get("src"):self.scripts.append(a)
        if tag=="img":self.img.append(a)
warn=[];fail=[]
SKIP_DIRS={"node_modules","skills","agent"}
def keep_dir(name): return name not in SKIP_DIRS and (not name.startswith(".") or name==".well-known")
def walk_files():
    for base,dirs,files in os.walk(ROOT):
        dirs[:]=[d for d in dirs if keep_dir(d)]
        for name in files:
            yield Path(base)/name
for f in (x for x in walk_files() if x.suffix.lower()==".html"):
    size=f.stat().st_size
    if size>350_000:fail.append((f,f"HTML {size/1024:.0f} KB > 350 KB"))
    elif size>180_000:warn.append((f,f"HTML {size/1024:.0f} KB"))
    p=P()
    try:p.feed(f.read_text(encoding="utf-8",errors="replace"))
    except:continue
    if len(p.scripts)>25:warn.append((f,f"{len(p.scripts)} external scripts"))
for f in walk_files():
    if f.suffix.lower() in {".png",".jpg",".jpeg",".webp",".svg"}:
        rel=f.relative_to(ROOT).as_posix()
        size=f.stat().st_size
        if rel.startswith("assets/linkedin/"):
            if size>500_000:fail.append((f,f"social image {size/1024:.0f} KB > 500 KB"))
            elif size>400_000:warn.append((f,f"social image {size/1024:.0f} KB"))
        else:
            if size>600_000:fail.append((f,f"image {size/1024:.0f} KB > 600 KB"))
            elif size>250_000:warn.append((f,f"image {size/1024:.0f} KB"))
print("FAILURES",len(fail));print("WARNINGS",len(warn))
for f,m in fail[:80]:print("FAIL",f.relative_to(ROOT),m)
for f,m in warn[:80]:print("WARN",f.relative_to(ROOT),m)
sys.exit(1 if fail else 0)
