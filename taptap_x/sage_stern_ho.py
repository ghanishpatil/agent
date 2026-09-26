from sage.all import *
from itertools import combinations
from math import ceil, sqrt, gcd as igcd
from random import randint, seed as rseed
def isPrime(x): return is_prime(x)

R = ZZ["x"]; X = R.gen()

def lll(B): return B.LLL()

# Generalized generator: lattice with the RAW outputs (window of width w = deg+1) plus identity.
# For a recurrence of order d, connection poly degree d. Use 'w' = number of poly coeffs.
# B: rows i=0..n-1 ; cols: first t are "equation" cols using outputs, last n are identity.
# Try two variants: differences vs raw.
def gen_polys(y, n, t, order, mode="diff"):
    B = matrix(ZZ, n, n + t)
    for i in range(n):
        for j in range(t):
            if mode=="diff":
                B[i,j] = y[i+j+1]-y[i+j]
            else:
                B[i,j] = y[i+j]
        B[i, t+i] = 1
    B = B.LLL()
    ps=[]
    for r in B.rows():
        P=R(list(r[t:]))
        if P!=0: ps.append(P)
    return ps

def try_recover(y, k, order, checkbits):
    for mode in ["diff","raw"]:
        for n in range(order+2, order+30):
            for t in range(1, 20):
                if n+t+1 > len(y): break
                try: polys=gen_polys(y, n, t, order, mode)
                except Exception: continue
                # gcd of resultants over triples of the SMALLEST polys
                polys=[P for P in polys if P.degree()>=1][:8]
                found=None
                for comb in combinations(polys,3):
                    P0,P1,P2=comb
                    try:
                        m_=igcd(igcd(int(P0.resultant(P1)),int(P1.resultant(P2))),int(P0.resultant(P2)))
                    except Exception: continue
                    if m_>1 and abs(int(m_).bit_length()-k)<=2:
                        found=m_; break
                if found:
                    return mode,n,t,found
    return None

def gen_seq(order,k,low,cnt,sd=1234):
    rseed(sd)
    p=2**k - randint(2**(k//3),2**(k//3+2))
    while not isPrime(p): p-=1
    C=[randint(1,p) for _ in range(order)]
    A=[randint(1,p) for _ in range(order)]
    for _ in range(cnt):
        A.append(sum(ci*ai for ci,ai in zip(C[::-1],A[::-1]))%p)
    y=[ai>>low for ai in A[order:]]
    return p,C,A,y

for order in [2,3]:
    p,C,A,y=gen_seq(order,48,16,150)
    res=try_recover(y,48,order,2)
    print(f"order={order} true_p={p} -> ", end="")
    if res:
        mode,n,t,m_=res
        print(f"recovered p? {m_==p}  (mode={mode},n={n},t={t}, m={m_})")
    else:
        print("NOT recovered")
