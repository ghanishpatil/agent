# Tesseract Installation for Windows

To extract the flag text, you need to install Tesseract OCR:

1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install it (default location: C:\Program Files\Tesseract-OCR)
3. Add to PATH or set in Python:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

Alternatively, you can manually inspect the generated images:
- green_text_cropped.jpg - Contains the flag text
- left_text_only.jpg - Alternative extraction

The flag should be visible as white text on black background in these images.
Open them in an image viewer and read the text manually.
