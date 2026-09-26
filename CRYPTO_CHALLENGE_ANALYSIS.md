# Cryptography Challenge Analysis

## Challenge Details
- **Name**: CnK3cCB
- **Category**: Cryptography
- **Difficulty**: Medium
- **Points**: 300
- **Flag Format**: Kaal*

## Files Provided
1. `encrypt.py` - Encryption code with incomplete parameters
2. `flag_cipher.txt` - Encrypted flag (hex): `adee3839c59e972f2b2e96440f0002d0`
3. `known_pair.txt` - Known plaintext-ciphertext pair
4. `diagram.png` - Visual representation of the cipher

## Known Plaintext-Ciphertext Pair
- **Plaintext**: `c91ca824783e91dc41a856162bcfaebc`
- **Ciphertext**: `25c4ceee22c0529b19c2b51886fed24c`
- **PT XOR CT**: `ecd866ca5afec347586ae30ead317cf0`

## Encryption Structure
```python
def encrypt(key, pt):
    k1 = key[:3]  # First 3 bytes
    k2 = key[3:]  # Remaining bytes
    return fun(k2, fun(k1, pt))
```

The `fun` function applies:
1. XOR with MD5(key)
2. S-box substitution
3. Permutation
4. Repeat for ROUNDS

## Missing Parameters
- `ROUNDS = None` - Number of rounds (likely 1 or 2)
- `SBOX = None` - Substitution box (likely identity: 0→0, 1→1, ..., 255→255)
- `PERM = None` - Permutation (likely identity: [0,1,2,...,15])

## Attack Strategy: Meet-in-the-Middle (MITM)

With the simplest assumptions (ROUNDS=1, identity SBOX/PERM):
- Encryption becomes: `CT = (PT XOR MD5(k1)) XOR MD5(k2)`
- This is vulnerable to MITM attack

### MITM Complexity
- **Forward phase**: Build table of all `fun(k1, PT)` for all k1 values
  - For k1 = 3 bytes: 2^24 = 16,777,216 entries (~320MB RAM)
  
- **Backward phase**: For each k2, compute `decrypt_fun(k2, CT)` and check table
  - For k2 = 3 bytes: 2^24 = 16,777,216 checks
  
- **Total**: 2^24 + 2^24 = 2^25 operations (vs 2^48 for brute force)

## Attempts Made

### 1. Simple Parameter Guessing
- Tried common keys (kaal, flag, password, etc.)
- Tried different key lengths
- **Result**: No match

### 2. MITM with k1=3, k2=3
- Built forward table: 16.7M entries
- Searched k2 space: 16.7M values
- **Result**: No match found (currently running parallel version)

### 3. MITM with k1=3, k2=4
- Forward table: 16.7M entries
- Searched first 50M of 4.3B k2 values
- **Result**: No match in tested range

### 4. ASCII Key Search
- Tested printable ASCII keys up to length 8
- Tested numeric keys (0-9) up to length 7
- **Result**: No match

### 5. Smaller Key Sizes
- Tried k1=2, k2=2 (65K combinations each)
- Tried k1=2, k2=3
- **Result**: No match

## Possible Explanations

1. **Larger Key Space**: k2 might be 4+ bytes, requiring billions of checks
2. **Non-Identity SBOX/PERM**: The S-box or permutation might not be identity
3. **Multiple Rounds**: ROUNDS might be > 1, complicating the structure
4. **Hidden Hint**: The diagram.png might contain steganographic hints
5. **Different Key Split**: Maybe k1 is not exactly 3 bytes

## Next Steps

1. **Complete parallel MITM** for k1=3, k2=3
2. **Analyze diagram.png** more carefully for hidden data
3. **Try non-identity SBOX/PERM** with small key spaces
4. **Distributed computing** for larger k2 values (k2=4 or k2=5)
5. **Check for mathematical weaknesses** in the cipher structure

## Resources Required

For exhaustive search of k1=3, k2=4:
- Time: ~10-20 hours on single core
- Memory: ~500MB
- Can be parallelized across multiple cores/machines

## Current Status

Running parallel MITM solver for k1=3, k2=3 configuration.
If this doesn't find the key, will need to either:
- Extend search to k2=4 (much longer)
- Reconsider the SBOX/PERM assumptions
- Look for additional hints in the challenge materials
