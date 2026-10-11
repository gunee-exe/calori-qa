import json, re, sys, urllib.request, urllib.parse, pathlib
UA = {"User-Agent": "CaloriQA/1.0 (university test project)"}
out = pathlib.Path(sys.argv[1])
picks = {
  "biryani": "File:Hyderabad biryani & naan.jpg",
  "egg_breakfast": "File:Liat Portal for Foodie Disorder - Israeli breakfast plate with fried egg and avocado.jpg",
  "salad": "File:Garden salad - San Francisco.jpg",
  "dal_rice_chapati": "File:Bhendi chapati and dal rice.jpg",
  "apple": "File:Red Apple.jpg",
  "chapati": "File:Chapati-1.jpg",
  "cat_nonfood": "File:Cute gray cat sitting in bed.jpg",
}
q = {"action": "query", "titles": "|".join(picks.values()), "prop": "imageinfo",
     "iiprop": "url|extmetadata", "iiurlwidth": 1280, "format": "json"}
r = json.load(urllib.request.urlopen(urllib.request.Request(
    "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(q), headers=UA), timeout=30))
by_title = {p["title"]: p for p in r["query"]["pages"].values()}
manifest = []
for name, title in picks.items():
    p = by_title[title]; ii = p["imageinfo"][0]; m = ii["extmetadata"]
    url = ii.get("thumburl") or ii["url"]
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
    f = out / f"{name}.jpg"; f.write_bytes(data)
    artist = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()
    manifest.append({"file": f.name, "title": title, "licence": m.get("LicenseShortName", {}).get("value"),
                     "author": artist, "page": ii["descriptionurl"], "bytes": len(data)})
    print(f"{f.name:24} {len(data):>8} B  {manifest[-1]['licence']:14} {artist[:40]}")
(out / "SOURCES.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
