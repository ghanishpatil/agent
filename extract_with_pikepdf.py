#!/usr/bin/env python3
import pikepdf
from pathlib import Path

pdf_path = Path("Cases/Case - 7_protected.pdf")

with pikepdf.open(pdf_path, password="CAN") as pdf:
    print("CASE 7 - Using pikepdf")
    print("="*80)
    
    for page_num, page in enumerate(pdf.pages):
        print(f"\nPAGE {page_num + 1}")
        print("="*80)
        
        # Extract text
        try:
            text = page.extract_text()
            print(text)
        except Exception as e:
            print(f"Error: {e}")
            
            # Try to get raw content
            try:
                print("\nRaw content stream:")
                print(page.Contents.read_bytes())
            except:
                pass
