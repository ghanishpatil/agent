from PIL import Image
import numpy as np
import hashlib

print("="*80)
print("ADVANCED BOARD POSITION DECODING")
print("="*80)

img = Image.open("board.png")
pixels = np.array(img.convert('RGB'))

# Extract board state
grid_size = 8
cell_size = 90
board = [[None for _ in range(8)] for _ in range(8)]

for row in range(grid_size):
    for col in range(grid_size):
        y = row * cell_size + cell_size // 2
        x = col * cell_size + cell_size // 2
        region = pixels[y-30:y+30, x-30:x+30, :]
        min_brightness = np.min(np.mean(region, axis=2))
        
        if min_brightness < 100:
            board[row][col] = 'B' if min_brightness < 40 else 'W'

# Print board
print("\nBoard:")
for row in range(8):
    print(f"{8-row} ", end="")
    for col in range(8):
        piece = board[row][col]
        print(f" {piece if piece else '.'} ", end="")
    print()
print("  a  b  c  d  e  f  g  h")

# Try different encoding schemes
print("\n[1. POSITION AS BINARY]")
# Each square is a bit: piece=1, empty=0
binary_str = ''.join(['1' if board[r][c] else '0' for r in range(8) for c in range(8)])
print(f"Binary: {binary_str}")

# Convert to ASCII
ascii_result = []
for i in range(0, len(binary_str), 8):
    byte = binary_str[i:i+8]
    if len(byte) == 8:
        char_code = int(byte, 2)
        if 32 <= char_code <= 126:
            ascii_result.append(chr(char_code))
        else:
            ascii_result.append('.')

ascii_text = ''.join(ascii_result)
print(f"As ASCII: {ascii_text}")
if 'KAAL' in ascii_text or 'FLAG' in ascii_text:
    print(f"*** FOUND: {ascii_text} ***")

# Try reverse
binary_str_rev = binary_str[::-1]
ascii_result_rev = []
for i in range(0, len(binary_str_rev), 8):
    byte = binary_str_rev[i:i+8]
    if len(byte) == 8:
        char_code = int(byte, 2)
        if 32 <= char_code <= 126:
            ascii_result_rev.append(chr(char_code))
        else:
            ascii_result_rev.append('.')
ascii_text_rev = ''.join(ascii_result_rev)
print(f"Reversed: {ascii_text_rev}")

print("\n[2. BLACK vs WHITE ENCODING]")
# Black=1, White=0, Empty=skip
black_white_binary = ''.join(['1' if board[r][c] == 'B' else '0' if board[r][c] == 'W' else '' 
                               for r in range(8) for c in range(8)])
print(f"Black/White binary: {black_white_binary}")

# Convert to ASCII
if len(black_white_binary) >= 8:
    ascii_bw = []
    for i in range(0, len(black_white_binary) - 7, 8):
        byte = black_white_binary[i:i+8]
        char_code = int(byte, 2)
        if 32 <= char_code <= 126:
            ascii_bw.append(chr(char_code))
        else:
            ascii_bw.append('.')
    ascii_bw_text = ''.join(ascii_bw)
    print(f"As ASCII: {ascii_bw_text}")
    if 'KAAL' in ascii_bw_text:
        print(f"*** FOUND: {ascii_bw_text} ***")

print("\n[3. POSITION COORDINATES AS VALUES]")
# Convert piece positions to numbers
black_positions = []
white_positions = []

for row in range(8):
    for col in range(8):
        if board[row][col] == 'B':
            black_positions.append(row * 8 + col)
        elif board[row][col] == 'W':
            white_positions.append(row * 8 + col)

print(f"Black positions: {black_positions}")
print(f"White positions: {white_positions}")

# Try as ASCII
black_ascii = ''.join([chr(p) if 32 <= p <= 126 else '.' for p in black_positions])
white_ascii = ''.join([chr(p) if 32 <= p <= 126 else '.' for p in white_positions])
print(f"Black as ASCII: {black_ascii}")
print(f"White as ASCII: {white_ascii}")

# Try XOR
if len(black_positions) == len(white_positions):
    xor_vals = [b ^ w for b, w in zip(black_positions, white_positions)]
    xor_ascii = ''.join([chr(x) if 32 <= x <= 126 else '.' for x in xor_vals])
    print(f"XOR as ASCII: {xor_ascii}")

print("\n[4. CHESS NOTATION ENCODING]")
# Convert to algebraic notation
black_squares = []
white_squares = []

for row in range(8):
    for col in range(8):
        if board[row][col] == 'B':
            black_squares.append(f"{chr(97+col)}{8-row}")
        elif board[row][col] == 'W':
            white_squares.append(f"{chr(97+col)}{8-row}")

print(f"Black: {', '.join(black_squares)}")
print(f"White: {', '.join(white_squares)}")

# Try first letters
black_letters = ''.join([s[0] for s in black_squares])
white_letters = ''.join([s[0] for s in white_squares])
print(f"Black first letters: {black_letters}")
print(f"White first letters: {white_letters}")

# Try numbers
black_numbers = ''.join([s[1] for s in black_squares])
white_numbers = ''.join([s[1] for s in white_squares])
print(f"Black numbers: {black_numbers}")
print(f"White numbers: {white_numbers}")

print("\n[5. HASH OF POSITION]")
# Maybe the position hash is the answer
position_str = ''.join(['B' if board[r][c] == 'B' else 'W' if board[r][c] == 'W' else '.' 
                        for r in range(8) for c in range(8)])
print(f"Position string: {position_str}")

md5_hash = hashlib.md5(position_str.encode()).hexdigest()
sha1_hash = hashlib.sha1(position_str.encode()).hexdigest()
print(f"MD5: {md5_hash}")
print(f"SHA1: {sha1_hash}")

# Try as flag
possible_flags = [
    f"KAAL{{{md5_hash}}}",
    f"KAAL{{{md5_hash[:8]}}}",
    f"KAAL{{{sha1_hash[:8]}}}",
]
print("\nPossible hash-based flags:")
for flag in possible_flags:
    print(f"  {flag}")

print("\n[6. READING DIAGONALS]")
# Try reading diagonals
diag1 = [board[i][i] for i in range(8)]
diag2 = [board[i][7-i] for i in range(8)]
print(f"Main diagonal: {diag1}")
print(f"Anti-diagonal: {diag2}")

print("\n" + "="*80)
