#!/usr/bin/env python3
"""
Use the robots.txt hint: q355q636678723p4
Maybe q and p are parameters, and the numbers are indices/keys
"""

from xml.etree import ElementTree as ET

# Read the saved SVG
with open('svg_output.svg', 'r', encoding='utf-8') as f:
    svg_content = f.read()

root = ET.fromstring(svg_content)
rects = root.findall('.//{http://www.w3.org/2000/svg}rect')

print("="*60)
print("USING ROBOTS.TXT HINT: q355q636678723p4")
print("="*60)

# Parse the hint
# Could be: q=355, q=636, 678723, p=4
# Or: indices 355, 636, 678723, 4

# Extract all bits
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

# Sort by position
sorted_bits = sorted(bits, key=lambda b: (b['y'], b['x']))

# Try using the numbers as indices
indices = [355, 636, 678723, 4]
print("\n[*] Method 1: Using as indices into sorted bits")
for idx in indices:
    if idx < len(sorted_bits):
        bit = sorted_bits[idx]
        print(f"  Index {idx}: k={bit['k']}, chr={chr(bit['k']) if 32 <= bit['k'] <= 126 else '?'}")

# Try using as data-k values to filter
print("\n[*] Method 2: Filter by data-k values")
target_k = [355, 636, 678723, 4]
for k_val in target_k:
    matching = [b for b in bits if b['k'] == k_val]
    if matching:
        print(f"  k={k_val}: Found {len(matching)} bits")
        for b in matching:
            print(f"    pos=({b['x']},{b['y']}), fill={b['fill']}, opacity={b['opacity']}")

# Try modulo operations
print("\n[*] Method 3: Using hint numbers with modulo")
# 678723 is large - maybe it's a key or seed
seed = 678723
print(f"  Seed: {seed}")

# Try XOR with seed
result = []
for b in sorted_bits[:100]:  # First 100 bits
    val = b['k'] ^ (seed % 10000)
    if 32 <= val <= 126:
        result.append(chr(val))
    else:
        result.append('.')
print(f"  XOR result: {''.join(result)}")

# Try different interpretation: q and p might be quadrant and position
print("\n[*] Method 4: Quadrant interpretation")
# q=355 might mean quadrant 3, position 55
# q=636 might mean quadrant 6, position 36
# p=4 might mean pattern 4

# Let's look at the grid structure
# SVG is 324x324, so maybe 36x36 grid of 9x9 cells?
print(f"  SVG dimensions: 324x324")
print(f"  Possible grid: 36x36 cells")

# Try extracting bits at specific positions
positions = [(355, 636), (636, 355), (4, 4)]
print("\n[*] Method 5: Looking for bits at specific coordinates")
for px, py in positions:
    nearby = [b for b in bits if abs(b['x'] - px) < 10 and abs(b['y'] - py) < 10]
    if nearby:
        print(f"  Near ({px},{py}): {len(nearby)} bits")
        for b in nearby:
            print(f"    k={b['k']}, chr={chr(b['k']) if 32 <= b['k'] <= 126 else '?'}")

# Try base conversion
print("\n[*] Method 6: Number analysis")
numbers = [355, 636, 678723, 4]
print(f"  Numbers: {numbers}")
print(f"  Sum: {sum(numbers)}")
print(f"  Product: {355 * 636 * 4}")  # Skip the large one
print(f"  678723 in hex: 0x{678723:x}")
print(f"  678723 in binary: {bin(678723)}")

# Maybe it's telling us to look at every Nth bit
print("\n[*] Method 7: Stride pattern")
for stride in [355, 636, 4]:
    if stride < len(sorted_bits):
        selected = sorted_bits[::stride]
        k_vals = [b['k'] for b in selected]
        text = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_vals)
        print(f"  Every {stride}th bit: {text[:50]}")

print("\n" + "="*60)
