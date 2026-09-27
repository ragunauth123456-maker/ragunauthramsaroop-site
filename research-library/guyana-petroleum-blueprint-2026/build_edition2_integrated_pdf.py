#!/usr/bin/env python3
"""Build a truthful Edition 2 integrated DEVELOPMENT PDF from the ten GitHub Parts.

This is a readable manuscript export, not the peer-reviewed final release.
No research text, citations or financial figures are invented by the renderer.
"""
from __future__ import annotations
import csv,hashlib,html,json,re
from pathlib import Path
import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate,Frame,PageTemplate,PageBreak,
 Paragraph,Spacer,Table,TableStyle,HRFlowable)
from reportlab.platypus.tableofcontents import TableOfContents
try:
 from svglib.svglib import svg2rlg
except ImportError:
 svg2rlg=None

D=Path(__file__).resolve().parent
PDF=D/"guyana-petroleum-edition-2-expanded-working-manuscript.pdf"
AUDIT=D/"EDITION2_PDF_AUDIT.json"
NAVY=colors.HexColor("#142D43");GREEN=colors.HexColor("#217355")
INK=colors.HexColor("#233748");PALE=colors.HexColor("#E8F1ED")
fontdir=Path("/usr/share/fonts/truetype/dejavu")
if (fontdir/"DejaVuSans.ttf").is_file():
 for name,file in [("F","DejaVuSans.ttf"),("FB","DejaVuSans-Bold.ttf")]:
  pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
 pdfmetrics.registerFontFamily("F",normal="F",bold="FB")
else:
 F="Helvetica";FB="Helvetica-Bold"
if "F" in pdfmetrics.getRegisteredFontNames():F="F";FB="FB"
S={
 "body":ParagraphStyle("B",fontName=F,fontSize=9.6,leading=16.0,textColor=INK,spaceAfter=9,allowOrphans=0,allowWidows=0),
 "small":ParagraphStyle("Sm",fontName=F,fontSize=8.1,leading=12,textColor=INK,spaceAfter=7),
 "bullet":ParagraphStyle("Bu",fontName=F,fontSize=9.4,leading=15,textColor=INK,leftIndent=16,firstLineIndent=-9,spaceAfter=5),
 "h1":ParagraphStyle("H1",fontName=FB,fontSize=17,leading=23,textColor=NAVY,spaceBefore=17,spaceAfter=10,keepWithNext=True),
 "h2":ParagraphStyle("H2",fontName=FB,fontSize=11.6,leading=17,textColor=GREEN,spaceBefore=15,spaceAfter=8,keepWithNext=True),
 "h3":ParagraphStyle("H3",fontName=FB,fontSize=10.1,leading=15,textColor=NAVY,spaceBefore=10,spaceAfter=6,keepWithNext=True),
 "cover":ParagraphStyle("C",fontName=FB,fontSize=29,leading=39,textColor=NAVY,spaceAfter=17),
 "toc":ParagraphStyle("T",fontName=F,fontSize=10,leading=19,textColor=NAVY,leftIndent=18,firstLineIndent=-18),
 "source":ParagraphStyle("R",fontName=F,fontSize=7.6,leading=12,textColor=INK,spaceAfter=7)
}
PARTS="I II III IV V VI VII VIII IX X".split()
texts={p:(D/f"FLAGSHIP_PART_{p}_MANUSCRIPT.md").read_text(encoding="utf-8") for p in PARTS}
src=(D/"SOURCE_REGISTER.md").read_text(encoding="utf-8")
sources=[]
for line in src.splitlines():
 if re.match(r"^\|\s*S\d{2,3}\s*\|",line):
  row=[c.strip() for c in line.strip().strip("|").split("|")]
  if len(row)>=5:sources.append(row[:5])
source_ids={row[0] for row in sources}
assert len(sources)>=140 and len(PARTS)==10
count=re.compile(r"\b[A-Za-z0-9]+(?:[-'’][A-Za-z0-9]+)*\b")
words=sum(len(count.findall(t)) for t in texts.values())

def mk(t):
 t=html.escape(t.strip(),quote=False)
 t=re.sub(r"\*\*([^*]+)\*\*",r"<b>\1</b>",t)
 t=re.sub(r"\bS(\d{2,3})\b",lambda m:('<link href="#S'+str(int(m[1])).zfill(2)+'" color="#217355">'+m[0]+'</link>') if ('S'+str(int(m[1])).zfill(2)) in source_ids else m[0],t)
 return t

class Book(BaseDocTemplate):
 def __init__(self):
  super().__init__(str(PDF),pagesize=A4,leftMargin=22*mm,rightMargin=22*mm,
   topMargin=19*mm,bottomMargin=20*mm,title="Guyana Petroleum Transformation Edition 2 (Expanded Working Manuscript)",
   author="Ragunauth Ramsaroop",subject="Independent research; unreviewed development edition")
  self.addPageTemplates(PageTemplate(id="p",frames=[Frame(self.leftMargin,self.bottomMargin,self.width,self.height,id="f")],onPage=self.bg))
 def beforeDocument(self):self.n=0
 def bg(self,c,d):
  c.saveState()
  if d.page==1:
   c.setFillColor(GREEN);c.rect(0,0,7*mm,A4[1],stroke=0,fill=1)
  else:
   c.setStrokeColor(PALE);c.line(22*mm,15*mm,A4[0]-22*mm,15*mm)
   c.setFillColor(colors.HexColor("#536777"));c.setFont(F,7)
   c.drawString(22*mm,10*mm,"RAGUNAUTH RAMSAROOP | EDITION 2 EXPANDED WORKING MANUSCRIPT")
   c.drawRightString(A4[0]-22*mm,10*mm,str(d.page))
  c.restoreState()
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and getattr(f,"in_toc",False):
   self.n+=1;k=f"p{self.n}";self.canv.bookmarkPage(k)
   self.notify("TOCEntry",(0,f.getPlainText(),self.page,k))
   self.canv.addOutlineEntry(f.getPlainText()[:110],k,level=0)
def P(t,style="body"):return Paragraph(mk(t),S[style])
def H(t,style="h1",toc=False):
 p=P(t,style);p.in_toc=toc;return p

def parse_md(txt):
 out=[];para=[];li=[]
 def flush():
  if para:out.append(P(" ".join(para)));para.clear()
 def flush_li():
  for x in li:out.append(P("• "+x,"bullet"))
  li.clear()
 for line in txt.splitlines():
  t=line.strip()
  if not t:flush();flush_li();continue
  if t.startswith("#"):
   flush();flush_li()
   depth=len(t)-len(t.lstrip("#"));head=t[depth:].strip()
   if depth==1:continue
   out.append(H(head,"h2" if depth<=3 else "h3"));continue
  if t.startswith(("- ","* ")):
   flush();li.append(t[2:]);continue
  if re.match(r"^\d+[.)]\s+",t):
   flush();li.append(t);continue
  if t.startswith("|"):
   flush();flush_li();out.append(P(t.replace("|","  /  "),"small"));continue
  if t=="---":flush();flush_li();continue
  flush_li();para.append(t)
 flush();flush_li()
 return out
SOURCES_TITLE="Source register (dated and qualified)"
story=[Spacer(1,26*mm),P("INDEPENDENT RESEARCH  /  27 SEPTEMBER 2026","small"),
       P("GUYANA'S PETROLEUM TRANSFORMATION","cover"),
       HRFlowable(width="100%",thickness=3,color=GREEN,spaceAfter=18),
       P("Exploration, the Stabroek agreement, first oil, sovereign wealth, environmental governance and a transferable blueprint for emerging producers."),
       Spacer(1,9*mm),P("Independent research by Ragunauth Ramsaroop","h2"),
       P("Edition 2.0 — expanded ten-part WORKING manuscript. Not the commissioned final edition; external peer review pending.","small"),
       Spacer(1,9*mm),P(f"{words:,} lexical core words and {len(sources)} registered sources. The full 120,000–150,000 word target is NOT yet achieved; this edition makes all existing expanded core writing available instead of claiming unfinished research is complete.","small"),
       PageBreak(),H("Contents")]
toc=TableOfContents();toc.levelStyles=[S["toc"]];story.extend([toc,PageBreak(),
 H("Research integrity and publication status"),
 P("This integrated development export contains the full ten-Part core manuscript and a dated source register. It replaces the much shorter integrated core of Edition 1.2. Research dossiers and wide technical CSVs remain editable in the companion cloud-worker package rather than being counted as additional core chapters."),
 P("Unresolved release gates: sufficient new substantive core research; full source-to-claim verification; precise first-half 2026 NRF cash/accrual bridge; direct legal, environmental and household outcome evidence; external specialist review; and the final graphic, accessibility and editorial QA."),
 P("Government-reported H1 2026 petroleum receipts and fund accounting use different timing boundaries. An approximately US$184 million difference has a likely December 2025 receivables explanation, but the last transaction-level reconciliation remains open."),
 P("The ten complete integrated Parts begin on the next page; the accompanying editable CSVs retain the complete technical detail.","small")])
names=["Historical foundations and pre-discovery readiness","Petroleum contracts and fiscal mechanics","Development approvals and offshore production","The Natural Resource Fund and public wealth","Environmental governance and spill readiness","Local content and social distribution","Economic transformation and diversification","Transparency and institutional learning","International comparator mechanisms","A new-producer operating blueprint"]
# Original source-linked exhibit generated by the independent deterministic worker.
fig=D.parent.parent/"edition2-worker-artifacts"/"nrf_2022_2025.svg"
if fig.is_file() and svg2rlg is not None:
 drawing=svg2rlg(str(fig))
 if drawing:
  ratio=min(164*mm/drawing.width,94*mm/drawing.height)
  drawing.scale(ratio,ratio);drawing.width*=ratio;drawing.height*=ratio
  story.extend([PageBreak(),H("Original exhibit | Natural Resource Fund 2022–2025"),drawing,
   P("Reproducible bar chart from the source-registered rounded annual ledger (S44, S88, S109). H1 2026 excluded because the exact recognition bridge is unresolved.","small")])
for p,name in zip(PARTS,names):
 story.extend([PageBreak(),H(f"PART {p} | {name}",toc=True),
  HRFlowable(width="100%",thickness=1.3,color=GREEN,spaceAfter=10)])
 story.extend(parse_md(texts[p]))
# Selected high-readability tables: full machine-readable data remain in companion package.
story.extend([PageBreak(),H("Reproducible data exhibits"),
 P("All figures below are copied from the dated editable CSVs rather than invented for the PDF. Planned capacities must not be treated as realized production.")])
def table_from_csv(file,fields,titles,widths):
 with (D/file).open(newline="",encoding="utf-8") as inp: rows=list(csv.DictReader(inp))
 cell=lambda t: P(str(t),"small")
 grid=[[cell(x) for x in titles]]
 for row in rows:
  grid.append([cell(str(row.get(field,""))[:110]) for field in fields])
 tab=Table(grid,colWidths=[w*mm for w in widths],repeatRows=1,hAlign="LEFT")
 tab.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),PALE),
 ("VALIGN",(0,0),(-1,-1),"TOP"),
 ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#CCDCD2")),
 ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
 ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)]))
 return tab
story.append(H("Seven-development project register","h2"))
story.append(table_from_csv("OFFSHORE_PROJECT_REGISTER.csv",
 ["development","fpsO","first_oil_or_status_at_2026_09_27","design_oil_capacity_bpd"],
 ["Development","FPSO","Status at 27 Sep 2026","Design bpd"],[34,33,73,25]))
story.append(P("Project-specific source IDs and evidence classifications appear in OFFSHORE_PROJECT_REGISTER.csv. Future startups are not observed facts.","small"))
story.append(H("NRF annual stock and flow (USD millions)","h2"))
story.append(table_from_csv("NRF_ANNUAL_LEDGER.csv",
 ["year","petroleum_and_other_inflows_usd_m","withdrawals_usd_m","closing_balance_usd_m","status"],
 ["Period","Inflows","Withdrawals","Closing","Evidence status"],[24,27,27,27,60]))
story.append(P("2020-21 and 2026-H1 carry explicit provisional/open statuses. The 2025 December receivable is not double-counted as fresh 2026 accrued revenue. Primary series: S44, S88, S109, S137.","small"))

story.extend([PageBreak(),H("Evidence limits and corrections"),
 P("2020–2021 NRF interest splits and the H1 2026 cash/accrual reconciliation remain provisional where labelled. Permit wording is not proof of executed insurance or compliance. EITI status is dated; legal appellate reasons and full oil-pollution commencement should be rechecked from authoritative records."),
 P("All scenarios in companion CSVs are explicitly illustrative and do not constitute forecasts of petroleum production, government cash or political outcomes."),
 PageBreak(),H(SOURCES_TITLE),
 P(f"The {len(sources)} entries below come from the GitHub Edition 2 source register. Source-ID hyperlinks in the narrative jump to their respective entries. Claim-level external review remains pending.","small")])
for sid,title,evidence,limit,url in sources:
 story.append(Paragraph(f'<a name="{sid}"/><b>{mk(sid)} {html.escape(title)}</b>',S["source"]))
 story.append(P("Evidence: "+evidence,"small"))
 story.append(P("Limit: "+limit,"small"))
 story.append(Paragraph(f'<link href="{html.escape(url,quote=True)}" color="#217355">{html.escape(url)}</link>',S["small"]))
 story.append(Spacer(1,2*mm))
Book().multiBuild(story,maxPasses=5)
d=fitz.open(PDF)
n=d.page_count; blank=[i+1 for i,p in enumerate(d) if len(p.get_text().split())<8]
alltext="\n".join(p.get_text() for p in d)
assert not blank and all(("S"+str(i).zfill(2)) in alltext for i in range(1,len(sources)+1))
assert len(d.get_toc())==10 and n>=150 and len(alltext)>300000
sha=hashlib.sha256(PDF.read_bytes()).hexdigest()
audit={"edition":"2.0-expanded-WORKING-manuscript","publication_complete":False,
       "external_peer_review":"pending","pdf":PDF.name,"pages":n,"ten_core_parts":True,
       "core_lexical_words":words,"core_word_minimum_met":words>=120000,
       "sources":len(sources),"source_ids_rendered":True,"toc_entries":len(d.get_toc()),
       "blank_pages":blank,"sha256":sha,"legal_and_nrf_review":"open"}
AUDIT.write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
print(json.dumps(audit,indent=2))
