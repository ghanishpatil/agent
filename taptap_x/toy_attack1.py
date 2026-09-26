from toy import gen
from math import gcd
import numpy as np
from sympy import Matrix

order=3; trunc=16
p,C,A,Y=gen(order, 48, trunc, 40)
B=2**trunc
g=A[order:]              # generated exact
gt=[y*B for y in Y]      # generated truncated (low bits = 0)
N=len(g)
print("p",p)

def det_int(rows):
    return int(Matrix(rows).det())

# window vectors of length order+1
def windows(seq):
    W=[]
    for j in range(order, len(seq)):
        W.append([seq[j-k] for k in range(order+1)])  # (g_j, g_{j-1},...,g_{j-order})
    return W

# EXACT: det of (order+1) consecutive windows should be 0 mod p
Wex=windows(g)
dets=[]
for i in range(0, len(Wex)-(order+1), 1):
    block=Wex[i:i+order+1]
    d=det_int(block)
    dets.append(d)
gg=0
for d in dets: gg=gcd(gg,d)
print("EXACT gcd of window-block dets:", gg, "== p*?", gg%p==0, "gg//p" , (gg//p if p and gg%p==0 else None))

# TRUNCATED
Wt=windows(gt)
detst=[]
for i in range(0, len(Wt)-(order+1), 1):
    block=Wt[i:i+order+1]
    detst.append(det_int(block))
ggt=0
for d in detst: ggt=gcd(ggt,d)
print("TRUNC gcd:", ggt, "div by p?", ggt%p==0 if ggt else None)
print("first few trunc dets mod p:", [d%p for d in detst[:5]])
