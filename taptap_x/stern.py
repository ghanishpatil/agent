
# Generalized Stern's attack (Contini-Shparlinski) for order-`ord` truncated linear recurrence
# with unknown modulus and unknown coefficients.
# Ported to fpylll + sympy (no Sage).
#
# Recurrence: x_{i} = sum_{m=1..ord} c_m x_{i-m}  (mod p)   -- but note our challenge has NO increment.
# Outputs y_i = x_i >> low   (keep top s = k-low bits).
#
# _generate_polynomials (Section 2.1 generalized): build lattice from consecutive differences.
# For order n, the connection polynomial has degree n. We build B with n columns of differences
# spanning enough to force degree-n relations, plus identity.

from fpylll import IntegerMatrix, LLL
from sympy import Poly, symbols, gcd as sgcd, resultant, ZZ as sZZ, Integer
from math import gcd, isqrt, ceil, sqrt

x = symbols('x')

def shortest_vectors(B_rows):
    # B_rows: list of list of python ints. Return LLL-reduced rows.
    n=len(B_rows); m=len(B_rows[0])
    A=IntegerMatrix(n,m)
    for i in range(n):
        for j in range(m):
            A[i,j]=int(B_rows[i][j])
    LLL.reduction(A)
    out=[]
    for i in range(n):
        out.append([A[i,j] for j in range(m)])
    return out

def generate_polynomials(y, n, t):
    # Section 2.1: B is n x (n+t). B[i][j] = y[i+j+1]-y[i+j] for j in 0..t-1 ; B[i][t+i]=1
    rows=[]
    for i in range(n):
        row=[0]*(n+t)
        for j in range(t):
            row[j]=y[i+j+1]-y[i+j]
        row[t+i]=1
        rows.append(row)
    red=shortest_vectors(rows)
    polys=[]
    for v in red:
        coeffs=v[t:]  # the last n entries -> polynomial coefficients
        P=sum(int(c)*x**i for i,c in enumerate(coeffs))
        polys.append(Poly(P, x, domain=sZZ))
    return polys

def recover_modulus_and_poly(polys, order, check_modulus):
    from itertools import combinations
    results=[]
    # use small combos; modulus = gcd of resultants of pairs/triples
    cand_polys=[P for P in polys if P.degree()>=1]
    for comb in combinations(cand_polys, 3):
        P0,P1,P2=comb
        try:
            r01=int(resultant(P0.as_expr(),P1.as_expr(),x))
            r12=int(resultant(P1.as_expr(),P2.as_expr(),x))
            r02=int(resultant(P0.as_expr(),P2.as_expr(),x))
        except Exception:
            continue
        m_=gcd(gcd(abs(r01),abs(r12)),abs(r02))
        if m_>1 and check_modulus(m_):
            results.append((m_,comb))
    return results

if __name__=="__main__":
    from toy import gen
    ORD=3; LOW=16; K=48
    p,C,A,Y=gen(ORD, K, LOW, 80)
    print("true p", p, "bits", p.bit_length())
    # char poly of recurrence x_i = c3 x_{i-1}+c2 x_{i-2}+c1 x_{i-3}: x^3 - c3 x^2 - c2 x - c1
    print("true c (c1,c2,c3):", C)
    s=K-LOW  # output bits
    alpha=s/K
    t=int(1/alpha)
    n=ceil(sqrt(2*alpha*t*K))
    print("alpha",alpha,"init n",n,"t",t)
    # For order>1 we likely need n>=ORD+something. Try increasing chunk.
    for extra in range(0,6):
        nn=n+extra+ORD
        tt=t
        chunk=nn+tt
        if chunk+1>len(Y): break
        polys=generate_polynomials(Y[:chunk+1], nn, tt)
        res=recover_modulus_and_poly(polys, ORD, lambda mm: abs(mm.bit_length()-K)<=2)
        print(f"n={nn} t={tt} chunk={chunk}: candidate moduli:", [r[0]==p for r in res][:5], "any:", any(r[0]==p for r in res))
        for m_,comb in res:
            if m_==p:
                print("  FOUND p via resultant gcd!")
                break
