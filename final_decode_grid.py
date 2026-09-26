#!/usr/bin/env python3
"""
Use the X-Secret to decode the bonus grid
"""

# The grid from the screenshot (best transcription)
grid = [
    ['4', 'E', 'A', 'U', 'I', 'D', 'H', 'O', 'N', '8'],
    ['3', 'I', 'S', 'O', 'A', 'R', 'Y', '7', 'O', '7'],
    ['4', 'B', 'T', 'S', 'W', 'I', 'T', 'C', 'M', '2'],
    ['5', '6', 'P', 'U', 'M', 'P', 'K', 'I', 'N', '1'],
    ['8', 'R', 'S', 'O', 'Z', 'M', 'R', 'T', '1', '0'],
    ['8', '9', 'G', 'H', 'Q', 'S', 'T', '8', '9', '3'],
    ['3', 'I', '3', '2', '8', '6', 'R', 'Q', '1', '1'],
    ['H', 'A', 'U', 'N', 'I', 'E', 'D', '4', '8', '8'],
]

secret = "38h4vg6s45ch1lr19x4pe18s55r2kh1lx5331mh1mc5656w0"

print("="*60)
print("Decoding Grid with X-Secret")
print("="*60)

# The secret might be telling us which cells to read
# Format could be: row-col pairs

# Extract all characters from secret
chars = list(secret)

print(f"\nSecret: {secret}")
print(f"Secret length: {len(secret)}")

# Try interpreting as row,col pairs
print("\n[*] Method 1: Sequential pairs as (row, col)")
result1 = []
i = 0
while i < len(chars) - 1:
    try:
        row_char = chars[i]
        col_char = chars[i+1]
        
        # Try to convert to indices
        if row_char.isdigit() and col_char.isdigit():
            row = int(row_char)
            col = int(col_char)
            
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                cell_value = grid[row][col]
                result1.append(cell_value)
                print(f"  ({row},{col}) -> {cell_value}")
        
        i += 2
    except:
        i += 1

decoded1 = ''.join(result1)
print(f"\nDecoded method 1: {decoded1}")

if 'kaal{' in decoded1.lower():
    print(f"[!!!] FLAG FOUND: {decoded1}")

# Try method 2: Use letters as row indicators, numbers as columns
print("\n[*] Method 2: Letters=rows (a=0,b=1...), numbers=cols")
result2 = []

for char in chars:
    if char.isalpha():
        # This might be a row indicator
        row = ord(char.lower()) - ord('a')
        if row < len(grid):
            # Next number is column?
            pass
    elif char.isdigit():
        # This might be a column
        pass

# Try method 3: The secret itself might spell coordinates when decoded
print("\n[*] Method 3: Decode secret as cipher")

# Maybe the numbers in the secret are indices into the alphabet?
print("\n[*] Method 4: Numbers as alphabet indices")
result4 = []
for char in secret:
    if char.isdigit():
        idx = int(char)
        if idx > 0 and idx <= 26:
            result4.append(chr(ord('a') + idx - 1))

decoded4 = ''.join(result4)
print(f"Decoded as alphabet: {decoded4}")

if 'kaal' in decoded4:
    print(f"[!!!] FOUND KAAL!")

# Try reading the grid in a specific pattern
print("\n[*] Method 5: Read grid diagonally, spirally, etc.")

# Diagonal
diagonal = []
for i in range(min(len(grid), len(grid[0]))):
    diagonal.append(grid[i][i])

print(f"Diagonal: {''.join(diagonal)}")

# Try all rows
print("\n[*] All grid rows:")
for i, row in enumerate(grid):
    row_str = ''.join(str(c) for c in row)
    print(f"Row {i}: {row_str}")
    if 'kaal' in row_str.lower():
        print(f"  [!!!] FOUND KAAL IN ROW {i}!")

# Try all columns
print("\n[*] All grid columns:")
for col in range(len(grid[0])):
    col_str = ''.join(str(grid[row][col]) for row in range(len(grid)))
    print(f"Col {col}: {col_str}")
    if 'kaal' in col_str.lower():
        print(f"  [!!!] FOUND KAAL IN COL {col}!")

print("\n" + "="*60)
print("Analysis complete")
print("="*60)
