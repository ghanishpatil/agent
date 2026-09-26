#!/usr/bin/env python3
"""
Intel OSINT Challenge Guide
Based on challenge description clues:
- "edge of somewhere world hasn't been kind to"
- "stories rarely make headlines but leave their marks on the land"
- "one clue leads to another"

This suggests:
1. Conflict zones (Syria, Yemen, Ukraine, Gaza, etc.)
2. Disaster areas (Fukushima, Chernobyl, etc.)
3. Marginalized regions (refugee camps, disputed territories)
4. Areas with environmental damage

Flag Format: Kaal{part_1flag_coordinates after decimal 4digits}
"""

from PIL import Image
import hashlib

def analyze_image_hash(image_path):
    """Get image hash for reverse search"""
    with open(image_path, 'rb') as f:
        data = f.read()
        md5 = hashlib.md5(data).hexdigest()
        sha256 = hashlib.sha256(data).hexdigest()
    
    print(f"MD5: {md5}")
    print(f"SHA256: {sha256}")
    return md5, sha256

def get_image_details(image_path):
    """Extract all possible details"""
    img = Image.open(image_path)
    
    print("=" * 60)
    print("IMAGE ANALYSIS FOR OSINT")
    print("=" * 60)
    
    print(f"\nBasic Info:")
    print(f"  Size: {img.size[0]}x{img.size[1]} pixels")
    print(f"  Format: {img.format}")
    print(f"  Mode: {img.mode}")
    
    # Get dominant colors
    import numpy as np
    pixels = np.array(img)
    
    if len(pixels.shape) == 3:
        # Get average colors
        avg_color = pixels.mean(axis=(0,1))
        print(f"\n  Average color (RGBA): {avg_color}")
        
        # Check for specific color patterns
        # Desert/sandy: high red/yellow
        # Urban: gray tones
        # Vegetation: green
        
        if avg_color[0] > 150 and avg_color[1] > 130:  # Reddish/sandy
            print("  -> Possible desert or arid region")
        elif avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]:
            print("  -> Possible vegetation/green area")
        elif abs(avg_color[0] - avg_color[1]) < 20 and abs(avg_color[1] - avg_color[2]) < 20:
            print("  -> Possible urban/gray area")
    
    print("\n" + "=" * 60)
    print("REVERSE IMAGE SEARCH INSTRUCTIONS:")
    print("=" * 60)
    print("\n1. Google Images: https://images.google.com")
    print("   - Click camera icon")
    print("   - Upload intel.png")
    print("   - Look for similar images or locations")
    
    print("\n2. Yandex Images: https://yandex.com/images")
    print("   - Often better for geolocation")
    print("   - Upload the image")
    
    print("\n3. TinEye: https://tineye.com")
    print("   - Find exact matches or modifications")
    
    print("\n4. Bing Visual Search: https://www.bing.com/visualsearch")
    
    print("\n" + "=" * 60)
    print("MANUAL ANALYSIS CHECKLIST:")
    print("=" * 60)
    print("\n□ Look for text/signs (language clues)")
    print("□ Identify architectural style")
    print("□ Check vegetation type (climate indicator)")
    print("□ Look for vehicles (license plates, models)")
    print("□ Identify landmarks or unique features")
    print("□ Check terrain (mountains, water bodies)")
    print("□ Look for infrastructure (power lines, roads)")
    print("□ Identify any visible damage or conflict markers")
    
    print("\n" + "=" * 60)
    print("CONFLICT/DISASTER ZONES TO CONSIDER:")
    print("=" * 60)
    print("\n- Syria (Aleppo, Damascus, Raqqa)")
    print("- Yemen (Sana'a, Aden)")
    print("- Gaza Strip")
    print("- Ukraine (Mariupol, Donetsk)")
    print("- Afghanistan")
    print("- Libya")
    print("- Chernobyl Exclusion Zone")
    print("- Fukushima")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("\n1. Open intel.png and manually inspect it")
    print("2. Use reverse image search (Google/Yandex)")
    print("3. Identify the location")
    print("4. Get precise coordinates (Google Maps)")
    print("5. Extract 4 digits after decimal point")
    print("6. Format: Kaal{part_1flag_XXXX} where XXXX is coordinate decimals")

if __name__ == "__main__":
    image_path = r"D:\mission-git-hackss\intel.png"
    
    print("\nCalculating image hashes...")
    analyze_image_hash(image_path)
    print()
    
    get_image_details(image_path)
    
    print("\n" + "=" * 60)
    print("IMPORTANT: You need to manually view the image!")
    print("Open: D:\\mission-git-hackss\\intel.png")
    print("=" * 60)
