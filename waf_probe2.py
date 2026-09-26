import requests
b="https://56773-a245e895397d415a9c9e494df6c22a7b.sbx.secso.cc"
def post(desc):
    base={"title":"h","author":"b","description":desc,"reference":"http://e.com"}
    r=requests.post(b+"/category/tech/new", data=base, timeout=20, allow_redirects=False)
    return "OK" if r.status_code==302 else "BLOCK"
tests=[
 # newline handler on various tags
 "<a on\nclick=alert>x</a>",
 "<a\non\nclick=x>",
 "<svg\non\nload=x>",              # svg blocked anyway
 "<img\non\nerror=x>",            # img blocked anyway
 "<a href=x on\nclick=y>",
 # is 'alert' the only blocked, or generic? we can use other funcs
 "print",
 "confirm",
 "prompt",
 "top",
 "self",
 "globalThis",
 "this",
 "parent",
 "name",
 "eval",
 "Function",
 "constructor",
 "import",
 "fetch",
 "XMLHttpRequest",
 "navigator",
 "atob",
 "setTimeout",
 "String",
 "location",
 "href",
 "innerHTML",
 "write",
 # parens alternatives
 "`",
 "${",
 "&lpar;",
 "&rpar;",
 "&#x28;",
 "&#40;",
 # protocol variants
 "vbscript",
 "data",
 "&colon;",
 "&#58;",
 "&#x3a;",
]
for t in tests:
    print(post(t).ljust(6), repr(t))
