#!/usr/bin/env python3
"""
Visual analysis of intel.png for OSINT challenge
Looking for landmarks, text, or identifying features
"""

from PIL import Image
import numpy as np
import pytesseract

def extract_text_from_image(image_path):
    """Use OCR to extract any text from the image"""
    try:
        img = Image.open(image_path)
        
        # Try OCR on original
        text = pytesseract.image_to_string(img)
        print("OCR Text Found:")
        print(text)
        print("=" * 60)
        
        # Try with different preprocessing
        img_gray = img.convert('L')
        text_gray = pytesseract.image_to_string(img_gray)
        if text_gray != text:
            print("OCR Text (Grayscale):")
            print(text_gray)
            print("=" * 60)
        
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def analyze_image_properties(image_path):
    """Analyze image for hidden information"""
    img = Image.open(image_path)
    
    # Check image info
    print(f"Image Info:")
    print(f"  Format: {img.format}")
    print(f"  Size: {img.size}")
    print(f"  Mode: {img.mode}")
    
    if hasattr(img, 'info'):
        print(f"  Metadata: {img.info}")
    
    # Check for text chunks in PNG
    if img.format == 'PNG':
        print("\nPNG Chunks:")
        for chunk in img.info.keys():
            print(f"  {chunk}: {img.info[chunk]}")
    
    # Analyze pixel data for patterns
    pixels = np.array(img)
    print(f"\nPixel array shape: {pixels.shape}")
    print(f"Pixel data type: {pixels.dtype}")
    
    # Check LSB for steganography
    if len(pixels.shape) == 3:
        lsb_data = pixels[:, :, 0] & 1  # Get LSB of red channel
        unique_vals = np.unique(lsb_data)
        print(f"Unique LSB values in red channel: {unique_vals}")

def save_image_for_inspection(image_path):
    """Save a copy for manual inspection"""
    img = Image.open(image_path)
    
    # Save different versions
    img.save("intel_copy.png")
    print("\nSaved copy as intel_copy.png for manual inspection")
    
    # Try to enhance contrast
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(img)
    enhanced = enhancer.enhance(2.0)
    enhanced.save("intel_enhanced.png")
    print("Saved enhanced version as intel_enhanced.png")

if __name__ == "__main__":
    image_path = r"D:\mission-git-hackss\intel.png"
    
    print("Analyzing image properties...")
    analyze_image_properties(image_path)
    print("\n" + "=" * 60 + "\n")
    
    print("Attempting OCR...")
    extract_text_from_image(image_path)
    print("\n" + "=" * 60 + "\n")
    
    save_image_for_inspection(image_path)
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Manually inspect the image for landmarks, signs, or text")
    print("2. Use Google Reverse Image Search")
    print("3. Look for geographical features (buildings, terrain, etc.)")
    print("4. The challenge mentions 'edge of somewhere world hasn't been kind to'")
    print("   - Could be conflict zones, disaster areas, or neglected regions")
