#!/usr/bin/env python3
"""
Decode by looking at visual patterns in bit positions
"""

import requests
import time
from xml.etree import ElementTree as ET

TARGET_URL = "http://138.199.163.92:12669/"
SECRET_KEY = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

print("="*60)
print("VISUAL DECODE")
print("="*60)

time.sleep(25)

print("\n[*] Fetching SVG...")
resp = requests.get(TARGET_URL + "svg.php", params={'secret': SECRET_KEY})

# Save it
with open('decoded_svg.svg', 'w', encoding='utf-8') as f:
    f.write(resp.text)

print("  Saved to decoded_svg.svg")

# Parse and create a visual grid
root = ET.fromstring(resp.text)
rects = root.findall('.//{http://www.w3.org/2000/svg}rect')

bits = []
for rect in rects:
    if rect.get('class') == 'bit':
        x = int(rect.get('x', 0))
        y = int(rect.get('y', 0))
        bits.append((x, y))

print(f"  Found {len(bits)} bit rectangles")

# Create a simple ASCII art representation
print("\n[*] Creating ASCII representation...")
print("  (Each 'X' represents a bit rectangle)")

# SVG is 324x324, let's make a 32x32 grid
grid_size = 32
cell_size = 324 // grid_size

grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]

for x, y in bits:
    grid_x = x // cell_size
    grid_y = y // cell_size
    if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size:
        grid[grid_y][grid_x] = 'X'

print()
for row in grid:
    print(''.join(row))

print("\n[!] Open 'decoded_svg.svg' in a browser to see the visual flag!")
print("="*60)
