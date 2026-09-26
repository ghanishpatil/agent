
from fpylll import IntegerMatrix, LLL
from math import gcd
from sympy import symbols, resultant, Poly, ZZ as sZZ
from itertools import combinations
from toy import gen

x=symbols('x')
def lll_rows(rows):
    n=len(rows); m=len(rows[0]); A=IntegerMatrix(n,m)
    for i in range(n):
        for j in range(m): A[i,j]=int(rows[i][j])
    LLL.reduction(A)
    return [[A[i,j] for j in range(m)] for i in range(n)]

def gen_polys(y,n,t):
    rows=[]
    for i in range(n):
        row=[0]*(n+t)
        for j in range(t): row[j]=y[i+j+1]-y[i+j]
        row[t+i]=1
        rows.append(row)
    red=lll_rows(rows)
    ps=[]
    for v in red:
        P=sum(int(c)*x**i for i,c in enumerate(v[t:]))
        if P!=0: ps.append(Poly(P,x,domain=sZZ))
    return ps

ORD=3; LOW=16; K=48
p,C,A,Y=gen(ORD,K,LOW,150)
print("true p",p, "factor-ish bits", p.bit_length())
# char poly: x^3 - c3 x^2 - c2 x - c1 (mod p) with c1=C[0],c2=C[1],c3=C[2]
print("true char poly coeffs [const..x^3]:", [(-C[0])%p, (-C[1])%p, (-C[2])%p, 1])

for (n,t) in [(4,2),(4,3),(5,3),(6,3),(5,4),(6,4),(8,4),(8,6),(10,6),(12,8)]:
    if n+t+1>len(Y): continue
    ps=gen_polys(Y[:n+t+1],n,t)
    degs=[P.degree() for P in ps]
    cp=[P for P in ps if 1<=P.degree()<=ORD]
    # resultant gcd over pairs
    g=0; rr=[]
    for P0,P1 in combinations(cp,2):
        try: r=abs(int(resultant(P0.as_expr(),P1.as_expr(),x)))
        except: continue
        if r: rr.append(r); g=gcd(g,r) if g else r
    info=""
    if g:
        info=f"gcd_bits={g.bit_length()} div_p={g%p==0}"
        # also check gcd//p small
    print(f"n={n} t={t} degs={degs} #cp={len(cp)} {info}")
