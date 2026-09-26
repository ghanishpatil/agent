#!/usr/bin/env python3
"""Extract full text from Case 1 to find the password hint"""

import PyPDF2
from pathlib import Path

pdf_path = Path("Cases/Case - 1.pdf")

with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    
    print("="*80)
    print("FULL TEXT FROM CASE 1")
    print("="*80)
    
    for page_num, page in enumerate(reader.pages):
        print(f"\n{'='*80}")
        print(f"PAGE {page_num + 1}")
        print(f"{'='*80}\n")
        text = page.extract_text()
        print(text)
    
    print("\n" + "="*80)
    print("METADATA")
    print("="*80)
    if reader.metadata:
        for key, value in reader.metadata.items():
            print(f"{key}: {value}")
