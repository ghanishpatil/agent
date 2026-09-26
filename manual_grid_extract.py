#!/usr/bin/env python3
"""
Manually extract the grid data from the image by analyzing pixel patterns
"""

from PIL import Image, ImageDraw
import numpy as np

def analyze_grid_structure():
    """Analyze the grid structure to extract the table"""
    print("="*60)
    print("Manual Grid Extraction")
    print("="*60)
    
    img = Image.open('kaalchakra_image.png')
    
    # Convert to numpy array for easier analysis
    img_array = np.array(img)
    
    print(f"[*] Image shape: {img_array.shape}")
    
    # The grid appears to be in a specific region
    # Let's focus on the right half where the "Bonus Puppy" section is
    
    # From the screenshot, the grid appears to be roughly:
    # - In the right half of the image
    # - Has a dark background with light text
    # - Is a table with rows and columns
    
    # Let's try to find the table by looking for grid lines
    # Grid lines are typically horizontal/vertical lines of similar color
    
    # Convert to grayscale
    img_gray = img.convert('L')
    gray_array = np.array(img_gray)
    
    # Find horizontal lines (rows)
    print("\n[*] Looking for horizontal grid lines...")
    horizontal_lines = []
    
    for y in range(gray_array.shape[0]):
        # Count how many pixels in this row are similar (grid line)
        row = gray_array[y, :]
        # Check if this row has many pixels of similar value (indicating a line)
        unique, counts = np.unique(row, return_counts=True)
        if len(counts) > 0 and max(counts) > gray_array.shape[1] * 0.7:
            horizontal_lines.append(y)
    
    print(f"[+] Found {len(horizontal_lines)} potential horizontal lines")
    
    # Find vertical lines (columns)
    print("\n[*] Looking for vertical grid lines...")
    vertical_lines = []
    
    for x in range(gray_array.shape[1]):
        col = gray_array[:, x]
        unique, counts = np.unique(col, return_counts=True)
        if len(counts) > 0 and max(counts) > gray_array.shape[0] * 0.7:
            vertical_lines.append(x)
    
    print(f"[+] Found {len(vertical_lines)} potential vertical lines")
    
    # Based on the screenshot, the grid appears to be approximately:
    # - 10 columns
    # - 10 rows
    # - Located in the right portion of the image
    
    # Let's manually define the approximate grid region based on the screenshot
    # The grid appears to start around x=500 and spans about 250 pixels
    # It appears to start around y=200 and spans about 250 pixels
    
    grid_x_start = 500
    grid_x_end = 750
    grid_y_start = 200
    grid_y_end = 450
    
    # Extract the grid region
    grid_region = img.crop((grid_x_start, grid_y_start, grid_x_end, grid_y_end))
    grid_region.save('extracted_grid.png')
    print(f"\n[+] Saved extracted grid region to extracted_grid.png")
    
    # Now let's try to read the characters in each cell
    # We'll divide the grid into cells and analyze each one
    
    rows = 10
    cols = 10
    
    cell_width = (grid_x_end - grid_x_start) // cols
    cell_height = (grid_y_end - grid_y_start) // rows
    
    print(f"\n[*] Cell size: {cell_width}x{cell_height}")
    
    # Extract each cell
    print("\n[*] Extracting cells...")
    
    grid_data = []
    
    for row in range(rows):
        row_data = []
        for col in range(cols):
            x1 = grid_x_start + col * cell_width
            y1 = grid_y_start + row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            
            cell = img.crop((x1, y1, x2, y2))
            cell.save(f'cell_{row}_{col}.png')
            
            # Try to identify the character in this cell
            # For now, just note that we've extracted it
            row_data.append(f"cell_{row}_{col}")
        
        grid_data.append(row_data)
    
    print(f"[+] Extracted {rows}x{cols} = {rows*cols} cells")
    print("[*] Cells saved as cell_R_C.png")
    
    return grid_data

def try_manual_transcription():
    """
    Based on the screenshot, manually transcribe what we can see
    """
    print("\n" + "="*60)
    print("Manual Transcription from Screenshot")
    print("="*60)
    
    # From the screenshot, the grid appears to show:
    # A table with letters and numbers
    # This looks like it could be a Polybius square or similar cipher
    
    # The visible pattern from the screenshot shows:
    # Row headers and column headers with numbers/letters
    # Cells containing single letters
    
    print("\n[*] The grid appears to be a cipher table")
    print("[*] Likely a Polybius square or coordinate cipher")
    print("[*] Each cell contains a letter")
    print("[*] Row/column coordinates map to letters")
    
    # Without being able to read the exact values, let's note what we know:
    print("\n[*] To decode:")
    print("  1. Need to transcribe the exact grid values")
    print("  2. Look for a message encoded in the coordinates")
    print("  3. Or the grid itself spells out the flag")
    
    # The challenge mentions "time echoes" - maybe the flag is encoded
    # using time-based coordinates or a repeating pattern

def main():
    print("Manual Grid Extraction Tool")
    print()
    
    try:
        grid_data = analyze_grid_structure()
        try_manual_transcription()
        
        print("\n" + "="*60)
        print("Next Steps:")
        print("="*60)
        print("1. Check extracted_grid.png for clearer view")
        print("2. Check individual cell_R_C.png files")
        print("3. Manually transcribe the letters from each cell")
        print("4. Build the complete cipher table")
        print("5. Decode the message")
        
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
