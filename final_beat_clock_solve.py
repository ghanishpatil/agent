#!/usr/bin/env python3
"""
Final solver - extract bits from color-coded rectangles
Green variants = 1, Blue variants = 0
"""

import re

def extract_flag_from_colors():
    """Extract flag from color-coded bit elements"""
    
    with open('svg_response.svg', 'r') as f:
        svg_content = f.read()
    
    # Find all rect elements with class="bit"
    bit_rects = re.findall(r'<rect[^>]*class="bit"[^>]*>', svg_content)
    
    print(f"[*] Found {len(bit_rects)} 'bit' elements")
    
    # Extract position, fill color for each bit
    bit_info = []
    for rect in bit_rects:
        x_match = re.search(r'x="(\d+)"', rect)
        y_match = re.search(r'y="(\d+)"', rect)
        fill_match = re.search(r'fill="([^"]+)"', rect)
        
        if x_match and y_match and fill_match:
            x = int(x_match.group(1))
            y = int(y_match.group(1))
            fill = fill_match.group(1)
            
            bit_info.append({
                'x': x,
                'y': y,
                'fill': fill
            })
    
    # Sort by position (row-major: y first, then x)
    bit_info.sort(key=lambda b: (b['y'], b['x']))
    
    print(f"[*] Sorted {len(bit_info)} bit elements")
    
    # Extract bits based on color
    # Green (#00ff00, #00f000, etc.) = 1
    # Blue (#0000ff, #0000dd, etc.) = 0
    
    bits = []
    for bit in bit_info:
        fill = bit['fill'].lower()
        
        # Check if green (has 'ff' or 'f0' in middle positions)
        if 'ff00' in fill or 'f000' in fill:  # Green variants
            bits.append('1')
        elif '00ff' in fill or '00dd' in fill or '00ee' in fill:  # Blue variants
            bits.append('0')
        else:
            print(f"[!] Unknown color: {fill}")
    
    print(f"[*] Extracted {len(bits)} bits")
    print(f"[*] Bit string (first 100): {''.join(bits[:100])}")
    
    # Convert bits to ASCII
    decoded = ''
    for i in range(0, len(bits) - 7, 8):
        byte_str = ''.join(bits[i:i+8])
        byte_val = int(byte_str, 2)
        
        # Only add printable characters
        if 32 <= byte_val <= 126:
            decoded += chr(byte_val)
        else:
            decoded += f'[{byte_val:02x}]'
    
    print(f"\n[*] Decoded message:")
    print(decoded)
    
    # Look for flag
    if "Kaal{" in decoded:
        flags = re.findall(r'Kaal\{[^}]+\}', decoded)
        for flag in flags:
            print(f"\n[+] FLAG FOUND: {flag}")
            return flag
    
    # Try without filtering non-printable
    decoded_raw = ''
    for i in range(0, len(bits) - 7, 8):
        byte_str = ''.join(bits[i:i+8])
        byte_val = int(byte_str, 2)
        decoded_raw += chr(byte_val)
    
    print(f"\n[*] Raw decoded (with non-printable):")
    print(repr(decoded_raw))
    
    if "Kaal{" in decoded_raw:
        flags = re.findall(r'Kaal\{[^}]+\}', decoded_raw)
        for flag in flags:
            print(f"\n[+] FLAG FOUND: {flag}")
            return flag
    
    return None

def main():
    print("=" * 60)
    print("Beat The Clock - Final Solve")
    print("=" * 60)
    
    flag = extract_flag_from_colors()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found")

if __name__ == "__main__":
    main()
