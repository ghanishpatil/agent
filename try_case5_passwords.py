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
                    return True
    except:
        pass
    return False

pdf_path = Path("Cases/Case - 5_protected.pdf")

# Based on "Information Interchange" hint
passwords = [
    # Direct variations
    "Interchange",
    "INTERCHANGE",
    "interchange",
    "InformationInterchange",
    
    # The spacing is weird: "I nterchange"
    "Interchange",
    "I",
    "In",
    
    # Maybe it's about the article title or conclusion
    "Balance",
    "BALANCE",
    "balance",
    "BalanceAndTransparency",
    "Equilibrium",
    "EQUILIBRIUM",
    
    # Subject name
    "DevMalhotra",
    "Malhotra",
    
    # Pattern from other cases - 13 days
    "13days",
    "13Days",
    
    # The word "Balance" appears 3 times
    "BalanceBalanceBalance",
    
    # Electoral theme
    "Electoral",
    "ELECTORAL",
    "Election",
    "ELECTION",
    
    # Maybe interchange means reverse?
    "egnahcretnI",  # Interchange reversed
    
    # Or swap first/last letters?
    "Enterchange",
    
    # The hint might be in the spacing
    "Interchange",
    "Inter change",
    "I nterchange",
]

print("Trying passwords for Case 5...")
print("="*60)

for pwd in passwords:
    if try_password(pdf_path, pwd):
        print(f"SUCCESS! Password is: {pwd}")
        break
    else:
        print(f"Failed: {pwd}")
else:
    print("\nNone worked. Need to analyze Case 4 more carefully.")
