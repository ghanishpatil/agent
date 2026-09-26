from PIL import Image
import numpy as np

print("="*80)
print("FINAL BOARD SOLVE ATTEMPT")
print("="*80)

# The pairs from numbers were interesting: XXMMB7 for black
# Let me check if there's more to extract

img = Image.open("board.png")
pixels = np.array(img.convert('RGB'))

grid_size = 8
cell_size = 90

# Get exact piece positions with more detail
pieces_data = []

for row in range(grid_size):
    for col in range(grid_size):
        y = row * cell_size + cell_size // 2
        x = col * cell_size + cell_size // 2
        
        region = pixels[y-30:y+30, x-30:x+30, :]
        min_brightness = np.min(np.mean(region, axis=2))
        avg_brightness = np.mean(region)
        
        if min_brightness < 100:
            piece_type = 'B' if min_brightness < 40 else 'W'
            pos = f"{chr(97+col)}{8-row}"
            
            # Get exact RGB values at center
            center_rgb = pixels[y, x, :]
            
            pieces_data.append({
                'pos': pos,
                'type': piece_type,
                'min_bright': min_brightness,
                'avg_bright': avg_brightness,
                'rgb': center_rgb,
                'row': row,
                'col': col
            })

print(f"\nFound {len(pieces_data)} pieces")

# Check if RGB values encode something
print("\n[CHECKING RGB VALUES]")
for piece in pieces_data[:5]:  # First 5
    print(f"{piece['pos']} ({piece['type']}): RGB={piece['rgb']}, Min={piece['min_bright']:.1f}")

# Try reading the numbers in different ways
black_positions = [p for p in pieces_data if p['type'] == 'B']
white_positions = [p for p in pieces_data if p['type'] == 'W']

print(f"\nBlack: {[p['pos'] for p in black_positions]}")
print(f"White: {[p['pos'] for p in white_positions]}")

# The number pattern was: Black 888877776655, White 66433322111
# As pairs: Black XXMMB7, White B+!...

print("\n[ANALYZING NUMBER PAIRS]")
black_nums = "888877776655"
white_nums = "66433322111"

# Try as hex
try:
    black_hex = bytes.fromhex(black_nums)
    print(f"Black as hex: {black_hex}")
except:
    pass

# Try different groupings
print("\nBlack number groupings:")
print(f"  Pairs: {[black_nums[i:i+2] for i in range(0, len(black_nums), 2)]}")
print(f"  Triples: {[black_nums[i:i+3] for i in range(0, len(black_nums), 3)]}")

# As ASCII codes
black_ascii_pairs = ''.join([chr(int(black_nums[i:i+2])) for i in range(0, len(black_nums)-1, 2)])
print(f"  As ASCII: {repr(black_ascii_pairs)}")

print("\nWhite number groupings:")
print(f"  Pairs: {[white_nums[i:i+2] for i in range(0, len(white_nums), 2)]}")

# Check if this is a known chess puzzle
print("\n[CHECKING FOR KNOWN PATTERNS]")

# FEN notation
fen_rows = []
for row in range(8):
    fen_row = ""
    empty_count = 0
    for col in range(8):
        piece = None
        for p in pieces_data:
            if p['row'] == row and p['col'] == col:
                piece = p['type']
                break
        
        if piece:
            if empty_count > 0:
                fen_row += str(empty_count)
                empty_count = 0
            fen_row += piece.lower() if piece == 'B' else piece
        else:
            empty_count += 1
    
    if empty_count > 0:
        fen_row += str(empty_count)
    fen_rows.append(fen_row)

fen = '/'.join(fen_rows)
print(f"\nFEN notation: {fen}")

# Maybe the FEN or position encodes the flag
import hashlib
fen_hash = hashlib.md5(fen.encode()).hexdigest()
print(f"FEN MD5: {fen_hash}")

# Check if it's a specific endgame
print("\n[ENDGAME ANALYSIS]")
print(f"Material: Black={len(black_positions)}, White={len(white_positions)}")
print("Black has 1 more piece")

# In many board games, having more pieces = winning
print("\nConclusion: BLACK WINS (more pieces)")

# Generate all possible flag formats
possible_flags = [
    "Kaal{black}",
    "KAAL{BLACK}",
    "Kaal{Black}",
    "KAAL{black}",
    "Kaal{BLACK}",
    "KAAL{Black}",
    "Kaal{b}",
    "KAAL{B}",
    "Kaal{blackwins}",
    "Kaal{black_wins}",
    "KAAL{BLACKWINS}",
]

print("\nAll possible flag formats to try:")
for i, flag in enumerate(possible_flags, 1):
    print(f"{i:2}. {flag}")

print("\n" + "="*80)
print("RECOMMENDATION: Try Kaal{black} first (matches previous flag format)")
print("="*80)
