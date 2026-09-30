#!/usr/bin/env python3
"""Forensic page-by-page visual alignment audit for the static public site."""
from __future__ import annotations
import argparse, asyncio, json, re, socketserver, threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from urllib.parse import quote
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
SKIP={".git","node_modules","_next","pagefind",".pagefind-public","skills"}
VIEWPORTS={
    "desktop":{"width":1440,"height":1000},
    "mobile":{"width":390,"height":844},
}
EXEC_PREFIXES=(
    "/", "/executive-profile/","/leadership/","/evidence/","/research-library/","/media/",
    "/resume.html","/engage/","/recruiter-mode/","/board-ceo-mode/","/recognition-media/",
    "/case-studies/","/insights/","/white-papers/","/authority/","/decision-brief/",
    "/professional-engagement/","/executive-engagement/","/executive-search/","/executive-perspectives/"
)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass

def routes():
    out=[]
    for p in ROOT.rglob("*.html"):
        rel=p.relative_to(ROOT)
        if any(x in SKIP for x in rel.parts): continue
        s=rel.as_posix()
        if s=="index.html": route="/"
        elif s.endswith("/index.html"): route="/"+s[:-10]
        else: route="/"+s
        out.append(route)
    return sorted(set(out))

JS=r"""
() => {
 const vw=innerWidth,vh=innerHeight;
 const visible=e=>{
   const cs=getComputedStyle(e),r=e.getBoundingClientRect();
   return cs.display!=="none"&&cs.visibility!=="hidden"&&+cs.opacity!==0&&r.width>1&&r.height>1;
 };
 const insideScroller=e=>{
   let p=e.parentElement;
   while(p&&p!==document.body){
     const c=getComputedStyle(p);
     if(["auto","scroll","hidden","clip"].includes(c.overflowX)) return true;
     p=p.parentElement;
   }
   return false;
 };
 const selector=e=>{
   if(e.id) return "#"+CSS.escape(e.id);
   let s=e.tagName.toLowerCase();
   if(e.classList&&e.classList.length) s+="."+[...e.classList].slice(0,2).map(CSS.escape).join(".");
   return s;
 };
 const all=[...document.querySelectorAll("body *")].filter(visible);
 const offscreen=[];
 const clippedText=[];
 const badImages=[];
 const tinyControls=[];
 for(const e of all){
   const r=e.getBoundingClientRect(),cs=getComputedStyle(e);
   if(!insideScroller(e)&&cs.position!=="fixed"&&cs.position!=="absolute"){
     if(r.right>vw+3||r.left<-3) offscreen.push({el:selector(e),left:Math.round(r.left),right:Math.round(r.right),w:Math.round(r.width)});
   }
   const text=(e.childElementCount===0?e.textContent:"").trim();
   if(text.length>24 && e.clientWidth>0 && e.scrollWidth>e.clientWidth+3 && ["hidden","clip"].includes(cs.overflowX)){
     clippedText.push({el:selector(e),text:text.slice(0,90),client:e.clientWidth,scroll:e.scrollWidth});
   }
   if(e.tagName==="IMG" && (!e.complete || e.naturalWidth===0)) badImages.push({el:selector(e),src:e.getAttribute("src")});
   if((e.matches("button,summary,[role=button],.btn,.contact-chip")) && vw<=420 && (r.height<34||r.width<34)){
     tinyControls.push({el:selector(e),w:Math.round(r.width),h:Math.round(r.height)});
   }
 }
 const fixed=all.filter(e=>["fixed"].includes(getComputedStyle(e).position)).map(e=>({e,r:e.getBoundingClientRect()}));
 const overlaps=[];
 for(let i=0;i<fixed.length;i++)for(let j=i+1;j<fixed.length;j++){
   const a=fixed[i],b=fixed[j];
   const x=Math.max(0,Math.min(a.r.right,b.r.right)-Math.max(a.r.left,b.r.left));
   const y=Math.max(0,Math.min(a.r.bottom,b.r.bottom)-Math.max(a.r.top,b.r.top));
   if(x*y>500) overlaps.push({a:selector(a.e),b:selector(b.e),area:Math.round(x*y)});
 }
 const h1=document.querySelector("h1");
 const main=document.querySelector("main");
 const nav=document.querySelector("header nav,.navlinks,.nav-links,.site-header nav,.topbar nav");
 const footer=document.querySelector("footer");
 const bodyStyle=getComputedStyle(document.body);
 return {
   title:document.title,
   bodyOverflow:document.documentElement.scrollWidth>vw+3,
   scrollWidth:document.documentElement.scrollWidth,
   viewport:vw,
   offscreen:offscreen.slice(0,20),
   clippedText:clippedText.slice(0,12),
   badImages:badImages.slice(0,12),
   tinyControls:tinyControls.slice(0,12),
   fixedOverlaps:overlaps.slice(0,12),
   h1:h1?{text:h1.textContent.trim().slice(0,120),left:Math.round(h1.getBoundingClientRect().left),top:Math.round(h1.getBoundingClientRect().top),size:parseFloat(getComputedStyle(h1).fontSize)}:null,
   main:main?{left:Math.round(main.getBoundingClientRect().left),right:Math.round(main.getBoundingClientRect().right)}:null,
   nav:nav?{height:Math.round(nav.getBoundingClientRect().height),scroll:nav.scrollWidth,client:nav.clientWidth}:null,
   footer:footer?{height:Math.round(footer.getBoundingClientRect().height)}:null,
   bodyFont:parseFloat(bodyStyle.fontSize),
   accessibilityButton:!!document.querySelector(".rr-a11y-toggle"),
   smartGuide:!!document.querySelector(".rr-utility-dock,.rr-smart-guide,[data-smart-guide]")
 };
}
"""

async def audit_one(browser,base,route,sem):
    out={"route":route,"viewports":{},"errors":[],"warnings":[]}
    async with sem:
      context=await browser.new_context(service_workers="block")
      page=await context.new_page()
      for name,vp in VIEWPORTS.items():
        await page.set_viewport_size(vp)
        try:
          resp=await page.goto(base+route,wait_until="domcontentloaded",timeout=20000)
          await page.wait_for_timeout(120)
          if not resp or resp.status>=400:
            out["errors"].append(f"{name}: HTTP {resp.status if resp else 'no response'}")
            continue
          data=await page.evaluate(JS)
          out["viewports"][name]=data
          if data["bodyOverflow"]: out["errors"].append(f"{name}: horizontal page overflow {data['scrollWidth']}px > {data['viewport']}px")
          if data["badImages"]: out["errors"].append(f"{name}: broken image(s): {data['badImages'][:3]}")
          if data["fixedOverlaps"]: out["errors"].append(f"{name}: overlapping fixed UI: {data['fixedOverlaps'][:3]}")
          if data["clippedText"]: out["warnings"].append(f"{name}: clipped text candidates: {data['clippedText'][:3]}")
          if data["offscreen"]: out["warnings"].append(f"{name}: offscreen candidates: {data['offscreen'][:3]}")
          if data["tinyControls"]: out["warnings"].append(f"{name}: small controls: {data['tinyControls'][:3]}")
          if name=="desktop" and data.get("nav") and data["nav"]["scroll"]>data["nav"]["client"]+2:
            out["errors"].append("desktop: primary navigation overflows")
          if data["bodyFont"]<15: out["warnings"].append(f"{name}: body font {data['bodyFont']}px")
          if route in EXEC_PREFIXES or any(route.startswith(x) for x in EXEC_PREFIXES if x!="/"):
            h=data.get("h1")
            if h and name=="desktop" and h["size"]<36: out["warnings"].append(f"desktop: executive H1 is only {h['size']}px")
        except Exception as e:
          out["errors"].append(f"{name}: {type(e).__name__}: {e}")
      await context.close()
    return out

async def main_async(strict=False):
    handler=lambda *a,**kw: Quiet(*a,directory=str(ROOT),**kw)
    server=socketserver.ThreadingTCPServer(("127.0.0.1",0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f"http://127.0.0.1:{server.server_address[1]}"
    async with async_playwright() as p:
      browser=await p.chromium.launch(headless=True,args=["--no-sandbox"])
      sem=asyncio.Semaphore(6)
      results=await asyncio.gather(*(audit_one(browser,base,r,sem) for r in routes()))
      await browser.close()
    server.shutdown()
    errors=[x for x in results if x["errors"]]
    warnings=[x for x in results if x["warnings"]]
    report={"summary":{"routes":len(results),"error_pages":len(errors),"warning_pages":len(warnings),"viewports":list(VIEWPORTS)},"results":results}
    (ROOT/"audit").mkdir(exist_ok=True)
    (ROOT/"audit/visual-alignment-audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("VISUAL_ALIGNMENT_AUDIT",json.dumps(report["summary"]))
    for x in errors:
      print("ERROR",x["route"]," | ".join(x["errors"]))
    for x in warnings[:120]:
      print("WARN",x["route"]," | ".join(x["warnings"]))
    return 1 if strict and errors else 0

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--strict",action="store_true");args=ap.parse_args()
    raise SystemExit(asyncio.run(main_async(args.strict)))
