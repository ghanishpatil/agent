#!/usr/bin/env python3
"""
Final attempt at Håstad's attack
Based on the hint and what we found, let me try a different approach:
- The challenge mentions "small exponent" - likely e=3
- We found e=7 and e=9 in the files, but these might be red herrings
- The secret number 83927465839274658392746583 might be important

Let me try to see if this challenge expects us to have the RSA parameters
from the challenge description page itself.
"""

# For now, let me create a template solver that can work once we have the params

def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using CRT
    x ≡ r1 (mod n1)
    x ≡ r2 (mod n2)
    x ≡ r3 (mod n3)
    """
    total = 0
    prod = 1
    for m in moduli:
        prod *= m
    
    for r, m in zip(remainders, moduli):
        p = prod // m
        total += r * pow(p, -1, m) * p
    
    return total % prod

def hastad_broadcast_attack(c1, n1, c2, n2, c3, n3, e=3):
    """
    Håstad's Broadcast Attack
    When same message M is encrypted with small e across different moduli
    """
    print("="*70)
    print("HÅSTAD'S BROADCAST ATTACK")
    print("="*70)
    print(f"\nExponent e = {e}")
    print(f"\nCiphertext 1: {c1}")
    print(f"Modulus 1: {n1}")
    print(f"\nCiphertext 2: {c2}")
    print(f"Modulus 2: {n2}")
    print(f"\nCiphertext 3: {c3}")
    print(f"Modulus 3: {n3}")
    
    # Apply CRT to get M^e mod (n1*n2*n3)
    M_pow_e = chinese_remainder_theorem([c1, c2, c3], [n1, n2, n3])
    
    print(f"\nM^{e} mod (n1*n2*n3) = {M_pow_e}")
    
    # Since M^e < n1*n2*n3 (for small messages), we can take the e-th root directly
    # Use integer nth root
    def integer_nth_root(x, n):
        """Calculate integer nth root"""
        if x == 0:
            return 0
        
        # Binary search for the root
        low = 0
        high = x
        
        while low < high:
            mid = (low + high + 1) // 2
            if mid ** n <= x:
                low = mid
            else:
                high = mid - 1
        
        return low
    
    M = integer_nth_root(M_pow_e, e)
    
    print(f"\nM = {M}")
    
    # Convert to bytes
    try:
        from Crypto.Util.number import long_to_bytes
        message = long_to_bytes(M)
        print(f"\nDecrypted message (bytes): {message}")
        print(f"Decrypted message (text): {message.decode('utf-8', errors='ignore')}")
        
        # Check if it's a flag
        if b'Kaal{' in message or b'kaal{' in message:
            print(f"\n*** FLAG FOUND: {message.decode('utf-8', errors='ignore')} ***")
        
        return message
    except Exception as e:
        print(f"\nError converting to bytes: {e}")
        return None

# Example usage (need actual values from challenge page)
print("This solver is ready to use once we have the RSA parameters.")
print("\nWe need:")
print("- n1, c1 (from soul_stone_1st)")
print("- n2, c2 (from time_stone_2nd)")
print("- n3, c3 (from mind_stone_3rd)")
print("- e (likely 3)")

print("\n" + "="*70)
print("WHAT WE FOUND SO FAR")
print("="*70)
print("soul_stone: e=7 (might be red herring)")
print("time_stone: e=9 (might be red herring)")
print("mind_stone: 2157869541235478521545895 (in comment)")
print("mind_stone secret: 83927465839274658392746583")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)
print("1. Check the challenge page for RSA parameters")
print("2. Or try to extract n and c from the audio data itself")
print("3. The numbers we found might BE the c values")

# Let's try assuming the numbers we found are c values and e=3
print("\n" + "="*70)
print("ATTEMPTING WITH FOUND NUMBERS")
print("="*70)

# If these are the c values and we need to find n values...
# Or maybe the challenge expects us to get n and c from elsewhere

# Let me try one more thing - check if the file sizes or audio properties encode the values
import wave

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    with wave.open(filename, 'rb') as wav:
        n_frames = wav.getnframes()
        sample_rate = wav.getframerate()
        
        print(f"\n{stone}:")
        print(f"  Frames: {n_frames}")
        print(f"  Sample rate: {sample_rate}")
        print(f"  Duration: {n_frames / sample_rate:.6f} seconds")
        
        # Maybe the frame count or duration encodes something?
        print(f"  Frames as potential value: {n_frames}")
