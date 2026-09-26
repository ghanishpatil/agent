from sage.all import *
from math import gcd as igcd
from random import randint, seed as rseed
import sys

# Recover p for order-d truncated recurrence via orthogonal-lattice on window vectors,
# breaking trivial Q-dependence by treating each window as an independent HNP sample:
#   true w_i = (A_i,...,A_{i+d})  satisfies  w_i . kappa = 0 mod p.
#   We know highs Y_i = A_i>>low. Unknown low e_i in [0,W).
# Kannan embedding: find kappa mod p directly is HNP with d unknowns -> hard.
#
# Alternative CORRECT method: recover p using consecutive (d+1)x(d+1) Hankel determinants of the
# EXACT sequence = 0 mod p. Denoise: the (d+1)x(d+2) Hankel window has a right-kernel vector over Q
# (since d+2 > d+1... no). Use LLL to recover the exact low bits via the relation that the
# (d+2) consecutive states are linearly dependent mod p with SMALL integer combo? No, combo=char poly (large).
#
# Let's just do the thing that provably works: EXACT gcd of Hankel dets = p. So we only need to
# denoise ~ (2d+2) consecutive states. Do that with a lattice where unknowns are those low bits and
# we require the (d+1)x(d+1) determinant to vanish mod p -- but p unknown.
#
# FINAL approach that works and is standard: recover kappa OVER THE INTEGERS by noting the truncated
# sequence, scaled, approximately satisfies the recurrence; use LLL to find the integer relation with
# the SMALLEST residual across many windows. The relation vector is (kappa mod p) reduced -> but we can
# instead find MANY independent small "residual" polynomials via a big lattice and gcd their resultants.
#
# Implement generalized-Stern with a WIDER lattice (Contini-Shparlinski higher-order):
#   Build matrix with rows = windows of the sequence-of-differences of order chosen so degree matches.
# We brute the # of difference passes AND (n,t), and accept when gcd is a ~k-bit number (=p).

R=ZZ["x"]; X=R.gen()

def diffs(seq, times):
    s=list(seq)
    for _ in range(times):
        s=[s[i+1]-s[i] for i in range(len(s)-1)]
    return s

def gen_polys(seq,n,t):
    B=matrix(ZZ,n,n+t)
    for i in range(n):
        for j in range(t): B[i,j]=seq[i+j+1]-seq[i+j]
        B[i,t+i]=1
    B=B.LLL()
    out=[]
    for r in B.rows():
        P=R(list(r[t:]))
        if P!=0: out.append(P)
    return out

def recover(y,k,order):
    from itertools import combinations
    best=[]
    for dp in range(0, order+1):
        seq=diffs(y,dp)
        for n in range(order+2, 20):
            for t in range(1, 16):
                if n+t+1>len(seq): continue
                try: polys=gen_polys(seq[:n+t+1],n,t)
                except Exception: continue
                cp=[P for P in polys if P.degree()>=1][:6]
                for comb in combinations(cp,3):
                    P0,P1,P2=comb
                    try:
                        m_=igcd(igcd(int(P0.resultant(P1)),int(P1.resultant(P2))),int(P0.resultant(P2)))
                    except Exception: continue
                    if m_>1:
                        b=int(m_).bit_length()
                        if abs(b-k)<=1:
                            return (dp,n,t,m_)
    return None

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
p,C,A,y=gen_seq(order,48,16,180)
r=recover(y,48,order)
print(f"order={order} p={p} -> {r}", "HIT" if (r and r[3]==p) else "MISS")
