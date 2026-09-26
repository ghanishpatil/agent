#!/usr/bin/env python3
"""
Extract 'bit' class elements from SVG - these are the real signal
"""

import re

def extract_bit_signal():
    """Extract bit class elements and decode"""
    
    with open('svg_response.svg', 'r') as f:
        svg_content = f.read()
    
    # Find all rect elements with class="bit"
    bit_rects = re.findall(r'<rect[^>]*class="bit"[^>]*>', svg_content)
    
    print(f"[*] Found {len(bit_rects)} 'bit' elements")
    
    if not bit_rects:
        print("[!] No bit elements found")
        return
    
    # Extract position and data-k for each bit
    bit_info = []
    for rect in bit_rects:
        x_match = re.search(r'x="(\d+)"', rect)
        y_match = re.search(r'y="(\d+)"', rect)
        k_match = re.search(r'data-k="(\d+)"', rect)
        fill_match = re.search(r'fill="([^"]+)"', rect)
        
        if x_match and y_match and k_match:
            x = int(x_match.group(1))
            y = int(y_match.group(1))
            k = int(k_match.group(1))
            fill = fill_match.group(1) if fill_match else None
            
            bit_info.append({
                'x': x,
                'y': y,
                'k': k,
                'fill': fill,
                'rect': rect
            })
    
    print(f"\n[*] Bit elements extracted: {len(bit_info)}")
    
    # Sort by position (row-major: y first, then x)
    bit_info.sort(key=lambda b: (b['y'], b['x']))
    
    print("\n[*] First 10 bit elements (sorted):")
    for i, bit in enumerate(bit_info[:10]):
        print(f"  {i}: x={bit['x']}, y={bit['y']}, k={bit['k']}, fill={bit['fill']}")
    
    # Method 1: Decode data-k values as ASCII
    print("\n[Method 1] Decoding data-k as ASCII:")
    decoded1 = ''.join(chr(b['k'] % 256) for b in bit_info)
    print(decoded1)
    
    if "Kaal{" in decoded1:
        flags = re.findall(r'Kaal\{[^}]+\}', decoded1)
        for flag in flags:
            print(f"\n[+] FLAG FOUND: {flag}")
            return flag
    
    # Method 2: Use fill color as binary (green=#00ff00 or similar)
    print("\n[Method 2] Analyzing fill colors:")
    colors = [b['fill'] for b in bit_info]
    unique_colors = set(colors)
    print(f"[*] Unique colors: {unique_colors}")
    
    # RGB colors might encode bits
    # #00ff00 = green, #0000ff = blue, #ff0000 = red
    # Maybe: green=1, blue=0, red=control?
    
    # Try extracting bits based on color
    bits = []
    for bit in bit_info:
        if bit['fill'] == '#00ff00' or 'ff00' in bit['fill']:  # Green
            bits.append('1')
        elif bit['fill'] == '#0000ff' or '00ff' in bit['fill']:  # Blue
            bits.append('0')
        else:
            # Skip control/other colors
            pass
    
    print(f"[*] Extracted {len(bits)} bits from colors")
    print(f"[*] Bit string: {' '.join(bits)}")
    
    if len(bits) >= 8:
        # Convert to ASCII
        decoded2 = ''
        for i in range(0, len(bits) - 7, 8):
            byte = ''.join(bits[i:i+8])
            decoded2 += chr(int(byte, 2))
        
        print(f"[*] Decoded from color bits: {decoded2}")
        
        if "Kaal{" in decoded2:
            flags = re.findall(r'Kaal\{[^}]+\}', decoded2)
            for flag in flags:
                print(f"\n[+] FLAG FOUND: {flag}")
                return flag
    
    # Method 3: Look at data-k values more carefully
    print("\n[Method 3] Analyzing data-k values:")
    k_values = [b['k'] for b in bit_info]
    print(f"[*] K values: {k_values}")
    
    # Try different interpretations
    # Maybe k values are ASCII codes directly
    decoded3 = ''.join(chr(k) if k < 128 else '?' for k in k_values)
    print(f"[*] Direct ASCII: {decoded3}")
    
    if "Kaal{" in decoded3:
        flags = re.findall(r'Kaal\{[^}]+\}', decoded3)
        for flag in flags:
            print(f"\n[+] FLAG FOUND: {flag}")
            return flag
    
    # Method 4: Check if k values encode positions or indices
    print("\n[Method 4] Checking for patterns in k values:")
    
    # Maybe the k values themselves form the message when sorted
    sorted_k = sorted(k_values)
    print(f"[*] Sorted k values: {sorted_k[:20]}")
    
    # Or maybe we need to look at the LSB of k values
    lsb_bits = [str(k & 1) for k in k_values]
    print(f"[*] LSB of k values: {''.join(lsb_bits)}")
    
    if len(lsb_bits) >= 8:
        decoded4 = ''
        for i in range(0, len(lsb_bits) - 7, 8):
            byte = ''.join(lsb_bits[i:i+8])
            decoded4 += chr(int(byte, 2))
        
        print(f"[*] Decoded from LSB: {decoded4[:100]}")
        
        if "Kaal{" in decoded4:
            flags = re.findall(r'Kaal\{[^}]+\}', decoded4)
            for flag in flags:
                print(f"\n[+] FLAG FOUND: {flag}")
                return flag
    
    return None

def main():
    print("=" * 60)
    print("Extracting 'bit' Signal from SVG")
    print("=" * 60)
    
    flag = extract_bit_signal()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found. Need more analysis.")

if __name__ == "__main__":
    main()
