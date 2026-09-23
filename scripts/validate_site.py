"""Static privacy, routing, social-card and sitemap checks for RR Free Tools."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json, re, struct, sys, xml.etree.ElementTree as ET, zipfile
ROOT=Path(__file__).resolve().parents[1];TOOLS=ROOT/"tools"
issues=[]
class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.links=[];self.meta={};self.canonical=None;self.jsonscripts=[];self._json=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ("a","img","script","link"):
            for key in ("href","src"):
                if a.get(key):self.links.append(a[key])
        if tag=="link" and a.get("rel")=="canonical":self.canonical=a.get("href")
        if tag=="meta":
            k=a.get("property") or a.get("name")
            if k:self.meta[k]=a.get("content")
        if tag=="script" and a.get("type")=="application/ld+json":self._json=True
    def handle_data(self,data):
        if self._json:self.jsonscripts.append(data)
    def handle_endtag(self,tag):
        if tag=="script":self._json=False
def local_link(src,path):
    parsed=urlparse(src)
    if parsed.scheme or src.startswith(("#","mailto:","tel:","data:","javascript:","//")):return None
    rel=unquote(parsed.path)
    if not rel:return None
    target=(ROOT/rel.lstrip("/")) if rel.startswith("/") else (path.parent/rel)
    if target.is_dir():target/= "index.html"
    if not target.suffix and not target.exists():target/= "index.html"
    return target
html_pages=list(ROOT.rglob("*.html"))
for page in html_pages:
    text=page.read_text(encoding="utf-8",errors="replace")
    if "/tools/assets/analytics-loader.js" not in text:
        issues.append((str(page),"missing analytics consent loader"))
robots_text=(ROOT/"robots.txt").read_text(encoding="utf-8",errors="replace")
if "Sitemap: https://ragunauthramsaroop.com/tools/sitemap.xml" not in robots_text:
    issues.append((str(ROOT/"robots.txt"),"tools sitemap not advertised"))
try:
    tool_map=ET.parse(TOOLS/"sitemap.xml").getroot()
    tool_locs=[e.text for e in tool_map.iter() if e.tag.endswith("}loc") or e.tag=="loc"]
    if len(tool_locs)<20:
        issues.append((str(TOOLS/"sitemap.xml"),"unexpectedly small tools sitemap"))
except Exception as ex:
    issues.append((str(TOOLS/"sitemap.xml"),"invalid tools sitemap: "+str(ex)))
sitemap=ET.parse(ROOT/"sitemap.xml").getroot()
locs={e.text for e in sitemap.iter() if e.tag.endswith("}loc") or e.tag=="loc"}
for path in html_pages:
    s=path.read_text(encoding="utf-8",errors="replace")
    p=AuditParser()
    try:p.feed(s)
    except Exception as ex:issues.append((str(path),"HTML parse: "+str(ex)))
    for src in p.links:
        dest=local_link(src,path)
        if dest is not None and not dest.exists():issues.append((str(path),"missing asset: "+src))
    for raw in p.jsonscripts:
        try:json.loads(raw)
        except Exception as ex:issues.append((str(path),"invalid JSON-LD: "+str(ex)))
    if TOOLS in path.parents and path.name=="index.html" and path.parent.name!="assets":
        if not p.canonical or not p.canonical.startswith("https://ragunauthramsaroop.com/tools/"):issues.append((str(path),"canonical mismatch"))
        if p.canonical not in locs:issues.append((str(path),"missing from root sitemap"))
        if path.parent.name not in ("privacy",) and path.parent!=TOOLS:
            if "RR_GUIDE" not in s:issues.append((str(path),"missing editorial guide"))
            og=p.meta.get("og:image","")
            if not og.endswith("/"+path.parent.name+".png"):issues.append((str(path),"og:image not unique"))
            if "tools/assets/tools.js" not in s and "tools/assets/growth-tools.js" not in s:issues.append((str(path),"missing tool runtime"))
    if "data-appdeploy-overlay" in s or "data-appdeploy-network-hook" in s:issues.append((str(path),"legacy AppDeploy overlay"))
imgs=list((TOOLS/"assets"/"og").glob("*.png"))
for p in imgs:
    b=p.read_bytes()[:24]
    if len(b)!=24 or b[:8]!=b"\x89PNG\r\n\x1a\n" or struct.unpack(">II",b[16:24])!=(1200,630):
        issues.append((str(p),"incorrect social image"))
z=TOOLS/"downloads"/"rr-free-templates.zip"
if not zipfile.is_zipfile(z):issues.append((str(z),"ZIP missing or invalid"))
elif len(zipfile.ZipFile(z).namelist())<18:issues.append((str(z),"template pack unexpectedly incomplete"))
for js in [TOOLS/"assets"/"tools.js",TOOLS/"assets"/"growth-tools.js"]:
    if "api-v2.appdeploy" in js.read_text(encoding="utf-8"):issues.append((str(js),"paid API dependency"))
print("HTML_PAGES",len(html_pages))
print("TOOL_INDEX_PAGES",len([p for p in html_pages if TOOLS in p.parents and p.name=="index.html"]))
print("SHARE_IMAGES",len(imgs))
print("SITEMAP_URLS",len(locs))
print("TEMPLATE_PACK_FILES",len(zipfile.ZipFile(z).namelist()) if zipfile.is_zipfile(z) else 0)
print("ISSUES",len(issues))
for p,msg in issues[:80]:print("FAIL",p,msg)
sys.exit(1 if issues else 0)
