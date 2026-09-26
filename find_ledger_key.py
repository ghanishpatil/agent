#!/usr/bin/env python3
"""
Once you have the unredacted text, paste it here to find the ledger key
"""

# INSTRUCTIONS:
# 1. Visit https://reveal.epstein-docs.org/
# 2. Upload emails.pdf
# 3. Copy all the unredacted text
# 4. Paste it in the unredacted_text variable below
# 5. Run this script

unredacted_text = """
PASTE THE UNREDACTED EMAIL TEXT HERE
"""

print("="*80)
print("FINDING LEDGER KEY FROM UNREDACTED EMAILS")
print("="*80)

if "PASTE" in unredacted_text:
    print("\n⚠ Please paste the unredacted email text first!")
    print("\nSteps:")
    print("1. Visit: https://reveal.epstein-docs.org/")
    print("2. Upload: emails.pdf")
    print("3. Copy all visible text after redactions are removed")
    print("4. Paste it in this script where it says 'PASTE THE UNREDACTED EMAIL TEXT HERE'")
    print("5. Run this script again")
else:
    import re
    
    print("\n[Analyzing unredacted text]")
    print(f"Text length: {len(unredacted_text)} characters")
    
    # Look for patterns
    print("\n[Looking for email addresses]")
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', unredacted_text)
    for email in emails:
        print(f"  {email}")
    
    print("\n[Looking for Subject names/numbers]")
    subjects = re.findall(r'Subject\s+\d+[:\s]+([^\n]+)', unredacted_text, re.IGNORECASE)
    for subj in subjects:
        print(f"  {subj}")
    
    print("\n[Looking for names]")
    # Common name patterns
    names = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', unredacted_text)
    for name in set(names):
        print(f"  {name}")
    
    print("\n[Looking for codes/keys]")
    codes = re.findall(r'\b[A-Z0-9]{8,}\b', unredacted_text)
    for code in set(codes):
        print(f"  {code}")
    
    print("\n[Looking for 'ledger' mentions]")
    lines = unredacted_text.split('\n')
    for i, line in enumerate(lines):
        if 'ledger' in line.lower():
            print(f"  Line {i}: {line}")
            if i > 0:
                print(f"    Before: {lines[i-1]}")
            if i < len(lines) - 1:
                print(f"    After: {lines[i+1]}")
    
    print("\n[Looking for flags]")
    flags = re.findall(r'Kaal\{[^}]+\}', unredacted_text, re.IGNORECASE)
    if flags:
        print("\n" + "="*80)
        print("✓✓✓ FOUND FLAG:")
        print("="*80)
        for flag in flags:
            print(f"  {flag}")
        print("="*80)

print("\n" + "="*80)
