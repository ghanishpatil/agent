#!/usr/bin/env python3
"""
Extract hidden text from redacted PDF
"""
import PyPDF2
import re

print("="*80)
print("EXTRACTING TEXT FROM EMAILS.PDF")
print("="*80)

# Open the PDF
with open('emails.pdf', 'rb') as f:
    pdf_reader = PyPDF2.PdfReader(f)
    
    print(f"\n[PDF Info]")
    print(f"Pages: {len(pdf_reader.pages)}")
    
    # Extract text from all pages
    full_text = ""
    for i, page in enumerate(pdf_reader.pages):
        print(f"\n{'='*80}")
        print(f"[Page {i+1}]")
        print(f"{'='*80}")
        
        text = page.extract_text()
        full_text += text + "\n\n"
        print(text)
    
    # Save full text
    with open('emails_extracted.txt', 'w', encoding='utf-8') as out:
        out.write(full_text)
    
    print(f"\n{'='*80}")
    print(f"[Searching for Flag Pattern]")
    print(f"{'='*80}")
    
    # Look for Kaal{} pattern
    flags = re.findall(r'Kaal\{[^}]+\}', full_text, re.IGNORECASE)
    if flags:
        print(f"\n✓ Found {len(flags)} flag(s):")
        for flag in flags:
            print(f"  {flag}")
    else:
        print(f"\n✗ No obvious flag found")
        
        # Look for suspicious patterns
        print(f"\n[Looking for hidden patterns]")
        
        # Look for base64
        import base64
        b64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', full_text)
        if b64_patterns:
            print(f"\nFound {len(b64_patterns)} potential base64 strings:")
            for pattern in b64_patterns[:10]:
                try:
                    decoded = base64.b64decode(pattern)
                    if b'Kaal' in decoded or b'flag' in decoded:
                        print(f"  {pattern} -> {decoded}")
                except:
                    pass
        
        # Look for hex patterns
        hex_patterns = re.findall(r'[0-9a-fA-F]{32,}', full_text)
        if hex_patterns:
            print(f"\nFound {len(hex_patterns)} potential hex strings:")
            for pattern in hex_patterns[:10]:
                print(f"  {pattern}")

print("\n" + "="*80)
