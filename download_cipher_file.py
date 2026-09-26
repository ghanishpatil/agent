#!/usr/bin/env python3
"""Download and analyze the cipher file"""
import requests

url = "https://files.ctf7.com/media/challenge_attachments/cipher_binXXadc.txt"

print("="*80)
print("DOWNLOADING CIPHER FILE")
print("="*80)

try:
    response = requests.get(url, timeout=10)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        print(f"Content:\n{content}")
        
        # Save to file
        with open("cipher_file.txt", "w") as f:
            f.write(content)
        print(f"\nSaved to: cipher_file.txt")
        
        # Analyze
        print(f"\nLength: {len(content)}")
        print(f"Lines: {content.count(chr(10)) + 1}")
        
    else:
        print(f"Failed to download: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
