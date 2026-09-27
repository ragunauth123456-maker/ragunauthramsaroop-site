#!/usr/bin/env python3
"""Build and audit the Guyana petroleum flagship reference edition.

Independent research publication. External peer review is not claimed.
Uses only repository source files and reproducible scenario data.
"""
from __future__ import annotations
import csv, hashlib, html, json, re
from collections import Counter
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, PageBreak, Paragraph, Spacer, Table, TableStyle, Flowable
from reportlab.platypus.tableofcontents import TableOfContents
import fitz

BASE=Path(__file__).resolve().parent
OUT=BASE/"guyana-petroleum-transformation-edition-1.2-scrutiny-candidate.pdf"
MANIFEST=BASE/"PUBLICATION_MANIFEST.json"
AUDIT=BASE/"FLAGSHIP_PDF_AUDIT.json"
NAVY=colors.HexColor("#102A43"); FOREST=colors.HexColor("#17624F"); SAGE=colors.HexColor("#E4F0EA")
TEXT=colors.HexColor("#243B53"); GRAY=colors.HexColor("#627D98"); PALE=colors.HexColor("#F4F8F6")
fp=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"); fb=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
if fp.exists() and fb.exists():
    pdfmetrics.registerFont(TTFont("R",str(fp))); pdfmetrics.registerFont(TTFont("RB",str(fb)))
    pdfmetrics.registerFontFamily("R",normal="R",bold="RB"); FONTA,FONTB="R","RB"
else: FONTA,FONTB="Helvetica","Helvetica-Bold"
s=getSampleStyleSheet()
s.add(ParagraphStyle(name="BodyF",fontName=FONTA,fontSize=9.35,leading=15.2,textColor=TEXT,spaceAfter=8,allowWidows=0,allowOrphans=0))
s.add(ParagraphStyle(name="H1F",fontName=FONTB,fontSize=17.5,leading=23,textColor=NAVY,spaceBefore=20,spaceAfter=10,keepWithNext=1))
s.add(ParagraphStyle(name="H2F",fontName=FONTB,fontSize=12.4,leading=17.5,textColor=FOREST,spaceBefore=15,spaceAfter=8,keepWithNext=1))
s.add(ParagraphStyle(name="H3F",fontName=FONTB,fontSize=10.5,leading=15,textColor=NAVY,spaceBefore=10,spaceAfter=6,keepWithNext=1))
s.add(ParagraphStyle(name="BulletF",parent=s["BodyF"],leftIndent=18,firstLineIndent=-11,spaceAfter=5))
s.add(ParagraphStyle(name="SmallF",fontName=FONTA,fontSize=8.0,leading=12.2,textColor=GRAY,spaceAfter=5))
s.add(ParagraphStyle(name="RefF",fontName=FONTA,fontSize=7.8,leading=12.0,textColor=TEXT,leftIndent=8,firstLineIndent=-8,spaceAfter=8))
s.add(ParagraphStyle(name="TOCF",fontName=FONTA,fontSize=9.3,leading=16,textColor=TEXT,leftIndent=18,firstLineIndent=-18))
s.add(ParagraphStyle(name="CoverK",fontName=FONTB,fontSize=10,leading=16,textColor=FOREST,spaceAfter=15))
s.add(ParagraphStyle(name="CoverT",fontName=FONTB,fontSize=29,leading=37,textColor=NAVY,spaceAfter=18))
s.add(ParagraphStyle(name="CoverS",fontName=FONTA,fontSize=13,leading=20,textColor=TEXT,spaceAfter=20))

def mk(x):
    x=html.escape(x)
    x=re.sub(r"\*\*(.+?)\*\*",r"<b>\1</b>",x)
    x=re.sub(r"\[S(\d{2,3})\]",r'<font color="#17624F">[S\1]</font>',x)
    return x

class Rule(Flowable):
    def __init__(self): Flowable.__init__(self); self.width,self.height=166*mm,2*mm
    def draw(self):
        self.canv.setStrokeColor(FOREST); self.canv.setLineWidth(2); self.canv.line(0,1*mm,self.width,1*mm)

class Doc(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=22*mm,rightMargin=22*mm,topMargin=20*mm,bottomMargin=20*mm,
                         title="Guyana's Petroleum Transformation: The Guyana Sequence",
                         author="Ragunauth Ramsaroop",subject="Independent exploration-to-production case study and implementation blueprint")
        f=Frame(self.leftMargin,self.bottomMargin,self.width,self.height,id="f")
        self.addPageTemplates([PageTemplate(id="p",frames=f,onPage=self.bg)]); self.nh=0
    def beforeDocument(self): self.nh=0
    def bg(self,c,d):
        c.saveState()
        if d.page==1:
            c.setFillColor(FOREST); c.rect(0,0,9*mm,A4[1],stroke=0,fill=1)
        else:
            c.setStrokeColor(SAGE); c.line(22*mm,14.5*mm,A4[0]-22*mm,14.5*mm)
            c.setFont(FONTA,7); c.setFillColor(GRAY)
            c.drawString(22*mm,10*mm,"INDEPENDENT RESEARCH | AUDITED PUBLICATION CANDIDATE | 27 SEP 2026")
            c.drawRightString(A4[0]-22*mm,10*mm,str(d.page))
        c.restoreState()
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and getattr(f,"toc_level",None) is not None:
            self.nh+=1; key=f"h{self.nh}"; self.canv.bookmarkPage(key)
            self.notify("TOCEntry",(f.toc_level,f.getPlainText(),self.page,key))
            if f.toc_level<=1: self.canv.addOutlineEntry(f.getPlainText()[:120],key,level=f.toc_level,closed=False)

def h1(x):
    p=Paragraph(mk(x),s["H1F"]); p.toc_level=0; return p

def flow(text, dedupe=None, toc=True):
    story=[]; para=[]
    def flush():
        if not para:return
        raw=" ".join(para).strip(); para.clear()
        norm=re.sub(r"\s+"," ",raw.lower())
        if dedupe is not None and len(raw)>250:
            if norm in dedupe:return
            dedupe.add(norm)
        story.append(Paragraph(mk(raw),s["BodyF"]))
    for line in text.splitlines():
        v=line.strip()
        if not v: flush(); continue
        if v.startswith("# "):
            flush(); p=Paragraph(mk(v[2:]),s["H1F"])
            if toc: p.toc_level=0
            story.append(p)
        elif v.startswith("## "):
            flush(); p=Paragraph(mk(v[3:]),s["H1F"])
            if toc: p.toc_level=0
            story.append(p)
        elif v.startswith("### "):
            flush(); title=v[4:]
            if re.match(r"^Chapter\s+\d+\.",title):
                title=re.sub(r"^Chapter","Analytical section",title,count=1)
            p=Paragraph(mk(title),s["H2F"])
            story.append(p)
        elif v.startswith("#### "):
            flush(); story.append(Paragraph(mk(v[5:]),s["H3F"]))
        elif v.startswith(("- ","* ")):
            flush(); story.append(Paragraph("&#8226; "+mk(v[2:]),s["BulletF"]))
        elif re.match(r"^\d+\.\s",v):
            flush(); story.append(Paragraph(mk(v),s["BulletF"]))
        elif v.startswith("|"):
            flush()
        else: para.append(v)
    flush(); return story
def src_rows(txt):
    out=[]
    for line in txt.splitlines():
        if re.match(r"^\|\s*S\d{2,3}\s*\|",line):
            cells=[x.strip() for x in line.strip().strip("|").split("|")]
            if len(cells)>=5:out.append(cells[:5])
    return out

def _fmt_cell(field,value):
    try: x=float(value)
    except Exception: return str(value).replace("_"," ")
    if field in ("government_share_of_gross","requested_cost_fraction","volume_factor","return_rate"):
        return "{:.1f}%".format(x*100)
    if field=="price_usd_per_barrel": return "${:,.0f}".format(x)
    if field=="barrels_illustrative": return "{:.2f}m".format(x/1_000_000)
    if field.endswith("_usd"):
        scale=1_000_000_000 if abs(x)>=1_000_000_000 else 1_000_000
        suffix="bn" if scale==1_000_000_000 else "m"
        return "${:,.2f}{}".format(x/scale,suffix)
    if field=="year_index": return str(int(x))
    return "{:,.2f}".format(x)

def add_csv_table(story,path,title,fields,labels,note):
    story.extend([PageBreak(),h1(title),Paragraph(mk(note),s["SmallF"])])
    with path.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
    if not rows:return
    grid=[[Paragraph(mk(x),s["SmallF"]) for x in labels]]
    for row in rows:
        grid.append([Paragraph(mk(_fmt_cell(field,row.get(field,""))),s["SmallF"]) for field in fields])
    widths=[164*mm/len(fields)]*len(fields)
    t=Table(grid,colWidths=widths,repeatRows=1,hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),SAGE),
                           ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#C8D8D1")),
                           ("VALIGN",(0,0),(-1,-1),"TOP"),
                           ("FONTSIZE",(0,0),(-1,-1),7.2),
                           ("TOPPADDING",(0,0),(-1,-1),4),
                           ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story.append(t)
core=[f"FLAGSHIP_PART_{x}_MANUSCRIPT.md" for x in ["I","II","III","IV","V","VI","VII","VIII","IX","X"]]
evidence=[
"MANUSCRIPT_WORKING_DRAFT.md","COUNTRY_PLAYBOOK.md","NEW_PRODUCER_BLUEPRINT.md","COMPARATIVE_CASES.md",
"PART_I_FOUNDATIONS_RESEARCH_DOSSIER.md","PART_II_CONTRACT_AND_COST_RECOVERY_DOSSIER.md",
"PART_III_PRE_FIRST_OIL_AND_PRODUCTION_DOSSIER.md","PART_IV_NRF_AND_PUBLIC_BALANCE_SHEET_DOSSIER.md",
"PART_V_ENVIRONMENT_CLIMATE_AND_SPILL_DOSSIER.md","PART_VI_LOCAL_CONTENT_AND_SOCIAL_OUTCOMES_DOSSIER.md",
"PART_VII_ECONOMIC_TRANSFORMATION_DOSSIER.md","PART_VIII_ACCOUNTABILITY_AND_INSTITUTIONAL_LEARNING_DOSSIER.md",
"PART_IX_COMPARATIVE_CASES_DOSSIER.md","PART_X_NEW_PRODUCER_OPERATING_MANUAL.md",
"NRF_RECONCILIATION_WORKBOOK.md","ENVIRONMENTAL_PERMIT_AND_RISK_REGISTER.md","MODEL_METHODS_AND_LIMITATIONS.md",
"LEGAL_EVIDENCE_LEDGER.md","CORRECTIONS_REGISTER.md"]
annex=sorted(p.name for p in BASE.glob("TECHNICAL_ANNEX_*.md"))
hardening=(BASE/"FLAGSHIP_HARDENING_ADDENDUM.md").read_text(encoding="utf-8")
adversarial=(BASE/"ADVERSARIAL_PUBLICATION_AUDIT.md").read_text(encoding="utf-8")
claim_matrix=(BASE/"CLAIM_SOURCE_MATRIX.md").read_text(encoding="utf-8")
assert len(core)==10 and len(annex)>=13
all_text={n:(BASE/n).read_text(encoding="utf-8") for n in core+evidence+annex}
core_section_count=sum(len(re.findall(r"^###\s+Chapter\s+\d+\.",all_text[n],flags=re.M)) for n in core)
brief=(BASE/"EXECUTIVE_BRIEF.md").read_text(encoding="utf-8")
sources=(BASE/"SOURCE_REGISTER.md").read_text(encoding="utf-8")
gates=(BASE/"PUBLICATION_REVIEW_GATES.md").read_text(encoding="utf-8")
source_rows=src_rows(sources); assert len(source_rows)>=106

# exact duplicate long-paragraph audit in source corpus
paras=[]
for name,txt in all_text.items():
    for p in re.split(r"\n\s*\n",txt):
        q=re.sub(r"\s+"," ",p.strip().lower())
        if len(q)>=300 and not q.startswith("#"):paras.append(q)
counts=Counter(paras); duplicate_long=sum(v-1 for v in counts.values() if v>1)

story=[Spacer(1,22*mm),Paragraph("GUYANA | EXPLORATION TO PRODUCTION",s["CoverK"]),
       Paragraph("GUYANA'S PETROLEUM<br/>TRANSFORMATION",s["CoverT"]),Rule(),Spacer(1,7*mm),
       Paragraph("The Guyana Sequence: exploration, contracts, first oil, sovereign wealth, environmental stewardship, national development and a transferable blueprint for emerging producers",s["CoverS"]),
       Spacer(1,9*mm),Paragraph("Independent research by Ragunauth Ramsaroop",s["H2F"]),
       Paragraph("Edition 1.2 | Scrutiny-hardened publication candidate | Evidence cut-off: 27 September 2026",s["BodyF"]),
       Paragraph("Independent research. No political or electoral ranking. Government, operator, multilateral, judicial and stakeholder positions are attributed. External peer review remains pending.",s["SmallF"]),
       PageBreak(),h1("Contents")]
toc=TableOfContents(); toc.levelStyles=[s["TOCF"],s["TOCF"]]; story.extend([toc,PageBreak(),h1("Executive brief")])
story.extend(flow("\n".join(brief.splitlines()[3:]),set(),toc=True))
story.extend([PageBreak(),h1("Audit hardening addendum")]); story.extend(flow(hardening,set(),toc=True))

seen=set()
story.extend([PageBreak(),h1("Part I-X | Integrated flagship manuscript")])
for n in core:
    story.append(PageBreak()); story.extend(flow(all_text[n],seen,toc=True))

story.extend([PageBreak(),h1("Evidence dossiers and implementation workbooks"),
              Paragraph("Supporting dossiers preserve detailed research notes, reconciliation methods and operating tools. They are evidence annex material, not additional core chapters.",s["BodyF"])])
for n in evidence:
    story.append(PageBreak()); story.extend(flow(all_text[n],seen,toc=False))

story.extend([PageBreak(),h1("Technical annexes")])
for n in annex:
    story.append(PageBreak()); story.extend(flow(all_text[n],seen,toc=False))

add_csv_table(story,BASE/"ILLUSTRATIVE_SCENARIOS.csv","Scenario tables | Contract sensitivity",
              ["barrels_illustrative","price_usd_per_barrel","requested_cost_fraction","gross_sales_usd","government_total_usd","government_share_of_gross"],
              ["Barrels","Price","Cost share","Gross sales","Government","Gov. share"],
              "Illustrative arithmetic only. Values are not forecasts and do not represent observed government receipts.")
add_csv_table(story,BASE/"ILLUSTRATIVE_PRODUCTION_SHOCKS.csv","Scenario tables | Production shocks",
              ["volume_factor","price_usd_per_barrel","requested_cost_fraction","gross_sales_usd","government_total_usd","government_share_of_gross"],
              ["Volume factor","Price","Cost share","Gross sales","Government","Gov. share"],
              "Combined volume, price and cost sensitivities. All inputs are illustrative.")
add_csv_table(story,BASE/"ILLUSTRATIVE_FUND_STRESS.csv","Scenario tables | Sovereign-fund stress",
              ["scenario","year_index","opening_usd","deposits_usd","withdrawals_usd","closing_usd"],
              ["Scenario","Year","Opening","Deposits","Withdrawals","Closing"],
              "Synthetic sovereign-fund stress paths. They are decision tests, not projections of the Natural Resource Fund.")

story.extend([PageBreak(),h1("Adversarial publication audit")]); story.extend(flow(adversarial,seen,toc=False))
story.extend([PageBreak(),h1("High-risk claim audit")])
for line in claim_matrix.splitlines():
    if re.match(r"^\|\s*C\d{3}\s*\|",line):
        cells=[x.strip() for x in line.strip().strip("|").split("|")]
        if len(cells)>=5:
            vals=[html.escape(x) for x in cells[:5]]
            story.append(Paragraph("<b>{}</b> {}<br/><font color=\"#17624F\">Sources: {} | Status: {}</font><br/><font color=\"#627D98\">{}</font>".format(*vals),s["RefF"]))

story.extend([PageBreak(),h1("Publication review gates")]); story.extend(flow(gates,seen,toc=False))
story.extend([PageBreak(),h1("Dated source register"),
              Paragraph("Source IDs are used throughout the publication. URLs point to the public source used for the stated claim. Limitations remain part of the evidence record.",s["BodyF"])])
for ident,label,evidence_text,caveat,url in source_rows:
    u=html.escape(url,quote=True)
    body=f'<b>{html.escape(ident)}</b> {html.escape(label)}<br/>{html.escape(evidence_text)}<br/><font color="#627D98">Limit: {html.escape(caveat)}</font><br/><link href="{u}" color="#17624F">{html.escape(url)}</link>'
    story.append(Paragraph(body,s["RefF"]))
marker="### Priority evidence items for future revision and external review"
if marker in sources:
    story.extend([PageBreak(),h1("Open evidence items")])
    story.extend(flow(marker+sources.split(marker,1)[1],seen,toc=False))

doc=Doc(OUT); doc.multiBuild(story)
pdf=fitz.open(OUT); pages=pdf.page_count; texts=[p.get_text() for p in pdf]; flat="\n".join(texts)
word_re=re.compile(r"\b[A-Za-z0-9][A-Za-z0-9'’-]*\b")
lex=lambda t: len(word_re.findall(t))
substantive=sum(lex(t)>=100 for t in texts[2:])
blank=sum(lex(t)<15 for t in texts)
def page_of(needle):
    for i,t in enumerate(texts):
        if needle in t:return i
    return None
core_hits=[i for i,t in enumerate(texts) if "Part I-X | Integrated flagship manuscript" in t]
core_start=max(core_hits) if core_hits else None
evidence_hits=[i for i,t in enumerate(texts) if "Supporting dossiers preserve detailed research notes" in t]
evidence_start=max(evidence_hits) if evidence_hits else None
core_pages=(evidence_start-core_start) if core_start is not None and evidence_start is not None else None
core_lexical_words=sum(lex(t) for t in texts[core_start:evidence_start]) if core_pages is not None else None
assert core_pages is not None and core_pages>=100, f"Core manuscript boundary audit failed: {core_pages}"
assert core_lexical_words is not None and core_lexical_words>=20000, f"Core manuscript word audit failed: {core_lexical_words}"
assert all(row[0] in flat for row in source_rows)
assert "Natural Resource Fund" in flat and "Oil Pollution" in flat and "Timor-Leste" in flat
assert "Petroleum Activities Act" in flat and "International Court of Justice" in flat
assert pages>=400, f"Publication candidate below 400-page research-compendium gate: {pages}"
assert substantive>=int((pages-2)*0.62), f"Too many sparse pages: {substantive}/{pages}"
assert blank<=18, f"Too many near-blank pages: {blank}"
assert duplicate_long<=25, f"Source corpus contains too many exact long-paragraph duplicates: {duplicate_long}"
sha=hashlib.sha256(OUT.read_bytes()).hexdigest()
word_counts={k:len(v.split()) for k,v in all_text.items()}
audit={
 "document":OUT.name,"edition":"1.2-scrutiny-candidate","stage":"publication_candidate",
 "evidence_cutoff":"2026-09-27","pages_actual":pages,
 "substantive_pages_at_least_100_lexical_words":substantive,"near_blank_pages":blank,
 "core_integrated_pages":core_pages,"core_integrated_lexical_words":core_lexical_words,"core_analytical_sections":core_section_count,
 "source_records":len(source_rows),"core_parts":len(core),"technical_annexes":len(annex),
 "evidence_workbooks":len(evidence),"research_words_before_deduplication":sum(word_counts.values())+len(brief.split())+len(sources.split())+len(gates.split())+len(hardening.split())+len(adversarial.split()),
 "exact_duplicate_long_paragraphs_in_source_corpus":duplicate_long,
 "sha256":sha,"citations_embedded":True,"searchable_text":len(flat)>100000,
 "tables_redesigned_for_readability":True,"tagged_pdf_accessibility":False,
 "internal_adversarial_audit":"completed_with_open_gates","pinpoint_legal_evidence_ledger":True,"corrections_register":True,
 "external_peer_review":"pending","political_ranking":"none",
 "publication_complete":False
}
AUDIT.write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
manifest_files=[
 OUT,
 AUDIT,
 BASE/"SOURCE_REGISTER.md",
 BASE/"CLAIM_SOURCE_MATRIX.md",
 BASE/"LEGAL_EVIDENCE_LEDGER.md",
 BASE/"CORRECTIONS_REGISTER.md",
 BASE/"RESEARCH_INTEGRITY_AUDIT.json",
 BASE/"ILLUSTRATIVE_SCENARIOS.csv",
 BASE/"ILLUSTRATIVE_PRODUCTION_SHOCKS.csv",
 BASE/"ILLUSTRATIVE_FUND_STRESS.csv",
]
file_hashes={}
for path in manifest_files:
    if path.exists():
        file_hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
manifest={
 "edition":"1.2-scrutiny-candidate",
 "evidence_cutoff":"2026-09-27",
 "publication_status":"candidate",
 "external_peer_review":"pending",
 "pdf":OUT.name,
 "pdf_sha256":sha,
 "source_records":len(source_rows),
 "high_risk_claim_matrix":"CLAIM_SOURCE_MATRIX.md",
 "legal_evidence_ledger":"LEGAL_EVIDENCE_LEDGER.md",
 "corrections_register":"CORRECTIONS_REGISTER.md",
 "open_evidence_items_preserved":True,
 "file_sha256":file_hashes
}
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
for no in sorted(set([0,1,2,10,pages//4,pages//2,(3*pages)//4,pages-2,pages-1])):
    pix=pdf[no].get_pixmap(matrix=fitz.Matrix(1.25,1.25)); pix.save(str(BASE/f"_flagship_preview_{no+1}.png"))
pdf.close()
print(json.dumps(audit,indent=2))
