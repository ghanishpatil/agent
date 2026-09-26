#!/usr/bin/env python3
import PyPDF2
from pathlib import Path

for case_num in range(1, 5):
    if case_num == 1:
        pdf_path = Path(f"Cases/Case - 1.pdf")
        password = None
    else:
        pdf_path = Path(f"Cases/Case - {case_num}_protected.pdf")
        passwords_map = {2: "VOICE", 3: "CANNOT", 4: "SILENCE"}
        password = passwords_map[case_num]
    
    print(f"\n{'='*80}")
    print(f"CASE {case_num} METADATA")
    print(f"{'='*80}")
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        if reader.is_encrypted and password:
            reader.decrypt(password)
        
        if reader.metadata:
            for key, value in reader.metadata.items():
                print(f"{key}: {value}")
        else:
            print("No metadata found")
