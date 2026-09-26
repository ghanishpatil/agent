# How to Extract the Flag from the Image

## Summary
The flag is hidden in the image `image_sJM6Gg8.jpg` as very dark text. I've extracted and enhanced it for you.

## Generated Images (Open These!)

I've created clean versions of the flag text:

1. **FLAG_IMAGE.png** - Full flag text (white on black)
2. **FLAG_IMAGE_TOP.png** - Top portion where the flag starts (easier to read)
3. **green_text_cropped.jpg** - Alternative extraction
4. **green_text_high_contrast.jpg** - High contrast version

## How to Read the Flag

### Option 1: Open the Images (EASIEST)
1. Open `FLAG_IMAGE_TOP.png` in any image viewer (Windows Photos, Paint, etc.)
2. The flag should be visible as white text on black background
3. Look for text starting with "Kaal{"

### Option 2: Install Tesseract OCR
If you want to extract the text automatically:

1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install it (default: C:\Program Files\Tesseract-OCR)
3. Run the OCR script:
   ```
   python ocr_extract_flag.py
   ```

### Option 3: Use Online OCR
1. Upload `FLAG_IMAGE_TOP.png` to an online OCR service like:
   - https://www.onlineocr.net/
   - https://www.newocr.com/
2. Extract the text

## Technical Details

The challenge hid the flag by:
- Using very dark pixels (RGB values around 4, 27, 12)
- Encoding text in the green channel (highest signal)
- Making it nearly invisible to the naked eye

The extraction process:
1. Extracted green channel from original image
2. Applied threshold (>35) to create binary image
3. Cropped to text region
4. Saved as high-contrast PNG

## Flag Format
The flag should be in the format: `Kaal{...}`

## Next Steps
Open `FLAG_IMAGE_TOP.png` and read the flag text manually, or use OCR to extract it automatically.
