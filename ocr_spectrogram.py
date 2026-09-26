#!/usr/bin/env python3
"""
OCR the spectrogram images to find hidden text
"""

import os

for img_file in ['spectrogram_full.png', 'spectrogram_high_freq.png']:
    if os.path.exists(img_file):
        print(f"\n[*] OCR on {img_file}...")
        
        try:
            import pytesseract
            from PIL import Image
            
            img = Image.open(img_file)
            text = pytesseract.image_to_string(img)
            
            print(f"    Extracted text:")
            print(text)
            
            import re
            flags = re.findall(r'Kaal\{[^}]+\}', text)
            if flags:
                print(f"\n[+] *** FLAG FOUND IN SPECTROGRAM ***: {flags[0]}")
                
        except ImportError:
            print("    pytesseract not available")
        except Exception as e:
            print(f"    OCR error: {e}")

print("\n[*] Done!")
