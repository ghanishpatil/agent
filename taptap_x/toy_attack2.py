
# Attack: recover coefficients c and modulus p from truncated order-`ord` linear recurrence.
# Method: build an integer lattice whose short vectors reveal the recurrence relation.
#
# Relation (exact): g_j = sum_{m=1..ord} c_m g_{j-m} - t_j p    (t_j integers)
# Unknowns: c_m (large, ~p), p (~2^pbits), and low bits e_j (< B).
# g_j = Y_j*B + e_j.
#
# Strategy A (recover p via "integer relation among windows using known highs + LLL on errors"):
# For each j: define R_j = g_j - sum c_m g_{j-m}. R_j = t_j p.
# Consider consecutive j: the (ord+1) x (ord+1) matrix of consecutive u-vectors is singular mod p.
#
# Instead use the classic: the vector w=(1,-c_1,...,-c_ord) satisfies U*w = 0 mod p where U rows are
# windows. Over Z: (windows | I) etc.  We'll try Nguyen-Stern orthogonal lattice on the columns.
#
# For a first attempt, we RECOVER p by LLL that finds small integer combos of the *known* high vectors
# that would be 0 mod p if errors were 0, i.e., find kernel of the high-part matrix over Z that is small.

from toy import gen
from fpylll import IntegerMatrix, LLL, GSO
from math import gcd
from sympy import Matrix

ord=3; trunc=16; pbits=48
p,C,A,Y=gen(ord, pbits, trunc, 60)
B=2**trunc
g=A[ord:]                 # exact generated
gt=[y*B for y in Y]       # truncated
N=len(g)
print("p",p,"C",C)

# --- Recover w=(1,-c1,...,-cord) mod p and p, via lattice on windows ---
# Build windows u_j = (g_j, g_{j-1}, ..., g_{j-ord})  for j=ord..N-1
# We know only highs U_j. Let e_j window errors small.
# Consider matrix M (rows = U_j). We seek w with U_j . w ~ 0 mod p (small residue from errors).
#
# Trick to get p: pick ord+2 consecutive EXACT-unknown windows; they are lin. dependent mod p.
# Use LLL to find the small integer combination lambda (length ord+2) s.t. sum lambda_i u_{j+i} = 0 (exactly, as vectors) mod p.
# Actually consecutive windows overlap; the dependency is exactly the recurrence => lambda ~ (1,-c..) shifted. Not small.

# Let's just verify the exact-gcd p-recovery and then attempt to recover errors by CVP once we GUESS p.
def det_int(rows): return int(Matrix(rows).det())
def windows(seq):
    return [[seq[j-k] for k in range(ord+1)] for j in range(ord, len(seq))]
Wex=windows(g)
gg=0
for i in range(len(Wex)-(ord+1)):
    gg=gcd(gg, det_int(Wex[i:i+ord+1]))
print("exact gcd p:", gg, gg==p)

# Recover c from exact g via linear solve mod p (sanity)
import sympy
M=Matrix([[g[j-1],g[j-2],g[j-3]] for j in range(ord, ord+ord)])   # 3 eqns
rhs=Matrix([g[j] for j in range(ord, ord+ord)])
Mi=M.inv_mod(p)
c=(Mi*rhs)%p
print("recovered c (from exact):", list(c), "true", [C[2],C[1],C[0]])
