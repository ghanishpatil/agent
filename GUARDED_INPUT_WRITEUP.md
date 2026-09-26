# Guarded Input - Writeup

**Challenge:** Guarded Input  
**Category:** Reverse Engineering  
**Flag:** `Kaal{4r3_y0u_cr4k3_k44l_ch4kr4}`

## Description
A mysterious program locked behind a single condition. It reveals nothing unless provided with the exact input it seeks.

**File:** crackme.exe (MinGW x64 PE)

## Solution

### Step 1: Binary Analysis
Examined the 64-bit Windows executable and extracted strings:
- "Enter key: ", "Flag: ", "Wrong key!", "Nice try... but wrong flag"

Found two sets of encoded strings in the .text section constructed via movabs instructions.

### Step 2: Decoy Flag Discovery
Located encoded stack strings at RVA 0x178f:
```
'flag: Eo' + 'obuhboiQ' + 'ha{`jQma' + '`i|oz{bo' + 'zga`}Ql{' + 'zQya|`iQ' + '`iQl|as'
```

XOR'd with key 0x0e:
```python
decoded = ''.join(chr(ord(c) ^ 0x0e) for c in encoded)
# Result: hboi4.Kaal{flag_found_congratulations_but_worng_ng_bro}
```

This is a **decoy flag** (note "worng" typo) shown on wrong input.

### Step 3: Key Extraction
Found three key generation functions:
- Function 1 (RVA 0x184c): `0x7a1b0f1e` → bytes `[0x1e, 0x0f, 0x1b, 0x7a]`
- Function 2 (RVA 0x186f): `0x2b203c2d + 0x2b` → bytes `[0x2d, 0x3c, 0x20, 0x2b, 0x2b]`
- Function 3 (RVA 0x189d): `0x7c2d203c` → bytes `[0x3c, 0x20, 0x2d, 0x7c]`

Each byte XOR'd with 0x5b at RVA 0x18c0:
```python
key_bytes = [0x1e, 0x0f, 0x1b, 0x7a, 0x2d, 0x3c, 0x20, 0x2b, 0x2b, 0x3c, 0x20, 0x2d, 0x7c]
key = ''.join(chr(b ^ 0x5b) for b in key_bytes)
# Result: ET@!vg{ppg{v'
```

### Step 4: Getting Scrambled Flag
Running with the correct key:
```bash
./crackme.exe
Enter key: ET@!vg{ppg{v'
Flag: K_cauc_ha0rl4ly44k{_k4r433k4r_}
```

Output is scrambled - needs decoding.

### Step 5: Rail Fence Decryption
The scrambled flag uses Rail Fence cipher with 7 rails:

```python
def rail_fence_decrypt(text, rails):
    fence = [['' for _ in range(len(text))] for _ in range(rails)]
    rail, direction = 0, 1
    
    for col in range(len(text)):
        fence[rail][col] = '*'
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1
    
    index = 0
    for row in range(rails):
        for col in range(len(text)):
            if fence[row][col] == '*':
                fence[row][col] = text[index]
                index += 1
    
    result, rail, direction = [], 0, 1
    for col in range(len(text)):
        result.append(fence[rail][col])
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1
    
    return ''.join(result)

flag = rail_fence_decrypt("K_cauc_ha0rl4ly44k{_k4r433k4r_}", 7)
# Result: Kaal{4r3_y0u_cr4k3_k44l_ch4kr4}
```

## Flag
`Kaal{4r3_y0u_cr4k3_k44l_ch4kr4}`

Reads as: "are you crake kaal chakra"
