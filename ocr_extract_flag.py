#!/usr/bin/env python3
"""
Extract flag from binary images using OCR
"""
from PIL import Image
import pytesseract
import numpy as np

print("="*60)
print("OCR FLAG EXTRACTION")
print("="*60)

# Try different binary images
images = [
    'binary_cropped_autoleveled.jpg',
    'binary_cropped_contrasted.jpg',
    'binary_cropped_equalized.jpg'
]

for img_path in images:
    print(f"\n[Processing {img_path}]")
    
    try:
        img = Image.open(img_path)
        
        # Try OCR with different configurations
        configs = [
            '--psm 6',  # Assume uniform block of text
            '--psm 7',  # Treat as single line
            '--psm 11', # Sparse text
            '--psm 13', # Raw line
        ]
        
        for config in configs:
            text = pytesseract.image_to_string(img, config=config)
            text = text.strip()
            
            if text and len(text) > 5:
                print(f"\n  Config: {config}")
                print(f"  Text: {text}")
                
                # Look for flag pattern
                if 'Kaal{' in text or 'kaal{' in text.lower():
                    print(f"\n{'='*60}")
                    print(f"FOUND FLAG: {text}")
                    print(f"{'='*60}")
        
        # Also try inverting the image (white text on black -> black text on white)
        img_inverted = Image.eval(img, lambda x: 255 - x)
        
        print(f"\n  [Trying inverted image]")
        for config in configs:
            text = pytesseract.image_to_string(img_inverted, config=config)
            text = text.strip()
            
            if text and len(text) > 5:
                print(f"\n  Config: {config}")
                print(f"  Text: {text}")
                
                if 'Kaal{' in text or 'kaal{' in text.lower():
                    print(f"\n{'='*60}")
                    print(f"FOUND FLAG: {text}")
                    print(f"{'='*60}")
                    
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "="*60)
