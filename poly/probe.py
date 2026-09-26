import requests
s = requests.Session()
base = "https://polynomial.secso.cc"
for path in ["", "/", "/robots.txt", "/source", "/app.py", "/static/app.py"]:
    try:
        r = s.get(base + path, timeout=20)
        print("== GET", path or "/", "->", r.status_code, "len", len(r.text))
        print(r.text[:1500])
        print("-- headers:", dict(r.headers))
        print("=" * 70)
    except Exception as e:
        print(path, "ERR", repr(e))
