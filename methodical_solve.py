#!/usr/bin/env python3
"""
METHODICAL STEP-BY-STEP SOLUTION
Hint: "When the exponent is small, the message doesn't stay hidden for long"
This means: Håstad's Broadcast Attack with e=3

The THREE stones represent THREE encryptions of the SAME message with e=3
"""

from Crypto.Util.number import long_to_bytes
import sys
sys.set_int_max_str_digits(100000)

print("="*70)
print("STEP 1: Understanding the Challenge")
print("="*70)
print("Håstad's Broadcast Attack:")
print("- Same message M encrypted 3 times")
print("- Small exponent e (typically 3)")
print("- Three different moduli: n1, n2, n3")
print("- Three ciphertexts: c1, c2, c3")
print("- If M^3 < n1*n2*n3, we can recover M directly!")

print("\n" + "="*70)
print("STEP 2: What We Found")
print("="*70)
print("From mind_stone_3rd.wav:")
print("  - Hidden ZIP password: 2157869541235478521545895")
print("  - Secret in ZIP: 83927465839274658392746583")
print("\nFrom soul_stone_1st.wav: 'e=7' (might be misdirection)")
print("From time_stone_2nd.wav: 'e=9' (might be misdirection)")

print("\n" + "="*70)
print("STEP 3: Key Insight")
print("="*70)
print("The hint says 'THREE fragments' and 'REPETITION was intentional'")
print("Maybe each WAV file CONTAINS its own n and c values!")
print("Let me check if there are THREE sets of hidden data...")

# Check each file for hidden ZIPs or appended data
import struct
import zipfile
import os

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    print(f"\n{stone}:")
    
    with open(filename, 'rb') as f:
        data = f.read()
        
        # Check for RIFF size vs actual size
        riff_size = struct.unpack('<I', data[4:8])[0]
        actual_size = len(data)
        expected_size = riff_size + 8
        
        print(f"  Expected size: {expected_size}")
        print(f"  Actual size: {actual_size}")
        
        if actual_size > expected_size:
            extra_bytes = actual_size - expected_size
            print(f"  *** EXTRA DATA: {extra_bytes} bytes ***")
            
            # Extract extra data
            extra = data[expected_size:]
            print(f"  First 100 bytes: {extra[:100]}")
            
            # Check if it's a ZIP
            if b'PK' in extra:
                print(f"  Contains ZIP file!")
                
                # Try to extract
                # First, get any number before the ZIP
                lines = extra.split(b'\n', 1)
                if lines[0].strip().isdigit():
                    number = lines[0].decode('ascii').strip()
                    print(f"  Number before ZIP: {number}")
                    
                    # Save and extract ZIP
                    zip_data = lines[1] if len(lines) > 1 else extra[extra.find(b'PK'):]
                    zip_filename = f'{stone}_hidden.zip'
                    
                    with open(zip_filename, 'wb') as zf:
                        zf.write(zip_data)
                    
                    # Try to extract with the number as password
                    try:
                        with zipfile.ZipFile(zip_filename, 'r') as zf:
                            zf.extractall(f'{stone}_extracted', pwd=number.encode())
                            print(f"  Extracted ZIP with password: {number}")
                            
                            # Read contents
                            for name in zf.namelist():
                                with open(f'{stone}_extracted/{name}', 'r') as f:
                                    content = f.read()
                                    print(f"  {name}: {content}")
                    except Exception as e:
                        print(f"  Error extracting: {e}")
        else:
            print(f"  No extra data")

print("\n" + "="*70)
print("STEP 4: If we have THREE (n, c) pairs, solve with Håstad")
print("="*70)
