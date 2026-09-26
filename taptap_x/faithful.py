from sage.all import *
from itertools import combinations
from math import ceil, sqrt, gcd as igcd
from random import randint, seed as rseed
import sys

R=ZZ["x"]; X=R.gen()

def generate_polynomials(y, n, t):
    B=matrix(ZZ,n,n+t)
    for i in range(n):
        for j in range(t):
            B[i,j]=y[i+j+1]-y[i+j]
        B[i,t+i]=1
    B=B.LLL()
    for r in B.rows():
        P=R(list(r[t:]))
        if P!=0: yield P

def recover_modulus(y,k,s,check,tmax=12):
    alpha=s/k; t=max(1,int(1/alpha)); n=ceil(sqrt(2*alpha*t*k))
    while t<=tmax:
        chunk=n+t
        if chunk>len(y):
            t+=1; n=ceil(sqrt(2*alpha*t*k)); continue
        polys=[]
        for i in range(len(y)//chunk):
            polys+=list(generate_polynomials(y[chunk*i:chunk*(i+1)],n,t))
        for comb in combinations(polys,3):
            P0,P1,P2=comb
            try:
                m_=igcd(igcd(int(P0.resultant(P1)),int(P1.resultant(P2))),int(P0.resultant(P2)))
            except Exception: continue
            if m_>1 and check(m_):
                return m_,(n,t)
        t+=1; n=ceil(sqrt(2*alpha*t*k))
    return None,None

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

order=int(sys.argv[1]) if len(sys.argv)>1 else 2
K=48; LOW=16; s=K-LOW
p,C,A,y=gen_seq(order,K,LOW,180)
m_,par=recover_modulus(y,K,s,lambda mm:abs(int(mm).bit_length()-K)<=1)
print(f"order={order} p={p} recovered={m_} par={par} HIT={m_==p}")
