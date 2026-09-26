#!/usr/bin/env python3
"""
Try using easyocr which doesn't require tesseract installation
"""
try:
    import easyocr
    
    print("Initializing EasyOCR...")
    reader = easyocr.Reader(['en'], gpu=False)
    
    print("Reading FLAG_IMAGE_TOP.png...")
    result = reader.readtext('FLAG_IMAGE_TOP.png', detail=0)
    
    print("\nExtracted text:")
    for text in result:
        print(f"  {text}")
    
    # Join all text
    full_text = ' '.join(result)
    print(f"\nFull text: {full_text}")
    
    # Look for flag pattern
    if 'Kaal{' in full_text or 'kaal{' in full_text.lower():
        print(f"\n{'='*80}")
        print(f"FOUND FLAG: {full_text}")
        print(f"{'='*80}")
    
except ImportError:
    print("EasyOCR not installed. Installing...")
    import subprocess
    subprocess.run(['pip', 'install', 'easyocr'], check=True)
    print("\nPlease run this script again after installation completes.")
except Exception as e:
    print(f"Error: {e}")
    print("\nAlternatively, open FLAG_IMAGE_TOP.png in an image viewer and read the flag manually.")
