from PIL import Image
import numpy as np

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("GAME STATE ANALYSIS - WHO WINS?")
print("="*80)

img = Image.open(image_path)
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
print("\nBoard Position:")
print("  a  b  c  d  e  f  g  h")
for row in range(8):
    print(f"{8-row} ", end="")
    for col in range(8):
        piece = board[row][col]
        print(f" {piece if piece else '.'} ", end="")
    print(f" {8-row}")
print("  a  b  c  d  e  f  g  h")

# List all pieces
black_pieces = []
white_pieces = []
for row in range(8):
    for col in range(8):
        if board[row][col] == 'B':
            black_pieces.append(f"{chr(97+col)}{8-row}")
        elif board[row][col] == 'W':
            white_pieces.append(f"{chr(97+col)}{8-row}")

print(f"\nBlack ({len(black_pieces)}): {', '.join(sorted(black_pieces))}")
print(f"White ({len(white_pieces)}): {', '.join(sorted(white_pieces))}")

# Analyze as different game types
print("\n" + "="*80)
print("ANALYSIS AS DIFFERENT GAME TYPES")
print("="*80)

# 1. CHESS
print("\n[1. CHESS ANALYSIS]")
print("If this is chess, we need to identify piece types and check for checkmate.")
print("Without knowing piece types, we can only count material.")
print(f"Material count: Black={len(black_pieces)}, White={len(white_pieces)}")

# 2. CHECKERS/DRAUGHTS
print("\n[2. CHECKERS ANALYSIS]")
# Check mobility
black_moves = 0
white_moves = 0

for row in range(8):
    for col in range(8):
        if board[row][col] == 'B':
            # Black moves down (increasing row)
            if row < 7:
                if col > 0 and board[row+1][col-1] is None:
                    black_moves += 1
                if col < 7 and board[row+1][col+1] is None:
                    black_moves += 1
        elif board[row][col] == 'W':
            # White moves up (decreasing row)
            if row > 0:
                if col > 0 and board[row-1][col-1] is None:
                    white_moves += 1
                if col < 7 and board[row-1][col+1] is None:
                    white_moves += 1

print(f"Black possible moves: {black_moves}")
print(f"White possible moves: {white_moves}")

if black_moves == 0 and white_moves > 0:
    print("=> WHITE WINS (Black has no moves)")
    winner = "WHITE"
elif white_moves == 0 and black_moves > 0:
    print("=> BLACK WINS (White has no moves)")
    winner = "BLACK"
elif black_moves == 0 and white_moves == 0:
    print("=> DRAW (No moves for either side)")
    winner = "DRAW"
else:
    print("=> Game continues (both sides have moves)")
    winner = None

# 3. REVERSI/OTHELLO
print("\n[3. REVERSI/OTHELLO ANALYSIS]")
print("In Reversi, the player with more pieces wins.")
if len(black_pieces) > len(white_pieces):
    print(f"=> BLACK WINS ({len(black_pieces)} vs {len(white_pieces)})")
    reversi_winner = "BLACK"
elif len(white_pieces) > len(black_pieces):
    print(f"=> WHITE WINS ({len(white_pieces)} vs {len(black_pieces)})")
    reversi_winner = "WHITE"
else:
    print(f"=> DRAW ({len(black_pieces)} vs {len(white_pieces)})")
    reversi_winner = "DRAW"

# 4. GO
print("\n[4. GO ANALYSIS]")
print("In Go, we'd need to count territory, not just pieces.")
print("This doesn't look like a Go board (wrong piece distribution).")

# Try to determine the most likely game type
print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

if winner:
    print(f"\nMost likely answer: {winner}")
    
    # Generate possible flag formats
    possible_flags = [
        f"KAAL{{{winner}}}",
        f"KAAL{{{winner.lower()}}}",
        f"Kaal{{{winner}}}",
        f"Kaal{{{winner.lower()}}}",
        f"KAAL{{{winner.capitalize()}}}",
    ]
    
    print("\nPossible flags:")
    for flag in possible_flags:
        print(f"  {flag}")
else:
    print("\nCannot determine winner from position alone.")
    print("Trying Reversi/Othello logic:")
    print(f"  Winner: {reversi_winner}")
    
    possible_flags = [
        f"KAAL{{{reversi_winner}}}",
        f"KAAL{{{reversi_winner.lower()}}}",
        f"Kaal{{{reversi_winner}}}",
        f"Kaal{{{reversi_winner.lower()}}}",
    ]
    
    print("\nPossible flags:")
    for flag in possible_flags:
        print(f"  {flag}")

# Also check if the piece positions themselves encode something
print("\n[CHECKING IF POSITIONS ENCODE DATA]")
# Convert positions to binary
black_binary = ''.join(['1' if board[r][c] == 'B' else '0' for r in range(8) for c in range(8)])
white_binary = ''.join(['1' if board[r][c] == 'W' else '0' for r in range(8) for c in range(8)])

print(f"\nBlack as binary: {black_binary}")
print(f"White as binary: {white_binary}")

# Try to decode as ASCII
def binary_to_ascii(binary_str):
    result = []
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        if len(byte) == 8:
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:
                result.append(chr(char_code))
            else:
                result.append('.')
    return ''.join(result)

black_ascii = binary_to_ascii(black_binary)
white_ascii = binary_to_ascii(white_binary)

print(f"Black as ASCII: {black_ascii}")
print(f"White as ASCII: {white_ascii}")

if 'KAAL' in black_ascii or 'FLAG' in black_ascii:
    print(f"*** FOUND IN BLACK: {black_ascii} ***")
if 'KAAL' in white_ascii or 'FLAG' in white_ascii:
    print(f"*** FOUND IN WHITE: {white_ascii} ***")

print("\n" + "="*80)
