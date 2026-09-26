#!/usr/bin/env python3
"""
FINAL SOLUTION ATTEMPT
Based on typical CTF Hastad attacks, let me create example RSA params
and see if the pattern matches what we should be looking for
"""

from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime
import sys
sys.set_int_max_str_digits(100000)

# The hint says "small exponent" - this means e=3
# For Hastad's attack to work, we need:
# - Same message M encrypted 3 times
# - e=3 for all
# - Three different moduli n1, n2, n3
# - Three ciphertexts c1, c2, c3

# Since I can't find the RSA params in the files, let me check if maybe
# the challenge expects us to use a tool or service

print("="*70)
print("STONES CHALLENGE - FINAL ANALYSIS")
print("="*70)

print("\nWhat we definitively found:")
print("1. soul_stone_1st.wav - contains 'e=7' (likely red herring)")
print("2. time_stone_2nd.wav - contains 'e=9' (likely red herring)")
print("3. mind_stone_3rd.wav - hidden ZIP with:")
print("   - Password: 2157869541235478521545895")
print("   - Secret: 83927465839274658392746583")

print("\nThe challenge hint:")
print("'Three fragments. Same pattern. Repetition was intentional.'")
print("'When the exponent is small, the message doesn't stay hidden for long.'")

print("\nThis clearly indicates Håstad's Broadcast Attack with e=3")

print("\n" + "="*70)
print("POSSIBLE SCENARIOS")
print("="*70)

print("\n1. RSA parameters are on the challenge platform page")
print("   - Most likely scenario for CTF challenges")
print("   - Check the challenge description for n1, c1, n2, c2, n3, c3")

print("\n2. There's a server/service to connect to")
print("   - Some CTF challenges provide RSA params via netcat")
print("   - Check if there's a host:port to connect to")

print("\n3. The audio files encode params in a specific way")
print("   - Frequency modulation")
print("   - Phase encoding")
print("   - Specific steganography tool required")

print("\n4. The numbers we found ARE the solution")
print("   - Let me try one more interpretation...")

# Maybe the secret number, when properly decoded, IS the flag
secret = 83927465839274658392746583

# Try interpreting as different bases
print("\n" + "="*70)
print("TRYING DIFFERENT INTERPRETATIONS OF SECRET NUMBER")
print("="*70)

# As octal?
try:
    octal_str = oct(secret)[2:]
    print(f"As octal: {octal_str}")
except:
    pass

# As binary string interpreted as ASCII?
binary = bin(secret)[2:]
print(f"Binary length: {len(binary)} bits")

# Try chunks of 7 or 8 bits as ASCII
for chunk_size in [7, 8]:
    chars = []
    for i in range(0, len(binary), chunk_size):
        chunk = binary[i:i+chunk_size]
        if len(chunk) == chunk_size:
            val = int(chunk, 2)
            if 32 <= val <= 126:
                chars.append(chr(val))
    if chars:
        result = ''.join(chars)
        print(f"\nBinary as {chunk_size}-bit ASCII: {result}")
        if 'Kaal{' in result or 'kaal{' in result:
            print(f"*** FLAG FOUND: {result} ***")

# Maybe it's a substitution cipher where digits map to letters?
# 0-9 -> a-j or similar
secret_str = str(secret)
digit_to_letter = {str(i): chr(ord('a') + i) for i in range(10)}
substituted = ''.join(digit_to_letter.get(d, d) for d in secret_str)
print(f"\nDigits as letters (0=a, 1=b, etc): {substituted}")

# Try with uppercase
digit_to_upper = {str(i): chr(ord('A') + i) for i in range(10)}
substituted_upper = ''.join(digit_to_upper.get(d, d) for d in secret_str)
print(f"Digits as uppercase: {substituted_upper}")

# Maybe split into groups and convert?
# Like phone number encoding: 2=ABC, 3=DEF, etc.
phone_map = {
    '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL',
    '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ'
}

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("\nI've exhausted all automated extraction methods.")
print("The RSA parameters (n and c values) are NOT embedded in the WAV files")
print("in any standard format.")
print("\nTO GET THE FLAG:")
print("1. Go to the challenge page where you downloaded the ZIP")
print("2. Look for large numbers labeled as n1, c1, n2, c2, n3, c3")
print("3. Provide those numbers and I'll solve it instantly")
print("\nOR")
print("Check if there's a netcat service: nc <host> <port>")
print("That might provide the RSA parameters")
