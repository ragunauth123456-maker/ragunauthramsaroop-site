"""Submit changed or published URLs to IndexNow without a paid service."""
from pathlib import Path
import argparse, json, re, subprocess, sys, urllib.request, urllib.error, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
STATE=Path(r"C:\AgentSwarm\qa-logs\indexnow-last-commit.txt")
HOST="ragunauthramsaroop.com"
ENDPOINT="https://api.indexnow.org/indexnow"

def key_file():
    for p in ROOT.glob("*.txt"):
        if re.fullmatch(r"[A-Za-z0-9-]{32,64}\.txt",p.name):
            try:
                if p.read_text(encoding="utf-8").strip()==p.stem:return p
            except: pass
    raise RuntimeError("IndexNow key file not found")

def sitemap_urls():
    urls=[]
    for sm in [ROOT/"sitemap.xml",ROOT/"tools"/"sitemap.xml",ROOT/"topics"/"sitemap.xml"]:
        if not sm.exists():continue
        tree=ET.parse(sm)
        for e in tree.getroot().iter():
            if e.tag.endswith("}loc") or e.tag=="loc":
                if e.text and e.text.startswith("https://ragunauthramsaroop.com/"):urls.append(e.text.strip())
    return sorted(set(urls))

def git(*args):
    return subprocess.check_output(["git","-C",str(ROOT),*args],text=True,stderr=subprocess.DEVNULL).strip()

def map_changed(old,new):
    names=git("diff","--name-only",f"{old}..{new}").splitlines()
    shared=False;urls=set()
    for name in names:
        name=name.replace("\\","/")
        if name in {"sitemap.xml","robots.txt","llms.txt"} or name.startswith(("assets/","tools/assets/","_next/static/")):
            shared=True
        if name=="index.html":urls.add("https://ragunauthramsaroop.com/")
        elif name.endswith("/index.html"):
            urls.add("https://ragunauthramsaroop.com/"+name[:-10])
        elif name.endswith(".html"):
            urls.add("https://ragunauthramsaroop.com/"+name)
        elif name.startswith("tools/downloads/"):
            urls.add("https://ragunauthramsaroop.com/"+name)
    return sitemap_urls() if shared else sorted(urls)

def submit(urls,keyp):
    if not urls:return 0,"No URLs changed"
    payload={"host":HOST,"key":keyp.stem,"keyLocation":f"https://{HOST}/{keyp.name}","urlList":urls[:10000]}
    req=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode("utf-8"),headers={"Content-Type":"application/json; charset=utf-8","User-Agent":"RR-IndexNow/1.0"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=25) as r:return r.status,r.read().decode("utf-8","ignore")
    except urllib.error.HTTPError as e:return e.code,e.read().decode("utf-8","ignore")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--changed-only",action="store_true");args=ap.parse_args()
    keyp=key_file();head=git("rev-parse","HEAD")
    old=STATE.read_text(encoding="utf-8").strip() if STATE.exists() else ""
    if args.changed_only and old==head:
        print("INDEXNOW no new commit");return 0
    urls=map_changed(old,head) if args.changed_only and old else sitemap_urls()
    code,body=submit(urls,keyp)
    print("INDEXNOW",code,"URLS",len(urls),body[:300])
    if code in (200,202):
        STATE.parent.mkdir(parents=True,exist_ok=True);STATE.write_text(head,encoding="utf-8");return 0
    return 1
if __name__=="__main__":sys.exit(main())
