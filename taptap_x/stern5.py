
# Faithful port of Contini-Shparlinski Stern attack (ORDER 1) to fpylll+sympy, tested on an
# ORDER-1 toy first to validate the machinery, THEN think about order-25.
from fpylll import IntegerMatrix, LLL
from math import gcd, ceil, sqrt
from sympy import symbols, resultant, Poly, ZZ as sZZ, Integer, gcd as pgcd
from sympy.polys.domains import ZZ
from itertools import combinations
from random import randint, seed as rseed
from Crypto.Util.number import isPrime

x=symbols('x')

def lll_rows(rows):
    n=len(rows); m=len(rows[0]); A=IntegerMatrix(n,m)
    for i in range(n):
        for j in range(m): A[i,j]=int(rows[i][j])
    LLL.reduction(A)
    return [[A[i,j] for j in range(m)] for i in range(n)]

def generate_polynomials(y,n,t):
    rows=[]
    for i in range(n):
        row=[0]*(n+t)
        for j in range(t): row[j]=y[i+j+1]-y[i+j]
        row[t+i]=1
        rows.append(row)
    red=lll_rows(rows)
    for v in red:
        P=sum(int(l)*x**i for i,l in enumerate(v[t:]))
        if P!=0: yield Poly(P,x,domain=sZZ)

def recover(y,k,s,check):
    alpha=s/k; t=int(1/alpha); n=ceil(sqrt(2*alpha*t*k))
    chunk=n+t
    while chunk<=len(y):
        polys=[]
        for i in range(len(y)//chunk):
            polys+=list(generate_polynomials(y[chunk*i:chunk*(i+1)],n,t))
        for comb in combinations(polys,3):
            P0,P1,P2=comb
            try:
                m_=gcd(gcd(abs(int(resultant(P0.as_expr(),P1.as_expr(),x))),
                            abs(int(resultant(P1.as_expr(),P2.as_expr(),x)))),
                            abs(int(resultant(P0.as_expr(),P2.as_expr(),x))))
            except Exception: continue
            if m_>1 and check(m_):
                return m_,(n,t)
        t+=1; n=ceil(sqrt(2*alpha*t*k)); chunk=n+t
    return None,None

# ORDER-1 toy (classic truncated LCG, no increment): x_{i+1}=a*x_i mod p ; y=x>>low
def gen1(k,low,cnt,sd=7):
    rseed(sd)
    p=2**k - randint(2**(k//3),2**(k//3+2))
    while not isPrime(p): p-=1
    a=randint(2,p-1); x0=randint(2,p-1)
    xs=[x0]
    for _ in range(cnt): xs.append(xs[-1]*a%p)
    y=[v>>low for v in xs]
    return p,a,y

if __name__=="__main__":
    K=48; LOW=16; s=K-LOW
    p,a,y=gen1(K,LOW,80)
    print("order-1 toy true p",p)
    m_,params=recover(y,K,s,lambda mm: abs(mm.bit_length()-K)<=1)
    print("recovered modulus:", m_, "params", params, "== p:", m_==p)
