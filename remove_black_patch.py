from PIL import Image
import numpy as np

# Load the corrupted QR code
img_path = r"D:\mission-git-hackss\Corrupted_QR.png"
img = Image.open(img_path)
img_array = np.array(img)

print(f"Image shape: {img_array.shape}")
print(f"Image mode: {img.mode}")

# Find the black patch (typically at the top)
# We'll scan from top to find where the actual QR code starts
height, width = img_array.shape[:2]

# Find the first row that contains QR code pattern (not solid black)
start_row = 0
for i in range(height):
    row = img_array[i]
    # Check if row has variation (not all black)
    if len(row.shape) == 1:  # Grayscale
        if np.std(row) > 10:  # Has variation
            start_row = i
            break
    else:  # RGB
        if np.std(row) > 10:
            start_row = i
            break

print(f"Black patch detected from row 0 to {start_row}")
print(f"Removing {start_row} rows from top")

# Remove the black patch by cropping
if start_row > 0:
    cleaned_array = img_array[start_row:, :]
    cleaned_img = Image.fromarray(cleaned_array)
    
    # Save the cleaned image
    output_path = r"D:\mission-git-hackss\Corrupted_QR_cleaned.png"
    cleaned_img.save(output_path)
    print(f"\nCleaned image saved to: {output_path}")
    print(f"New dimensions: {cleaned_img.size}")
else:
    print("No black patch detected at the top")
