#!/usr/bin/env python3
"""
Decode the signal from the SVG
"The signal is real" - focus on 'bit' class
"Most of what you see is not" - ignore noise, junk, bg, ctrl
"The clock does not care" - maybe ignore timing/order?
"""

from xml.etree import ElementTree as ET

# Read the saved SVG
with open('svg_output.svg', 'r', encoding='utf-8') as f:
    svg_content = f.read()

root = ET.fromstring(svg_content)
rects = root.findall('.//{http://www.w3.org/2000/svg}rect')

print("="*60)
print("DECODING THE SIGNAL")
print("="*60)

# Extract only 'bit' class (the signal)
bits = []
for rect in rects:
    if rect.get('class') == 'bit':
        data_k = int(rect.get('data-k', 0))
        x = int(rect.get('x', 0))
        y = int(rect.get('y', 0))
        fill = rect.get('fill', '')
        opacity = float(rect.get('opacity', 0))
        bits.append({
            'k': data_k,
            'x': x,
            'y': y,
            'fill': fill,
            'opacity': opacity
        })

print(f"\n[*] Found {len(bits)} signal bits")

# Try different sorting methods
print("\n[*] Method 1: Sort by data-k value")
sorted_by_k = sorted(bits, key=lambda b: b['k'])
k_values = [b['k'] for b in sorted_by_k]
print(f"  First 20 k values: {k_values[:20]}")

# Try ASCII decode
ascii_text = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_values)
print(f"  ASCII (mod 128): {ascii_text[:100]}")

# Try direct chr
ascii_text2 = ''.join(chr(k) if 32 <= k <= 126 else '.' for k in k_values if k < 256)
print(f"  ASCII (direct): {ascii_text2[:100]}")

# Method 2: Sort by position (reading order: top to bottom, left to right)
print("\n[*] Method 2: Sort by position (y, then x)")
sorted_by_pos = sorted(bits, key=lambda b: (b['y'], b['x']))
pos_k = [b['k'] for b in sorted_by_pos]
print(f"  First 20 k values: {pos_k[:20]}")

ascii_pos = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in pos_k)
print(f"  ASCII: {ascii_pos[:100]}")

# Method 3: Use opacity as binary
print("\n[*] Method 3: Opacity threshold")
high_opacity = [b for b in sorted_by_pos if b['opacity'] > 0.7]
print(f"  High opacity bits: {len(high_opacity)}")
high_k = [b['k'] for b in high_opacity]
ascii_high = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in high_k)
print(f"  ASCII: {ascii_high[:100]}")

# Method 4: Group by color
print("\n[*] Method 4: By color")
by_color = {}
for b in bits:
    color = b['fill']
    if color not in by_color:
        by_color[color] = []
    by_color[color].append(b)

for color, color_bits in sorted(by_color.items()):
    print(f"\n  Color {color}: {len(color_bits)} bits")
    sorted_color = sorted(color_bits, key=lambda b: b['k'])
    k_vals = [b['k'] for b in sorted_color]
    ascii_color = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_vals)
    print(f"    ASCII: {ascii_color[:80]}")
    
    # Try position sort
    sorted_color_pos = sorted(color_bits, key=lambda b: (b['y'], b['x']))
    k_vals_pos = [b['k'] for b in sorted_color_pos]
    ascii_color_pos = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_vals_pos)
    print(f"    ASCII (pos): {ascii_color_pos[:80]}")

# Method 5: XOR all k values
print("\n[*] Method 5: XOR analysis")
xor_result = 0
for b in bits:
    xor_result ^= b['k']
print(f"  XOR of all k values: {xor_result} (0x{xor_result:x})")
print(f"  As char: {chr(xor_result) if 32 <= xor_result <= 126 else '?'}")

# Method 6: Sum and modulo
print("\n[*] Method 6: Sum analysis")
total = sum(b['k'] for b in bits)
print(f"  Sum of all k values: {total}")
print(f"  Sum mod 256: {total % 256} -> {chr(total % 256) if 32 <= total % 256 <= 126 else '?'}")

# Method 7: Look for flag pattern in k values
print("\n[*] Method 7: Looking for 'Kaal{' pattern")
# K=75, a=97, l=108, {=123
target = [75, 97, 97, 108, 123]
for i in range(len(k_values) - 4):
    if k_values[i:i+5] == target:
        print(f"  Found 'Kaal{{' at index {i}!")
        print(f"  Following values: {k_values[i:i+50]}")

print("\n" + "="*60)
