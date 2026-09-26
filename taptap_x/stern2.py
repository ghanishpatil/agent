
# Correct generalized Stern (Contini-Shparlinski) recovery of modulus p for an order-`ORD`
# truncated linear recurrence x_i = sum c_m x_{i-m} mod p, outputs y_i = x_i >> low.
#
# Idea: x_i = y_i*W + e_i, W=2^low, 0<=e_i<W.
# The recurrence gives a linear relation with UNKNOWN coeffs. But consider vectors
#   v_i = (x_i, x_{i+1}, ..., x_{i+ORD})    (ORD+1 dims)
# All v_i lie in the lattice orthogonal (mod p) to w=(-c1..-cORD? ) ... single relation.
# So any ORD+2 of the v_i are lin. dependent over Z/p; equivalently there is a fixed
# integer vector (the connection polynomial coeffs, reduced mod p) k=(k0..kORD) with
#   sum_j k_j x_{i+j} = 0 mod p   for all i.   (k = (-c1..-cORD? , 1) up to sign)
# We DON'T know k. Stern: build lattice on differences of outputs to find short k.
#
# Build B (rows indexed i=0..n-1): columns = [ D_{i,0},...,D_{i,t-1} | e_i-block(identity) ]
# where D_{i,j} = y_{i+j} (we search combos of consecutive y that are ~0 mod p).
# Simpler, robust approach that WORKS: find a short integer relation among consecutive
# outputs y using LLL such that sum_j k_j * y_{i+j} is tiny for MANY i simultaneously.
# Then sum_j k_j * x_{i+j} = sum k_j (y_{i+j} W + e_{i+j}) = W*(small) + sum k_j e_{i+j}.
# Since sum k_j x_{i+j} = 0 mod p and |sum k_j e| is small-ish, we get multiples of p.
#
# Concretely: LLL the lattice with rows r_i = [ y_i, y_{i+1}, ..., y_{i+ORD} ] scaled, plus
# a big weight on making the combination small. Standard: columns are the y-windows over
# MANY shifts; find kernel vector k s.t. k . window ~ 0.
#
# We use the construction: Matrix M (rows = shifts s=0..S-1) has entries M[s][j] = y_{s+j},
# j=0..ORD.  A short vector in the LEFT null space isn't what we want; we want k in the
# right kernel over reals of the (S x (ORD+1)) matrix of TRUE x-windows. Over reals with y
# approx, use LLL on the embedding:
#   Lattice basis rows (ORD+1 of them): [ K * y_{col}?? ]  -> use the "kernel via LLL" trick:
# Build A = (ORD+1) x (ORD+1+S): left block = identity*1 ; right block[j][s] = round(y_{s+j}).
# Then a vector m in row space with small right part means sum_j m_j y_{s+j} ~ 0 for all s.
# The m_j (left block) is the connection polynomial k. LLL finds it.

from fpylll import IntegerMatrix, LLL
from math import gcd
from sympy import Matrix

def recover_connection_poly(Y, ORD, S, scale):
    d = ORD+1
    ncols = d + S
    rows=[]
    for j in range(d):
        row=[0]*ncols
        row[j]=1
        for s in range(S):
            row[d+s]= scale * Y[s+j]
        rows.append(row)
    A=IntegerMatrix(d, ncols)
    for i in range(d):
        for jj in range(ncols):
            A[i,jj]=int(rows[i][jj])
    LLL.reduction(A)
    # first reduced row: left part = connection poly k (small), right part ~ scale*(sum k_j y) small
    cands=[]
    for i in range(d):
        k=[A[i,j] for j in range(d)]
        if any(k):
            cands.append(k)
    return cands

def recover_p(Y, ORD):
    # Try to get connection poly k, then p = gcd over i of ( sum_j k_j * (Y[i+j]) )? No: that's y not x.
    # Instead: once we have k (integer connection poly, = char poly coeffs up to sign, reduced mod p),
    # compute L_i = sum_j k_j * (Y[i+j]*W). This ≡ -(sum_j k_j e_{i+j}) mod p, small*W-ish; and it is
    # ALSO ≡ 0 mod p only if k is the TRUE relation with e handled. Not directly multiples of p.
    # Better classic: p = gcd of (ORD+1)x(ORD+1) minors of EXACT x windows. We don't have exact x.
    #
    # Real Stern: k found here is the connection poly MOD p. Two different reduced vectors k^(1),k^(2)
    # are both ≡ (char poly)*scalar mod p, so k^(1) and k^(2) as integer polynomials have resultant
    # divisible by p. p = gcd of resultants of pairs of candidate polynomials.
    from sympy import symbols, resultant, Poly, ZZ as sZZ
    x=symbols('x')
    best=None
    for S in range(ORD+2, min(len(Y)-ORD, ORD+40)):
        for scale_bits in [1, 20, 40, 60, 80, 100]:
            scale=1<<scale_bits
            cands=recover_connection_poly(Y, ORD, S, scale)
            polys=[]
            for k in cands:
                P=sum(int(c)*x**i for i,c in enumerate(k))
                if P!=0:
                    polys.append(Poly(P,x,domain=sZZ))
            # gcd of resultants of pairs
            from itertools import combinations
            g=0
            rs=[]
            for P0,P1 in combinations(polys,2):
                if P0.degree()<1 or P1.degree()<1: continue
                try:
                    r=int(resultant(P0.as_expr(),P1.as_expr(),x))
                except Exception:
                    continue
                if r: rs.append(abs(r))
            for r in rs: g=gcd(g,r)
            yield (S, scale_bits, g, rs[:2])

if __name__=="__main__":
    from toy import gen
    ORD=3; LOW=16; K=48
    p,C,A,Y=gen(ORD,K,LOW,120)
    print("true p", p, "bits", p.bit_length())
    hit=False
    for S,sb,g,rs in recover_p(Y,ORD):
        div = (g%p==0 and g>0)
        if div:
            print(f"S={S} scale2^{sb}: gcd={g}  DIVISIBLE by p (g/p={g//p})")
            hit=True
            break
    if not hit:
        print("no direct hit; sample last:", S,sb,g)
