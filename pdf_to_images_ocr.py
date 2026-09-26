#!/usr/bin/env python3
"""
Convert PDF pages to images and OCR them
"""
import fitz  # PyMuPDF
from PIL import Image
import io

print("="*80)
print("CONVERTING PDF TO IMAGES")
print("="*80)

# Open PDF
doc = fitz.open('emails.pdf')

print(f"\n[Converting {len(doc)} pages to images]")

all_text = ""

for page_num in range(len(doc)):
    page = doc[page_num]
    
    # Remove annotations first
    for annot in page.annots():
        page.delete_annot(annot)
    
    # Convert page to image at high resolution
    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
    pix = page.get_pixmap(matrix=mat)
    
    # Save as PNG
    img_filename = f"email_page_{page_num+1}.png"
    pix.save(img_filename)
    print(f"\n✓ Saved: {img_filename}")
    
    # Try OCR
    try:
        import pytesseract
        from PIL import Image
        
        # Load image
        img = Image.open(img_filename)
        
        # OCR
        text = pytesseract.image_to_string(img)
        
        print(f"\n[OCR Text from Page {page_num+1}]")
        print("="*80)
        print(text)
        print("="*80)
        
        all_text += f"\n\n--- PAGE {page_num+1} ---\n\n{text}"
        
        # Save individual page text
        with open(f"email_page_{page_num+1}_ocr.txt", 'w', encoding='utf-8') as f:
            f.write(text)
        
    except ImportError:
        print(f"  Tesseract not available - install with: pip install pytesseract")
        print(f"  Also need to install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    except Exception as e:
        print(f"  OCR error: {e}")

doc.close()

# Save all OCR text
if all_text:
    with open('emails_ocr_all.txt', 'w', encoding='utf-8') as f:
        f.write(all_text)
    print(f"\n✓ Saved all OCR text to: emails_ocr_all.txt")
    
    # Look for flags
    import re
    flags = re.findall(r'Kaal\{[^}]+\}', all_text, re.IGNORECASE)
    if flags:
        print(f"\n{'='*80}")
        print("✓✓✓ FOUND FLAGS:")
        print('='*80)
        for flag in flags:
            print(f"  {flag}")
        print('='*80)

print("\n" + "="*80)
