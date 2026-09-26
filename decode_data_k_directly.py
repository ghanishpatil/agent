#!/usr/bin/env python3
"""
Try decoding data-k values directly as character codes
Maybe they encode the flag when sorted by position
"""

import re

def decode_from_data_k():
    """Extract and decode data-k from bit elements"""
    
    with open('svg_response.svg', 'r') as f:
        svg_content = f.read()
    
    # Find all bit elements
    bit_rects = re.findall(r'<rect[^>]*class="bit"[^>]*>', svg_content)
    
    print(f"[*] Found {len(bit_rects)} bit elements")
    
    # Extract all info
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
    
    # Sort by position
    bits.sort(key=lambda b: (b['y'], b['x']))
    
    print(f"\n[*] First 20 sorted bits:")
    for i, bit in enumerate(bits[:20]):
        char = chr(bit['k'] % 256) if bit['k'] % 256 >= 32 and bit['k'] % 256 < 127 else '?'
        print(f"  {i}: pos=({bit['x']},{bit['y']}), k={bit['k']}, k%256={bit['k']%256} ('{char}'), fill={bit['fill']}")
    
    # Try different decoding methods
    
    # Method 1: k % 256
    decoded1 = ''.join(chr(b['k'] % 256) for b in bits)
    print(f"\n[Method 1] k % 256:")
    print(repr(decoded1[:100]))
    
    # Method 2: k % 128 (7-bit ASCII)
    decoded2 = ''.join(chr(b['k'] % 128) if b['k'] % 128 >= 32 else '?' for b in bits)
    print(f"\n[Method 2] k % 128:")
    print(decoded2[:100])
    
    # Method 3: k // 100 (scale down)
    decoded3 = ''.join(chr(b['k'] // 100) if 32 <= b['k'] // 100 < 127 else '?' for b in bits)
    print(f"\n[Method 3] k // 100:")
    print(decoded3[:100])
    
    # Method 4: Look for patterns in k values
    k_values = [b['k'] for b in bits]
    print(f"\n[Method 4] K value statistics:")
    print(f"  Min: {min(k_values)}, Max: {max(k_values)}")
    print(f"  Range suggests: {max(k_values) // 256 + 1} possible bytes per value")
    
    # Method 5: Maybe k encodes position in alphabet or flag
    # Try XOR with a key
    for key in [0x42, 0x4B, 0x61, 0x6B]:  # B, K, a, k
        decoded5 = ''.join(chr((b['k'] ^ key) % 256) if 32 <= (b['k'] ^ key) % 256 < 127 else '?' for b in bits)
        if 'Kaal' in decoded5 or 'flag' in decoded5.lower():
            print(f"\n[Method 5] XOR with {hex(key)}:")
            print(decoded5[:100])
    
    # Check all decoded strings for flag
    for method, decoded in [('1', decoded1), ('2', decoded2), ('3', decoded3)]:
        if "Kaal{" in decoded:
            flags = re.findall(r'Kaal\{[^}]+\}', decoded)
            for flag in flags:
                print(f"\n[+] FLAG FOUND in Method {method}: {flag}")
                return flag
    
    return None

def main():
    print("=" * 60)
    print("Decoding data-k Values Directly")
    print("=" * 60)
    
    flag = decode_from_data_k()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found")

if __name__ == "__main__":
    main()
