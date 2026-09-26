from sage.all import *
from math import gcd as igcd
from functools import reduce
from random import randint, seed as rseed
import sys

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

def recover_p(Y, order, low, k, num=None):
    W=2**low
    d=order
    # window vectors w_i = (Y[i],...,Y[i+d]) * W  (approx of true states, low bits 0)
    m = d+1                      # dim of each vector
    if num is None: num = min(len(Y)-d, 60)
    rows_w = [[Y[i+j]*W for j in range(m)] for i in range(num)]  # num x m
    # Orthogonal lattice: find short u (num-dim) with u . rows_w ~ 0 in every column.
    # Lattice basis: [ I_num | Kcol * rows_w ]  (num x (num+m)). Short vectors: small u and small u.W.
    K = 2**(k+40)   # weight to force u.W ~ 0
    B = matrix(ZZ, num, num+m)
    for i in range(num):
        B[i,i]=1
        for j in range(m):
            B[i, num+j] = K * rows_w[i][j]
    B=B.LLL()
    # For each reduced row, the last m entries = K * (u . column). If ~0 mod p, then u.column = p*something.
    # Recompute u . (true approx W-vectors) exactly (without K) to get multiples of p.
    cand=0
    vals=[]
    for r in B.rows():
        u=[r[i] for i in range(num)]
        if not any(u): continue
        # exact combination in each column
        for j in range(m):
            s=sum(u[i]*rows_w[i][j] for i in range(num))
            vals.append(s)
    g=0
    for v in vals:
        g=igcd(g, abs(int(v)))
    return g, vals[:6]

if __name__=="__main__":
    order=int(sys.argv[1]) if len(sys.argv)>1 else 3
    p,C,A,y=gen_seq(order,48,16,180)
    g,sample=recover_p(y,order,16,48)
    print(f"order={order} p={p}")
    print(f"gcd={g} bits={int(g).bit_length() if g else 0} div_p={(g%p==0) if g else False} g//p={(g//p) if (g and g%p==0) else None}")
