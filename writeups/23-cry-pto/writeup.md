# cry-pto — K17 CTF (crypto, beginner, 207 pts, 37 solves)

**Flag:** `K17{y0u_ar3_f1ll3d_w1th_deter1min4t10n}`
**Service:** `nc chal.secso.cc 2000` (server-run grading — submit a valid tag for `root`, server prints `/flag`).

## Recon (Rule Zero — read the code as spec)
`CRYSig` builds a 128×64 binary matrix (`TAG_SIZE*8 = 128` rows, each `int.from_bytes(os.urandom(8))` = a 64-bit vector).
`sign(m)` (m = 8 bytes = 64-bit vector) outputs 128 bits, bit *i* = `popcount(row_i & m) % 2` = the **GF(2) dot product** of row *i* with the message. Tag = 16 bytes.

Interaction:
1. Server prints `sign(user)` for `user=b"babyuser"` (free).
2. We send one `query` (blocked only if `query == root`), server returns `sign(query)`.
3. We send a tag; if `verify(root, tag)` passes → it prints `/flag`.  `root=b"chadr00t"`.

## Key insight
`sign(m) = M·m` over GF(2), so it's **linear** with no affine constant (`sign(0)=0`):
`sign(a ⊕ b) = sign(a) ⊕ sign(b)`.

We need `sign(root)` but can't query `root` directly. Choose `query = root ⊕ user` (≠ root, since `user≠0`). Then:
```
sign(query) = sign(root ⊕ user) = sign(root) ⊕ sign(user)
⇒ sign(root) = sign(query) ⊕ sign(user)
```
Both `sign(query)` and `sign(user)` are given → forge `sign(root)` with zero knowledge of the matrix.

## Exploit (self-validating)
```python
user=b"babyuser"; root=b"chadr00t"
query=bytes(a^b for a,b in zip(root,user))          # 0109031d07435506, != root
io=remote("chal.secso.cc",2000)
usig=bytes.fromhex(io.recvline().split(b":",1)[1].strip())
io.recvuntil(b"> "); io.sendline(query.hex().encode())
qsig=bytes.fromhex(io.recvline().split(b":",1)[1].strip())
root_sig=bytes(a^b for a,b in zip(qsig,usig))       # = sign(root)
io.recvuntil(b"> "); io.sendline(root_sig.hex().encode())
print(io.recvall())                                  # K17{...}
```
Run values: `usig=5ccfadfba01632b18eed489c6b97f6b4`, `qsig=368bfffa93bfeae99ad9303c79853521`,
`root_sig=6a44520133a9d858143478a01212c395` → **flag printed**. Also verified locally: the identity held for 1000/1000 random matrices before touching the server.

## Verification
The server itself accepted the forged tag and returned the flag — no guessing, fully self-validating.

## Generalization (the CLASS + the TELL)
- **Class:** *Linear MAC / signature forgery over GF(2)*. Any "signature" built from `popcount(row & msg) % 2`, matrix·vector, XOR-folds, or bit parities is **linear** → `sign(a⊕b)=sign(a)⊕sign(b)`.
- **The TELL:** signing is bitwise/parity/matrix-multiply with **no secret nonce and no nonlinear step (no S-box/mod add/hash)**, and the server gives you an oracle on chosen messages plus a freebie. Combine known tags by XOR to reach the target message `root = ⊕ of things you can sign`. `sign(0)=0` means it's purely linear (no constant to cancel).
- **Reusable trick:** when the forbidden target `t` and an allowed message `q` and a free message `f` satisfy `t = q ⊕ f`, then `tag(t) = tag(q) ⊕ tag(f)`. More generally, query a basis and solve the linear system; here one XOR sufficed.
