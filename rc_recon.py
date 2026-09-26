import requests
base="https://reverse-captcha.unswsecsoc.workers.dev"
s=requests.Session()
for path in ["/","/robots.txt","/flag","/captcha","/api","/challenge"]:
    try:
        r=s.get(base+path, timeout=20)
        print(f"=== GET {path} -> {r.status_code} ({len(r.text)} bytes) ct={r.headers.get('content-type')}")
        print(r.text[:1500])
        print("--- headers ---", dict(r.headers))
        print()
    except Exception as e:
        print(f"GET {path} error {e!r}")
