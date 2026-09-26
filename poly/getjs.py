import requests
base = "https://polynomial.secso.cc"
r = requests.get(base + "/assets/index-0OGNtCbS.js", timeout=30)
print("status", r.status_code, "len", len(r.text))
open("/work/bundle.js","w",encoding="utf-8").write(r.text)
t = r.text
# find interesting API-ish strings
import re
for kw in ["/api", "fetch(", "axios", "evaluate", "polynomial", "admin", "flag", "format", "report", "POST", "coeff"]:
    idxs = [m.start() for m in re.finditer(re.escape(kw), t)]
    print(f"\n### {kw!r} ({len(idxs)} hits)")
    for i in idxs[:8]:
        print(repr(t[max(0,i-80):i+120]))
