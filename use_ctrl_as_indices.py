#!/usr/bin/env python3
"""
Use ctrl data-k values as indices into bit array
"""

import re

def use_ctrl_as_selector():
    """Use ctrl k values to select specific bits"""
    
    with open('svg_response.svg', 'r') as f:
        svg_content = f.read()
    
    # Extract all bits
    bit_rects = re.findall(r'<rect[^>]*class="bit"[^>]*>', svg_content)
    
    bits = []
    for rect in bit_rects:
        x_match = re.search(r'x="(\d+)"', rect)
        y_match = re.search(r'y="(\d+)"', rect)
        k_match = re.search(r'data-k="(\d+)"', rect)
        fill_match = re.search(r'fill="([^"]+)"', rect)
        
        if x_match and y_match and k_match:
            bits.append({
                'x': int(x_match.group(1)),
                'y': int(y_match.group(1)),
                'k': int(k_match.group(1)),
                'fill': fill_match.group(1) if fill_match else None
            })
    
    # Sort bits by position
    bits.sort(key=lambda b: (b['y'], b['x']))
    
    print(f"[*] Total bits: {len(bits)}")
    
    # Extract ctrl elements
    ctrl_rects = re.findall(r'<rect[^>]*class="ctrl"[^>]*>', svg_content)
    
    ctrl_k_values = []
    for rect in ctrl_rects:
        k_match = re.search(r'data-k="(\d+)"', rect)
        if k_match:
            ctrl_k_values.append(int(k_match.group(1)))
    
    print(f"[*] Ctrl k values: {len(ctrl_k_values)}")
    
    # Try using ctrl k values as indices (mod len(bits))
    print("\n[Method 1] Using ctrl k as indices into bit array:")
    selected_bits = []
    for k in ctrl_k_values:
        idx = k % len(bits)
        selected_bits.append(bits[idx])
    
    # Decode selected bits
    bit_string = []
    for bit in selected_bits:
        fill = bit['fill'].lower() if bit['fill'] else ''
        if 'ff00' in fill or 'f000' in fill:
            bit_string.append('1')
        elif '00ff' in fill or '00dd' in fill:
            bit_string.append('0')
    
    if len(bit_string) >= 8:
        decoded = ''
        for i in range(0, len(bit_string) - 7, 8):
            byte_str = ''.join(bit_string[i:i+8])
            byte_val = int(byte_str, 2)
            decoded += chr(byte_val) if 32 <= byte_val < 127 else '?'
        
        print(f"  Decoded: {decoded}")
        
        if "Kaal{" in decoded:
            flags = re.findall(r'Kaal\{[^}]+\}', decoded)
            for flag in flags:
                print(f"\n[+] FLAG FOUND: {flag}")
                return flag
    
    # Try using ctrl k // 100 as indices
    print("\n[Method 2] Using ctrl k // 100 as indices:")
    selected_bits2 = []
    for k in ctrl_k_values:
        idx = (k // 100) % len(bits)
        selected_bits2.append(bits[idx])
    
    bit_string2 = []
    for bit in selected_bits2:
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
            decoded2 += chr(byte_val) if 32 <= byte_val < 127 else '?'
        
        print(f"  Decoded: {decoded2}")
        
        if "Kaal{" in decoded2:
            flags = re.findall(r'Kaal\{[^}]+\}', decoded2)
            for flag in flags:
                print(f"\n[+] FLAG FOUND: {flag}")
                return flag
    
    # Try decoding ctrl k values directly
    print("\n[Method 3] Decoding ctrl k values directly:")
    decoded3 = ''.join(chr(k % 256) if 32 <= k % 256 < 127 else '?' for k in ctrl_k_values)
    print(f"  Decoded: {decoded3}")
    
    if "Kaal{" in decoded3:
        flags = re.findall(r'Kaal\{[^}]+\}', decoded3)
        for flag in flags:
            print(f"\n[+] FLAG FOUND: {flag}")
            return flag
    
    return None

def main():
    print("=" * 60)
    print("Using Ctrl as Selector/Index")
    print("=" * 60)
    
    flag = use_ctrl_as_selector()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found")

if __name__ == "__main__":
    main()
