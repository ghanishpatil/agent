#!/usr/bin/env python3
"""
Analyze the emails PDF for hidden data and redacted text
"""
import PyPDF2
import fitz  # PyMuPDF
import re

print("="*80)
print("ANALYZING BLACK WIDOW EMAILS PDF")
print("="*80)

# Use PyMuPDF to extract text more carefully
doc = fitz.open('emails.pdf')

print(f"\n[PDF Info]")
print(f"Pages: {len(doc)}")

all_text = ""

for page_num in range(len(doc)):
    page = doc[page_num]
    
    print(f"\n{'='*80}")
    print(f"PAGE {page_num + 1}")
    print('='*80)
    
    # Extract text with layout preservation
    text = page.get_text("text")
    print(text)
    all_text += text + "\n\n"
    
    # Also try to get text blocks with positions
    blocks = page.get_text("dict")["blocks"]
    
    # Look for hidden text (text under black rectangles)
    print(f"\n[Checking for hidden/covered text]")
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text_content = span["text"]
                    # Check if text color is white or very light (might be hidden)
                    color = span.get("color", 0)
                    if text_content.strip():
                        print(f"  Text: '{text_content}' | Color: {color}")

# Save all text
with open('emails_full_text.txt', 'w', encoding='utf-8') as f:
    f.write(all_text)

print(f"\n{'='*80}")
print("[ANALYSIS]")
print('='*80)

# Look for patterns
print(f"\n[Looking for Kaal{{}} flags]")
flags = re.findall(r'Kaal\{[^}]+\}', all_text, re.IGNORECASE)
if flags:
    for flag in flags:
        print(f"  ✓ {flag}")
else:
    print("  No direct flags found")

# Look for Subject numbers
print(f"\n[Subject numbers mentioned]")
subjects = re.findall(r'Subject\s+(\d+)', all_text, re.IGNORECASE)
if subjects:
    print(f"  Subjects: {subjects}")

# Look for dates
print(f"\n[Dates mentioned]")
dates = re.findall(r'Date:\s*([^\n]+)', all_text)
for date in dates:
    print(f"  {date}")

# Look for any encoded strings
print(f"\n[Looking for encoded strings]")
# Base64
b64 = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', all_text)
if b64:
    print(f"  Base64 candidates: {len(b64)}")
    for i, s in enumerate(b64[:5]):
        print(f"    {i+1}. {s}")

# Hex
hex_strings = re.findall(r'[0-9a-fA-F]{16,}', all_text)
if hex_strings:
    print(f"  Hex candidates: {len(hex_strings)}")
    for i, s in enumerate(hex_strings[:5]):
        print(f"    {i+1}. {s}")

# Look for keywords
print(f"\n[Keywords]")
keywords = ['ledger', 'key', 'budapest', 'widow', 'subject', 'cargo', 'protocol']
for kw in keywords:
    count = all_text.lower().count(kw.lower())
    if count > 0:
        print(f"  '{kw}': {count} times")

# Check for metadata
print(f"\n[PDF Metadata]")
print(f"  {doc.metadata}")

# Check for hidden layers or annotations
print(f"\n[Checking for annotations/hidden content]")
for page_num in range(len(doc)):
    page = doc[page_num]
    annots = page.annots()
    if annots:
        print(f"  Page {page_num+1} has annotations:")
        for annot in annots:
            print(f"    Type: {annot.type}, Info: {annot.info}")

doc.close()

print("\n" + "="*80)
