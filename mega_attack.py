#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re
import time

def try_decrypt(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                if reader.decrypt(password):
                    return reader
    except:
        pass
    return None

pdf_path = Path("Cases/Flag_protected.pdf")

# Read mega wordlist
with open("mega_wordlist.txt", "r") as f:
    wordlist = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(wordlist)} passwords")
print("Starting MEGA attack...")
print("="*80)

start_time = time.time()

for i, pwd in enumerate(wordlist):
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n\n*** PASSWORD CRACKED: '{pwd}' ***\n")
        print(f"Found after trying {i+1} passwords in {time.time() - start_time:.2f} seconds")
        print("\n" + "="*80)
        print("EXTRACTING FLAG...")
        print("="*80 + "\n")
        
        full_text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                full_text += text
                print(f"--- PAGE {page_num + 1} ---")
                print(text)
                print()
            except Exception as e:
                print(f"Error on page {page_num + 1}: {e}")
        
        # Extract flag
        flags = re.findall(r'BPCTF\{[^}]+\}', full_text)
        if flags:
            print("\n" + "="*80)
            print("*** THE FLAG ***")
            print("="*80)
            for flag in flags:
                print(flag)
            print("="*80)
        else:
            print("\nNo BPCTF{} pattern found. Searching for alternatives...")
            other = re.findall(r'\{[^}]{10,}\}', full_text)
            if other:
                print("Possible flags:")
                for f in other:
                    print(f)
        
        exit(0)
    
    if (i + 1) % 500 == 0:
        elapsed = time.time() - start_time
        rate = (i + 1) / elapsed
        remaining = (len(wordlist) - i - 1) / rate
        print(f"[{i + 1}/{len(wordlist)}] {rate:.0f} pwd/s | ETA: {remaining:.0f}s")

print(f"\nExhausted all {len(wordlist)} passwords in {time.time() - start_time:.2f} seconds")
print("Password not in wordlist.")
