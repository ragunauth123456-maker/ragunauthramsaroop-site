from pathlib import Path
import json
p=Path("assets/search-index.json")
j=json.loads(p.read_text(encoding="utf-8"))
for d in j.get("documents",[]):
    d["text"]=str(d.get("text",""))[:1500]
p.write_text(json.dumps(j,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print("SEARCH_PAYLOAD",p.stat().st_size)
