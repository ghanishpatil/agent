#!/usr/bin/env python3
"""
Use stegano library to extract hidden data
"""
from stegano import lsb
from stegano.lsbset import generators
import re

image_path = "image_sJM6Gg8.jpg"

print("="*60)
print("STEGANO LSB EXTRACTION")
print("="*60)

# Try LSB extraction
print("\n[1] LSB extraction:")
try:
    secret = lsb.reveal(image_path)
    if secret:
        print(f"    Extracted: {secret[:500]}")
        
        if 'Kaal{' in secret:
            flag = re.search(r'Kaal\{[^}]+\}', secret)
            if flag:
                print(f"\n[+] FLAG FOUND: {flag.group(0)}")
    else:
        print("    No hidden message found")
except Exception as e:
    print(f"    Error: {e}")

# Try with different generators
print("\n[2] Trying different LSB generators:")
generators_list = [
    ('eratosthenes', generators.eratosthenes()),
    ('fibonacci', generators.fibonacci()),
    ('identity', generators.identity()),
]

for name, gen in generators_list:
    try:
        print(f"\n    Generator: {name}")
        secret = lsb.reveal(image_path, gen)
        if secret:
            print(f"        Extracted: {secret[:200]}")
            if 'Kaal{' in secret:
                flag = re.search(r'Kaal\{[^}]+\}', secret)
                if flag:
                    print(f"\n[+] FLAG FOUND with {name}: {flag.group(0)}")
    except Exception as e:
        print(f"        Error: {e}")

print("\n" + "="*60)
