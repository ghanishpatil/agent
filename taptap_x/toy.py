from random import randint, seed
from Crypto.Util.number import isPrime

# Toy with same structure, small params, to develop the attack.
def gen(order, pbits, trunc, ngen, sd=1234):
    seed(sd)
    p = 2**pbits - randint(2**(pbits//3), 2**(pbits//3+2))
    while not isPrime(p): p -= 1
    n=order
    C=[randint(1,p) for _ in range(n)]
    A=[randint(1,p) for _ in range(n)]
    for _ in range(ngen):
        A.append(sum(ci*ai for ci,ai in zip(C[::-1],A[::-1]))%p)
    Y=[ai>>trunc for ai in A[::-1][:ngen]][::-1]
    return p,C,A,Y

if __name__=="__main__":
    p,C,A,Y=gen(3, 48, 16, 40)
    print("p",p,"bits",p.bit_length())
    print("C",C)
    print("A0..A_n-1", A[:3])
    print("gen count", len(A)-3)
    print("Y[:5]", Y[:5])
    # recurrence check
    B=2**16
    g=A[3:]   # generated
    # g_j = sum_{m=1..3} C[3-m]*g_{j-m} for j>=3 (all generated)
    for j in range(3,10):
        pred=(C[2]*g[j-1]+C[1]*g[j-2]+C[0]*g[j-3])%p
        assert pred==g[j], (j,pred,g[j])
    print("toy recurrence on generated OK")
