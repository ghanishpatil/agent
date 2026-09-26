# Stones Challenge - Complete Analysis

## Challenge Description
- **Hint**: "Three fragments. Same pattern. Repetition was intentional. When the exponent is small, the message doesn't stay hidden for long."
- **Attack Type**: Håstad's Broadcast Attack (RSA with small exponent e=3)
- **Files**: soul_stone_1st.wav, time_stone_2nd.wav, mind_stone_3rd.wav

## What I Found

### 1. mind_stone_3rd.wav
- **ICMT Comment**: `2157869541235478521545895`
- **Hidden ZIP** (password-protected with the comment number)
  - Password: `2157869541235478521545895`
  - Contents: `secret.txt` with value `83927465839274658392746583`

### 2. soul_stone_1st.wav
- Contains text "e=7" (likely misdirection)
- No hidden ZIP or metadata
- Pure audio data (sine wave at 700Hz)

### 3. time_stone_2nd.wav
- Contains text "e=9" (likely misdirection)
- No hidden ZIP or metadata  
- Pure audio data (sine wave at 700Hz)

## Håstad's Broadcast Attack Requirements

To solve this, we need:
- **e = 3** (small exponent, as per hint)
- **Three (n, c) pairs**:
  - (n1, c1) from soul_stone
  - (n2, c2) from time_stone
  - (n3, c3) from mind_stone

### What's Missing
The actual RSA parameters (n and c values) are NOT embedded in the WAV files in any standard format I could find.

## Possible Solutions

### Option 1: Parameters on Challenge Page
Most likely, the RSA parameters are provided in the challenge description on the CTF platform. Look for:
```
n1 = [large number ~1024 bits]
c1 = [large number]
n2 = [large number ~1024 bits]
c2 = [large number]
n3 = [large number ~1024 bits]
c3 = [large number]
```

### Option 2: Network Service
There might be a server to connect to:
```bash
nc [hostname] [port]
```
That provides the RSA parameters.

### Option 3: The Numbers We Found ARE the Solution
If the secret number `83927465839274658392746583` IS the plaintext message M:
```python
from Crypto.Util.number import long_to_bytes
M = 83927465839274658392746583
flag = long_to_bytes(M)
# Result: b'ElU\n*@\xbaO\x80\xaaW'
# Not a valid flag format
```

## Solution Script (Ready to Use)

Once you have the RSA parameters, use this:

```python
from Crypto.Util.number import long_to_bytes

def crt(remainders, moduli):
    total = 0
    prod = 1
    for m in moduli:
        prod *= m
    
    for r, m in zip(remainders, moduli):
        p = prod // m
        total += r * pow(p, -1, m) * p
    
    return total % prod

def cube_root(n):
    low, high = 0, n
    while low < high:
        mid = (low + high + 1) // 2
        if mid ** 3 <= n:
            low = mid
        else:
            high = mid - 1
    return low

# INSERT YOUR RSA PARAMETERS HERE
n1 = # from challenge page
c1 = # from challenge page
n2 = # from challenge page
c2 = # from challenge page
n3 = # from challenge page
c3 = # from challenge page

# Håstad's Attack
M_cubed = crt([c1, c2, c3], [n1, n2, n3])
M = cube_root(M_cubed)
flag = long_to_bytes(M)
print(f"FLAG: {flag.decode()}")
```

## Next Steps
1. Check the challenge page for RSA parameters
2. If there's a netcat service, connect and get the parameters
3. Run the solution script with the parameters
4. Submit the flag in format: `Kaal{...}`
