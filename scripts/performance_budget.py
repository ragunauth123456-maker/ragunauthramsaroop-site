from pathlib import Path
from html.parser import HTMLParser
import sys
ROOT=Path(__file__).resolve().parents[1]
class P(HTMLParser):
    def __init__(self):super().__init__();self.scripts=[];self.img=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="script" and a.get("src"):self.scripts.append(a)
        if tag=="img":self.img.append(a)
warn=[];fail=[]
for f in ROOT.rglob("*.html"):
    size=f.stat().st_size
    if size>350_000:fail.append((f,f"HTML {size/1024:.0f} KB > 350 KB"))
    elif size>180_000:warn.append((f,f"HTML {size/1024:.0f} KB"))
    p=P()
    try:p.feed(f.read_text(encoding="utf-8",errors="replace"))
    except:continue
    if len(p.scripts)>25:warn.append((f,f"{len(p.scripts)} external scripts"))
for f in ROOT.rglob("*"):
    if f.is_file() and f.suffix.lower() in {".png",".jpg",".jpeg",".webp",".svg"}:
        if f.stat().st_size>600_000:fail.append((f,f"image {f.stat().st_size/1024:.0f} KB > 600 KB"))
        elif f.stat().st_size>250_000:warn.append((f,f"image {f.stat().st_size/1024:.0f} KB"))
print("FAILURES",len(fail));print("WARNINGS",len(warn))
for f,m in fail[:80]:print("FAIL",f.relative_to(ROOT),m)
for f,m in warn[:80]:print("WARN",f.relative_to(ROOT),m)
sys.exit(1 if fail else 0)
