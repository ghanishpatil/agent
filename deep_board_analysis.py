from PIL import Image
import numpy as np
import os

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("DEEP BOARD.PNG ANALYSIS")
print("="*80)

# Load image
img = Image.open(image_path)
print(f"\nImage: {img.size[0]}x{img.size[1]} {img.mode}")

# Save a copy locally to examine
img.save("board_local.png")
print("Saved local copy: board_local.png")

# Convert to RGB array
img_rgb = img.convert('RGB')
pixels = np.array(img_rgb)

print(f"\nPixel array shape: {pixels.shape}")

# Check LSB of each channel
print("\n[LSB STEGANOGRAPHY CHECK]")
for channel_idx, channel_name in enumerate(['Red', 'Green', 'Blue']):
    lsb_data = pixels[:, :, channel_idx] & 1
    unique_vals = np.unique(lsb_data)
    print(f"{channel_name} LSB unique values: {unique_vals}")
    
    # Try to extract LSB bits as bytes
    lsb_flat = lsb_data.flatten()
    
    # Convert bits to bytes
    byte_count = len(lsb_flat) // 8
    lsb_bytes = []
    for i in range(min(1000, byte_count)):  # First 1000 bytes
        byte_val = 0
        for bit_idx in range(8):
            byte_val = (byte_val << 1) | lsb_flat[i*8 + bit_idx]
        lsb_bytes.append(byte_val)
    
    # Look for ASCII text
    lsb_text = bytes(lsb_bytes)
    if b'KAAL' in lsb_text or b'FLAG' in lsb_text or b'flag' in lsb_text:
        print(f"  FOUND in {channel_name} LSB: {lsb_text}")
    
    # Check for printable ASCII
    printable_count = sum(1 for b in lsb_bytes if 32 <= b <= 126)
    print(f"  Printable ASCII ratio: {printable_count}/{len(lsb_bytes)} = {printable_count/len(lsb_bytes):.2%}")

# Check alpha channel if exists
if img.mode == 'RGBA':
    print("\n[ALPHA CHANNEL CHECK]")
    img_rgba = np.array(img)
    alpha = img_rgba[:, :, 3]
    unique_alpha = np.unique(alpha)
    print(f"Unique alpha values: {unique_alpha}")
    
    if len(unique_alpha) > 2:  # More than just 0 and 255
        print("Alpha channel has varying transparency - might contain data")
        alpha_flat = alpha.flatten()
        alpha_bytes = alpha_flat[:1000]
        alpha_text = bytes(alpha_bytes)
        if b'KAAL' in alpha_text or b'FLAG' in alpha_text:
            print(f"FOUND in alpha: {alpha_text}")

# Analyze image visually
print("\n[VISUAL ANALYSIS]")
# Check if it looks like a game board by analyzing color distribution
unique_colors = len(np.unique(pixels.reshape(-1, 3), axis=0))
print(f"Unique colors in image: {unique_colors}")

# Check for grid patterns (common in board games)
# Sample middle row
mid_row = pixels[360, :, :]
color_changes = 0
for i in range(1, len(mid_row)):
    if not np.array_equal(mid_row[i], mid_row[i-1]):
        color_changes += 1
print(f"Color changes in middle row: {color_changes}")

# Check corners and edges for patterns
print(f"\nTop-left corner (10x10) average color: {np.mean(pixels[:10, :10, :], axis=(0,1))}")
print(f"Top-right corner (10x10) average color: {np.mean(pixels[:10, -10:, :], axis=(0,1))}")
print(f"Bottom-left corner (10x10) average color: {np.mean(pixels[-10:, :10, :], axis=(0,1))}")
print(f"Bottom-right corner (10x10) average color: {np.mean(pixels[-10:, -10:, :], axis=(0,1))}")

# Try to detect if it's tic-tac-toe, chess, checkers, etc.
# by looking at the structure
print("\n[BOARD TYPE DETECTION]")
# Check if image is divided into clear sections
# Sample at regular intervals
grid_size = 3  # Try 3x3 (tic-tac-toe)
cell_size = 720 // grid_size
print(f"Testing {grid_size}x{grid_size} grid (cell size: {cell_size}x{cell_size})")

for row in range(grid_size):
    for col in range(grid_size):
        y = row * cell_size + cell_size // 2
        x = col * cell_size + cell_size // 2
        color = pixels[y, x, :]
        print(f"  Cell [{row},{col}] center color: {color}")

print("\n" + "="*80)
print("Analysis complete. Check board_local.png to visually inspect the board.")
print("="*80)
