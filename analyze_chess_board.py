from PIL import Image
import numpy as np

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("CHESS BOARD ANALYSIS - Who Wins?")
print("="*80)

img = Image.open(image_path)
img_rgb = img.convert('RGB')
pixels = np.array(img_rgb)

print(f"\nImage: {img.size[0]}x{img.size[1]}")

# Chess board is 8x8
grid_size = 8
cell_size = 720 // grid_size  # 90 pixels per cell

print(f"\nAnalyzing as {grid_size}x{grid_size} chess board (cell size: {cell_size}x{cell_size})")

# Analyze each square
board_state = []
for row in range(grid_size):
    row_data = []
    for col in range(grid_size):
        # Sample center of each cell
        y = row * cell_size + cell_size // 2
        x = col * cell_size + cell_size // 2
        
        # Get a small region around center
        region = pixels[y-10:y+10, x-10:x+10, :]
        avg_color = np.mean(region, axis=(0,1))
        
        # Determine if square is light or dark
        brightness = np.mean(avg_color)
        is_light = brightness > 150
        
        # Check for pieces (darker spots on squares)
        min_brightness = np.min(np.mean(region, axis=2))
        has_piece = min_brightness < 100
        
        row_data.append({
            'pos': f"{chr(97+col)}{8-row}",  # Chess notation (a1-h8)
            'color': 'light' if is_light else 'dark',
            'avg_brightness': brightness,
            'min_brightness': min_brightness,
            'has_piece': has_piece
        })
    board_state.append(row_data)

# Print board state
print("\nBoard State (from white's perspective):")
print("  a    b    c    d    e    f    g    h")
for row_idx, row in enumerate(board_state):
    print(f"{8-row_idx} ", end="")
    for cell in row:
        if cell['has_piece']:
            print("[ X ]", end="")
        else:
            print("[   ]", end="")
    print(f" {8-row_idx}")
print("  a    b    c    d    e    f    g    h")

# Count pieces
piece_count = sum(1 for row in board_state for cell in row if cell['has_piece'])
print(f"\nTotal pieces detected: {piece_count}")

# List all squares with pieces
print("\nSquares with pieces:")
for row in board_state:
    for cell in row:
        if cell['has_piece']:
            print(f"  {cell['pos']}: brightness={cell['min_brightness']:.1f}")

# Try to extract text from image using different methods
print("\n[CHECKING FOR HIDDEN TEXT]")

# Check if there's text overlay
from PIL import ImageEnhance, ImageFilter

# Enhance contrast
enhancer = ImageEnhance.Contrast(img_rgb)
enhanced = enhancer.enhance(3.0)
enhanced.save("board_enhanced.png")
print("Saved enhanced image: board_enhanced.png")

# Try edge detection
edges = img_rgb.filter(ImageFilter.FIND_EDGES)
edges.save("board_edges.png")
print("Saved edge detection: board_edges.png")

# Check for text in specific regions (like bottom or top of board)
# Sometimes flags are written as text overlay
print("\n[CHECKING METADATA AND CHUNKS]")
import struct

with open(image_path, 'rb') as f:
    data = f.read()
    
    # Look for PNG chunks
    pos = 8  # Skip PNG signature
    while pos < len(data):
        if pos + 8 > len(data):
            break
        
        chunk_len = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8].decode('ascii', errors='ignore')
        
        if chunk_type in ['tEXt', 'iTXt', 'zTXt']:
            chunk_data = data[pos+8:pos+8+chunk_len]
            print(f"\nFound {chunk_type} chunk:")
            print(f"  Data: {chunk_data[:200]}")
        
        pos += 12 + chunk_len  # length + type + data + CRC

print("\n" + "="*80)
