#!/usr/bin/env python3
"""
Full metadata and filename analysis
"""
import exif
from PIL import Image
import os

image_path = "image_sJM6Gg8.jpg"

print("="*60)
print("FULL METADATA ANALYSIS")
print("="*60)

# Filename analysis
print("\n[1] Filename analysis:")
filename = os.path.basename(image_path)
print(f"    Filename: {filename}")
print(f"    Without extension: {filename.rsplit('.', 1)[0]}")

# The filename is: image_sJM6Gg8
# This could be base64 or encoded
import base64

encoded_part = "sJM6Gg8"
print(f"\n[2] Decoding filename part '{encoded_part}':")

# Try base64
for padding in ['', '=', '==', '===']:
    try:
        decoded = base64.b64decode(encoded_part + padding)
        print(f"    Base64 (padding '{padding}'): {decoded}")
        try:
            as_str = decoded.decode('utf-8')
            print(f"        As string: {as_str}")
            if 'Kaal' in as_str or 'flag' in as_str.lower():
                print(f"        *** POTENTIAL: {as_str} ***")
        except:
            pass
    except:
        pass

# Try URL decoding
import urllib.parse
url_decoded = urllib.parse.unquote(encoded_part)
print(f"    URL decoded: {url_decoded}")

# Check with exif library
print(f"\n[3] EXIF with exif library:")
try:
    with open(image_path, 'rb') as f:
        img = exif.Image(f)
    
    if img.has_exif:
        print("    EXIF data found:")
        for attr in dir(img):
            if not attr.startswith('_') and hasattr(img, attr):
                try:
                    value = getattr(img, attr)
                    if value and not callable(value):
                        print(f"        {attr}: {value}")
                        
                        # Check if any field contains flag
                        if isinstance(value, str) and ('Kaal' in value or 'flag' in value.lower()):
                            print(f"            *** POTENTIAL FLAG: {value} ***")
                except:
                    pass
    else:
        print("    No EXIF data")
except Exception as e:
    print(f"    Error: {e}")

# Check PIL Image info
print(f"\n[4] PIL Image info:")
img = Image.open(image_path)
if img.info:
    for key, value in img.info.items():
        print(f"    {key}: {value}")
        if isinstance(value, str) and ('Kaal' in value or 'flag' in value.lower()):
            print(f"        *** POTENTIAL FLAG: {value} ***")

# Check for QR codes or barcodes in the image
print(f"\n[5] Checking for QR codes:")
try:
    from pyzbar.pyzbar import decode
    decoded_objects = decode(img)
    if decoded_objects:
        for obj in decoded_objects:
            print(f"    Type: {obj.type}")
            print(f"    Data: {obj.data.decode()}")
            if b'Kaal{' in obj.data:
                print(f"        *** FLAG FOUND: {obj.data.decode()} ***")
    else:
        print("    No QR codes found")
except ImportError:
    print("    pyzbar not installed, skipping QR code check")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "="*60)
