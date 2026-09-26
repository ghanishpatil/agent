# Cryptography Challenge - Solution Status

## Challenge: CnK3cCB
**Category**: Cryptography  
**Difficulty**: Medium  
**Points**: 300  
**Flag Format**: Kaal*

## Current Status: IN PROGRESS

The challenge requires a **Meet-in-the-Middle (MITM) attack** on a double-encryption scheme.

## What We Know

### Encryption Structure
```python
def encrypt(key, pt):
    k1 = key[:3]  # First 3 bytes
    k2 = key[3:]  # Remaining bytes
    return fun(k2, fun(k1, pt))
```

With the simplest assumptions (ROUNDS=1, identity SBOX/PERM):
```
CT = (PT XOR MD5(k1)) XOR MD5(k2)
```

### Known Values
- **Plaintext**: `c91ca824783e91dc41a856162bcfaebc`
- **Ciphertext**: `25c4ceee22c0529b19c2b51886fed24c`
- **Flag (encrypted)**: `adee3839c59e972f2b2e96440f0002d0`

## Attack Strategy

### MITM Algorithm
1. **Forward Phase**: Build table of all `PT XOR MD5(k1)` for all k1 values
2. **Backward Phase**: For each k2, compute `CT XOR MD5(k2)` and check if it's in the table
3. **When match found**: We have both k1 and k2, can decrypt the flag

### Complexity Analysis

| Configuration | Forward Table | Search Space | Total Ops | Est. Time (single core) |
|--------------|---------------|--------------|-----------|------------------------|
| k1=3, k2=3   | 16.7M         | 16.7M        | 33.5M     | ~5-10 minutes         |
| k1=3, k2=4   | 16.7M         | 4.3B         | 4.3B      | ~10-20 hours          |
| k1=3, k2=5   | 16.7M         | 1.1T         | 1.1T      | ~months               |

## What We've Tried

✗ Common keys (kaal, flag, password, etc.)  
✗ Numeric patterns (years, PINs)  
✗ Sequential and repeating byte patterns  
✗ Keys derived from PT/CT  
✗ Different key split positions  
✗ Single encryption (not double)  
✗ k1=1, k2=1 through k1=2, k2=3  
✗ First 50M of k1=3, k2=4 space  
⏳ **CURRENTLY RUNNING**: Full k1=3, k2=3 search

## Current Solver

**File**: `optimized_final_solver.py`  
**Status**: Running in background (Process ID: 8)  
**Configuration**: k1=3 bytes, k2=3 bytes  
**Progress**: Check with `getProcessOutput`

This solver will:
- Build forward table: ~16.7M entries (~1-2 minutes)
- Search k2 space: ~16.7M checks (~5-10 minutes)
- **If successful**: Will print the flag and exit
- **If unsuccessful**: Key is likely in k2=4 or higher range

## Next Steps if k1=3, k2=3 Fails

### Option 1: Extended Search (k1=3, k2=4)
- Use `continuous_solver.py` which saves progress
- Estimated time: 10-20 hours on single core
- Can be parallelized across multiple cores/machines

### Option 2: Cloud Computing
- Spin up multiple cloud instances
- Divide the k2 search space
- Each instance searches a different range
- Estimated cost: $5-20 depending on provider

### Option 3: GPU Acceleration
- Implement CUDA/OpenCL version
- Could reduce time to minutes/hours
- Requires GPU programming expertise

### Option 4: Re-examine Assumptions
- Maybe SBOX/PERM are not identity
- Maybe ROUNDS != 1
- Maybe there's a hint in diagram.png we missed

## How to Check Progress

```bash
# Check if solver is still running
python -c "import psutil; print([p for p in psutil.process_iter() if 'python' in p.name().lower()])"

# Or check the process output
# (use getProcessOutput tool with processId 8)
```

## If Key is Found

The solver will automatically:
1. Verify the key works
2. Decrypt the flag
3. Print the flag in multiple formats
4. Exit with success code

## Recommendation

**Wait for the current solver to complete** (~10-15 minutes total).

If it doesn't find the key, then:
1. Start `continuous_solver.py` for the k1=3, k2=4 search
2. Let it run overnight
3. Or consider cloud computing for faster results

## Files Created

- `optimized_final_solver.py` - Currently running
- `continuous_solver.py` - For long-running searches with progress saving
- `CRYPTO_CHALLENGE_ANALYSIS.md` - Detailed technical analysis
- Multiple test scripts for edge cases and patterns

---

**Last Updated**: Just now  
**Status**: Solver running, awaiting results
