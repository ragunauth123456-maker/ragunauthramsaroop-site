"""Prepare one searchable author-abstract URL and same-directory PDF per work.
Google Scholar crawls independently; never label a work indexed without evidence.
"""
from pathlib import Path
from html import escape
import json,re,shutil,pymupdf,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BASE="https://ragunauthramsaroop.com"
regpath=ROOT/"research-library"/"publication-register.json"
reg=json.loads(regpath.read_text(encoding="utf-8"))
library=ROOT/"research-library"/"index.html"
libhtml=library.read_text(encoding="utf-8")
sitemap=ROOT/"sitemap.xml";sitemap_text=sitemap.read_text(encoding="utf-8")
feed=ROOT/"research-library"/"feed.xml";feed_text=feed.read_text(encoding="utf-8")
cfg={
"guyana-2040":(1,r"(?im)^Abstract\s*$",r"(?im)^White paper element\s*$"),
"guyana-power-demand-2030":(1,r"(?im)^Executive summary\s*$",r"(?im)^1\.\s+The 2026 starting point\s*$"),
"critical-minerals-energy-security":(1,r"(?im)^Abstract\s*$",r"(?im)^Keywords:\s*"),
"guyana-economy-2030":(8,r"(?im)^1\s+Executive Abstract\s*$",r"(?im)^2\s+Research Questions\s*$"),
"new-geography-globalization":(1,r"(?im)^Abstract\s*$",r"(?im)^Keywords:\s*"),
"water-security-economic-security":(1,r"(?im)^Abstract\s*$",r"(?im)^Keywords:\s*"),
"guyana-lcds-2030":(2,r"(?im)^Executive overview\s*$",r"(?im)^1\.\s+Purpose, audience and method\s*$")}
def original_abstract(d,p):
    start,head,end=cfg[p["slug"]]
    body="\n".join(d[i].get_text() for i in range(start,min(start+7,len(d))))
    headings=list(re.finditer(head,body))
    if not headings:raise ValueError("Author abstract heading not found: "+p["slug"])
    candidates=[]
    for h in headings:
        tail=body[h.end():]
        finish=re.search(end,tail)
        if finish and 300<=len(tail[:finish.start()])<=12000:
            candidates.append(tail[:finish.start()])
    if not candidates:raise ValueError("Author abstract ending not found: "+p["slug"])
    body=candidates[0]
    body=body.replace(p["title"]+"\nRagunauth Ramsaroop\n","")
    body=re.sub(r"(?m)^Ragunauth Ramsaroop\s*$","",body)
    body=re.sub(r"(?<=\w)-\n(?=[a-z])","",body)
    body=re.sub(r"(?m)^(?:GUYANA 2040\s*/\s*POLICY WHITE PAPER|COMPREHENSIVE EVIDENCE REVIEW).*?$","",body)
    body=re.sub(r"(?m)^Page\s+\w+\s+of\s+\d+\s*$","",body)
    body=re.sub(r"\s+"," ",body).strip()
    if not 300<=len(body)<=12000:raise ValueError("Review unusual abstract: "+p["slug"]+" "+str(len(body)))
    parts=re.split(r"(?<=[.!?])\s+(?=[A-Z])",body)
    lines=[];current=""
    for s in parts:
        if len(current)+len(s)>870 and current:lines.append(current.strip());current=""
        current+=" "+s
    if current:lines.append(current.strip())
    return lines
results=[]
for p in reg["papers"]:
    slug=p["slug"]
    old=BASE+"/research-papers/"+slug+".pdf"
    old_rel="/research-papers/"+slug+".pdf"
    new_rel="/research-library/"+slug+"/full-text.pdf"
    new=BASE+new_rel
    original=ROOT/"research-papers"/(slug+".pdf")
    source=pymupdf.open(original)
    assert "ragunauth" in (source[0].get_text()+source[1].get_text()).lower()
    abstract=original_abstract(source,p)
    dest=ROOT/"research-library"/slug/"full-text.pdf"
    if slug=="guyana-power-demand-2030":
        source.save(dest,garbage=4,deflate=True,use_objstms=1)
    else:shutil.copy2(original,dest)
    pages=len(source);source.close()
    verify=pymupdf.open(dest)
    assert len(verify)==pages and len(verify[0].get_text())>150
    verify.close()
    raw=(ROOT/"research-library"/slug/"index.html").read_text(encoding="utf-8")
    assert raw.count('name="citation_title"')==1 and raw.count('name="citation_author"')==1
    raw=raw.replace(old,new).replace('href="'+old_rel+'"','href="'+new_rel+'"')
    raw=re.sub(r'<meta name="citation_pdf_url"[^>]*>',"",raw)
    raw=re.sub(r'<meta name="citation_publication_date"[^>]*>','<meta name="citation_publication_date" content="2026/09/25">',raw)
    raw=raw.replace("</head>",'<meta name="citation_pdf_url" content="'+new+'"><meta name="citation_online_date" content="2026/09/25"><link rel="alternate" type="application/pdf" href="'+new+'"></head>',1)
    block='<section class="scholar-abstract" id="author-abstract" aria-label="Full original abstract" style="max-width:78ch;margin:28px 0"><h2>Full author abstract or executive overview</h2>'+''.join('<p>'+escape(a)+'</p>' for a in abstract)+'</section>'
    ix=raw.index('<p class="lead">');ix=raw.index("</p>",ix)+4
    raw=raw[:ix]+block+raw[ix:]
    # Preserve existing PDF URLs for old external links, but offer a unique indexed copy.
    ix=raw.index('<div class="actions">');ix=raw.index("</div>",ix)
    raw=raw[:ix]+'<a class="btn alt" href="'+old_rel+'">Original published PDF</a>'+raw[ix:]
    (ROOT/"research-library"/slug/"index.html").write_text(raw,encoding="utf-8")
    libhtml=libhtml.replace(old,new).replace('href="'+old_rel+'"','href="'+new_rel+'"')
    feed_text=feed_text.replace(old,new)
    if p.get("old"):
        oldpage=ROOT/"white-papers"/p["old"]/"index.html"
        existing=oldpage.read_text(encoding="utf-8")
        oldpage.write_text(existing.replace('href="'+old_rel+'"','href="'+new_rel+'"'),encoding="utf-8")
    sitemap_text=re.sub(r"<url><loc>"+re.escape(old)+r"</loc><lastmod>[^<]+</lastmod></url>\s*","",sitemap_text)
    if "<loc>"+new+"</loc>" not in sitemap_text:
        sitemap_text=sitemap_text.replace("</urlset>","<url><loc>"+new+"</loc><lastmod>2026-09-25</lastmod></url>\n</urlset>")
    p.update(google_scholar_status="crawl_ready_not_indexed",scholar_html_url=BASE+"/research-library/"+slug+"/",scholar_pdf_url=new,scholar_pdf_bytes=dest.stat().st_size,scholar_full_abstract_chars=sum(len(a) for a in abstract))
    results.append({"slug":slug,"html":p["scholar_html_url"],"pdf":new,"pdf_bytes":dest.stat().st_size,"under_5_mib":dest.stat().st_size<=5*1024*1024,"under_5_mb_decimal":dest.stat().st_size<=5000000,"original_abstract_chars":p["scholar_full_abstract_chars"],"author":"Ragunauth Ramsaroop","citation_metadata":True})
library.write_text(libhtml,encoding="utf-8")
feed.write_text(feed_text,encoding="utf-8")
sitemap.write_text(sitemap_text,encoding="utf-8")
regpath.write_text(json.dumps(reg,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
(ROOT/"research-library"/"scholar-readiness.json").write_text(json.dumps({"verified_at":"2026-09-25","status":"eligible_for_automatic_crawling_not_indexing_confirmed","google_scholar_submission_route":"Google Scholar crawler, not direct upload","guidelines":"https://scholar.google.com/intl/en/scholar/inclusion.html","papers":results},indent=2)+"\n",encoding="utf-8")
for test in (ROOT/"research-library"/"guyana-power-demand-2030").glob("scholar-*.pdf"):
    if test.name!="full-text.pdf":test.unlink()
ET.parse(sitemap);ET.parse(feed)
for p in results:
    txt=(ROOT/"research-library"/p["slug"]/"index.html").read_text(encoding="utf-8")
    assert txt.count('name="citation_pdf_url"')==1 and p["pdf"] in txt and "scholar-abstract" in txt
    assert p["under_5_mib"],"Document above five mebibytes: "+p["slug"]
print("SCHOLAR_ARCHIVE_QA",json.dumps({"count":len(results),"all_same_directory":True,"all_author_abstracts":True,"all_under_5_mib":True,"strict_5_mb_over": [p["slug"] for p in results if not p["under_5_mb_decimal"]],"google_scholar_indexed":False},indent=2),flush=True)
