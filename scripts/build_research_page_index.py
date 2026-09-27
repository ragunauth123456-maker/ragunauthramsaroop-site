"""Generate an auditable, per-page public PDF text index. No OCR or inferred page numbers."""
from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"data/research-papers.json"
OUTPUT=ROOT/"data/research-pages.json"
MAX_PDF_BYTES=35_000_000
MAX_PAGES=170
MAX_CHARS_PER_PAGE=1800

def normalize(text):
    return re.sub(r"\s+"," ",text or "").strip()

def build():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    output={"generated_at":datetime.now(timezone.utc).isoformat(),"generator":"pypdf text extraction from public PDFs; no OCR","papers":[],"excluded":[]}
    for item in manifest["papers"]:
        slug=item["slug"]
        pdf=ROOT/item["pdf"].lstrip("/")
        if not pdf.is_file():
            output["excluded"].append({"slug":slug,"reason":"PDF missing"})
            continue
        size=pdf.stat().st_size
        if size>MAX_PDF_BYTES:
            output["excluded"].append({"slug":slug,"reason":"PDF exceeds indexing budget","bytes":size})
            continue
        try:
            reader=PdfReader(str(pdf),strict=False)
            pages=[]
            for pageno,page in enumerate(reader.pages[:MAX_PAGES],start=1):
                raw=page.extract_text() or ""
                text=normalize(raw)
                if len(text)>=40:
                    pages.append({"page":pageno,"text":text[:MAX_CHARS_PER_PAGE]})
            result={"slug":slug,"title":item["title"],"pdf":item["pdf"],
                    "file_sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),
                    "page_count":len(reader.pages),"indexed_pages":len(pages),
                    "pages":pages}
            output["papers"].append(result)
            if not pages:
                output["excluded"].append({"slug":slug,"reason":"No extractable text. Manual reading or OCR required."})
        except Exception as ex:
            output["excluded"].append({"slug":slug,"reason":type(ex).__name__+" during PDF parsing"})
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(output,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print("PAPERS",len(output["papers"]),"INDEXED_PAGES",sum(len(x["pages"]) for x in output["papers"]),
          "EXCLUSIONS",len(output["excluded"]),"OUTPUT_BYTES",OUTPUT.stat().st_size)
    if not output["papers"]:
        raise SystemExit("No public PDF could be indexed; do not publish an empty replacement.")

if __name__=="__main__":
    build()
