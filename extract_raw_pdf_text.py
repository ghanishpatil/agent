#!/usr/bin/env python3
"""
Extract raw text from PDF using different methods
"""
import PyPDF2
import fitz

print("="*80)
print("EXTRACTING RAW PDF TEXT - ALL METHODS")
print("="*80)

# Method 1: PyPDF2 with extraction mode
print("\n[Method 1: PyPDF2 Raw Extraction]")
try:
    with open('emails.pdf', 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        for i, page in enumerate(pdf.pages):
            print(f"\n--- Page {i+1} ---")
            text = page.extract_text()
            if text.strip():
                print(text)
            else:
                print("(No text)")
                
                # Try to get the page content stream
                if '/Contents' in page:
                    print("\nRaw content stream exists")
except Exception as e:
    print(f"Error: {e}")

# Method 2: PyMuPDF with different extraction modes
print("\n" + "="*80)
print("[Method 2: PyMuPDF - Text Extraction]")
print("="*80)

doc = fitz.open('emails.pdf')

for page_num in range(len(doc)):
    page = doc[page_num]
    
    print(f"\n--- Page {page_num+1} ---")
    
    # Try different extraction methods
    text_methods = {
        "text": page.get_text("text"),
        "blocks": page.get_text("blocks"),
        "words": page.get_text("words"),
        "html": page.get_text("html"),
        "dict": page.get_text("dict"),
        "rawdict": page.get_text("rawdict"),
    }
    
    for method, result in text_methods.items():
        if method in ["text", "html"]:
            if result and result.strip():
                print(f"\n[{method}]:")
                print(result[:500] if len(result) > 500 else result)
        elif method in ["blocks", "words"]:
            if result:
                print(f"\n[{method}]: {len(result)} items")
                if len(result) > 0:
                    print(f"  First item: {result[0]}")
        elif method in ["dict", "rawdict"]:
            if result and 'blocks' in result:
                blocks = result['blocks']
                print(f"\n[{method}]: {len(blocks)} blocks")
                for block in blocks:
                    if 'lines' in block:
                        for line in block['lines']:
                            for span in line['spans']:
                                if span['text'].strip():
                                    print(f"  Text: '{span['text']}'")

doc.close()

print("\n" + "="*80)
