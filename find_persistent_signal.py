#!/usr/bin/env python3
"""
Download multiple SVG responses and find the persistent signal
The "clock does not care" - find what doesn't change
"""

import requests
import re
import time
from collections import Counter

BASE_URL = "http://138.199.163.92:12669"
SECRET = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

def download_svg():
    """Download one SVG response"""
    url = f"{BASE_URL}/svg.php?secret={SECRET}"
    resp = requests.get(url, timeout=10)
    return resp.text

def extract_bit_elements(svg_content):
    """Extract all bit class elements with their properties"""
    bit_rects = re.findall(r'<rect[^>]*class="bit"[^>]*>', svg_content)
    
    bits = []
    for rect in bit_rects:
        x_match = re.search(r'x="(\d+)"', rect)
        y_match = re.search(r'y="(\d+)"', rect)
        fill_match = re.search(r'fill="([^"]+)"', rect)
        k_match = re.search(r'data-k="(\d+)"', rect)
        
        if x_match and y_match and fill_match:
            x = int(x_match.group(1))
            y = int(y_match.group(1))
            fill = fill_match.group(1)
            k = int(k_match.group(1)) if k_match else None
            
            # Create a unique identifier for this bit position
            bit_id = f"{x},{y}"
            
            bits.append({
                'id': bit_id,
                'x': x,
                'y': y,
                'fill': fill,
                'k': k
            })
    
    return bits

def find_persistent_bits(num_samples=5):
    """Download multiple SVGs and find bits that appear consistently"""
    
    print(f"[*] Downloading {num_samples} SVG samples...")
    
    all_samples = []
    for i in range(num_samples):
        print(f"[*] Sample {i+1}/{num_samples}...")
        svg = download_svg()
        bits = extract_bit_elements(svg)
        all_samples.append(bits)
        
        print(f"    Found {len(bits)} bit elements")
        
        if i < num_samples - 1:
            time.sleep(3)  # Avoid rate limit
    
    # Find bits that appear in ALL samples
    print(f"\n[*] Analyzing persistent bits...")
    
    # Get all bit IDs from first sample
    first_sample_ids = {bit['id'] for bit in all_samples[0]}
    
    # Find IDs that appear in all samples
    persistent_ids = first_sample_ids.copy()
    for sample in all_samples[1:]:
        sample_ids = {bit['id'] for bit in sample}
        persistent_ids &= sample_ids
    
    print(f"[*] Persistent bit positions: {len(persistent_ids)}")
    
    if not persistent_ids:
        print("[!] No persistent bits found!")
        return None
    
    # Extract persistent bits from first sample (they should be the same in all)
    persistent_bits = [bit for bit in all_samples[0] if bit['id'] in persistent_ids]
    
    # Sort by position
    persistent_bits.sort(key=lambda b: (b['y'], b['x']))
    
    print(f"\n[*] Persistent bits (sorted by position):")
    for i, bit in enumerate(persistent_bits[:10]):
        print(f"  {i}: x={bit['x']}, y={bit['y']}, fill={bit['fill']}, k={bit['k']}")
    
    # Extract flag from persistent bits
    bits_string = []
    for bit in persistent_bits:
        fill = bit['fill'].lower()
        
        # Green = 1, Blue = 0
        if 'ff00' in fill or 'f000' in fill:  # Green
            bits_string.append('1')
        elif '00ff' in fill or '00dd' in fill or '00ee' in fill:  # Blue
            bits_string.append('0')
    
    print(f"\n[*] Extracted {len(bits_string)} bits from persistent signal")
    print(f"[*] Bit string: {''.join(bits_string)}")
    
    # Convert to ASCII
    decoded = ''
    for i in range(0, len(bits_string) - 7, 8):
        byte_str = ''.join(bits_string[i:i+8])
        byte_val = int(byte_str, 2)
        decoded += chr(byte_val)
    
    print(f"\n[*] Decoded message:")
    print(decoded)
    print(repr(decoded))
    
    # Look for flag
    if "Kaal{" in decoded:
        flags = re.findall(r'Kaal\{[^}]+\}', decoded)
        for flag in flags:
            print(f"\n[+] FLAG FOUND: {flag}")
            return flag
    
    return None

def main():
    print("=" * 60)
    print("Finding Persistent Signal (Clock-Independent)")
    print("=" * 60)
    
    flag = find_persistent_bits(num_samples=3)
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found in persistent signal")

if __name__ == "__main__":
    main()
