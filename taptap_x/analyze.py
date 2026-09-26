# Reproduce the generation logic on toy values to nail the recurrence indexing.
from random import randint, seed
seed(1)
p = 10**9+7
n = 25
C = [randint(1,p) for _ in range(n)]
A = [randint(1,p) for _ in range(n)]
init = A[:]
for _ in range(5):
    A.append(sum(ci*ai for ci,ai in zip(C[::-1], A[::-1])) % p)

# Verify: new = sum over j of C_rev[j]*A_rev[j], zip truncates to len 25 (=len C)
# A_rev[0]=A[-1] (newest). C_rev[0]=C[-1]=C[24].
# So new = C[24]*A[-1] + C[23]*A[-2] + ... + C[0]*A[-25]
def new_term(A):
    s=0
    for j in range(25):
        s += C[24-j]*A[-1-j]
    return s % p
for k in range(25,30):
    # recompute A[k] from A[:k]
    pref = A[:k]
    assert new_term(pref) == A[k], (k, new_term(pref), A[k])
print("recurrence confirmed: A[k] = sum_{j=0..24} C[24-j]*A[k-1-j] mod p")
print("=> A[k] = C[24]*A[k-1] + C[23]*A[k-2] + ... + C[0]*A[k-25]")
# Equivalent: coefficient of A[k-1-j] is C[24-j]; let d=k-1-j, j=k-1-d
# A[k] = sum_{m=1..25} C[25-m]*A[k-m]  (m=j+1). coeff of A[k-m] = C[25-m]. m=1->C[24],m=25->C[0]. yes.
