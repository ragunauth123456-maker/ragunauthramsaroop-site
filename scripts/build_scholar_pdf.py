#!/usr/bin/env python3
"""Create an under-5-MB Scholar derivative without modifying the approved original.

The original PDF remains at /research-papers/guyana-power-demand-2030.pdf.
One large RGB figure is re-encoded as a 256-colour PDF indexed image.
This is visually near-identical, not pixel-lossless; every PDF page is rendered
and checked before the scholarly copy is replaced.
Requires pypdf, Pillow and PyMuPDF.
"""
from pathlib import Path
import hashlib, json, time, zlib
import pymupdf
from PIL import Image, ImageChops, ImageStat
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, ArrayObject, ByteStringObject

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research-papers/guyana-power-demand-2030.pdf"
TARGET = ROOT / "research-library/guyana-power-demand-2030/full-text.pdf"
AUDIT = TARGET.parent / "optimization-audit.json"
EXPECTED_SHA256 = "27f864c0c5118d209b3b4ae9e04850d7ae3e409c957a8bf926e64ad67d7806ad"
MAX_BYTES = 5_000_000

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def render_error(before, after):
    p = before.get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False)
    q = after.get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False)
    assert (p.width,p.height)==(q.width,q.height)
    a = Image.frombytes("RGB", (p.width,p.height), p.samples)
    b = Image.frombytes("RGB", (q.width,q.height), q.samples)
    st = ImageStat.Stat(ImageChops.difference(a, b))
    return (max(st.mean), max(st.rms))

def main():
    assert SOURCE.is_file() and sha(SOURCE) == EXPECTED_SHA256, "Approved master PDF changed"
    assert TARGET.is_file(), "Expected existing scholarly copy not found"
    original_sha = sha(SOURCE)
    reader = PdfReader(str(SOURCE))
    writer = PdfWriter(clone_from=reader)
    writer.pdf_header = "%PDF-1.7"
    img = writer.pages[0]["/Resources"]["/XObject"].get_object()["/Im13"].get_object()
    assert (int(img["/Width"]), int(img["/Height"])) == (8478,4353)
    assert img["/Filter"] == "/FlateDecode" and img["/ColorSpace"] == "/DeviceRGB"
    assert "/SMask" in img, "Preserve original soft mask"
    pixels = Image.frombytes("RGB", (8478,4353), zlib.decompress(img._data))
    indexed = pixels.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                              dither=Image.Dither.NONE)
    palette = bytes(indexed.getpalette()[:768])
    assert len(palette) == 768
    img._data = zlib.compress(indexed.tobytes(), level=9)
    img[NameObject("/Filter")] = NameObject("/FlateDecode")
    img[NameObject("/ColorSpace")] = ArrayObject(
        [NameObject("/Indexed"), NameObject("/DeviceRGB"),
         NumberObject(255), ByteStringObject(palette)])
    img[NameObject("/BitsPerComponent")] = NumberObject(8)
    writer.add_metadata({
        "/Title": "Guyana Power Demand 2030",
        "/Author": "Ragunauth Ramsaroop",
        "/Subject": "Independent research white paper",
        "/Keywords": "Guyana, electricity demand, power generation, energy security, 2030"
    })
    temp = TARGET.with_name("full-text.scholar-build.pdf")
    try:
        with temp.open("wb") as handle:
            writer.write(handle)
        assert 50_000 < temp.stat().st_size < MAX_BYTES, "PDF exceeds Scholar's 5 MB limit"
        source_doc, candidate = pymupdf.open(SOURCE), pymupdf.open(temp)
        prior = pymupdf.open(TARGET)
        assert len(source_doc) == len(candidate) == len(prior) == 22
        assert candidate.metadata["title"] == "Guyana Power Demand 2030"
        assert candidate.metadata["author"] == "Ragunauth Ramsaroop"
        results = []
        for ix in range(22):
            assert source_doc[ix].get_text() == candidate[ix].get_text()
            assert prior[ix].get_text() == candidate[ix].get_text()
            assert source_doc[ix].get_links() == candidate[ix].get_links()
            assert source_doc[ix].rect == candidate[ix].rect
            results.append(render_error(source_doc[ix], candidate[ix]))
        assert source_doc.get_toc() == candidate.get_toc()
        assert max(x[0] for x in results) < 1.5, "Figure colour change exceeded mean threshold"
        assert max(x[1] for x in results) < 7.0, "Figure colour change exceeded RMS threshold"
        candidate.close();source_doc.close();prior.close()
        assert sha(SOURCE) == original_sha, "Master copy changed unexpectedly"
        temp.replace(TARGET)
        audit = {
            "checked_at": "2026-09-26", "paper": "Guyana Power Demand 2030",
            "original_pdf_url": "https://ragunauthramsaroop.com/research-papers/guyana-power-demand-2030.pdf",
            "scholar_pdf_url": "https://ragunauthramsaroop.com/research-library/guyana-power-demand-2030/full-text.pdf",
            "approved_original_sha256": original_sha,
            "optimized_sha256": sha(TARGET),
            "original_bytes": SOURCE.stat().st_size,
            "optimized_bytes": TARGET.stat().st_size,
            "scholar_size_limit_bytes": MAX_BYTES,
            "original_pdf_untouched": sha(SOURCE) == original_sha,
            "pages": 22, "all_page_text_exact": True,
            "all_page_links_exact": True,
            "page_dimensions_and_toc_exact": True,
            "render_max_mean_difference": round(max(x[0] for x in results),4),
            "render_max_rms_difference": round(max(x[1] for x in results),4),
            "method": "Pypdf: one 8478x4353 RGB figure re-encoded as an indexed 256-colour image with its original alpha mask unchanged; slight colour quantization; full-resolution approved original separately retained.",
            "google_scholar_indexing": "not independently verified"
        }
        AUDIT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("SCHOLAR_PDF_OPTIMIZED",json.dumps(audit,ensure_ascii=False),flush=True)
    finally:
        if temp.exists(): temp.unlink()

if __name__ == "__main__":
    main()
