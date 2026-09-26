#!/usr/bin/env python3
import PyPDF2
from pathlib import Path

pdf_path = Path("Cases/Case - 4_protected.pdf")

with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    reader.decrypt("SILENCE")
    
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()
    
    print("Looking for patterns in Case 4...")
    print("="*80)
    
    # The hint is "Information Interchange"
    # Look for unusual capitalization or patterns
    
    lines = full_text.split('\n')
    for i, line in enumerate(lines):
        # Look for lines with unusual spacing or capitalization
        if 'Information' in line or 'Interchange' in line:
            print(f"Line {i}: {line}")
        
        # Look for lines with multiple capital letters mid-sentence
        words = line.split()
        capitals = []
        for j, word in enumerate(words):
            if j > 0 and word and len(word) > 0 and word[0].isupper():
                capitals.append(word[0])
        
        if len(capitals) >= 4:
            print(f"Capitals: {''.join(capitals)} | {line[:100]}")
