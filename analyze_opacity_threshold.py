#!/usr/bin/env python3
"""
Analyze opacity values - maybe high opacity = real signal
"""

import re

def analyze_by_opacity():
    """Extract bits with high opacity (real signal)"""
    
    with open('svg_response.svg', 'r') as f:
        svg_content = f.read()
    
    # Find all bit elements
    bit_rects = re.findall(r'<rect[^>]*class="bit"[^>]*>', svg_content)
    
    print(f"[*] Found {len(bit_rects)} bit elements")
    
    # Extract all info including opacity
    bits = []
    for rect in bit_rects:
        x_match = re.search(r'x="(\d+)"', rect)
        y_match = re.search(r'y="(\d+)"', rect)
        k_match = re.search(r'data-k="(\d+)"', rect)
        fill_match = re.search(r'fill="([^"]+)"', rect)
        opacity_match = re.search(r'opacity="([\d.]+)"', rect)
        
        if x_match and y_match and k_match and opacity_match:
            bits.append({
                'x': int(x_match.group(1)),
                'y': int(y_match.group(1)),
                'k': int(k_match.group(1)),
                'fill': fill_match.group(1) if fill_match else None,
                'opacity': float(opacity_match.group(1))
            })
    
    # Analyze opacity distribution
    opacities = [b['opacity'] for b in bits]
    print(f"\n[*] Opacity statistics:")
    print(f"  Min: {min(opacities):.2f}, Max: {max(opacities):.2f}")
    print(f"  Mean: {sum(opacities)/len(opacities):.2f}")
    
    # Try different thresholds
    for threshold in [0.7, 0.75, 0.8, 0.85, 0.9]:
        high_opacity_bits = [b for b in bits if b['opacity'] >= threshold]
        print(f"\n[Threshold {threshold}] {len(high_opacity_bits)} high-opacity bits")
        
        if len(high_opacity_bits) == 0:
            continue
        
        # Sort by position
        high_opacity_bits.sort(key=lambda b: (b['y'], b['x']))
        
        # Extract color-based bits
        bit_string = []
        for bit in high_opacity_bits:
            fill = bit['fill'].lower() if bit['fill'] else ''
            
            if 'ff00' in fill or 'f000' in fill:  # Green
                bit_string.append('1')
            elif '00ff' in fill or '00dd' in fill:  # Blue
                bit_string.append('0')
        
        if len(bit_string) >= 8:
            # Convert to ASCII
            decoded = ''
            for i in range(0, len(bit_string) - 7, 8):
                byte_str = ''.join(bit_string[i:i+8])
                byte_val = int(byte_str, 2)
                if 32 <= byte_val < 127:
                    decoded += chr(byte_val)
                else:
                    decoded += '?'
            
            print(f"  Decoded: {decoded}")
            
            if "Kaal{" in decoded:
                flags = re.findall(r'Kaal\{[^}]+\}', decoded)
                for flag in flags:
                    print(f"\n[+] FLAG FOUND: {flag}")
                    return flag
    
    # Try extracting data-k from high opacity bits
    print(f"\n[*] Trying data-k from high opacity bits (threshold 0.8)...")
    high_bits = [b for b in bits if b['opacity'] >= 0.8]
    high_bits.sort(key=lambda b: (b['y'], b['x']))
    
    decoded_k = ''.join(chr(b['k'] % 256) if 32 <= b['k'] % 256 < 127 else '?' for b in high_bits)
    print(f"  Decoded from k: {decoded_k[:100]}")
    
    if "Kaal{" in decoded_k:
        flags = re.findall(r'Kaal\{[^}]+\}', decoded_k)
        for flag in flags:
            print(f"\n[+] FLAG FOUND: {flag}")
            return flag
    
    return None

def main():
    print("=" * 60)
    print("Analyzing Opacity Threshold")
    print("=" * 60)
    
    flag = analyze_by_opacity()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found")

if __name__ == "__main__":
    main()
