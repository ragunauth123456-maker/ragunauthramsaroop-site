from pathlib import Path
from io import BytesIO
from PIL import Image
from html import escape
import subprocess,pymupdf,json,re,shutil,xml.etree.ElementTree as ET
ROOT=Path("C:/Users/Fano Faizul/Documents/RagunauthWebsiteUpdate/site-publication-work")
SITE="https://ragunauthramsaroop.com"
def cmd(args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,encoding="utf-8",errors="replace",timeout=100)
 print("GIT",args[:3],p.returncode,(p.stdout or "")[-200:],(p.stderr or "")[-200:],flush=True)
 if p.returncode:raise RuntimeError("Command failed: "+" ".join(args))
 return p
def extract_full_abstract(pdf,p):
 cfg={
 "guyana-2040":(1,r"(?im)^Abstract\s*$",r"(?im)^White paper element\s*$"),
 "guyana-power-demand-2030":(1,r"(?im)^Executive summary\s*$",r"(?im)^1\.\s+The 2026 starting point\s*$"),
 "critical-minerals-energy-security":(1,r"(?im)^Abstract\s*$",r"(?im)^Keywords:\s*"),
 "guyana-economy-2030":(8,r"(?im)^1\s+Executive Abstract\s*$",r"(?im)^2\s+Research Questions\s*$"),
 "new-geography-globalization":(1,r"(?im)^Abstract\s*$",r"(?im)^Keywords:\s*"),
 "water-security-economic-security":(1,r"(?im)^Abstract\s*$",r"(?im)^Keywords:\s*"),
 "guyana-lcds-2030":(2,r"(?im)^Executive overview\s*$",r"(?im)^1\.\s+Purpose, audience and method\s*$")}
 start,first,last=cfg[p["slug"]]
 first_page=pdf[start].get_text()
 hit=list(re.finditer(first,first_page))
 if not hit:raise ValueError("PDF has no matching abstract heading: "+p["slug"])
 raw=first_page[hit[-1].end():]+"\n"+"\n".join(pdf[i].get_text() for i in range(start+1,min(start+7,len(pdf))))
 end=re.search(last,raw)
 if not end:raise ValueError("End of author-written abstract not located: "+p["slug"])
 raw=raw[:end.start()]
 raw=raw.replace(p["title"]+"\nRagunauth Ramsaroop\n","")
 raw=re.sub(r"(?m)^Ragunauth Ramsaroop\s*$","",raw)
 raw=re.sub(r"(?<=\w)-\n(?=[a-z])","",raw)
 raw=re.sub(r"(?m)^(?:GUYANA 2040\s*/\s*POLICY WHITE PAPER|COMPREHENSIVE EVIDENCE REVIEW).*?$","",raw)
 raw=re.sub(r"(?m)^Page\s+\w+\s+of\s+\d+\s*$","",raw)
 raw=re.sub(r"\s+"," ",raw).strip()
 if len(raw)<250 or len(raw)>29000:raise ValueError("Review abstract length: "+p["slug"]+" "+str(len(raw)))
 sentences=re.split(r"(?<=[.!?])\s+(?=[A-Z])",raw)
 paras=[];buf=""
 for s in sentences:
  if len(buf)+len(s)>900 and buf:paras.append(buf.strip());buf=""
  buf+=" "+s
 if buf.strip():paras.append(buf.strip())
 return paras
def optimize_power_pdf(source,dest):
 doc=pymupdf.open(source)
 if dest.exists():dest.unlink()
 doc.save(dest,garbage=4,deflate=True,use_objstms=1)
 doc.close()
 if dest.stat().st_size >= 5*1024*1024:raise RuntimeError("Optimized PDF exceeds the 5 MiB threshold")
 before=pymupdf.open(source);after=pymupdf.open(dest)
 assert len(before)==len(after) and before[0].get_text()==after[0].get_text() and before[-1].get_text()==after[-1].get_text()
 after.close();before.close()
def main():
 branch=subprocess.run(["git","branch","--show-current"],cwd=ROOT,text=True,capture_output=True).stdout.strip()
 if branch!="publication/google-scholar-crawl-readiness":
  cmd(["git","fetch","origin","main"])
  cmd(["git","checkout","main"])
  cmd(["git","pull","--ff-only","origin","main"])
  cmd(["git","checkout","-b","publication/google-scholar-crawl-readiness"])
 regpath=ROOT/"research-library"/"publication-register.json"
 reg=json.loads(regpath.read_text(encoding="utf-8"))
 root_index=ROOT/"research-library"/"index.html"
 libhtml=root_index.read_text(encoding="utf-8")
 sitemap_file=ROOT/"sitemap.xml";sitemap=sitemap_file.read_text(encoding="utf-8")
 results=[]
 for p in reg["papers"]:
  slug=p["slug"];source=ROOT/"research-papers"/(slug+".pdf")
  doc=pymupdf.open(source)
  abstract=extract_full_abstract(doc,p)
  doc.close()
  target=ROOT/"research-library"/slug/"full-text.pdf"
  if slug=="guyana-power-demand-2030":optimize_power_pdf(source,target)
  else:shutil.copy2(source,target)
  html_path=ROOT/"research-library"/slug/"index.html";html=html_path.read_text(encoding="utf-8")
  old_url=SITE+"/research-papers/"+slug+".pdf"
  new_url=SITE+"/research-library/"+slug+"/full-text.pdf"
  old_rel="/research-papers/"+slug+".pdf";new_rel="/research-library/"+slug+"/full-text.pdf"
  html=html.replace(old_url,new_url).replace('href="'+old_rel+'"','href="'+new_rel+'"')
  html=re.sub(r'<meta name="citation_pdf_url"[^>]*>',"",html)
  html=html.replace("</head>",'<meta name="citation_pdf_url" content="'+new_url+'"><link rel="alternate" type="application/pdf" href="'+new_url+'"></head>',1)
  sec='<section id="author-abstract" style="margin:32px 0;max-width:78ch" aria-label="Full author-written abstract"><h2 style="font-size:26px">Abstract or executive overview</h2>'+''.join('<p>'+escape(x)+'</p>' for x in abstract)+'</section>'
  ix=html.index('<p class="lead">');ix=html.index("</p>",ix)+4
  html=html[:ix]+sec+html[ix:]
  original_button='<a class="btn alt" href="'+old_rel+'">Original publication PDF</a>'
  ix=html.index('<div class="actions">');ix=html.index("</div>",ix)
  html=html[:ix]+original_button+html[ix:]
  html_path.write_text(html,encoding="utf-8")
  libhtml=libhtml.replace(old_url,new_url).replace('href="'+old_rel+'"','href="'+new_rel+'"')
  if "<loc>"+new_url+"</loc>" not in sitemap:
   sitemap=sitemap.replace("</urlset>","<url><loc>"+new_url+"</loc><lastmod>2026-09-25</lastmod></url>\n</urlset>")
  p.update(scholar_pdf_url=new_url,scholar_pdf_bytes=target.stat().st_size,scholar_status="crawl_ready_not_index_verified",abstract_source="Full author-written abstract or executive overview from the original PDF")
  results.append({"slug":slug,"pdf_bytes":target.stat().st_size,"abstract_chars":sum(len(x) for x in abstract),"metadata":"title, author, publication date and same-directory PDF","crawl_ready":True})
 root_index.write_text(libhtml,encoding="utf-8")
 sitemap_file.write_text(sitemap,encoding="utf-8")
 regpath.write_text(json.dumps(reg,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 report={"checked_at":"2026-09-25","google_scholar_submission":"Automatic crawler only, no direct submission available","scholar_indexing":"not verified","robots":"public crawler allowed","sitemap":SITE+"/sitemap.xml","papers":results}
 reportpath=ROOT/"research-library"/"scholar-readiness.json"
 reportpath.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 for test in (ROOT/"research-library"/"guyana-power-demand-2030").glob("scholar-size-test*.pdf"):test.unlink()
 ET.parse(sitemap_file)
 for p in reg["papers"]:
  item=ROOT/"research-library"/p["slug"]
  txt=(item/"index.html").read_text(encoding="utf-8")
  assert txt.count('name="citation_pdf_url"')==1 and "citation_title" in txt and 'name="citation_author"' in txt
  assert 'id="author-abstract"' in txt and str(p["scholar_pdf_bytes"]) and p["scholar_pdf_bytes"]<5*1024*1024
  assert p["scholar_pdf_url"] in txt and '<loc>'+p["scholar_pdf_url"]+'</loc>' in sitemap
 check=subprocess.run(["python","scripts/validate_site.py"],cwd=ROOT,text=True,capture_output=True,timeout=110)
 print("STATIC_QA",check.returncode,check.stdout[-700:],check.stderr[-200:],flush=True)
 if check.returncode:raise RuntimeError("Static site audit failed")
 print("SCHOLAR_READINESS_PASS",json.dumps(report,ensure_ascii=True),flush=True)
if __name__=="__main__":main()
