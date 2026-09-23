from pathlib import Path
from html.parser import HTMLParser
import json,sys
ROOT=Path(__file__).resolve().parents[1];TOOLS=ROOT/"tools";issues=[]
catalog=json.loads((ROOT/"api/v1/catalog.json").read_text(encoding="utf-8"))
if len(catalog.get("tools",[]))!=26:issues.append("catalog must contain 26 tools")
for t in catalog.get("tools",[]):
 p=ROOT/t["url"].lstrip("/")/"index.html" if not t["url"].endswith("/") else ROOT/t["url"].lstrip("/")/"index.html"
 if not p.exists():issues.append("missing "+t["url"]);continue
 s=p.read_text(encoding="utf-8",errors="replace")
 for needle in ("/tools/assets/tool-enhancements.js","/tools/assets/tool-pro.js","/tools/assets/report-export.js","WebApplication","Methodology"):
  if needle not in s:issues.append(f"{t['url']} missing {needle}")
for rel in ("tools/assets/tool-pro.js","tools/assets/tool-enhancements.js","tools/assets/report-export.js","data/tool-method-details.json","service-worker.js","embed/index.html","scenario-lab/index.html","my-toolkit/index.html"):
 if not (ROOT/rel).exists():issues.append("missing "+rel)
methods=json.loads((ROOT/"data/tool-method-details.json").read_text(encoding="utf-8"))
for t in catalog.get("tools",[]):
 slug=t["url"].strip("/").split("/")[-1]
 if slug not in methods:issues.append("method detail missing "+slug)
print("TOOLS",len(catalog.get("tools",[])));print("ISSUES",len(issues))
for x in issues:print("FAIL",x)
sys.exit(1 if issues else 0)
