
from hashlib import md5

BLOCK_SIZE = 16
ROUNDS = None
SBOX = None
PERM = None

def xor(a,b):
    return bytes([x^y for x,y in zip(a,b)])

def fun(key, pt):

    key = md5(key).digest()
    state = bytearray(pt)

    for r in range(ROUNDS):

        state = bytearray(xor(state,key))

        for i in range(BLOCK_SIZE):
            state[i] = SBOX[state[i]]

        new = bytearray(BLOCK_SIZE)

        for i in range(BLOCK_SIZE):
            new[i] = state[PERM[i]]

        state = new

    return bytes(state)


def encrypt(key, pt):

    k1 = key[:3]
    k2 = key[3:]

    return fun(k2, fun(k1, pt))
