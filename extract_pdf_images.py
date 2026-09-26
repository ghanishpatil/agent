#!/usr/bin/env python3
"""
Extract images and analyze PDF structure
"""
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image
import io

print("="*80)
print("EXTRACTING PDF IMAGES AND STRUCTURE")
print("="*80)

# Try with PyMuPDF (fitz)
try:
    doc = fitz.open('emails.pdf')
    
    print(f"\n[PDF Info]")
    print(f"Pages: {len(doc)}")
    print(f"Metadata: {doc.metadata}")
    
    # Extract images from each page
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        print(f"\n[Page {page_num + 1}]")
        
        # Get text
        text = page.get_text()
        if text.strip():
            print(f"Text found: {len(text)} characters")
            print(f"Preview: {text[:500]}")
        else:
            print("No text found")
        
        # Get images
        image_list = page.get_images()
        print(f"Images found: {len(image_list)}")
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Save image
            image_filename = f"email_page{page_num+1}_img{img_index+1}.{image_ext}"
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)
            
            print(f"  Saved: {image_filename} ({len(image_bytes)} bytes)")
            
            # Try OCR on the image
            try:
                from PIL import Image
                import pytesseract
                
                img_pil = Image.open(io.BytesIO(image_bytes))
                ocr_text = pytesseract.image_to_string(img_pil)
                
                if ocr_text.strip():
                    print(f"  OCR text preview: {ocr_text[:200]}")
                    
                    # Save OCR text
                    with open(f"email_page{page_num+1}_img{img_index+1}_ocr.txt", "w", encoding='utf-8') as f:
                        f.write(ocr_text)
            except Exception as e:
                print(f"  OCR not available: {e}")
    
    doc.close()
    
except Exception as e:
    print(f"PyMuPDF error: {e}")

# Also check PDF structure
print(f"\n[Checking PDF structure with PyPDF2]")
try:
    with open('emails.pdf', 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        
        for i, page in enumerate(pdf.pages):
            print(f"\nPage {i+1} objects:")
            if '/XObject' in page['/Resources']:
                xobjects = page['/Resources']['/XObject'].get_object()
                print(f"  XObjects: {list(xobjects.keys())}")
            
            # Check for fonts
            if '/Font' in page['/Resources']:
                fonts = page['/Resources']['/Font'].get_object()
                print(f"  Fonts: {list(fonts.keys())}")
            
except Exception as e:
    print(f"PyPDF2 error: {e}")

print("\n" + "="*80)
