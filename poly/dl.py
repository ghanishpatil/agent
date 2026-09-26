import requests, os
base = "https://polynomial.secso.cc"
os.makedirs("/work/site/assets", exist_ok=True)
files = {
  "/": "/work/site/index.html",
  "/assets/index-0OGNtCbS.js": "/work/site/assets/index-0OGNtCbS.js",
  "/assets/index-C55u8Rdf.css": "/work/site/assets/index-C55u8Rdf.css",
}
for url, path in files.items():
    r = requests.get(base+url, timeout=30)
    open(path, "w", encoding="utf-8").write(r.text)
    print(url, "->", r.status_code, len(r.text), "saved", path)
