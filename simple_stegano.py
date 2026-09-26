#!/usr/bin/env python3
"""
Simple stegano extraction
"""
from stegano import lsb
import re

image_path = "image_sJM6Gg8.jpg"

print("="*60)
print("STEGANO EXTRACTION")
print("="*60)

print("\n[1] LSB reveal:")
try:
    secret = lsb.reveal(image_path)
    if secret:
        print(f"    Length: {len(secret)}")
        print(f"    Content: {secret}")
        
        if 'Kaal{' in secret:
            flag = re.search(r'Kaal\{[^}]+\}', secret)
            if flag:
                print(f"\n[+] FLAG: {flag.group(0)}")
        else:
            print("\n    No flag found, but message extracted")
    else:
        print("    No hidden message")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "="*60)
