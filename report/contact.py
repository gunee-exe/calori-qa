"""contact.py OUT name1 name2 ... : grid-overlaid contact sheet (full-res coords every 200 px)."""
import sys
from PIL import Image, ImageDraw
Q = "H:/flutter_apps/calori-qa"
out, names = sys.argv[1], sys.argv[2:]
W, H = 360, 808  # 1/3 scale
sheet = Image.new("RGB", (W * len(names) + 8 * (len(names) - 1), H + 22), "white")
d = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    im = Image.open(f"{Q}/evidence/{n}.png").convert("RGB").resize((W, H))
    g = ImageDraw.Draw(im)
    for y in range(200, 2424, 200):
        g.line([(0, y / 3), (W, y / 3)], fill=(255, 0, 255), width=1)
        g.text((2, y / 3 - 11), str(y), fill=(255, 0, 255))
    for x in (200, 400, 600, 800, 1000):
        g.line([(x / 3, 0), (x / 3, H)], fill=(0, 200, 255), width=1)
    x0 = i * (W + 8)
    sheet.paste(im, (x0, 22))
    d.text((x0 + 2, 4), n[:52], fill="black")
sheet.save(f"{Q}/work/view/{out}.jpg", quality=80)
