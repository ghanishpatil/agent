#!/usr/bin/env python3
"""
Comprehensive final attempt for Beat The Clock CTF
Tries all promising decoding methods
"""

import requests
import re
import time
from collections import Counter

BASE_URL = "http://138.199.163.92:12669"
SECRET = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

def download_fresh_svg():
    """Download a fresh SVG"""
    print("[*] Downloading fresh SVG...")
    time.sleep(3)
    url = f"{BASE_URL}/svg.php?secret={SECRET}"
    resp = requests.get(url, timeout=10)
    return resp.text

def extract_elements(svg_content):
    """Extract all element types"""
    elements = {}
    
    for class_name in ['bit', 'ctrl', 'noise', 'junk', 'bg']:
        rects = re.findall(rf'<rect[^>]*class="{class_name}"[^>]*>', svg_content)
        
        items = []
        for rect in rects:
            x_match = re.search(r'x="(\d+)"', rect)
            y_match = re.search(r'y="(\d+)"', rect)
            k_match = re.search(r'data-k="(\d+)"', rect)
            fill_match = re.search(r'fill="([^"]+)"', rect)
            opacity_match = re.search(r'opacity="([\d.]+)"', rect)
            
            if x_match and y_match and k_match:
                items.append({
                    'x': int(x_match.group(1)),
                    'y': int(y_match.group(1)),
                    'k': int(k_match.group(1)),
                    'fill': fill_match.group(1) if fill_match else None,
                    'opacity': float(opacity_match.group(1)) if opacity_match else 0.5
                })
        
        elements[class_name] = items
    
    return elements

def try_all_methods(elements):
    """Try all decoding methods"""
    
    bits = elements['bit']
    bits.sort(key=lambda b: (b['y'], b['x']))
    
    print(f"\n[*] Total bit elements: {len(bits)}")
    
    methods = []
    
    # Method 1: Color-based binary (all bits)
    bit_string = []
    for bit in bits:
        fill = bit['fill'].lower() if bit['fill'] else ''
        if 'ff00' in fill or 'f000' in fill:
            bit_string.append('1')
        elif '00ff' in fill or '00dd' in fill or '00ee' in fill:
            bit_string.append('0')
    
    if len(bit_string) >= 8:
        decoded = ''
        for i in range(0, len(bit_string) - 7, 8):
            byte_str = ''.join(bit_string[i:i+8])
            byte_val = int(byte_str, 2)
            decoded += chr(byte_val) if byte_val != 0 else ''
        methods.append(('Color-based binary', decoded))
    
    # Method 2: High opacity bits only
    high_opacity_bits = [b for b in bits if b['opacity'] >= 0.85]
    high_opacity_bits.sort(key=lambda b: (b['y'], b['x']))
    
    bit_string2 = []
    for bit in high_opacity_bits:
        fill = bit['fill'].lower() if bit['fill'] else ''
        if 'ff00' in fill or 'f000' in fill:
            bit_string2.append('1')
        elif '00ff' in fill or '00dd' in fill:
            bit_string2.append('0')
    
    if len(bit_string2) >= 8:
        decoded2 = ''
        for i in range(0, len(bit_string2) - 7, 8):
            byte_str = ''.join(bit_string2[i:i+8])
            byte_val = int(byte_str, 2)
            decoded2 += chr(byte_val) if byte_val != 0 else ''
        methods.append(('High opacity (0.85+)', decoded2))
    
    # Method 3: data-k values directly
    decoded3 = ''.join(chr(b['k'] % 256) if 32 <= b['k'] % 256 < 127 else '' for b in bits)
    methods.append(('data-k mod 256', decoded3))
    
    # Method 4: XOR data-k with common keys
    for key in [0x4B, 0x61, 0x6C]:  # K, a, l
        decoded4 = ''.join(chr((b['k'] ^ key) % 256) if 32 <= (b['k'] ^ key) % 256 < 127 else '' for b in bits)
        if 'Kaal' in decoded4 or 'flag' in decoded4.lower():
            methods.append((f'data-k XOR {hex(key)}', decoded4))
    
    # Method 5: Only green bits (1s)
    green_bits = [b for b in bits if b['fill'] and ('ff00' in b['fill'].lower() or 'f000' in b['fill'].lower())]
    green_bits.sort(key=lambda b: (b['y'], b['x']))
    decoded5 = ''.join(chr(b['k'] % 256) if 32 <= b['k'] % 256 < 127 else '' for b in green_bits)
    methods.append(('Green bits only (k mod 256)', decoded5))
    
    # Method 6: Only blue bits (0s)
    blue_bits = [b for b in bits if b['fill'] and ('00ff' in b['fill'].lower() or '00dd' in b['fill'].lower())]
    blue_bits.sort(key=lambda b: (b['y'], b['x']))
    decoded6 = ''.join(chr(b['k'] % 256) if 32 <= b['k'] % 256 < 127 else '' for b in blue_bits)
    methods.append(('Blue bits only (k mod 256)', decoded6))
    
    # Check all methods for flag
    for method_name, decoded in methods:
        print(f"\n[{method_name}]")
        print(f"  Length: {len(decoded)}")
        print(f"  Preview: {decoded[:80]}")
        
        if "Kaal{" in decoded:
            flags = re.findall(r'Kaal\{[^}]+\}', decoded)
            for flag in flags:
                print(f"\n[+] FLAG FOUND: {flag}")
                return flag
    
    return None

def main():
    print("=" * 60)
    print("BEAT THE CLOCK - FINAL COMPREHENSIVE ATTEMPT")
    print("=" * 60)
    
    svg_content = download_fresh_svg()
    
    # Check for flag directly in response
    if "Kaal{" in svg_content:
        print("[+] FLAG FOUND DIRECTLY IN RESPONSE!")
        flags = re.findall(r'Kaal\{[^}]+\}', svg_content)
        for flag in flags:
            print(f"[+] FLAG: {flag}")
            return
    
    elements = extract_elements(svg_content)
    
    print(f"\n[*] Element counts:")
    for class_name, items in elements.items():
        print(f"  {class_name}: {len(items)}")
    
    flag = try_all_methods(elements)
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found with current methods")
        print("[!] This challenge may require:")
        print("    - Specific timing/clock synchronization")
        print("    - Multiple requests to assemble flag")
        print("    - Visual rendering of SVG")
        print("    - Different secret key or approach")

if __name__ == "__main__":
    main()
