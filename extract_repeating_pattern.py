#!/usr/bin/env python3
"""
BREAKTHROUGH: The audio has repeating patterns!
Extract the UNIQUE pattern from each file - that might be the RSA data!
"""

import wave
from Crypto.Util.number import long_to_bytes
import sys
sys.set_int_max_str_digits(100000)

print("="*70)
print("EXTRACTING REPEATING PATTERNS")
print("="*70)

def find_period(data, max_period=10000):
    """Find the repeating period in data"""
    for period in range(100, min(max_period, len(data)//2)):
        if data[:period] == data[period:period*2]:
            # Verify it repeats throughout
            is_repeating = True
            for i in range(0, len(data)-period, period):
                if data[i:i+period] != data[:period]:
                    is_repeating = False
                    break
            if is_repeating:
                return period
    return None

rsa_data = {}

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    
    print(f"\n{stone}:")
    
    with wave.open(filename, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        
        # Find the repeating period
        period = find_period(frames)
        
        if period:
            print(f"  Repeating period: {period} bytes")
            
            # Extract the unique pattern
            pattern = frames[:period]
            print(f"  Pattern length: {len(pattern)} bytes")
            
            # Convert to integer
            pattern_int = int.from_bytes(pattern, 'big')
            print(f"  As integer: {pattern_int}")
            print(f"  Bit length: {pattern_int.bit_length()}")
            
            # Try to decode as text
            try:
                text = long_to_bytes(pattern_int).decode('latin-1', errors='ignore')
                print(f"  As text (first 100 chars): {text[:100]}")
                
                if 'Kaal{' in text or 'kaal{' in text:
                    print(f"  *** FLAG FOUND: {text} ***")
            except:
                pass
            
            rsa_data[stone] = {
                'pattern': pattern,
                'pattern_int': pattern_int,
                'period': period
            }
        else:
            print(f"  No clear repeating period found")
            
            # Try fixed periods
            for test_period in [1000, 2000, 5000]:
                pattern = frames[:test_period]
                pattern_int = int.from_bytes(pattern, 'big')
                
                print(f"  Testing period {test_period}:")
                print(f"    As integer bit length: {pattern_int.bit_length()}")
                
                rsa_data[f"{stone}_{test_period}"] = pattern_int

# Now check if we have three values that could be ciphertexts
print("\n" + "="*70)
print("ATTEMPTING HÅSTAD'S ATTACK WITH EXTRACTED PATTERNS")
print("="*70)

if len(rsa_data) >= 3:
    print("We have patterns from all three files!")
    print("But we still need the moduli (n values)...")
    
    # Maybe the moduli are ALSO encoded in the files?
    # Or maybe they're derived from the file properties?
    
    print("\nPossibility: The numbers we found ARE the moduli!")
    print(f"n (from comment): 2157869541235478521545895")
    print(f"c (from secret): 83927465839274658392746583")
    
    # But we need THREE sets...
    # Maybe each file has its own hidden number?

print("\n" + "="*70)
print("CHECKING: Do ALL files have hidden ZIPs?")
print("="*70)
print("Let me check more carefully for hidden data in soul and time stones...")
