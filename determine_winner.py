from PIL import Image
import numpy as np

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("CHESS BOARD - DETERMINING WINNER")
print("="*80)

img = Image.open(image_path)
pixels = np.array(img.convert('RGB'))

grid_size = 8
cell_size = 90

# Analyze each square more carefully
board = []
for row in range(grid_size):
    row_data = []
    for col in range(grid_size):
        y = row * cell_size + cell_size // 2
        x = col * cell_size + cell_size // 2
        
        # Sample larger region
        region = pixels[y-30:y+30, x-30:x+30, :]
        
        # Get min brightness (darkest point = piece)
        brightness_map = np.mean(region, axis=2)
        min_brightness = np.min(brightness_map)
        avg_brightness = np.mean(brightness_map)
        
        # Determine piece presence and color
        has_piece = min_brightness < 100
        
        if has_piece:
            # Dark pieces (black) have min brightness ~32-33
            # Light pieces (white) have min brightness ~52-57
            if min_brightness < 40:
                piece_color = 'BLACK'
            else:
                piece_color = 'WHITE'
        else:
            piece_color = None
        
        pos = f"{chr(97+col)}{8-row}"
        row_data.append({
            'pos': pos,
            'piece': piece_color,
            'min_bright': min_brightness,
            'avg_bright': avg_brightness
        })
    board.append(row_data)

# Print board with colors
print("\nBoard State:")
print("  a    b    c    d    e    f    g    h")
for row_idx, row in enumerate(board):
    print(f"{8-row_idx} ", end="")
    for cell in row:
        if cell['piece'] == 'BLACK':
            print("[ B ]", end="")
        elif cell['piece'] == 'WHITE':
            print("[ W ]", end="")
        else:
            print("[   ]", end="")
    print(f" {8-row_idx}")
print("  a    b    c    d    e    f    g    h")

# Count pieces
black_pieces = []
white_pieces = []

for row in board:
    for cell in row:
        if cell['piece'] == 'BLACK':
            black_pieces.append(cell['pos'])
        elif cell['piece'] == 'WHITE':
            white_pieces.append(cell['pos'])

print(f"\nBLACK pieces ({len(black_pieces)}): {', '.join(black_pieces)}")
print(f"WHITE pieces ({len(white_pieces)}): {', '.join(white_pieces)}")

# Analyze position
print("\n[POSITION ANALYSIS]")

# Check for checkmate patterns
# Look at piece positions to determine game state

# White pieces are on: f6, h6, d4, c3, f3, g3, f2, h2, e1, f1, h1
# Black pieces are on: b8, d8, f8, g8, a7, b7, e7, h7, b6, d6, d5, h5

# Typically in chess:
# - Row 1 is white's back rank
# - Row 8 is black's back rank
# - White pieces on rows 1-4 suggests white is defending/attacking
# - Black pieces on rows 5-8 suggests black is attacking

print("\nWhite pieces distribution:")
print(f"  Back rank (1): {[p for p in white_pieces if p.endswith('1')]}")
print(f"  Rows 2-4: {[p for p in white_pieces if p[-1] in '234']}")
print(f"  Rows 5-8: {[p for p in white_pieces if p[-1] in '5678']}")

print("\nBlack pieces distribution:")
print(f"  Back rank (8): {[p for p in black_pieces if p.endswith('8')]}")
print(f"  Rows 5-7: {[p for p in black_pieces if p[-1] in '567']}")
print(f"  Rows 1-4: {[p for p in black_pieces if p[-1] in '1234']}")

# Check for king positions (usually on e1 for white, e8 for black)
# Or look for checkmate patterns

print("\n[CHECKING FOR CHECKMATE/STALEMATE]")
# In a typical endgame, if one side has significantly more pieces or better position

# Material count (rough estimate - all pieces counted equally here)
print(f"Material: Black={len(black_pieces)}, White={len(white_pieces)}")

if len(black_pieces) > len(white_pieces):
    print("Black has material advantage")
elif len(white_pieces) > len(black_pieces):
    print("White has material advantage")
else:
    print("Material is equal")

# Check if this is a specific endgame pattern
# Look for king positions
white_king_candidates = [p for p in white_pieces if p in ['e1', 'f1', 'g1', 'h1']]
black_king_candidates = [p for p in black_pieces if p in ['e8', 'd8', 'f8', 'g8']]

print(f"\nPossible white king: {white_king_candidates}")
print(f"Possible black king: {black_king_candidates}")

# Try to determine winner based on position
print("\n" + "="*80)
print("ANALYSIS:")
print("This appears to be a chess endgame position.")
print("To determine the winner, we need to analyze the exact position.")
print("\nLet me check if there's hidden data that tells us the winner...")
print("="*80)

# Check for steganography in specific patterns
# Maybe the answer is encoded in the piece positions themselves

# Convert positions to numbers
def pos_to_num(pos):
    col = ord(pos[0]) - ord('a')  # 0-7
    row = int(pos[1]) - 1  # 0-7
    return row * 8 + col

black_nums = sorted([pos_to_num(p) for p in black_pieces])
white_nums = sorted([pos_to_num(p) for p in white_pieces])

print(f"\nBlack piece positions as numbers: {black_nums}")
print(f"White piece positions as numbers: {white_nums}")

# Check if these numbers spell something
# Or check for ASCII patterns
black_chars = ''.join([chr(n) if 32 <= n <= 126 else '.' for n in black_nums])
white_chars = ''.join([chr(n) if 32 <= n <= 126 else '.' for n in white_nums])

print(f"\nBlack as ASCII: {black_chars}")
print(f"White as ASCII: {white_chars}")

# Try XOR or other combinations
xor_result = []
for i in range(min(len(black_nums), len(white_nums))):
    xor_result.append(black_nums[i] ^ white_nums[i])

print(f"\nXOR of positions: {xor_result}")
xor_chars = ''.join([chr(n) if 32 <= n <= 126 else '.' for n in xor_result])
print(f"XOR as ASCII: {xor_chars}")

print("\n" + "="*80)
