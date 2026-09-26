#!/usr/bin/env python3
import PyPDF2
import pikepdf
from pathlib import Path

pdf_path = Path("Cases/Flag_protected.pdf")

print("Inspecting Flag PDF...")
print("="*60)

# Try with PyPDF2
print("\n1. PyPDF2 Analysis:")
try:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        print(f"   Encrypted: {reader.is_encrypted}")
        print(f"   Number of pages: {len(reader.pages)}")
        
        # Try to get any unencrypted metadata
        try:
            if hasattr(reader, 'trailer'):
                print(f"   Trailer keys: {list(reader.trailer.keys())}")
        except:
            pass
except Exception as e:
    print(f"   Error: {e}")

# Try with pikepdf
print("\n2. Pikepdf Analysis:")
try:
    pdf = pikepdf.open(pdf_path, allow_overwriting_input=True)
    print("   PDF opened without password!")
    print(f"   Pages: {len(pdf.pages)}")
    
    if pdf.docinfo:
        print("   Document Info:")
        for key, value in pdf.docinfo.items():
            print(f"     {key}: {value}")
except pikepdf.PasswordError:
    print("   Password protected")
    
    # Try to get encryption info
    try:
        pdf = pikepdf.open(pdf_path, password="", allow_overwriting_input=True)
    except:
        pass
except Exception as e:
    print(f"   Error: {e}")

# Check file size and structure
print("\n3. File Info:")
print(f"   File size: {pdf_path.stat().st_size} bytes")

# Read raw bytes to look for any hints
print("\n4. Searching for text patterns in raw PDF...")
with open(pdf_path, 'rb') as f:
    content = f.read()
    
    # Look for common PDF strings
    if b'/Encrypt' in content:
        print("   Found /Encrypt dictionary")
    
    # Look for any readable text
    import re
    text_patterns = re.findall(b'[A-Za-z]{4,}', content)
    if text_patterns:
        unique_words = set([p.decode('latin-1', errors='ignore') for p in text_patterns[:50]])
        print(f"   Found {len(unique_words)} readable word patterns (first 50):")
        for word in sorted(unique_words)[:20]:
            if len(word) > 3:
                print(f"     - {word}")

print("\n" + "="*60)
print("Analysis complete.")
