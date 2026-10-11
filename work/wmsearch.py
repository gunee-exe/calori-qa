import json, sys, urllib.request, urllib.parse
UA = {"User-Agent": "CaloriQA/1.0 (university test project)"}
def api(params):
    params = dict(params, format="json")
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
for q in sys.argv[1:]:
    # Commons is the shared file repo, so enwiki's API resolves Commons files too;
    # search runs against enwiki's File namespace mirror via generator=search on commons isn't possible,
    # so use the foreign search: list=search on enwiki ns 6 covers only local files. Use Commons via api.wikimedia? fallback below.
    r = api({"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6,
             "gsrlimit": 5, "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 1024})
    print("==", q)
    for p in (r.get("query", {}).get("pages", {}) or {}).values():
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        print("  ", p["title"], "|", m.get("LicenseShortName", {}).get("value"), "|", ii.get("thumburl"))
