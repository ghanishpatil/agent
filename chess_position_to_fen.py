from PIL import Image
import numpy as np

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("CHESS POSITION ANALYSIS")
print("="*80)

img = Image.open(image_path)
pixels = np.array(img.convert('RGB'))

grid_size = 8
cell_size = 90

# Build board representation
board = [[None for _ in range(8)] for _ in range(8)]

for row in range(grid_size):
    for col in range(grid_size):
        y = row * cell_size + cell_size // 2
        x = col * cell_size + cell_size // 2
        
        region = pixels[y-30:y+30, x-30:x+30, :]
        brightness_map = np.mean(region, axis=2)
        min_brightness = np.min(brightness_map)
        
        if min_brightness < 100:
            if min_brightness < 40:
                board[row][col] = 'b'  # black piece
            else:
                board[row][col] = 'w'  # white piece

# Print board
print("\nBoard (row 8 at top, row 1 at bottom):")
print("  a  b  c  d  e  f  g  h")
for row in range(8):
    print(f"{8-row} ", end="")
    for col in range(8):
        piece = board[row][col]
        if piece == 'b':
            print(" B ", end="")
        elif piece == 'w':
            print(" W ", end="")
        else:
            print(" . ", end="")
    print(f" {8-row}")
print("  a  b  c  d  e  f  g  h")

# Analyze the position
print("\n[POSITION ANALYSIS]")

# Count pieces by row
for row in range(8):
    black_count = sum(1 for c in board[row] if c == 'b')
    white_count = sum(1 for c in board[row] if c == 'w')
    print(f"Row {8-row}: {black_count} black, {white_count} white")

# This looks like it might be a checkers/draughts game, not chess
# In checkers, pieces move diagonally
# Let's check if this is checkers

print("\n[CHECKING IF THIS IS CHECKERS/DRAUGHTS]")
print("In checkers:")
print("- Pieces only occupy dark squares")
print("- Pieces move diagonally")
print("- Game is won by capturing all opponent pieces or blocking them")

# Check if pieces are only on dark squares
# In chess notation, dark squares are where (file + rank) is odd
# a1=odd, a2=even, b1=even, b2=odd, etc.

pieces_on_dark = 0
pieces_on_light = 0

for row in range(8):
    for col in range(8):
        if board[row][col] is not None:
            # row 0 = rank 8, row 7 = rank 1
            rank = 8 - row
            file_num = col + 1
            
            # Dark square if (file + rank) is even (in standard chess board orientation)
            # Actually, a1 is dark, so (col + row) even = dark
            is_dark = (col + row) % 2 == 1
            
            if is_dark:
                pieces_on_dark += 1
            else:
                pieces_on_light += 1

print(f"\nPieces on dark squares: {pieces_on_dark}")
print(f"Pieces on light squares: {pieces_on_light}")

if pieces_on_light == 0:
    print("\nThis is CHECKERS/DRAUGHTS! All pieces are on dark squares.")
    
    # In checkers, analyze who can move
    print("\n[CHECKERS ANALYSIS]")
    
    # Black pieces (top): b8, d8, f8, g8, a7, b7, e7, h7, b6, d6, d5, h5
    # White pieces (bottom): f6, h6, d4, c3, f3, g3, f2, h2, e1, f1, h1
    
    # In checkers, pieces move forward diagonally
    # Black moves down (toward row 1)
    # White moves up (toward row 8)
    
    # Check if either side is blocked
    black_can_move = False
    white_can_move = False
    
    # Check black pieces
    for row in range(8):
        for col in range(8):
            if board[row][col] == 'b':
                # Check if can move down-left or down-right
                if row < 7:  # Not on bottom row
                    if col > 0 and board[row+1][col-1] is None:
                        black_can_move = True
                    if col < 7 and board[row+1][col+1] is None:
                        black_can_move = True
    
    # Check white pieces
    for row in range(8):
        for col in range(8):
            if board[row][col] == 'w':
                # Check if can move up-left or up-right
                if row > 0:  # Not on top row
                    if col > 0 and board[row-1][col-1] is None:
                        white_can_move = True
                    if col < 7 and board[row-1][col+1] is None:
                        white_can_move = True
    
    print(f"Black can move: {black_can_move}")
    print(f"White can move: {white_can_move}")
    
    if not black_can_move and white_can_move:
        print("\n*** WHITE WINS! Black is blocked. ***")
        winner = "WHITE"
    elif not white_can_move and black_can_move:
        print("\n*** BLACK WINS! White is blocked. ***")
        winner = "BLACK"
    elif not black_can_move and not white_can_move:
        print("\n*** DRAW! Both sides are blocked. ***")
        winner = "DRAW"
    else:
        # Count pieces
        black_count = sum(1 for row in board for c in row if c == 'b')
        white_count = sum(1 for row in board for c in row if c == 'w')
        print(f"\nBoth sides can move. Material: Black={black_count}, White={white_count}")
        if black_count > white_count:
            print("Black has material advantage")
            winner = "BLACK"
        elif white_count > black_count:
            print("White has material advantage")
            winner = "WHITE"
        else:
            winner = "UNKNOWN"
    
    print(f"\n{'='*80}")
    print(f"WINNER: {winner}")
    print(f"{'='*80}")
    
    # Try flag formats
    possible_flags = [
        f"KAAL{{{winner}}}",
        f"KAAL{{{winner.lower()}}}",
        f"KAAL{{{winner.capitalize()}}}",
        f"Kaal{{{winner}}}",
        f"Kaal{{{winner.lower()}}}",
    ]
    
    print("\nPossible flag formats:")
    for flag in possible_flags:
        print(f"  {flag}")

print("\n" + "="*80)
