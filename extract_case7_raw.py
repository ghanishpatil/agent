#!/usr/bin/env python3
import PyPDF2
from pathlib import Path

pdf_path = Path("Cases/Case - 7_protected.pdf")

with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    reader.decrypt("CAN")
    
    print("CASE 7 - RAW EXTRACTION")
    print("="*80)
    
    for page_num, page in enumerate(reader.pages):
        print(f"\n{'='*80}")
        print(f"PAGE {page_num + 1}")
        print(f"{'='*80}\n")
        
        # Try to get raw text
        text = page.extract_text()
        
        # Print as repr to see special characters
        print("TEXT (repr):")
        print(repr(text))
        print()
        
        # Also print normally
        print("TEXT (normal):")
        for line in text.split('\n'):
            try:
                print(line)
            except:
                print(f"[Line with encoding issues: {repr(line)}]")
