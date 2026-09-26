import requests
base = "https://polynomial.secso.cc"
s = requests.Session()

# Report endpoint behavior
r = s.post(base + "/report", data={"url": "/?x=1&y=2&format=standard&autoEval=1"},
           allow_redirects=False, timeout=25)
print("POST /report ->", r.status_code)
print("headers:", dict(r.headers))
print("body:", r.text[:1000])
print("cookies:", s.cookies.get_dict())
print("=" * 60)

# Try JSON body too
import json
r2 = s.post(base + "/report", json={"url": "/?format=standard"},
            allow_redirects=False, timeout=25)
print("POST /report (json) ->", r2.status_code, r2.text[:400])
print("=" * 60)

for p in ["/flag", "/admin", "/bot", "/report", "/api/report", "/health"]:
    try:
        rr = s.get(base + p, timeout=15, allow_redirects=False)
        print("GET", p, "->", rr.status_code, "len", len(rr.text), rr.headers.get("content-type"))
    except Exception as e:
        print("GET", p, "ERR", e)
