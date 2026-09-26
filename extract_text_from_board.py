from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("EXTRACTING TEXT/PATTERNS FROM BOARD IMAGE")
print("="*80)

img = Image.open(image_path)

# Try different image processing techniques
print("\n[1. High Contrast]")
enhancer = ImageEnhance.Contrast(img)
high_contrast = enhancer.enhance(5.0)
high_contrast.save("board_high_contrast.png")
print("Saved: board_high_contrast.png")

print("\n[2. Grayscale + Threshold]")
gray = img.convert('L')
# Try different thresholds
for threshold in [50, 100, 150, 200]:
    binary = gray.point(lambda x: 255 if x > threshold else 0)
    binary.save(f"board_threshold_{threshold}.png")
    print(f"Saved: board_threshold_{threshold}.png")

print("\n[3. Edge Detection]")
edges = img.convert('RGB').filter(ImageFilter.FIND_EDGES)
edges.save("board_edges.png")
print("Saved: board_edges.png")

print("\n[4. Invert Colors]")
inverted = ImageOps.invert(img.convert('RGB'))
inverted.save("board_inverted.png")
print("Saved: board_inverted.png")

print("\n[5. Sharpen]")
sharpened = img.filter(ImageFilter.SHARPEN)
sharpened.save("board_sharpened.png")
print("Saved: board_sharpened.png")

# Check for patterns in specific regions
print("\n[6. Checking specific regions for text]")
pixels = np.array(img.convert('RGB'))

# Check borders
top_border = pixels[:50, :, :]
bottom_border = pixels[-50:, :, :]
left_border = pixels[:, :50, :]
right_border = pixels[:, -50:, :]

print(f"Top border unique colors: {len(np.unique(top_border.reshape(-1, 3), axis=0))}")
print(f"Bottom border unique colors: {len(np.unique(bottom_border.reshape(-1, 3), axis=0))}")
print(f"Left border unique colors: {len(np.unique(left_border.reshape(-1, 3), axis=0))}")
print(f"Right border unique colors: {len(np.unique(right_border.reshape(-1, 3), axis=0))}")

# Check center
center = pixels[300:420, 300:420, :]
print(f"Center region unique colors: {len(np.unique(center.reshape(-1, 3), axis=0))}")

# Look for very dark or very light pixels that might be text
very_dark = np.where(np.mean(pixels, axis=2) < 10)
very_light = np.where(np.mean(pixels, axis=2) > 245)

print(f"\nVery dark pixels: {len(very_dark[0])}")
print(f"Very light pixels: {len(very_light[0])}")

if len(very_dark[0]) > 0:
    print(f"Dark pixel locations (first 10): {list(zip(very_dark[0][:10], very_dark[1][:10]))}")

# Try OCR if pytesseract is available
try:
    import pytesseract
    print("\n[7. OCR Attempt]")
    text = pytesseract.image_to_string(img)
    if text.strip():
        print(f"OCR found text: {text}")
    else:
        print("No text found by OCR")
    
    # Try on high contrast version
    text2 = pytesseract.image_to_string(high_contrast)
    if text2.strip():
        print(f"OCR on high contrast: {text2}")
except ImportError:
    print("\n[7. OCR] pytesseract not available")

# Check if pieces form a pattern
print("\n[8. Checking if piece positions form a pattern]")
# Extract piece positions as a grid
grid_size = 8
cell_size = 90
board_grid = [[0 for _ in range(8)] for _ in range(8)]

for row in range(grid_size):
    for col in range(grid_size):
        y = row * cell_size + cell_size // 2
        x = col * cell_size + cell_size // 2
        region = pixels[y-30:y+30, x-30:x+30, :]
        min_brightness = np.min(np.mean(region, axis=2))
        
        if min_brightness < 100:
            if min_brightness < 40:
                board_grid[row][col] = 1  # Black
            else:
                board_grid[row][col] = 2  # White

# Print as visual pattern
print("\nBoard as pattern (1=Black, 2=White, 0=Empty):")
for row in board_grid:
    print(' '.join([str(x) for x in row]))

# Check if this pattern spells something
# Try reading as QR code pattern or similar
print("\n[9. Checking for QR code or barcode patterns]")
try:
    from pyzbar.pyzbar import decode
    decoded = decode(img)
    if decoded:
        for obj in decoded:
            print(f"Found: {obj.type} - {obj.data.decode('utf-8')}")
    else:
        print("No QR/barcode found")
except ImportError:
    print("pyzbar not available")

print("\n" + "="*80)
print("Check the generated images for any visible text or patterns")
print("="*80)
