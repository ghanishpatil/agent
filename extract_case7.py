#!/usr/bin/env python3
import PyPDF2
from pathlib import Path

pdf_path = Path("Cases/Case - 7_protected.pdf")

with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    reader.decrypt("CAN")
    
    print("="*80)
    print("CASE 7 - FULL TEXT")
    print("="*80)
    
    for page_num, page in enumerate(reader.pages):
        print(f"\n{'='*80}")
        print(f"PAGE {page_num + 1}")
        print(f"{'='*80}\n")
        try:
            text = page.extract_text()
            print(text)
        except Exception as e:
            print(f"Error extracting page {page_num + 1}: {e}")
