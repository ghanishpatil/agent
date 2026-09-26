#!/usr/bin/env python3
import PyPDF2
from pathlib import Path

def try_password(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                result = reader.decrypt(password)
                if result:
                    print(f"✅ SUCCESS! Password '{password}' works!")
                    # Extract text
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    print("\n" + "="*80)
                    print("EXTRACTED TEXT:")
                    print("="*80)
                    print(text[:2000])
                    return True
    except Exception as e:
        print(f"Error: {e}")
    return False

pdf_path = Path("Cases/Case - 2_protected.pdf")

# Try Voice and variations
passwords = ["Voice", "voice", "VOICE", "VoIcE"]

for pwd in passwords:
    print(f"Trying: {pwd}")
    if try_password(pdf_path, pwd):
        break
