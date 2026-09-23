from pathlib import Path
import requests, json, hashlib, re, datetime
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data/source-sources.json"
OUT=ROOT/"data/source-monitor.json"
LIVE=ROOT/"data/guyana-live.json"
UA={"User-Agent":"RR-Public-Intelligence-Monitor/1.0 (+https://ragunauthramsaroop.com/)"}
now=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
try: previous={x["url"]:x for x in json.loads(OUT.read_text(encoding="utf-8")).get("sources",[])}
except: previous={}
rows=[]
for src in json.loads(REG.read_text(encoding="utf-8")).get("sources",[]):
    row=dict(src); row.update({"checked_at":now,"status":"error","changed":False})
    try:
        r=requests.get(src["url"],timeout=25,headers=UA)
        row["http_status"]=r.status_code
        text=r.text if "text" in r.headers.get("content-type","") or "json" in r.headers.get("content-type","") else ""
        clean=re.sub(r"\s+"," ",BeautifulSoup(text,"html.parser").get_text(" ",strip=True) if text.lstrip().startswith("<") else text)[:120000]
        h=hashlib.sha256(clean.encode("utf-8","ignore")).hexdigest()
        row["sha256"]=h;row["status"]="ok" if r.ok else "http-error";row["changed"]=bool(previous.get(src["url"],{}).get("sha256") and previous[src["url"]].get("sha256")!=h)
        row["content_length"]=len(r.content)
    except Exception as e:
        row["error"]=str(e)[:240]
    rows.append(row)
OUT.write_text(json.dumps({"generated":now,"sources":rows},ensure_ascii=False,indent=2),encoding="utf-8")

# Headline Guyana metrics from official Bureau of Statistics, preserving previous snapshot on parse failure.
try: live=json.loads(LIVE.read_text(encoding="utf-8"))
except: live={"metrics":[]}
try:
    r=requests.get("https://statisticsguyana.gov.gy/",timeout=25,headers=UA);r.raise_for_status()
    text=re.sub(r"\s+"," ",BeautifulSoup(r.text,"html.parser").get_text(" ",strip=True))
    specs=[
      ("Population",r"Population\s+([0-9,]+)\s*\(([^)]+)\)","people"),
      ("Unemployment rate",r"Unemployment Rate\s+([0-9.]+%)\s*\(([^)]+)\)","rate"),
      ("Exports (FOB)",r"Exports \(FOB\)\s+([^\(]+)\s*\(([^)]+)\)","USD"),
      ("Imports (CIF)",r"Imports \(CIF\)\s+([^\(]+)\s*\(([^)]+)\)","USD"),
      ("Real GDP growth",r"Real GDP Growth Rate \(Entire Economy\)\s+([0-9.]+%)\s*\(([^)]+)\)","rate"),
      ("Monthly average exchange mid-rate",r"Monthly Average Exchange Mid-Rate\s+([^\(]+)\s*\(([^)]+)\)","GYD reference"),
      ("Public-sector minimum wage",r"Minimum Wage \(Public Sector\)\s+([^\(]+)\s*\(([^)]+)\)","GYD")
    ]
    metrics=[]
    for label,pat,unit in specs:
        m=re.search(pat,text,re.I)
        if m: metrics.append({"label":label,"value":m.group(1).strip(),"period":m.group(2).strip(),"unit":unit,"source":"https://statisticsguyana.gov.gy/"})
    if metrics: live={"generated":now,"metrics":metrics}
except Exception: pass

# Add latest World Bank public indicators.
for code,label,unit in [
 ("NY.GDP.MKTP.KD.ZG","World Bank GDP growth","%"),
 ("FP.CPI.TOTL.ZG","World Bank inflation","%"),
 ("SP.POP.TOTL","World Bank population","people"),
 ("NY.GDP.MKTP.CD","World Bank GDP","USD")
]:
    try:
        j=requests.get(f"https://api.worldbank.org/v2/country/GUY/indicator/{code}?format=json&per_page=6",timeout=25,headers=UA).json()
        x=next((z for z in (j[1] or []) if z.get("value") is not None),None)
        if x:
            live.setdefault("metrics",[]).append({"label":label,"value":x["value"],"period":x["date"],"unit":unit,"source":"https://data.worldbank.org/country/guyana","indicator":code})
    except Exception: pass
LIVE.write_text(json.dumps(live,ensure_ascii=False,indent=2),encoding="utf-8")

api=ROOT/"api/v1";api.mkdir(parents=True,exist_ok=True)
(api/"sources.json").write_text(OUT.read_text(encoding="utf-8"),encoding="utf-8")
(api/"guyana.json").write_text(LIVE.read_text(encoding="utf-8"),encoding="utf-8")
