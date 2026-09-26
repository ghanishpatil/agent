from sage.all import *
from itertools import combinations
from math import ceil, sqrt, gcd as igcd

# jvdsn generate_polynomials (order-1 Stern), Sage version
def generate_polynomials(y, n, t):
    B = matrix(ZZ, n, n + t)
    for i in range(n):
        for j in range(t):
            B[i, j] = y[i + j + 1] - y[i + j]
        B[i, t + i] = 1
    B = B.LLL()
    R = ZZ["x"]; x = R.gen()
    polys=[]
    for r in B.rows():
        P = R(list(r[t:]))
        if P != 0: polys.append(P)
    return polys

def recover_modulus(y, k, s, check):
    alpha = s/k; t=int(1/alpha); n=ceil(sqrt(2*alpha*t*k)); chunk=n+t
    while chunk <= len(y):
        polys=[]
        for i in range(len(y)//chunk):
            polys += generate_polynomials(y[chunk*i:chunk*(i+1)], n, t)
        for comb in combinations(polys,3):
            P0,P1,P2=comb
            m_ = igcd(igcd(int(P0.resultant(P1)), int(P1.resultant(P2))), int(P0.resultant(P2)))
            if m_>1 and check(m_):
                return m_,(n,t)
        t+=1; n=ceil(sqrt(2*alpha*t*k)); chunk=n+t
    return None,None

# order-1 LCG WITH increment (matches Stern's model): x=(a*x+c) mod p ; y=x>>low
set_random_seed(7)
K=48; LOW=16; s=K-LOW
p = random_prime(2**K, lbound=2**(K-1))
a = randint(2,p-1); cinc=randint(1,p-1); x0=randint(1,p-1)
xs=[x0]
for _ in range(100): xs.append((a*xs[-1]+cinc)%p)
y=[v>>LOW for v in xs]
print("true p", p)
m_,par = recover_modulus(y, K, s, lambda mm: abs(int(mm).bit_length()-K)<=1)
print("recovered", m_, par, "==p", m_==p)
