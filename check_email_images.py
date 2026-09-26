#!/usr/bin/env python3
"""
Check the email images we created and provide manual transcription template
"""
from PIL import Image
import os

print("="*80)
print("CHECKING EMAIL IMAGES")
print("="*80)

for i in range(1, 4):
    img_file = f"email_page_{i}.png"
    if os.path.exists(img_file):
        img = Image.open(img_file)
        print(f"\n[{img_file}]")
        print(f"  Size: {img.size}")
        print(f"  Mode: {img.mode}")
        print(f"  Format: {img.format}")
        
        # Save info
        print(f"  ✓ Image exists and is readable")
    else:
        print(f"\n[{img_file}] - NOT FOUND")

print("\n" + "="*80)
print("MANUAL TRANSCRIPTION NEEDED")
print("="*80)

print("""
The PDF contains image-based text that needs to be manually read.

Based on the screenshot provided, here's what we know:
- MESSAGE 1 OF 5 (Page 1)
- Date: October 14, 2011, 04:30 PM
- Subject: Cargo Transport - Beta Protocol
- Mentions "Subject 4" with redacted name

The challenge asks for the "ledger key" of a high-ranking official.

NEXT STEPS:
1. Open email_page_1.png, email_page_2.png, email_page_3.png
2. Read all visible text from all 5 messages
3. Look for patterns in:
   - Subject numbers (Subject 4, etc.)
   - Dates
   - Redacted names/emails
   - Any codes or keys mentioned
4. The "ledger key" might be:
   - Hidden in the redacted parts
   - Formed from Subject numbers
   - In metadata or steganography
   - A pattern from the dates or message numbers
""")

print("\n" + "="*80)
