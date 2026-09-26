#!/usr/bin/env python3
import PyPDF2
from pathlib import Path

passwords = {
    1: None,
    2: "VOICE",
    3: "CANNOT",
    4: "SILENCE",
    5: "BUT",
    6: "SYSTEM",
    7: "CAN",
}

for case_num in range(1, 8):
    print(f"\n{'#'*80}")
    print(f"# CASE {case_num}")
    print(f"{'#'*80}\n")
    
    if case_num == 1:
        pdf_path = Path(f"Cases/Case - 1.pdf")
    else:
        pdf_path = Path(f"Cases/Case - {case_num}_protected.pdf")
    
    password = passwords.get(case_num)
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            if reader.is_encrypted:
                if not password:
                    print(f"LOCKED - Need password from Case {case_num - 1}")
                    break
                if not reader.decrypt(password):
                    print(f"FAILED - Password '{password}' didn't work")
                    break
                print(f"UNLOCKED with password: {password}")
            
            for page_num, page in enumerate(reader.pages):
                print(f"\n{'='*80}")
                print(f"PAGE {page_num + 1}")
                print(f"{'='*80}\n")
                text = page.extract_text()
                print(text)
    except Exception as e:
        print(f"ERROR: {e}")
        break
