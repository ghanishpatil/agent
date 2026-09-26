#!/usr/bin/env python3
"""
Extract the real signal from SVG noise
"""

import requests
import re
import time

BASE_URL = "http://138.199.163.92:12669"
SECRET = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

def analyze_svg_with_secret():
    """Download SVG with secret and extract signal"""
    print("[*] Downloading SVG with secret...")
    time.sleep(2)
    
    url = f"{BASE_URL}/svg.php?secret={SECRET}"
    resp = requests.get(url, timeout=10)
    
    print(f"[*] Response status: {resp.status_code}")
    print(f"[*] Response length: {len(resp.text)}")
    
    # Save for analysis
    with open('svg_response.svg', 'w') as f:
        f.write(resp.text)
    
    # Extract all rect elements
    all_rects = re.findall(r'<rect[^>]+>', resp.text)
    print(f"[*] Total rect elements: {len(all_rects)}")
    
    # Separate signal from noise
    signal_rects = [r for r in all_rects if 'class="signal"' in r]
    noise_rects = [r for r in all_rects if 'class="noise"' in r]
    
    print(f"[*] Signal rects: {len(signal_rects)}")
    print(f"[*] Noise rects: {len(noise_rects)}")
    
    if signal_rects:
        print("\n[*] Analyzing signal elements...")
        
        # Extract data-k values from signal elements
        signal_data = []
        for rect in signal_rects:
            match = re.search(r'data-k="(\d+)"', rect)
            if match:
                signal_data.append(int(match.group(1)))
        
        print(f"[*] Signal data-k values: {len(signal_data)}")
        
        if signal_data:
            # Try different decoding methods
            
            # Method 1: Direct ASCII (mod 256)
            try:
                decoded1 = ''.join(chr(val % 256) for val in signal_data)
                print(f"\n[Method 1] Direct ASCII (mod 256):")
                print(decoded1[:200])
                
                if "Kaal{" in decoded1:
                    flags = re.findall(r'Kaal\{[^}]+\}', decoded1)
                    for flag in flags:
                        print(f"\n[+] FLAG FOUND: {flag}")
                        return flag
            except:
                pass
            
            # Method 2: Divide by 100 (scale down)
            try:
                decoded2 = ''.join(chr(val // 100) for val in signal_data if val // 100 < 128)
                print(f"\n[Method 2] Divide by 100:")
                print(decoded2[:200])
                
                if "Kaal{" in decoded2:
                    flags = re.findall(r'Kaal\{[^}]+\}', decoded2)
                    for flag in flags:
                        print(f"\n[+] FLAG FOUND: {flag}")
                        return flag
            except:
                pass
            
            # Method 3: Extract position info
            print(f"\n[Method 3] Analyzing positions...")
            positions = []
            for rect in signal_rects:
                x_match = re.search(r'x="(\d+)"', rect)
                y_match = re.search(r'y="(\d+)"', rect)
                if x_match and y_match:
                    x = int(x_match.group(1))
                    y = int(y_match.group(1))
                    positions.append((x, y))
            
            print(f"[*] Signal positions: {len(positions)}")
            if positions:
                print(f"[*] First 10 positions: {positions[:10]}")
            
            # Method 4: Look at opacity patterns
            opacities = []
            for rect in signal_rects:
                op_match = re.search(r'opacity="([\d.]+)"', rect)
                if op_match:
                    opacities.append(float(op_match.group(1)))
            
            if opacities:
                print(f"\n[Method 4] Opacity analysis:")
                print(f"[*] Unique opacities: {sorted(set(opacities))}")
                
                # Try binary encoding based on opacity threshold
                threshold = 0.5
                bits = ''.join('1' if op > threshold else '0' for op in opacities)
                print(f"[*] Binary string (threshold {threshold}): {bits[:100]}")
                
                # Convert to ASCII
                try:
                    decoded4 = ''
                    for i in range(0, len(bits) - 7, 8):
                        byte = bits[i:i+8]
                        decoded4 += chr(int(byte, 2))
                    
                    print(f"[*] Decoded from opacity: {decoded4[:200]}")
                    
                    if "Kaal{" in decoded4:
                        flags = re.findall(r'Kaal\{[^}]+\}', decoded4)
                        for flag in flags:
                            print(f"\n[+] FLAG FOUND: {flag}")
                            return flag
                except:
                    pass
            
            # Method 5: Sort by position and extract
            print(f"\n[Method 5] Position-sorted extraction...")
            
            # Create list of (x, y, data-k) tuples
            signal_info = []
            for rect in signal_rects:
                x_match = re.search(r'x="(\d+)"', rect)
                y_match = re.search(r'y="(\d+)"', rect)
                k_match = re.search(r'data-k="(\d+)"', rect)
                
                if x_match and y_match and k_match:
                    x = int(x_match.group(1))
                    y = int(y_match.group(1))
                    k = int(k_match.group(1))
                    signal_info.append((x, y, k))
            
            # Sort by y, then x (row-major order)
            signal_info.sort(key=lambda t: (t[1], t[0]))
            
            sorted_data = [k for x, y, k in signal_info]
            print(f"[*] Sorted signal data: {len(sorted_data)} values")
            
            # Try decoding sorted data
            try:
                decoded5 = ''.join(chr(val % 256) for val in sorted_data)
                print(f"[*] Sorted decoded: {decoded5[:200]}")
                
                if "Kaal{" in decoded5:
                    flags = re.findall(r'Kaal\{[^}]+\}', decoded5)
                    for flag in flags:
                        print(f"\n[+] FLAG FOUND: {flag}")
                        return flag
            except:
                pass
    
    return None

def main():
    print("=" * 60)
    print("Beat The Clock - Signal Extraction")
    print("=" * 60)
    
    flag = analyze_svg_with_secret()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found in signal analysis")

if __name__ == "__main__":
    main()
