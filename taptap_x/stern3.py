
from fpylll import IntegerMatrix, LLL
from math import gcd, ceil, sqrt
from sympy import symbols, resultant, Poly, ZZ as sZZ
from itertools import combinations

x=symbols('x')

def lll_rows(rows):
    n=len(rows); m=len(rows[0])
    A=IntegerMatrix(n,m)
    for i in range(n):
        for j in range(m):
            A[i,j]=int(rows[i][j])
    LLL.reduction(A)
    return [[A[i,j] for j in range(m)] for i in range(n)]

def generate_polynomials(y, n, t):
    # faithful port: B is n x (n+t); B[i][j]=y[i+j+1]-y[i+j] for j<t ; B[i][t+i]=1
    rows=[]
    for i in range(n):
        row=[0]*(n+t)
        for j in range(t):
            row[j]=y[i+j+1]-y[i+j]
        row[t+i]=1
        rows.append(row)
    red=lll_rows(rows)
    polys=[]
    for v in red:
        coeffs=v[t:]
        P=sum(int(c)*x**i for i,c in enumerate(coeffs))
        if P!=0:
            polys.append(Poly(P,x,domain=sZZ))
    return polys

def try_recover(Y, ORD, K):
    # scan n,t
    for n in range(ORD+1, ORD+18):
        for t in range(1, 14):
            if n+t+1 > len(Y): continue
            try:
                polys=generate_polynomials(Y[:n+t+1], n, t)
            except Exception as e:
                continue
            # gcd of resultants of triples
            cp=[P for P in polys if P.degree()>=1]
            g=0
            for comb in combinations(cp, 3):
                P0,P1,P2=comb
                try:
                    r=gcd(gcd(abs(int(resultant(P0.as_expr(),P1.as_expr(),x))),
                              abs(int(resultant(P1.as_expr(),P2.as_expr(),x)))),
                              abs(int(resultant(P0.as_expr(),P2.as_expr(),x))))
                except Exception:
                    continue
                if r>1:
                    g=gcd(g,r) if g else r
            yield (n,t,g)

if __name__=="__main__":
    from toy import gen
    ORD=3; LOW=16; K=48
    p,C,A,Y=gen(ORD,K,LOW,150)
    print("true p", p)
    found=False
    for n,t,g in try_recover(Y,ORD,K):
        if g and g%p==0:
            print(f"n={n} t={t}: gcd multiple of p! g={g} g/p={g//p}")
            found=True; break
        elif g and g.bit_length()>0:
            pass
    if not found:
        print("scan done, no p-multiple found")
