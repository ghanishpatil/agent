#!/usr/bin/env python3
import PyPDF2

with open("Cases/Case - 7_protected.pdf", 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    reader.decrypt("CAN")
    
    for page_num, page in enumerate(reader.pages, 1):
        print(f"\n{'='*80}")
        print(f"PAGE {page_num}")
        print("="*80)
        
        text = page.extract_text()
        
        # Print with Unicode
        print(text)
        
        # Also print hex of special characters
        print("\n--- SPECIAL CHARACTERS ---")
        for i, char in enumerate(text):
            if ord(char) > 127:
                print(f"Position {i}: '{char}' (U+{ord(char):04X})")
        
        # Save to file with UTF-8
        with open(f"case7_page{page_num}_utf8.txt", "w", encoding="utf-8") as out:
            out.write(text)
