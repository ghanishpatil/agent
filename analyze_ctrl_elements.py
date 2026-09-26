#!/usr/bin/env python3
"""
Analyze 'ctrl' class elements - they might be control signals
"""

import re

def analyze_control_signals():
    """Extract and analyze ctrl elements"""
    
    with open('svg_response.svg', 'r') as f:
        svg_content = f.read()
    
    # Find all element types
    all_classes = re.findall(r'class="([^"]+)"', svg_content)
    class_counts = {}
    for cls in all_classes:
        class_counts[cls] = class_counts.get(cls, 0) + 1
    
    print("[*] Element class distribution:")
    for cls, count in sorted(class_counts.items()):
        print(f"  {cls}: {count}")
    
    # Extract ctrl elements
    ctrl_rects = re.findall(r'<rect[^>]*class="ctrl"[^>]*>', svg_content)
    print(f"\n[*] Found {len(ctrl_rects)} ctrl elements")
    
    ctrl_info = []
    for rect in ctrl_rects:
        x_match = re.search(r'x="(\d+)"', rect)
        y_match = re.search(r'y="(\d+)"', rect)
        k_match = re.search(r'data-k="(\d+)"', rect)
        
        if x_match and y_match and k_match:
            ctrl_info.append({
                'x': int(x_match.group(1)),
                'y': int(y_match.group(1)),
                'k': int(k_match.group(1))
            })
    
    ctrl_info.sort(key=lambda c: (c['y'], c['x']))
    
    print("\n[*] Ctrl elements (sorted):")
    for i, ctrl in enumerate(ctrl_info):
        print(f"  {i}: pos=({ctrl['x']},{ctrl['y']}), k={ctrl['k']}")
    
    # Maybe ctrl k values are indices or keys
    print(f"\n[*] Ctrl k values: {[c['k'] for c in ctrl_info]}")
    
    # Try using ctrl positions to filter bit elements
    print("\n[*] Extracting bits near ctrl elements...")
    
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
    
    # Check if ctrl elements mark rows/columns to extract
    ctrl_rows = set(c['y'] for c in ctrl_info)
    ctrl_cols = set(c['x'] for c in ctrl_info)
    
    print(f"[*] Ctrl rows: {sorted(ctrl_rows)}")
    print(f"[*] Ctrl cols: {sorted(ctrl_cols)}")
    
    # Extract bits in ctrl rows
    bits_in_ctrl_rows = [b for b in bits if b['y'] in ctrl_rows]
    print(f"\n[*] Bits in ctrl rows: {len(bits_in_ctrl_rows)}")
    
    if bits_in_ctrl_rows:
        bits_in_ctrl_rows.sort(key=lambda b: (b['y'], b['x']))
        
        # Decode
        bit_string = []
        for bit in bits_in_ctrl_rows:
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
            
            print(f"  Decoded from ctrl rows: {decoded}")
            
            if "Kaal{" in decoded:
                flags = re.findall(r'Kaal\{[^}]+\}', decoded)
                for flag in flags:
                    print(f"\n[+] FLAG FOUND: {flag}")
                    return flag
    
    return None

def main():
    print("=" * 60)
    print("Analyzing Control Elements")
    print("=" * 60)
    
    flag = analyze_control_signals()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found")

if __name__ == "__main__":
    main()
