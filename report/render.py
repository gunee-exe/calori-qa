"""render.py PDF OUTPREFIX [per_sheet]: contact sheets of PDF pages for layout review."""
import sys, pymupdf
from PIL import Image
pdf, prefix = sys.argv[1], sys.argv[2]
per = int(sys.argv[3]) if len(sys.argv) > 3 else 6
doc = pymupdf.open(pdf)
pages = []
for p in doc:
    pix = p.get_pixmap(dpi=55)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    pages.append(im)
cols = 3
for s in range(0, len(pages), per):
    chunk = pages[s:s + per]
    w = max(i.width for i in chunk); h = max(i.height for i in chunk)
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8), rows * (h + 8)), (120, 120, 120))
    for k, im in enumerate(chunk):
        sheet.paste(im, ((k % cols) * (w + 8), (k // cols) * (h + 8)))
    sheet.save(f"{prefix}_{s // per + 1:02d}.jpg", quality=72)
print(len(pages), "pages")
