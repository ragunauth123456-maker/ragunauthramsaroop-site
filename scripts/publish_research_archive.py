#!/usr/bin/env python3
"""Publish verified independent PDFs already present on the authorized K1 machine.
Never synthesize missing PDFs or assign a DOI before an external deposit confirms it.
"""
from pathlib import Path
from datetime import datetime, timezone
from html import escape
from email.utils import format_datetime
import hashlib, json, shutil, sys
import xml.etree.ElementTree as ET
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path.home()/"Downloads"
SITE="https://ragunauthramsaroop.com"
TODAY="2026-09-25"
PAPERS=[
 dict(slug="guyana-2040",source="02_Guyana_2040_Strategic_Statecraft.pdf",title="Guyana 2040: From Resource Wealth to Strategic Statecraft",date="2026-09-12",category="National strategy",old="guyana-2040",keywords=["Guyana","resource governance","institutional capacity"],abstract="An independent framework for translating Guyana's resource wealth into enduring institutional, productive and national capabilities."),
 dict(slug="guyana-power-demand-2030",source="03_Guyana_Power_Demand_2030.pdf",title="Guyana Power Demand 2030",date="2026-09-15",category="Energy and infrastructure",old="guyana-power-demand-2030",keywords=["Guyana","electricity demand","power systems"],abstract="An evidence-led assessment that separates measured demand from development scenarios and evaluates generation and grid requirements through 2030."),
 dict(slug="critical-minerals-energy-security",source="Critical_Minerals_Are_the_New_Energy_Security.pdf",title="Critical Minerals Are the New Energy Security",date="2026-09-17",category="Mining and energy security",old="critical-minerals-energy-security",keywords=["critical minerals","supply chains","energy security"],abstract="A research monograph examining mining, processing concentration, trade, investment, circular supply and governance across strategic mineral value chains."),
 dict(slug="guyana-economy-2030",source="Guyana_Economy_2030.pdf",title="Guyana Economy 2030",date="2026-09-19",category="Economic development",old="guyana-economy-2030",keywords=["Guyana","macroeconomics","public finance"],abstract="An independent analysis of the choices, assumptions and risks involved in converting exceptional resource revenue into durable national prosperity."),
 dict(slug="new-geography-globalization",source="The_New_Geography_of_Globalization.pdf",title="The New Geography of Globalization",date="2026-09-19",category="Global trade and economic security",old="new-geography-globalization",keywords=["globalization","industrial policy","trade"],abstract="A comparative study of trade, industrial policy, investment, technology and supply-chain restructuring in a period of geopolitical fragmentation."),
 dict(slug="water-security-economic-security",source="Water_Security_as_Economic_Security.pdf",title="Water Security as Economic Security",date="2026-09-20",category="Infrastructure and resilience",old="water-security-economic-security",keywords=["water security","economic resilience","infrastructure"],abstract="A systems analysis of water risk across agriculture, energy, industry, AI infrastructure, finance, trade and national resilience to 2040."),
 dict(slug="guyana-lcds-2030",source="Guyana_LCDS_2030_Comprehensive_White_Paper.pdf",title="Guyana's Low Carbon Development Strategy 2030",date="2026-09-24",category="Climate finance and forest governance",old=None,keywords=["Guyana","LCDS 2030","forest finance","climate accountability"],abstract="An independent evidence review of forest conservation, carbon finance, national development and governance accountability under Guyana's Low Carbon Development Strategy 2030.")
]
STYLE="""<style>*,*::before,*::after{box-sizing:border-box}body{margin:0;background:#f4f7f5;color:#12372b;font:16px/1.68 system-ui,-apple-system,Segoe UI,sans-serif}a{color:#146648}a:hover{text-decoration:underline}.mast{background:#082e25;color:white;padding:21px max(22px,calc((100vw - 1100px)/2))}.mast a{color:#c5ecd8;margin-right:24px;text-decoration:none;font-weight:650}.wrap{max-width:1050px;padding:42px 22px 90px;margin:auto}.eyebrow{color:#438267;text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:800}h1{font-size:clamp(32px,5vw,50px);line-height:1.13;letter-spacing:-.035em;margin:12px 0 16px}h2{line-height:1.3}p{max-width:78ch}.lead{font-size:19px;color:#426256}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(275px,1fr));gap:18px;margin-top:30px}.paper{background:white;border:1px solid #d6e4dc;border-radius:14px;padding:25px;box-shadow:0 2px 10px #12372b09}.paper h2{font-size:22px;margin:11px 0}.cat{color:#52806b;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.08em}.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:23px}.btn{display:inline-block;background:#0d4935;color:white;padding:11px 17px;border-radius:8px;text-decoration:none;font-weight:700}.btn.alt{background:#e7f0eb;color:#0d4935}.note{border-left:4px solid #5ca17d;background:#edf5ef;padding:16px 21px;margin-top:34px}footer{border-top:1px solid #cadbd0;margin-top:45px;padding-top:25px;color:#557264;font-size:14px}small{color:#637b6b}</style>"""
def page(title,description,canonical,body,extra="",structured=None):
    ld=('<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False).replace("<","\\u003c")+'</script>') if structured else ""
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       '<title>'+escape(title)+' | Ragunauth Ramsaroop</title><meta name="description" content="'+escape(description,quote=True)+'">'
       '<meta name="author" content="Ragunauth Ramsaroop"><link rel="canonical" href="'+canonical+'">'
       '<meta property="og:type" content="article"><meta property="og:title" content="'+escape(title,quote=True)+'">'
       '<meta property="og:description" content="'+escape(description,quote=True)+'">'
       '<meta property="og:url" content="'+canonical+'"><link rel="alternate" type="application/rss+xml" title="Research archive RSS" href="/research-library/feed.xml">'
       +extra+STYLE+ld+'<script defer src="/tools/assets/analytics-loader.js"></script></head><body>'
       '<nav class="mast" aria-label="Research navigation"><a href="/">Ragunauth Ramsaroop</a><a href="/white-papers/">Research</a><a href="/research-library/">Full PDF Library</a></nav>'
       '<main class="wrap">'+body+'<footer>Independent research by Ragunauth Ramsaroop. Publications do not represent an official position of any employer or cited institution. '
       'No peer-review claim is made. Copyright remains with the author unless another licence is expressly specified.</footer></main></body></html>')
def write(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding="utf-8")
def record_paper(p):
    src=SOURCE/p["source"]
    if not src.is_file() or src.stat().st_size<25000:raise RuntimeError("Missing or empty approved source PDF: "+p["source"])
    doc=pymupdf.open(src)
    try:
        front="\n".join(doc[i].get_text() for i in range(min(2,len(doc)))).casefold()
        if len(doc)<5 or "ragunauth" not in front or "ramsaroop" not in front:raise RuntimeError("Front matter or page audit failed: "+p["source"])
        if p["slug"]=="guyana-lcds-2030" and "low carbon" not in front:raise RuntimeError("Wrong LCDS source")
        if p["slug"]=="guyana-power-demand-2030" and "power demand" not in front:raise RuntimeError("Wrong electricity source")
        pages=len(doc)
    finally:doc.close()
    dest=ROOT/"research-papers"/(p["slug"]+".pdf")
    dest.parent.mkdir(exist_ok=True)
    if dest.exists() and hashlib.sha256(dest.read_bytes()).digest()!=hashlib.sha256(src.read_bytes()).digest():
        raise RuntimeError("Existing published PDF differs; do not overwrite without version review: "+str(dest))
    shutil.copyfile(src,dest)
    data=dest.read_bytes()
    p.update(pages=pages,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),pdf_url=SITE+"/research-papers/"+p["slug"]+".pdf",page_url=SITE+"/research-library/"+p["slug"]+"/",doi=None,zenodo_status="not_submitted",ssrn_status="not_submitted")
    return p
def item_ld(p):
    return {"@context":"https://schema.org","@type":"ScholarlyArticle","headline":p["title"],"author":{"@type":"Person","name":"Ragunauth Ramsaroop","url":SITE+"/"},"datePublished":TODAY,"dateCreated":p["date"],"description":p["abstract"],"url":p["page_url"],"encoding":{"@type":"MediaObject","contentUrl":p["pdf_url"],"encodingFormat":"application/pdf"},"isAccessibleForFree":True,"isPartOf":{"@type":"CollectionPage","name":"Ragunauth Ramsaroop Research Library","url":SITE+"/research-library/"}}
def single_page(p):
    href="/research-papers/"+p["slug"]+".pdf"
    body=('<div class="eyebrow">'+escape(p["category"])+' | Independent white paper and research monograph</div><h1>'+escape(p["title"])+'</h1>'
        '<p class="lead">'+escape(p["abstract"])+'</p><p>Author: Ragunauth Ramsaroop<br>Source edition: '+p["date"]
        +' | Website publication: '+TODAY+' | '+str(p["pages"])+' pages</p>'
        '<div class="actions"><a class="btn" href="'+href+'" type="application/pdf">Read or download the complete PDF</a>'
        +('<a class="btn alt" href="/white-papers/'+p["old"]+'/">Read executive overview</a>' if p["old"] else "")
        +'<a class="btn alt" href="/research-library/">All papers</a></div>'
        '<div class="note"><strong>Research record:</strong> This is an independently authored work. Evidence cut-offs, methods, source references and limitations appear in the PDF. DOI pending an independently completed repository deposit. No external deposition or peer review is claimed.</div>')
    scholar=('<meta name="citation_title" content="'+escape(p["title"],quote=True)+'"><meta name="citation_author" content="Ramsaroop, Ragunauth">'
             '<meta name="citation_publication_date" content="'+TODAY+'"><meta name="citation_pdf_url" content="'+p["pdf_url"]+'">')
    # Scholar commonly requires PDFs below 5 MB; do not claim indexing for larger files.
    if p["bytes"]>=5000000:scholar=scholar.replace('<meta name="citation_pdf_url" content="'+p["pdf_url"]+'">',"")
    write(ROOT/"research-library"/p["slug"]/"index.html",page(p["title"],p["abstract"],p["page_url"],body,scholar,item_ld(p)))
def main():
    out=[record_paper(dict(p)) for p in PAPERS]
    for p in out:single_page(p)
    cards=[]
    for p in out:
        href="/research-papers/"+p["slug"]+".pdf"
        cards.append('<article class="paper" id="'+p["slug"]+'"><div class="cat">'+escape(p["category"])+'</div><h2><a href="/research-library/'+p["slug"]+'/">'+escape(p["title"])+'</a></h2><p>'+escape(p["abstract"])+'</p><small>'+str(p["pages"])+' pages | Source edition '+p["date"]+'</small><div class="actions"><a class="btn" href="'+href+'">Download PDF</a><a class="btn alt" href="/research-library/'+p["slug"]+'/">Publication details</a></div></article>')
    body='<div class="eyebrow">Independent research | Open access to read</div><h1>Research and white-paper library</h1><p class="lead">Complete PDFs covering economic development, mining, energy, climate finance, trade and resilience. Author: Ragunauth Ramsaroop.</p><div class="grid">'+''.join(cards)+'</div><div class="note">All documents retain their original author ownership. DOI identifiers will appear here only after confirmed Zenodo deposits. This website does not claim external peer review.</div><p>For executive summaries of other publications, visit <a href="/white-papers/">Research &amp; Publications</a>.</p>'
    index=page("Research and White Paper Library","Complete independent white papers and research monographs by Ragunauth Ramsaroop.",SITE+"/research-library/",body,structured={"@context":"https://schema.org","@type":"CollectionPage","name":"Research and White Paper Library","url":SITE+"/research-library/","hasPart":[item_ld(p) for p in out]})
    write(ROOT/"research-library"/"index.html",index)
    register={"author":"Ragunauth Ramsaroop","website_release":TODAY,"rights":"Copyright Ragunauth Ramsaroop. Licence selection required for external repository deposits.","status":"self-hosted, pending external deposition","papers":out,"excluded_sources":["09_Water_Security_as_Economic_Security.pdf (zero bytes; never publish)"]}
    write(ROOT/"research-library"/"publication-register.json",json.dumps(register,indent=2,ensure_ascii=False)+"\n")
    zen={"status":"metadata_ready_not_deposited","license":"AUTHOR_SELECTION_REQUIRED","doi_policy":"Do not invent DOIs or request a duplicate DOI if the exact version has one","creator":{"name":"Ramsaroop, Ragunauth","affiliation":"Independent researcher"},"deposits":[{"title":p["title"],"resource_type":"publication / report","creator":"Ramsaroop, Ragunauth","description":p["abstract"],"keywords":p["keywords"],"publication_date":TODAY,"filename":p["slug"]+".pdf","source_url":p["pdf_url"],"doi":None} for p in out]}
    write(ROOT/"research-library"/"zenodo-ready-metadata.json",json.dumps(zen,indent=2,ensure_ascii=False)+"\n")
    md="# External repository submission register\n\n"
    md+="The seven source PDFs are hosted on this website. No Zenodo DOI or SSRN posting is claimed until the external service confirms one. Select a repository licence before submission; do not assign Creative Commons by default.\n\n"
    md+="Zenodo official deposit: https://zenodo.org/uploads/new\n\nSSRN official submissions: https://www.ssrn.com/index.cfm/en/submit/\n\n"
    for p in out:md+="- "+p["title"]+": website PDF hosted; Zenodo not submitted; SSRN not submitted; DOI not assigned.\n"
    md+="\nAdditional 25 September publications awaiting transfer of the latest audited PDF to K1: Guyana Carbon Credits; Guyana and the Global Biodiversity Alliance; Who Pays for the Energy Transition; Omai Gold. Do not mistake a missing local source for publication.\n"
    write(ROOT/"research-library"/"EXTERNAL_DEPOSITS.md",md)
    # Independent RSS feed. Do not rewrite the existing site's feed or misstate third-party deposits.
    from xml.sax.saxutils import escape as xe
    pub=format_datetime(datetime(2026,9,25,19,30,tzinfo=timezone.utc))
    items="".join('<item><title>'+xe(p["title"])+'</title><link>'+p["page_url"]+'</link><guid isPermaLink="true">'+p["page_url"]+'</guid><description>'+xe(p["abstract"])+'</description><pubDate>'+pub+'</pubDate><enclosure url="'+p["pdf_url"]+'" type="application/pdf" length="'+str(p["bytes"])+'"/></item>' for p in out)
    rss='<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>Ragunauth Ramsaroop Research Publications</title><link>'+SITE+'/research-library/</link><description>Independent research PDFs</description><language>en</language>'+items+'</channel></rss>'
    write(ROOT/"research-library"/"feed.xml",rss)
    # Add download banners outside the hydrated Next.js root; do not break the site's existing client routing.
    targets=[("white-papers/index.html",None)]+[("white-papers/"+p["old"]+"/index.html",p) for p in out if p["old"]]
    for rel,p in targets:
        path=ROOT/rel
        if not path.is_file():raise RuntimeError("Expected existing publication page missing: "+rel)
        html=path.read_text(encoding="utf-8")
        if "RR_RESEARCH_ARCHIVE_2026" not in html:
            dest=("/research-papers/"+p["slug"]+".pdf") if p else "/research-library/"
            label=("Download full PDF: "+p["title"]) if p else "Download complete research PDFs"
            banner='<nav aria-label="Full research downloads" style="background:#0c4635;color:#fff;text-align:center;padding:10px 16px;font:600 14px system-ui" data-publication-archive="RR_RESEARCH_ARCHIVE_2026"><a style="color:#fff" href="'+dest+'">'+escape(label)+'</a> Â· <a style="color:#cce5d8" href="/research-library/">All downloadable papers</a></nav>'
            if '<body><div id="__next">' not in html:raise RuntimeError("Unexpected Next root markup: "+rel)
            html=html.replace('<body><div id="__next">','<body>'+banner+'<div id="__next">',1)
        if p:
            meta='<meta name="citation_title" content="'+escape(p["title"],quote=True)+'"><meta name="citation_author" content="Ramsaroop, Ragunauth"><meta name="citation_publication_date" content="'+TODAY+'">'
            if p["bytes"]<5000000:meta+='<meta name="citation_pdf_url" content="'+p["pdf_url"]+'">'
            if 'name="citation_title"' not in html:html=html.replace("</head>",meta+"</head>",1)
        path.write_text(html,encoding="utf-8")
    sm=ROOT/"sitemap.xml"
    sitemap=sm.read_text(encoding="utf-8")
    locs=[SITE+"/research-library/"]+[p["page_url"] for p in out]+[p["pdf_url"] for p in out]
    for url in locs:
        if "<loc>"+url+"</loc>" not in sitemap:
            sitemap=sitemap.replace("</urlset>","<url><loc>"+url+"</loc><lastmod>"+TODAY+"</lastmod></url>\n</urlset>")
    sm.write_text(sitemap,encoding="utf-8")
    readme=ROOT/"README.md"
    rd=readme.read_text(encoding="utf-8-sig")
    if "Complete PDF Library" not in rd:rd=rd.replace("- [White Papers]("+SITE+"/white-papers/)","- [White Papers]("+SITE+"/white-papers/)\n- [Complete PDF Library]("+SITE+"/research-library/)")
    readme.write_text(rd,encoding="utf-8")
    # Hard checks on all created public PDF links and pages.
    ET.parse(sm);ET.parse(ROOT/"research-library"/"feed.xml")
    for p in out:
        src=ROOT/"research-papers"/(p["slug"]+".pdf")
        assert src.exists() and src.stat().st_size==p["bytes"]
        assert (ROOT/"research-library"/p["slug"]/"index.html").exists()
    print(json.dumps({"status":"ARCHIVE_READY","pdfs":len(out),"pages":len(out)+1,"bytes":sum(p["bytes"] for p in out),"skipped_zero_byte_sources":1,"checks":"PASS","external_deposits":"NOT_SUBMITTED","titles":[p["title"] for p in out]},indent=2))
if __name__=="__main__":main()
