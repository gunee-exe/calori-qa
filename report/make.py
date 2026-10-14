"""Build the .docx, fill the TOC with real page numbers (from a LibreOffice render), and export the PDF."""
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pymupdf

HERE = pathlib.Path(__file__).parent
Q = HERE.parent
DOCX = Q / "Calori_Test_Summary_Report.docx"
PDFDIR = Q / "work" / "pdf"
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
if not pathlib.Path(SOFFICE).exists():
    SOFFICE = shutil.which("soffice") or "soffice"


def build(toc=None):
    args = [sys.executable, str(HERE / "build_report.py")]
    if toc is not None:
        (HERE / "toc.json").write_text(json.dumps(toc, ensure_ascii=False), encoding="utf-8")
        args.append(str(HERE / "toc.json"))
    out = subprocess.run(args, cwd=HERE, capture_output=True, text=True)
    if out.returncode:
        sys.exit(out.stderr)
    print(out.stdout.strip())
    return json.loads((HERE / "headings.json").read_text(encoding="utf-8"))


def to_pdf():
    PDFDIR.mkdir(parents=True, exist_ok=True)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(PDFDIR), str(DOCX)],
                   capture_output=True, text=True, check=True)
    return PDFDIR / (DOCX.stem + ".pdf")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def pages_for(pdf, headings):
    doc = pymupdf.open(pdf)
    texts = [norm(p.get_text()) for p in doc]
    toc_pages = {i for i, t in enumerate(texts) if re.search(r"\.{12,}", t)}
    start = max(toc_pages) + 1 if toc_pages else 0
    result, cur = [], start
    for level, h in headings:
        hn = norm(h)
        found = next((i for i in range(cur, len(texts)) if hn in texts[i]), None)
        if found is None:
            print("NOT FOUND:", h)
            found = cur
        cur = found
        result.append([level, h, str(found + 1)])
    return result, doc.page_count


if __name__ == "__main__":
    heads = build()
    toc = [[lvl, h, "0"] for lvl, h in heads]
    for attempt in range(3):
        build(toc)
        pdf = to_pdf()
        new, n = pages_for(pdf, heads)
        print(f"pass {attempt + 1}: {n} pages")
        if new == toc:
            break
        toc = new
    build(toc)
    pdf = to_pdf()
    check, n = pages_for(pdf, heads)
    print("final pages:", n, "| TOC consistent:", check == toc)
    shutil.copy(pdf, Q / "Calori_Test_Summary_Report.pdf")
