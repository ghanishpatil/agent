print("="*80)
print("DECODING LETTER PATTERNS FROM BOARD")
print("="*80)

# From the board analysis
black_letters = "bdfgabehbddh"
white_letters = "fhdcfgfhefh"
black_numbers = "888877776655"
white_numbers = "66433322111"

print(f"\nBlack letters: {black_letters}")
print(f"White letters: {white_letters}")
print(f"Black numbers: {black_numbers}")
print(f"White numbers: {white_numbers}")

# Try different combinations
print("\n[1. INTERLEAVED]")
interleaved = ''.join([b + w for b, w in zip(black_letters, white_letters)])
print(f"Interleaved: {interleaved}")

print("\n[2. CONCATENATED]")
concat = black_letters + white_letters
print(f"Concatenated: {concat}")

print("\n[3. FREQUENCY ANALYSIS]")
from collections import Counter
black_freq = Counter(black_letters)
white_freq = Counter(white_letters)
print(f"Black frequency: {black_freq}")
print(f"White frequency: {white_freq}")

print("\n[4. LETTER TO NUMBER]")
# a=1, b=2, etc.
black_nums = [ord(c) - ord('a') + 1 for c in black_letters]
white_nums = [ord(c) - ord('a') + 1 for c in white_letters]
print(f"Black as numbers: {black_nums}")
print(f"White as numbers: {white_nums}")

# Try as ASCII
black_ascii = ''.join([chr(n) if n < 127 else '.' for n in black_nums])
white_ascii = ''.join([chr(n) if n < 127 else '.' for n in white_nums])
print(f"Black ASCII: {black_ascii}")
print(f"White ASCII: {white_ascii}")

print("\n[5. CHESS MOVE SEQUENCE]")
# Maybe it's a sequence of moves
black_moves = ["b8", "d8", "f8", "g8", "a7", "b7", "e7", "h7", "b6", "d6", "d5", "h5"]
white_moves = ["f6", "h6", "d4", "c3", "f3", "g3", "f2", "h2", "e1", "f1", "h1"]

print(f"Black moves: {' '.join(black_moves)}")
print(f"White moves: {' '.join(white_moves)}")

# Check if this spells something
move_letters = ''.join([m[0] for m in black_moves + white_moves])
print(f"All move letters: {move_letters}")

print("\n[6. LOOKING FOR PATTERNS IN NUMBERS]")
# Black: 888877776655
# White: 66433322111

# Try reading as pairs
black_pairs = [black_numbers[i:i+2] for i in range(0, len(black_numbers), 2)]
white_pairs = [white_numbers[i:i+2] for i in range(0, len(white_numbers), 2)]
print(f"Black pairs: {black_pairs}")
print(f"White pairs: {white_pairs}")

# Convert to ASCII
black_pair_ascii = ''.join([chr(int(p)) if int(p) < 127 and int(p) > 31 else '.' for p in black_pairs])
white_pair_ascii = ''.join([chr(int(p)) if int(p) < 127 and int(p) > 31 else '.' for p in white_pairs])
print(f"Black pairs as ASCII: {black_pair_ascii}")
print(f"White pairs as ASCII: {white_pair_ascii}")

print("\n[7. UNIQUE POSITIONS]")
# Maybe only unique letters matter
black_unique = ''.join(dict.fromkeys(black_letters))
white_unique = ''.join(dict.fromkeys(white_letters))
print(f"Black unique: {black_unique}")
print(f"White unique: {white_unique}")

print("\n[8. DIFFERENCE/XOR OF LETTERS]")
# XOR the letter values
xor_result = []
for b, w in zip(black_letters, white_letters):
    xor_val = ord(b) ^ ord(w)
    xor_result.append(xor_val)

print(f"XOR values: {xor_result}")
xor_ascii = ''.join([chr(x) if 32 <= x <= 126 else '.' for x in xor_result])
print(f"XOR as ASCII: {xor_ascii}")

print("\n[9. CAESAR SHIFT]")
# Try different Caesar shifts
for shift in range(1, 26):
    shifted_black = ''.join([chr((ord(c) - ord('a') + shift) % 26 + ord('a')) for c in black_letters])
    shifted_white = ''.join([chr((ord(c) - ord('a') + shift) % 26 + ord('a')) for c in white_letters])
    
    if 'kaal' in shifted_black.lower() or 'flag' in shifted_black.lower():
        print(f"Shift {shift} - Black: {shifted_black}")
    if 'kaal' in shifted_white.lower() or 'flag' in shifted_white.lower():
        print(f"Shift {shift} - White: {shifted_white}")

print("\n[10. READING AS COORDINATES]")
# Combine letters and numbers
black_coords = list(zip(black_letters, black_numbers))
white_coords = list(zip(white_letters, white_numbers))
print(f"Black coords: {black_coords}")
print(f"White coords: {white_coords}")

# Maybe the answer is literally about who wins
print("\n[11. GAME ANALYSIS]")
print("Black pieces: 12")
print("White pieces: 11")
print("In Reversi/Othello: BLACK WINS")
print("\nPossible flags:")
print("  Kaal{black}")
print("  KAAL{BLACK}")
print("  Kaal{Black}")

print("\n" + "="*80)
