from sage.all import *
from itertools import combinations
from math import gcd as igcd
from random import randint, seed as rseed

R=ZZ["x"]; X=R.gen()

def gen_seq(order,k,low,cnt,sd=1234):
    rseed(sd)
    p=2**k - randint(2**(k//3),2**(k//3+2))
    while not is_prime(p): p-=1
    C=[randint(1,p) for _ in range(order)]
    A=[randint(1,p) for _ in range(order)]
    for _ in range(cnt):
        A.append(sum(ci*ai for ci,ai in zip(C[::-1],A[::-1]))%p)
    y=[ai>>low for ai in A[order:]]
    return p,C,A,y

# Build lattice: poly degree D (D+1 coeffs). For shifts j=0..t-1 constraint sum_i v_i * y_{j+i} ~ 0.
# Columns: [ scale*y-equations (t cols) | identity (D+1 cols) ].  Rows = D+1.
def gen_polys(y, D, t, scale):
    n=D+1
    B=matrix(ZZ, n, t+n)
    for i in range(n):       # coeff index i (row) 
        for j in range(t):   # shift j
            B[i,j] = scale*y[j+i]
        B[i, t+i]=1
    B=B.LLL()
    ps=[]
    for r in B.rows():
        P=R(list(r[t:]))
        if P!=0: ps.append(P)
    return ps

def scan(y,k,order):
    for D in range(order, order+3):
        for t in range(order+2, order+40):
            if t+D+1>len(y): break
            for sbits in [1,8,16,24,32,40,48]:
                scale=1<<sbits
                try: polys=gen_polys(y,D,t,scale)
                except Exception: continue
                polys=[P for P in polys if P.degree()>=1]
                for comb in combinations(polys[:6],3):
                    P0,P1,P2=comb
                    try:
                        m_=igcd(igcd(int(P0.resultant(P1)),int(P1.resultant(P2))),int(P0.resultant(P2)))
                    except Exception: continue
                    if m_>1 and abs(int(m_).bit_length()-k)<=2:
                        return (D,t,sbits,m_)
    return None

for order in [1,2,3]:
    p,C,A,y=gen_seq(order,48,16,180)
    r=scan(y,48,order)
    print(f"order={order} p={p} => {r} hit={r is not None and r[3]==p}")
