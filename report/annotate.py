"""Draw highlight boxes on each defect's primary screenshot -> report/annotated/DEF-xx.jpg,
and make report-sized copies of other evidence -> report/small/<name>.jpg."""
import pathlib
from PIL import Image, ImageDraw, ImageFont

import defects as D

Q = pathlib.Path("H:/flutter_apps/calori-qa")
OUT = Q / "report" / "annotated"
SMALL = Q / "report" / "small"
OUT.mkdir(exist_ok=True)
SMALL.mkdir(exist_ok=True)
RED = (220, 38, 38)
FONT = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
WIDTH = 600  # report copies: legible at ~6 cm, small enough to keep the .docx light


def small(name):
    src = Q / "evidence" / f"{name}.png"
    dst = SMALL / f"{name}.jpg"
    if not dst.exists():
        im = Image.open(src).convert("RGB")
        im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS).save(dst, quality=86)
    return dst


def label(draw, xy, text, img_w):
    x, y = xy
    tw = draw.textlength(text, font=FONT)
    x = max(8, min(x, img_w - tw - 24))
    draw.rounded_rectangle([x, y, x + tw + 20, y + 48], radius=10, fill=RED)
    draw.text((x + 10, y + 5), text, font=FONT, fill="white")


def annotate(defect):
    name = defect["evidence"][0]
    im = Image.open(Q / "evidence" / f"{name}.png").convert("RGB")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for (x1, y1, x2, y2), _ in defect["boxes"]:
        od.rectangle([x1, y1, x2, y2], fill=(220, 38, 38, 28))
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    dr = ImageDraw.Draw(im)
    for (x1, y1, x2, y2), text in defect["boxes"]:
        dr.rectangle([x1, y1, x2, y2], outline=RED, width=9)
        if text:
            below = text.startswith("v:")
            text = text[2:] if below else text
            ly = y2 + 10 if below or y1 <= 70 else y1 - 58
            if ly + 48 > im.height:
                ly = y1 + 10
            label(dr, (x1, ly), text, im.width)
    out = OUT / f"{defect['id']}.jpg"
    im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS).save(out, quality=86)
    return out


if __name__ == "__main__":
    for dfx in D.DEFECTS:
        annotate(dfx)
        for ev in dfx["evidence"][1:]:
            if not ev.endswith(".mp4"):
                small(ev)
    print(len(list(OUT.glob("*.jpg"))), "annotated;", len(list(SMALL.glob("*.jpg"))), "small copies")
