#!/usr/bin/env python3
"""
Remove redaction boxes and extract hidden text
"""
import fitz  # PyMuPDF

print("="*80)
print("REMOVING REDACTIONS FROM PDF")
print("="*80)

# Open the PDF
doc = fitz.open('emails.pdf')

print(f"\n[Processing {len(doc)} pages]")

# Create a new PDF without annotations
for page_num in range(len(doc)):
    page = doc[page_num]
    
    print(f"\nPage {page_num + 1}:")
    
    # Get all annotations
    annots = page.annots()
    if annots:
        print(f"  Found {len(list(page.annots()))} annotations")
        
        # Delete all annotations (redaction boxes)
        for annot in page.annots():
            page.delete_annot(annot)
        
        print(f"  ✓ Removed annotations")
    
    # Now extract text
    text = page.get_text("text")
    if text.strip():
        print(f"  Text found: {len(text)} characters")
        print(f"\n{text}")
    else:
        print(f"  No text found")

# Save the cleaned PDF
doc.save('emails_unredacted.pdf')
print(f"\n✓ Saved cleaned PDF to: emails_unredacted.pdf")

# Extract all text from cleaned PDF
all_text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text("text")
    all_text += text + "\n\n"

# Save text
with open('emails_unredacted.txt', 'w', encoding='utf-8') as f:
    f.write(all_text)

print(f"✓ Saved text to: emails_unredacted.txt")

doc.close()

# Now analyze the unredacted text
print(f"\n{'='*80}")
print("[ANALYZING UNREDACTED TEXT]")
print('='*80)

import re

# Look for flags
flags = re.findall(r'Kaal\{[^}]+\}', all_text, re.IGNORECASE)
if flags:
    print(f"\n✓✓✓ FOUND FLAGS:")
    for flag in flags:
        print(f"  {flag}")
else:
    print(f"\nNo Kaal{{}} flags found")

# Look for "ledger key"
if 'ledger' in all_text.lower():
    print(f"\n[Ledger mentions]")
    lines = all_text.split('\n')
    for i, line in enumerate(lines):
        if 'ledger' in line.lower():
            print(f"  Line {i}: {line}")
            # Print context
            if i > 0:
                print(f"    Before: {lines[i-1]}")
            if i < len(lines) - 1:
                print(f"    After: {lines[i+1]}")

# Look for Subject numbers
subjects = re.findall(r'Subject\s+(\d+)', all_text, re.IGNORECASE)
if subjects:
    print(f"\n[Subject numbers]: {subjects}")

# Look for any patterns that might be keys
print(f"\n[Looking for potential keys]")
# Alphanumeric strings
keys = re.findall(r'\b[A-Z0-9]{10,}\b', all_text)
if keys:
    print(f"  Potential keys: {keys[:10]}")

print("\n" + "="*80)
